import logging, math, csv, json, os, subprocess, copy, datetime
import random as rand
from pathlib import Path
from random import choice


from PySide6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
  QLabel,
  QPushButton,
  QGridLayout,
  QWidget,
  QVBoxLayout,
  QStackedWidget,
  QSizePolicy,
  QGroupBox,
  QComboBox, QPlainTextEdit, QSpacerItem, QFileDialog, QSpinBox, QTableWidget, QTableWidgetItem, QTableView, QLineEdit, QHBoxLayout
)

import database as db
import data_models as dm
import helper as hp
import app_config as apc

class CharacterBuildWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Data Models
    self.raceModel = dm.getDataModels().defineProxyModel(modelType=dm.GameParameterProxyModel, sourceModel='GAME_PARAMETER')
    self.raceModel.setParameter(parameterName='RACE')
    self.classModel = dm.getDataModels().defineProxyModel(modelType=dm.GameParameterProxyModel, sourceModel='GAME_PARAMETER')
    self.classModel.setParameter(parameterName='CLASS')

    # Header Label
    _headerLabel = QLabel('Character Builder')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    ## Settings Group Box
    self.settingsGroupBox = QGroupBox()
    self.settingsGroupBox.setTitle('Settings')
    self.settingsGroupBox.setMinimumSize(400, 900)
    self.settingsGroupBox.setMaximumSize(400, 900)
    self.settingsGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    # Race
    _raceComboBoxLabel = QLabel('Race:')
    _raceComboBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _raceComboBoxLabel.setMaximumSize(100, 20)

    self.raceComboBox = QComboBox()
    self.raceComboBox.setModel(self.raceModel)
    self.raceComboBox.setModelColumn(self.raceModel.sourceModel().record().indexOf('VALUE_1'))
    self.raceComboBox.setMaximumSize(150, 30)
    self.raceComboBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    # Class
    _classComboBoxLabel = QLabel('Class:')
    _classComboBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _classComboBoxLabel.setMaximumSize(100, 20)

    self.classComboBox = QComboBox()
    self.classComboBox.setModel(self.classModel)
    self.classComboBox.setModelColumn(self.classModel.sourceModel().record().indexOf('VALUE_1'))
    self.classComboBox.setMaximumSize(150, 30)
    self.classComboBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    # Level
    _levelSpinBoxLabel = QLabel('Level:')
    _levelSpinBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _levelSpinBoxLabel.setMaximumSize(150, 20)

    self.levelSpinBox = QSpinBox()
    self.levelSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.levelSpinBox.setMinimum(0)
    self.levelSpinBox.setMaximum(100)
    self.levelSpinBox.setValue(1)
    self.levelSpinBox.setMaximumWidth(60)

    # Age
    _ageSpinBoxLabel = QLabel('Age:')
    _ageSpinBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _ageSpinBoxLabel.setMaximumSize(150, 20)

    self.ageSpinBox = QSpinBox()
    self.ageSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.ageSpinBox.setMinimum(1)
    self.ageSpinBox.setMaximum(3000)
    self.ageSpinBox.setValue(1)
    self.ageSpinBox.setMaximumWidth(60)

    # Random character
    self.randomCharacterButton = QPushButton("Random Character")
    self.randomCharacterButton.setMinimumWidth(150)
    self.randomCharacterButton.clicked.connect(self.handleRandomCharacterButton)

    # Generate
    self.generateButton = QPushButton("Generate")
    self.generateButton.setMinimumWidth(150)
    self.generateButton.clicked.connect(self.handleGenerateButton)

    # Clear
    self.clearButton = QPushButton("Clear")
    self.clearButton.setMinimumWidth(150)
    self.clearButton.clicked.connect(self.handleClearButton)

    # Save to file
    self.saveToFileButton = QPushButton("Save To File")
    self.saveToFileButton.setMinimumWidth(150)
    self.saveToFileButton.clicked.connect(self.handleSaveToFileButton)

    # Finish settings group box
    self.settingsGroupBoxLayout = QGridLayout()
    self.settingsGroupBoxLayout.setSpacing(15)
    self.settingsGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.settingsGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.settingsGroupBoxLayout.addWidget(_classComboBoxLabel, 0, 0)
    self.settingsGroupBoxLayout.addWidget(self.classComboBox, 0, 1)
    self.settingsGroupBoxLayout.addWidget(_raceComboBoxLabel, 1, 0)
    self.settingsGroupBoxLayout.addWidget(self.raceComboBox, 1, 1)
    self.settingsGroupBoxLayout.addWidget(_levelSpinBoxLabel, 2, 0)
    self.settingsGroupBoxLayout.addWidget(self.levelSpinBox, 2, 1)
    self.settingsGroupBoxLayout.addWidget(_ageSpinBoxLabel, 3, 0)
    self.settingsGroupBoxLayout.addWidget(self.ageSpinBox, 3, 1)

    self.settingsGroupBoxLayout.addWidget(self.randomCharacterButton, 9, 0)
    self.settingsGroupBoxLayout.addWidget(self.generateButton, 10, 0)
    self.settingsGroupBoxLayout.addWidget(self.clearButton, 11, 0)
    self.settingsGroupBoxLayout.addWidget(self.saveToFileButton, 12, 0)

    self.settingsGroupBox.setLayout(self.settingsGroupBoxLayout)

    ## Character GroupBox
    self.characterGroupBox = QGroupBox()
    self.characterGroupBox.setTitle('Character')
    self.characterGroupBox.setMinimumSize(900, 900)
    self.characterGroupBox.setMaximumSize(1500, 900)
    self.characterGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    # Character name
    _nameLineEditLabel = QLabel('Name:')
    _nameLineEditLabel.setFont(QFont('Ubuntu Sans', 12))
    _nameLineEditLabel.setMaximumSize(80, 20)
    self.nameLineEdit = QLineEdit()
    self.nameLineEdit.setMaximumWidth(200)

    # Character class
    _classLineEditLabel = QLabel('Class:')
    _classLineEditLabel.setFont(QFont('Ubuntu Sans', 12))
    _classLineEditLabel.setMaximumSize(80, 20)
    self.classLineEdit = QLineEdit()
    self.classLineEdit.setMaximumWidth(200)

    # Character race
    _raceLineEditLabel = QLabel('Race:')
    _raceLineEditLabel.setFont(QFont('Ubuntu Sans', 12))
    _raceLineEditLabel.setMaximumSize(80, 20)
    self.raceLineEdit = QLineEdit()
    self.raceLineEdit.setMaximumWidth(200)

    # Character level
    _levelLineEditLabel = QLabel('Level:')
    _levelLineEditLabel.setFont(QFont('Ubuntu Sans', 12))
    _levelLineEditLabel.setMaximumSize(80, 20)
    self.levelLineEdit = QLineEdit()
    self.levelLineEdit.setMaximumWidth(200)

    # Character HP
    _hpSpinBoxLabel = QLabel('HP:')
    _hpSpinBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _hpSpinBoxLabel.setMaximumSize(150, 20)

    self.hpSpinBox = QSpinBox()
    self.hpSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.hpSpinBox.setMinimum(1)
    self.hpSpinBox.setMaximum(1000)
    self.hpSpinBox.setValue(1)
    self.hpSpinBox.setMaximumWidth(60)

    # Strength score
    _strengthSpinBoxLabel = QLabel('Strength:')
    _strengthSpinBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _strengthSpinBoxLabel.setMaximumSize(150, 20)

    self.strengthSpinBox = QSpinBox()
    self.strengthSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.strengthSpinBox.setMinimum(1)
    self.strengthSpinBox.setMaximum(30)
    self.strengthSpinBox.setValue(1)
    self.strengthSpinBox.setMaximumWidth(60)

    # Intelligence score
    _intelligenceSpinBoxLabel = QLabel('Intelligence:')
    _intelligenceSpinBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _intelligenceSpinBoxLabel.setMaximumSize(150, 20)

    self.intelligenceSpinBox = QSpinBox()
    self.intelligenceSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.intelligenceSpinBox.setMinimum(1)
    self.intelligenceSpinBox.setMaximum(30)
    self.intelligenceSpinBox.setValue(1)
    self.intelligenceSpinBox.setMaximumWidth(60)

    # Wisdom score
    _wisdomSpinBoxLabel = QLabel('Wisdom:')
    _wisdomSpinBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _wisdomSpinBoxLabel.setMaximumSize(150, 20)

    self.wisdomSpinBox = QSpinBox()
    self.wisdomSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.wisdomSpinBox.setMinimum(1)
    self.wisdomSpinBox.setMaximum(30)
    self.wisdomSpinBox.setValue(1)
    self.wisdomSpinBox.setMaximumWidth(60)

    # Dexterity score
    _dexteritySpinBoxLabel = QLabel('Dexterity:')
    _dexteritySpinBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _dexteritySpinBoxLabel.setMaximumSize(150, 20)

    self.dexteritySpinBox = QSpinBox()
    self.dexteritySpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.dexteritySpinBox.setMinimum(1)
    self.dexteritySpinBox.setMaximum(30)
    self.dexteritySpinBox.setValue(1)
    self.dexteritySpinBox.setMaximumWidth(60)

    # Constitution score
    _constitutionSpinBoxLabel = QLabel('Constitution:')
    _constitutionSpinBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _constitutionSpinBoxLabel.setMaximumSize(150, 20)

    self.constitutionSpinBox = QSpinBox()
    self.constitutionSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.constitutionSpinBox.setMinimum(1)
    self.constitutionSpinBox.setMaximum(30)
    self.constitutionSpinBox.setValue(1)
    self.constitutionSpinBox.setMaximumWidth(60)

    # Charisma score
    _charismaSpinBoxLabel = QLabel('Charisma:')
    _charismaSpinBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _charismaSpinBoxLabel.setMaximumSize(150, 20)

    self.charismaSpinBox = QSpinBox()
    self.charismaSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.charismaSpinBox.setMinimum(1)
    self.charismaSpinBox.setMaximum(30)
    self.charismaSpinBox.setValue(1)
    self.charismaSpinBox.setMaximumWidth(60)

    # Character age
    _ageLineEditLabel = QLabel('Age:')
    _ageLineEditLabel.setFont(QFont('Ubuntu Sans', 12))
    _ageLineEditLabel.setMaximumSize(80, 20)
    self.ageLineEdit = QLineEdit()
    self.ageLineEdit.setMaximumWidth(200)

    ## Sub Group boxes

    # General Group Box
    self.generalGroupBoxLayout = QGridLayout()
    self.generalGroupBoxLayout.setSpacing(20)
    self.generalGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.generalGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.generalGroupBoxLayout.addWidget(_nameLineEditLabel, 0, 0)
    self.generalGroupBoxLayout.addWidget(self.nameLineEdit, 0, 1)
    self.generalGroupBoxLayout.addWidget(_classLineEditLabel, 1, 0)
    self.generalGroupBoxLayout.addWidget(self.classLineEdit, 1, 1)
    self.generalGroupBoxLayout.addWidget(_raceLineEditLabel, 2, 0)
    self.generalGroupBoxLayout.addWidget(self.raceLineEdit, 2, 1)
    self.generalGroupBoxLayout.addWidget(_levelLineEditLabel, 3, 0)
    self.generalGroupBoxLayout.addWidget(self.levelLineEdit, 3, 1)
    self.generalGroupBoxLayout.addWidget(_hpSpinBoxLabel, 4, 0)
    self.generalGroupBoxLayout.addWidget(self.hpSpinBox, 4, 1)

    self.generalGroupBox = QGroupBox()
    self.generalGroupBox.setTitle('General')
    self.generalGroupBox.setMaximumSize(400, 300)
    self.generalGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    self.generalGroupBox.setLayout(self.generalGroupBoxLayout)




    ## Finish character group box
    self.characterGroupBoxLayout = QGridLayout()
    self.characterGroupBoxLayout.setSpacing(20)
    self.characterGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.characterGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.characterGroupBoxLayout.addWidget(self.generalGroupBox, 1, 0)

    self.characterGroupBoxLayout.addWidget(_strengthSpinBoxLabel, 5, 0)
    self.characterGroupBoxLayout.addWidget(self.strengthSpinBox, 5, 1)
    self.characterGroupBoxLayout.addWidget(_intelligenceSpinBoxLabel, 6, 0)
    self.characterGroupBoxLayout.addWidget(self.intelligenceSpinBox, 6, 1)
    self.characterGroupBoxLayout.addWidget(_wisdomSpinBoxLabel, 7, 0)
    self.characterGroupBoxLayout.addWidget(self.wisdomSpinBox, 7, 1)
    self.characterGroupBoxLayout.addWidget(_dexteritySpinBoxLabel, 8, 0)
    self.characterGroupBoxLayout.addWidget(self.dexteritySpinBox, 8, 1)
    self.characterGroupBoxLayout.addWidget(_constitutionSpinBoxLabel, 9, 0)
    self.characterGroupBoxLayout.addWidget(self.constitutionSpinBox, 9, 1)
    self.characterGroupBoxLayout.addWidget(_charismaSpinBoxLabel, 10, 0)
    self.characterGroupBoxLayout.addWidget(self.charismaSpinBox, 10, 1)


    self.characterGroupBoxLayout.addWidget(_ageLineEditLabel, 11, 0)
    self.characterGroupBoxLayout.addWidget(self.ageLineEdit, 11, 1)

    self.characterGroupBox.setLayout(self.characterGroupBoxLayout)

    ## Finish setup
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainGridLayout.addWidget(_headerLabel, 1, 0)
    _mainGridLayout.addWidget(self.settingsGroupBox, 2, 0)
    _mainGridLayout.addWidget(self.characterGroupBox, 2, 1)
    self.setLayout(_mainGridLayout)

  def handleClearButton(self):
    pass

  def handleSaveToFileButton(self):
    _fileDialog = QFileDialog()
    _fileDialog.setNameFilter('*.txt')
    _fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    _filename = []

    _filePath = ''
    if _fileDialog.exec_():
      _filename = _fileDialog.selectedFiles()
      _filePath = _filename[0]
      _fileExtension = '.txt'
      _lastChars = _filePath[len(_filePath) - len(_fileExtension) : len(_filePath)]
      _filePath += _fileExtension if _lastChars != _fileExtension else ''

    with open(file=_filePath, mode='w', newline='') as _file:
      _file.write(self.weatherOutputPlainText.toPlainText())

  def handleGenerateButton(self):
    self.nameLineEdit.setText('Gary Greyhawk')
    self.classLineEdit.setText(self.classComboBox.currentText())
    self.raceLineEdit.setText(self.raceComboBox.currentText())
    self.levelLineEdit.setText(str(self.levelSpinBox.value()))

    _rollHpTwice = False
    if self.raceComboBox.currentText() == 'Human':
      _rollHpTwice = True

    _hpScore = 0
    for i in range(self.levelSpinBox.value()):
      _dieHpScore = hp.rollDice(1, 8)
      if _rollHpTwice:
        _dieScore = max(_dieHpScore, hp.rollDice(1, 8))
      _hpScore += _dieHpScore
    self.hpSpinBox.setValue(_hpScore)

    _strengthScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=5)
    self.strengthSpinBox.setValue(_strengthScore)
    _intelligenceScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=5)
    self.intelligenceSpinBox.setValue(_intelligenceScore)
    _wisdomScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=5)
    self.wisdomSpinBox.setValue(_wisdomScore)
    _dexterityScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=5)
    self.dexteritySpinBox.setValue(_dexterityScore)
    _constitutionScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=5)
    self.constitutionSpinBox.setValue(_constitutionScore)
    _charismaScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=5)
    self.charismaSpinBox.setValue(_charismaScore)

    _ageScore = hp.rollDice(3, 20)
    self.ageLineEdit.setText(str(_ageScore))

  def handleRandomCharacterButton(self):
    pass

class DungeonCreatorWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Fields
    self.numberOfLevels = 1

    # Header Label
    _headerLabel = QLabel('Dungeon Creator')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    ## Random dungeon from preset group box ##

    # Dungeon size label and combo box
    _dungeonSizeLabel = QLabel('Dungeon Size:')
    _dungeonSizeLabel.setFont(QFont('Ubuntu Sans', 11))
    _dungeonSizeLabel.setMaximumSize(150, 20)

    self.dungeonSizeComboBox = QComboBox()
    self.dungeonSizeModel = dm.getDataModels().defineProxyModel(modelType=dm.GameParameterProxyModel, sourceModel='GAME_PARAMETER')
    self.dungeonSizeModel.setParameter(parameterName='DUNGEON_SIZE')
    self.dungeonSizeComboBox.setModel(self.dungeonSizeModel)
    self.dungeonSizeComboBox.setModelColumn(self.dungeonSizeModel.sourceModel().record().indexOf('VALUE_1'))
    self.dungeonSizeComboBox.currentTextChanged.connect(self.handleDungeonSizeComboBoxChanged)

    # Room density label combo box
    _roomDensityLabel = QLabel('Room Density:')
    _dungeonSizeLabel.setFont(QFont('Ubuntu Sans', 11))
    _dungeonSizeLabel.setMaximumSize(150, 20)

    self.roomDensityComboBox = QComboBox()

    # Treasure type label and combo box
    _treasureTypeLabel = QLabel('Treasure Type:')
    _treasureTypeLabel.setFont(QFont('Ubuntu Sans', 11))
    _treasureTypeLabel.setMaximumSize(150, 20)

    self.treasureTypeComboBox = QComboBox()
    self.treasureTypeModel = dm.getDataModels().defineProxyModel(modelType=dm.GameParameterProxyModel, sourceModel='GAME_PARAMETER')
    self.treasureTypeModel.setParameter(parameterName='TREASURE_TYPE')
    self.treasureTypeComboBox.setModel(self.treasureTypeModel)
    self.treasureTypeComboBox.setModelColumn(self.treasureTypeModel.sourceModel().record().indexOf('VALUE_4'))
    self.treasureTypeComboBox.currentTextChanged.connect(self.handleTreasureTypeComboBoxChanged)

    # Description
    _descriptionLabel = QLabel('Description:')
    self.descriptionContentLabel = QLabel()

    # Generate button
    self.randomDungeonGenerateButton = QPushButton("Generate")
    self.randomDungeonGenerateButton.clicked.connect(self.handleRandomDungeonGenerateButton)

    # Clear button
    self.randomDungeonClearButton = QPushButton("Clear")
    self.randomDungeonClearButton.clicked.connect(self.handleRandomDungeonClearButton)

    # Group Box
    _randomFromPresetGroupBoxLayout = QGridLayout()
    _randomFromPresetGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _randomFromPresetGroupBoxLayout.setVerticalSpacing(15)
    _randomFromPresetGroupBoxLayout.setContentsMargins(15, 20, 15, 20)
    _randomFromPresetGroupBoxLayout.addWidget(_dungeonSizeLabel, 0, 0)
    _randomFromPresetGroupBoxLayout.addWidget(self.dungeonSizeComboBox, 0, 1)
    _randomFromPresetGroupBoxLayout.addWidget(_treasureTypeLabel, 1, 0)
    _randomFromPresetGroupBoxLayout.addWidget(self.treasureTypeComboBox, 1, 1)
    _randomFromPresetGroupBoxLayout.addWidget(_descriptionLabel, 2, 0)
    _randomFromPresetGroupBoxLayout.addWidget(self.descriptionContentLabel, 2, 1)
    _randomFromPresetGroupBoxLayout.addWidget(self.randomDungeonGenerateButton, 3, 0)
    _randomFromPresetGroupBoxLayout.addWidget(self.randomDungeonClearButton, 4, 0)

    self.randomFromPresetGroupBox = QGroupBox()
    self.randomFromPresetGroupBox.setTitle('Random Dungeon From Preset')
    self.randomFromPresetGroupBox.setMinimumWidth(600)
    self.randomFromPresetGroupBox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    self.randomFromPresetGroupBox.setLayout(_randomFromPresetGroupBoxLayout)

    ## Custom Dungeon ##

    # Number of dungeon levels label and spin box
    _numberOfLevelsLabel = QLabel('Number Of Levels:')
    _numberOfLevelsLabel.setFont(QFont('Ubuntu Sans', 11))
    _numberOfLevelsLabel.setMaximumSize(150, 20)

    self.numberOfLevelsSpinBox = QSpinBox()
    self.numberOfLevelsSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.numberOfLevelsSpinBox.setMinimum(1)
    self.numberOfLevelsSpinBox.setMaximum(5000)
    self.numberOfLevelsSpinBox.setValue(1)
    self.numberOfLevelsSpinBox.setMaximumWidth(100)
    self.numberOfLevelsSpinBox.valueChanged.connect(lambda newValue: self.handleNumberOfLevelsSpinBoxValueChanged(newValue=newValue))

    # Table Widget for level settings
    self.levelSettingTableWidget = QTableWidget()
    self.levelSettingTableWidget.setColumnCount(3)
    self.levelSettingTableWidget.horizontalHeader().setStretchLastSection(True)
    self.levelSettingTableWidget.verticalHeader().hide()
    self.levelSettingTableWidget.setMinimumWidth(400)

    _levelHeaderItem = QTableWidgetItem('Level')
    _numberOfRoomsHeaderItem = QTableWidgetItem('Rooms')
    _treasureHeaderItem = QTableWidgetItem('Average Treasure (GP)')
    self.levelSettingTableWidget.setHorizontalHeaderItem(0, _levelHeaderItem)
    self.levelSettingTableWidget.setHorizontalHeaderItem(1, _numberOfRoomsHeaderItem)
    self.levelSettingTableWidget.setHorizontalHeaderItem(2, _treasureHeaderItem)

    self.addRowToLevelSettingsTable()

    # Generate button
    self.customDungeonGenerateButton = QPushButton("Generate")
    self.customDungeonGenerateButton.setMaximumWidth(120)
    self.customDungeonGenerateButton.clicked.connect(self.handleCustomDungeonGenerateButton)

    # Clear Output button
    self.customDungeonClearOutputButton = QPushButton("Clear Output")
    self.customDungeonClearOutputButton.setMaximumWidth(120)
    self.customDungeonClearOutputButton.clicked.connect(self.handleClearOutputButton)

    # Reset button
    self.customDungeonResetButton = QPushButton("Reset")
    self.customDungeonResetButton.setMaximumWidth(120)
    self.customDungeonResetButton.clicked.connect(self.handleResetCustomDungeonButton)

    # Group Box
    _customDungeonGroupBoxLayout = QGridLayout()
    _customDungeonGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _customDungeonGroupBoxLayout.setVerticalSpacing(15)
    _customDungeonGroupBoxLayout.setContentsMargins(15, 20, 15, 20)
    _customDungeonGroupBoxLayout.addWidget(_numberOfLevelsLabel, 0, 0)
    _customDungeonGroupBoxLayout.addWidget(self.numberOfLevelsSpinBox, 0, 1)
    _customDungeonGroupBoxLayout.addWidget(self.levelSettingTableWidget, 1, 0, 1, 2)
    _customDungeonGroupBoxLayout.addWidget(self.customDungeonGenerateButton, 2, 0)
    _customDungeonGroupBoxLayout.addWidget(self.customDungeonResetButton, 3, 0)
    _customDungeonGroupBoxLayout.addWidget(self.customDungeonClearOutputButton, 4, 0)

    self.customDungeonGroupBox = QGroupBox()
    self.customDungeonGroupBox.setTitle('Custom Dungeon')
    self.customDungeonGroupBox.setMinimumWidth(600)
    self.customDungeonGroupBox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    self.customDungeonGroupBox.setLayout(_customDungeonGroupBoxLayout)

    ## Output plain text ##
    self.outputPlainText = QPlainTextEdit()
    self.outputPlainText.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    self.outputPlainText.setFont(QFont('Consolas', 11))

    ## Main Group Box ##
    self.dungeonCreatorGroupBoxLayout = QGridLayout()
    self.dungeonCreatorGroupBoxLayout.setSpacing(20)
    self.dungeonCreatorGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.dungeonCreatorGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.dungeonCreatorGroupBoxLayout.addWidget(self.randomFromPresetGroupBox, 0, 0)
    self.dungeonCreatorGroupBoxLayout.addWidget(self.outputPlainText, 0, 1, 4, 1)
    self.dungeonCreatorGroupBoxLayout.addWidget(self.customDungeonGroupBox, 1, 0)
    self.dungeonCreatorGroupBoxLayout.addItem(QSpacerItem(10, 3000), 2, 0)

    self.dungeonCreatorGroupBox = QGroupBox()
    self.dungeonCreatorGroupBox.setTitle('Settings')
    self.dungeonCreatorGroupBox.setMinimumSize(900, 900)
    self.dungeonCreatorGroupBox.setMaximumSize(2500, 1300)
    self.dungeonCreatorGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    self.dungeonCreatorGroupBox.setLayout(self.dungeonCreatorGroupBoxLayout)

    ## Finish setup ##
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainGridLayout.addWidget(_headerLabel, 1, 0)
    _mainGridLayout.addWidget(self.dungeonCreatorGroupBox, 2, 0)
    self.setLayout(_mainGridLayout)

    ## Initialize relevant widgets and class variables ##
    _levelRowItem = QTableWidgetItem('1')
    _levelRowItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    self.levelSettingTableWidget.setItem(0, 0, _levelRowItem)
    _roomRowItem = QTableWidgetItem('1')
    _roomRowItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    self.levelSettingTableWidget.setItem(0, 1, _roomRowItem)
    self.handleDungeonSizeComboBoxChanged()

  def generateTreasure(self):
    _treasureId = self.treasureTypeModel.data(self.treasureTypeModel.index(self.treasureTypeComboBox.currentIndex(), self.treasureTypeModel.sourceModel().record().indexOf('ID'), self.treasureTypeComboBox.rootModelIndex()))

    _treasureParameterTypeId = db.getGameParameterTypeId(parameterName='TREASURE')
    _treasureItems = db.query(statement=f'select VALUE_3 as ITEM, VALUE_2 as ITEM_TYPE, VALUE_4 as PROBABILITY, VALUE_5 as ITEM_GROUP, VALUE_6 as GROUP_LOGICAL_OPERATOR from GAME_PARAMETER where TYPE = ? and VALUE_1 = ? order by VALUE_5, VALUE_6 desc', args=(_treasureParameterTypeId, _treasureId), one=False)
    _itemCoinId = db.getGameParameterValueFieldId(parameterName='ITEM_TYPE', parameterValueColumn='VALUE_1', parameterValue='Coin')
    _itemGemId = db.getGameParameterValueFieldId(parameterName='ITEM_TYPE', parameterValueColumn='VALUE_1', parameterValue='Gem')
    _itemJewelleryId = db.getGameParameterValueFieldId(parameterName='ITEM_TYPE', parameterValueColumn='VALUE_1', parameterValue='Jewellery')
    _itemMagicItemId = db.getGameParameterValueFieldId(parameterName='ITEM_TYPE', parameterValueColumn='VALUE_1', parameterValue='Magic Item')

    _parameterGemId = db.getGameParameterTypeId('GEM_VALUES')
    _parameterJewelleryId = db.getGameParameterTypeId('JEWELLERY_VALUES')
    _parameterTreasureItemTypeId = db.getGameParameterTypeId('ITEM_TYPE')

    _itemGemValues = db.query(statement=f'select VALUE_1 as VALUE, VALUE_2 as PROBABILITY from GAME_PARAMETER where TYPE = ?', args=(_parameterGemId,), one=False)
    _itemJewelleryValues = db.query(statement=f'select VALUE_1 as VALUE from GAME_PARAMETER where TYPE = ?', args=(_parameterJewelleryId,), one=True)

    _magicItemTypes = db.query(statement='select gp.ID, gp.VALUE_1 as ITEM_TYPE from GAME_PARAMETER gp where gp.TYPE = ? and gp.VALUE_2 = True and gp.VALUE_3 = ?', args=(_parameterTreasureItemTypeId, _itemMagicItemId), one=False)
    _magicItemTypesTemp = []
    _allMagicItemTypes = _magicItemTypes
    _newItems = True

    # Recursively find all magic item types
    while _newItems:
      _newItems = False
      for _magicItemType in _allMagicItemTypes:
        _magicItemTypes = db.query(statement='select gp.ID, gp.VALUE_1 as ITEM_TYPE from GAME_PARAMETER gp where gp.TYPE = ? and gp.VALUE_2 = True and gp.VALUE_3 = ?', args=(_parameterTreasureItemTypeId, _magicItemType['ID']), one=False)
        if _magicItemTypes:
          _allMagicItemTypes.remove(_magicItemType)
          _newItems = True
          _magicItemTypesTemp.extend(_magicItemTypes)

      if _newItems:
        _allMagicItemTypes.extend(_magicItemTypesTemp)


    _coins = {}
    _gems = {}
    _jewellery = {}
    _magicItems = {}
    _totalValueGP = 0
    _currentItemGroup = 0
    _treasure = {}

    # Transpose items from rows into columns per item group
    for _treasureItem in _treasureItems:
      _currentItemGroup = _treasureItem['ITEM_GROUP']
      if _currentItemGroup not in _treasure:
        _treasure[_currentItemGroup] = []
      _treasure[_currentItemGroup].append(_treasureItem)

    _finalTreasure = []
    # Resolve item groups with multiple items
    for _key in _treasure.keys():
      if len(_treasure[_key]) == 1:
        _finalTreasure.append(_treasure[_key][0])
      else:
        _logicalOp = _treasure[_key][0]['GROUP_LOGICAL_OPERATOR'].upper()
        if _logicalOp == 'OR':
          _finalTreasure.append(choice(_treasure[_key]))
        elif _logicalOp == 'AND':
          for _treasureItem in _treasure[_key]:
            _finalTreasure.append(_treasureItem)

    # Determine which items are in the treasure and build the final list of treasure items
    for _item in _finalTreasure:
      _treasureItemD100Roll = hp.rollDice(1, 100)
      _prob = math.ceil(float(_item['PROBABILITY']))

      if _treasureItemD100Roll > _prob:
        continue

      _treasureItem = hp.splitAndProcessValueStatement(_item['ITEM'])
      _itemType = int(_item['ITEM_TYPE'])
      # Coins
      if _itemType == _itemCoinId:
        _currency = _treasureItem[1].upper()
        if _currency not in _coins:
          _coins[_currency] = 0
        _coins[_currency] += _treasureItem[0]

        _currencyFactor = 1
        if _treasureItem[1] == 'cp':
          _currencyFactor = 1 / 100
        elif _treasureItem[1] == 'sp':
          _currencyFactor = 1 / 10
        elif _treasureItem[1] == 'ep':
          _currencyFactor = 1 / 2
        elif _treasureItem[1] == 'gp':
          _currencyFactor = 1
        elif _treasureItem[1] == 'pp':
            _currencyFactor = 5
        _totalValueGP += math.floor(_treasureItem[0] * _currencyFactor)
        # Magic Items
      elif _itemType == _itemMagicItemId:
        # What kind of magic item is in the treasure

        for i in range(_treasureItem[0]):
          _magicItem = choice(_magicItemTypes)['ITEM_TYPE']
          if _magicItem not in _magicItems:
            _magicItems[_magicItem] = 0
          _magicItems[_magicItem] += 1
      # Gems
      elif _itemType == _itemGemId:
        for i in range(_treasureItem[0]):
          _gemD100Result = hp.rollDice(1, 100)
          _probabilitySum = 0.0
          for _gem in _itemGemValues:
            _probabilitySum += float(_gem['PROBABILITY'])
            if _gemD100Result <= math.ceil(_probabilitySum):
              _valueStatementComponents = hp.splitAndProcessValueStatement(_gem['VALUE'])
              _dictKey = f'{_valueStatementComponents[0]} {_valueStatementComponents[1]}'
              _gemValue = _valueStatementComponents[0]
              if str(_dictKey) not in _gems:
                _gems[str(_dictKey)] = 0
              _gems[str(_dictKey)] += 1
              _totalValueGP += _gemValue
              break
      # Jewellery
      elif _itemType == _itemJewelleryId:
        for i in range(_treasureItem[0]):
          _jewelleryValue = hp.splitAndProcessValueStatement(_itemJewelleryValues['VALUE'])
          _dictKey = f'{str(_jewelleryValue[0])} {_jewelleryValue[1]}'
          if _dictKey not in _jewellery:
            _jewellery[_dictKey] = 0
          _jewellery[_dictKey] += 1
          _totalValueGP += _jewelleryValue[0]
      else:
        pass

    return {'TOTAL_VALUE_GP': _totalValueGP, 'COIN': _coins, 'GEMS': _gems, 'JEWELLERY': _jewellery, 'MAGIC_ITEMS': _magicItems}

  def generateLevel(self, rooms):
    _gameSystem = 1 #OSE
    _roomContents = db.query(statement='select PROBABILITY, CONTENT, TREASURE_CHANCE from ROOM_CONTENT_X_GAME_SYSTEM where GAME_SYSTEM = ? order by ID', args=(_gameSystem,))

    _rawResults = []
    for _room in range(rooms):
      _roomD100Result = hp.rollDice(1, 100)
      _finalRoomContent = {}
      _probabilitySum = 0
      for _content in _roomContents:
        _probabilitySum += _content['PROBABILITY']
        if _roomD100Result <= math.ceil(_probabilitySum):
          _finalRoomContent = _content
          break

      _rawResults.append(_finalRoomContent)

    _result = []
    for i  in range(len(_rawResults)):
      _treasureD100Result = hp.rollDice(1, 100)
      _treasureResultStr = 'Treasure: None'
      if len(_rawResults[i]) == 0:
        pass
      if _treasureD100Result <= math.ceil(_rawResults[i]['TREASURE_CHANCE']):
        _treasureResultStr = 'Treasure: Yes'

      _result.append(f'Room {i + 1}: {_rawResults[i]['CONTENT']}, {_treasureResultStr}')

    return _result

  def addRowToLevelSettingsTable(self):
    self.levelSettingTableWidget.setRowCount(self.levelSettingTableWidget.rowCount() + 1)
    _levelRowItem = QTableWidgetItem(str(self.numberOfLevels))
    _levelRowItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    self.levelSettingTableWidget.setItem(self.numberOfLevels - 1, 0, _levelRowItem)

    _numberOfRoomsSpinBox = QSpinBox()
    _numberOfRoomsSpinBox.setFont(QFont('Ubuntu Mono', 11))
    _numberOfRoomsSpinBox.setMinimum(0)
    _numberOfRoomsSpinBox.setMaximum(5000)
    _numberOfRoomsSpinBox.setValue(1)
    _numberOfRoomsSpinBox.setMaximumWidth(100)

    self.levelSettingTableWidget.setCellWidget(self.numberOfLevels - 1, 1, _numberOfRoomsSpinBox)
    #setItem(self.numberOfLevels - 1, 1, _roomCountRowItem)

    _treasureRowItem = QTableWidgetItem()
    _treasureRowItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
    self.levelSettingTableWidget.setItem(self.numberOfLevels - 1, 2, _treasureRowItem)

  def generateDungeonName(self):
    _dungeonNameParameterId = db.getGameParameterTypeId(parameterName='DUNGEON_NAME')
    _dungeonNames = db.query(statement='select VALUE_1 as NAME from GAME_PARAMETER where TYPE = ?', args=(_dungeonNameParameterId, ))

    return choice(_dungeonNames)['NAME']

  def printLevel(self, levelNumber=None, levelContents=None):
    self.outputPlainText.appendPlainText(f'\nLevel {levelNumber + 1}:')
    self.outputPlainText.appendPlainText((f'=' * len(f'Level {levelNumber + 1}:')) + '\n')
    for _room in levelContents:
      self.outputPlainText.appendPlainText(_room)


  def handleRandomDungeonGenerateButton(self):

    _dungeonName = self.generateDungeonName()
    _finalTreasureItems = self.generateTreasure()

    self.outputPlainText.appendPlainText(f'{_dungeonName}')
    self.outputPlainText.appendPlainText('=' * len(_dungeonName) + '\n')

    self.outputPlainText.appendPlainText(f'TREASURE')
    self.outputPlainText.appendPlainText('=' * len('TREASURE') + '\n')

    for _treasureItemType in _finalTreasureItems.keys():
      if _treasureItemType == 'TOTAL_VALUE_GP':
        continue

      self.outputPlainText.appendPlainText(f'{_treasureItemType}:')
      for _treasureItem in _finalTreasureItems[_treasureItemType].keys():
        self.outputPlainText.appendPlainText(f'{_treasureItem}: {_finalTreasureItems[_treasureItemType][_treasureItem]}')
      self.outputPlainText.appendPlainText(f'')

    self.outputPlainText.appendPlainText(f'Total Value: {_finalTreasureItems['TOTAL_VALUE_GP']} gp\n\n')

    self.outputPlainText.appendPlainText(f'DUNGEON LAYOUT')
    self.outputPlainText.appendPlainText('=' * len('DUNGEON LAYOUT') + '\n')

    _numberOfLevelsValueStatement = self.dungeonSizeModel.data(self.dungeonSizeModel.index(self.dungeonSizeComboBox.currentIndex(), self.dungeonSizeModel.sourceModel().record().indexOf('VALUE_2'), self.dungeonSizeComboBox.rootModelIndex()))
    _numberOfLevelsResult = hp.splitAndProcessValueStatement(_numberOfLevelsValueStatement)

    _numberOfRoomsValueStatement = self.dungeonSizeModel.data(self.dungeonSizeModel.index(self.dungeonSizeComboBox.currentIndex(), self.dungeonSizeModel.sourceModel().record().indexOf('VALUE_3'), self.dungeonSizeComboBox.rootModelIndex()))
    for i in range(_numberOfLevelsResult[0]):
      _numberOfRoomsResult = hp.splitAndProcessValueStatement(_numberOfRoomsValueStatement)
      self.printLevel(i, self.generateLevel(rooms=_numberOfRoomsResult[0]))

  def handleRandomDungeonClearButton(self):
    self.handleClearOutputButton()

  def handleDungeonSizeComboBoxChanged(self):
    self.updateDescriptionContentLabel()

  def handleTreasureTypeComboBoxChanged(self):
    self.updateDescriptionContentLabel()

  def updateDescriptionContentLabel(self):
    _numberOfLevels = 'Levels: ' + self.dungeonSizeModel.data(self.dungeonSizeModel.index(self.dungeonSizeComboBox.currentIndex(), self.dungeonSizeModel.sourceModel().record().indexOf('VALUE_2'), self.dungeonSizeComboBox.rootModelIndex()))
    _numberOfRoomsPerLevel = 'Rooms: ' + self.dungeonSizeModel.data(self.dungeonSizeModel.index(self.dungeonSizeComboBox.currentIndex(), self.dungeonSizeModel.sourceModel().record().indexOf('VALUE_3'), self.dungeonSizeComboBox.rootModelIndex()))
    _treasureType = 'Treasure: ' + self.treasureTypeModel.data(self.treasureTypeModel.index(self.treasureTypeComboBox.currentIndex(), self.treasureTypeModel.sourceModel().record().indexOf('VALUE_4'), self.treasureTypeComboBox.rootModelIndex()))
    self.descriptionContentLabel.setText(f'{_numberOfLevels}\n{_numberOfRoomsPerLevel}\n{_treasureType}')

  def handleResetCustomDungeonButton(self):
    self.numberOfLevels = 1
    self.numberOfLevelsSpinBox.setValue(1)
    self.levelSettingTableWidget.setRowCount(0)
    self.addRowToLevelSettingsTable()
    self.outputPlainText.clear()

  def handleClearOutputButton(self):
    self.outputPlainText.clear()

  def handleCustomDungeonGenerateButton(self):
    _dungeonName = self.generateDungeonName()
    self.outputPlainText.appendPlainText(_dungeonName)
    self.outputPlainText.appendPlainText('=' * len(_dungeonName) + '\n')

    for i in range(self.levelSettingTableWidget.rowCount()):
      _numberOfRooms = int(self.levelSettingTableWidget.cellWidget(i, 1).value())
      _level = self.generateLevel(rooms=_numberOfRooms)

      _levelHeaderText = f'Level {i + 1}'
      self.outputPlainText.appendPlainText(_levelHeaderText + '\n')
      for _room in _level:
        self.outputPlainText.appendPlainText(_room)

      self.outputPlainText.appendPlainText('')

  def handleNumberOfLevelsSpinBoxValueChanged(self, newValue):
    _oldNumber = self.numberOfLevels
    self.numberOfLevels = newValue

    _rowCount = self.levelSettingTableWidget.rowCount()

    # Add row to level table
    if self.numberOfLevels > _oldNumber:
      if _rowCount >= self.numberOfLevels:
        self.levelSettingTableWidget.showRow(self.numberOfLevels - 1)
      else:
        self.addRowToLevelSettingsTable()
    # Remove row from level table
    elif self.numberOfLevels < _oldNumber:
      self.levelSettingTableWidget.hideRow(self.numberOfLevels)

class ItemDataManagerWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Data Models
    # self.climateModel = dm.getDataModels().defineProxyModel(modelType=dm.GameParameterProxyModel, sourceModel='GAME_PARAMETER')
    # self.climateModel.setParameter(parameterName='CLIMATE')

    # Fields
    self.currentImportCsvFilePath = f'{apc.ROOT_INPUT_PATH}/osr_armor_weapons_equipment/csv/osr_armor_weapons_equipment_export.csv'
    self.jsonImportPath = f'{apc.ROOT_INPUT_PATH}/osr_armor_weapons_equipment/json'
    self.imageImportPath = f'{apc.ROOT_INPUT_PATH}/osr_armor_weapons_equipment/images'
    self.jsonExportPath = f'{apc.JSON_EXPORT_PATH}/foundry_module_osr_armor_weapons_equipment'
    self.itemKeyLength = 16 # Foundry says it must be 16 digits
    #self.itemData = {'WEAPON_AMMUNITION': [], 'ARMOR': [], 'EQUIPMENT': []}
    self.itemData = []
    self.itemKeys = []
    self.loadItemKeysFromDatabase()

    # Foundry json objects
    self.foundryItemTagTemplate = {'title': '', 'value': ''}

    # Header Label
    _headerLabel = QLabel('Item Data Manager')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    # Main Group Box
    self.itemDataManagerGroupBox = QGroupBox()
    self.itemDataManagerGroupBox.setTitle('Settings')
    self.itemDataManagerGroupBox.setMinimumSize(900, 900)
    self.itemDataManagerGroupBox.setMaximumSize(1500, 900)
    self.itemDataManagerGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    # CSV-File label and selection button
    _csvFileSelectionLabel = QLabel('CSV File:')
    _csvFileSelectionLabel.setFont(QFont('Ubuntu Sans', 12))
    _csvFileSelectionLabel.setMaximumSize(100, 20)

    self.csvFileSelectionButton = QPushButton("Choose CSV Input File")
    self.csvFileSelectionButton.setMaximumWidth(210)
    self.csvFileSelectionButton.clicked.connect(self.handleCsvFileSelectionButton)

    # CSV-File display label
    self.csvFileDisplayLabel = QLabel(self.currentImportCsvFilePath)
    self.csvFileDisplayLabel.setFont(QFont('Ubuntu Sans', 7))
    self.csvFileDisplayLabel.setMinimumSize(300, 10)

    # CSV import button
    self.csvImportButton = QPushButton("Import CSV")
    self.csvImportButton.setMinimumWidth(150)
    self.csvImportButton.clicked.connect(self.handleCsvImportButton)

    # Save to db button
    self.saveToDbButton = QPushButton("Save To Database")
    self.saveToDbButton.setMinimumWidth(150)
    self.saveToDbButton.clicked.connect(self.handleSaveToDbButton)

    # Export to json button
    self.exportToJsonButton = QPushButton("Export To JSON")
    self.exportToJsonButton.setMinimumWidth(100)
    self.exportToJsonButton.clicked.connect(self.handleExportToJsonButton)

    # Copy export to foundry module dir
    self.copyToFoundryModuleDirButton = QPushButton("Copy To Module Dir")
    self.copyToFoundryModuleDirButton.setMinimumWidth(150)
    self.copyToFoundryModuleDirButton.clicked.connect(self.handleCopyToFoundryModuleDirButton)

    # Finish main GroupBox
    self.itemDataManagerGroupBoxLayout = QGridLayout()
    self.itemDataManagerGroupBoxLayout.setSpacing(20)
    self.itemDataManagerGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.itemDataManagerGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.itemDataManagerGroupBoxLayout.addWidget(_csvFileSelectionLabel, 0, 0)
    self.itemDataManagerGroupBoxLayout.addWidget(self.csvFileSelectionButton, 0, 1)
    self.itemDataManagerGroupBoxLayout.addWidget(self.csvFileDisplayLabel, 1, 0, 1, 2)
    self.itemDataManagerGroupBoxLayout.addWidget(self.csvImportButton, 3, 0)
    self.itemDataManagerGroupBoxLayout.addWidget(self.saveToDbButton, 4, 0)
    self.itemDataManagerGroupBoxLayout.addWidget(self.exportToJsonButton, 4, 1)
    self.itemDataManagerGroupBoxLayout.addWidget(self.copyToFoundryModuleDirButton, 5, 0)

    self.itemDataManagerGroupBox.setLayout(self.itemDataManagerGroupBoxLayout)

    # Finish setup
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainGridLayout.addWidget(_headerLabel, 1, 0)
    _mainGridLayout.addWidget(self.itemDataManagerGroupBox, 2, 0)
    self.setLayout(_mainGridLayout)

  def handleCopyToFoundryModuleDirButton(self):
    _fromPath = f'{self.jsonExportPath}/*'
    _toPath = f'{apc.FOUNDRY_INSTALL_DATA_PATH}/{apc.FOUNDRY_MODULE_ROOT_PATH}/{apc.OSR_EQUIPMENT_PACK_NAME}/data/json'
    subprocess.run(f'rm -r {_toPath}/*')
    subprocess.run(f'cp {_fromPath}/* {_toPath}')


  def handleExportToJsonButton(self):
    # Delete all files in target directory

    _removedFilesCount = 0
    for _fileName in os.listdir(self.jsonExportPath):
      logging.info(f'Removing files from: {os.path.join(self.jsonExportPath, _fileName)}')
      for _fileName2 in os.listdir(os.path.join(self.jsonExportPath, _fileName)):
        _filePath = os.path.join(self.jsonExportPath, _fileName, _fileName2)
        if os.path.isfile(_filePath):
          os.remove(_filePath)
          _removedFilesCount += 1

    logging.info(f'Removed {_removedFilesCount} files')

    # Set necessary config values and counters
    _imagePath = apc.OSR_EQUIPMENT_IMAGE_PATH
    _imgExtension = 'webp'
    _itemCount = 0

    # Gather item images
    _itemImages = []
    for _fileName in os.listdir(self.imageImportPath):
      # Cut away extension and license info
      for _fileName2 in os.listdir(os.path.join(self.imageImportPath, _fileName)):
        _name = _fileName2[0:_fileName2.rindex('.')][0:_fileName2.rindex('_')].replace('_', ' ')
        _itemImages.append({'NAME': _name, 'FILENAME': os.path.join(_fileName, _fileName2)})

    ######################
    ### Export Weapons ###
    ######################

    # Read json template and store empty version for reset
    _jsonItemWeaponTemplateEmpty = None
    _jsonItemArmorTemplateEmpty = None
    _jsonItemEquipmentTemplateEmpty = None

    with open(Path(self.jsonImportPath) / 'foundry_ose_item_weapon_template.json', mode='r') as file:
      _jsonItemWeaponTemplateEmpty = json.load(file)
    with open(Path(self.jsonImportPath) / 'foundry_ose_item_armor_template.json', mode='r') as file:
      _jsonItemArmorTemplateEmpty = json.load(file)
    with open(Path(self.jsonImportPath) / 'foundry_ose_item_equipment_template.json', mode='r') as file:
      _jsonItemEquipmentTemplateEmpty = json.load(file)

    _jsonTemplate = None
    for _item in self.itemData:
      _inputSubDir = ''
      if _item['TYPE'].upper() == 'WEAPON':
        _jsonTemplate = copy.deepcopy(_jsonItemWeaponTemplateEmpty)
      if _item['TYPE'].upper() == 'ARMOR':
        _jsonTemplate = copy.deepcopy(_jsonItemArmorTemplateEmpty)
      if _item['TYPE'].upper() in ('EQUIPMENT', 'AMMUNITION'):
        _jsonTemplate = copy.deepcopy(_jsonItemEquipmentTemplateEmpty)

      ## General
      _jsonTemplate['name'] = _item['NAME']

      ## OSE specific
      _jsonTemplate['system']['weight'] = int(_item['WEIGHT'].strip()) if _item['WEIGHT'].strip() else 0
      _jsonTemplate['system']['cost'] = int(_item['COST'].strip()) if _item['COST'].strip() else 0
      _jsonTemplate['system']['description'] = _item['DESCRIPTION'].strip()

      # Every item can contain a set of attributes, which can be:
      #   Only keys (SLOW, MISSILE, MELEE, etc.), they act as a boolean-kind-of flag
      #   Key-value pairs separated by a colon (Class: Heavy, Quantity: 20, etc.)

      # Default values
      _jsonTemplate['system']['quantity']['value'] = 1

      for _key in _item['ATTRIBUTES']:
        if _key == 'SLOW':
          if _item['TYPE'].upper() == 'ARMOR':
            _jsonTemplate['system']['slow'] = False
          _jsonTemplate['system']['slow'] = True
        if _key == 'MISSILE':
          _jsonTemplate['system']['range']['short'] = int(_item['RANGE_SHORT'].strip())
          _jsonTemplate['system']['range']['medium'] = int(_item['RANGE_MEDIUM'])
          _jsonTemplate['system']['range']['long'] = int(_item['RANGE_LONG'])
        if _key == 'MELEE':
          _jsonTemplate['system']['melee'] = True
        if _key == 'QUANTITY':
          _jsonTemplate['system']['quantity']['value'] = _item['ATTRIBUTES'][_key]
          _jsonTemplate['system']['quantity']['max'] = _item['ATTRIBUTES'][_key]

        # Weapon specific
        if _item['TYPE'].upper() == 'WEAPON':
          _jsonTemplate['system']['damage'] = _item['DAMAGE'].strip()
        # Armor specific
        if _item['TYPE'].upper() == 'ARMOR':
          # Usually signifies that the item is an actual piece of armor ('Chain Mail', 'Bascinet', 'Boiled Leather', etc.)
          if _key == 'CLASS':
            _jsonTemplate['system']['type'] = _item['ATTRIBUTES'][_key].lower()
        # Weapon specific

        # Equipment specific
        if _item['TYPE'].upper() == 'EQUIPMENT':
          if _item['CATEGORY'].upper() == 'CONTAINER':
            _jsonTemplate['type'] = 'container'

      # Tags
      self.createAndAddAttributeItemJsonTag(_jsonTemplate, _item['ATTRIBUTES'], 'BLUNT', 'Blunt', 'Blunt')
      self.createAndAddAttributeItemJsonTag(_jsonTemplate, _item['ATTRIBUTES'], 'BRACE', 'Brace', 'Brace')
      self.createAndAddAttributeItemJsonTag(_jsonTemplate, _item['ATTRIBUTES'], 'CHARGE', 'Charge', 'Charge')
      self.createAndAddAttributeItemJsonTag(_jsonTemplate, _item['ATTRIBUTES'], 'REACH', 'Reach', 'Reach')
      self.createAndAddAttributeItemJsonTag(_jsonTemplate, _item['ATTRIBUTES'], 'RELOAD', 'Reload', 'Reload')
      self.createAndAddAttributeItemJsonTag(_jsonTemplate, _item['ATTRIBUTES'], 'SPLASH', 'Splash', 'Splash')
      self.createAndAddAttributeItemJsonTag(_jsonTemplate , _item['ATTRIBUTES'], 'TWO-HANDED', 'Two-Handed', 'Two-Handed')

      # Define export dir
      _exportSubDir = ''
      if _item['TYPE'].upper() == 'WEAPON':
        _exportSubDir = 'osr-weapons'
      if _item['TYPE'].upper() == 'ARMOR':
        _exportSubDir = 'osr-armor'
      if _item['TYPE'].upper() in ('EQUIPMENT', 'AMMUNITION'):
        _exportSubDir = 'osr-equipment'

      # Images
      for _image in _itemImages:
        if _item['TYPE'].upper() in ('ARMOR', 'WEAPON'):
          if _item['NAME'].lower() == _image['NAME']:
            _jsonTemplate['img'] = f'{apc.OSR_EQUIPMENT_IMAGE_PATH}/{_image['FILENAME']}'
            break
        else:
          if _item['NAME'].lower().find(_image['NAME']) != -1:
            _jsonTemplate['img'] = f'{apc.OSR_EQUIPMENT_IMAGE_PATH}/{_image['FILENAME']}'
            break

      # Foundry specific
      _jsonTemplate['_id'] = self.getUniqueItemKey(_item['NAME'])
      _jsonTemplate['_key'] = _jsonTemplate['_key'] + _jsonTemplate['_id']
      _nowInMillis = int(datetime.datetime.now().timestamp() * 1000)
      _jsonTemplate['_stats']['createdTime'] = _nowInMillis
      _jsonTemplate['_stats']['modifiedTime'] = _nowInMillis

      # Write to json file
      _jsonOutfileName = f'{str(_jsonTemplate['name']).lower().translate(str.maketrans('', '', ".'!@#$%^&*()+,;:")).replace(' ', '_')}_{_jsonTemplate['_id']}.json'
      with open(file=Path(self.jsonExportPath) / _exportSubDir /  _jsonOutfileName, mode='w') as _jsonFile:
        json.dump(obj=_jsonTemplate, fp=_jsonFile, indent=2)

    # Write item keys to database
    self.writeItemKeysToDataBase()


  def handleSaveToDbButton(self):
    _itemParameterTypeId = db.getGameParameterTypeId(parameterName='ITEM')
    _dbResult = db.query(statement='select max(ID) as ID from GAME_PARAMETER where TYPE = ?', args=(_itemParameterTypeId,), one=True)

    _currentId = int(_dbResult['ID']) if _dbResult['ID'] else 0
    _newId = _currentId + 1

    for _type in self.itemData.keys():
      _itemTypeParameterTypeId = db.getGameParameterTypeId(parameterName='ITEM_TYPE')
      _itemTypeId = db.query('select ID from GAME_PARAMETER where TYPE = ? and upper(VALUE_1) = ? and VALUE_2 = 0', (_itemTypeParameterTypeId, _type), one=True)['ID']
      for _row in self.itemData[_type]:
        _itemCategoryId = db.query('select ID from GAME_PARAMETER where TYPE = ? and upper(VALUE_1) = ? and VALUE_2 = 1', (_itemTypeParameterTypeId, _row['CATEGORY'].upper()), one=True)
        if _itemCategoryId:
          _itemTypeId = _itemCategoryId['ID']  if _itemCategoryId['ID'] else _itemTypeId['ID']

        db.insert(f'insert into GAME_PARAMETER(TYPE, ID, VALUE_1, VALUE_2, VALUE_3, VALUE_4, VALUE_5) values(?, ?, ?, ?, ?, ?, ?)', (_itemParameterTypeId, _newId, _row['NAME'], str(_itemTypeId), _row['CATEGORY'], _row['WEIGHT'], _row['COST']))
        _newId +=1

    db.commitChanges()

  def handleCsvFileSelectionButton(self):
    _fileDialog = QFileDialog()
    _fileDialog.setNameFilter('*.csv *.json')
    _fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
    _filename = []

    if _fileDialog.exec_():
      _filename = _fileDialog.selectedFiles()
      self.currentImportCsvFilePath = _filename[0]
      self.csvFileDisplayLabel.setText(self.currentImportCsvFilePath)

  def handleCsvImportButton(self):
    if not self.currentImportCsvFilePath:
      logging.info('No csv file selected!')
      return

    # Read csv and store in list as dict per row
    _itemCount = 0
    logging.info(f'Importing items from {self.currentImportCsvFilePath}')
    with open(file=self.currentImportCsvFilePath, mode='r') as csvFile:
      _csvData = csv.DictReader(csvFile, fieldnames=None, restkey='OVERFLOW', dialect='excel', delimiter=';', quotechar='"')
      for _row in _csvData:
        self.itemData.append(_row)
        _itemCount += 1

    # Normalized attribute list for all items to save redundant code
    for _item in self.itemData:
      _rawAttributeList = _item['ATTRIBUTES'].strip().split(';')
      _attributeDict = {}
      for _attribute in _rawAttributeList:
        if ':' in _attribute:
          _parts = _attribute.split(':')
          _attributeDict[_parts[0].replace(' ', '').upper()] = _parts[1].replace(',', ', ').strip()
        else:
          _attributeDict[_attribute.replace(' ', '')] = True

      _item['ATTRIBUTES'] = _attributeDict

    logging.info(f'Imported {_itemCount} items.')

  def writeItemKeysToDataBase(self):
    _currentItemKeys = db.query(statement='select ITEM_NAME, KEY from FOUNDRY_ITEM_KEYS')

    if _currentItemKeys:
      for _key in self.itemKeys:
        _insertKey = True
        for _keyDb in _currentItemKeys:
          if _keyDb['ITEM_NAME'] == _key['ITEM_NAME']:
            _insertKey = False
            break

        if _insertKey:
          db.insert(statement='insert into FOUNDRY_ITEM_KEYS(ITEM_NAME, KEY) values(?, ?)', args=(_key['ITEM_NAME'], _key['KEY']), commit=False)
    else:
      for _key in self.itemKeys:
        db.insert(statement='insert into FOUNDRY_ITEM_KEYS(ITEM_NAME, KEY) values(?, ?)', args=(_key['ITEM_NAME'], _key['KEY']), commit=False)

    db.commitChanges()

  def loadItemKeysFromDatabase(self):
    _itemKeys = db.query(statement='select ITEM_NAME, KEY from FOUNDRY_ITEM_KEYS')
    if not _itemKeys:
      return

    for _item in _itemKeys:
      self.itemKeys.append({'ITEM_NAME': _item['ITEM_NAME'], 'KEY': _item['KEY']})

  def createAndAddAttributeItemJsonTag(self, jsonData, attributeList=None, name=None, title=None, value=None):
    if attributeList:
      if name not in attributeList:
        return

    _tag = copy.copy(self.foundryItemTagTemplate)
    _tag['title'] = title
    _tag['value'] = value
    jsonData['system']['tags'].append(_tag)

  def generateUniqueItemKey(self, itemName):
    _keyValid = False
    _key = ''
    while not _keyValid:
      for i in range(self.itemKeyLength):
        _isNextDigitNumeric = False if hp.rollDice(1, 2) == 1 else True
        _nextDigit = ''
        if _isNextDigitNumeric:
          _nextDigit = str(hp.rollDice(1, 10) - 1)
        else:
          _isNextDigitLowerCase = False if hp.rollDice(1, 2) == 1 else True
          _asciiStart = 65
          if _isNextDigitLowerCase:
            _asciiStart = 97
          _asciiOffset = hp.rollDice(1, 26) - 1
          _finalAscii = _asciiStart + _asciiOffset
          _nextDigit = chr(_finalAscii)

        _key += _nextDigit

      _keyValid = True
      for _item in self.itemKeys:
        if _item['KEY'] == _key:
          _keyValid = False
          break

      if _keyValid:
        self.itemKeys.append({'ITEM_NAME': itemName, 'KEY': _key})
      else:
        _key = ''

    return _key

  def getUniqueItemKey(self, itemName=''):
    _itemKeyFromDatabase = db.query(statement='select KEY from FOUNDRY_ITEM_KEYS where ITEM_NAME = ?', args=(itemName,), one=True)

    if _itemKeyFromDatabase:
      return _itemKeyFromDatabase['KEY']
    else:
      return self.generateUniqueItemKey(itemName)

