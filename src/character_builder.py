import copy
import json
import logging
import math
import pathlib
from random import choice
from collections.abc import Callable

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtSql import QSqlTableModel
from PySide6.QtWidgets import (
  QLabel,
  QPushButton,
  QGridLayout,
  QWidget,
  QVBoxLayout,
  QStackedWidget,
  QSizePolicy,
  QGroupBox,
  QComboBox, QPlainTextEdit, QSpacerItem, QFileDialog, QSpinBox, QTableWidget, QTableWidgetItem, QTableView, QLineEdit,
  QHBoxLayout, QCheckBox, QHeaderView, QApplication, QStyle, QScrollArea,
  QInputDialog, QDialog, QAbstractItemView, QToolButton, QDoubleSpinBox
)

from pypdf import PdfReader, PdfWriter

from database import beginTransaction
from src import data_models as dm
from src import database as db
from src import helper as hp
from src import qt_helper as qh
from src import qt_wrapper as qw
from src import app_config as apc
from src import data_access as data

class CharacterBuilderWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Fields
    self.className = ''
    self.classData = None
    self.hpRolls = []

    # Data Models
    self.raceModel = dm.getDataModels().model('RACE')
    self.classModel = dm.getDataModels().model('CLASS')
    self.alignmentModel = dm.getDataModels().model('ALIGNMENT')

    # Header Label
    _headerLabel = QLabel('Character Builder')
    _headerLabel.setObjectName('headerLabel')

    # GENERAL #

    # Character name
    _nameLineEditLabel = QLabel('Name:')
    self.nameLineEdit = QLineEdit()
    self.nameLineEdit.setProperty('name', 'name')

    _rollCharacterNameButton = self.makeRollToolButtonForProperty('Roll Character Name', self.handleRollCharacterNameButton)

    # Race
    _raceComboBoxLabel = QLabel('Race:')
    self.raceComboBox = QComboBox()
    self.raceComboBox.setModel(self.raceModel)
    self.raceComboBox.setModelColumn(self.raceModel.record().indexOf('NAME'))
    self.raceComboBox.setProperty('name', 'race')

    # Class
    _classComboBoxLabel = QLabel('Class:')
    self.classComboBox = QComboBox()
    self.classComboBox.setModel(self.classModel)
    self.classComboBox.setModelColumn(self.classModel.record().indexOf('NAME'))
    self.classComboBox.setCurrentIndex(-1)
    self.classComboBox.currentIndexChanged.connect(self.handleClassComboBoxChanged)
    self.classComboBox.setProperty('name', 'class')

    # Level
    _levelSpinBoxLabel = QLabel('Level:')
    self.levelSpinBox = self.makeSpinBox(name='level', minValue=1, maxValue=100, currentValue=1, targetFunction=self.handleLevelSpinBoxChanged)
    _rollLevelButton = self.makeRollToolButtonForProperty('Roll Level', self.handleRollLevelButton)

    # XP
    _xpLineEditLabel = QLabel('XP:')
    self.xpLineEdit = QLineEdit()
    self.xpLineEdit.setText('0')
    self.xpLineEdit.setProperty('name', 'xp')

    # XP Bonus
    _xpBonusLineEditLabel = QLabel('XP Bonus:')
    self.xpBonusLineEdit = QLineEdit()
    self.xpBonusLineEdit.setProperty('name', 'xp_bonus')
    self.xpBonusLineEdit.setText('None')

    # Starting Wealth
    _startingWealthSpinBoxLabel = QLabel('Starting Wealth:')
    _startingWealthSpinBoxLabel.setToolTip('Gold Pieces')
    self.startingWealthSpinBox = self.makeSpinBox(name='starting_wealth', minValue=0, maxValue=10000, currentValue=0)

    _rollStartingWealthButton = self.makeRollToolButtonForProperty('Roll Starting Wealth', self.handleRollStartingWealthButton)

    # Character title
    _titleLineEditLabel = QLabel('Title:')
    self.titleLineEdit = QLineEdit()
    self.titleLineEdit.setProperty('name', 'title')

    # Character alignment
    _alignmentComboboxLabel = QLabel('Alignment:')
    self.alignmentComboBox = QComboBox()
    self.alignmentComboBox.setModel(self.alignmentModel)
    self.alignmentComboBox.setModelColumn(self.alignmentModel.record().indexOf('NAME'))
    self.alignmentComboBox.setProperty('name', 'alignment')

    # Character sex
    _sexComboBoxLabel = QLabel('Sex')
    self.sexComboBox = QComboBox()
    self.sexComboBox.addItem('Female')
    self.sexComboBox.addItem('Male')
    self.sexComboBox.addItem('None')
    self.sexComboBox.setCurrentText('None')
    self.sexComboBox.setProperty('name', 'sex')

    # Character age
    _ageSpinBoxLabel = QLabel('Age:')
    self.ageSpinBox = self.makeSpinBox(name='age', minValue=1, maxValue=99999, currentValue=1)
    _rollCharacterAgeButton = self.makeRollToolButtonForProperty('Roll Character Age', self.handleRollCharacterAgeButton)

    # Character height
    _heightLineEditLabel = QLabel('Height:')
    _heightLineEditLabel.setToolTip('Feet and Inches')
    self.heightLineEdit = QLineEdit()
    self.heightLineEdit.setProperty('name', 'height')
    _rollCharacterHeightButton = self.makeRollToolButtonForProperty('Roll Character Height', self.handleRollCharacterHeightButton)

    # Character weight
    _weightLineEditLabel = QLabel('Weight:')
    _weightLineEditLabel.setToolTip('Pounds')
    self.weightLineEdit = QLineEdit()
    self.weightLineEdit.setProperty('name', 'weight')
    _rollCharacterWeightButton = self.makeRollToolButtonForProperty('Roll Character Weight', self.handleRollCharacterWeightButton)

    # MOVEMENT #

    # Overland
    _movementOverlandLabelLabel = QLabel('Overland:')
    _movementOverlandLabelLabel.setToolTip('Miles per day')
    self.movementOverlandLabel = QLabel()

    # Exploration
    _movementExplorationLineEditLabel = QLabel('Exploration:')
    _movementExplorationLineEditLabel.setToolTip('Feet per turn')
    self.movementExplorationLineEdit = QLineEdit('120')
    self.movementExplorationLineEdit.setProperty('name', 'movement_exploration')
    self.movementExplorationLineEdit.textChanged.connect(self.handleMovementExplorationLineEditTextChanged)

    # Encounter
    _movementEncounterLabelLabel = QLabel('Encounter:')
    _movementEncounterLabelLabel.setToolTip('Feet per round')
    self.movementEncounterLabel = QLabel()

    # ABILITIES #

    # Strength score
    _strengthSpinBoxLabel = QLabel('Strength:')
    self.strengthSpinBox = self.makeSpinBox(name='strength_score', minValue=1, maxValue=30, currentValue=10, targetFunction=self.handleStrengthSpinBoxValueChanged)
    _rollStrengthButton = self.makeRollToolButtonForProperty('Roll Strength Score', lambda : self.handleRollAbilityScoreButtonClicked('STR'))

    _strengthModSpinBoxLabel = QLabel('Mod:')
    self.strengthModSpinBox = self.makeSpinBox(name='strength_mod', minValue=-3, maxValue=3, targetFunction=self.handleStrengthModSpinBoxValueChanged)

    # Intelligence score
    _intelligenceSpinBoxLabel = QLabel('Intelligence:')
    self.intelligenceSpinBox = self.makeSpinBox(name='intelligence_score', minValue=1, maxValue=30, currentValue=10, targetFunction=self.handleIntelligenceSpinBoxValueChanged)
    _rollIntelligenceButton = self.makeRollToolButtonForProperty('Roll Intelligence Score', lambda : self.handleRollAbilityScoreButtonClicked('INT'))

    _intelligenceModSpinBoxLabel = QLabel('Mod:')
    self.intelligenceModSpinBox = self.makeSpinBox(name='intelligence_mod', minValue=-3, maxValue=3)

    # Wisdom score
    _wisdomSpinBoxLabel = QLabel('Wisdom:')
    self.wisdomSpinBox = self.makeSpinBox(name='wisdom_score', minValue=1, maxValue=30, currentValue=10, targetFunction=self.handleWisdomSpinBoxValueChanged)
    _rollWisdomButton = self.makeRollToolButtonForProperty('Roll Wisdom Score', lambda : self.handleRollAbilityScoreButtonClicked('WIS'))

    _wisdomModSpinBoxLabel = QLabel('Mod:')
    self.wisdomModSpinBox = self.makeSpinBox(name='wisdom_mod', minValue=-3, maxValue=3)

    # Dexterity score
    _dexteritySpinBoxLabel = QLabel('Dexterity:')
    self.dexteritySpinBox = self.makeSpinBox(name='dexterity_score', minValue=1, maxValue=30, currentValue=10, targetFunction=self.handleDexteritySpinBoxValueChanged)
    _rollDexterityButton = self.makeRollToolButtonForProperty('Roll Dexterity Score', lambda : self.handleRollAbilityScoreButtonClicked('DEX'))

    _dexterityModSpinBoxLabel = QLabel('Mod:')
    self.dexterityModSpinBox = self.makeSpinBox(name='dexterity_mod', minValue=-3, maxValue=3, targetFunction=self.handleDexterityModSpinBoxValueChanged)

    # Constitution score
    _constitutionSpinBoxLabel = QLabel('Constitution:')
    self.constitutionSpinBox = self.makeSpinBox(name='constitution_score', minValue=1, maxValue=30, currentValue=10, targetFunction=self.handleConstitutionSpinBoxValueChanged)
    _rollConstitutionButton = self.makeRollToolButtonForProperty('Roll Constitution Score', lambda : self.handleRollAbilityScoreButtonClicked('CON'))

    _constitutionModSpinBoxLabel = QLabel('Mod:')
    self.constitutionModSpinBox = self.makeSpinBox(name='constitution_mod', minValue=-3, maxValue=3)

    # Charisma score
    _charismaSpinBoxLabel = QLabel('Charisma:')
    self.charismaSpinBox = self.makeSpinBox(name='charisma_score', minValue=1, maxValue=30, currentValue=10, targetFunction=self.handleCharismaSpinBoxValueChanged)
    _rollCharismaButton = self.makeRollToolButtonForProperty('Roll Charisma Score', lambda : self.handleRollAbilityScoreButtonClicked('CHA'))

    _charismaModSpinBoxLabel = QLabel('Mod:')
    self.charismaModSpinBox = self.makeSpinBox(name='charisma_mod', minValue=-3, maxValue=3)

    # Generate-all button
    _generateAllAbilityScoresButton = QPushButton('Generate All Scores')
    _generateAllAbilityScoresButton.clicked.connect(self.handleGenerateAllAbilityScoresButton)

    # Reset button
    _resetAbilityScoresButton = QPushButton('Reset Scores')
    _resetAbilityScoresButton.clicked.connect(self.handleResetAbilityScoresButton)

    # COMBAT #

    # Character HD
    self.hdSpinBoxLabel = QLabel('HD:')
    self.hdSpinBox = self.makeSpinBox(name='hit_dice', minValue=1, maxValue=100, currentValue=1, targetFunction=self.handleHdSpinBoxValueChanged)

    # Character HP
    _hpLineEditLabel = QLabel('Hit Points:')
    self.hpLineEdit = QLineEdit()
    self.hpLineEdit.setProperty('name', 'hit_points')

    # Roll HP button
    _rollHpButton = self.makeRollToolButtonForProperty('Roll Hit Points', self.handleRollHpButtonClicked)

    # THAC0
    _thac0SpinBoxLabel = QLabel('THAC0:')
    self.thac0SpinBox = QSpinBox()
    self.thac0SpinBox = self.makeSpinBox(name='thac0', minValue=5, maxValue=20, currentValue=19)

    # Character AC
    _acSpinBoxLabel = QLabel('AC:')
    self.acSpinBox = QSpinBox()
    self.acSpinBox = self.makeSpinBox(name='ac', minValue=-3, maxValue=22, currentValue=9)
    #self.acSpinBox.valueChanged.connect(self.handleAcSpinBoxValueChanged)

    # AC Bonus
    _acBonusLabelLabel = QLabel('AC Bonus:')
    self.acBonusLabel = QLabel('0')

    #Unarmored AC
    _unarmoredACLabelLabel = QLabel('Unarmored AC:')
    self.unarmoredACLabel = QLabel('9')

    # Melee Bonus
    _meleeBonusLabel = QLabel('Melee Bonus:')
    self.meleeBonusSpinBox = QSpinBox()
    self.meleeBonusSpinBox = self.makeSpinBox(name='meleeBonus', minValue=-3, maxValue=3, currentValue=0)

    # Missile Bonus
    _missileBonusLabel = QLabel('Missile Bonus:')
    self.missileBonusSpinBox = QSpinBox()
    self.missileBonusSpinBox = self.makeSpinBox(name='missileBonus', minValue=-3, maxValue=3, currentValue=0)

    # Missile Bonus
    _initiativeBonusLabel = QLabel('Initiative Bonus:')
    self.initiativeBonusSpinBox = QSpinBox()
    self.initiativeBonusSpinBox = self.makeSpinBox(name='initiativeBonus', minValue=-10, maxValue=10, currentValue=0)

    # SAVING THROWS #
    _minSave = 1
    _maxSave = 16
    _savePoisonDeathSpinBoxLabel = QLabel('Death, Poison:')
    self.savePoisonDeathSpinBox = self.makeSpinBox(name='save_d', minValue=_minSave, maxValue=_maxSave, currentValue=_maxSave)

    _saveMagicWandsSpinBoxLabel = QLabel('Magic Wands:')
    self.saveMagicWandsSpinBox = self.makeSpinBox(name='save_w', minValue=_minSave, maxValue=_maxSave, currentValue=_maxSave)

    _saveParalysisPetrificationSpinBoxLabel = QLabel('Paralysis, Petrification:')
    self.saveParalysisPetrificationSpinBox = self.makeSpinBox(name='save_p', minValue=_minSave, maxValue=_maxSave, currentValue=_maxSave)

    _saveBreathAttacksSpinBoxLabel = QLabel('Breath Attacks:')
    self.saveBreathAttacksSpinBox = self.makeSpinBox(name='save_b', minValue=_minSave, maxValue=_maxSave, currentValue=_maxSave)

    _saveSpellsRodsStavesSpinBoxLabel = QLabel('Spells, Magic Rods and Staves:')
    self.saveSpellsRodsStavesSpinBox = self.makeSpinBox(name='save_s', minValue=_minSave, maxValue=_maxSave, currentValue=_maxSave)

    _wisdomModifierToSaveVsMagicLabel = QLabel('Wisdom modifier to saves vs. magic:')
    self.wisdomModifierToSaveVsMagicSpinBox = self.makeSpinBox(name='wisdom_mod_to_save_vs_magic', minValue=_minSave, maxValue=_maxSave, currentValue=_maxSave)

    # ADVENTURING SKILLS #

    # Foraging In The Wild
    _foragingSkillLabel = QLabel('Forage In The Wild:')
    self.foragingSkillSpinBox = self.makeSpinBox(name='skill_forage', minValue=1, maxValue=6, currentValue=1)

    # Find Room Trap
    _findRoomTrapSkillLabel = QLabel('Find Room Trap:')
    self.findRoomTrapSkillSpinBox = self.makeSpinBox(name='skill_find_room_trap', minValue=1, maxValue=6, currentValue=1)

    # Hunt In The Wild
    _huntingSkillLabel = QLabel('Hunt In The Wild:')
    self.huntingSkillSpinBox = self.makeSpinBox(name='skill_hunt', minValue=1, maxValue=6, currentValue=1)

    # Listen At Door
    _listenAtDoorSkillLabel = QLabel('Listen At Door:')
    self.listenAtDoorSkillSpinBox = self.makeSpinBox(name='skill_listen_door', minValue=1, maxValue=6, currentValue=1)

    # Foraging
    _openStuckDoorSkillLabel = QLabel('Open Stuck Door:')
    self.openStuckDoorSkillSpinBox = self.makeSpinBox(name='skill_open_stuck_door', minValue=1, maxValue=6, currentValue=1)

    # Foraging
    _findSecretDoorSkillLabel = QLabel('Find Secret Door:')
    self.findSecretDoorSkillSpinBox = self.makeSpinBox(name='skill_find_secret_door', minValue=1, maxValue=6, currentValue=1)

    # LANGUAGES #
    _literacyLabel = QLabel('Literacy:')
    _literacyLabel.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    self.literacyLineEdit = QLineEdit()

    _spokenLanguagesLabel = QLabel('Spoken Languages:')
    self.spokenLanguagesLineEdit = QLineEdit()
    self.spokenLanguagesLineEdit.setProperty('name', 'spokenLanguages')

    _languagesLineEditLabel = QLabel('Languages:')
    self.languagesLineEdit = QLineEdit()
    self.languagesLineEdit.setProperty('name', 'languages')

    _npcReactionsModifierLabel = QLabel('NPC Reactions Mod:')
    self.npcReactionsModifierSpinBox = QSpinBox()
    self.npcReactionsModifierSpinBox.setMinimum(-10)
    self.npcReactionsModifierSpinBox.setMaximum(10)

    _maxNumberOfRetainersLabel = QLabel('Maximum Number of Retainers:')
    self.maxNumberOfRetainersSpinBox = QSpinBox()
    self.maxNumberOfRetainersSpinBox.setMinimum(1)
    self.maxNumberOfRetainersSpinBox.setMaximum(99)

    _retainerLoyaltyLabel = QLabel('Retainer Loyalty:')
    self.retainerLoyaltySpinBox = QSpinBox()
    self.retainerLoyaltySpinBox.setMinimum(2)
    self.retainerLoyaltySpinBox.setMaximum(12)

    ## Sub Group boxes

    # General Group Box
    self.generalGroupBoxLayout = QGridLayout()
    self.generalGroupBoxLayout.setSpacing(20)
    self.generalGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.generalGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.generalGroupBoxLayout.addWidget(_nameLineEditLabel, 0, 0)
    self.generalGroupBoxLayout.addWidget(self.nameLineEdit, 0, 1)
    self.generalGroupBoxLayout.addWidget(_rollCharacterNameButton, 0, 2)
    self.generalGroupBoxLayout.addWidget(_titleLineEditLabel, 0, 3)
    self.generalGroupBoxLayout.addWidget(self.titleLineEdit, 0, 4)
    self.generalGroupBoxLayout.addWidget(_classComboBoxLabel, 1, 0)
    self.generalGroupBoxLayout.addWidget(self.classComboBox, 1, 1)
    self.generalGroupBoxLayout.addWidget(_alignmentComboboxLabel, 1, 3)
    self.generalGroupBoxLayout.addWidget(self.alignmentComboBox, 1, 4)
    #self.generalGroupBoxLayout.addWidget(_raceComboBoxLabel, 2, 0)
    #self.generalGroupBoxLayout.addWidget(self.raceComboBox, 2, 1)
    self.generalGroupBoxLayout.addWidget(_levelSpinBoxLabel, 2, 0)
    self.generalGroupBoxLayout.addWidget(self.levelSpinBox, 2, 1)
    self.generalGroupBoxLayout.addWidget(_rollLevelButton, 2, 2)
    self.generalGroupBoxLayout.addWidget(_sexComboBoxLabel, 2, 3)
    self.generalGroupBoxLayout.addWidget(self.sexComboBox, 2, 4)
    self.generalGroupBoxLayout.addWidget(_xpLineEditLabel, 3, 0)
    self.generalGroupBoxLayout.addWidget(self.xpLineEdit, 3, 1)
    self.generalGroupBoxLayout.addWidget(_ageSpinBoxLabel, 3, 3)
    self.generalGroupBoxLayout.addWidget(self.ageSpinBox, 3, 4)
    self.generalGroupBoxLayout.addWidget(_rollCharacterAgeButton, 3, 5)
    self.generalGroupBoxLayout.addWidget(_xpBonusLineEditLabel, 4, 0)
    self.generalGroupBoxLayout.addWidget(self.xpBonusLineEdit, 4, 1)
    self.generalGroupBoxLayout.addWidget(_heightLineEditLabel, 4, 3)
    self.generalGroupBoxLayout.addWidget(self.heightLineEdit, 4, 4)
    self.generalGroupBoxLayout.addWidget(_rollCharacterHeightButton, 4, 5)
    self.generalGroupBoxLayout.addWidget(_startingWealthSpinBoxLabel, 5, 0)
    self.generalGroupBoxLayout.addWidget(self.startingWealthSpinBox, 5, 1)
    self.generalGroupBoxLayout.addWidget(_rollStartingWealthButton, 5, 2)
    self.generalGroupBoxLayout.addWidget(_weightLineEditLabel, 5, 3)
    self.generalGroupBoxLayout.addWidget(self.weightLineEdit, 5, 4)
    self.generalGroupBoxLayout.addWidget(_rollCharacterWeightButton, 5, 5)

    self.generalGroupBoxLayout.setColumnStretch(0, 1)
    self.generalGroupBoxLayout.setColumnStretch(1, 2)
    self.generalGroupBoxLayout.setColumnStretch(2, 1)
    self.generalGroupBoxLayout.setColumnStretch(3, 2)
    self.generalGroupBoxLayout.setColumnStretch(4, 2)
    self.generalGroupBoxLayout.setColumnStretch(5, 1)

    self.generalGroupBox = QGroupBox()
    self.generalGroupBox.setTitle('General')
    self.generalGroupBox.setLayout(self.generalGroupBoxLayout)

    # Abilities group box
    self.abilitiesGroupBoxLayout = QGridLayout()
    self.abilitiesGroupBoxLayout.setSpacing(20)
    self.abilitiesGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.abilitiesGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.abilitiesGroupBoxLayout.addWidget(_strengthSpinBoxLabel, 0, 0)
    self.abilitiesGroupBoxLayout.addWidget(self.strengthSpinBox, 0, 1)
    self.abilitiesGroupBoxLayout.addWidget(_rollStrengthButton, 0, 2)
    self.abilitiesGroupBoxLayout.addWidget(_strengthModSpinBoxLabel, 0, 3)
    self.abilitiesGroupBoxLayout.addWidget(self.strengthModSpinBox, 0, 4)
    self.abilitiesGroupBoxLayout.addWidget(_intelligenceSpinBoxLabel, 1, 0)
    self.abilitiesGroupBoxLayout.addWidget(self.intelligenceSpinBox, 1, 1)
    self.abilitiesGroupBoxLayout.addWidget(_rollIntelligenceButton, 1, 2)
    #self.abilitiesGroupBoxLayout.addWidget(_intelligenceModSpinBoxLabel, 1, 3)
    #self.abilitiesGroupBoxLayout.addWidget(self.intelligenceModSpinBox, 1, 4)
    self.abilitiesGroupBoxLayout.addWidget(_wisdomSpinBoxLabel, 2, 0)
    self.abilitiesGroupBoxLayout.addWidget(self.wisdomSpinBox, 2, 1)
    self.abilitiesGroupBoxLayout.addWidget(_rollWisdomButton, 2, 2)
    self.abilitiesGroupBoxLayout.addWidget(_wisdomModSpinBoxLabel, 2, 3)
    self.abilitiesGroupBoxLayout.addWidget(self.wisdomModSpinBox, 2, 4)
    self.abilitiesGroupBoxLayout.addWidget(_dexteritySpinBoxLabel, 3, 0)
    self.abilitiesGroupBoxLayout.addWidget(self.dexteritySpinBox, 3, 1)
    self.abilitiesGroupBoxLayout.addWidget(_rollDexterityButton, 3, 2)
    self.abilitiesGroupBoxLayout.addWidget(_dexterityModSpinBoxLabel, 3, 3)
    self.abilitiesGroupBoxLayout.addWidget(self.dexterityModSpinBox, 3, 4)
    self.abilitiesGroupBoxLayout.addWidget(_constitutionSpinBoxLabel, 4, 0)
    self.abilitiesGroupBoxLayout.addWidget(self.constitutionSpinBox, 4, 1)
    self.abilitiesGroupBoxLayout.addWidget(_rollConstitutionButton, 4, 2)
    self.abilitiesGroupBoxLayout.addWidget(_constitutionModSpinBoxLabel, 4, 3)
    self.abilitiesGroupBoxLayout.addWidget(self.constitutionModSpinBox, 4, 4)
    self.abilitiesGroupBoxLayout.addWidget(_charismaSpinBoxLabel, 5, 0)
    self.abilitiesGroupBoxLayout.addWidget(self.charismaSpinBox, 5, 1)
    self.abilitiesGroupBoxLayout.addWidget(_rollCharismaButton, 5, 2)
    #self.abilitiesGroupBoxLayout.addWidget(_charismaModSpinBoxLabel, 5, 3)
    #self.abilitiesGroupBoxLayout.addWidget(self.charismaModSpinBox, 5, 4)
    self.abilitiesGroupBoxLayout.addWidget(_generateAllAbilityScoresButton, 6, 0, 1, 2)
    self.abilitiesGroupBoxLayout.addWidget(_resetAbilityScoresButton, 6, 2, 1, 2)

    self.abilitiesGroupBoxLayout.setColumnStretch(0, 1)
    self.abilitiesGroupBoxLayout.setColumnStretch(1, 1)
    self.abilitiesGroupBoxLayout.setColumnStretch(2, 1)
    self.abilitiesGroupBoxLayout.setColumnStretch(3, 1)
    self.abilitiesGroupBoxLayout.setColumnStretch(4, 1)
    self.abilitiesGroupBoxLayout.setColumnStretch(5, 3)

    self.abilitiesGroupBox = QGroupBox()
    self.abilitiesGroupBox.setTitle('Abilities')
    self.abilitiesGroupBox.setLayout(self.abilitiesGroupBoxLayout)

    # Movement group box
    self.movementGroupBoxLayout = QGridLayout()
    self.movementGroupBoxLayout.setSpacing(20)
    self.movementGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.movementGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.movementGroupBoxLayout.addWidget(_movementOverlandLabelLabel, 0, 0)
    self.movementGroupBoxLayout.addWidget(self.movementOverlandLabel, 0, 1)
    self.movementGroupBoxLayout.addWidget(_movementExplorationLineEditLabel, 1, 0)
    self.movementGroupBoxLayout.addWidget(self.movementExplorationLineEdit, 1, 1)
    self.movementGroupBoxLayout.addWidget(_movementEncounterLabelLabel, 2, 0)
    self.movementGroupBoxLayout.addWidget(self.movementEncounterLabel, 2, 1)

    self.movementGroupBoxLayout.setColumnStretch(0, 1)
    self.movementGroupBoxLayout.setColumnStretch(1, 1)
    self.movementGroupBoxLayout.setColumnStretch(2, 2)

    self.movementGroupBox = QGroupBox()
    self.movementGroupBox.setTitle('Movement')
    self.movementGroupBox.setLayout(self.movementGroupBoxLayout)

    # Combat group box
    self.combatGroupBoxLayout = QGridLayout()
    self.combatGroupBoxLayout.setSpacing(20)
    self.combatGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.combatGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.combatGroupBoxLayout.addWidget(self.hdSpinBoxLabel, 0, 0)
    self.combatGroupBoxLayout.addWidget(self.hdSpinBox, 0, 1)
    self.combatGroupBoxLayout.addWidget(_hpLineEditLabel, 0, 2)
    self.combatGroupBoxLayout.addWidget(self.hpLineEdit, 0, 3)
    self.combatGroupBoxLayout.addWidget(_rollHpButton, 0, 4, alignment=Qt.AlignmentFlag.AlignLeft)
    self.combatGroupBoxLayout.addWidget(_thac0SpinBoxLabel, 1, 0)
    self.combatGroupBoxLayout.addWidget(self.thac0SpinBox, 1, 1)
    self.combatGroupBoxLayout.addWidget(_acSpinBoxLabel, 2, 0)
    self.combatGroupBoxLayout.addWidget(self.acSpinBox, 2, 1)
    self.combatGroupBoxLayout.addWidget(_acBonusLabelLabel, 2, 2)
    self.combatGroupBoxLayout.addWidget(self.acBonusLabel, 2, 3)
    self.combatGroupBoxLayout.addWidget(_unarmoredACLabelLabel, 2, 4)
    self.combatGroupBoxLayout.addWidget(self.unarmoredACLabel, 2, 5)
    self.combatGroupBoxLayout.addWidget(_meleeBonusLabel, 3, 0)
    self.combatGroupBoxLayout.addWidget(self.meleeBonusSpinBox, 3, 1)
    self.combatGroupBoxLayout.addWidget(_missileBonusLabel, 4, 0)
    self.combatGroupBoxLayout.addWidget(self.missileBonusSpinBox, 4, 1)
    self.combatGroupBoxLayout.addWidget(_initiativeBonusLabel, 5, 0)
    self.combatGroupBoxLayout.addWidget(self.initiativeBonusSpinBox, 5, 1)

    self.combatGroupBoxLayout.setColumnStretch(0, 1)
    self.combatGroupBoxLayout.setColumnStretch(1, 1)
    self.combatGroupBoxLayout.setColumnStretch(2, 1)
    self.combatGroupBoxLayout.setColumnStretch(3, 1)
    self.combatGroupBoxLayout.setColumnStretch(4, 0)
    self.combatGroupBoxLayout.setColumnStretch(5, 1)
    self.combatGroupBoxLayout.setColumnStretch(6, 1)

    self.combatGroupBox = QGroupBox()
    self.combatGroupBox.setTitle('Combat')
    self.combatGroupBox.setLayout(self.combatGroupBoxLayout)

    # Saving Throw group box
    self.saveGroupBoxLayout = QGridLayout()
    self.saveGroupBoxLayout.setSpacing(20)
    self.saveGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.saveGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.saveGroupBoxLayout.addWidget(_savePoisonDeathSpinBoxLabel, 0, 0)
    self.saveGroupBoxLayout.addWidget(self.savePoisonDeathSpinBox, 0, 1)
    self.saveGroupBoxLayout.addWidget(_saveMagicWandsSpinBoxLabel, 1, 0)
    self.saveGroupBoxLayout.addWidget(self.saveMagicWandsSpinBox, 1, 1)
    self.saveGroupBoxLayout.addWidget(_saveParalysisPetrificationSpinBoxLabel, 2, 0)
    self.saveGroupBoxLayout.addWidget(self.saveParalysisPetrificationSpinBox, 2, 1)
    self.saveGroupBoxLayout.addWidget(_saveBreathAttacksSpinBoxLabel, 3, 0)
    self.saveGroupBoxLayout.addWidget(self.saveBreathAttacksSpinBox, 3, 1)
    self.saveGroupBoxLayout.addWidget(_saveSpellsRodsStavesSpinBoxLabel, 4, 0)
    self.saveGroupBoxLayout.addWidget(self.saveSpellsRodsStavesSpinBox, 4, 1)
    self.saveGroupBoxLayout.addWidget(_wisdomModifierToSaveVsMagicLabel, 5, 0)
    self.saveGroupBoxLayout.addWidget(self.wisdomModifierToSaveVsMagicSpinBox, 5, 1)

    self.saveGroupBoxLayout.setColumnStretch(0, 1)
    self.saveGroupBoxLayout.setColumnStretch(1, 1)
    self.saveGroupBoxLayout.setColumnStretch(2, 2)

    self.saveGroupBox = QGroupBox()
    self.saveGroupBox.setTitle('Saving Throws')
    self.saveGroupBox.setLayout(self.saveGroupBoxLayout)

    # Adventuring Skills group box
    self.adventureSkillsGroupBoxLayout = QGridLayout()
    self.adventureSkillsGroupBoxLayout.setSpacing(20)
    self.adventureSkillsGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.adventureSkillsGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.adventureSkillsGroupBoxLayout.addWidget(_foragingSkillLabel, 0, 0)
    self.adventureSkillsGroupBoxLayout.addWidget(self.foragingSkillSpinBox, 0, 1)
    self.adventureSkillsGroupBoxLayout.addWidget(_findRoomTrapSkillLabel, 1, 0)
    self.adventureSkillsGroupBoxLayout.addWidget(self.findRoomTrapSkillSpinBox, 1, 1)
    self.adventureSkillsGroupBoxLayout.addWidget(_huntingSkillLabel, 2, 0)
    self.adventureSkillsGroupBoxLayout.addWidget(self.huntingSkillSpinBox, 2, 1)
    self.adventureSkillsGroupBoxLayout.addWidget(_listenAtDoorSkillLabel, 3, 0)
    self.adventureSkillsGroupBoxLayout.addWidget(self.listenAtDoorSkillSpinBox, 3, 1)
    self.adventureSkillsGroupBoxLayout.addWidget(_openStuckDoorSkillLabel, 4, 0)
    self.adventureSkillsGroupBoxLayout.addWidget(self.openStuckDoorSkillSpinBox, 4, 1)
    self.adventureSkillsGroupBoxLayout.addWidget(_findSecretDoorSkillLabel, 5, 0)
    self.adventureSkillsGroupBoxLayout.addWidget(self.findSecretDoorSkillSpinBox, 5, 1)

    self.adventureSkillsGroupBoxLayout.setColumnStretch(0, 1)
    self.adventureSkillsGroupBoxLayout.setColumnStretch(1, 1)
    self.adventureSkillsGroupBoxLayout.setColumnStretch(2, 2)

    self.adventureSkillsGroupBox = QGroupBox()
    self.adventureSkillsGroupBox.setTitle('Adventuring Skills')
    self.adventureSkillsGroupBox.setLayout(self.adventureSkillsGroupBoxLayout)

    # Trait scroll area
    _traitGroupBoxLayout = QGridLayout()
    self.traitScrollArea = TraitsScrollArea(mode='view')
    _traitGroupBoxLayout.addWidget(self.traitScrollArea, 0, 0)

    _traitGroupBox = QGroupBox()
    _traitGroupBox.setTitle('Traits')
    _traitGroupBox.setLayout(_traitGroupBoxLayout)

    # Languages group box
    self.languagesGroupBoxLayout = QGridLayout()
    self.languagesGroupBoxLayout.setSpacing(20)
    self.languagesGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.languagesGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.languagesGroupBoxLayout.addWidget(_literacyLabel, 0, 0)
    self.languagesGroupBoxLayout.addWidget(self.literacyLineEdit, 0, 1)
    self.languagesGroupBoxLayout.addWidget(_spokenLanguagesLabel, 0, 2)
    self.languagesGroupBoxLayout.addWidget(self.spokenLanguagesLineEdit, 0, 3)
    self.languagesGroupBoxLayout.addWidget(_languagesLineEditLabel, 1, 0)
    self.languagesGroupBoxLayout.addWidget(self.languagesLineEdit, 1, 1, 1, 3)

    self.languagesGroupBox = QGroupBox()
    self.languagesGroupBox.setTitle('Languages')
    self.languagesGroupBox.setLayout(self.languagesGroupBoxLayout)

    # NPC & Retainers group box

    self.npcGroupBoxLayout = QGridLayout()
    self.npcGroupBoxLayout.setSpacing(20)
    self.npcGroupBoxLayout.setContentsMargins(10, 20, 10, 20)
    self.npcGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    self.npcGroupBoxLayout.addWidget(_npcReactionsModifierLabel, 0, 0)
    self.npcGroupBoxLayout.addWidget(self.npcReactionsModifierSpinBox, 0, 1)
    self.npcGroupBoxLayout.addWidget(_maxNumberOfRetainersLabel, 1, 0)
    self.npcGroupBoxLayout.addWidget(self.maxNumberOfRetainersSpinBox, 1, 1)
    self.npcGroupBoxLayout.addWidget(_retainerLoyaltyLabel, 1, 2)
    self.npcGroupBoxLayout.addWidget(self.retainerLoyaltySpinBox, 1, 3)

    self.npcGroupBox = QGroupBox()
    self.npcGroupBox.setTitle('NPCs and Retainers')
    self.npcGroupBox.setLayout(self.npcGroupBoxLayout)

    ## Buttons

    # Generate Random Character
    self.generateRandomCharacterButton = QPushButton("Generate Random Character")
    self.generateRandomCharacterButton.clicked.connect(self.handleGenerateRandomCharacterButton)

    # Load from database
    self.loadFromDatabaseButton = QPushButton("Load From Database")
    self.loadFromDatabaseButton.clicked.connect(self.handleLoadFromDatabaseButton)

    # Save to database
    self.saveToDatabaseButton = QPushButton("Save To Database")
    self.saveToDatabaseButton.clicked.connect(self.handleSaveToDatabaseButton)

    # Delete from database
    self.deleteFromDatabaseButton = QPushButton("Delete From Database")
    self.deleteFromDatabaseButton.clicked.connect(self.handleDeleteFromDatabaseButton)

    # Export to file
    self.exportToFileButton = QPushButton("Export To File")
    self.exportToFileButton.clicked.connect(self.handleExportToFileButton)

    # Export to character sheet
    self.exportToCharacterSheetPdfButton = QPushButton("Export To Character Sheet")
    self.exportToCharacterSheetPdfButton.clicked.connect(self.handleExportToCharacterSheetPdfButton)

    # Clear
    self.clearButton = QPushButton("Clear")
    self.clearButton.clicked.connect(self.handleClearButton)

    # Buttons helper layout
    _buttonHelperLayout = QHBoxLayout()
    _buttonHelperLayout.addWidget(self.generateRandomCharacterButton)
    _buttonHelperLayout.addWidget(self.loadFromDatabaseButton)
    _buttonHelperLayout.addWidget(self.saveToDatabaseButton)
    _buttonHelperLayout.addWidget(self.deleteFromDatabaseButton)
    _buttonHelperLayout.addWidget(self.exportToFileButton)
    _buttonHelperLayout.addWidget(self.exportToCharacterSheetPdfButton)
    _buttonHelperLayout.addWidget(self.clearButton)
    _buttonHelperLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum))

    # Load character widget
    self.loadCharacterWidget = LoadDialogWidget(dataModelName='CHARACTER')
    self.loadCharacterWidget.setWindowTitle('Load Character From Database')
    self.loadCharacterWidget.characterSelectedForLoad.connect(self.loadCharacterFromDatabase)

    # Move load character widget to center of the main window
    _mainWindow = hp.getMainWindow()
    _pos = _mainWindow.mapToGlobal(self.rect().topLeft())
    _size = _mainWindow.size()
    _x = _pos.x() + (_size.width() - self.loadCharacterWidget.width()) // 2
    _y = _pos.y() + (_size.height() - self.loadCharacterWidget.height()) // 2
    self.loadCharacterWidget.move(QPoint(_x, _y))

    ## Finish setup
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(15)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainGridLayout.setContentsMargins(15, 15, 15, 15)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainGridLayout.addWidget(_headerLabel, 0, 0)
    _mainGridLayout.addWidget(self.generalGroupBox, 1, 0)
    _mainGridLayout.addWidget(self.abilitiesGroupBox, 1, 1)
    _mainGridLayout.addWidget(self.movementGroupBox, 1, 2)
    _mainGridLayout.addWidget(_traitGroupBox, 1, 3, 2, 1)
    _mainGridLayout.addWidget(self.combatGroupBox, 2, 0)
    _mainGridLayout.addWidget(self.saveGroupBox, 2, 1)
    _mainGridLayout.addWidget(self.adventureSkillsGroupBox, 2, 2)
    _mainGridLayout.addWidget(self.languagesGroupBox, 3, 0)
    _mainGridLayout.addWidget(self.npcGroupBox, 3, 1)
    _mainGridLayout.addLayout(_buttonHelperLayout, 4, 0)
    _mainGridLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), 4, 3)
    _mainGridLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 5, 0)

    self.setLayout(_mainGridLayout)
    self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    # Initial UI setup
    self.handleMovementExplorationLineEditTextChanged()
    self.handleStrengthSpinBoxValueChanged()
    self.handleIntelligenceSpinBoxValueChanged()
    self.handleWisdomSpinBoxValueChanged()
    self.handleDexteritySpinBoxValueChanged()
    self.handleConstitutionSpinBoxValueChanged()
    self.handleCharismaSpinBoxValueChanged()

  def applyClassModifiers(self):
    _modifiers = data.getGameSystemData().getClassProperty('ose', self.className, 'character_modifiers')
    if not _modifiers:
      return

    for _modifier in _modifiers:
      _widget = qh.findChildByProperty(self, QWidget, 'name', _modifier['property'])
      if not _widget:
        continue

      if (not '+' in _modifier['value'] and
          not '-' in _modifier['value'] and
          not '*' in _modifier['value']):
        if type(_widget) in (QLineEdit, QPlainTextEdit):
          _widget.setText(_modifier['value'])
        elif type(_widget) == QSpinBox:
          _widget.setValue(int(_modifier['value']))
      else:
        _operator = ''
        _currentValue = 0
        if type(_widget) in (QLineEdit, QPlainTextEdit):
          _currentValue = int(_widget.text())
        elif type(_widget) == QSpinBox:
          _currentValue = _widget.value()

        _value = 0
        if '+' in _modifier['value']:
          _value = int(_modifier['value'].split('+')[1])
          _value = _currentValue + _value
        elif '-' in _modifier['value']:
          _value = int(_modifier['value'].split('-')[1])
          _value = _currentValue - _value
        elif '*' in _modifier['value']:
          _value = int(_modifier['value'].split('*')[1])
          _value = _currentValue * _value

        if type(_widget) in (QLineEdit, QPlainTextEdit):
          _widget.setText(str(_value))
        elif type(_widget) == QSpinBox:
          _widget.setValue(_value)

  def calculateAbilityModifier(self, score : int) -> int:
    _mod = 3
    if score < 4:
      _mod = -3
    elif score < 6:
      _mod = -2
    elif score < 9:
      _mod = -1
    elif score < 13:
      _mod = 0
    elif score < 16:
      _mod = 1
    elif score < 18:
      _mod = 2

    return _mod

  def calculateHpModifier(self) -> int:
    return self.constitutionModSpinBox.value()

  def calculateInitiativeModifier(self) -> int:
    _dexterityScore = self.dexteritySpinBox.value()

    _initiativeModifier = 0
    if _dexterityScore < 4:
      _initiativeModifier = -2
    elif _dexterityScore < 9:
      _initiativeModifier = -1
    elif _dexterityScore < 13:
      _initiativeModifier = 0
    elif _dexterityScore < 18:
      _initiativeModifier = 1
    else:
      _initiativeModifier = 2

    return _initiativeModifier

  def calculateOpenStuckDoorChance(self) -> int:
    _strengthScore = self.strengthSpinBox.value()
    _chance = 0
    if _strengthScore < 9:
      _chance = 1
    elif _strengthScore < 13:
      _chance = 2
    elif _strengthScore < 16:
      _chance = 3
    elif _strengthScore < 18:
      _chance = 4
    else:
      _chance = 5

    return _chance

  def calculateUnarmoredAc(self):
    return 9 - self.calculateAbilityModifier(self.dexteritySpinBox.value())

  def calculateWisdomMagicSavesModifier(self) -> int:
    return self.wisdomModSpinBox.value()

  def calculateXpBonus(self):
    _xpBonus = data.getGameSystemData().getClassProperty('ose', self.className, 'prime_requisite_xp_bonus')
    if not _xpBonus:
      return

    _minorBonusRequirement = False
    _majorBonusRequirement = False

    _finalResults = []

    for _bonusLevel in _xpBonus.values():
      _fulfilledCurrent = False
      _abilityScores = {}

      for _key in _bonusLevel.keys():
        if _key == 'condition':
          continue

        _abilityScore = 0
        match _key.lower():
          case 'str':
            _abilityScore = self.strengthSpinBox.value()
          case 'int':
            _abilityScore = self.intelligenceSpinBox.value()
          case 'wis':
            _abilityScore = self.wisdomSpinBox.value()
          case 'dex':
            _abilityScore = self.dexteritySpinBox.value()
          case 'con':
            _abilityScore = self.constitutionSpinBox.value()
          case 'cha':
            _abilityScore = self.charismaSpinBox.value()
          case _:
            continue

        _abilityScores[_key] = _abilityScore

      _fulfilledTotal = False
      _lastValue = None
      _currentValue = None
      _fulfilledCurrent = False
      for _score in _abilityScores.keys():
        _currentValue = _abilityScores[_score]
        # First xp bonus requirement
        if _lastValue is None:
          if _currentValue >= _bonusLevel[_score]:
            _fulfilledTotal = True
          _lastValue = _currentValue
          continue
        else:
          # Further xp bonus requirement
          if _currentValue >= _bonusLevel[_score]:
            _fulfilledCurrent = True

        _condition = _bonusLevel.get('condition', None)

        if _condition == 'and':
          _fulfilledTotal =  _fulfilledCurrent and _fulfilledTotal
        elif _condition == 'or':
          _fulfilledTotal =  _fulfilledCurrent or _fulfilledTotal

        _lastValue = _currentValue

      _finalResults.append(_fulfilledTotal)

    _xpBonusValues = list(_xpBonus.keys())
    _finalBonus = ''
    for i in range(len(_finalResults)):
      if _finalResults[i]:
        _finalBonus = _xpBonusValues[i]

    self.xpBonusLineEdit.setText(_finalBonus)

  def getRaceFromClass(self) -> str | None:
    if not self.className:
      return None

    if self.className in ('Elf', 'Dwarf', 'Halfling'):
      return self.className

    return 'Human'

  def getValueFromWidget(self, widget) -> int | str | None:
    if type(widget) in (QLineEdit, QPlainTextEdit):
      return widget.text()
    elif type(widget) == QSpinBox:
      return widget.value()
    elif type(widget) == QComboBox:
      return widget.currentText()

    return None


  def handleCharismaSpinBoxValueChanged(self):
    _charismaScore = self.charismaSpinBox.value()

    _npcReactionsModifier = 0
    if _charismaScore < 4:
      _npcReactionsModifier = -2
    elif _charismaScore < 9:
      _npcReactionsModifier = -1
    elif _charismaScore < 13:
      _npcReactionsModifier = 0
    elif _charismaScore < 18:
      _npcReactionsModifier = 1
    else:
      _npcReactionsModifier = 2

    self.npcReactionsModifierSpinBox.setValue(_npcReactionsModifier)

    _maxNumberOfRetainers = 0
    _retainerLoyalty = 0
    if _charismaScore < 4:
      _maxNumberOfRetainers = 1
      _retainerLoyalty = 4
    elif _charismaScore < 6:
      _maxNumberOfRetainers = 2
      _retainerLoyalty = 5
    elif _charismaScore < 9:
      _maxNumberOfRetainers = 3
      _retainerLoyalty = 6
    elif _charismaScore < 13:
      _maxNumberOfRetainers = 4
      _retainerLoyalty = 7
    elif _charismaScore < 16:
      _maxNumberOfRetainers = 5
      _retainerLoyalty = 8
    elif _charismaScore < 18:
      _maxNumberOfRetainers = 6
      _retainerLoyalty = 9
    else:
      _maxNumberOfRetainers = 7
      _retainerLoyalty = 10

    self.maxNumberOfRetainersSpinBox.setValue(_maxNumberOfRetainers)
    self.retainerLoyaltySpinBox.setValue(_retainerLoyalty)

  def handleClassComboBoxChanged(self):
    # Gather class data
    if not self.classComboBox.currentText():
      return

    self.className = self.classComboBox.currentText()

    _classData = data.getGameSystemData().getClass(gameSystem='ose', className=self.className)

    if _classData is None and self.classComboBox.currentIndex() != -1:
      logging.error(f'No data found for class "{self.classComboBox.currentText()}" for game system ose')
      self.className = None
      return

    self.classData = _classData

    self.traitScrollArea.addTraitsFromJson(self.classData['traits'])
    self.updateUiWithClassData()

  def handleClearButton(self):
    self.classComboBox.setCurrentIndex(-1)
    self.nameLineEdit.clear()
    self.xpLineEdit.clear()
    self.xpBonusLineEdit.setText('None')
    self.startingWealthSpinBox.setValue(self.startingWealthSpinBox.minimum())
    self.languagesLineEdit.clear()
    self.titleLineEdit.clear()
    self.alignmentComboBox.setCurrentIndex(0)
    self.heightLineEdit.clear()
    self.weightLineEdit.clear()

    self.resetAbilityScores()

    self.hdSpinBox.setValue(self.hdSpinBox.minimum())
    self.hpLineEdit.setText('')
    self.thac0SpinBox.setValue(19)
    self.acSpinBox.setValue(9)

    self.savePoisonDeathSpinBox.setValue(self.savePoisonDeathSpinBox.maximum())
    self.saveMagicWandsSpinBox.setValue(self.saveMagicWandsSpinBox.maximum())
    self.saveParalysisPetrificationSpinBox.setValue(self.saveParalysisPetrificationSpinBox.maximum())
    self.saveBreathAttacksSpinBox.setValue(self.saveBreathAttacksSpinBox.maximum())
    self.saveSpellsRodsStavesSpinBox.setValue(self.saveSpellsRodsStavesSpinBox.maximum())

    self.foragingSkillSpinBox.setValue(self.foragingSkillSpinBox.minimum())
    self.findRoomTrapSkillSpinBox.setValue(self.findRoomTrapSkillSpinBox.minimum())
    self.huntingSkillSpinBox.setValue(self.huntingSkillSpinBox.minimum())
    self.listenAtDoorSkillSpinBox.setValue(self.listenAtDoorSkillSpinBox.minimum())
    self.openStuckDoorSkillSpinBox.setValue(self.openStuckDoorSkillSpinBox.minimum())
    self.findSecretDoorSkillSpinBox.setValue(self.findSecretDoorSkillSpinBox.minimum())

    self.initiativeBonusSpinBox.setValue(0)
    self.hdSpinBoxLabel.setText('HD:')

  def handleConstitutionSpinBoxValueChanged(self):
    _constitutionScore = self.constitutionSpinBox.value()
    self.constitutionModSpinBox.setValue(self.calculateAbilityModifier(_constitutionScore))

  def handleDeleteFromDatabaseButton(self):
    _characterId = dm.getDataModels().getDataForModelIndex(modelName='CHARACTER', columnName='ID', filterColumns=('Name',), filterValues=(self.nameLineEdit.text(),))
    if not _characterId:
      logging.warning(f'The character "{self.nameLineEdit.text()}" cannot be found in the database.')
      return

    _dialog = hp.OkCancelDialog(
      title=f'Delete Character',
      text=f'Do you really want to delete the character "{self.nameLineEdit.text()}"?')

    _deleteCharacter = _dialog.exec()
    if not _deleteCharacter:
      return
    else:
      db.beginTransaction()
      # Delete character property data
      _sqlRc = db.delete('delete from CHARACTER_X_CHARACTER_PROPERTY where CHARACTER = ?', (_characterId,))
      # Delete character data
      _sqlRc = max(db.delete('delete from CHARACTER where ID = ?', (_characterId,)), _sqlRc)

      if _sqlRc != 0:
        logging.error(f'Character "{self.nameLineEdit.text()}" could not be deleted from the database.')
        db.rollbackChanges()

      db.endTransaction()

      if _sqlRc == 0:
        logging.info(f'Character "{self.nameLineEdit.text()}" was successfully deleted from the database.')
        dm.getDataModels().model('CHARACTER').select()
        dm.getDataModels().model('CHARACTER_X_CHARACTER_PROPERTY').select()

  def handleDexterityModSpinBoxValueChanged(self):
    self.updateAC()
    self.missileBonusSpinBox.setValue(self.dexterityModSpinBox.value())

  def handleDexteritySpinBoxValueChanged(self):
    _dexScore = self.dexteritySpinBox.value()
    self.dexterityModSpinBox.setValue(self.calculateAbilityModifier(_dexScore))
    self.initiativeBonusSpinBox.setValue(self.calculateInitiativeModifier())

  def handleExportToCharacterSheetPdfButton(self):
    _fileNames = hp.makeFileDialog(acceptedFileExtensions='pdf files (*.pdf)', multipleFiles=False, acceptMode=QFileDialog.AcceptMode.AcceptSave)
    if not _fileNames:
      logging.error('No file selected for export')
      return

    _filePath = pathlib.Path(_fileNames[0])
    _extLower = _filePath.suffix.replace('.', '').lower()
    if _extLower != 'pdf':
      logging.error(f'Invalid file extension "{_extLower}" selected for export')
      return

    _characterData = self.serializeCharacterToDict()

    _levelProgression = self.classData.get('level_progression').get('rows')
    _levelNormalized = self.levelSpinBox.value() - 1
    _thac0 = int(_levelProgression[_levelNormalized]['thac0'].split(' ')[0])





    _characterDataToPdfMapping = {
      # General
      'Name': _characterData['name'],
      'Title': '',
      'Race': _characterData['race'],
      'Level': _characterData['level'],
      'Class': _characterData['class'],
      'Alignment': _characterData['alignment'],

      # Ability Scores
      'STR': _characterData['strength_score'],
      'INT': _characterData['intelligence_score'],
      'WIS': _characterData['wisdom_score'],
      'DEX': _characterData['dexterity_score'],
      'CON': _characterData['constitution_score'],
      'CHA': _characterData['charisma_score'],

      # Saving Throws
      'Death Save': _characterData['save_d'],
      'Wands Save': _characterData['save_w'],
      'Paralysis Save': _characterData['save_p'],
      'Breath Save': _characterData['save_b'],
      'Spells Save': _characterData['save_s'],
      'Magic Save Mod': self.calculateAbilityModifier(_characterData['wisdom_score']),

      # Combat
      'HP': _characterData['hit_points'],
      'Max HP': _characterData['hit_points'],
      'CON HP Mod': self.calculateAbilityModifier(_characterData['constitution_score']),

      'AC': _characterData['ac'],
      'Unarmoured AC': self.calculateUnarmoredAc(),
      'DEX AC Mod': self.calculateAbilityModifier(_characterData['dexterity_score']),

      # Attack Rolls
      'STR Melee Mod': self.calculateAbilityModifier(_characterData['strength_score']),
      'DEX Missile Mod': self.calculateAbilityModifier(_characterData['dexterity_score']),
      'Attack Bonus': '',
      'THAC0': _thac0,
      'THAC1': _thac0 - 1,
      'THAC2': _thac0 - 2,
      'THAC3': _thac0 - 3,
      'THAC4': _thac0 - 4,
      'THAC5': _thac0 - 5,
      'THAC6': _thac0 - 6,
      'THAC7': _thac0 - 7,
      'THAC8': _thac0 - 8,
      'THAC9': _thac0 - 9,

      # Encounters
      'Reactions CHA Mod': self.npcReactionsModifierSpinBox.value(),
      'Initiative DEX Mod': '',

      # Movement
      'Overland Movement': _characterData['movement_overland'],
      'Exporation Movement': _characterData['movement_overland'],
      'Encounter Movement': _characterData['movement_overland'],

      # Adventuring Skills
      'Forage': _characterData['skill_forage'],
      'Find Room Trap': _characterData['skill_find_room_trap'],
      'Hunt': _characterData['skill_hunt'],
      'Listen at Door': _characterData['skill_listen_door'],
      'Open Stuck Door': _characterData['skill_open_stuck_door'],
      'Find Secret Door': _characterData['skill_find_secret_door'],

      # Abilities, Skills, Weapons
      'Abilities, Skills, Weapons': '',
      # Languages
      'Languages': _characterData['languages'],
      'Literacy': '/Yes',
      # Equipment
      'Equipment': '',
      # Weapons and Armour
      'Weapons and Armour': '',
      # Magic Items
      'Magic Items': '',
      # Treasure
      'Treasure': '',
      # Other Notes
      'Notes': '',

      # Coins
      'PP': '',
      'GP': _characterData['starting_wealth'],
      'EP': '',
      'SP': '',
      'CP': '',

      # XP
      'XP': _characterData['xp'],
      'XP for Next Level': _levelProgression[_levelNormalized + 1]['xp'],
      'PR XP Bonus': self.xpBonusLineEdit.text(),
      
      # Encumbrance
      'Treasure Encumbrance': '',
      'Equipment Encumbrance': '',
      'Total Encumbrance': ''
    }



    _pdfReader = PdfReader(apc.ROOT_INPUT_PATH / 'rules' / 'ose' / 'character_sheet.pdf')
    _fields = _pdfReader.get_fields()

    _pdfWriter = PdfWriter()
    _pdfWriter.append(_pdfReader)

    for _key in _characterDataToPdfMapping:
      _pageNumber = _pdfReader.get_pages_showing_field(_fields[_key])[0].page_number
      _pdfWriter.update_page_form_field_values(_pdfWriter.pages[_pageNumber], {f'{_key}': _characterDataToPdfMapping[_key]}, auto_regenerate=False) #, flatten=True)
      #_pdfWriter.remove_annotations(subtypes='/Widget')

    _pdfWriter.write(_filePath)

  def handleExportToFileButton(self):
    _fileDialogNameFilter = [
      "All Supported Files (*.yaml *.yml *.json *.csv)",
      "yaml files (*.yaml *.yml)",
      "json files (*.json)",
      "csv files (*.csv)",
      "All files (*)"
    ]
    _fileNames = hp.makeFileDialog(acceptedFileExtensions=_fileDialogNameFilter, multipleFiles=False, acceptMode=QFileDialog.AcceptMode.AcceptSave)
    if not _fileNames:
      logging.error('No file selected for export')
      return

    _filePath = pathlib.Path(_fileNames[0])
    _extLower = _filePath.suffix.replace('.', '').lower()
    _characterData = self.serializeCharacterToDict()

    if not _characterData:
      logging.error('Character data could not be exported!')
      return

    if _extLower == 'csv':
      hp.writeDictToCsv(_characterData, _filePath, ';')
    elif _extLower == 'json':
      hp.writeDictToJson(_characterData, _filePath)
    elif _extLower == 'yaml':
      hp.writeDictToYaml(_characterData, _filePath)
    else:
      logging.error(f'Unsupported file extension "{_extLower}" for export')


  def handleGenerateAllAbilityScoresButton(self):
    self.handleRollAbilityScoreButtonClicked('STR')
    self.handleRollAbilityScoreButtonClicked('INT')
    self.handleRollAbilityScoreButtonClicked('WIS')
    self.handleRollAbilityScoreButtonClicked('DEX')
    self.handleRollAbilityScoreButtonClicked('CON')
    self.handleRollAbilityScoreButtonClicked('CHA')

  def handleGenerateRandomCharacterButton(self):
    # Name
    if not self.className:
      _classes = [_c.get('name', None) for _c in data.getGameSystemData().getAllClassesForGameSystem('ose').values()]
      self.className = choice(_classes)
      self.classComboBox.setCurrentText(self.className)
      logging.info(f'Rolled class "{self.className}"')

    _race = self.getRaceFromClass()
    logging.info(f'Determined race "{_race}"')

    _raceId = dm.getDataModels().getDataForModelIndex(modelName='RACE', columnName='ID', filterColumns=('NAME',), filterValues=(_race,))
    _firstNames = dm.getDataModels().getDataForModelColumn(modelName='CREATURE_NAME', columnName='FIRST_NAME', filterColumn='RACE', filterValue=_raceId)
    _lastNames = dm.getDataModels().getDataForModelColumn(modelName='CREATURE_NAME', columnName='LAST_NAME', filterColumn='RACE', filterValue=_raceId)

    _fullNames = []
    for i in range(len(_firstNames)):
      _fullNames.append(f'{_firstNames[i]} {_lastNames[i]}')

    _name = choice(_fullNames) if len(_fullNames) > 0 else choice(['John Doe', 'Jane Doe'])

    self.nameLineEdit.setText(_name)
    logging.info(f'Rolled name "{_name}"')

    # Age
    _ageScore = hp.rollDice(3, 20)
    self.ageSpinBox.setValue(_ageScore)

    # Ability Scores
    _reRollThreshold = 5
    _strengthScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=_reRollThreshold)
    self.strengthSpinBox.setValue(_strengthScore)
    logging.info(f'Rolled {_strengthScore} for Strength')
    _intelligenceScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=_reRollThreshold)
    self.intelligenceSpinBox.setValue(_intelligenceScore)
    logging.info(f'Rolled {_intelligenceScore} for Intelligence')
    _wisdomScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=_reRollThreshold)
    self.wisdomSpinBox.setValue(_wisdomScore)
    logging.info(f'Rolled {_wisdomScore} for Wisdom')
    _dexterityScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=_reRollThreshold)
    self.dexteritySpinBox.setValue(_dexterityScore)
    logging.info(f'Rolled {_dexterityScore} for Dexterity')
    _constitutionScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=_reRollThreshold)
    self.constitutionSpinBox.setValue(_constitutionScore)
    logging.info(f'Rolled {_constitutionScore} for Constitution')
    _charismaScore = hp.rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=_reRollThreshold)
    self.charismaSpinBox.setValue(_charismaScore)
    logging.info(f'Rolled {_charismaScore} for Charisma')

    # Ability Score modifiers
    _mod = self.calculateAbilityModifier(_strengthScore)
    self.strengthModSpinBox.setValue(_mod)
    logging.info(f'Determined {_mod} for Strength modifier')

    _mod = self.calculateAbilityModifier(_wisdomScore)
    self.wisdomModSpinBox.setValue(_mod)
    logging.info(f'Determined {_mod} for Wisdom modifier')

    _mod = self.calculateAbilityModifier(_constitutionScore)
    self.constitutionModSpinBox.setValue(_mod)
    logging.info(f'Determined {_mod} for Constitution modifier')

    _mod = self.calculateAbilityModifier(_dexterityScore)
    self.dexterityModSpinBox.setValue(_mod)
    logging.info(f'Determined {_mod} for Dexterity modifier')

    # HP
    self.handleRollHpButtonClicked()

    # AC
    self.updateAC()
    logging.info(f'Determined AC of {self.acSpinBox.value()}')
    logging.info(f'Determined AC bonus of {self.acBonusLabel.text()}')

    # Weight
    self.handleRollCharacterWeightButton()
    logging.info(f'Rolled weight of {self.weightLineEdit.text()} lbs')

    # Height
    self.handleRollCharacterHeightButton()
    logging.info(f'Rolled height of {self.heightLineEdit.text()}')

    # Starting wealth
    self.handleRollStartingWealthButton()
    logging.info(f'Rolled starting wealth of {self.startingWealthSpinBox.value()} gp')

    # Languages
    self.languagesLineEdit.setText(self.classData.get('languages', ''))
    logging.info(f'Determined languages "{self.languagesLineEdit.text()}"')

    # Apply class modifiers
    self.applyClassModifiers()

    # XP bonus
    self.calculateXpBonus()
    logging.info(f'Determined XP bonus of {self.xpBonusLineEdit.text()}')

  def handleHdSpinBoxValueChanged(self):
    if not self.classData:
      return

  def handleIntelligenceSpinBoxValueChanged(self):
    _intelligenceScore = self.intelligenceSpinBox.value()

    # ToDo: Move to database
    _numberOfLanguagesSpoken = ''
    if _intelligenceScore < 4:
      _numberOfLanguagesSpoken = 'Native (broken speech)'
    elif _intelligenceScore < 13:
      _numberOfLanguagesSpoken = 'Native'
    elif _intelligenceScore < 16:
      _numberOfLanguagesSpoken = 'Native + 1 additional'
    elif _intelligenceScore < 18:
      _numberOfLanguagesSpoken = 'Native + 2 additional'
    else:
      _numberOfLanguagesSpoken = 'Native + 3 additional'
    self.spokenLanguagesLineEdit.setText(_numberOfLanguagesSpoken)

    _literacy = ''
    if _intelligenceScore < 6:
      _literacy = 'Illiterate'
    elif _intelligenceScore < 9:
      _literacy = 'Basic'
    else:
      _literacy = 'Literate'
    self.literacyLineEdit.setText(_literacy)

  def handleLevelSpinBoxChanged(self):
    self.updateUiWithClassData()

  def handleLoadFromDatabaseButton(self):
    self.loadCharacterWidget.show()
    self.loadCharacterWidget.raise_()
    self.loadCharacterWidget.activateWindow()

  # Updates movement fields
  def handleMovementExplorationLineEditTextChanged(self):
    if not self.movementExplorationLineEdit.text():
      self.movementOverlandLabel.setText('')
      self.movementEncounterLabel.setText('')
      return

    if not hp.isStringAnInteger(self.movementExplorationLineEdit.text()):
      self.movementOverlandLabel.setText('')
      self.movementEncounterLabel.setText('')
      logging.error(f'Values for movement must be integers!')
      return

    _exploration = int(self.movementExplorationLineEdit.text())
    _overland = math.floor(_exploration * 0.2) if _exploration >= 5 else 1
    _encounter = math.floor(_exploration / 3)  if _exploration >= 3 else 1

    self.movementOverlandLabel.setText(f'{_overland}')
    self.movementEncounterLabel.setText(f'{_encounter}')

  def handleResetAbilityScoresButton(self):
    self.resetAbilityScores()

  def handleRollAbilityScoreButtonClicked(self, scoreName : str):
    _score = hp.rollAbilityScore(mode='3d6DownTheLine')
    match scoreName:
      case 'STR':
        self.strengthSpinBox.setValue(_score)
        logging.info(f'Rolled {_score} for Strength')
      case 'INT':
        self.intelligenceSpinBox.setValue(_score)
        logging.info(f'Rolled {_score} for Intelligence')
      case 'WIS':
        self.wisdomSpinBox.setValue(_score)
        logging.info(f'Rolled {_score} for Wisdom')
      case 'DEX':
        self.dexteritySpinBox.setValue(_score)
        logging.info(f'Rolled {_score} for Dexterity')
      case 'CON':
        self.constitutionSpinBox.setValue(_score)
        logging.info(f'Rolled {_score} for Constitution')
      case 'CHA':
        self.charismaSpinBox.setValue(_score)
        logging.info(f'Rolled {_score} for Charisma')
      case _:
        pass

  def handleRollCharacterAgeButton(self):
    if not self.className or not self.getRaceFromClass():
      logging.error('Rolling for a character\'s age requires a class to be selected! Any class except "Dwarf", "Elf" and "Halfling" are considered to be human when generating character age.')
      return

    _race = self.getRaceFromClass()

    _ageMin = dm.getDataModels().getDataForModelIndex(modelName='RACE', columnName='AGE_MIN', filterColumns=('NAME',), filterValues=(_race,))
    _ageMax = dm.getDataModels().getDataForModelIndex(modelName='RACE', columnName='AGE_MAX', filterColumns=('NAME',), filterValues=(_race,))

    _age = choice(range(_ageMin, _ageMax + 1))
    self.ageSpinBox.setValue(_age)

  def handleRollCharacterNameButton(self) -> str | None:
    if not self.className or not self.getRaceFromClass():
      logging.error('Rolling for a character\'s name requires a class to be selected! Any class except "Dwarf", "Elf" and "Halfling" are considered to be human when generating a character name.')
      return

    _firstNames = dm.getDataModels().getDataForModelColumn(modelName='CREATURE_NAME', columnName='FIRST_NAME', filterColumn='NAME', filterValue=self.getRaceFromClass())
    _lastNames = dm.getDataModels().getDataForModelColumn(modelName='CREATURE_NAME', columnName='LAST_NAME', filterColumn='NAME', filterValue=self.getRaceFromClass())

    _firstName = choice(_firstNames) if len(_firstNames) > 0 else 'John'
    _lastName = choice(_lastNames) if len(_lastNames) > 0 else 'Doe'

    self.nameLineEdit.setText(f'{_firstName} {_lastName}')

  def handleRollCharacterHeightButton(self):
    if not self.className or not self.getRaceFromClass():
      logging.error('Rolling for a character\'s height requires a class to be selected! Any class except "Dwarf", "Elf" and "Halfling" are considered to be human when generating character height.')
      return

    _race = self.getRaceFromClass()

    # Stored in kilogram
    _heightMin = dm.getDataModels().getDataForModelIndex(modelName='RACE', columnName='HEIGHT_MIN', filterColumns=('NAME',), filterValues=(_race,))
    _heightMax = dm.getDataModels().getDataForModelIndex(modelName='RACE', columnName='HEIGHT_MAX', filterColumns=('NAME',), filterValues=(_race,))

    _height = choice(range(_heightMin, _heightMax + 1))

    # Convert to feet and inches
    _feet = int(_height // 30.48)
    _remainder = _height % 30.48
    _inches = int(_remainder // 2.5)

    self.heightLineEdit.setText(f'{_feet}\' {_inches}\"')

  def handleRollCharacterWeightButton(self):
    if not self.className or not self.getRaceFromClass():
      logging.error('Rolling for a character\'s weight requires a class to be selected! Any class except "Dwarf", "Elf" and "Halfling" are considered to be human when generating character weight.')
      return

    _race = self.getRaceFromClass()

    # Stored in centimeter
    _weightMin = dm.getDataModels().getDataForModelIndex(modelName='RACE', columnName='WEIGHT_MIN', filterColumns=('NAME',), filterValues=(_race,))
    _weightMax = dm.getDataModels().getDataForModelIndex(modelName='RACE', columnName='WEIGHT_MAX', filterColumns=('NAME',), filterValues=(_race,))

    _weight = choice(range(_weightMin, _weightMax + 1))

    # Convert into lbs
    _kgToLbsFactor = 2.2
    _weight = math.floor(_weight * _kgToLbsFactor)

    self.weightLineEdit.setText(f'{_weight}')

  def handleRollHpButtonClicked(self):
    if not self.className:
      logging.error('Rolling HP requires a class to be selected!')
      return

    #ToDo: Make dynamic when other game systems are implemented
    _oseGameSystemId = 1

    #ToDo: Move out of here to a more central place, maybe write subroutines?
    ## Determine the difference in hp bonus per level above level 9
    _hdProgression = [_r['hd'] for _r in self.classData.get('level_progression').get('rows')]

    # Extract the bonus from the first two levels above level 9 and calculate the difference
    _hpBonusDifference = 0
    if len(_hdProgression) == 10:
      _hpBonusDifference = int(_hdProgression[9].replace('*', '').split('+')[1])
    if len(_hdProgression) > 10:
      _level10HpBonus = int(_hdProgression[9].replace('*', '').split('+')[1])
      _level11HpBonus = int(_hdProgression[10].replace('*', '').split('+')[1])
      _hpBonusDifference = _level11HpBonus - _level10HpBonus

    _numHitDice = self.hdSpinBox.value()
    _hitDice = int(self.classData['hit_dice'].split('d')[1])
    _constitutionHpModifier = self.calculateHpModifier()

    # Roll config
    _enableReRollOn1sAnd2s = True
    _enableAverageOnLowerThanAverage = False
    _hitDieAverage = sum(range(1, _hitDice + 1)) / _hitDice

    _sum = 0
    for i in range(_numHitDice):
      _hp = hp.rollDice(1, _hitDice) if i <= 8 else _hpBonusDifference

      while _hp < _hitDieAverage and _enableReRollOn1sAnd2s:
        if i <= 8:
          _hp = hp.rollDice(1, _hitDice)
        else:
          _hp = _hpBonusDifference
          break

      _hp = max(_hp, math.ceil(_hitDieAverage)) if _enableAverageOnLowerThanAverage else _hp

      _preText = 'Rolled' if i <= 8 else 'Added'
      logging.info(f'{_preText} {_hp} hp for level {i + 1}. Applied {_constitutionHpModifier} from Constitution.')

      _hp += _constitutionHpModifier
      _sum += _hp

    self.hpLineEdit.setText(str(_sum))

    logging.info(f'Rolled {_sum} hit points in total.')

  def handleRollLevelButton(self):
    if not self.className:
      logging.error('Rolling a character\'s level requires a class to be selected!')
      return

    _maxLevel = data.getGameSystemData().getClassProperty('ose', self.className, 'maximum_level')
    if not _maxLevel:
      _maxLevel = 100

    self.levelSpinBox.setValue(choice(range(1, _maxLevel + 1)))

  def handleRollStartingWealthButton(self):
    _startingWealth = hp.rollDice(3, 6) * 10
    self.startingWealthSpinBox.setValue(_startingWealth)

  def handleSaveToDatabaseButton(self):
    # ToDo: Make dynamic when other game systems are implemented

    _characterName = self.nameLineEdit.text()
    if not _characterName:
      logging.error('Character name is required in order to save to the database!')
      return

    # Check if character already exists
    _characterId = dm.getDataModels().getDataForModelIndex(modelName='CHARACTER', columnName='ID', filterColumns=('NAME',), filterValues=(_characterName,))

    db.beginTransaction()
    _sqlRc = 0
    if _characterId:
      _dialog = hp.OkCancelDialog(
        title=f'Character Already Exists!',
        text=f'The character "{_characterName}" already exists!\nDo you want to overwrite it?')

      _overwriteCharacter = _dialog.exec()
      if not _overwriteCharacter:
        logging.info(f'Character {_characterName} has not been saved.')
        return
      else:
        # Delete character property data
        _sqlRc = db.delete('delete from CHARACTER_X_CHARACTER_PROPERTY where CHARACTER = ?', (_characterId,))
        # Delete character data
        _sqlRc = max(db.delete('delete from CHARACTER where ID = ?', (_characterId,)), _sqlRc)

    # Retrieve character properties
    _characterProperties = [_k for _k in data.getGameSystemData().getCharacterDefinition().keys()]

    # Collect general data from UI
    _characterAge = self.ageSpinBox.value()
    _characterHeight = hp.coalesce(self.heightLineEdit.text())
    _characterWeight = int(hp.coalesce(self.weightLineEdit.text())) if hp.coalesce(self.weightLineEdit.text()) else None

    # Collect character property data from UI
    _characterData = {}
    for _property in _characterProperties:
      _widget = qh.findChildByProperty(self, QWidget, 'name', _property)
      if _widget:
        if type(_widget) == QLineEdit:
          _characterData[_property] = _widget.text()
        elif type(_widget) == QSpinBox:
          _characterData[_property] = _widget.value()
        elif type(_widget) == QComboBox:
          _characterData[_property] = _widget.currentText()

    # Adjust some values
    _characterData['sex'] = _characterData['sex'][:1]

    # Insert general character data
    _columns = 'GAME_SYSTEM, NAME, SEX, AGE, HEIGHT, WEIGHT'
    _args = ('ose', _characterData['name'], _characterData['sex'], int(_characterData['age']), _characterData['height'], int(_characterData['weight']))
    _sqlRc = max(db.insert(f'insert into CHARACTER({_columns}) values(?, ?, ?, ?, ?, ?)', _args), _sqlRc)
    _newCharacterId = -1
    if _sqlRc == 0:
      # Refresh model to retrieve new character id
      dm.getDataModels().model('CHARACTER').select()
      _newCharacterId = dm.getDataModels().getDataForModelIndex(modelName='CHARACTER', columnName='ID', filterColumns=('NAME',), filterValues=(_characterName,))

    # Insert game system-specific data
    _columns = 'CHARACTER, PROPERTY, VALUE'
    for _entry in _characterData.keys():
      if _entry in ('name', 'sex', 'age', 'height', 'weight'):
        continue
      _value = _characterData[_entry]
      _args = (_newCharacterId, _entry, _value)
      _sqlRc = max(db.insert(f'insert into CHARACTER_X_CHARACTER_PROPERTY({_columns}) values(?, ?, ?)', _args), _sqlRc)

      if _sqlRc != 0:
        break

    if _sqlRc == 0:
      db.endTransaction()
      dm.getDataModels().model('CHARACTER').select()
      dm.getDataModels().model('CHARACTER_X_CHARACTER_PROPERTY').select()
      logging.info(f'Character "{_characterName}" was successfully saved to database.')
    else:
      db.rollbackChanges()

  def handleStrengthModSpinBoxValueChanged(self):
    self.meleeBonusSpinBox.setValue(self.strengthModSpinBox.value())

  def handleStrengthSpinBoxValueChanged(self):
    _strengthScore = self.strengthSpinBox.value()
    self.strengthModSpinBox.setValue(self.calculateAbilityModifier(_strengthScore))
    self.openStuckDoorSkillSpinBox.setValue(self.calculateOpenStuckDoorChance())

  def handleWisdomSpinBoxValueChanged(self):
    _wisdomScore = self.wisdomSpinBox.value()
    self.wisdomModSpinBox.setValue(self.calculateAbilityModifier(_wisdomScore))
    self.wisdomModifierToSaveVsMagicSpinBox.setValue(self.calculateWisdomMagicSavesModifier())

  def loadCharacterFromDatabase(self, characterId : int):
    # ToDo: make dynamic when other game systems are implemented
    _generalCharacterData = dm.getDataModels().getDataForModelColumns(modelName='CHARACTER', columns = ['NAME', 'AGE', 'SEX', 'HEIGHT', 'WEIGHT'], filterColumn='ID', filterValue=characterId)
    _systemSpecificCharacterData = dm.getDataModels().getDataForModelColumns(modelName='CHARACTER_X_CHARACTER_PROPERTY', columns = ['PROPERTY', 'VALUE'], filterColumn='CHARACTER', filterValue=characterId)

    for _key in _generalCharacterData.keys():
      _widget = qh.findChildByProperty(self, QWidget, 'name', _key.lower())
      if _widget:
        if type(_widget) == QLineEdit:
          _widget.setText(str(_generalCharacterData[_key]))
        elif type(_widget) == QSpinBox:
          _widget.setValue(int(_generalCharacterData[_key]) if _generalCharacterData[_key] else 0)
        elif type(_widget) == QComboBox:
          _widget.setCurrentText(_generalCharacterData[_key])

    for _entry in _systemSpecificCharacterData:
      _widget = qh.findChildByProperty(self, QWidget, 'name', _entry['PROPERTY'].lower())
      if _widget:
        if type(_widget) == QLineEdit:
          _widget.setText(str(_entry['VALUE']))
        elif type(_widget) == QSpinBox:
          _widget.setValue(int(_entry['VALUE']) if _entry['VALUE'] else 0)
        elif type(_widget) == QComboBox:
          _widget.setCurrentText(_entry['VALUE'])


  def makeRollToolButtonForProperty(self, toolTip : str, targetFunction : Callable) -> QToolButton:
    _button = QToolButton()
    _button.setFont(apc.Icons.font())
    _button.setText(apc.Icons.text('dice'))
    _button.setToolTip(toolTip)
    _button.clicked.connect(targetFunction)

    return _button

  def makeSpinBox(self, name: str, minValue : int | None = None, maxValue : int | None = None, currentValue : int | None = None, targetFunction : Callable = None) -> QSpinBox:
    _spinBox= QSpinBox()
    _spinBox.setProperty('name', name)

    if minValue:
      _spinBox.setMinimum(minValue)
    if maxValue:
      _spinBox.setMaximum(maxValue)
    if currentValue:
      _spinBox.setValue(currentValue)
    if targetFunction:
      _spinBox.valueChanged.connect(targetFunction)

    return _spinBox

  def resetAbilityScores(self):
    _defaultScore = 10
    self.strengthSpinBox.setValue(_defaultScore)
    self.intelligenceSpinBox.setValue(_defaultScore)
    self.wisdomSpinBox.setValue(_defaultScore)
    self.dexteritySpinBox.setValue(_defaultScore)
    self.constitutionSpinBox.setValue(_defaultScore)
    self.charismaSpinBox.setValue(_defaultScore)

  def serializeCharacterToDict(self):
    _characterDefinition = data.getGameSystemData().getCharacterDefinition()
    # Audit character definition vs. UI
    for _key in _characterDefinition.keys():
      _widget = qh.findChildByProperty(self, QWidget, 'name', _key)

      if not _widget:
        logging.error(f'No widget found for property {_key}')
        continue

    _characterDefinition['name'] = hp.coalesce(self.nameLineEdit.text(), '')
    _characterDefinition['class'] = hp.coalesce(self.className, '')
    _characterDefinition['race'] = hp.coalesce(self.getRaceFromClass(), '')
    _characterDefinition['sex'] = hp.coalesce(self.sexComboBox.currentText(), '')
    _characterDefinition['age'] = hp.coalesce(self.ageSpinBox.value(), '')
    _characterDefinition['height'] = hp.coalesce(self.heightLineEdit.text(), '')
    _characterDefinition['weight'] = hp.coalesce(f'{self.weightLineEdit.text()} lbs', '')
    _characterDefinition['alignment'] = hp.coalesce(self.alignmentComboBox.currentText(), '')
    _characterDefinition['level'] = int(hp.coalesce(self.levelSpinBox.value(), 0))
    _characterDefinition['xp'] = int(hp.coalesce(self.xpLineEdit.text(), 0))
    #_characterDefinition['infravision'] = hp.coalesce(self.infravisionLineEdit.text(), 0)
    _characterDefinition['starting_wealth'] = hp.coalesce(self.startingWealthSpinBox.value(), 0)
    _characterDefinition['languages'] = hp.coalesce(self.languagesLineEdit.text(), '')
    _characterDefinition['strength_score'] = hp.coalesce(int(self.strengthSpinBox.value()), 0)
    _characterDefinition['dexterity_score'] = hp.coalesce(int(self.dexteritySpinBox.value()), 0)
    _characterDefinition['intelligence_score'] = hp.coalesce(int(self.intelligenceSpinBox.value()), 0)
    _characterDefinition['wisdom_score'] = hp.coalesce(int(self.wisdomSpinBox.value()), 0)
    _characterDefinition['constitution_score'] = hp.coalesce(int(self.constitutionSpinBox.value()), 0)
    _characterDefinition['charisma_score'] = hp.coalesce(int(self.charismaSpinBox.value()), 0)
    _characterDefinition['movement_exploration'] = hp.coalesce(int(self.movementExplorationLineEdit.text()), 0)
    _characterDefinition['movement_encounter'] = hp.coalesce(int(self.movementEncounterLabel.text()), 0)
    _characterDefinition['movement_overland'] = hp.coalesce(int(self.movementOverlandLabel.text()), 0)
    _characterDefinition['hit_dice'] = self.classData.get('hit_dice', '')
    _characterDefinition['hit_points'] = hp.coalesce(int(self.hpLineEdit.text()), 0)
    _characterDefinition['thac0'] = hp.coalesce(self.thac0SpinBox.value(), 0)
    _characterDefinition['ac'] = hp.coalesce(self.acSpinBox.value(), 0)
    _characterDefinition['save_d'] = hp.coalesce(self.savePoisonDeathSpinBox.value(), 0)
    _characterDefinition['save_w'] = hp.coalesce(self.saveMagicWandsSpinBox.value(), 0)
    _characterDefinition['save_p'] = hp.coalesce(self.saveParalysisPetrificationSpinBox.value(), 0)
    _characterDefinition['save_b'] = hp.coalesce(self.saveBreathAttacksSpinBox.value(), 0)
    _characterDefinition['save_s'] = hp.coalesce(self.saveSpellsRodsStavesSpinBox.value(), 0)
    _characterDefinition['skill_forage'] = hp.coalesce(int(self.foragingSkillSpinBox.value()), 1)
    _characterDefinition['skill_find_room_trap'] = hp.coalesce(int(self.findRoomTrapSkillSpinBox.value()), 1)
    _characterDefinition['skill_listen_door'] = hp.coalesce(int(self.listenAtDoorSkillSpinBox.value()), 1)
    _characterDefinition['skill_hunt'] = hp.coalesce(int(self.huntingSkillSpinBox.value()), 1)
    _characterDefinition['skill_open_stuck_door'] = hp.coalesce(int(self.openStuckDoorSkillSpinBox.value()), 1)
    _characterDefinition['skill_find_secret_door'] = hp.coalesce(int(self.findSecretDoorSkillSpinBox.value()), 1)
    _characterDefinition['notes'] = ''

    return _characterDefinition


  def updateAC(self):
    _ac = self.calculateUnarmoredAc()
    self.acSpinBox.setValue(_ac)
    self.acBonusLabel.setText(f'{self.dexterityModSpinBox.value()}')
    self.unarmoredACLabel.setText(str(_ac))

  def updateUiWithClassData(self):
    if not self.className:
      return

    # Get level from spin box
    _level = self.levelSpinBox.value()

    # Languages
    self.languagesLineEdit.setText(self.classData['languages'])

    # Hit-Dice
    _hitDice = self.classData['hit_dice']
    self.hdSpinBoxLabel.setText(f'HD ({_hitDice}):')

    # Get data based on level
    _levelProgression = self.classData['level_progression']
    _levelProgressionData = _levelProgression['rows']
    _levelNormalized = (_level if _level < len(_levelProgressionData) else len(_levelProgressionData) - 1) - 1

    # THAC0
    _thac0 = int(_levelProgressionData[_levelNormalized]['thac0'].split(' ')[0])
    self.thac0SpinBox.setValue(_thac0)

    # Saving Throws
    self.savePoisonDeathSpinBox.setValue(int(_levelProgressionData[_levelNormalized]['save_d']))
    self.saveParalysisPetrificationSpinBox.setValue(int(_levelProgressionData[_levelNormalized]['save_p']))
    self.saveSpellsRodsStavesSpinBox.setValue(int(_levelProgressionData[_levelNormalized]['save_s']))
    self.saveBreathAttacksSpinBox.setValue(int(_levelProgressionData[_levelNormalized]['save_b']))
    self.saveMagicWandsSpinBox.setValue(int(_levelProgressionData[_levelNormalized]['save_w']))

    # Apply class modifiers
    self.applyClassModifiers()

    # Determine potential xp bonus
    self.calculateXpBonus()

class LoadDialogWidget(QWidget):
  classSelectedForLoad = Signal(int)
  classSelectedForLoadNew = Signal(str)
  characterSelectedForLoad = Signal(int)

  def __init__(self, dataModelName : str, parent=None):
    super().__init__(parent)

    self.modelName = dataModelName

    self.gameSystemLabel = QLabel('Game System: ')
    self.gameSystemComboBox = QComboBox()
    self.gameSystemComboBox.setModel(dm.getDataModels().model('GAME_SYSTEM'))
    self.gameSystemComboBox.setModelColumn(dm.getDataModels().model('GAME_SYSTEM').record().indexOf('NAME'))
    self.gameSystemComboBox.currentIndexChanged.connect(self.handleGameSystemComboBoxIndexChanged)

    self.tableView = QTableView()
    self.tableView.setModel(dm.getDataModels().model(self.modelName))
    self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
    self.tableView.setSelectionMode(QTableView.SelectionMode.SingleSelection)
    self.tableView.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    self.tableView.horizontalHeader().setStretchLastSection(True)
    self.tableView.verticalHeader().hide()
    self.tableView.doubleClicked.connect(self.handleClassTableViewDoubleClick)
    self.tableView.hideColumn(self.tableView.model().record().indexOf('ID'))

    if self.modelName == 'CHARACTER':
      self.tableView.hideColumn(self.tableView.model().record().indexOf('GAME_SYSTEM'))


    self.loadButton = QPushButton('Load')
    self.loadButton.clicked.connect(self.handleLoadButton)

    _buttonHelperLayout = QHBoxLayout()
    _buttonHelperLayout.addWidget(self.loadButton)
    _buttonHelperLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

    _mainVBoxLayout = QVBoxLayout()
    _mainVBoxLayout.addWidget(self.gameSystemComboBox)
    _mainVBoxLayout.addWidget(self.tableView)
    _mainVBoxLayout.addLayout(_buttonHelperLayout)

    _widgetWidth = self.tableView.verticalHeader().width() + self.tableView.frameWidth() * 2
    _widgetWidth += sum(self.tableView.columnWidth(c) for c in range (self.tableView.model().columnCount()))
    _widgetWidth += _mainVBoxLayout.contentsMargins().left() + _mainVBoxLayout.contentsMargins().right()
    _widgetWidth += math.floor(_widgetWidth * 0.3)

    self.setLayout(_mainVBoxLayout)
    self.resize(_widgetWidth, self.size().height())

  def handleClassTableViewDoubleClick(self, index):
    self.handleLoadButton(index)

  def handleGameSystemComboBoxIndexChanged(self):
    pass

  def handleLoadButton(self, index=None):
    _model = self.tableView.model()
    _idColumn = _model.record().indexOf('ID')
    _idColumnName = _model.record().indexOf('NAME')

    _selectedId = -1
    _selectedName = ''
    if index:
      _selectedId = _model.index(index.row(), _idColumn).data()
      _selectedName = _model.index(index.row(), _idColumnName).data()
    else:
      for _index in self.tableView.selectionModel().selectedRows():
        _selectedId = _model.index(_index.row(), _idColumn).data()
        _selectedName = _model.index(_index.row(), _idColumnName).data()

    if self.modelName == 'CLASS':
      #self.classSelectedForLoad.emit(_selectedId)
      self.classSelectedForLoadNew.emit(_selectedName)
    elif self.modelName == 'CHARACTER':
      self.characterSelectedForLoad.emit(_selectedId)

    self.close()

class Trait:
  class Element:
    def __init__(self, order : int = 0, elementType : str = None, content : str | dict = None):
      self.order = order
      self.type = elementType
      self.content = content

  def __init__(self, name : str, elements : list | None):
    self.name = name
    self.elements = elements

class TraitGroupBox(QGroupBox):
  deletionRequested = Signal(int)

  def __init__(self, trait : Trait, layoutRow : int, parent=None, mode : str = 'edit'):
    super().__init__(parent)

    # Fields

    # Each group box keeps a copy of its trait so it can be locally modified before being saved by the TraitScrollArea
    self.trait = copy.deepcopy(trait)
    self.trait.elements = [] if not trait.elements else trait.elements
    self.traitName = trait.name
    self.setProperty('name', 'traitGroupBox')
    self.numStaticRows = 2
    self.mode = mode

    _nameLabel = QLabel('Name:')
    _nameLineEdit = QLineEdit()
    _nameLineEdit.setProperty('name', 'traitNameLineEdit')
    _nameLineEdit.setText(self.traitName)
    if self.mode == 'view':
      _nameLineEdit.setReadOnly(True)

    self.addElementComboBox = QComboBox()
    self.addElementComboBox.addItem('Add Element')
    self.addElementComboBox.model().item(0).setEnabled(False)
    self.addElementComboBox.addItems(['Text', 'Table'])
    self.addElementComboBox.activated.connect(self.handleAddElementComboBoxActivated)

    _deleteButton = QPushButton('Delete Trait')
    _deleteButton.setProperty('row', layoutRow)
    _deleteButton.setProperty('name', 'deleteTraitButton')
    _deleteButton.clicked.connect(self.handleDeleteTraitButton)

    _layout = QGridLayout()
    _layout.setSpacing(5)
    _layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    _layout.addWidget(_nameLabel, 0, 0)
    _layout.addWidget(_nameLineEdit, 0, 1, 1, 2)
    if self.mode == 'edit':
      _layout.addWidget(self.addElementComboBox, 1, 0)
      _layout.addWidget(_deleteButton, 1, 1)
    _layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum), 1, 2)
    self.setLayout(_layout)

    if self.trait.elements:
      self.buildLayout(self.trait.elements)

    self.setProperty('order', layoutRow)

  def buildLayout(self, elementList):
    _traitGroupBoxLayoutRowCount = self.layout().rowCount()
    _traitGroupBoxLayoutColumnCount = self.layout().columnCount()

    if elementList:
      for _element in elementList:
        _widget = None
        if _element.type == 'text':
          _widget = self.buildTextElement()
          _widget.editor.setHtml(_element.content)
          _widget.editor.syncInternalBlockFormatWithDocument()
          if self.mode == 'view':
            _widget.editor.setReadOnly(True)
        elif _element.type == 'table':
          _widget = self.buildTableElement(columns=_element.content['columns'], data=_element.content['rows'])
          _widget.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers if self.mode == 'view' else QAbstractItemView.EditTrigger.AnyKeyPressed)

        _layout = self.buildElementLayout(_widget, _element.type, _traitGroupBoxLayoutRowCount)

        self.layout().addLayout(_layout, _traitGroupBoxLayoutRowCount, 0, 1, 3)
        _traitGroupBoxLayoutRowCount = self.layout().rowCount()

      # Add spacer at the bottom to push up all elements above
      # Use widget here because spacer can't receive a custom property
      _spacerWidget = QWidget()
      _spacerWidget.setProperty('name', 'bottomSpacer')
      _spacerWidget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

      self.layout().addWidget(_spacerWidget, _traitGroupBoxLayoutRowCount, 0)

  def buildElementLayout(self, widget, elementType : str, layoutRow : int):
    _deleteButtonTooltip = ''

    if elementType == 'text':
      _deleteButtonTooltip = 'Delete Text'
    elif elementType == 'table':
      _deleteButtonTooltip = 'Delete Table'

    # Determine number of trait elements within the trait group
    _elementCount = 0
    for _child in self.findChildren(QHBoxLayout):
      if _child.property('name') == 'elementHBoxLayout':
        _elementCount +=1

    _widget = widget
    _widget.setProperty('order', _elementCount)

    _widgetVBoxLayout = QVBoxLayout()
    _widgetVBoxLayout.addWidget(widget)
    _widgetVBoxLayout.addStretch(1)

    # Build final layout
    _elementHBoxLayout = QHBoxLayout()
    _elementHBoxLayout.setProperty('name', 'elementHBoxLayout')
    _elementHBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _elementHBoxLayout.addLayout(_widgetVBoxLayout)

    if self.mode == 'edit':
      _buttonLayout = self.buildTraitElementButtonsLayout(deleteButtonTooltip=_deleteButtonTooltip, layoutRow=layoutRow)
      _elementHBoxLayout.addLayout(_buttonLayout)

    return _elementHBoxLayout

  def buildTraitElementButtonsLayout(self, deleteButtonTooltip='', layoutRow=-1):
    if layoutRow == -1:
      return

    # Delete trait button
    _deleteButton = QPushButton()
    _deleteButton.setIcon(QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon))
    _deleteButton.setToolTip(deleteButtonTooltip)
    _deleteButton.setProperty('row', layoutRow)
    _deleteButton.clicked.connect(self.handleDeleteTraitElementButton)

    # Move up button
    _moveUpButton = QPushButton()
    _moveUpButton.setIcon(QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
    _moveUpButton.setToolTip('Move Up')
    _moveUpButton.setProperty('row', layoutRow)
    _moveUpButton.clicked.connect(lambda clicked: self.handleMoveTraitElementUpDownButtons(layoutRow, 'up'))

    # Move down button
    _moveDownButton = QPushButton()
    _moveDownButton.setIcon(QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
    _moveDownButton.setToolTip('Move Down')
    _moveDownButton.setProperty('row', layoutRow)
    _moveDownButton.clicked.connect(lambda clicked: self.handleMoveTraitElementUpDownButtons(layoutRow, 'down'))

    # Buttons helper layout
    _innerButtonLayout = QHBoxLayout()
    _innerButtonLayout.addWidget(_moveUpButton)
    _innerButtonLayout.addWidget(_moveDownButton)
    _innerButtonLayout.addWidget(_deleteButton)
    _outerButtonLayout = QVBoxLayout()
    _outerButtonLayout.addLayout(_innerButtonLayout)
    _outerButtonLayout.addStretch(1)

    return _outerButtonLayout

  def buildTextElement(self):
    _element = qw.RichTextEditor(mode=self.mode)
    return _element

  def buildTableElement(self, columns : list = None, data : list = None):
    _data = data if data else []
    _columns = columns if columns else []

    _numRows = len(_data) if _data else 1
    _numColumns = len(_columns) if _columns else 1

    # Define table
    _table = QTableWidget(_numRows, _numColumns)
    _table.setHorizontalHeaderLabels(_columns)
    _table.horizontalHeader().setSectionsClickable(True)
    _table.horizontalHeader().setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
    _table.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
    _table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectItems)
    _table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
    _table.horizontalHeader().sectionDoubleClicked.connect(lambda sectionIndex: self.editHeaderSectionName(_table, sectionIndex))

    # Load data
    for i, _row in enumerate(_data):
      for j, _column in enumerate(_columns):
        _item = QTableWidgetItem(_row[_column])
        _table.setItem(i, j, _item)
    return _table

  def editHeaderSectionName(self, table, sectionIndex):
    _oldName = table.horizontalHeaderItem(sectionIndex).text()
    _newName, _ok = QInputDialog.getText(table, 'Rename Column', 'New Column Name:', text=_oldName)

    if _ok:
      table.horizontalHeaderItem(sectionIndex).setText(_newName)

  # Returns the value of the 'order'-property from the editor/table widget in the layout row
  def getTraitElementRegisterIndexFromLayoutRow(self, layoutRow : int) -> int | None:
    _layout = None
    for i in range(self.layout().count()):
      _row, _column, _rowSpan, _columnSpan = self.layout().getItemPosition(i)
      if _row == layoutRow:
        _layout = self.layout().itemAt(i)
        break

    if not _layout:
      return None

    _oldIndex = None
    for _widget in qh.iterateLayoutWidgets(_layout):
      if type(_widget) not in (QTableWidget, qw.RichTextEditor):
        continue
      _oldIndex = _widget.property('order')
      break

    return _oldIndex

  def handleAddElementComboBoxActivated(self, index):
    _elementType = self.addElementComboBox.itemText(index).lower()
    self.addElementComboBox.setCurrentIndex(0)

    _element = None
    if _elementType == 'text':
      _element  = Trait.Element(order=len(self.trait.elements), elementType=_elementType, content='')
    elif _elementType == 'table':
      _selectTableSizeWidget = qw.SelectTableSizeWidget(parent=self.addElementComboBox)
      _pos = self.addElementComboBox.mapToGlobal(QPoint(0, 0))
      _selectTableSizeWidget.move(_pos)

      if not _selectTableSizeWidget.exec():
        return

      _numRows, _numColumns = _selectTableSizeWidget.values()

      _columns = [''] * _numColumns
      _rows = [[''] * _numColumns for _ in range(_numRows)]
      _dict = {'columns': _columns, 'rows': _rows}
      _element  = Trait.Element(order=len(self.trait.elements), elementType=_elementType, content=_dict)

    self.trait.elements.append(Trait.Element(_element.order, _element.type, _element.content))

    self.removeTraitElementsFromUi()
    self.buildLayout(self.trait.elements)

  def handleDeleteTraitButton(self):
    _sender = self.sender()
    if not _sender.property('row'):
      return
    self.deletionRequested.emit(_sender.property('row'))

  def handleDeleteTraitElementButton(self):
    _index = self.getTraitElementRegisterIndexFromLayoutRow(self.sender().property('row'))

    del self.trait.elements[_index]

    self.removeTraitElementsFromUi()
    self.buildLayout(self.trait.elements)

  def handleMoveTraitElementUpDownButtons(self, layoutRow, direction):
    # Get the layout for the trait's element in base layout's row
    _oldIndex = self.getTraitElementRegisterIndexFromLayoutRow(layoutRow)
    if _oldIndex is None:
      return

    _newIndex = _oldIndex + 1 if direction == 'down' else _oldIndex - 1
    if not 0 <= _newIndex < len(self.trait.elements):
      return

    # Swap elements
    self.trait.elements[_oldIndex], self.trait.elements[_newIndex] = self.trait.elements[_newIndex], self.trait.elements[_oldIndex]

    self.removeTraitElementsFromUi()
    self.buildLayout(self.trait.elements)

  def rebuildLayout(self):
    _newLayout = qh.rebuildLayout(self.layout())
    qh.updateLayoutOnWidget(self, _newLayout)

  def removeTraitElementsFromUi(self):
    _layout = self.layout()

    for i in reversed(range(_layout.count())):
      _rowCount = self.layout().rowCount()
      _item = _layout.itemAt(i)
      _row, _column, _rowSpan, _columnSpan = self.layout().getItemPosition(i)

      if _row < self.numStaticRows:
        continue

      if not _item.layout():
        continue

      if _item.layout().property('name') == 'elementHBoxLayout':
        qh.clearLayout(_item.layout())
        _item.layout().setParent(None)

    # Remove spacer widget at the end of the layout
    # Will be added back by buildLayout()
    _spacerWidget = qh.findChildByProperty(self, QWidget, 'name', 'bottomSpacer')
    if _spacerWidget:
      self.layout().removeWidget(_spacerWidget)

    self.rebuildLayout()

class TraitsScrollArea(QScrollArea):
  def __init__(self, parent=None, mode : str = 'edit', displayTitle : bool = True):
    super().__init__(parent)

    # Fields
    self.traits = []
    self.mode = mode

    _traitsLabel = QLabel('Traits:')
    _addTraitButton = QPushButton('+')
    _addTraitButton.setProperty('name', 'addTraitButton')
    _addTraitButton.clicked.connect(self.handleAddTraitButton)

    _addTraitButtonHelperLayout = QHBoxLayout()
    _addTraitButtonHelperLayout.addWidget(_addTraitButton)
    _addTraitButtonHelperLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

    _layout = QGridLayout()
    _layout.setSpacing(10)
    _layout.setContentsMargins(0, 0, 0, 0)
    if mode == 'edit':
      _layout.addWidget(_traitsLabel, 0, 0)
      _layout.addLayout(_addTraitButtonHelperLayout, 1, 0)
    _layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    _containerWidget = QWidget()
    _containerWidget.setLayout(_layout)

    # Finish setup
    self.setWidgetResizable(True)
    #self.setFrameStyle(QFrame.Shape.NoFrame)
    self.setWidget(_containerWidget)

  def addTrait(self, name='', elementList : list = None, addToRegister = True):
    # Save trait to register
    _trait = Trait(name, elementList)
    if addToRegister:
      self.traits.append(_trait)

    _nameLabel = QLabel(name)
    _nameLabel.setProperty('name', 'traitNameLabel')

    _fileIcon = QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
    _editViewButton = QPushButton()
    _editViewButton.setIcon(_fileIcon)
    _editViewButton.setToolTip('View/Edit')
    _editViewButton.setProperty('name', 'editViewTraitButton')

    # Move up button
    _moveUpButton = QPushButton()
    _moveUpButton.setIcon(QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_ArrowUp))
    _moveUpButton.setToolTip('Move Up')
    _moveUpButton.setProperty('name', 'moveUpButton')
    # Move down button
    _moveDownButton = QPushButton()
    _moveDownButton.setIcon(QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_ArrowDown))
    _moveDownButton.setToolTip('Move Down')
    _moveDownButton.setProperty('name', 'moveDownButton')

    _trashIcon = QApplication.instance().style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
    _deleteButton = QPushButton()
    _deleteButton.setIcon(_trashIcon)
    _deleteButton.setToolTip('Delete')
    _deleteButton.setProperty('name', 'deleteTraitButton')

    _layoutRow = self.widget().layout().rowCount()
    _editViewButton.clicked.connect(lambda clicked : self.handleTraitEditViewButtonClicked(_layoutRow, name))
    _deleteButton.clicked.connect(lambda clicked : self.handleTraitDeleteButtonClicked(_layoutRow, name))
    _moveUpButton.clicked.connect(lambda clicked: self.handleMoveTraitElementUpDownButtons(_layoutRow, 'up'))
    _moveDownButton.clicked.connect(lambda clicked: self.handleMoveTraitElementUpDownButtons(_layoutRow, 'down'))

    self.widget().layout().addWidget(_nameLabel, _layoutRow, 0)
    self.widget().layout().addWidget(_editViewButton, _layoutRow, 1)

    if self.mode == 'edit':
      self.widget().layout().addWidget(_moveUpButton, _layoutRow, 2)
      self.widget().layout().addWidget(_moveDownButton, _layoutRow, 3)
      self.widget().layout().addWidget(_deleteButton, _layoutRow, 4)

  def addTraits(self):
    for _trait in self.traits:
      self.addTrait(name=_trait.name, elementList=_trait.elements, addToRegister=False)

  def addTraitsFromJson(self, traits):
    self.resetLayout()
    self.resetTraitRegister()

    # Load traits
    _traits = traits
    # Deserialize traits into Trait objects
    for i, _trait in enumerate(_traits):
      _elements = []
      for j, _elementDict in enumerate(_trait['elements']):
        _element = Trait.Element(j, _elementDict['type'], _elementDict['content'])
        _elements.append(_element)

      self.addTrait(name=_trait['name'], elementList=_elements, addToRegister=True)

  def getTraitPositionInRegisterByName(self, name : str) -> int | None :
    _position = next((_i for _i, _t in enumerate(self.traits) if _t.name == name), None)
    return _position

  def getTraitFromRegisterByName(self, name : str) -> Trait | None :
    _position = self.getTraitPositionInRegisterByName(name)
    return self.traits[_position] if _position is not None else None

  def handleAddTraitButton(self):
    self.addTrait()

  def handleMoveTraitElementUpDownButtons(self, layoutRow: int, direction: str):
    # Get name of the respective trait
    _traitName = None
    for i in range(self.widget().layout().count()):
      _row, _column, _rowSpan, _columnSpan = self.widget().layout().getItemPosition(i)

      if _row != layoutRow:
        continue

      _item = self.widget().layout().itemAt(i)
      if not _item.widget():
        continue

      if _item.widget().property('name') == 'traitNameLabel':
        _traitName = _item.widget().text()
        break

    if not _traitName:
      return

    _oldIndex = next((_i for _i, _t in enumerate(self.traits) if _t.name == _traitName), None)
    if _oldIndex is None:
      return

    _newIndex = _oldIndex + 1 if direction == 'down' else _oldIndex - 1
    if not 0 <= _newIndex < len(self.traits):
      return

    # Swap traits
    self.traits[_oldIndex], self.traits[_newIndex] = self.traits[_newIndex], self.traits[_oldIndex]

    self.resetLayout()
    self.addTraits()

  def handleTraitDeleteButtonClicked(self, row: int, name : str):
    # Delete trait from register
    _position = self.getTraitPositionInRegisterByName(name)
    if _position is not None:
      del self.traits[_position]

    self.resetLayout()
    self.addTraits()

  def handleTraitEditViewButtonClicked(self, row : int, name : str):
    # Build selected trait group box
    _trait = self.getTraitFromRegisterByName(name)
    if not _trait:
      return

    _traitGroupBox = TraitGroupBox(layoutRow=row, trait=_trait, mode=self.mode)
    _traitGroupBox.deletionRequested.connect(self.handleTraitGroupBoxDeletionRequested)

    _saveButton = QPushButton('Save')
    _saveButton.clicked.connect(lambda clicked : self.saveTraitToRegister(_traitGroupBox))

    _dialog = QDialog(self)

    _closeButton = QPushButton('Close')
    _closeButton.clicked.connect(_dialog.close)

    _layout = QGridLayout()
    _layout.addWidget(_traitGroupBox, 0, 0, 1, 3)
    if self.mode == 'edit':
      _layout.addWidget(_saveButton, 1, 0)
    _layout.addWidget(_closeButton, 1, 1)
    _layout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum), 1, 2)

    _dialog.setLayout(_layout)
    _dialog.setMinimumSize(700, 1000)

    _dialog.exec()

  def handleTraitGroupBoxDeletionRequested(self, row):
    _layout = self.widget().layout()
    _newLayout = qh.deleteRowFromGridLayout(_layout, row)

    # Update row properties for delete trait buttons
    for i in range(_newLayout.count()):
      _row, _, _, _ = _newLayout.getItemPosition(i)
      _item = _newLayout.itemAt(i)

      if _item.widget() and type(_item.widget()) == TraitGroupBox:
        _widgetLayout = _item.widget().layout()
        if not _widgetLayout:
          continue

        for _innerWidget in qh.iterateLayoutWidgets(_widgetLayout):
          if (type(_innerWidget) != QPushButton or
              not _innerWidget.property('name') == 'deleteTraitButton' or
              not _innerWidget.property('row')):
            continue

          _innerWidget.setProperty('row', _row)

    qh.updateLayoutOnWidget(self.widget(), _newLayout)

  def saveTraitToRegister(self, traitGroupBox):
    # Get trait's name
    _traitNameLineEdit = qh.findChildByProperty(traitGroupBox, QLineEdit, 'name', 'traitNameLineEdit')
    _traitNameOld = traitGroupBox.traitName
    _traitNameNew = _traitNameLineEdit.text() if _traitNameLineEdit else None

    if _traitNameNew is None:
      return

    _traitPositionInRegister = next((_i for _i, _trait in enumerate(self.traits) if _trait.name == _traitNameOld), None)

    if _traitPositionInRegister is None:
      return

    _elements = []
    for _child in traitGroupBox.findChildren(qw.RichTextEditor):
      _htmlStr = _child.toHtml()
      _order = _child.property('order')
      _elements.append(Trait.Element(_order, 'text', _htmlStr))

    for _child in traitGroupBox.findChildren(QTableWidget):
      _tableDict = qh.serializeTableWidgetToDict(_child)
      _order = _child.property('order')
      _elements.append(Trait.Element(_order, 'table', _tableDict))

    _elements.sort(key=lambda element: element.order)

    self.traits[_traitPositionInRegister] = Trait(_traitNameNew, _elements)

    self.resetLayout()
    for _trait in self.traits:
      self.addTrait(name=_trait.name, elementList=_trait.elements, addToRegister=False)

  def rebuildLayout(self):
    _newLayout = qh.rebuildLayout(self.widget().layout())
    qh.updateLayoutOnWidget(self.widget(), _newLayout)

  def resetLayout(self):
    _layout = self.widget().layout()

    for i in reversed(range(_layout.count())):
      _item = _layout.itemAt(i)
      if not _item.widget():
        continue

      if _item.widget().property('name') in ('traitNameLabel', 'editViewTraitButton', 'moveUpButton', 'moveDownButton', 'deleteTraitButton'):
        _item = _layout.takeAt(i)
        _item.widget().deleteLater()

    self.rebuildLayout()

  def resetTraitRegister(self):
    self.traits = []

  def serializeTraitRegister(self):
    _result = []
    for _trait in self.traits:
      _name = _trait.name
      _elements = []
      for i, _element in enumerate(_trait.elements):
        _elements.append({'order': i, 'type': _element.type, 'content': _element.content})
      _result.append({'name': _name, 'elements': _elements})

    return _result

