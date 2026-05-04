#from paises import paises
from PyQt5.QtWidgets  import *
from PyQt5.uic import *
from PyQt5.QtCore import *
import sys

class MiVentana(QMainWindow):

    def __init__(self):
        paises = ["Ecuador", "Brasil", "Argentina", "Armenia", "Mongolia", "Paraguay", "Panama", "Alemania", "Afganistan", "China", "Vietnam"]
        super().__init__()
        self.paises = paises
        loadUi("main.ui", self)
        completer = QCompleter(self.paises)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtBuscador.setCompleter(completer)
        self.scrollLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.scrollAreaWidgetContents.setLayout(self.scrollLayout)
        self.txtBuscador.returnPressed.connect(self.Buscar)
        self.btnBuscar.clicked.connect(self.Buscar)

        self.btn1.clicked.connect(lambda _, c=self.Configuraciones_2: self.Expandir(c))
        self.btn2.clicked.connect(lambda _, c=self.Anotaciones_2: self.Expandir(c))
        self.btn3.clicked.connect(lambda _, c=self.Cronometro_2: self.Expandir(c))
        self.btn4.clicked.connect(lambda _, c=self.Historial: self.Expandir(c))
        self.cerrarSideBar.clicked.connect(lambda: self.sideBar.setMaximumWidth(0))
        
        self.lista.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

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
        txt = str(pais.text())
        pais.deleteLater()
        self.txtCronometro.setText(f"03:00 - {txt}")
        self.timer = QTimer()
        self.time = QTime(0, 3, 0) #Tiempo que empieza el cronometro !!
        self.timer.start(1000)
        self.timer.timeout.connect(lambda: self.Cronometrar(txt))

    def Cronometrar(self, pais):
        self.time = self.time.addSecs(-1)
        timeDisplay = self.time.toString("mm:ss")
        self.txtCronometro.setText(f"{timeDisplay} - {pais}")
        if self.time == QTime(0, 0, 0):
            self.timer.stop()
            self.txtCronometro.setText(f"00:00")
    
    def Expandir(self, nombre):
        self.sideBar.setMaximumWidth(400)
        self.Anotaciones_2.setMaximumHeight(0)
        self.Configuraciones_2.setMaximumHeight(0)
        self.Historial.setMaximumHeight(0)
        self.Cronometro_2.setMaximumHeight(0)
        nombre.setMaximumHeight(16777215)
    
app= QApplication(sys.argv)
ventana= MiVentana()
ventana.show()
sys.exit(app.exec_()) 