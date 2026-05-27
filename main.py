import sqlite3
from PyQt5.QtWidgets  import *
from PyQt5.uic import *
from PyQt5.QtCore import *
import sys

class MiVentana(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("main.ui", self)

        self.conn = sqlite3.connect("db_CEPBMOON.db")
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("SELECT pais FROM tabdelegaciones WHERE enforo = 2")

        self.paises = [fila["pais"] for fila in self.cursor.fetchall()]
        self.completer = QCompleter(self.paises)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtBuscador.setCompleter(self.completer)
        self.scrollLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.scrollAreaWidgetContents.setLayout(self.scrollLayout)
        self.txtBuscador.returnPressed.connect(self.Buscar)
        self.btnBuscar.clicked.connect(self.Buscar)

        self.btn1.clicked.connect(lambda _, c=self.Configuraciones_2: self.Expandir(c))
        self.btn2.clicked.connect(lambda _, c=self.Anotaciones_2: self.Expandir(c))
        self.btn3.clicked.connect(lambda _, c=self.Cronometro_2: self.Expandir(c))
        self.btn4.clicked.connect(lambda _, c=self.Historial: self.Expandir(c))
        self.btn_verPaises.clicked.connect(lambda _, c=self.listaPaises_2: self.Expandir(c))
        self.btn_nombrarPaises.clicked.connect(lambda _, c=self.Delegados_3: (self.Expandir(c), self.DelegacionesEnForo(self.Delegados)))

        
        self.cerrarSideBar.clicked.connect(lambda: self.sideBar.setMaximumWidth(0))
        
        self.listaForo.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.listaHistorial.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.PaisesEnForo()
        self.DelegacionesEnForo(self.Delegados)
        self.Cronometro()

    def Buscar(self):                #Para buscar un pais y que se añada a la lista de oradores
        txt = self.txtBuscador.text().strip()
        if not txt or txt not in self.paises:
            return
        for i in range(self.scrollLayout.count()):
            item = self.scrollLayout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QPushButton) and widget.text() == txt:
                self.txtBuscador.clear()
                return
        
        last_index = self.scrollLayout.count() - 1
        if last_index >= 0:
            item = self.scrollLayout.itemAt(last_index)
            if item.spacerItem():
                self.scrollLayout.takeAt(last_index)

        btn = QPushButton(txt)
        btn.setMinimumSize(100, 100)
        btn.setMaximumSize(100, 100)
        btn.setStyleSheet('font: 10pt "Bahnschrift SemiBold"; text-align: left; background-color: rgb(255, 255, 255); border-radius: 20px; padding-left: 20px; margin-bottom: 3px;')
        btn.clicked.connect(lambda _, b=btn: self.QuitarPais(b))
        self.txtBuscador.clear()
        self.scrollLayout.addWidget(btn, alignment=Qt.AlignTop)
        self.scrollLayout.addStretch()
                
    def QuitarPais(self, pais):      #Afecta el *Historial*. Quitar un pais de la lista de oradores, registrar y cronometrarlo 
        def Registrar(nompais):
                conn = sqlite3.connect("db_CEPBMOON.db")
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE tabdelegaciones
                    SET turnos = turnos + 1
                    WHERE pais = ?
                """, (nompais,))
                conn.commit()
                conn.close()

                self.cursor.execute("SELECT turnos FROM tabdelegaciones WHERE pais = ?",(nompais,))
                turnos= self.cursor.fetchone()["turnos"]

                row_position = self.listaHistorial.rowCount()
                self.listaHistorial.insertRow(row_position)
                self.listaHistorial.setItem(row_position, 0, QTableWidgetItem(nompais))
                self.listaHistorial.setItem(row_position, 1, QTableWidgetItem(str(turnos)))

        def Cronometrar(pais):
            self.time = self.time.addSecs(-1)
            timeDisplay = self.time.toString("mm:ss")
            self.txtCronometro.setText(f"{timeDisplay} - {pais}")
            if self.time == QTime(0, 0, 0):
                self.timer.stop()
                self.txtCronometro.setText(f"00:00")
        
        txt = str(pais.text())
        pais.deleteLater()
        self.txtCronometro.setText(f"03:00 - {txt}")
        self.timer = QTimer()
        self.time = QTime(0, 3, 0) #Tiempo que empieza el cronometro !!
        self.timer.start(1000)
        self.timer.timeout.connect(lambda: Cronometrar(txt))
        Registrar(txt)

    def Buscador(self):              #Actualizar el buscador cuando se cambia los paises en un foro
        self.cursor.execute("SELECT pais FROM tabdelegaciones WHERE enforo = 2")
        paises = [fila["pais"] for fila in self.cursor.fetchall()]
        modelo = QStringListModel(paises)
        self.completer.setModel(modelo)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtBuscador.setCompleter(self.completer)
        self.paises = paises

    def PaisesEnForo(self):          #Actualizar que paises se cargarán, cargar la lista y checkboxes para seleccionar o no las delegaciones
        def PaisEnForo(state, pais):
            self.cursor.execute("""
                UPDATE tabdelegaciones
                SET enforo = ?
                WHERE pais = ?
            """, (state, pais))
            self.conn.commit()
            self.Buscador()

        def BuscarPais(n):
            self.listaForo.setRowCount(0)

            self.cursor.execute("""SELECT * FROM tabdelegaciones WHERE pais LIKE ?""", (f"{n}%",))
            for fila in self.cursor.fetchall():
                pais = fila["pais"]
                btn_paisEnForo = QCheckBox()
                btn_paisEnForo.setChecked(bool(fila["enforo"]))
                btn_paisEnForo.stateChanged.connect(lambda state, p=pais: PaisEnForo(state, p))
                btn_paisEnForo.setLayoutDirection(Qt.RightToLeft)

                row_position = self.listaForo.rowCount()
                self.listaForo.insertRow(row_position)
                self.listaForo.setItem(row_position,0,QTableWidgetItem(fila["pais"]))
                self.listaForo.setCellWidget(row_position,1,btn_paisEnForo)
        BuscarPais("")
        self.txtBuscarEnForo.textChanged.connect(BuscarPais)

    def DelegacionesEnForo(self, layout): #Nombra a los delegados en una delegación
        while layout.layout().count():
            item = layout.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self.DelegacionesEnForo(item.layout())

        self.cursor.execute("""SELECT idPais, pais FROM tabdelegaciones WHERE enforo = 2""")
        paisesEnForo=self.cursor.fetchall()
        hLayout = QHBoxLayout()
        for delegacion in paisesEnForo:
            nomPais = QLabel(str(delegacion["pais"]))
            nomPais.setStyleSheet('font: 12pt "Bahnschrift SemiBold"; text-align: center;')
            nomPais.setAlignment(Qt.AlignCenter)
            
            #Este va a ser cada delegado por cada pais en el foro!!
            self.cursor.execute("""SELECT * FROM tabDelegados WHERE idPais = ?""",(int(delegacion["idPais"]),))
            delegados = self.cursor.fetchall()
            hLayout = QHBoxLayout()
            for delegado in delegados:
                Delegado = str(delegado["Delegado"])
                d = QLineEdit(Delegado if Delegado != "None" else "")
                d.setStyleSheet('background-color: rgb(230, 230, 230);border-radius: 5px;padding:5px;font: 12pt "Bahnschrift SemiBold"; margin-bottom: 40px;')
                d.textChanged.connect(lambda texto, idNota=delegado["idNota"]: (
                                            self.cursor.execute(
                                                """UPDATE tabDelegados SET Delegado = ? WHERE idNota = ?""",
                                                (texto, idNota)
                                            ),
                                            self.conn.commit()
                                        )
                                    )
                hLayout.addWidget(d)

                self.conn.commit()
            layout.layout().addWidget(nomPais)
            layout.layout().addLayout(hLayout)   
            layout.layout().addStretch()

    def Cronometro(self):            #Afecta el *Cronometro*. 
        def MoverReloj(fecha):
            self.Cron.setSliderPosition(30+int(fecha.hour() * 60 + fecha.minute()))

        def IniciarCronometro(fecha):
            self.timerCron = QTimer()
            self.tiempoCron = QTime(fecha)

            def Cronometrar():
                self.tiempoCron = self.tiempoCron.addSecs(-1)
                self.txtCron.setTime(self.tiempoCron)
                MoverReloj(self.tiempoCron)
                if self.tiempoCron == QTime(0, 0, 0):
                    self.timerCron.stop()
                    self.txtCron.setReadOnly(False)

            self.txtCron.setReadOnly(True)
            self.timerCron.timeout.connect(Cronometrar)
            self.timerCron.start(1000)

        self.txtCron.timeChanged.connect(MoverReloj)
        self.btnComenzarCron.clicked.connect(lambda:(IniciarCronometro(self.txtCron.time()), MoverReloj(self.txtCron.time())))
        self.btnPausarCron.clicked.connect(lambda: (self.txtCron.setReadOnly(True if not self.txtCron.isReadOnly() else False), self.timerCron.stop()))

    def Expandir(self, nombre):      #Expandir la barra al costado, comprimir las demas barras
        self.sideBar.setMaximumWidth(400)
        self.Anotaciones_2.setMaximumHeight(0)
        self.Configuraciones_2.setMaximumHeight(0)
        self.Historial.setMaximumHeight(0)
        self.Cronometro_2.setMaximumHeight(0)
        self.listaPaises_2.setMaximumHeight(0)
        self.Delegados_3.setMaximumHeight(0)
        nombre.setMaximumHeight(16777215)
    
    def closeEvent(self, a0):        #Reiniciar los turnos de las delegaciones al cerrar el programa, crear un pdf que registra lo que sucedió en la sesión
        self.cursor.execute("""
            UPDATE tabdelegaciones
            SET turnos = 0""")
        self.conn.commit()
        self.conn.close()

app= QApplication(sys.argv)
ventana= MiVentana()
ventana.show()
sys.exit(app.exec_()) 