class ClassManagerOseWidget(QWidget):
  def __init__(self, parent=None):
    super().__init__(parent)

    #Fields
    self.gameSystemId = dm.getDataModels().getDataForModelIndex(modelName='GAME_SYSTEM', columnName='ID', filterColumns=('NAME_SHORT',), filterValues=('OSE',))
    self.isCustomClass = False
    self.usesMagic = False

    # Header Label
    _headerLabel = QLabel('Class Manager')
    _headerLabel.setObjectName('headerLabel')

    ## Settings GroupBox

    # Game System ComboBox
    _gameSystemLabel = QLabel('Game System: ')
    self.gameSystemComboBox = QComboBox()
    self.gameSystemComboBox.setModel(dm.getDataModels().model('GAME_SYSTEM'))
    self.gameSystemComboBox.setModelColumn(dm.getDataModels().model('GAME_SYSTEM').record().indexOf('NAME'))
    self.gameSystemComboBox.currentIndexChanged.connect(self.handleGameSystemComboBoxIndexChanged)

    # Custom Class CheckBox
    _customClassCheckBoxLabel = QLabel('Custom Class: ')
    self.customClassCheckBox = QCheckBox()
    self.customClassCheckBox.setChecked(self.isCustomClass)
    self.customClassCheckBox.toggled.connect(self.handleCustomClassCheckBoxToggled)

    # Uses Magic CheckBox
    _usesMagicCheckBoxLabel = QLabel('Uses Magic: ')
    self.usesMagicCheckBox = QCheckBox()
    self.usesMagicCheckBox.setChecked(self.usesMagic)
    self.usesMagicCheckBox.toggled.connect(self.handleUsesMagicCheckBoxToggled)

    _settingsGroupBoxGridLayout = QGridLayout()
    _settingsGroupBoxGridLayout.setSpacing(15)
    _settingsGroupBoxGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _settingsGroupBoxGridLayout.setContentsMargins(15, 15, 15, 15)
    _settingsGroupBoxGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _settingsGroupBoxGridLayout.addWidget(_gameSystemLabel, 0, 0)
    _settingsGroupBoxGridLayout.addWidget(self.gameSystemComboBox, 0, 1, 1, 3)
    _settingsGroupBoxGridLayout.addWidget(_customClassCheckBoxLabel, 1, 0)
    _settingsGroupBoxGridLayout.addWidget(self.customClassCheckBox, 1, 1)
    _settingsGroupBoxGridLayout.addWidget(_usesMagicCheckBoxLabel, 1, 2)
    _settingsGroupBoxGridLayout.addWidget(self.usesMagicCheckBox, 1, 3)

    _settingsGroupBoxGridLayout.setColumnStretch(0, 1)
    _settingsGroupBoxGridLayout.setColumnStretch(1, 1)
    _settingsGroupBoxGridLayout.setColumnStretch(2, 1)
    _settingsGroupBoxGridLayout.setColumnStretch(3, 1)
    _settingsGroupBoxGridLayout.setColumnStretch(4, 20)

    _settingsGroupBox = QGroupBox('Settings')
    _settingsGroupBox.setLayout(_settingsGroupBoxGridLayout)

    ## Class Manager GroupBox

    _nameLabel = QLabel('Name:')
    self.nameLineEdit = QLineEdit()
    self.nameLineEdit.setProperty('name', 'name')

    _primeRequisitesLabel = QLabel('Prime Requisites:')
    self.primeRequisitesLineEdit = QLineEdit()
    self.primeRequisitesLineEdit.setProperty('name', 'prime_requisites')

    _requirementsLabel = QLabel('Requirements:')
    self.requirementsLineEdit = QLineEdit()
    self.requirementsLineEdit.setProperty('name', 'requirements')

    _hitDiceLabel = QLabel('Hit Dice:')
    self.hitDiceLineEdit = QLineEdit()
    self.hitDiceLineEdit.setProperty('name', 'hit_dice')

    _maximumLevelLabel = QLabel('Maximum Level:')
    self.maximumLevelLineEdit = QLineEdit()
    self.maximumLevelLineEdit.setProperty('name', 'maximum_level')

    _armourLabel = QLabel('Armour:')
    self.armourLineEdit = QLineEdit()
    self.armourLineEdit.setProperty('name', 'armour')

    _weaponsLabel = QLabel('Weapons:')
    self.weaponsLineEdit = QLineEdit()
    self.weaponsLineEdit.setProperty('name', 'weapons')

    _languagesLabel = QLabel('Languages:')
    self.languagesLineEdit = QLineEdit()
    self.languagesLineEdit.setProperty('name', 'languages')

    _descriptionLabel = QLabel('Description:')
    self.descriptionPlainTextEdit = QPlainTextEdit()
    self.descriptionPlainTextEdit.setProperty('name', 'description')
    self.descriptionPlainTextEdit.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

    _levelProgressionLabel = QLabel('Level Progression:')
    _levelProgressionAddButton = QPushButton('+')
    _levelProgressionAddButton.clicked.connect(self.handleLevelProgressionAddButton)

    _levelProgressionAddButtonHelperLayout = QHBoxLayout()
    _levelProgressionAddButtonHelperLayout.addWidget(_levelProgressionAddButton)
    _levelProgressionAddButtonHelperLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum))

    self.levelProgressionTableWidget = QTableWidget()
    self.levelProgressionTableWidget.setProperty('name', 'level_progression')
    self.levelProgressionTableWidget.setRowCount(0)

    # Set up level progression table columns
    _levelProgressionDefinitionData = data.getGameSystemData().getClassDefinition(self.getGameSystemNameFromComboBox()).get('level_progression')
    _levelProgressionTableColumns = [_column['label'] for _column in _levelProgressionDefinitionData.get('columns', [])]
    self.levelProgressionTableWidget.setColumnCount(len(_levelProgressionTableColumns) + 1)

    for i, _column in enumerate(_levelProgressionTableColumns):
      self.levelProgressionTableWidget.setHorizontalHeaderItem(i, QTableWidgetItem(_column))
      _columnWidth = max(len(_column) * 10, 80)
      self.levelProgressionTableWidget.setColumnWidth(i, _columnWidth)

    self.levelProgressionTableWidget.setHorizontalHeaderItem(len(_levelProgressionTableColumns), QTableWidgetItem('ACTIONS'))
    self.levelProgressionTableWidget.setColumnWidth(len(_levelProgressionTableColumns), len('ACTIONS') * 10)
    # Traits #
    self.traitsScrollArea = TraitsScrollArea()

    # Bottom button row
    _importFromFileButton = QPushButton('Import From File')
    _loadFromDbButton = QPushButton('Load From Database')
    _loadFromDbButton.clicked.connect(self.handleLoadFromDbButton)
    _saveToDbButton = QPushButton('Save To Database')
    _saveToDbButton.clicked.connect(self.handleSaveToDatabaseButton)
    _exportToFileButton = QPushButton('Export To File')
    _clearButton = QPushButton('Clear')
    _clearButton.clicked.connect(self.handleClearButton)
    _helpButton = QPushButton('Help')

    ## Widgets, Pop-Ups, Tool-Windows, etc.

    # Load class pop-up
    self.loadClassWidget = LoadDialogWidget(dataModelName='CLASS')
    self.loadClassWidget.setWindowTitle('Load Class From Database')
    self.loadClassWidget.classSelectedForLoad.connect(self.loadClassDataFromDatabase)
    self.loadClassWidget.classSelectedForLoadNew.connect(self.loadClassData)

    # Move to Center of the main window
    _mainWindow = hp.getMainWindow()
    _pos = _mainWindow.mapToGlobal(self.rect().topLeft())
    _size = _mainWindow.size()
    _x = _pos.x() + (_size.width() - self.loadClassWidget.width()) // 2
    _y = _pos.y() + (_size.height() - self.loadClassWidget.height()) // 2
    self.loadClassWidget.move(QPoint(_x, _y))

    _bottomButtonRowHelperLayout = QHBoxLayout()
    _bottomButtonRowHelperLayout.addWidget(_importFromFileButton)
    _bottomButtonRowHelperLayout.addWidget(_loadFromDbButton)
    _bottomButtonRowHelperLayout.addWidget(_saveToDbButton)
    _bottomButtonRowHelperLayout.addWidget(_exportToFileButton)
    _bottomButtonRowHelperLayout.addWidget(_clearButton)
    _bottomButtonRowHelperLayout.addWidget(_helpButton)
    _bottomButtonRowHelperLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum))

    _propertiesGridLayout = QGridLayout()
    _propertiesGridLayout.setSpacing(15)
    _propertiesGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _propertiesGridLayout.setContentsMargins(15, 15, 15, 15)
    _propertiesGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    _propertiesGridLayout.addWidget(_nameLabel, 0, 0)
    _propertiesGridLayout.addWidget(self.nameLineEdit, 0, 1)
    _propertiesGridLayout.addWidget(_requirementsLabel, 0, 2)
    _propertiesGridLayout.addWidget(self.requirementsLineEdit, 0, 3)
    _propertiesGridLayout.addWidget(self.traitsScrollArea, 0, 4, 11, 1)
    _propertiesGridLayout.addWidget(_hitDiceLabel, 1, 0)
    _propertiesGridLayout.addWidget(self.hitDiceLineEdit, 1, 1)
    _propertiesGridLayout.addWidget(_primeRequisitesLabel, 1, 2)
    _propertiesGridLayout.addWidget(self.primeRequisitesLineEdit, 1, 3)
    _propertiesGridLayout.addWidget(_maximumLevelLabel, 2, 0)
    _propertiesGridLayout.addWidget(self.maximumLevelLineEdit, 2, 1)
    _propertiesGridLayout.addWidget(_armourLabel, 2, 2)
    _propertiesGridLayout.addWidget(self.armourLineEdit, 2, 3)
    _propertiesGridLayout.addWidget(_languagesLabel, 3, 0)
    _propertiesGridLayout.addWidget(self.languagesLineEdit, 3, 1)
    _propertiesGridLayout.addWidget(_weaponsLabel, 3, 2)
    _propertiesGridLayout.addWidget(self.weaponsLineEdit, 3, 3)
    _propertiesGridLayout.addWidget(_descriptionLabel, 4, 0)
    _propertiesGridLayout.addWidget(self.descriptionPlainTextEdit, 4, 1, 1, 3)
    _propertiesGridLayout.addWidget(_levelProgressionLabel, 5, 0)
    _propertiesGridLayout.addLayout(_levelProgressionAddButtonHelperLayout, 6, 0)
    _propertiesGridLayout.addWidget(self.levelProgressionTableWidget, 7, 0, 1, 4)
    _propertiesGridLayout.addLayout(_bottomButtonRowHelperLayout, 11, 0, 1, 4)

    _propertiesGridLayout.setColumnStretch(0, 1)
    _propertiesGridLayout.setColumnStretch(1, 1)
    _propertiesGridLayout.setColumnStretch(2, 1)
    _propertiesGridLayout.setColumnStretch(3, 1)
    _propertiesGridLayout.setColumnStretch(4, 1)

    _propertiesGroupBox = QGroupBox('Properties')
    _propertiesGroupBox.setLayout(_propertiesGridLayout)

    ## Main Layout

    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(15)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainGridLayout.setContentsMargins(15, 15, 15, 15)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    _mainGridLayout.addWidget(_headerLabel, 0, 0)
    _mainGridLayout.addWidget(_settingsGroupBox, 1, 0)
    _mainGridLayout.addWidget(_propertiesGroupBox, 2, 0)

    self.setLayout(_mainGridLayout)

  def buildTraitUiFromDb(self, traits : str):
    self.traitsScrollArea.resetLayout()
    self.traitsScrollArea.addTraitsFromJson(traits)

  def getClassPropertyId(self, propertyName):
    return dm.getDataModels().getDataForModelIndex(modelName='CLASS_PROPERTY', columnName='ID', filterColumns=('NAME',), filterValues=(propertyName,))

  def getGameSystemNameFromComboBox(self) -> str | None:
    _gameSystemLabel = self.gameSystemComboBox.currentText()
    _gameSystemData = data.getGameSystemData()
    _gameSystemName = next((_g for _g in _gameSystemData.gameSystemDataStorage if _gameSystemData.gameSystemDataStorage.get(_g)['label'] == _gameSystemLabel), None)

    return _gameSystemName

  def handleClearButton(self, confirm=True):
    if confirm:
      _confirmDialog = hp.OkCancelDialog(title='Clear All Data?', text='This will clear all data from the Manage Class UI.\nAre you sure you want to continue?')
      if not _confirmDialog.exec_():
        return

    _layout = self.layout()
    for _child in self.findChildren(QLineEdit):
      _child.clear()

    for _child in self.findChildren(QPlainTextEdit):
      _child.clear()

    self.levelProgressionTableWidget.setRowCount(0)
    for i in range(self.levelProgressionTableWidget.columnCount()):
      self.levelProgressionTableWidget.showColumn(i)
    self.traitsScrollArea.resetLayout()
    self.traitsScrollArea.traits = []

    self.isCustomClass = False
    self.usesMagic = False
    self.customClassCheckBox.setChecked(self.isCustomClass)
    self.usesMagicCheckBox.setChecked(self.usesMagic)

  def handleCustomClassCheckBoxToggled(self, toggled):
    self.isCustomClass = toggled
    self.customClassCheckBox.setChecked(toggled)

  def handleUsesMagicCheckBoxToggled(self, toggled):
    self.usesMagic = toggled
    self.usesMagicCheckBox.setChecked(toggled)

  def handleDeleteLevelProgressionRowButton(self):
    _sender = self.sender()
    if _sender is None:
      return

    _row = _sender.property('row')
    if _row is None:
      return

    self.levelProgressionTableWidget.removeRow(_row)

    # Update row properties after removal
    for _updateRow in range(_row, self.levelProgressionTableWidget.rowCount()):
      _container = self.levelProgressionTableWidget.cellWidget(_updateRow, self.levelProgressionTableWidget.columnCount() - 1)
      if not _container:
        continue

      for _button in _container.findChildren(QPushButton):
        _button.setProperty('row', _updateRow)

  def handleGameSystemComboBoxIndexChanged(self):
    pass

  def handleLevelProgressionAddButton(self):
    self.levelProgressionTableWidget.setRowCount(self.levelProgressionTableWidget.rowCount() + 1)
    for i in range(self.levelProgressionTableWidget.columnCount()):
      _item = QTableWidgetItem('')
      _item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
      self.levelProgressionTableWidget.setItem(self.levelProgressionTableWidget.rowCount() - 1, i, _item)

    app = QApplication.instance()
    _trashIcon = app.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
    _clearIcon = app.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload)

    _deleteButton = QPushButton()
    _deleteButton.setIcon(_trashIcon)
    _deleteButton.setToolTip('Delete')
    _deleteButton.setProperty('row', self.levelProgressionTableWidget.rowCount() - 1)
    _deleteButton.clicked.connect(self.handleDeleteLevelProgressionRowButton)

    _resetButton = QPushButton('-')
    _resetButton.setIcon(_clearIcon)
    _resetButton.setToolTip('Reset')
    _resetButton.setProperty('row', self.levelProgressionTableWidget.rowCount() - 1)
    _resetButton.clicked.connect(self.handleResetLevelProgressionRowButton)

    _buttonContainer = QWidget()
    _buttonContainerLayout = QHBoxLayout(_buttonContainer)
    _buttonContainerLayout.addWidget(_deleteButton)
    _buttonContainerLayout.addWidget(_resetButton)
    _buttonContainerLayout.setSpacing(5)
    _buttonContainerLayout.setContentsMargins(2, 2, 2, 2)

    self.levelProgressionTableWidget.setCellWidget(self.levelProgressionTableWidget.rowCount() - 1, self.levelProgressionTableWidget.columnCount() -1, _buttonContainer)

  def handleLoadFromDbButton(self):
    self.loadClassWidget.show()
    self.loadClassWidget.raise_()
    self.loadClassWidget.activateWindow()

  def handleResetLevelProgressionRowButton(self):
    _sender = QApplication.instance().focusWidget()
    if _sender is None:
      return

    _row = _sender.property('row')
    if _row is None:
      return

    for _column in range(self.levelProgressionTableWidget.columnCount() - 1):
      self.levelProgressionTableWidget.item(_row, _column).setText('')

  def handleSaveToDatabaseButton(self):
    # Class name here to make check asap
    _className = qh.findChildByProperty(self, QLineEdit, 'name', 'name').text()

    if not _className:
      logging.error(f'You must enter a class name to save a class to the database! All actions have been reverted.')
      return

    # Get class id from name
    _classId = dm.getDataModels().getDataForModelIndex(modelName='CLASS', columnName='ID', filterColumns=('NAME', 'GAME_SYSTEM'), filterValues=(_className, self.gameSystemId))

    _overwriteClass = False
    db.beginTransaction()

    if _classId:
      _dialog = hp.OkCancelDialog(
        title=f'Class {_className} Already Exists!',
        text=f'The class {_className} for game system OSE already exists!\nDo you want to overwrite it?')

      _overwriteClass = _dialog.exec()
      if not _overwriteClass:
        logging.info(f'Class {_className} has not been saved.')
        return
      else:
        db.delete(statement='delete from CLASS where ID = ?', args=(_classId,))
        db.delete(statement='delete from CLASS_X_CLASS_PROPERTY where CLASS = ?', args=(_classId,))

    # Write new class info to database
    _statement = 'insert into CLASS(NAME, GAME_SYSTEM, CUSTOM, USES_MAGIC) values (?, ?, ?, ?)'
    _args = (_className, self.gameSystemId, self.isCustomClass, self.usesMagic)
    _sqlRc = db.insert(statement=_statement, args=_args)
    _maxSqlRc = _sqlRc

    ## Text Edits
    _classPrimeRequisites = qh.findChildByProperty(self, QLineEdit, 'name', 'prime_requisites').text()
    _classRequirements = qh.findChildByProperty(self, QLineEdit, 'name', 'requirements').text()
    _classHitDice = qh.findChildByProperty(self, QLineEdit, 'name', 'hit_dice').text()
    _classMaximumLevel = qh.findChildByProperty(self, QLineEdit, 'name', 'maximum_level').text()
    _classArmour = qh.findChildByProperty(self, QLineEdit, 'name', 'armour').text()
    _classWeapons = qh.findChildByProperty(self, QLineEdit, 'name', 'weapons').text()
    _classLanguages = qh.findChildByProperty(self, QLineEdit, 'name', 'languages').text()
    _classDescription = qh.findChildByProperty(self, QPlainTextEdit, 'name', 'description').toPlainText()

    _maxSqlRc = max(self.writeClassPropertyToDb(_classId, self.getClassPropertyId('prime_requisites'), _classPrimeRequisites), _maxSqlRc)
    _maxSqlRc = max(self.writeClassPropertyToDb(_classId, self.getClassPropertyId('requirements'), _classRequirements), _maxSqlRc)
    _maxSqlRc = max(self.writeClassPropertyToDb(_classId, self.getClassPropertyId('hit_dice'), _classHitDice), _maxSqlRc)
    _maxSqlRc = max(self.writeClassPropertyToDb(_classId, self.getClassPropertyId('maximum_level'), _classMaximumLevel), _maxSqlRc)
    _maxSqlRc = max(self.writeClassPropertyToDb(_classId, self.getClassPropertyId('armour'), _classArmour), _maxSqlRc)
    _maxSqlRc = max(self.writeClassPropertyToDb(_classId, self.getClassPropertyId('weapons'), _classWeapons), _maxSqlRc)
    _maxSqlRc = max(self.writeClassPropertyToDb(_classId, self.getClassPropertyId('languages'), _classLanguages), _maxSqlRc)
    _maxSqlRc = max(self.writeClassPropertyToDb(_classId, self.getClassPropertyId('description'), _classDescription), _maxSqlRc)

    ## Level Progression Table
    for i in range(self.levelProgressionTableWidget.rowCount()):
      for j in range(self.levelProgressionTableWidget.columnCount()):
        _columnName = self.levelProgressionTableWidget.horizontalHeaderItem(j).text()
        # Exclude certain columns
        if _columnName == 'ACTIONS':
          continue

        # Map column header to property name and retrieve id for insert
        _propertyName = dm.getDataModels().getDataForModelIndex(modelName='CLASS_PROPERTY', columnName='NAME', filterColumns=('LABEL',), filterValues=(_columnName,))
        _propertyId = dm.getDataModels().getDataForModelIndex(modelName='CLASS_PROPERTY', columnName='ID', filterColumns=('NAME',), filterValues=(_propertyName,))

        _value = self.levelProgressionTableWidget.item(i, j).text() if self.levelProgressionTableWidget.item(i, j) else ''
        _maxSqlRc = max(self.writeClassPropertyToDb(_classId, propertyId=_propertyId, propertyValue=_value, order=i), _maxSqlRc)

   # Traits
    _serializedTraits = self.traitsScrollArea.serializeTraitRegister()
    _jsonStr = json.dumps(_serializedTraits)

    _traitsClassPropertyId = self.getClassPropertyId('traits')
    _maxSqlRc = max(self.writeClassPropertyToDb(_classId, _traitsClassPropertyId, _jsonStr), _maxSqlRc)

    if _maxSqlRc > 0:
      db.printLastError(message=f'An error occurred during insertion into the database! All transactions will be reverted.\n{hp.fillSqlPlaceholders(_statement, _args)}')
      db.printLastError()
      db.rollbackChanges()
      return

    db.endTransaction()

    # Refresh relevant models
    _classModel = dm.getDataModels().model('CLASS')
    _classModel.setQuery(_classModel.query().lastQuery())

  def changeSpellColumnVisibility(self, classId):
    _classUsesMagic = dm.getDataModels().getDataForModelIndex(modelName='CLASS', columnName='USES_MAGIC', filterColumns=('ID',), filterValues=(classId,))
    _hideSpellColumns = False
    if not bool(_classUsesMagic):
      _hideSpellColumns = True

    for i in range(self.levelProgressionTableWidget.columnCount()):
      _columName = self.levelProgressionTableWidget.horizontalHeaderItem(i).text().upper()
      if _columName.find('SPELL') != -1:
        self.levelProgressionTableWidget.setColumnHidden(i, _hideSpellColumns)

  def isUiEmpty(self):
    _isEmpty = not any(_child.text() for _child in self.findChildren(QLineEdit))
    _isEmpty = _isEmpty and self.levelProgressionTableWidget.rowCount() == 0

    return _isEmpty

  def loadClassData(self, className):
    if not self.isUiEmpty():
      _dialog = hp.OkCancelDialog(title='Override UI Data', text='Loading a class will override your current data!\nAre you sure?')

      if not _dialog.exec_():
        return
      else:
        self.handleClearButton(confirm=False)

    _gameSystemData = data.getGameSystemData()
    _gameSystemName = self.getGameSystemNameFromComboBox()

    if _gameSystemName is None:
      logging.error(f'Game system {_gameSystemName} not found in game system data!')
      return

    _classProperties = _gameSystemData.getClass(_gameSystemName, className)
    if _classProperties is None:
      logging.error(f'Class {className} not found in game system {_gameSystemName}!')
      return

    # Set simple properties which's values are strings, integers, floats, or booleans
    self.nameLineEdit.setText(_classProperties.get('name', ''))
    self.primeRequisitesLineEdit.setText(_classProperties.get('prime_requisites', ''))
    self.hitDiceLineEdit.setText(_classProperties.get('hit_dice', ''))
    self.requirementsLineEdit.setText(_classProperties.get('requirements', ''))
    self.maximumLevelLineEdit.setText(str(_classProperties.get('maximum_level', '')))
    self.armourLineEdit.setText(_classProperties.get('armour', ''))
    self.languagesLineEdit.setText(_classProperties.get('languages', ''))
    self.weaponsLineEdit.setText(_classProperties.get('weapons', ''))
    self.descriptionPlainTextEdit.setPlainText(_classProperties.get('description', ''))

    # Level progression data is supplied as a list of dictionaries where the position within the list determines the level
    _levelProgression = _classProperties.get('level_progression', {})
    _levelProgressionTableColumns = _levelProgression.get('columns', [])
    _maxSpellLevel = _classProperties.get('max_spell_level', 0)
    for _row, _level in enumerate(_levelProgression.get('rows', [])):
      self.handleLevelProgressionAddButton()
      for _columnPosition, _column in enumerate(_levelProgressionTableColumns):
        _columnLabel = _column.get('label', '')

        _levelEntry = _column.get('name', '')
        _value = _level.get(_levelEntry, '')
        for i in range(self.levelProgressionTableWidget.columnCount()):
          _columnName = self.levelProgressionTableWidget.horizontalHeaderItem(i).text()
          if _columnName == _columnLabel:
            self.levelProgressionTableWidget.item(_row, i).setText(str(_value))
            break

    for i in range(self.levelProgressionTableWidget.columnCount()):
      _columnName = self.levelProgressionTableWidget.horizontalHeaderItem(i).text()

      if (_columnName.lower().find('spells ') != -1 and
        (not _classProperties['uses_magic'] or int(_columnName.lower().split(' ')[1]) > _maxSpellLevel)):
        self.levelProgressionTableWidget.hideColumn(i)
        continue

    # Traits
    if 'traits' in _classProperties:
      self.buildTraitUiFromDb(_classProperties['traits'])

  def loadClassDataFromDatabase(self, classId):
    if not self.isUiEmpty():
      _dialog = hp.OkCancelDialog(title='Override UI Data', text='Loading a class will override your current data!\nAre you sure?')

      if not _dialog.exec_():
        return
      else:
        self.handleClearButton(confirm=False)

    # Get class data from access layer
    _className = dm.getDataModels().getDataForModelIndex(modelName='CLASS', columnName='NAME', filterColumns=('ID',), filterValues=(classId,))

    # Load and prepare class information
    _classProperties = self.prepareClassDataForLoading(classId)

    _nameField = qh.findChildByProperty(self, QLineEdit, 'name', 'name')
    _nameField.setText(_className)

    if not _classProperties:
      logging.info(f'The class {_className} does not have any registered properties!')
      return

    # Handle line and plain text edits
    for _key in _classProperties.keys():
      _value = _classProperties[_key] if _classProperties[_key] else ''
      _uiField = qh.findChildByProperty(self, QLineEdit, 'name', _key)
      if _uiField:
        _uiField.setText(_value)
        continue

      _uiField = qh.findChildByProperty(self, QPlainTextEdit, 'name', _key)
      if _uiField:
        _uiField.setPlainText(_value)
        continue

      if _key not in ('level_progression', 'saving_throws', 'traits'):
        logging.error(f'The class property {_key} does not have a corresponding ui field!')

    # Checkboxes
    self.handleCustomClassCheckBoxToggled(dm.getDataModels().getDataForModelIndex(modelName='CLASS', columnName='CUSTOM', filterColumns=('ID',), filterValues=(classId,)))
    self.handleUsesMagicCheckBoxToggled(dm.getDataModels().getDataForModelIndex(modelName='CLASS', columnName='USES_MAGIC', filterColumns=('ID',), filterValues=(classId,)))

    # Level progression table widget
    for i, _level in enumerate(_classProperties['level_progression']):
      self.handleLevelProgressionAddButton()

      for _key in _level.keys():
        _value = _level[_key]
        _columnId = qh.getColumnIdFromTableWidget(self.levelProgressionTableWidget, _key)
        if _columnId is not None:
          self.levelProgressionTableWidget.item(i, _columnId).setText(_value if _value else '')
        else:
          logging.error(f'The level progression property {_key} does not have a corresponding column in the table widget!')

    self.changeSpellColumnVisibility(classId)

    # Traits
    if 'traits' in _classProperties:
      self.buildTraitUiFromDb(_classProperties['traits'])

  def prepareClassDataForLoading(self, classId : int) -> dict:
    _classPropertySqlStatement = '''
          select ccp.ID, cp.NAME, cp.LABEL, ccp.VALUE, ccp.ORDER_1, cp.PARENT
          from GAME_SYSTEM gs
            left join CLASS_PROPERTY cp on gs.ID = cp.GAME_SYSTEM
            left join CLASS_X_CLASS_PROPERTY ccp on cp.ID = ccp.PROPERTY
          where gs.ID = ? and ccp.CLASS = ?        
          order by ccp.ID
        '''
    _classProperties = db.query(statement=_classPropertySqlStatement, args=(self.gameSystemId, classId))
    _classDataPrepared = {}

    # Process simple properties with no sub properties
    _simpleProperties = [_p for _p in _classProperties if not _p['PARENT']]
    for _property in _simpleProperties:
      _classDataPrepared[_property['NAME']] = _property['VALUE']

    # Prepare level progression data
    _levelProgressionProperties = [_p for _p in _classProperties if _p['PARENT'] == self.getClassPropertyId('level_progression')]
    _orderOld = _levelProgressionProperties[0]['ORDER_1'] if _levelProgressionProperties else -1
    _levelProgressionProcessed = []
    _levelDict = {}

    for _property in _levelProgressionProperties:
      if _orderOld != _property['ORDER_1']:
        _orderOld = _property['ORDER_1']
        _levelProgressionProcessed.append(_levelDict)
        _levelDict = {}

      # Labels are used to match easier to the target table widget
      _levelDict[_property['LABEL']] = _property['VALUE']

    if _levelDict:
      _levelProgressionProcessed.append(_levelDict)

    _classDataPrepared['level_progression'] = _levelProgressionProcessed

    # Prepare saving throw data
    _savingThrowProperties = [_p for _p in _classProperties if _p['PARENT'] == self.getClassPropertyId('saving_throws')]
    _orderOld = _savingThrowProperties[0]['ORDER_1'] if _savingThrowProperties else -1
    _savingThrowsProcessed = []
    _savingThrowDict = {}

    for _property in _savingThrowProperties:
      if _orderOld != _property['ORDER_1']:
        _orderOld = _property['ORDER_1']
        _savingThrowsProcessed.append(_savingThrowDict)
        _savingThrowDict = {}

      # Labels are used to match easier to the target table widget
      _savingThrowDict[_property['LABEL']] = _property['VALUE']

    _savingThrowsProcessed.append(_savingThrowDict)

    if _savingThrowsProcessed:
      _classDataPrepared['saving_throws'] = _savingThrowsProcessed

    return _classDataPrepared

  def writeClassPropertyToDb(self, classId, propertyId, propertyValue, order=None):
    _statement = 'insert into CLASS_X_CLASS_PROPERTY(CLASS, PROPERTY, ORDER_1, VALUE) values (?, ?, ?, ?)'
    _args = (classId, propertyId, order, propertyValue)
    _rc = db.insert(statement=_statement, args=_args)

    if _rc != 0:
      db.printLastError(message=f'An error occurred executing the following sql-statement!\n{hp.fillSqlPlaceholders(_statement, _args)}')

    return _rc

  def setCustomClassFlag(self, checked):
    self.isCustomClass = checked

  def setUsesMagicFlag(self, checked):
    self.usesMagic = checked

