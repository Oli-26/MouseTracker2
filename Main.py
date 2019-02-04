import PyQt5 
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from PyQt5.QtWidgets import QMainWindow,QWidget, QPushButton, QAction, QComboBox, QGridLayout, QLineEdit, QMessageBox, QCheckBox
from PyQt5.QtGui import QPainter, QColor, QBrush, QIcon, QFont
from PyQt5.QtCore import QRect, QPoint, QTimer
import sys
from pynput.mouse import Controller
from inputs import devices, get_gamepad
import random
import pygame 
from threading import Timer
import jsonify
import json

from os import listdir
import os

class StartWindow(QMainWindow):
    def __init__(self):
        super(StartWindow, self).__init__()
       
        ## Generic window set up.
        self.setWindowTitle("Main Menu")
        self.layout = QGridLayout()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget) 
        self.main_widget.setLayout(self.layout)
        
        ## This object holds the settings set by the user. 
        self.infoPackage = InfoPackage()
       
        ## Add buttons and connect them to actions.
        startButton = QPushButton("Start")
        editButton = QPushButton("Edit")
        
        self.layout.addWidget(startButton, 0, 0)
        self.layout.addWidget(editButton, 1, 0)
        
        startButton.clicked.connect(self.openMainWindow)
        editButton.clicked.connect(self.openEditWindow)
        self.show()
        
        
    
    def openMainWindow(self):
        self.mainWindow = MainWindow(self, self.infoPackage)

    def openEditWindow(self):
        self.editWindow = EditWindow(self, self.infoPackage)
     
    def getInfoPackage(self):
        return self.infoPackage
        

class InfoPackage():
    def __init__(self):
        ## Trail settings.
        self.Actions = list()
        self.trial_length = 20
        self.style = 0
        self.show_time = False
        self.show_points = False
        self.add_points = True
        self.remove_points = True
        self.start_points = 0
        self.blocking = True
        self.color_time = False
        self.filename = "filename"
    
        ## These lists are required for exporting to excel. 
        self.style_list = ["light", "dark", "strange", "no feedback"] 
        self.action_types = ["sensitivity" , "square1x", "square2x", "square1width", "square2width", "invert"]
        
    def setActions(self, actionList):
        self.Actions = actionList
    
    def setTrialTime(self, time, show, color):
        self.trial_length = time
        self.show_time = show
        self.color_time = color
        
    def setStyle(self, type, block):
        self.style = type
        self.blocking = block
        
    def setPoints(self, amount, showPoints, addPoints, removePoints):
        self.start_points = amount
        self.show_points = showPoints
        self.add_points = addPoints
        self.remove_points = removePoints
        
    def setFileName(self, name):
        self.filename = name
        
class EditAction():
    def __init__(self, type, value, time):
        self.type = type;
        self.value = value; 
        self.time = time;
 
