from ctypes import alignment
from PyQt5.QtWidgets import  QWidget, QPushButton, QHBoxLayout,\
    QVBoxLayout, QStyle, QSlider, QGridLayout, QInputDialog, QLabel, QShortcut, QFileDialog, \
    QTableWidgetItem, QGraphicsPixmapItem, QCheckBox, QLineEdit, QMessageBox, QDialog, QTableWidget, QMainWindow
from PyQt5.QtCore import Qt, QUrl, QSize, pyqtSignal
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtGui import QIcon,  QPixmap, QKeySequence
import pyqtgraph as pg
import json




        
class PlayerVideo(QWidget):
        def __init__(self,video):
            super().__init__()
            self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
            self.videowidget = QVideoWidget()
            self.playBtn = QPushButton()
            self.playBtn.setEnabled(False)
            self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
            self.slider = QSlider(Qt.Horizontal)
            self.slider.setRange(0, 0)
            self.spaceBar = QShortcut(QKeySequence(Qt.Key_Space), self)
            self.bskip = QShortcut(QKeySequence(Qt.Key_Left), self)
            self.fskip = QShortcut(QKeySequence(Qt.Key_Right), self)

            self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(video)))
            self.playBtn.setEnabled(True)

            hbox = QHBoxLayout()
            hbox.addWidget(self.playBtn)
            hbox.addWidget(self.slider)
            
            vbox = QVBoxLayout()
            vbox.addWidget(self.videowidget)
            vbox.addLayout(hbox)

            self.setLayout(vbox)

            self.playBtn.clicked.connect(self.play_video)
            self.slider.sliderMoved.connect(self.set_position)
            self.spaceBar.activated.connect(self.play_video)
            self.fskip.activated.connect(self.skip15)
            self.bskip.activated.connect(self.bskip15)
            self.mediaPlayer.setVideoOutput(self.videowidget)
            self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
            self.mediaPlayer.positionChanged.connect(self.position_changed)
            self.mediaPlayer.durationChanged.connect(self.duration_changed)

            self.setGeometry(350, 100, 700, 500)
            self.setWindowIcon(QIcon("soccer.ico"))
            self.setWindowTitle("MatchVideo")
            self.show()

    
        def bskip15(self):
            # rewind video 1.5 seconds
            self.position_changed(self.slider.sliderPosition() - 1500)
            self.mediaPlayer.setPosition(self.mediaPlayer.position() - 1500)

        def skip15(self):
            # send forward video 1.5 seconds
            self.position_changed(self.slider.sliderPosition() + 1500)
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1500)

            

        def play_video(self):
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()

            else:
                self.mediaPlayer.play()

        def mediastate_changed(self):
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

            else:
                self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

        def position_changed(self, position):
            self.slider.setValue(position)

        def duration_changed(self, duration):
            self.slider.setRange(0, duration)

        def set_position(self, position):
            self.mediaPlayer.setPosition(position)


class Pitch2Coord(pg.PlotWidget):
    """
        Class to generate pitch coord
    """

    def __init__(self,table,record):
        super().__init__()
        self.img = QGraphicsPixmapItem(QPixmap("utils/pitch.png"))
        self.addItem(self.img)
        self.setXRange(0, 700, padding=0)
        self.setYRange(0, 500, padding=0)
        self.setLimits(xMin=0, xMax=700, yMin=0, yMax=500)
        self.getPlotItem().hideAxis("bottom")
        self.getPlotItem().hideAxis("left")
        self.clicks = []
        self.record=record
        self.table=table

    def onClick(self, ev, mediaPlayer):
        p = self.plotItem.vb.mapSceneToView(ev.pos())
        x = p.x() if (p.x() > 0 and p.x() <= 700) else (0 if p.x() <= 700 else 700)
        y = p.y() if (p.y() > 0 and p.y() <= 500) else (0 if p.y() <= 500 else 500)
        if len(self.clicks) == 0:
            self.clear()
            self.addItem(self.img)
            self.table.setItem(0, 1, QTableWidgetItem(str(mediaPlayer.position())))
            self.record["timestamp"]=mediaPlayer.position()
            self.table.setItem(0, 3, QTableWidgetItem(str(round(100 * x / 700, 2))))
            self.record["x1"]=round(100 * x / 700, 2)
            self.table.setItem(0, 4, QTableWidgetItem(str(round(100 * y / 500, 2))))
            self.record["y1"]=round(100 * y / 500, 2)
            point = pg.LineSegmentROI([(x, y), (x, y)], pen=(4, 9), movable=False, rotatable=False, resizable=False)
            self.addItem(point)
            self.clicks.append((x, y))
        elif len(self.clicks) == 1:
            self.table.setItem(0, 5, QTableWidgetItem(str(round(100 * x / 700, 2))))
            self.table.setItem(0, 6, QTableWidgetItem(str(round(100 * y / 500, 2))))
            self.record["x2"]=round(100 * x / 700, 2)
            self.record["y2"]=round(100 * y / 500, 2)
            self.clicks.append((x, y))
            line = pg.LineSegmentROI(self.clicks, pen=(4, 9), movable=False, rotatable=False, resizable=False)
            self.addItem(line)
            self.clicks[:] = []

    def clear(self):
        """
        Remove all items from the PlotItem.
        """
        for i in self.items[:]:
            self.removeItem(i)