class GameParameterManager(QWidget):
  def __init__(self):
    super().__init__()

    # Fields
    self.numberOfEditorRows = 0
    self.exportPath = 'data/export'
    self.csvExportPath = f'{self.exportPath}/csv'
    self.sqlExportPath = f'{self.exportPath}/sql'

    # Header Label
    _headerLabel = QLabel('Game Parameter Manager')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    ## Game parameter selection

    # Combo box
    _gameParameterLabel = QLabel('Game Parameter:')
    _gameParameterLabel.setFont(QFont('Ubuntu Sans', 11))
    _gameParameterLabel.setMaximumSize(150, 20)

    self.gameParameterComboBox = QComboBox()
    self.gameParameterComboBox.setMaximumWidth(200)
    self.gameParameterTypeModel = dm.getDataModels().model(name='GAME_PARAMETER_TYPE')
    self.gameParameterComboBox.setModel(self.gameParameterTypeModel)
    self.gameParameterComboBox.setModelColumn(self.gameParameterTypeModel.record().indexOf('NAME'))
    self.gameParameterComboBox.currentTextChanged.connect(self.handleGameParameterComboBoxChanged)

    # Delete and copy button
    self.updateGameParameterButton = QPushButton('Update')
    self.updateGameParameterButton.clicked.connect(self.handleUpdateGameParameterButton)
    self.updateGameParameterButton.setMaximumWidth(80)
    self.deleteGameParameterButton = QPushButton('Delete')
    self.deleteGameParameterButton.clicked.connect(self.handleDeleteGameParameterButton)
    self.deleteGameParameterButton.setMaximumWidth(80)
    self.copyGameParameterButton = QPushButton('Copy')
    self.copyGameParameterButton.clicked.connect(self.handleCopyGameParameterButton)
    self.copyGameParameterButton.setMaximumWidth(80)

    ## Parameter view
    self.gameParameterModel = dm.getDataModels().defineProxyModel(modelType=dm.GameParameterProxyModel, sourceModel='GAME_PARAMETER')
    self.gameParameterModel.setParameter('GAME_SYSTEM')

    self.dataTable = QTableView()
    self.dataTable.setModel(self.gameParameterModel)
    self.dataTable.verticalHeader().hide()
    self.dataTable.horizontalHeader().setStretchLastSection(True)
    self.dataTable.setMinimumWidth(400)

    # New button
    self.newGameParameterButton = QPushButton('New')
    self.newGameParameterButton.clicked.connect(self.handleNewGameParameterButton)
    self.newGameParameterButton.setMaximumWidth(80)

    # Parameter Name
    _editorNameLabel = QLabel('Parameter Name: ')
    _editorNameLabel.setMaximumWidth(150)
    self.editorNameLineEdit = QLineEdit()
    self.editorNameLineEdit.setMaximumWidth(200)

    # Add row button
    self.editorAddRowButton = QPushButton('Add Row')
    self.editorAddRowButton.clicked.connect(self.handleEditorAddRowButton)
    self.editorAddRowButton.setMaximumWidth(100)

    # Save button
    self.editorSaveButton = QPushButton('Save')
    self.editorSaveButton.clicked.connect(self.handleEditorSaveButton)
    self.editorSaveButton.setMaximumWidth(100)

    # Export to sql-insert statement file button
    self.editorExportToSqlButton = QPushButton('Export To SQL')
    self.editorExportToSqlButton.clicked.connect(self.handleEditorExportToSqlButton)
    self.editorExportToSqlButton.setMaximumWidth(120)

    # Export to csv file button
    self.editorExportToCsvButton = QPushButton('Export To CSV')
    self.editorExportToCsvButton.clicked.connect(self.handleEditorExportToCsvButton)
    self.editorExportToCsvButton.setMaximumWidth(120)

    # Button layout
    _buttonLayout = QHBoxLayout()
    _buttonLayout.setSpacing(15)
    _buttonLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    _buttonLayout.addWidget(self.newGameParameterButton)
    _buttonLayout.addWidget(self.editorAddRowButton)
    _buttonLayout.addWidget(self.deleteGameParameterButton)
    _buttonLayout.addWidget(self.copyGameParameterButton)
    _buttonLayout.addItem(QSpacerItem(5000, 10))

    # Group Box layout
    _selectionGroupBoxLayout = QGridLayout()
    _selectionGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _selectionGroupBoxLayout.setVerticalSpacing(15)
    _selectionGroupBoxLayout.setContentsMargins(15, 20, 15, 20)
    _selectionGroupBoxLayout.addWidget(_gameParameterLabel, 0, 0)
    _selectionGroupBoxLayout.addWidget(self.gameParameterComboBox, 0, 1, 1, 4)
    _selectionGroupBoxLayout.addLayout(_buttonLayout, 1, 0, 1, 4)
    _selectionGroupBoxLayout.addWidget(_editorNameLabel, 3, 0)
    _selectionGroupBoxLayout.addWidget(self.editorNameLineEdit, 3, 1, 1, 4)
    _selectionGroupBoxLayout.addWidget(self.dataTable, 4, 0, 1, 5)
    _selectionGroupBoxLayout.addWidget(self.editorSaveButton, 5, 0)
    _selectionGroupBoxLayout.addWidget(self.editorExportToSqlButton, 6, 0)
    _selectionGroupBoxLayout.addWidget(self.editorExportToCsvButton, 6, 1)

    self.mainGroupBox = QGroupBox()
    self.mainGroupBox.setTitle('Game Parameter Editor')
    self.mainGroupBox.setMinimumSize(2000, 600)
    self.mainGroupBox.setMaximumSize(2200, 1500)
    #self.mainGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    self.mainGroupBox.setLayout(_selectionGroupBoxLayout)

    ## Finish setup ##
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainGridLayout.addWidget(_headerLabel, 1, 0)
    _mainGridLayout.addWidget(self.mainGroupBox, 2, 0)
    self.setLayout(_mainGridLayout)

    self.handleGameParameterComboBoxChanged()
  def handleEditorExportToSqlButton(self):
    filename = 'file.sql'
    outputPath = f'{self.sqlExportPath}/{filename}'
    #with open(file=f'{self.sqlExportPath}/{filename}', mode='w') as _jsonFile:
    #  _logMessage = f'Writing file {outputPath}'
    #  logging.info(_logMessage)
    pass

  def handleEditorExportToCsvButton(self):
    #with open(file=_jsonOutfilePath, mode='w') as _jsonFile:
      #_logMessage = f'Writing file {_jsonOutfilePath}'
      #logging.info(_logMessage)
      #json.dump(obj=_jsonTemplate, fp=_jsonFile, indent=2)
    pass

  def handleGameParameterComboBoxChanged(self):
    _parameterName = self.gameParameterComboBox.currentText().upper()
    self.gameParameterModel.setParameter(_parameterName)
    self.editorNameLineEdit.setText(_parameterName)

  def handleNewGameParameterButton(self):
    self.editorNameLineEdit.setText('')
    _model = self.gameParameterModel

    # Retrieve current autoincrement value
    _newParameterTypeId = db.query(statement='SELECT seq FROM sqlite_sequence WHERE name=?', args=('GAME_PARAMETER_TYPE',), one=True)['seq']
    _newParameterTypeId += 1
    _model.setParameterId(parameterId=_newParameterTypeId)
    _model.invalidate()

    for i in range(10):
      _record = _model.sourceModel().record()
      _record.setValue('TYPE', _newParameterTypeId)
      _record.setValue('ID', i + 1)
      _model.sourceModel().insertRecord(-1, _record)
    # make record for type model, fill and insert, if even possible

  def handleUpdateGameParameterButton(self):
    self.dataTable.setModel(self.gameParameterModel)
    self.editorNameLineEdit.setText(self.gameParameterComboBox.currentText())
    self.editorNameLineEdit.setDisabled(True)

  def handleCopyGameParameterButton(self):
    pass

  def handleDeleteGameParameterButton(self):
    pass

  def handleEditorAddRowButton(self):
    self.addRowToEditor()

  def handleEditorSaveButton(self):
    _newParameterName = self.editorNameLineEdit.text().upper() if len(self.editorNameLineEdit.text()) > 0 else None
    if not _newParameterName:
      # ToDo Errorhandling
      return

    _idColumnId = dm.getDataModels().columnId('GAME_PARAMETER_TYPE', 'ID')
    _nameColumnId = dm.getDataModels().columnId('GAME_PARAMETER_TYPE', 'NAME')

    # Check if parameter name is already in use
    _parameterExists = False
    for i in range(self.gameParameterTypeModel.rowCount()):
      _name = self.gameParameterTypeModel.data(self.gameParameterTypeModel.index(i, _nameColumnId))

      if _name == _newParameterName:
        _parameterExists = True
        break

    if not _parameterExists:
      # Insert new parameter
      _parameterTypeRecord = self.gameParameterTypeModel.record()
      _parameterTypeRecord.setValue('NAME', _newParameterName)
      self.gameParameterTypeModel.insertRecord(-1, _parameterTypeRecord)
      self.gameParameterTypeModel.submitAll()


    # Get the parameters id
    _newParameterId = -1
    for i in range(self.gameParameterTypeModel.rowCount()):
      _id = self.gameParameterTypeModel.data(self.gameParameterTypeModel.index(i, _idColumnId))
      _name = self.gameParameterTypeModel.data(self.gameParameterTypeModel.index(i, _nameColumnId))

      if _name == _newParameterName:
        _newParameterId = _id
        break

      _newParameterId = max(_newParameterId, _id)

    # Process rows in table
    _model = self.dataTable.model()
    rc = _model.rowCount()
    for i in range(_model.rowCount()):
      _values = []
      for j in range(10):
        _valueId = _model.sourceModel().record().indexOf(f'VALUE_{j + 1}')
        _value = _model.data(_model.index(i, _valueId))
        _values.append(str(_value))

      _parameterRecord = _model.sourceModel().record()
      _parameterRecord.setValue('TYPE', _newParameterId)
      _parameterRecord.setValue('ID', i + 1)
      for k in range (len(_values)):
        _parameterRecord.setValue(f'VALUE_{k + 1}', _values[k])

      _sourceRow = _model.mapToSource(_model.index(i, 0)).row()
      _model.sourceModel().setRecord(_sourceRow, _parameterRecord)
      _model.sourceModel().submitAll()
      _model.sourceModel().select()


  def addRowToEditor(self):
      _model = self.dataTable.model()
      _parameterTypeId = _model.parameterId()
      _idColumnIndex = _model.sourceModel().record().indexOf('ID')

      _newId = 0
      for _row in range(_model.rowCount()):
        _id = _model.data(_model.index(_row, _idColumnIndex))
        _newId = max(_newId, _id)

      _newId += 1
      _record = _model.sourceModel().record()
      _record.setValue('TYPE', _parameterTypeId)
      _record.setValue('ID', _newId)
      _model.sourceModel().insertRecord(-1, _record)

class WeatherWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Data Models
    self.climateModel = dm.getDataModels().defineProxyModel(modelType=dm.GameParameterProxyModel, sourceModel='GAME_PARAMETER')
    self.climateModel.setParameter(parameterName='CLIMATE')
    self.monthModel = dm.getDataModels().defineProxyModel(modelType=dm.GameParameterProxyModel, sourceModel='GAME_PARAMETER')
    self.monthModel.setParameter(parameterName='MONTH')

    # Header Label
    _headerLabel = QLabel('Determine Weather')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    # Main Group Box
    self.weatherGroupBox = QGroupBox()
    self.weatherGroupBox.setTitle('Settings')
    self.weatherGroupBox.setMinimumSize(900, 900)
    self.weatherGroupBox.setMaximumSize(1500, 900)
    self.weatherGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    # Climate label and combo box
    _climateComboBoxLabel = QLabel('Climate:')
    _climateComboBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _climateComboBoxLabel.setMaximumSize(100, 20)

    self.climateComboBox = QComboBox()
    self.climateComboBox.setModel(self.climateModel)
    self.climateComboBox.setModelColumn(self.climateModel.sourceModel().record().indexOf('VALUE_1'))
    self.climateComboBox.setMaximumSize(150, 30)
    self.climateComboBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    # Month label and combo box
    _monthComboBoxLabel = QLabel('Month:')
    _monthComboBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _monthComboBoxLabel.setMaximumSize(100, 20)

    self.monthComboBox = QComboBox()
    self.monthComboBox.setModel(self.monthModel)
    self.monthComboBox.setModelColumn(self.monthModel.sourceModel().record().indexOf('VALUE_2'))
    self.monthComboBox.setMaximumSize(150, 30)
    self.monthComboBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    # Time span to generate label and LineEdit
    _timeSpanLabel = QLabel('Time span (weeks):')
    _timeSpanLabel.setFont(QFont('Ubuntu Sans', 12))
    _timeSpanLabel.setMaximumSize(150, 20)

    self.timespanSpinBox = QSpinBox()
    self.timespanSpinBox.setFont(QFont('Ubuntu Mono', 11))
    self.timespanSpinBox.setMinimum(1)
    self.timespanSpinBox.setMaximum(5000)
    self.timespanSpinBox.setValue(1)
    self.timespanSpinBox.setMaximumWidth(100)

    # Generate button
    self.generateButton = QPushButton("Generate")
    self.generateButton.clicked.connect(self.handleGenerateButton)

    # Generate For Entire Year button
    self.generateYearButton = QPushButton("Generate Year")
    self.generateYearButton.clicked.connect(self.handleGenerateYearButton)

    # Clear button
    self.clearButton = QPushButton("Clear")
    self.clearButton.clicked.connect(self.handleClearButton)

    # Save button
    self.saveToFileButton = QPushButton("Save To File")
    self.saveToFileButton.clicked.connect(self.handleSaveToFileButton)

    # Output text box
    self.weatherOutputPlainText = QPlainTextEdit()
    self.weatherOutputPlainText.setFont(QFont('Consolas', 12))
    self.weatherOutputPlainText.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

    # Vbox Layout for boxes and buttons

    # Finish weather GroupBox
    self.weatherGroupBoxLayout = QGridLayout()
    self.weatherGroupBoxLayout.setSpacing(20)
    self.weatherGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.weatherGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.weatherGroupBoxLayout.addWidget(_climateComboBoxLabel, 0, 0)
    self.weatherGroupBoxLayout.addWidget(self.climateComboBox, 0, 1)
    self.weatherGroupBoxLayout.addWidget(self.weatherOutputPlainText, 0, 2, 8, 1)
    self.weatherGroupBoxLayout.addWidget(_monthComboBoxLabel, 1, 0)
    self.weatherGroupBoxLayout.addWidget(self.monthComboBox, 1, 1)
    self.weatherGroupBoxLayout.addWidget(_timeSpanLabel, 2, 0)
    self.weatherGroupBoxLayout.addWidget(self.timespanSpinBox, 2, 1)
    self.weatherGroupBoxLayout.addWidget(self.generateButton, 3, 0)
    self.weatherGroupBoxLayout.addWidget(self.generateYearButton, 4, 0)
    self.weatherGroupBoxLayout.addWidget(self.saveToFileButton, 5, 0)
    self.weatherGroupBoxLayout.addWidget(self.clearButton, 6, 0)

    self.weatherGroupBox.setLayout(self.weatherGroupBoxLayout)

    # Finish setup
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainGridLayout.addWidget(_headerLabel, 1, 0)
    _mainGridLayout.addWidget(self.weatherGroupBox, 2, 0)
    self.setLayout(_mainGridLayout)

  def handleClearButton(self):
    self.weatherOutputPlainText.clear()

  def handleSaveToFileButton(self):
    _fileDialog = QFileDialog()
    _fileDialog.setNameFilter('*.txt')
    _fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    _filename = []

    _filePath = ''
    if _fileDialog.exec_():
      _filename = _fileDialog.selectedFiles()
      _filePath = _filename[0]
      _fileExtension = '.txt'
      _lastChars = _filePath[len(_filePath) - len(_fileExtension) : len(_filePath)]
      _filePath += _fileExtension if _lastChars != _fileExtension else ''

    with open(file=_filePath, mode='w', newline='') as _file:
      _file.write(self.weatherOutputPlainText.toPlainText())

  def handleGenerateButton(self):
    _climateStr = self.climateComboBox.currentText()
    _monthStr = self.monthComboBox.currentText()
    _climate = self.climateModel.data(self.climateModel.index(self.climateComboBox.currentIndex(), self.climateModel.sourceModel().record().indexOf('ID'), self.climateComboBox.rootModelIndex()))
    _month = int(self.monthModel.data(self.monthModel.index(self.monthComboBox.currentIndex(), self.monthModel.sourceModel().record().indexOf('VALUE_1'), self.monthComboBox.rootModelIndex())))
    _timespan = self.timespanSpinBox.value()

    self.weatherOutputPlainText.appendPlainText(f'Climate: {_climateStr}\n')
    self.weatherOutputPlainText.appendPlainText(f'Month: {_monthStr}\n')
    for _item in (self.generateWeather(_climate, _month, _timespan)):
      self.weatherOutputPlainText.appendPlainText(_item)

    self.weatherOutputPlainText.verticalScrollBar().setValue(self.weatherOutputPlainText.verticalScrollBar().minimum())

  def handleGenerateYearButton(self):
    _climateStr = self.climateComboBox.currentText()
    _timespan = 4
    _months = dm.getDataModels().modelData(modelName='MONTH', columns=('ID', 'NAME'))
    _climate = dm.getDataModels().modelData(modelName='CLIMATE', columns=('ID', 'NAME'), one=True)

    self.weatherOutputPlainText.appendPlainText(f'Climate: {_climateStr}\n')
    for _month in _months:
      self.weatherOutputPlainText.appendPlainText(f'Month: {_month['NAME']}\n')
      _result = self.generateWeather(_climate['ID'], _month['ID'], _timespan)
      for _item in _result:
        self.weatherOutputPlainText.appendPlainText(_item)

    self.weatherOutputPlainText.verticalScrollBar().setValue(self.weatherOutputPlainText.verticalScrollBar().minimum())

  def generateWeather(self, climate, month, timeSpan):
    _climate = climate
    _month = month

    _result = []
    for _interval in range(timeSpan):
      # Determine precipitation class, determined by rolling a d100 and checking against the precipitation classes' probability for given climate and month
      _precipitationClasses = db.query('select PRECIPITATION_CLASS, PROBABILITY from CLIMATE_X_MONTH_X_PRECIPITATION_CLASS where CLIMATE = ? and MONTH = ?', args=(_climate, _month))
      _precipitationClassD100Result = rand.randrange(1, 100)

      _finalPrecipitationClassId = 0
      _probabilitySum = 0
      for _precipitationClass in _precipitationClasses:
        _probability = _precipitationClass['PROBABILITY']
        _probabilitySum += _probability
        if _precipitationClassD100Result <= _probabilitySum:
          _finalPrecipitationClassId = _precipitationClass['PRECIPITATION_CLASS']
          break

      # Determine precipitation class details
      _precipitationData = db.query('select CLASS, NAME, PRECIPITATION, WIND, SOLID, HOOK, DESCRIPTION  from PRECIPITATION_CLASS where ID = ?', args=(_finalPrecipitationClassId,), one=True)

      _precipitation = hp.splitAndProcessValueStatement(_precipitationData['PRECIPITATION'])
      _precipitationResult = str(_precipitation[0]) + ' ' + str(_precipitation[1])

      _wind = hp.splitAndProcessValueStatement(_precipitationData['WIND'])
      _windResult = str(_wind[0]) + ' ' + str(_wind[1])

      _solidResult = hp.rollDice(1, 100)
      _solidStr = 'No'
      if _solidResult < int(_precipitationData['SOLID']):
        _solidStr = 'Yes'

      _hookResult = hp.rollDice(1, 100)
      _hookStr = 'No'
      if _hookResult < int(_precipitationData['HOOK']):
        _hookStr = 'Yes'

      # Determine weather event duration
      _weatherEvent = 'Storm'
      _weatherEventDurations = db.query(f'select DURATION, PROBABILITY from WEATHER_EVENT_DURATION wed inner join WEATHER_EVENT we on wed.WEATHER_EVENT = we.ID where we.NAME = ?', args=(_weatherEvent,))
      _durationD100Result = rand.randrange(1, 100)

      _probabilitySum = 0
      _finalDuration = {}
      for _duration in _weatherEventDurations:
        _probability = _duration['PROBABILITY']
        _probabilitySum += _probability
        if _durationD100Result <= _probabilitySum:
          _finalDuration = _duration
          break

      # Determine average temperature and apply potential deviation
      _averageTemperature = db.query(f'select TEMPERATURE_DEG, TEMPERATURE_F from AVERAGE_TEMPERATURE_X_MONTH_X_CLIMATE where CLIMATE = ? and MONTH = ?', args=(_climate, _month), one=True)

      _deviations = db.query(f'select PROBABILITY, DEVIATION_DEG, DEVIATION_F from TEMPERATURE_DEVIATION_X_CLIMATE where CLIMATE = ?', args=(_climate,))
      _deviationD100Result = rand.randrange(1, 100)
      _finalDeviation = {}
      _probabilitySum = 0
      for _deviation in _deviations:
        probability = _deviation['PROBABILITY']
        _probabilitySum += probability
        if _deviationD100Result <= _probabilitySum:
          _finalDeviation = _deviation
          break

      _finalTemperature = [_averageTemperature['TEMPERATURE_DEG'] + _finalDeviation['DEVIATION_DEG'], _averageTemperature['TEMPERATURE_F'] + _finalDeviation['DEVIATION_F']]

      _headline = f'Week {_interval + 1}'
      _result.append(_headline)
      _result.append('=' * len(_headline) + '\n')
      _result.append(f'Precipitation Class: {_precipitationData['CLASS']}')
      _result.append(f'Name:  {_precipitationData['NAME']}')
      _result.append(f'Description: {_precipitationData['DESCRIPTION']}')
      _result.append(f'Precipitation: {_precipitationResult}')
      _result.append(f'Wind: {_windResult}')
      _result.append(f'Solid: {_solidStr}')
      _result.append(f'Hook: {_hookStr}')
      _result.append(f'Duration: {_finalDuration['DURATION']}')
      _result.append(f'Average Temperature: {_averageTemperature['TEMPERATURE_DEG']} C / {_averageTemperature['TEMPERATURE_F']} F')
      _result.append(f'Temperature Deviation: {_finalDeviation['DEVIATION_DEG']} C / {_finalDeviation['DEVIATION_F']} F')
      _result.append(f'Temperature: {_finalTemperature[0]} C / {_finalTemperature[1]} F')
      _result.append('')

    return _result