class EditWindow(QMainWindow):
    def __init__(self, parent, info):
        super(EditWindow, self).__init__()
        
        ## General window set up.
        self.info = info
        self.parent = parent
        self.layout = QGridLayout()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget) 
        self.main_widget.setLayout(self.layout)
        self.setWindowTitle("Options")
        
        
        ###
        ## Global settings
        ###
        
        # For ease of styling
        # An increment in maxIndex is symbolised by ####
        self.maxIndex = 0
         
        # Create larger font for points
        titleFont = QFont("Times", 10, QtGui.QFont.Bold) 
        self.saveTag = QLabel("Save filename: ")
        self.saveInput = QLineEdit(self.info.filename)
        
        self.layout.addWidget(self.saveTag, self.maxIndex, 0)
        self.layout.addWidget(self.saveInput, self.maxIndex, 1)
        
        ####
        self.maxIndex = self.maxIndex+1
        self.timeTag = QLabel("Trial length (s)")
        self.timeTag.setFont(titleFont)
        self.layout.addWidget(self.timeTag, self.maxIndex, 0)
        
        ####
        self.maxIndex = self.maxIndex+1
        self.timeInput = QLineEdit(str(self.info.trial_length));
        self.showTime = QCheckBox("Show time")
        if(self.info.show_time == 1):
            self.showTime.toggle()
        self.colorTime = QCheckBox("Color time")
        if(self.info.color_time == 1):
            self.colorTime.toggle()
        
        self.layout.addWidget(self.timeInput, self.maxIndex, 0)
        self.layout.addWidget(self.showTime, self.maxIndex, 1)
        self.layout.addWidget(self.colorTime, self.maxIndex, 2)
        
        ####
        self.maxIndex = self.maxIndex+1
        pointLabel = QLabel("Points")
        self.layout.addWidget(pointLabel, self.maxIndex, 0)
        
        ####
        self.maxIndex = self.maxIndex+1
        self.showPoints = QCheckBox("Show Points")
        if(self.info.show_points == 1):
            self.showPoints.toggle()
        
        self.startingPoints = QLineEdit(str(self.info.start_points))
        self.addPoints = QCheckBox("Gain points")
        if(self.info.add_points == 1):
            self.addPoints.toggle()
      
        self.layout.addWidget(self.showPoints, self.maxIndex, 1)
        self.layout.addWidget(self.startingPoints, self.maxIndex, 0)
        self.layout.addWidget(self.addPoints, self.maxIndex, 2)
        
        ####
        self.maxIndex = self.maxIndex+1
        self.blocking = QCheckBox("Blocking")
        if(self.info.blocking):
            self.blocking.toggle()
        self.removePoints = QCheckBox("Lose points")
        if(self.info.remove_points == 1):
            self.removePoints.toggle()
            
        self.layout.addWidget(self.blocking, self.maxIndex, 1)
        self.layout.addWidget(self.removePoints, self.maxIndex, 2)
        
        ####
        self.maxIndex = self.maxIndex+1
        self.styleTag = QLabel("Styles")
        self.layout.addWidget(self.styleTag, 6, 0)
        self.styleTag.setFont(titleFont)
         
        ####
        self.maxIndex = self.maxIndex+1
        self.style = QComboBox(self)
        self.style.addItem("light theme")
        self.style.addItem("dark theme")
        self.style.addItem("strange theme")
        self.style.addItem("No feedback theme")
        self.style.setCurrentIndex(self.info.style)
        pointLabel.setFont(titleFont)
        self.layout.addWidget(self.style, self.maxIndex, 0)

        ###
        ## Update settings.
        ###
        self.Actions = self.info.Actions
        self.ActionsTypes = list()
        self.ActionsValues = list()
        self.ActionsTimes = list()
        
        addButton = QPushButton("+")
        removeButton = QPushButton("-")
        submitButton = QPushButton("Save")
        
        typeTag = QLabel("type")
        valueTag = QLabel("value")
        timeTag = QLabel("time in sec")
        
        
        addButton.clicked.connect(self.add)
        removeButton.clicked.connect(self.remove)
        submitButton.clicked.connect(self.submit)
        
        
        ####
        self.maxIndex = self.maxIndex+1
        self.layout.addWidget(addButton, self.maxIndex, 0)
        self.layout.addWidget(removeButton, self.maxIndex, 1)
        self.layout.addWidget(submitButton, self.maxIndex, 2)
        
        ####
        self.maxIndex = self.maxIndex+1
        self.layout.addWidget(typeTag, self.maxIndex, 0)
        self.layout.addWidget(valueTag, self.maxIndex, 1)
        self.layout.addWidget(timeTag, self.maxIndex, 2)
        
        self.fill()
        self.show()
    
    
    
    def fill(self):
        '''
            Add actions for each actions currently in aciton list in info package.
        '''
        for a in self.Actions:
            self.add(a.type, a.value, a.time)
        
        
        
    
    def add(self, ty = 0, v = "1", ti = "0"):
        '''
            Add new action. Increment maxIndex.
            Creates a combo box and two inputs for value and time.
        '''
        self.typeBox = QComboBox(self)
        
        self.typeBox.addItem("sensitivity")
        self.typeBox.addItem("square1x(%)")
        self.typeBox.addItem("square2x(%)")
        self.typeBox.addItem("square1width")
        self.typeBox.addItem("square2width")
        self.typeBox.addItem("invert(1/0)")
        self.typeBox.setCurrentIndex(ty)
        
        offset = 9
        
        
        self.ActionsTypes.append(self.typeBox)
        
        currentIndex = len(self.ActionsTypes)
        
        self.layout.addWidget(self.typeBox, self.maxIndex, 0)
        
        
        self.valueBox = QLineEdit(v)
        self.ActionsValues.append(self.valueBox)
        self.layout.addWidget(self.valueBox,  self.maxIndex, 1)
    
        self.timeBox = QLineEdit (ti)
        self.ActionsTimes.append(self.timeBox)
        self.layout.addWidget(self.timeBox,  self.maxIndex, 2)
        self.maxIndex = self.maxIndex + 1
            
    def remove(self):
        '''
            Removes last action.
        '''
        if(len(self.ActionsTimes) != 0):
            self.maxIndex = self.maxIndex - 1
            self.ActionsTypes.pop().deleteLater()
            self.ActionsValues.pop().deleteLater()
            self.ActionsTimes.pop().deleteLater()
            
    def submit(self):
        '''
            Submit all information for information package.
        '''
        
        ## Initalise variables.
        infoPackage = self.parent.getInfoPackage()
        temp_list = list()
        i = 0
        startPoints = 0
        
        ## Catch if startpoints is not a number.
        try:
            startPoints = int(self.startingPoints.text())
        except:
            startingPoints = 0
            
   
        ## Set all other options.    
        self.info.setFileName(self.saveInput.text())
        self.info.setTrialTime(self.timeInput.text(), self.showTime.isChecked(), self.colorTime.isChecked())
        self.info.setStyle(self.style.currentIndex(), self.blocking.isChecked())
        self.info.setPoints(startPoints, self.showPoints.isChecked(), self.addPoints.isChecked(), self.removePoints.isChecked())
      
        
        ## Create actions list from inputs.
        for i in range(0, len(self.ActionsTypes)):
            type = self.ActionsTypes[i].currentIndex()
            val = self.ActionsValues[i].text()
            time = self.ActionsTimes[i].text()
            
            # Create action object.
            temp_action = EditAction(type, val, time)
            
            # Add action object to queue.
            temp_list.append(temp_action)
        
        # Assign queue to info package.
        self.info.setActions(temp_list)
        # Close settings window.
        self.close()
        
