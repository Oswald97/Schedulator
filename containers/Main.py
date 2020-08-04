from PyQt5 import QtCore
from containers import Generate, Instructor, ResultViewer, Room, Subject, Section
from components import Settings, Database, Timetable, ImportExportHandler as ioHandler
from py_ui import Main
import json
import gc

class MainWindow(Main.Ui_MainWindow):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setupUi(parent)
        self.connectButtons()
        self.settings = Settings.getSettings()
        self.loadSettings()
        self.handleSettings()
        self.drawTrees()
        self.tabWidget.currentChanged.connect(self.tabListener)
        self.tabWidget.setCurrentIndex(0)

    # Connect Main component buttons to respective actions
    def connectButtons(self):
        self.btnInstrAdd.clicked.connect(lambda: self.openInstructor())
        self.btnRoomAdd.clicked.connect(lambda: self.openRoom())
        self.btnSubjAdd.clicked.connect(lambda: self.openSubject())
        self.btnSecAdd.clicked.connect(lambda: self.openSection())
        self.btnScenResult.clicked.connect(lambda: self.openResult())
        self.btnScenGenerate.clicked.connect(lambda: self.openGenerate())
        self.btnInstrImport.clicked.connect(self.importInstructors)
        self.btnRoomImport.clicked.connect(self.importRooms)
        self.btnSubjImport.clicked.connect(self.importSubjects)
        self.actionSave_As.triggered.connect(self.saveAs)
        self.actionOpen.triggered.connect(self.load)
        self.actionSettings.triggered.connect(lambda: self.tabWidget.setCurrentIndex(4))
        self.actionExit.triggered.connect(exit)
        self.actionNew.triggered.connect(lambda: self.new())

    # Initialize trees and tables
    def drawTrees(self):
        self.instrTree = Instructor.Tree(self.treeInstr)
        self.roomTree = Room.Tree(self.treeRoom)
        self.subjTree = Subject.Tree(self.treeSubj)
        self.secTree = Section.Tree(self.treeSec)

    # Handle component openings

    def openInstructor(self, id=False):
        Instructor.Instructor(id)
        self.instrTree.display()

    def openRoom(self, id=False):
        Room.Room(id)
        self.roomTree.display()

    def openSubject(self, id=False):
        Subject.Subject(id)
        self.subjTree.display()

    def openSection(self, id=False):
        Section.Section(id)
        self.secTree.display()

    def tabListener(self, index):
        self.instrTree.display()
        self.roomTree.display()
        self.subjTree.display()
        self.secTree.display()
        if index == 4:
            self.checkContents()

    def checkContents(self):
        conn = Database.getConnection()
        cursor = conn.cursor()
        disabled = False
        cursor.execute('SELECT id FROM rooms LIMIT 1')
        if cursor.fetchone():
            disabled = True
        cursor.execute('SELECT id FROM instructors LIMIT 1')
        if cursor.fetchone():
            disabled = True
        cursor.execute('SELECT id FROM sections LIMIT 1')
        if cursor.fetchone():
            disabled = True
        cursor.execute('SELECT id FROM subjects LIMIT 1')
        if cursor.fetchone():
            disabled = True
        self.timeStarting.setDisabled(disabled)
        self.timeEnding.setDisabled(disabled)
        self.btnScenGenerate.setDisabled(not disabled)
        conn.close()

    def openResult(self):
        ResultViewer.ResultViewer()

    def openGenerate(self):
        gc.collect()
        result = Generate.Generate()
        if not len(result.topChromosomes):
            return False
        self.openResult()

    def importInstructors(self):
        instructors = ioHandler.getCSVFile('enseignants')
        if instructors:
            instructors.pop(0)
            instructors.pop(0)
            blankSchedule = json.dumps(Timetable.generateRawTable())
            for instructor in instructors:
                Instructor.Instructor.insertInstructor([instructor[0], float(instructor[1]), blankSchedule])
            self.tabListener(0)

    def importRooms(self):
        rooms = ioHandler.getCSVFile('salles')
        if rooms:
            rooms.pop(0)
            rooms.pop(0)
            blankSchedule = json.dumps(Timetable.generateRawTable())
            for room in rooms:
                Room.Room.insertRoom([room[0], blankSchedule, room[1]])
            self.tabListener(1)

    def importSubjects(self):
        subjects = ioHandler.getCSVFile('matieres')
        if subjects:
            subjects.pop(0)
            subjects.pop(0)
            for subject in subjects:
                Subject.Subject.insertSubject(
                    [subject[1], float(subject[3]), subject[0], '', json.dumps([]), int(subject[4]), subject[2]])
        self.tabListener(2)

    def saveAs(self):
        ioHandler.saveAs()

    def load(self):
        ioHandler.load()
        self.tabWidget.setCurrentIndex(0)
        self.tabListener(0)

    def loadSettings(self):
        self.timeStarting.setTime(QtCore.QTime(int(self.settings['starting_time']), 0))
        self.timeEnding.setTime(QtCore.QTime(int(self.settings['ending_time']) + 1, 0))
        if self.settings['lunchbreak']:
            self.radioLunchYes.setChecked(True)
        else:
            self.radioLunchNo.setChecked(False)

    # Handle Settings
    def handleSettings(self):

        self.timeStarting.timeChanged.connect(self.handleStartingTime)
        self.timeEnding.timeChanged.connect(self.handleEndingTime)
        self.radioLunchYes.toggled.connect(lambda state: self.updateSettings('lunchbreak', state))

    def handleStartingTime(self, time):
        if time.hour() >= self.settings['ending_time']:
            self.timeStarting.setTime(QtCore.QTime(int(self.settings['starting_time']), 0))
        else:
            self.updateSettings('starting_time', time.hour())

    def handleEndingTime(self, time):
        if (time.hour()) - 1 <= self.settings['starting_time']:
            self.timeEnding.setTime(QtCore.QTime(int(self.settings['ending_time']) + 1, 0))
        else:
            self.updateSettings('ending_time', (time.hour()) - 1)

    def handleMinPop(self, value):
        if value > self.settings['maximum_population']:
            self.editMinPop.setValue(self.settings['minimum_population'])
        else:
            self.updateSettings('minimum_population', value)

    def handleMaxPop(self, value):
        if value < self.settings['minimum_population']:
            self.editMaxPop.setValue(self.settings['maximum_population'])
        else:
            self.updateSettings('maximum_population', value)

    def handleMatrix(self, key, value, obj):
        difference = self.matrix[key] - value
        if self.matrixSum - difference > 100:
            obj.setValue(self.matrix[key])
        else:
            self.updateSettings('evaluation_matrix', value, key)
        self.matrixSum = sum(self.settings['evaluation_matrix'].values())
        self.matrix = self.settings['evaluation_matrix']
        self.lblTotal.setText('Total: {}%'.format(self.matrixSum))

    def updateSettings(self, key, value, secondKey=False):
        Settings.setSettings(key, value, secondKey)
        self.settings = Settings.getSettings()

    def new(self):
        ioHandler.removeTables()
        Database.setup()
        self.tabListener(0)
