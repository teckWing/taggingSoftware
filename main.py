from ctypes import alignment
from PyQt5.QtWidgets import QApplication
import sys
from utils.SoccerLib import *

   

app = QApplication(sys.argv)
app.setStyleSheet("""MainWindow {
        background-image: url("utils/endless-constellation.png"); 
        background-position: center;
    }""")





window=MainWindow()
window.show()
sys.exit(app.exec_())
app.aboutToQuit.connect(sys.exit(0))



