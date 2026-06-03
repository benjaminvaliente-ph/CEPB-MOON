import sqlite3
from PyQt5.QtWidgets  import *
from PyQt5.uic import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
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
        self.Configuraciones()
        self.Cronometro()
        self.Observaciones()

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
        pais.deleteLater()
        self.timer = QTimer()
        def Registrar(nompais):      # Añade el pais al historial
                self.cursor.execute("""UPDATE tabdelegaciones SET turnos = turnos + 1 WHERE pais = ?""", (nompais,))
                self.conn.commit()

                self.cursor.execute("SELECT turnos FROM tabdelegaciones WHERE pais = ?",(nompais,))
                turnos= self.cursor.fetchone()["turnos"]

                self.listaHistorial.insertRow(0)
                self.listaHistorial.setItem(0, 0, QTableWidgetItem(nompais))
                self.listaHistorial.setItem(0, 1, QTableWidgetItem(str(turnos)))
        
        txt = str(pais.text())

        def Cronometrar(tiempo): 
            def Cronometro(pais):
                if self.time == QTime(0, 0, 0):
                    self.timer.stop()
                    if tiempo == "pensar":
                        Cronometrar("contestar")
                    else:
                        self.txtCronometro.setText(f"00:00")
                    return
                self.time = self.time.addSecs(-1)
                timeDisplay = self.time.toString("mm:ss")
                self.txtCronometro.setText(f"{timeDisplay} - {pais}")
            
            self.Lectura.setEnabled(False)
            self.Cuestionar.setEnabled(False)
            self.Contestar.setEnabled(False)

            self.cursor.execute(f"SELECT {tiempo} FROM tabtiempos")
            t = self.cursor.fetchone()
            
            self.time = QTime(0, 0, 0)
            self.time = self.time.addSecs(int(t[f"{tiempo}"]))      # Añadir segundos - lee de la base de datos
            self.txtCronometro.setText(f"{self.time.toString("mm:ss")} - {txt}")
            try:
                self.timer.timeout.disconnect()
            except:
                pass
            self.timer.timeout.connect(lambda: Cronometro(txt))
            self.timer.start(1000)

        self.txtCronometro.setText(txt)
        self.Lectura = QShortcut(QKeySequence("l"), self)
        self.Cuestionar = QShortcut(QKeySequence("c"), self)
        self.Contestar = QShortcut(QKeySequence("r"), self)
        self.Lectura.activated.connect(lambda: Cronometrar("lectura"))
        self.Cuestionar.activated.connect(lambda: Cronometrar("cuestionar"))
        self.Contestar.activated.connect(lambda: Cronometrar("pensar"))

        Registrar(txt)

    def Observaciones(self):
        self.cursor.execute("SELECT pais FROM tabdelegaciones WHERE enforo = 2")

        self.paises = [fila["pais"] for fila in self.cursor.fetchall()]
        self.completerDelegacion = QCompleter(self.paises)
        self.completerDelegacion.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtDelegacion.setCompleter(self.completer)

    def Buscador(self):              #Actualizar el buscador cuando se cambia los paises en un foro
        self.cursor.execute("SELECT pais FROM tabdelegaciones WHERE enforo = 2")
        paises = [fila["pais"] for fila in self.cursor.fetchall()]
        modelo = QStringListModel(paises)
        self.completer.setModel(modelo)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtBuscador.setCompleter(self.completer)
        self.paises = paises

    def PaisesEnForo(self):          # Actualizar que paises se cargarán, cargar la lista y checkboxes para seleccionar o no las delegaciones
        def PaisEnForo(state, pais):
            self.cursor.execute("""UPDATE tabdelegaciones SET enforo = ? WHERE pais = ?""", (state, pais))
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

    def DelegacionesEnForo(self, layout): # Nombra a los delegados en una delegación
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
            
            self.cursor.execute("""SELECT * FROM tabDelegados WHERE idPais = ?""", (int(delegacion["idPais"]),))
            hLayout = QHBoxLayout()
            for delegado in self.cursor.fetchall():
                Delegado = str(delegado["Delegado"])
                d = QLineEdit(Delegado if Delegado != "None" else "")
                d.setStyleSheet('background-color: rgb(230, 230, 230);border-radius: 5px;padding:5px;font: 12pt "Bahnschrift SemiBold"; margin-bottom: 40px;')
                d.textChanged.connect(lambda texto, idNota=delegado["idNota"]: 
                                      (self.cursor.execute("""UPDATE tabDelegados SET Delegado = ? WHERE idNota = ?""",(texto, idNota)),
                                       self.conn.commit()))
                hLayout.addWidget(d)

                self.conn.commit()
            layout.layout().addWidget(nomPais)
            layout.layout().addLayout(hLayout)   
            layout.layout().addStretch()

    def Cronometro(self):            # Afecta el *Cronometro*. 
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
                    self.Expandir(self.Cronometro_2)

            self.txtCron.setReadOnly(True)
            self.timerCron.timeout.connect(Cronometrar)
            self.timerCron.start(1000)

        self.txtCron.timeChanged.connect(MoverReloj)
        self.btnComenzarCron.clicked.connect(lambda:(IniciarCronometro(self.txtCron.time()), MoverReloj(self.txtCron.time())))
        self.btnPausarCron.clicked.connect(lambda: (self.txtCron.setReadOnly(True if not self.txtCron.isReadOnly() else False), self.timerCron.stop()))

    def Configuraciones(self):       # Permite cambiar los tiempos
        def CambiarTiempo(columna, tiempo):
            segundos = tiempo.hour()*3600 + tiempo.minute()*60 + tiempo.second()
            self.cursor.execute(f"UPDATE tabtiempos SET {columna} = ?", (segundos,))
            self.conn.commit()

        self.cursor.execute("SELECT lectura, cuestionar, pensar, contestar FROM tabtiempos")
        tLectura, tCuestionar, tPensar, tContestar = self.cursor.fetchone()

        self.timeLectura.setTime(self.timeLectura.time().addSecs(tLectura))
        self.timeCuestionar.setTime(self.timeCuestionar.time().addSecs(tCuestionar))
        self.timePensar.setTime(self.timePensar.time().addSecs(tPensar))
        self.timeContestar.setTime(self.timeContestar.time().addSecs(tContestar))

        self.timeLectura.timeChanged.connect(lambda t: CambiarTiempo("lectura", t))
        self.timeCuestionar.timeChanged.connect(lambda t: CambiarTiempo("cuestionar", t))
        self.timePensar.timeChanged.connect(lambda t: CambiarTiempo("pensar", t))
        self.timeContestar.timeChanged.connect(lambda t: CambiarTiempo("contestar", t))

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
        self.cursor.execute("""UPDATE tabdelegaciones SET turnos = 0""")
        self.conn.commit()
        self.conn.close()

app= QApplication(sys.argv)
ventana= MiVentana()
ventana.show()
sys.exit(app.exec_()) 