class Tools(QWidget):
  def __init__(self):
    super().__init__()

    self.characterBuilderButton = QPushButton("Character Builder")
    self.dungeonRoomButton = QPushButton("Dungeon Creator")
    self.itemDataManagerButton = QPushButton("Item Data Manager")
    self.gameParameterManagerButton = QPushButton("Game Parameter Manager")
    self.weatherButton = QPushButton("Weather")

    self.menuWidget = QWidget()
    self.defineMenuLayout()

    self.characterBuilderWidget = CharacterBuildWidget()
    self.itemDataManagerWidget = ItemDataManagerWidget()
    self.dungeonRoomWidget = DungeonCreatorWidget()
    self.gameParameterManagerWidget = GameParameterManager()
    self.weatherWidget = WeatherWidget()

    self.contentStackedWidget = QStackedWidget()
    self.defineContentStackedWidget()

    self.mainGridLayout = QGridLayout()
    self.mainGridLayout.addWidget(self.menuWidget, 0, 0)
    self.mainGridLayout.addWidget(self.contentStackedWidget, 0, 1)
    self.setLayout(self.mainGridLayout)

  def changeWidget(self, widget):
    self.contentStackedWidget.setCurrentWidget(widget)

  def defineMenuLayout(self):
    self.characterBuilderButton.clicked.connect(lambda clicked: self.changeWidget(self.characterBuilderWidget))
    self.dungeonRoomButton.clicked.connect(lambda clicked: self.changeWidget(self.dungeonRoomWidget))
    self.itemDataManagerButton.clicked.connect(lambda clicked: self.changeWidget(self.itemDataManagerWidget))
    self.gameParameterManagerButton.clicked.connect(lambda clicked: self.changeWidget(self.gameParameterManagerWidget))
    self.weatherButton.clicked.connect(lambda clicked: self.changeWidget(self.weatherWidget))

    menuLayout = QVBoxLayout()
    menuLayout.addWidget(self.characterBuilderButton)
    menuLayout.addWidget(self.itemDataManagerButton)
    menuLayout.addWidget(self.dungeonRoomButton)
    menuLayout.addWidget(self.gameParameterManagerButton)
    menuLayout.addWidget(self.weatherButton)
    menuLayout.setSpacing(15)
    menuLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.menuWidget.setLayout(menuLayout)

  def defineContentStackedWidget(self):
    self.contentStackedWidget.addWidget(self.characterBuilderWidget)
    self.contentStackedWidget.addWidget(self.itemDataManagerWidget)
    self.contentStackedWidget.addWidget(self.dungeonRoomWidget)
    self.contentStackedWidget.addWidget(self.gameParameterManagerWidget)
    self.contentStackedWidget.addWidget(self.weatherWidget)
    self.contentStackedWidget.setCurrentIndex(1)