class CharacterBuilder(QWidget):
  def __init__(self):
    super().__init__()

    self.builderButton = QPushButton("Builder")
    self.customClassManagerButton = QPushButton("Class Manager")

    self.menuWidget = QWidget()
    self.defineMenuLayout()

    self.builderWidget = CharacterBuilderWidget()
    self.classManagerWidget = ClassManagerOseWidget()

    self.contentStackedWidget = QStackedWidget()
    self.defineContentStackedWidget()

    self.mainGridLayout = QGridLayout()
    self.mainGridLayout.addWidget(self.menuWidget, 0, 0)
    self.mainGridLayout.addWidget(self.contentStackedWidget, 0, 1)
    self.setLayout(self.mainGridLayout)

  def changeWidget(self, widget):
    self.contentStackedWidget.setCurrentWidget(widget)

  def defineMenuLayout(self):
    self.builderButton.clicked.connect(lambda clicked: self.changeWidget(self.builderWidget))
    self.customClassManagerButton.clicked.connect(lambda clicked: self.changeWidget(self.classManagerWidget))

    menuLayout = QVBoxLayout()
    menuLayout.addWidget(self.builderButton)
    #menuLayout.addWidget(self.customClassManagerButton)
    menuLayout.setSpacing(15)
    menuLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.menuWidget.setLayout(menuLayout)

  def defineContentStackedWidget(self):
    self.contentStackedWidget.addWidget(self.builderWidget)
    self.contentStackedWidget.addWidget(self.classManagerWidget)
    self.contentStackedWidget.setCurrentIndex(0)