class QPlayer(QPushButton):
    """
    Class for player buttons
    """
   

    def __init__(self, txt,table,record):
        super().__init__(txt)
        self.table=table
        self.record=record
        self.name = ""
        self.setGeometry(0, 0, 2, 2)
        self.setFixedSize(QSize(75, 50))

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.RightButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()
        elif event.button() == Qt.LeftButton:
           self.table.setItem(0, 0, QTableWidgetItem(str(self.name)))
           self.record["Player"]=self.name

        super(QPlayer, self).mousePressEvent(event)

    
    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() == 0:
                self.name, done1 = QInputDialog.getText(
                    self, 'Lineup', 'Enter player name:')
                self.setText(self.name)

                return

        super(QPlayer, self).mouseReleaseEvent(event)


class QEvent(QPushButton):
    """
    Class for event buttons
    """
    lasttag=None
    lastsub=None

    def __init__(self, txt, table,record,listbox ,*args):
        super().__init__(txt)
        self.table=table
        self.record=record
        self.listbox=listbox
        self.setFixedSize(QSize(75, 50))




    def onClick(self, event,sub,tag,layout):
        
        self.record["tag"]=[]
        self.record["sub"]=None
        for x in self.listbox:
            x.setOff()

        self.table.setItem(0, 2, QTableWidgetItem(str(self.text())))
        if QEvent.lastsub is None and QEvent.lasttag is None:
            layout.addWidget(sub,5,1,7,7)
            layout.addWidget(tag,9,1,11,7)
            
            
        else:
           QEvent.lastsub.hide()
           QEvent.lasttag.hide()
           layout.replaceWidget(QEvent.lastsub,sub)
           layout.replaceWidget(QEvent.lasttag,tag)
           sub.show()
           tag.show()
        
        self.record["event"]=self.text()
        QEvent.lasttag = tag
        QEvent.lastsub = sub
        


class QAction(QPushButton):
    """
    Class for possession buttons
    """
    lastbtn = None
    lastaction=""

    def __init__(self, txt,record=None ,*args):
        super().__init__(txt)
        self.record=record
        self.setFixedSize(QSize(120, 60))
        self.setCheckable(True)
        self.clicked.connect(self.press)




    def press(self):
        if QAction.lastbtn is None:
            QAction.lastbtn=self
            QAction.lastaction=self.text()
            self.setChecked(True)
            self.record["action"]=self.text()
        
        elif self.text() !=QAction.lastaction:
            QAction.lastbtn.setChecked(False)  
            QAction.lastbtn=self
            QAction.lastaction=self.text()
            self.setChecked(True)
            self.record["action"]=self.text()
                
        elif self.text() ==QAction.lastaction and self.isChecked()==False:
           self.record["action"]="No info"
           QAction.lastaction="No info"

        
           
        
        