class MainWindow(QMainWindow):
    def __init__(self, parent, info):
        super(MainWindow, self).__init__()
        
        ## General initalisation. 
        self.setWindowTitle("Play")
        self.info = info
        self.recorder = Recorder()
        
        
        ## Set color scheme depending on style selected.
        if(self.info.style == 0):
            self.background_color = "white"
            self.square_color_normal = "grey"
            self.square_color_score = "green"
            self.square_color_fail = "red"
        if(self.info.style == 1):
            self.background_color = "grey"
            self.square_color_normal = "white"
            self.square_color_score = "green"
            self.square_color_fail = "red"
        if(self.info.style == 2):
            self.background_color = "blue"
            self.square_color_normal = "yellow"
            self.square_color_score = "green"
            self.square_color_fail = "red"
        if(self.info.style == 3):
            self.background_color = "white"
            self.square_color_normal = "grey"
            self.square_color_score = "grey"
            self.square_color_fail = "grey"
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(self.background_color))
        self.setPalette(p)

        ## Create first rectangle details.
        self.begin_one = QtCore.QPoint()
        self.end_one = QtCore.QPoint()
        self.color_one = QtGui.QColor(self.square_color_normal)
        self.width_one= 140
        self.x_one = 300
        
        ## Create second rectangle details.
        self.begin_two = QtCore.QPoint()
        self.end_two = QtCore.QPoint()
        self.color_two = QtGui.QColor(self.square_color_normal)
        self.width_two = 140
        self.x_two = 1500
        
        ## Initalise Mouse 
        self.mouse = Controller()
        
        
        ## Create exit menu option.
        exitAction = QAction(QIcon('exit.png'), "exit", self)
        exitAction.setShortcut('Ctrl+E')
        exitAction.triggered.connect(self.close_call)
      
        ## Add menu bar.
        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(exitAction)
        
        ## Initalise pygame and configer depending on if a joystick is available.
        pygame.init()
        if(pygame.joystick.get_count() < 1):
            self.type = "mouse"
        else:
            print("Joystick connected.")
            self.my_joystick = pygame.joystick.Joystick(0)
            self.my_joystick.init()
            self.type = "joystick"
       

        ## Initalise basic variables. 
        # This identifies mouse position, be it from the mouse or another controller.
        self.mouse_indicator = 0
        # This indicates the current sensitivity.
        self.sensitivity = 1
        # This indcates if the mouse movement is flipped.
        self.flipSensitivity = 0
        # This indicates the default y position of the rectangles on the screen.
        self.default_y = 300
        # This initalises the variable indicating the current activated square. 0 implies none are active.
        self.current_activated = 0
        # This blocks points from dropping after the an inital point has been lost.
        self.lose_block = 0
        # Inialises points based on Info class.
        self.points = self.info.start_points
        # Signal for trail status. Required because of the way pyqt5 uses threading.
        self.trial_over = False
        
        # Initalise square positions.
        self.set_first_square(300, self.default_y, 140, 80)
        self.set_second_square(1500, self.default_y, 140, 80)
        
        # If time is active, create label and initalise it.
        if(self.info.show_time):
            self.time_left = int(self.info.trial_length)
            self.timeLabel = QLabel(str(self.info.trial_length) + " seconds", self)
            self.timeLabel.setStyleSheet('color: green')
            timeFont = QFont()
            self.timeLabel.setWordWrap(True)   
            self.timeLabel.setFont(timeFont)
            self.timeLabel.move(20, 25)
            self.clock_timer = QTimer()
            self.clock_timer.timeout.connect(self.update_time)
            self.clock_timer.start(1000)
       
        # If show points is active, create label and initalise it.    
        if(self.info.show_points):
            self.pointsLabel = QLabel(str(self.points), self)
            pointsFont = QFont("Times", 15, QtGui.QFont.Bold) 
            self.pointsLabel.move(850,150)
            self.pointsLabel.setFont(pointsFont)

      
        # Maximize window and add auther tag.
        self.initalize_tag()
        self.showMaximized()
        self.show()
        
        # Create timer to call tracking function every 100ms.
        self.timer = QTimer()
        self.timer.timeout.connect(self.track)
        self.timer.start(100)
        
        
        # Create timer for each action set in actions list.
        for action in self.info.Actions:
            t = Timer(float(action.time), self.call_action, [action])
            t.start()
            
        # Create timer to indicate end of trial.    
        t = Timer(float(self.info.trial_length), self.end_trial)
        t.start()
       
       
       
    def update_time(self):
        if(self.trial_over):
            return;
        self.time_left = self.time_left-1
        self.timeLabel.setText(str(self.time_left) + " seconds")
        
        ## If color time is active, set color depending on time relative to initial time.
        if(self.info.color_time and self.time_left < int(self.info.trial_length)/2 and self.time_left > int(self.info.trial_length)/4):
            self.timeLabel.setStyleSheet('color: orange')
        elif(self.info.color_time and self.time_left < int(self.info.trial_length)/4):
            self.timeLabel.setStyleSheet('color: red')
        
        
    def end_trial(self):
        self.trial_over = True
        
       
    def closeEvent(self, event):
        print ("Closing")
        self.trial_over = True
        self.timer.stop()
    
    def call_action(self, action):
        '''
            Handles all action calling from actions list.
            Returns if trial time is already over.
        '''
        if(self.trial_over):
            print("Failed to call action. Trial already finished.")
            return;
        if(action.type == 0):
            self.sensitivity = float(action.value)
        if(action.type == 1):
            self.x_one = xWidth = self.geometry().width()*float(action.value)/100
            self.set_first_square(self.x_one, self.default_y, self.width_one, 80)
        if(action.type == 2):
            self.x_two = xWidth = self.geometry().width()*float(action.value)/100
            self.set_second_square(self.x_two, self.default_y, self.width_two, 80)
        if(action.type == 3):
            self.width_one = float(action.value)
            self.set_first_square(self.x_one, self.default_y, self.width_one, 80)
        if(action.type == 4):
            self.width_two = float(action.value)
            self.set_second_square(self.x_two, self.default_y, self.width_two, 80)
        if(action.type == 5):
            self.flipSensitivity = float(action.value)
        self.update_labels()
        
    def close_call(self):
        self.timer.stop()
        self.close()
    
    def set_first_square(self, x, y, w, h):
        self.begin_one = QtCore.QPoint((x - w/2), (y - h/2))
        self.end_one =  QtCore.QPoint((x + w/2), (y + h/2))
        
    def set_second_square(self, x, y, w, h):
        self.begin_two = QtCore.QPoint((x - w/2), (y - h/2))
        self.end_two =  QtCore.QPoint((x + w/2), (y + h/2))
    
    
    def update_labels(self):
        if(self.info.show_points== 1):
            self.pointsLabel.setText(str(self.points))
        
    def paintEvent(self, event):
        '''
            Draw rectangles. Two for goals, one for indicator.
        '''
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(self.color_one)  
        qp.setBrush(br)   
        qp.drawRect(QtCore.QRect(self.begin_one, self.end_one))
        
        
        br = QtGui.QBrush(self.color_two)  
        qp.setBrush(br)   
        qp.drawRect(QtCore.QRect(self.begin_two, self.end_two))
        
        
        br = QtGui.QBrush(QtGui.QColor("black"))
        qp.setBrush(br)
        qp.drawRect(self.mouse_indicator-10, self.default_y , 20, 20)

    def get_position(self):
        '''
            Get position dependant on wether the user is using a mouse or a joystick.
        '''
        if(self.type == "mouse"):
            return self.mouse.position[0]
        elif(self.type == "joystick"):
            pygame.event.pump()
            #print(self.my_joystick.get_axis(0))
            return (1+self.my_joystick.get_axis(0))*self.geometry().width()/2
        
    def track(self):
        '''
            This is effectively the main loop of the 'game'.
            This functions moves the mouse, handles color changes and other effects.
        '''
        
        # If trail is over, indicated by signal "trial_over" then end the trial. Begin saving process.
        if(self.trial_over == True):
            if(self.timer):
                self.timer.stop()
            QMessageBox.about(None, "Finish", "You finished with " + str(self.points) +" points.")    
            SaveFileWindow(self)
            self.close_call()
           
    
    
        # Get width of window.
        xWidth = self.geometry().width()
        
        # Get position of mouse or controler (x axis)
        self.pos = self.get_position()
        
        # Record position of input, before it is adjusted to sensitivity.
        self.recorder.record_pos(self.pos)
        
        # Adjust position by sensitivity settings.
        self.mouse_indicator = ((self.pos - (xWidth/2))*self.sensitivity) + (xWidth/2)
        
        # Variables for non blocking mode.
        not_in_square1 = False
        not_in_square2 = False
       
        # Flip position if flip setting is active.
        if(self.flipSensitivity == 1):
            self.mouse_indicator = ((-self.pos + (xWidth/2))*self.sensitivity) + (xWidth/2)
       
        # Check rect one
        if(self.mouse_indicator < self.end_one.x() and self.mouse_indicator > self.begin_one.x()):
            if(self.current_activated != 1):
                ## Pass case, gain a point.
                self.color_one.setNamedColor(self.square_color_score)
                self.color_two.setNamedColor(self.square_color_normal)
                self.current_activated = 1
                self.gain()
                self.lose_block = 0
        else:
            not_in_square1 = True      
        if(self.mouse_indicator < self.begin_one.x() and self.lose_block != 1):
            ## Fail case, lose a point.
            self.color_one.setNamedColor(self.square_color_fail)
            self.lose()
            self.lose_block = 1
          
        
        # Check rect two
        if(self.mouse_indicator < self.end_two.x() and self.mouse_indicator > self.begin_two.x()):
            if(self.current_activated != 2):
                ## Pass case, gain a point.
                self.color_two.setNamedColor(self.square_color_score) 
                self.color_one.setNamedColor(self.square_color_normal)
                self.current_activated = 2
                self.gain()
                self.lose_block = 0
        else:
            not_in_square2 = True
            
        if(self.mouse_indicator > self.end_two.x() and self.lose_block != 1):
            ## Fail case, lose a point.
            self.color_two.setNamedColor(self.square_color_fail)   
            self.lose()            
            self.lose_block = 1
       
        # If blocking is not active, then reset current square if between the two.
        if(not_in_square1 and not_in_square2 and self.info.blocking == False and self.mouse_indicator > self.end_one.x() and self.mouse_indicator < self.begin_two.x()):
            self.current_activated = 0
        
        # Update the Ui.
        self.update()

   
    def gain(self):
        if(self.info.add_points):
            self.points = self.points+1
            self.update_labels()
        
    def lose(self):
        if(self.info.remove_points):
            self.points = self.points-1
            
            if(self.points < 0):
                self.points = 0
            self.update_labels()
        

        
    def initalize_tag(self):
        titleLabel = QLabel("By Oliver Holder, \nRuud den Hartigh", self)
        titleLabel.move(300,1300)

