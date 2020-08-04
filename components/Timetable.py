from PyQt5 import QtCore, QtWidgets, QtGui
from components import Settings, TableModel
import json


# Used for displaying toggable timetable
class Timetable:
    def __init__(self, table, data=False):
        self.table = table
        header = [['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']]
        with open('timeslots.json') as json_file:
            timeslots = json.load(json_file)['timeslots']
        settings = Settings.getSettings()
        header.append(timeslots[settings['starting_time']:settings['ending_time'] + 1])
        self.data = data
        if not data:
            self.data = []
            for i in range(settings['ending_time'] + 1 - settings['starting_time']):
                self.data.append(['Disponible', 'Disponible', 'Disponible', 'Disponible', 'Disponible', 'Disponible'])
        self.model = TimetableModel(header, self.data)
        table.setModel(self.model)
        table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        table.clicked.connect(self.toggleCells)
        table.horizontalHeader().sectionClicked.connect(self.toggleCells)
        table.verticalHeader().sectionClicked.connect(self.toggleCells)
        table.findChild(QtWidgets.QAbstractButton).clicked.connect(self.toggleCells)

    # Toggles the availability and changes UI color to appropriate color
    def toggleCells(self):
        indexes = self.table.selectionModel().selectedIndexes()
        for i in indexes:
            value = 'Disponible' if self.data[i.row()][i.column()] == 'Indisponible' else 'Indisponible'
            if value == 'Disponible':
                self.table.setStyleSheet('selection-background-color: rgb(46, 204, 113); selection-color: black;')
            else:
                self.table.setStyleSheet('selection-background-color: rgb(231, 76, 60); selection-color: black;')
            self.model.setData(i, value)

    def getData(self):
        return self.data


# Timetable model that provides color support for availability status
class TimetableModel(TableModel.TableModel):
    def __init__(self, header, data):
        super().__init__(header, data)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()
        elif role == QtCore.Qt.BackgroundRole:
            if self.data[index.row()][index.column()] == 'Disponible':
                return QtGui.QBrush(QtGui.QColor(46, 204, 113))
            else:
                return QtGui.QBrush(QtGui.QColor(231, 76, 60))
        elif role != QtCore.Qt.DisplayRole:
            return QtCore.QVariant()
        return self.data[index.row()][index.column()]


def generateRawTable():
    settings = Settings.getSettings()
    data = []
    for i in range(settings['ending_time'] + 1 - settings['starting_time']):
        data.append(['Disponible', 'Disponible', 'Disponible', 'Disponible', 'Disponible', 'Disponible'])
    return data
