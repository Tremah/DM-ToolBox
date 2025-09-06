import math
import sys

from PySide6.QtCore import Qt, QPoint
from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QGuiApplication
from PySide6.QtWidgets import (
  QApplication,
  QMainWindow,
  QGridLayout,
  QWidget,
  QStackedWidget,
  QSizeGrip, QDockWidget
)
from PySide6.QtSql import QSqlTableModel

import database as db
import dice_roller as dr
import creature_editor as ce
import database_manager as dbm
import table_generator as tbg
import tools as tls
import data_models as dm
import log as log

## Main Window ##
class MainWindow(QMainWindow):
  def __init__(self):
    super().__init__()

    # Setup database
    db.openConnection('QSQLITE', 'db/database.sqlite')
    dm.getDataModels().defineModels()

    self.setWindowTitle("DM ToolBox")

    # Window Size
    _screenSize = QGuiApplication.primaryScreen().size()
    _windowSizeMultiplier = 0.8
    _windowWidth = _screenSize.width() * min(_windowSizeMultiplier, 1)
    _windowHeight = _screenSize.height() * min(_windowSizeMultiplier, 1)
    self.setMinimumSize(QSize(math.floor(_windowWidth), math.floor(_windowHeight)))

    # Window Position
    _windowPosX = math.floor(_screenSize.width() * 0.5) - math.floor(_windowWidth * 0.5)
    _windowPosY = math.floor(_screenSize.height() * 0.5) - math.floor(_windowHeight * 0.5) - 200
    self.move(_windowPosX, _windowPosY)

    creatureEditor = ce.CreatureEditor()
    diceRoller = dr.DiceRoller()
    databaseManager = dbm.DatabaseManager()
    tableGenerator = tbg.TableGenerator()
    tools = tls.Tools()

    ## Layout ##
    self.baseGridLayout = QGridLayout()
    self.centralWidget = QWidget()
    self.centralWidget.setLayout(self.baseGridLayout)
    self.setCentralWidget(self.centralWidget)
    self.baseGridLayout.addWidget(QSizeGrip(self.centralWidget), 10, 10)

    self.stackedWidget = QStackedWidget()
    self.baseGridLayout.addWidget(self.stackedWidget, 0, 0)

    self.stackedWidget.addWidget(creatureEditor)
    self.stackedWidget.addWidget(diceRoller)
    self.stackedWidget.addWidget(databaseManager)
    self.stackedWidget.addWidget(tableGenerator)
    self.stackedWidget.addWidget(tools)
    self.stackedWidget.setCurrentIndex(4)

    ## Menus ##
    self.mainMenu = self.menuBar()

    # File menu
    fileMenu = self.mainMenu.addMenu('File')
    button_action = QAction("Close", self)
    button_action.triggered.connect(self.closeApplication)
    fileMenu.addAction(button_action)

    # Dice Roller
    button_action = QAction("Dice Roller", self)
    button_action.triggered.connect(lambda clicked: self.changeWidget(diceRoller))
    self.mainMenu.addAction(button_action)

    # Creature Editor
    button_action = QAction("Creature Editor", self)
    button_action.triggered.connect(lambda clicked: self.changeWidget(creatureEditor))
    self.mainMenu.addAction(button_action)

    # Table Generator
    button_action = QAction("Table Generator", self)
    button_action.triggered.connect(lambda clicked: self.changeWidget(tableGenerator))
    self.mainMenu.addAction(button_action)

    # Database Manager
    button_action = QAction("Database Manager", self)
    button_action.triggered.connect(lambda clicked: self.changeWidget(databaseManager))
    self.mainMenu.addAction(button_action)

    # Tools
    button_action = QAction("Tools", self)
    button_action.triggered.connect(lambda clicked: self.changeWidget(tools))
    self.mainMenu.addAction(button_action)

  def changeWidget(self, widget):
    self.stackedWidget.setCurrentWidget(widget)

  def closeEvent(self, event):
    self.closeApplication()

  def closeApplication(self):
    db.closeConnection()
    app.shutdown()

app = QApplication(sys.argv)

def main():
  _logWindow = log.LogWindow()
  _mainWindow = MainWindow()

  _mainWindow.show()

  _dock = QDockWidget("Logs", _mainWindow)
  _dock.setWidget(_logWindow)
  _dock.setAllowedAreas(Qt.DockWidgetArea.RightDockWidgetArea)
  _mainWindow.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, _dock)



  app.setStyleSheet("QGroupBox{border: 1px solid #555; margin-top: 9px;} QGroupBox::title {subcontrol-origin: margin; left: 15px; padding: 0px 1px 0px 1px;}")
  app.exec()

  return 0


main()