class Recorder():
    def __init__(self):
        self.mouseX = list()
        
        
    def record_pos(self, x):
       self.mouseX.append(x)
    
        
    def get_x_list(self):
        return self.mouseX
    
        

class SaveFileWindow(QMainWindow):
     def __init__(self, parent=None):
        super(SaveFileWindow, self).__init__(parent)
        self.setWindowTitle("Save file as:")
        self.parent = parent
        self.layout = QGridLayout()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget) 
        self.main_widget.setLayout(self.layout)
        
        self.file_name_label = QLabel(str(self.parent.info.filename))
        self.layout.addWidget(self.file_name_label, 0, 0)
        
        self.save_button = QPushButton("Save file")
        self.save_button.clicked.connect(self.save_file)
        self.layout.addWidget(self.save_button, 0, 1)
        
        
        
        self.show()

     def save_file(self):
        '''
            Attempts to save file with the name in the text box.
            Saves both questions and form.
        '''
        file_name = self.parent.info.filename
        
        # If there is no filename, then do nothing.
        if (file_name == ""):
            return 
            
        for name in listdir("saves/"):
            if name == (self.parent.info.filename + ".txt") :
                buttonReply = QMessageBox.question(self, 'Attempted Overwrite', "Are you sure you want to overwrite" + " [" + file_name + "]", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if buttonReply == QMessageBox.No:
                    return
                
                
            
        try:
            f = open("saves/" + file_name + ".txt", "w+")
            f.write(str(file_name) + "  " + str(self.parent.points) + "//")
            f.write(str(self.parent.info.trial_length) + "//")
            f.write("Data (" + str(self.parent.points)  + ") | Mouse x position |  - " + json.dumps(self.parent.recorder.get_x_list()) + "//")
            f.write("~")    
       
            f.close()
        except:
           print("Saving failed")
           
           
        ## From here it is saving the file in excel
        import xlwt
    
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet("my sheet")
    
        xPos = 0        
        yPos = 0
           
    
        # Add in time stamps for data
        
        tempList = self.parent.recorder.get_x_list()
        if(not len(self.parent.recorder.get_x_list()) == 0):
            worksheet.write(0, 0, "Time (in ms)")
            worksheet.write(0, 1, "X position")
            worksheet.write(0, 2, "X position (normalized)")
            time_index = 1
            yPos = 1
            
            for n in tempList:
                worksheet.write(yPos, 0, str(yPos*100))
                worksheet.write(yPos, 1, str(n))
                
                norm = (int)(100*(n/self.parent.geometry().width()))
                worksheet.write(yPos, 2, str( norm/100))
                yPos = yPos+1
                
                
       
        
        worksheet.write(0, 3, "Points = " + str(self.parent.points))
        
        
        ## Trial options
        worksheet.write(0, 4, "Length = " + str(self.parent.info.trial_length))
        worksheet.write(1, 4, "Start points = " + str(self.parent.info.start_points))
        
        
        if(self.parent.info.show_points):
            worksheet.write(2,4, "Show points: true")
        else:
            worksheet.write(2,4, "Show points: false")
        
        
        
        if(self.parent.info.add_points):
            worksheet.write(3,4, "Add points: true")
        else:
            worksheet.write(3,4, "Add points: false")
        

        if(self.parent.info.remove_points):
            worksheet.write(4,4, "Remove points: true")
        else:
            worksheet.write(4,4, "Remove points: false")
        
        
        if(self.parent.info.show_time):
            worksheet.write(5,4, "Show time: true")
        else:
            worksheet.write(5,4, "Show time: false")
        
        if(self.parent.info.color_time):
           worksheet.write(6,4, "Color time: true")
        else:
            worksheet.write(6,4, "Color time: false")
        
        if(self.parent.info.blocking):
            worksheet.write(7,4, "blocking: true")
        else:
            worksheet.write(7,4, "blocking: false")
        
      
        
        worksheet.write(8,4, "Style: " + self.parent.info.style_list[self.parent.info.style])
        
        
        worksheet.write(0, 5, "Actions [type, value, time]")
        yPos = 1
        for n in self.parent.info.Actions:
            worksheet.write(yPos, 5, "[" + str(self.parent.info.action_types[n.type]) + ", " + str(n.value) + ", " + str(n.time) + "]")
            yPos = yPos+1
        workbook.save("saves/" + self.parent.info.filename + ".xls")
        self.close()
                  
       
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    startWindow= StartWindow()
    sys.exit(app.exec_())