class MultipleCheckbox(QWidget):

    def __init__(self,record, unique=False,*args):
        super().__init__()
        self.cb = []
        self.grid = QGridLayout()
        self.record=record
        self.unique=unique
        pos = -1
        for i in range(10):
            for j in range(10):
                pos +=1
                if pos<len(args):
                    self.cb.append(CheckBox(str(args[pos])))
                    self.grid.addWidget(self.cb[pos], i, j)

                else:
                    
                    self.grid.addLayout(QVBoxLayout(), i, j)
        
        
        for x in self.cb:
            x.addBox(self)

                   
        
        self.setLayout(self.grid)

    def setOff(self):
        for x in self.cb:
            x.setChecked(False)
    
    

class CheckBox(QCheckBox):
    

    def __init__(self, txt):
        super().__init__(txt)
        
        

    def addBox(self,box):
        self.box=box
        self.clicked.connect(self.check)

    def check(self):
        
        if self.box.unique==False:
            if self.isChecked() == True:
                self.box.record["tag"].append(self.text())
            else:
                self.box.record["tag"].remove(self.text())
        else:
            self.box.record["sub"]=self.text()
            for x in self.box.cb:
                if x.text()!=self.text():
                    x.setChecked(False)

class MainWindow(QMainWindow):
    
    
    def __init__(self ,*args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setRowCount(1)
        self.table.setFixedSize(self.screen().size().width()*0.5,self.screen().size().height()/10)
        self.table.setHorizontalHeaderLabels(["Player", "Time", "Events", "x1", "y1", "x2", "y2","ID Match","Period"])
        self.record={}
        self.record["tag"]=[]
        self.sub=None
        self.tag=[]
        self.setWindowIcon(QIcon("utils/soccer.ico"))
        self.setWindowTitle("SoccerTagging")
        self.create_dash()
        self.showMaximized()
        

    def create_dash(self):
        # Multimedia Player  Box
        self.openBtn = QPushButton("Open Video")
        self.openBtn.clicked.connect(self.open_file)   
        hbox = QHBoxLayout()
        hbox.addWidget(self.openBtn)
        vbox = QVBoxLayout()
        grid_action=QGridLayout()
        grid_action.addWidget(QAction("Offensive Possession",self.record),0,0)
        
        grid_action.addWidget(QAction("Difensive Possession",self.record),0,1)
        vbox.addLayout(grid_action)
        vbox.addLayout(hbox)    
        
        
        # Events Box

        mainLayout = QGridLayout()
        mainLayout.addWidget(QLabel(),5,0,7,7)
        mainLayout.addWidget(QLabel(),9,0,11,7)
        
        tableLayout = QVBoxLayout()
        mainLayout.addLayout(tableLayout,0,0,0,7)

        buttonLayout = QHBoxLayout()
        mainLayout.addLayout(buttonLayout,3,0,3,7)
        buttonLayout.addStretch(1)

        # Event buttons - Subevents Checkbox  - Tag Checkbox 
        passsub= MultipleCheckbox(self.record,True,"Croos","Simple Pass","Smart Pass","Launch","High Pass","Head Pass","Hand Pass")
        passtag= MultipleCheckbox(self.record,False,"Accurate", "Not Accurate","High","Low","Blocked")
        shotsub =MultipleCheckbox(self.record,True,"Reflexes","Save attempt","Shot")
        shottag = MultipleCheckbox(self.record,False,"Accurate","Not Accurate","Goal","Outside")
        duelsub = MultipleCheckbox(self.record,True,"Air duel","Offensive duel","Defensive Duel","Loose ball duel")
        dueltag=MultipleCheckbox(self.record,False,"Won", "Neutral","Lost")
        foulsub = MultipleCheckbox(self.record,True,"Foul (also Penalty)","Hand Foul")
        foultag=MultipleCheckbox(self.record,False,"Yellow Card", "Red Card")
        piecessub = MultipleCheckbox(self.record,True,"Set Pieces", "Corner", "Free Kick", "Free kick cross", "Free kick shot", "Goal kick","Penalty",
         "Throw in")
        piecestag =MultipleCheckbox(self.record,False,"Accurate", "Not Accurate","High","Low","Blocked","Direct","Indirect","Foot Right","Foot Left")
        otherssub = MultipleCheckbox(self.record,True,"Goalkeeper leaving line","Whistle", "Ball Out","Offside","Acceleration","Clearance","Touch")
        otherstag =MultipleCheckbox(self.record,False,"Accurate", "Not Accurate","Feint","Missed Ball")
        mainLayout.addWidget(QLabel(),5,1,7,7)
        mainLayout.addWidget(QLabel(),9,1,11,7)
     
        
        self.listbox=[passsub,passtag,shotsub,shottag,duelsub,dueltag,foulsub,foultag,piecessub,piecestag,otherssub,otherstag]

        passbtn = QEvent("Pass",self.table,self.record,self.listbox)
        shotbtn = QEvent("Shot",self.table,self.record,self.listbox)
        duelbtn = QEvent("Duel",self.table,self.record,self.listbox)
        foulbtn = QEvent("Foul",self.table,self.record,self.listbox)
        piecesbtn = QEvent("Set Pieces",self.table,self.record,self.listbox)
        othersbtn = QEvent("Others",self.table,self.record,self.listbox)
        
        
        

        buttonLayout.addWidget(passbtn)
        buttonLayout.addWidget(shotbtn)
        buttonLayout.addWidget(duelbtn)
        buttonLayout.addWidget(foulbtn)
        buttonLayout.addWidget(piecesbtn)
        buttonLayout.addWidget(othersbtn)
        buttonLayout.addStretch(1)

        tableLayout.addWidget(self.table)
        self.table.setFixedSize(self.size().width()*1.5, self.size().height()*0.175)
        

        tableLayout.addStretch(1)

        passbtn.clicked.connect(lambda ev: passbtn.onClick(ev,passsub,passtag,mainLayout))
        shotbtn.clicked.connect(lambda ev: shotbtn.onClick(ev, shotsub, shottag, mainLayout))
        duelbtn.clicked.connect(lambda ev: duelbtn.onClick(ev, duelsub, dueltag, mainLayout))
        foulbtn.clicked.connect(lambda ev:   foulbtn.onClick(ev,   foulsub,   foultag, mainLayout))
        piecesbtn.clicked.connect(lambda ev: piecesbtn.onClick(ev, piecessub, piecestag, mainLayout))
        othersbtn.clicked.connect(lambda ev: othersbtn.onClick(ev, otherssub, otherstag, mainLayout))
        


        

        # Players  Box

        self.grid_player = QGridLayout()
        btn1 = QPlayer("Player1", self.table,self.record)
        btn2 = QPlayer("Player2", self.table,self.record)
        btn3 = QPlayer("Player3", self.table,self.record)
        btn4 = QPlayer("Player4", self.table,self.record)
        btn5 = QPlayer("Player5", self.table,self.record)
        btn6 = QPlayer("Player6", self.table,self.record)
        btn7 = QPlayer("Player7", self.table,self.record)
        btn8 = QPlayer("Player8", self.table,self.record)
        btn9 = QPlayer("Player9", self.table,self.record)
        btn10 = QPlayer("Player10", self.table,self.record)
        btn11 = QPlayer("Player11", self.table,self.record)
        btn12 = QPlayer("Sub1",self.table,self.record)
        btn13 = QPlayer("Sub2",self.table,self.record)
        btn14 = QPlayer("Sub3",self.table,self.record)
        btn15 = QPlayer("Sub4",self.table,self.record)
        btn16 = QPlayer("Sub5",self.table,self.record)
        
        
        label = QLabel()
        pixmap = QPixmap("utils/bg2.png")
        label.setPixmap(pixmap.scaled(self.screen().size().width()/2.2,self.screen().size().height()/2.2))
        self.grid_player.addWidget(label,0,0,4,5)
        self.grid_player.addWidget(btn1, 0, 0)
        self.grid_player.addWidget(btn2, 0, 1)
        self.grid_player.addWidget(btn3, 0, 2)
        self.grid_player.addWidget(btn4, 1, 0)
        self.grid_player.addWidget(btn5, 1, 1)
        self.grid_player.addWidget(btn6, 1, 2)
        self.grid_player.addWidget(btn7, 2, 0)
        self.grid_player.addWidget(btn8, 2, 1)
        self.grid_player.addWidget(btn9, 2, 2)
        self.grid_player.addWidget(btn10, 3, 0)
        self.grid_player.addWidget(btn11, 3, 1)

        self.grid_player.addWidget(btn12, 0, 3)
        self.grid_player.addWidget(btn13, 0, 4)
        self.grid_player.addWidget(btn14, 0, 5)
        self.grid_player.addWidget(btn15, 1, 3)
        self.grid_player.addWidget(btn16, 1, 4)



        

        # Generation pitch cords Box
        self.pitch = Pitch2Coord(self.table,self.record)
        self.pitch.scene().sigMouseClicked.connect(lambda ev: self.pitch.onClick(ev, self.mp.mediaPlayer))


        # Final
        self.enter = QShortcut(QKeySequence(Qt.Key_Return), self)
        self.enter.activated.connect(self.save)
        self.grid = QGridLayout()
        self.grid.setColumnMinimumWidth(1, 900)
        self.grid.setRowMinimumHeight(0, 500)
        self.grid.addLayout(vbox, 0, 0)
        label = QLabel()
        pixmap = QPixmap("utils/bg3.png")
        label.setPixmap(pixmap.scaled(self.screen().size().width()/2,self.screen().size().height()/2))
        self.grid.addWidget(label, 1, 1)        
        self.grid.addLayout(mainLayout, 1, 1)
        
        
        
        self.grid.addLayout(self.grid_player, 0, 1)  
        
        self.grid.addWidget(self.pitch, 1, 0)
     
        
        dash = QWidget()
        self.grid.setColumnMinimumWidth(0,self.screen().size().width()/2)
        self.grid.setRowMinimumHeight(0,self.screen().size().height()/2)
        dash.setLayout(self.grid)
       
        self.setCentralWidget(dash)
    
    def save(self):
        
        with open(self.record["ID Match"]+".json","a") as f:
            json.dump(self.record, f)


        self.record.clear()
        self.record["action"]=QAction.lastaction
        self.record["ID Match"]=self.match.id
        self.record["Period"]=self.match.period
        self.table.removeRow(0)
        rowPosition = self.table.rowCount()
        self.table.insertRow(rowPosition)
        self.table.setItem(0, 7, QTableWidgetItem(str(self.match.id)))
        self.table.setItem(0, 8, QTableWidgetItem(str(self.match.period)))
        QEvent.lastsub.hide()
        QEvent.lasttag.hide()
        for x in self.listbox:
            x.setOff()
        
    def open_file(self):
            
            filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
            if filename!="":
                self.match=MatchInfo()
                if self.match.exec_() == QDialog.Accepted:
                        self.mp=PlayerVideo(filename)
                        self.record["ID Match"]=self.match.id
                        self.record["Period"]=self.match.period
                        self.table.setItem(0, 7, QTableWidgetItem(str(self.match.id)))
                        self.table.setItem(0, 8, QTableWidgetItem(str(self.match.period)))

    
    


               
class MatchInfo(QDialog):
    """
    Class for generic info of a match  that will be common to all events in the same match
    """
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Match Info')
        self.resize(500, 120)
        layout = QGridLayout()
        
        label_id = QLabel('<font size="4"> ID Match </font>')
        self.lineEdit_id = QLineEdit()
        self.lineEdit_id.setPlaceholderText('Please enter ID Match')
        layout.addWidget(label_id, 0, 0)
        layout.addWidget(self.lineEdit_id, 0, 1)


        label_period = QLabel('<font size="4"> Period </font>')
        self.lineEdit_period = QLineEdit()
        self.lineEdit_period.setPlaceholderText('Please enter Period')
        layout.addWidget(label_period, 1, 0)
        layout.addWidget(self.lineEdit_period, 1, 1)      

      


        

        button_enter = QPushButton('Enter')
        button_enter.clicked.connect(self.insert)
        self.enter=QShortcut(QKeySequence(Qt.Key_Return),self)
        self.enter.activated.connect(self.insert)
        layout.addWidget(button_enter, 3, 0, 1, 2)
        layout.setRowMinimumHeight(2, 75)
        self.setLayout(layout)
        

        
        

    def insert(self):
        msg=QMessageBox()
        self.id=self.lineEdit_id.text()
        self.period=self.lineEdit_period.text()
        self.accept()
        msg.setText('Entered')
        msg.exec_()
        