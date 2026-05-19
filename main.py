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
        
        self.cerrarSideBar.clicked.connect(lambda: self.sideBar.setMaximumWidth(0))
        
        self.listaForo.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.listaHistorial.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.PaisesEnForo()

    def Buscar(self):

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
                
    def QuitarPais(self, pais):
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

    def Buscador(self):
        self.cursor.execute("SELECT pais FROM tabdelegaciones WHERE enforo = 2")
        paises = [fila["pais"] for fila in self.cursor.fetchall()]
        modelo = QStringListModel(paises)
        self.completer.setModel(modelo)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtBuscador.setCompleter(self.completer)
        self.paises = paises

    def PaisesEnForo(self):
        def PaisEnForo(state, pais):
            self.cursor.execute("""
                UPDATE tabdelegaciones
                SET enforo = ?
                WHERE pais = ?
            """, (state, pais))
            self.conn.commit()
            self.Buscador()

        self.cursor.execute("SELECT pais, enforo FROM tabdelegaciones")
        for fila in self.cursor.fetchall():
            pais = fila[0]

            btn_paisEnForo = QCheckBox()
            btn_paisEnForo.setChecked(bool(fila["enforo"]))
            btn_paisEnForo.stateChanged.connect(lambda state, p=pais: PaisEnForo(state, p))
            
            row_position = self.listaForo.rowCount()
            self.listaForo.insertRow(row_position)
            self.listaForo.setItem(row_position, 0, QTableWidgetItem(fila["pais"]))
            self.listaForo.setCellWidget(row_position, 1, btn_paisEnForo)
        self.Buscador()

    def Expandir(self, nombre):
        self.sideBar.setMaximumWidth(400)
        self.Anotaciones_2.setMaximumHeight(0)
        self.Configuraciones_2.setMaximumHeight(0)
        self.Historial.setMaximumHeight(0)
        self.Cronometro_2.setMaximumHeight(0)
        self.listaPaises_2.setMaximumHeight(0)
        nombre.setMaximumHeight(16777215)
    
    def closeEvent(self, a0):
        self.cursor.execute("""
            UPDATE tabdelegaciones
            SET turnos = 0""")
        self.conn.commit()
        self.conn.close()

app= QApplication(sys.argv)
ventana= MiVentana()
ventana.show()
sys.exit(app.exec_()) 