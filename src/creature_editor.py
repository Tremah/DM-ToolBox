import csv
import logging
import sqlite3

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
  QLabel,
  QPushButton,
  QGridLayout,
  QWidget,
  QPlainTextEdit,
  QVBoxLayout,
  QHBoxLayout,
  QStackedWidget,
  QSizePolicy,
  QSpacerItem,
  QTableWidget,
  QTableWidgetItem,
  QListWidget,
  QListWidgetItem,
  QAbstractItemView,
  QGroupBox,
  QButtonGroup,
  QFormLayout,
  QComboBox,
  QCheckBox,
  QFileDialog, QTableView, QTextEdit
)

import database as db
import qt_wrapper as qtw
import data_models as dm


class CreatureEditorImportWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Fields
    self.creatureData = []

    headerLabel = QLabel('Import Creatures')
    headerLabel.setFont(QFont('Ubuntu Sans', 14))

    self.contentTextBox = QPlainTextEdit()
    self.contentTextBox.setPlaceholderText("CSV-data here...")

    self.reviewTable = QTableWidget()
    self.reviewTable.setAlternatingRowColors(True)
    self.reviewTable.horizontalHeader().setStretchLastSection(True)

    _gameSystemComboBoxLabel = QLabel('Game System:')
    self.gameSystemComboBox = QComboBox()
    self.gameSystemComboBox.setModel(dm.getDataModels().model('GAME_SYSTEM'))
    self.gameSystemComboBox.setModelColumn(2)

    _reviewButton = QPushButton('Import And Check')
    _reviewButton.setMinimumSize(150, 30)
    _reviewButton.clicked.connect(self.importAndCheckCsv)
    _reviewButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    _saveButton = QPushButton('Save')
    _saveButton.setMinimumSize(60, 30)
    _saveButton.clicked.connect(self.writeImportToDatabase)
    _saveButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    _clearButton = QPushButton('Clear')
    _clearButton.setMinimumSize(60, 30)
    _clearButton.clicked.connect(self.clearTable)
    _clearButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    # Helper Layouts
    _secondRowHBoxLayout = QHBoxLayout()
    _secondRowHBoxLayout.addWidget(self.contentTextBox)
    _secondRowHBoxLayout.addWidget(self.reviewTable)

    _thirdRowHBoxLayout = QGridLayout()
    _thirdRowHBoxLayout.addWidget(_gameSystemComboBoxLabel, 0, 0)
    _thirdRowHBoxLayout.addWidget(self.gameSystemComboBox, 0, 1)
    _thirdRowHBoxLayout.addWidget(_reviewButton, 1, 0)
    _thirdRowHBoxLayout.addWidget(_saveButton, 1, 1)
    _thirdRowHBoxLayout.addWidget(_clearButton, 1, 2)
    _thirdRowHBoxLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), 1, 3)
    _thirdRowHBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    # Finalize main layout
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(20)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainGridLayout.addWidget(headerLabel, 0, 0)
    _mainGridLayout.addLayout(_secondRowHBoxLayout, 1, 0)
    _mainGridLayout.addLayout(_thirdRowHBoxLayout, 2, 0)
    _mainGridLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 3, 0)

    _mainGridLayout.setRowStretch(0, 0)
    _mainGridLayout.setRowStretch(1, 2)
    _mainGridLayout.setRowStretch(2, 0)
    _mainGridLayout.setRowStretch(3, 1)

    self.setLayout(_mainGridLayout)

  def clearTable(self):
    self.contentTextBox.clear()
    self.reviewTable.clear()
    self.reviewTable.setRowCount(0)
    self.reviewTable.setColumnCount(0)
    self.creatureData.clear()

  def importAndCheckCsv(self):
    _csvRawData = self.contentTextBox.toPlainText().splitlines()
    _csvRows = csv.DictReader(_csvRawData, fieldnames=None, restkey='OVERFLOW', dialect='excel', delimiter=';', quotechar='"')

    # Check vs. the game system's data model if all needed columns are present
    _gameSystemModel = self.gameSystemComboBox.model()
    _gameSystemId = _gameSystemModel.data(_gameSystemModel.index(self.gameSystemComboBox.currentIndex(), _gameSystemModel.record().indexOf('ID'), self.gameSystemComboBox.rootModelIndex()))

    _creatureProperties = db.query(statement='select PROPERTY from GAME_SYSTEM_X_CREATURE_PROPERTY where GAME_SYSTEM = ?', args=(_gameSystemId,))
    _columnsInModelButNotInCsvData = []
    for _property in _creatureProperties:
      if _property['PROPERTY'] not in _csvRows.fieldnames:
        _columnsInModelButNotInCsvData.append(_property['PROPERTY'])

    # One or more necessary columns were not found in the imported data
    if _columnsInModelButNotInCsvData:
      _columnsStr = ', '.join(_columnsInModelButNotInCsvData)
      logging.error(f'{_columnsStr} not found in the supplied data.')
      return

    # Set headers
    _i = 0
    self.reviewTable.setColumnCount(len(_csvRows.fieldnames))
    for field in _csvRows.fieldnames:
      item = QTableWidgetItem(field)
      self.reviewTable.setHorizontalHeaderItem(_i, item)
      _i = _i + 1

    # Prepare Data
    for _row in _csvRows:
      self.creatureData.append(_row)

    # Insert into review table
    _i = 0
    _j = 0
    self.reviewTable.setRowCount(len(self.creatureData))
    for _creature in self.creatureData:
      for attrib in _creature:
        item = QTableWidgetItem(_creature[attrib])
        self.reviewTable.setItem(_i, _j, item)
        _j += 1
      _i += 1
      _j = 0

    self.reviewTable.show()

  def writeImportToDatabase(self):
    _gameSystemModel = self.gameSystemComboBox.model()
    _gameSystemId = _gameSystemModel.data(_gameSystemModel.index(self.gameSystemComboBox.currentIndex(), _gameSystemModel.record().indexOf('ID'), self.gameSystemComboBox.rootModelIndex()))

    # Clean up creature tables before import
    db.begin()

    _creatureIds = db.query(statement='select ID from CREATURE where GAME_SYSTEM = ?', args=(_gameSystemId,))
    db.query(statement='delete from CREATURE where GAME_SYSTEM = ?', args=(_gameSystemId,))
    db.query(statement='delete from CREATURE_X_GAME_SYSTEM_PROPERTY where GAME_SYSTEM = ?', args=(_gameSystemId,))

    _creatureIdList = []
    for _id in _creatureIds:
      _creatureIdList.append(_id['ID'])

    _creatureIdTuple = tuple(_creatureIdList)
    _placeHolders = ','.join(['?'] * len(_creatureIdTuple))

    if _creatureIdTuple:
      db.query(statement=f'delete from CREATURE_X_ENVIRONMENT where CREATURE in ({_placeHolders})', args=_creatureIdTuple)

    _creatureCount = 0
    try:
      # Get max ID to keep track of creature IDs for foreign keys
      _maxCreatureIdResult = db.query(statement='select max(ID) as ID from CREATURE', one=True)
      _nextCreatureID = 0 if not _maxCreatureIdResult['ID'] else _maxCreatureIdResult['ID']

      # Prepare creature properties for the current game system
      _creatureProperties = db.query(statement='select ID, PROPERTY as NAME from GAME_SYSTEM_X_CREATURE_PROPERTY where GAME_SYSTEM = ?', args=(_gameSystemId,))

      # Prepare environments
      _environmentsDb = db.query(statement='select ID, NAME from ENVIRONMENT')
      _environmentsDbDict = {}
      for _environmentDb in _environmentsDb:
        _environmentsDbDict[_environmentDb['NAME']] = _environmentDb['ID']

      # Prepare content sources
      _sourcesDb = db.query(f'select ID, NAME from CONTENT_SOURCE')
      _sourceDbDict = {}
      for _source in _sourcesDb:
        _sourceDbDict[_source['NAME']] = _source['ID']

      for _creature in self.creatureData:
        # Translate source names into ids
        _sourceId = _sourceDbDict[_creature['SOURCE']]

        _type = db.query(statement='select ID from CREATURE_TYPE where NAME = ?', args=(_creature['TYPE'],), one=True)
        db.insert(statement='insert into CREATURE(NAME, TYPE, GAME_SYSTEM, DESCRIPTION, TRAITS, SOURCE) values(?, ?, ?, ?, ?, ?)', args=(_creature['NAME'], _type['ID'], _gameSystemId, _creature['DESCRIPTION'], _creature['TRAITS'], _sourceId))
        _nextCreatureID += 1

        for _property in _creatureProperties:
          db.insert(statement=f'insert into CREATURE_X_GAME_SYSTEM_PROPERTY(CREATURE, GAME_SYSTEM, PROPERTY, VALUE) values(?, ?, ?, ?)', args=(_nextCreatureID, _gameSystemId, _property['ID'], _creature[_property['NAME']]))


        # Split environment list and translate into their ids
        _environmentList = _creature['ENVIRONMENT'].split(',')
        for _environment in _environmentList:
          _environmentId = _environmentsDbDict[_environment.strip()]
          db.insert(statement='insert into CREATURE_X_ENVIRONMENT(CREATURE, ENVIRONMENT) values(?, ?)', args=(_nextCreatureID, _environmentId))

        _creatureCount += 1

      if not db.commitChanges():
        db.printLastError()
        logging.error(f'Commit failed, rolling back')
        db.rollbackChanges()
      else:
        logging.info(f'{_creatureCount} creatures were written to the database')

    except Exception as e:
      logging.error(f'An error occurred during insertion of the creature data: {e}')
      db.rollbackChanges()

    # Refresh data model
    _model = dm.getDataModels().model('CREATURE_OSR')
    _query = _model.query().lastQuery()
    _model.setQuery(_query)
    _rc = _model.rowCount()
    while _model.canFetchMore():
      _model.fetchMore()
    _rc = _model.rowCount()
    pass


class CreatureEditorViewWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Header Label
    _headerLabel = QLabel('List Creatures')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    # Data Table
    self.dataTable = qtw.DataTable(lastSectionStretch=True)
    self.dataTable.setSelectionMode(QTableView.SelectionMode.SingleSelection)
    self.dataTable.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
    self.dataTable.clicked.connect(self.handleDataTableClicked)

    # Filter Group Box
    self.mainFilterGroupBox = qtw.CreatureFilterGroupBox(title='Filters', applyFilterMethod=self.dataTable.filterTable, setCreatureModelMethod=self.dataTable.setDataModel, resetFormMethod=self.resetForm)

    ## Stat Block
    # Description
    self.statBlockDescriptionValueTextEdit = QTextEdit()
    self.statBlockDescriptionValueTextEdit.setObjectName('labelTextEdit')
    self.statBlockDescriptionValueTextEdit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    _statBlockDescriptionGroupBoxLayout = QGridLayout()
    _statBlockDescriptionGroupBoxLayout.addWidget(self.statBlockDescriptionValueTextEdit, 0, 0)
    _statBlockDescriptionGroupBox = QGroupBox('Description')
    _statBlockDescriptionGroupBox.setLayout(_statBlockDescriptionGroupBoxLayout)
    _statBlockDescriptionGroupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    # General
    _statBlockNameDisplayLabel = self.makeStatBlockLabel(text='Name:')
    self.statBlockNameValueLabel = self.makeStatBlockLabel()

    _statBlockTypeDisplayLabel = self.makeStatBlockLabel(text='Type:')
    self.statBlockTypeValueLabel = self.makeStatBlockLabel()

    _statBlockEnvironmentDisplayLabel = self.makeStatBlockLabel(text='Environment:')
    self.statBlockEnvironmentValueLabel = self.makeStatBlockLabel()

    _statBlockSourceDisplayLabel = self.makeStatBlockLabel(text='Source:')
    self.statBlockSourceValueLabel = self.makeStatBlockLabel()

    for _label in [
      _statBlockNameDisplayLabel, self.statBlockNameValueLabel,
      _statBlockTypeDisplayLabel, self.statBlockTypeValueLabel,
      _statBlockEnvironmentDisplayLabel, self.statBlockEnvironmentValueLabel,
      _statBlockSourceDisplayLabel, self.statBlockSourceValueLabel
    ]:
      _label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
      _label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)


    _statBlockGeneralGroupBoxLayout = QGridLayout()
    _statBlockGeneralGroupBoxLayout.addWidget(_statBlockNameDisplayLabel, 0, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    _statBlockGeneralGroupBoxLayout.addWidget(self.statBlockNameValueLabel, 0, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    _statBlockGeneralGroupBoxLayout.addWidget(_statBlockTypeDisplayLabel, 1, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    _statBlockGeneralGroupBoxLayout.addWidget(self.statBlockTypeValueLabel, 1, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    _statBlockGeneralGroupBoxLayout.addWidget(_statBlockEnvironmentDisplayLabel, 2, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    _statBlockGeneralGroupBoxLayout.addWidget(self.statBlockEnvironmentValueLabel, 2, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    _statBlockGeneralGroupBoxLayout.addWidget(_statBlockSourceDisplayLabel, 3, 0, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    _statBlockGeneralGroupBoxLayout.addWidget(self.statBlockSourceValueLabel, 3, 1, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    _statBlockGeneralGroupBoxLayout.addItem(QSpacerItem(0,0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum), 3, 2)

    _statBlockGeneralGroupBox = QGroupBox('General')
    _statBlockGeneralGroupBox.setLayout(_statBlockGeneralGroupBoxLayout)
    _statBlockGeneralGroupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    # Combat
    _statBlockThac0DisplayLabel = self.makeStatBlockLabel(text='THAC0:')
    self.statBlockThac0ValueLabel = self.makeStatBlockLabel()

    _statBlockHdDisplayLabel = self.makeStatBlockLabel(text='HD:')
    self.statBlockHdValueLabel = self.makeStatBlockLabel()

    _statBlockAcDisplayLabel = self.makeStatBlockLabel(text='AC:')
    self.statBlockAcValueLabel = self.makeStatBlockLabel()

    _statBlockAttacksDisplayLabel = self.makeStatBlockLabel(text='Attacks:')
    self.statBlockAttacksValueTextEdit = QTextEdit()
    self.statBlockAttacksValueTextEdit.setObjectName('labelTextEdit')
    self.statBlockAttacksValueTextEdit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
    self.statBlockAttacksValueTextEdit.setMaximumHeight(100)

    _statBlockCombatGroupBoxLayout = QGridLayout()
    _statBlockCombatGroupBoxLayout.addWidget(_statBlockThac0DisplayLabel, 0, 0)
    _statBlockCombatGroupBoxLayout.addWidget(self.statBlockThac0ValueLabel, 0, 1)
    _statBlockCombatGroupBoxLayout.addWidget(_statBlockHdDisplayLabel, 1, 0)
    _statBlockCombatGroupBoxLayout.addWidget(self.statBlockHdValueLabel, 1, 1)
    _statBlockCombatGroupBoxLayout.addWidget(_statBlockAcDisplayLabel, 2, 0)
    _statBlockCombatGroupBoxLayout.addWidget(self.statBlockAcValueLabel, 2, 1)
    _statBlockCombatGroupBoxLayout.addWidget(_statBlockAttacksDisplayLabel, 3, 0, alignment=Qt.AlignmentFlag.AlignTop)
    _statBlockCombatGroupBoxLayout.addWidget(self.statBlockAttacksValueTextEdit, 3, 1)
    _statBlockCombatGroupBox = QGroupBox('Combat')
    _statBlockCombatGroupBox.setLayout(_statBlockCombatGroupBoxLayout)
    _statBlockCombatGroupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    # Saving Throws
    _statBlockSaveAsHdDisplayLabel = self.makeStatBlockLabel(text='Saves As HD:')
    self.statBlockSaveAsHdValueLabel = self.makeStatBlockLabel()
    _statBlockStDpDisplayLabel = self.makeStatBlockLabel(text='Death, Poison:')
    self.statBlockStDpValueLabel = self.makeStatBlockLabel()
    _statBlockStWDisplayLabel = self.makeStatBlockLabel(text='Magic Wands:')
    self.statBlockStWValueLabel = self.makeStatBlockLabel()
    _statBlockStPDisplayLabel = self.makeStatBlockLabel(text='Paralysis, Petrification:')
    self.statBlockStPValueLabel = self.makeStatBlockLabel()
    _statBlockStBDisplayLabel = self.makeStatBlockLabel(text='Breath Attacks:')
    self.statBlockStBValueLabel = self.makeStatBlockLabel()
    _statBlockStSrsDisplayLabel = self.makeStatBlockLabel(text='Spells, Magic Rods, Staves:')
    self.statBlockStSrsValueLabel = self.makeStatBlockLabel()

    _statBlockSavingThrowsGroupBoxLayout = QGridLayout()
    _statBlockSavingThrowsGroupBoxLayout.addWidget(_statBlockSaveAsHdDisplayLabel, 0, 0)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(self.statBlockSaveAsHdValueLabel, 0, 1)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(_statBlockStDpDisplayLabel, 1, 0)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(self.statBlockStDpValueLabel, 1, 1)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(_statBlockStWDisplayLabel, 2, 0)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(self.statBlockStWValueLabel, 2, 1)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(_statBlockStPDisplayLabel, 3, 0)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(self.statBlockStPValueLabel, 3, 1)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(_statBlockStBDisplayLabel, 4, 0)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(self.statBlockStBValueLabel, 4, 1)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(_statBlockStSrsDisplayLabel, 5, 0)
    _statBlockSavingThrowsGroupBoxLayout.addWidget(self.statBlockStSrsValueLabel, 5, 1)
    _statBlockSavingThrowsGroupBoxLayout.addItem(QSpacerItem(0,0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum), 5, 2)
    _statBlockSavingThrowGroupBox = QGroupBox('Saving Throws')
    _statBlockSavingThrowGroupBox.setLayout(_statBlockSavingThrowsGroupBoxLayout)
    _statBlockSavingThrowGroupBox.setMinimumWidth(350)
    _statBlockSavingThrowGroupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    # Traits
    self.statBlockTraitsValueTextEdit = QTextEdit()
    self.statBlockTraitsValueTextEdit.setObjectName('labelTextEdit')
    self.statBlockTraitsValueTextEdit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

    _statBlockTraitsGroupBoxLayout = QGridLayout()
    _statBlockTraitsGroupBoxLayout.addWidget(self.statBlockTraitsValueTextEdit, 0, 0)
    _statBlockTraitsGroupBox = QGroupBox('Traits')
    _statBlockTraitsGroupBox.setLayout(_statBlockTraitsGroupBoxLayout)
    _statBlockTraitsGroupBox.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

    # Main group box
    _statBlockGroupBoxLayout = QGridLayout()
    _statBlockGroupBoxLayout.setContentsMargins(15, 15, 15, 15)
    _statBlockGroupBoxLayout.setSpacing(20)
    _statBlockGroupBoxLayout.addWidget(_statBlockDescriptionGroupBox, 0, 0)
    _statBlockGroupBoxLayout.addWidget(_statBlockGeneralGroupBox, 1, 0)
    _statBlockGroupBoxLayout.addWidget(_statBlockCombatGroupBox, 2, 0)
    _statBlockGroupBoxLayout.addWidget(_statBlockSavingThrowGroupBox, 3, 0)
    _statBlockGroupBoxLayout.addWidget(_statBlockTraitsGroupBox, 4, 0)

    _statBlockGroupBoxLayout.setRowStretch(0, 1)
    _statBlockGroupBoxLayout.setRowStretch(1, 1)
    _statBlockGroupBoxLayout.setRowStretch(2, 1)
    _statBlockGroupBoxLayout.setRowStretch(3, 1)
    _statBlockGroupBoxLayout.setRowStretch(4, 3)

    self.statBlockGroupBox = QGroupBox('Stat Block')
    self.statBlockGroupBox.setLayout(_statBlockGroupBoxLayout)

    ## Data table group box
    _searchResultGroupBox = QGroupBox('Search Result')
    _searchResultGroupBoxLayout = QGridLayout()
    _searchResultGroupBoxLayout.setContentsMargins(10, 20, 10, 10)
    _searchResultGroupBoxLayout.setSpacing(15)
    _searchResultGroupBoxLayout.addWidget(self.dataTable, 0, 0)
    _searchResultGroupBox.setLayout(_searchResultGroupBoxLayout)


    # Finish setup
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(15)
    _mainGridLayout.addWidget(_headerLabel, 0, 0)
    _mainGridLayout.addWidget(self.mainFilterGroupBox, 1, 0, 1, 2)
    _mainGridLayout.addWidget(_searchResultGroupBox, 2, 0)
    _mainGridLayout.addWidget(self.statBlockGroupBox, 2, 1)

    _mainGridLayout.setRowStretch(0, 1)
    _mainGridLayout.setRowStretch(1, 1)
    _mainGridLayout.setRowStretch(2, 3)

    _mainGridLayout.setColumnStretch(0, 2)
    _mainGridLayout.setColumnStretch(1, 1)

    self.setLayout(_mainGridLayout)

    _filterValues = self.mainFilterGroupBox.getFilterItems()
    self.dataTable.filterTable(_filterValues)

  def makeStatBlockLabel(self, text='', bold=False):
    _label = QLabel(text)

    if bold:
      _font = _label.font()
      _font.setBold(True)
      _label.setFont(_font)

    return _label

  def handleDataTableClicked(self):
    _selectedRow = self.dataTable.selectionModel().selectedRows()[0].row()
    _selectedIndex = self.dataTable.selectionModel().selectedIndexes()

    for _column in range(self.dataTable.model().columnCount()):
      _index = self.dataTable.model().index(_selectedRow, _column)
      _columnName = self.dataTable.model().headerData(_column, Qt.Orientation.Horizontal)
      _text = _index.data()

      if _columnName == 'NAME':
        self.statBlockNameValueLabel.setText(_index.data())
      elif _columnName == 'DESCRIPTION':
        self.statBlockDescriptionValueTextEdit.setText(_index.data())
      elif _columnName == 'TRAITS':
        _text = _index.data().replace('; ', '\n\n').replace(';', '\n\n')
        self.statBlockTraitsValueTextEdit.setText(_text)
      elif _columnName == 'TYPE':
        self.statBlockTypeValueLabel.setText(_index.data())
      elif _columnName == 'ENVIRONMENT':
        self.statBlockEnvironmentValueLabel.setText(_index.data())
      elif _columnName == 'SOURCE':
        self.statBlockSourceValueLabel.setText(_index.data())
      elif _columnName == 'THAC0':
        self.statBlockThac0ValueLabel.setText(_index.data())
      elif _columnName == 'HD':
        self.statBlockHdValueLabel.setText(_index.data())
      elif _columnName == 'AC':
        self.statBlockAcValueLabel.setText(_index.data())
      elif _columnName == 'ATTACKS':
        _text = _index.data()
        self.statBlockAttacksValueTextEdit.setText(_text)
      elif _columnName == 'SV_HD':
        self.statBlockSaveAsHdValueLabel.setText(_index.data())
      elif _columnName == 'ST_D':
        self.statBlockStDpValueLabel.setText(_index.data())
      elif _columnName == 'ST_W':
        self.statBlockStWValueLabel.setText(_index.data())
      elif _columnName == 'ST_P':
        self.statBlockStPValueLabel.setText(_index.data())
      elif _columnName == 'ST_B':
        self.statBlockStBValueLabel.setText(_index.data())
      elif _columnName == 'ST_S':
        self.statBlockStSrsValueLabel.setText(_index.data())
    pass

  def resetForm(self):
    self.mainFilterGroupBox.resetFilter()
    self.dataTable.invalidateAllRows()

class CreatureEditorNewWidget(QWidget):
  def __init__(self):
    super().__init__()

    self.mainGridLayout = QGridLayout()
    self.groupBox = QGroupBox()
    self.groupBox.setTitle('Filters')
    groupBoxGridLayout = QGridLayout()
    button = QPushButton('Test')
    groupBoxGridLayout.addWidget(button, 0, 0)
    self.groupBox.setLayout(groupBoxGridLayout)
    self.mainGridLayout.addWidget(self.groupBox)

    self.setLayout(self.mainGridLayout)


class CreatureEditorExportWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Variables
    self._currentExportFilePath = ''

    # Header Label
    _headerLabel = QLabel('Export Creatures')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    # Search Result Table Group Box
    self.searchResultTable = qtw.DataTable()
    _searchResultGroupBox = self.defineSearchResultsGroupBox()

    # Filter Group Box
    self._mainFilterGroupBox = qtw.CreatureFilterGroupBox(title='Filters', applyFilterMethod=self.searchResultTable.filterTable, setCreatureModelMethod=self.searchResultTable.setDataModel, resetFormMethod=self.resetForm)

    # Preview Table Group Box
    self.previewTable = qtw.DataTable()
    _previewTableGroupBox = self.definePreviewTableGroupBox()

    # Export Settings Group Box
    _exportSettingsGroupBox = self.defineExportSettingsGroupBox()

    # Finish setup
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.addWidget(_headerLabel, 0, 0)
    _mainGridLayout.addWidget(self._mainFilterGroupBox, 1, 0, 1, 3)
    _mainGridLayout.addWidget(_searchResultGroupBox, 2, 0)
    _mainGridLayout.addWidget(_previewTableGroupBox, 2, 1)
    _mainGridLayout.addWidget(_exportSettingsGroupBox, 2, 2)
    self.setLayout(_mainGridLayout)

  def resetForm(self):
    self._mainFilterGroupBox.resetFilter()
    self.searchResultTable.clearFilter()
    self.previewTable.clearFilter()

  def defineSearchResultsGroupBox(self):
    _searchResultGroupBox = QGroupBox('Search Result')
    _searchResultGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    _searchResultGroupBoxLayout = QGridLayout()
    _searchResultGroupBoxLayout.setSpacing(15)

    # Add All To Export Button
    _addAllToExportButton = QPushButton('Add All To Export')
    _addAllToExportButton.setMinimumSize(150, 30)
    _addAllToExportButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _addAllToExportButton.clicked.connect(lambda clicked: self.addDataToPreviewTable(addSelection=False))

    # Add Selection To Export Button
    _addSelectionToExportButton = QPushButton('Add Selection To Export')
    _addSelectionToExportButton.setMinimumSize(195, 30)
    _addSelectionToExportButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _addSelectionToExportButton.clicked.connect(lambda clicked: self.addDataToPreviewTable(addSelection=True))

    # Clear Search Results Button
    _clearSearchResultButton = QPushButton('Clear')
    _clearSearchResultButton.setMinimumSize(80, 30)
    _clearSearchResultButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _clearSearchResultButton.clicked.connect(self.searchResultTable.clearFilter)

    # Search Result Table
    self.searchResultTable.addColumn(name='NAME', position=0, width=350, alignment=Qt.AlignmentFlag.AlignLeft)
    self.searchResultTable.addColumn(name='TYPE', position=1, width=150, alignment=Qt.AlignmentFlag.AlignLeft)
    self.searchResultTable.addColumn(name='CR', position=2, width=100, alignment=Qt.AlignmentFlag.AlignCenter)
    self.searchResultTable.addColumn(name='ALIGNMENT', position=3, width=150, alignment=Qt.AlignmentFlag.AlignLeft)
    self.searchResultTable.addColumn(name='ENVIRONMENT', position=4, width=350, alignment=Qt.AlignmentFlag.AlignLeft)
    self.searchResultTable.addColumn(name='SOURCE', position=5, width=350, alignment=Qt.AlignmentFlag.AlignLeft)

    # Finish Setup
    _searchResultGroupBoxLayout.setContentsMargins(10, 20, 10, 10)
    _searchResultGroupBoxLayout.addWidget(self.searchResultTable, 1, 0, 1, 4)
    _searchResultGroupBoxLayout.addWidget(_addAllToExportButton, 2, 0)
    _searchResultGroupBoxLayout.addWidget(_addSelectionToExportButton, 2, 1)
    _searchResultGroupBoxLayout.addWidget(_clearSearchResultButton, 2, 2)
    _searchResultGroupBox.setLayout(_searchResultGroupBoxLayout)
    _searchResultGroupBoxLayout.addItem(QSpacerItem(1000, 10), 2, 3)

    return _searchResultGroupBox

  def definePreviewTableGroupBox(self):
    _previewTableGroupBox = QGroupBox('Export Preview')
    _previewTableGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    _previewTableGroupBoxLayout = QGridLayout()
    _previewTableGroupBoxLayout.setSpacing(15)

    _removeFromExportButton = QPushButton('Remove Entry')
    _removeFromExportButton.setMinimumSize(130, 30)
    _removeFromExportButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _removeFromExportButton.clicked.connect(self.removeEntryFromExportTable)

    _clearExportTableButton = QPushButton('Clear')
    _clearExportTableButton.setMinimumSize(80, 30)
    _clearExportTableButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _clearExportTableButton.clicked.connect(self.previewTable.clearFilter)

    # Preview Table
    self.previewTable.addColumn(name='NAME', position=0, width=350, alignment=Qt.AlignmentFlag.AlignLeft)
    self.previewTable.addColumn(name='TYPE', position=1, width=150, alignment=Qt.AlignmentFlag.AlignLeft)
    self.previewTable.addColumn(name='CR', position=2, width=100, alignment=Qt.AlignmentFlag.AlignCenter)
    self.previewTable.addColumn(name='ALIGNMENT', position=3, width=150, alignment=Qt.AlignmentFlag.AlignLeft)
    self.previewTable.addColumn(name='ENVIRONMENT', position=4, width=350, alignment=Qt.AlignmentFlag.AlignLeft)
    self.previewTable.addColumn(name='SOURCE', position=5, width=350, alignment=Qt.AlignmentFlag.AlignLeft)

    _previewTableGroupBoxLayout.setContentsMargins(10, 20, 10, 10)
    _previewTableGroupBoxLayout.addWidget(self.previewTable, 1, 0, 1, 3)
    _previewTableGroupBoxLayout.addWidget(_removeFromExportButton, 2, 0)
    _previewTableGroupBoxLayout.addWidget(_clearExportTableButton, 2, 1)
    _previewTableGroupBoxLayout.addItem(QSpacerItem(1000, 10), 2, 2)
    _previewTableGroupBox.setLayout(_previewTableGroupBoxLayout)

    return _previewTableGroupBox

  def defineExportSettingsGroupBox(self):
    _exportSettingsGroupBox = QGroupBox('Export Settings')
    _exportSettingsGroupBox.setMinimumWidth(330)
    _exportSettingsGroupBoxMainLayout = QGridLayout()
    _exportSettingsGroupBoxMainLayout.setVerticalSpacing(20)
    _exportSettingsGroupBoxMainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    self.includeHeaderCheckBox = QCheckBox()
    self.includeHeaderCheckBox.setMinimumSize(30, 30)
    self.includeHeaderCheckBox.setStyleSheet(
      'QCheckBox::indicator::unchecked{border: 1px solid #777; color=white; width=15; height=15;} QCheckBox::indicator::checked{color=white; width=15; height=15;}')

    _chooseExportComboBox = QComboBox()
    _chooseExportComboBox.addItem('csv')
    _chooseExportComboBox.addItem('tsv')
    _chooseExportComboBox.addItem('json')

    _chooseExportFileButton = QPushButton('Choose Export File')
    _chooseExportFileButton.clicked.connect(self.chooseExportFile)

    self.exportFilenameLabel = QLabel(self._currentExportFilePath)

    _exportButton = QPushButton('Export')
    _exportButton.clicked.connect(self.exportData)

    _exportSettingsGroupBoxMainLayout.addWidget(QLabel('Include Header:'), 0, 0)
    _exportSettingsGroupBoxMainLayout.addWidget(self.includeHeaderCheckBox, 0, 1)
    _exportSettingsGroupBoxMainLayout.addWidget(QLabel('Export Format: '), 1, 0)
    _exportSettingsGroupBoxMainLayout.addWidget(_chooseExportComboBox, 1, 1)
    _exportSettingsGroupBoxMainLayout.addWidget(QLabel('Export File: '), 2, 0)
    _exportSettingsGroupBoxMainLayout.addWidget(_chooseExportFileButton, 2, 1)
    _exportSettingsGroupBoxMainLayout.addWidget(self.exportFilenameLabel, 4, 0, 1, 2)
    _exportSettingsGroupBoxMainLayout.addWidget(_exportButton, 5, 0, 1, 2)
    _exportSettingsGroupBox.setLayout(_exportSettingsGroupBoxMainLayout)

    return _exportSettingsGroupBox

  def chooseExportFile(self):
    _fileDialog = QFileDialog()
    _fileDialog.setNameFilter('*.csv *.json')
    _fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    _filename = []

    if _fileDialog.exec_():
      _filename = _fileDialog.selectedFiles()
      self._currentExportFilePath = _filename[0]
      self.exportFilenameLabel.setText(self._currentExportFilePath)

  def addDataToPreviewTable(self, addSelection):
    _selectedRows = self.searchResultTable.getRows(onlySelectedRows=addSelection)
    self.previewTable.addDataToTable(_selectedRows)

  def exportData(self):
    _fieldNames = []
    for _currentColumn in range(self.previewTable.columnCount()):
      _fieldNames.append(self.previewTable.horizontalHeaderItem(_currentColumn).text())

    _dataRows = []
    for _currentRow in range(self.previewTable.rowCount()):
      _row = {}
      for _currentColumn in range(self.previewTable.columnCount()):
        _value = self.previewTable.item(_currentRow, _currentColumn).text()
        _fieldName = self.previewTable.horizontalHeaderItem(_currentColumn).text()
        _row[_fieldName] = _value
      _dataRows.append(_row)

    with open(file=self.exportFilenameLabel.text(), mode='w', newline='') as _csvfile:
      _csvDictWriter = csv.DictWriter(_csvfile, delimiter=';', fieldnames=_fieldNames, quoting=csv.QUOTE_NONE, escapechar='\\')

      if self.includeHeaderCheckBox.isChecked():
        _csvDictWriter.writeheader()

      _csvDictWriter.writerows(_dataRows)

  def removeEntryFromExportTable(self):
    _items = self.previewTable.selectedItems()
    for _item in _items:
      self.previewTable.removeRow(_item.row())



class CreatureEditor(QWidget):
  def __init__(self):
    super().__init__()

    self.newButton = QPushButton("New")
    self.editButton = QPushButton("Edit")
    self.viewButton = QPushButton("View")
    self.importButton = QPushButton("Import")
    self.exportButton = QPushButton("Export")

    self.menuWidget = QWidget()
    self.contentStackedWidget = QStackedWidget()

    self.creatureEditorNewWidget = CreatureEditorNewWidget()
    self.creatureEditorListWidget = CreatureEditorViewWidget()
    self.creatureEditorImportWidget = CreatureEditorImportWidget()
    self.creatureEditorExportWidget = CreatureEditorExportWidget()

    self.mainGridLayout = QGridLayout()

    self.defineMenuLayout()
    self.defineContentStackedWidget()

    self.mainGridLayout.addWidget(self.menuWidget, 0, 0)
    self.mainGridLayout.addWidget(self.contentStackedWidget, 0, 1)
    self.setLayout(self.mainGridLayout)

  def defineMenuLayout(self):
    self.newButton.clicked.connect(lambda clicked: self.changeWidget(self.creatureEditorNewWidget))
    self.importButton.clicked.connect(lambda clicked: self.changeWidget(self.creatureEditorImportWidget))
    self.viewButton.clicked.connect(lambda clicked: self.changeWidget(self.creatureEditorListWidget))
    self.exportButton.clicked.connect(lambda clicked: self.changeWidget(self.creatureEditorExportWidget))

    menuLayout = QVBoxLayout()
    menuLayout.addWidget(self.newButton, 0)
    menuLayout.addWidget(self.editButton)
    menuLayout.addWidget(self.viewButton)
    menuLayout.addWidget(self.importButton)
    menuLayout.addWidget(self.exportButton)
    menuLayout.setSpacing(15)
    menuLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    self.menuWidget.setLayout(menuLayout)

  def defineContentStackedWidget(self):
    self.contentStackedWidget.addWidget(self.creatureEditorImportWidget)
    self.contentStackedWidget.addWidget(self.creatureEditorListWidget)
    self.contentStackedWidget.addWidget(self.creatureEditorNewWidget)
    self.contentStackedWidget.addWidget(self.creatureEditorExportWidget)
    self.contentStackedWidget.setCurrentIndex(1)

  def changeWidget(self, widget):
    self.contentStackedWidget.setCurrentWidget(widget)
