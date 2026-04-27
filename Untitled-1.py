from PyQt5.QtWidgets  import *
from PyQt5.uic import *
from PyQt5.QtCore import *
import sys

class MiVentana(QMainWindow):

    def __init__(self):
        
        super().__init__()
        self.paises = ["Ecuador", "Argentina", "Alemania","Paraguay","Panama","Brasil"]
        loadUi("main.ui", self)

        completer = QCompleter(self.paises)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.txtBuscador.setCompleter(completer)
        self.scrollLayout = QHBoxLayout(self.scrollAreaWidgetContents)
        self.scrollAreaWidgetContents.setLayout(self.scrollLayout)
        self.txtBuscador.returnPressed.connect(self.Buscar)
        self.btnBuscar.clicked.connect(self.Buscar)
        
    def Buscar(self):
        item = self.scrollLayout.takeAt(self.scrollLayout.count() - 1)
        del item
        txt=self.txtBuscador.text() 
        if txt in self.paises:
                btn=QPushButton(f"{txt}")
                btn.setMinimumSize(100, 100)
                btn.setMaximumSize(100, 100)
                btn.setStyleSheet('font: 10pt "Bahnschrift SemiBold"; text-align: left; background-color: rgb(255, 255, 255); border-radius: 20px; padding-left: 20px; margin-bottom: 3px;')
                btn.clicked.connect(lambda _, btn=btn: self.QuitarPais(btn))            
                self.txtBuscador.clear()
                self.scrollLayout.addWidget(btn, alignment=Qt.AlignTop)
                self.scrollLayout.addStretch()
                
    def QuitarPais(self, pais):
        txt = str(pais.text())
        pais.deleteLater()
        self.timer = QTimer()
        self.time = QTime(0, 3, 0) #Tiempo que empieza el cronometro !!
        self.timer.start(1000)
        self.timer.timeout.connect(lambda: self.Cronometrar(txt))

    def Cronometrar(self, pais):
        self.time = self.time.addSecs(-1)
        timeDisplay = self.time.toString("mm:ss")
        self.txtCronometro.setText(f"{timeDisplay} - {pais}")
        if self.time == 0:
             

app= QApplication(sys.argv)
ventana= MiVentana()
ventana.show()
sys.exit(app.exec_()) 