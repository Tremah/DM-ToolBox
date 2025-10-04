import csv as csv
import math
import random

import pyperclip as pclip
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColorConstants
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
  QTableWidgetItem,
  QListWidget,
  QListWidgetItem,
  QGroupBox,
  QLineEdit,
  QComboBox,
  QCheckBox,
  QDialog,
  QFileDialog,
  QDialogButtonBox
)

import database as db
import qt_wrapper as qtw


class EncounterTableWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Variables
    self._currentExportFilePath = ''

    # Header Label
    _headerLabel = QLabel('Encounter Table Generator')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    # Search Result Table Group Box
    self.searchResultTable = qtw.DataTable()
    _searchResultGroupBox = self.defineSearchResultsGroupBox()

    # Filter Group Box
    self._mainFilterGroupBox = qtw.CreatureFilterGroupBox(title='Filters', applyFilterMethod=self.searchResultTable.filterTable, setCreatureModelMethod=self.searchResultTable.setDataModel, resetFormMethod=self.resetForm)

    # Encounter Table Creation Setting Group Box
    self.addDieColumnToEncounterTableCheckBox = QCheckBox()
    self.autoPopulateDieColumnCheckBox = QCheckBox()
    self.dieAmountComboBox = QComboBox()
    self.dieComboBox = QComboBox()
    self.supplyDieRangesAsProbabilitiesCheckBox = QCheckBox()
    self.generateDieRangesFromProbabilitiesButton = QPushButton('Generate Die Ranges')
    self.includeSpecialCheckBox = QCheckBox()
    self.includeRollTwoAndCombineCheckbox = QCheckBox()

    _encounterCreationSettingsGroupBox = self.defineEncounterCreationSettingsGroupBox()

    # Filter and settings row layout
    self.filterCreationSettingsRowLayout = QHBoxLayout()
    self.filterCreationSettingsRowLayout.setSpacing(30)
    self.filterCreationSettingsRowLayout.addWidget(self._mainFilterGroupBox)
    self.filterCreationSettingsRowLayout.addWidget(_encounterCreationSettingsGroupBox)

    # Encounter Table Group Box
    self.encounterTable = qtw.DataTable(lastSectionStretch=True)
    _encounterTableGroupBox = self.defineEncounterTableGroupBox()

    #Save Table Group Box
    self.tableNameLineEdit = QLineEdit()
    self.tableNameLineEdit.setPlaceholderText('Table name here...')
    _saveTableButton = QPushButton('Save Table')
    _saveTableButton.setMaximumWidth(100)
    _saveTableButton.clicked.connect(self.writeTableToDatabase)

    self.saveTableGroupBoxLayout = QGridLayout()
    self.saveTableGroupBoxLayout.setSpacing(15)
    self.saveTableGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0)
    self.saveTableGroupBoxLayout.addWidget(QLabel('Table Name: '), 1, 0)
    self.saveTableGroupBoxLayout.addWidget(self.tableNameLineEdit, 1, 1)
    self.saveTableGroupBoxLayout.addWidget(_saveTableButton, 2, 0, 1, 2)

    _saveTableGroupBox = QGroupBox('Save')
    _saveTableGroupBox.setMaximumWidth(500)
    _saveTableGroupBox.setLayout(self.saveTableGroupBoxLayout)

    #Load Table Group Box
    self.loadTableComboBox = QComboBox()
    self.loadDataIntoTableComboBox(combobox=self.loadTableComboBox)
    self.loadTableButton = QPushButton('Load Table')
    self.loadTableButton.setMaximumWidth(100)
    self.loadTableButton.clicked.connect(self.handleLoadTableButton)

    self.loadTableGroupBoxLayout = QGridLayout()
    self.loadTableGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0)
    self.loadTableGroupBoxLayout.addWidget(QLabel('Table: '), 1, 0)
    self.loadTableGroupBoxLayout.addWidget(self.loadTableComboBox, 1, 1)
    self.loadTableGroupBoxLayout.addWidget(self.loadTableButton, 2, 0, 1, 2)

    _loadTableGroupBox = QGroupBox('Load')
    _loadTableGroupBox.setMaximumWidth(500)
    _loadTableGroupBox.setLayout(self.loadTableGroupBoxLayout)

    #Delete Table Group Box
    self.deleteTableComboBox = QComboBox()
    self.loadDataIntoTableComboBox(combobox=self.deleteTableComboBox)
    self.deleteTableButton = QPushButton('Delete Table')
    self.deleteTableButton.setMaximumWidth(100)
    self.deleteTableButton.clicked.connect(self.handleDeleteTableButton)

    self.deleteTableGroupBoxLayout = QGridLayout()
    self.deleteTableGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0)
    self.deleteTableGroupBoxLayout.addWidget(QLabel('Table: '), 1, 0)
    self.deleteTableGroupBoxLayout.addWidget(self.deleteTableComboBox, 1, 1)
    self.deleteTableGroupBoxLayout.addWidget(self.deleteTableButton, 2, 0, 1, 2)

    _deleteTableGroupBox = QGroupBox('Delete')
    _deleteTableGroupBox.setMaximumWidth(500)
    _deleteTableGroupBox.setLayout(self.deleteTableGroupBoxLayout)

    # Export Settings Group Box
    self.includeHeaderCheckBox = QCheckBox()
    self.exportFilenameLabel = QLabel()
    self.exportToComboBox = QComboBox()
    self.outputWidget = QWidget()
    _exportSettingsGroupBox = self.defineExportSettingsGroupBox()
    _exportSettingsGroupBox.setMaximumWidth(500)

    # Log
    self.logList = QListWidget()
    self.logList.setFont(QFont('Ubuntu Mono', 10))
    self.logList.setWordWrap(True)

    _clearLogButton = QPushButton('Clear')
    _clearLogButton.setMaximumSize(80, 30)
    _clearLogButton.clicked.connect(self.logList.clear())

    _logListGroupBoxLayout = QVBoxLayout()
    _logListGroupBoxLayout.addWidget(self.logList)
    _logListGroupBoxLayout.addWidget(_clearLogButton)
    _logListGroupBoxLayout.setContentsMargins(15, 15, 15, 15)
    _logListGroupBox = QGroupBox('Log')
    _logListGroupBox.setMaximumWidth(500)
    _logListGroupBox.setLayout(_logListGroupBoxLayout)

    # Finish setup
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setColumnStretch(0, 1)
    _mainGridLayout.setColumnStretch(1, 2)
    _mainGridLayout.setColumnStretch(2, 1)
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.addWidget(_headerLabel, 0, 0)
    _mainGridLayout.addLayout(self.filterCreationSettingsRowLayout, 1, 0, 1, 3)
    _mainGridLayout.addWidget(_searchResultGroupBox, 2, 0, 5, 1)
    _mainGridLayout.addWidget(_encounterTableGroupBox, 2, 1, 5, 1)
    _mainGridLayout.addWidget(_saveTableGroupBox, 2, 2)
    _mainGridLayout.addWidget(_loadTableGroupBox, 3, 2)
    _mainGridLayout.addWidget(_deleteTableGroupBox, 4, 2)
    _mainGridLayout.addWidget(_exportSettingsGroupBox, 5, 2)
    _mainGridLayout.addWidget(_logListGroupBox, 6, 2)
    self.setLayout(_mainGridLayout)

  def loadDataIntoTableComboBox(self, combobox):
    _tablesNames = db.query('select distinct TABLE_NAME as NAME from ENCOUNTER_TABLE')

    combobox.clear()
    for _table in _tablesNames:
      combobox.addItem(_table['NAME'])

  def resetForm(self):
    self._mainFilterGroupBox.resetFilter()
    self.searchResultTable.clearFilter()
    self.encounterTable.invalidateAllRows()

  def handleAddDieColumnToEncounterTableCheckBoxStateChanged(self, checked):
    if checked is True:
      self.autoPopulateDieColumnCheckBox.setEnabled(True)
      if not self.encounterTable.columnExists('DIE'):
        self.encounterTable.addColumn(name='DIE', position=0, width=60, alignment=Qt.AlignmentFlag.AlignCenter)
    else:
      self.autoPopulateDieColumnCheckBox.setChecked(False)
      self.autoPopulateDieColumnCheckBox.setEnabled(False)
      if not self.supplyDieRangesAsProbabilitiesCheckBox.isChecked():
        self.encounterTable.removeColumn(name='DIE')

  def handleAutoPopulateDieColumnCheckBoxStateChanged(self):
    _checked = self.autoPopulateDieColumnCheckBox.isChecked()

    self.dieAmountComboBox.setEnabled(_checked)
    self.dieComboBox.setEnabled(_checked)

    if _checked:
      self.handleDieComboBoxIndexChanged()
    else:
      self.encounterTable.clearColumn('DIE')

  def handleDieComboBoxIndexChanged(self):
    _encounterTableRowCount = self.encounterTable.rowCount()
    if self.dieComboBox.currentIndex() == -1 or _encounterTableRowCount == 0:
      return

    _selectedDie = self.dieComboBox.currentText()
    _numberOfDice = int(self.dieAmountComboBox.currentText())
    _dieFaces = db.query(f'select * from DIE where NAME = ?', args=(_selectedDie,), one=True)['FACES']
    if _encounterTableRowCount > 0 and _encounterTableRowCount > _numberOfDice * _dieFaces:
      self.addEntryToLog(f'Selected die ({_numberOfDice}{_selectedDie}) has to few faces.')
      return

    _dieRanges = self.generateDieRanges(numberOfDataItems=_encounterTableRowCount, numberOfDice=_numberOfDice, dieFaces=_dieFaces)

    _dieColumnIndex = self.encounterTable.getColumnIndexFromName('DIE')
    #self.encounterTable.horizontalHeaderItem(_dieColumnIndex).setText(f'1{_selectedDie}')

    for _currentRow in range(_encounterTableRowCount):
      _item = QTableWidgetItem(_dieRanges[_currentRow])
      _item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
      self.encounterTable.setItem(_currentRow, _dieColumnIndex, _item)

  def handleDieRangesProbabilitiesCheckBoxStateChanged(self, checked, dieColumnPresent, position):
    _position = position
    if not dieColumnPresent:
      _position = 0

    if checked:
      if not self.encounterTable.columnExists('PROBABILITY'):
        self.encounterTable.addColumn(name='PROBABILITY', position=_position, width=130, alignment=Qt.AlignmentFlag.AlignCenter)
      self.generateDieRangesFromProbabilitiesButton.setEnabled(True)

      if not self.encounterTable.columnExists('DIE'):
        self.encounterTable.addColumn(name='DIE', position=0, width=60, alignment=Qt.AlignmentFlag.AlignCenter)

      self.addDieColumnToEncounterTableCheckBox.setChecked(True)
    else:
      self.generateDieRangesFromProbabilitiesButton.setEnabled(False)
      self.encounterTable.removeColumn(name='PROBABILITY')
      if self.encounterTable.columnExists('DIE') and not self.addDieColumnToEncounterTableCheckBox.isChecked():
        self.encounterTable.removeColumn(name='DIE')

  def handleIncludeSpecialCheckboxStateChanged(self):
    _checked = self.includeSpecialCheckBox.isChecked()

    if _checked:
      self.encounterTable.setRowCount(self.encounterTable.rowCount() + 1)
      self.encounterTable.setItem(self.encounterTable.rowCount() - 1, self.encounterTable.getColumnIndexFromName('NAME'), QTableWidgetItem('Special'))
    else:
      for _row in range(self.encounterTable.rowCount()):
        if self.encounterTable.item(_row, self.encounterTable.getColumnIndexFromName('NAME')).text().upper() == 'SPECIAL':
          self.encounterTable.removeRow(_row)
          break

  def handleIncludeRollTowAndCombineCheckboxStateChanged(self):
    _checked = self.includeRollTwoAndCombineCheckbox.isChecked()

    if _checked:
      self.encounterTable.setRowCount(self.encounterTable.rowCount() + 1)
      self.encounterTable.setItem(self.encounterTable.rowCount() - 1, self.encounterTable.getColumnIndexFromName('NAME'), QTableWidgetItem('Roll Two And Combine'))
    else:
      for _row in range(self.encounterTable.rowCount()):
        if self.encounterTable.item(_row, self.encounterTable.getColumnIndexFromName('NAME')).text().upper() == 'ROLL TWO AND COMBINE':
          self.encounterTable.removeRow(_row)
          break

  def handleLoadTableButton(self):
    _tableToLoad = self.loadTableComboBox.currentText()

    _data = db.query(f'''
      select
        DIE_RANGE as DIE,
        PROBABILITY,
        CREATURE_NAME as NAME,
        CREATURE_TYPE as TYPE,
        CREATURE_CR as CR,
        CREATURE_ALIGNMENT as ALIGNMENT,
        CREATURE_ENVIRONMENT as ENVIRONMENT,
        CREATURE_SOURCE as SOURCE
      from
        ENCOUNTER_TABLE
      where
        TABLE_NAME == "{_tableToLoad}"''')

    self.encounterTable.addDataToTable(rows=_data, clear=True)

  def handleDeleteTableButton(self):
    _tableToDrop = self.deleteTableComboBox.currentText()

    _reviewDialog = QDialog()
    _reviewDialog.setWindowTitle(f'Delete Table {_tableToDrop}?')

    _question = QLabel(f'Do you really want to delete the encounter table "{_tableToDrop}"?')
    _dialogButtons = QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
    _buttonBox = QDialogButtonBox(_dialogButtons)
    _buttonBox.accepted.connect(_reviewDialog.accept)
    _buttonBox.rejected.connect(_reviewDialog.reject)

    _reviewDialogLayout = QGridLayout()
    _reviewDialogLayout.addWidget(_question, 0, 0)
    _reviewDialogLayout.addWidget(_buttonBox, 1, 0)
    _reviewDialog.setLayout(_reviewDialogLayout)
    _reviewDialog.exec()

    if _reviewDialog.result() == 1:
      _result = db.execute(f'delete from ENCOUNTER_TABLE where TABLE_NAME = "{_tableToDrop}"', commit=True)

    self.loadDataIntoTableComboBox(combobox=self.loadTableComboBox)
    self.loadDataIntoTableComboBox(combobox=self.deleteTableComboBox)

  def generateDieRanges(self, numberOfDataItems, numberOfDice, dieFaces):
    _rangeDistancePerItem = ((numberOfDice * dieFaces) - (numberOfDice - 1)) // numberOfDataItems
    _remainder = ((numberOfDice * dieFaces) - (numberOfDice - 1)) % numberOfDataItems

    _remainderIndexList = []
    _i = 0
    while _i < _remainder:
      _indexForRemainder = random.randint(0, numberOfDataItems - 1)
      if not _indexForRemainder in _remainderIndexList:
        _remainderIndexList.append(_indexForRemainder)
        _i += 1

    _rangeStr = ''
    _rangeStart = numberOfDice
    _dieRanges = []
    for i in range(numberOfDataItems):
      _rangeEnd = _rangeStart + _rangeDistancePerItem - 1
      if i in _remainderIndexList:
        _rangeEnd += 1

      if _rangeStart == _rangeEnd:
        _rangeStr = str(_rangeStart)
      else:
        _rangeStr = f'{_rangeStart}-{_rangeEnd}'

      _dieRanges.append(_rangeStr)
      _rangeStart = _rangeEnd + 1

    return _dieRanges

  def generateDieRangesFromProbabilities(self):
    _probabilities = self.encounterTable.getRows(selectColumns=['PROBABILITY'])

    _sum = 0
    for _item in _probabilities:
      if _item != '':
        _sum += int(_item)

    if _sum < 100:
      self.addEntryToLog(f'Probabilities ({_sum}) are less than 100')
    elif _sum > 100:
      self.addEntryToLog(f'Probabilities ({_sum}) are greater than 100')

    _dieFaces = 100
    _numberOfDice = math.ceil(len(_probabilities) / _dieFaces)
    _totalDieValues = _numberOfDice * _dieFaces
    _dieRanges = []
    _dieRangeStart = _numberOfDice
    _dieRangeEnd = 0
    for _prob in _probabilities:
      if _prob == '':
        _dieRangeStr = ''
      else:
        _dieRangeDistance = math.floor(_totalDieValues * (int(_prob)/100))
        _dieRangeEnd = _dieRangeEnd + _dieRangeDistance
        _dieRangeEnd = min(_dieRangeEnd, _totalDieValues)
        _dieRangeStr = f'{_dieRangeStart}-{_dieRangeEnd}'
        _dieRangeStart = _dieRangeEnd + 1

      _dieRanges.append(_dieRangeStr)

    _dieColumnIndex = self.encounterTable.getColumnIndexFromName('DIE')

    for _currentRow in range(self.encounterTable.rowCount()):
      _item = QTableWidgetItem(_dieRanges[_currentRow])
      _item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
      self.encounterTable.setItem(_currentRow, _dieColumnIndex, _item)

  def addEntryToLog(self, text, color=None):
    _item = QListWidgetItem(text)
    if color is not None:
      _item.setForeground(color)

    self.logList.addItem(_item)

  def modifyDataTableColumns(self, table, add, position, title):
    _data = table.getRows()

    if add:
      table.setColumnCount(table.columnCount() + 1)
      # Gather data from table to prepare moving columns to make space for the new column
      for _newColumn in range(table.columnCount() - 1, position, -1):
        _oldColumnName = table.horizontalHeaderItem(_newColumn - 1).text()
        _currentRowIndex = 0
        table.setHorizontalHeaderItem(_newColumn, QTableWidgetItem(_oldColumnName))

        for _dataRow in _data:
          _itemText = ''
          if _oldColumnName.upper() in ('DIE', 'PROBABILITY'):
            _itemText = ''
          else:
            _itemText = _dataRow[_oldColumnName]
          _newItem = QTableWidgetItem(_itemText)

          if _oldColumnName == 'CR':
            _newItem.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

          table.setItem(_currentRowIndex, _newColumn, _newItem)
          _currentRowIndex += 1
        table.setColumnWidth(_newColumn, table.columnWidths[_oldColumnName])

      table.horizontalHeaderItem(position).setText(title.upper())
      _currentRowIndex = 0
      for _currentRowIndex in range(table.rowCount()):
        table.item(_currentRowIndex, position).setText('')
      table.setColumnWidth(position, table.columnWidths[title.upper()])
    else:
      table.removeColumn(position)

  def copyToClipboard(self, text):
    pclip.copy(text)

  def addDataToEncounterTable(self, addSelection):
    _selectedRows = self.searchResultTable.getRows(onlySelectedRows=addSelection)

    self.encounterTable.addDataToTable(_selectedRows)

  def chooseExportFile(self):
    _fileDialog = QFileDialog()
    _fileDialog.setNameFilter('*.csv *.json')
    _fileDialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    _filename = []

    if _fileDialog.exec_():
      _filename = _fileDialog.selectedFiles()
      self._currentExportFilePath = _filename[0]
      self.exportFilenameLabel.setText(self._currentExportFilePath)

  def exportTable(self):
    _fieldNames = []
    for _currentColumn in range(self.encounterTable.columnCount()):
      _fieldNames.append(self.encounterTable.horizontalHeaderItem(_currentColumn).text())

    if self.exportToComboBox.currentText() == 'File':
      _dataRows = []
      for _currentRow in range(self.encounterTable.rowCount()):
        _row = {}
        for _currentColumn in range(self.encounterTable.columnCount()):
          _value = self.encounterTable.item(_currentRow, _currentColumn).text()
          _fieldName = self.encounterTable.horizontalHeaderItem(_currentColumn).text()
          _row[_fieldName] = _value
        _dataRows.append(_row)

      with open(file=self.exportFilenameLabel.text(), mode='w', newline='') as _csvfile:
        _csvDictWriter = csv.DictWriter(_csvfile, delimiter=';', fieldnames=_fieldNames, quoting=csv.QUOTE_NONE,
                                        escapechar='\\')

        if self.includeHeaderCheckBox.isChecked():
          _csvDictWriter.writeheader()

        _csvDictWriter.writerows(_dataRows)
    elif self.exportToComboBox.currentText() == 'Output Window':
      _outputString = ''
      if self.includeHeaderCheckBox.isChecked():
        _outputString = ';'.join(_fieldNames) + '\n'

      for _currentRow in range(self.encounterTable.rowCount()):
        for _currentColumn in range(self.encounterTable.columnCount()):
          if _currentColumn != 0:
            _outputString = _outputString + ';'
          if self.encounterTable.item(_currentRow, _currentColumn) is not None:
            _outputString = _outputString + self.encounterTable.item(_currentRow, _currentColumn).text()
        if _currentRow != self.encounterTable.rowCount() - 1:
          _outputString = _outputString + '\n'

      self.outputWidget.findChildren(QPlainTextEdit)[0].setPlainText(_outputString)
      self.outputWidget.show()

  def writeTableToDatabase(self):
    if self.tableNameLineEdit.text() == '':
      self.addEntryToLog('No table name supplied!', color=QColorConstants.Red)
      return

    if self.encounterTable.rowCount() == 0:
      self.addEntryToLog('No data in encounter table!')
      return

    _tableName = self.tableNameLineEdit.text()

    _dieColumnExists = False
    _probColumnExists = False
    if self.encounterTable.getColumnIndexFromName('DIE') is not None:
      _dieColumnExists = True
    if self.encounterTable.getColumnIndexFromName('PROBABILITY') is not None:
      _probColumnExists = True

    for _row in self.encounterTable.getRows():
      _dieRangeValue = ''
      _probValue = ''
      if _dieColumnExists:
        _dieRangeValue = _row['DIE']
      if _probColumnExists:
        _probValue = _row['PROBABILITY']

      db.execute(statement='''
        insert into ENCOUNTER_TABLE("TABLE_NAME", "DIE_RANGE", "PROBABILITY", "CREATURE_NAME", "CREATURE_TYPE", "CREATURE_CR", "CREATURE_ALIGNMENT", "CREATURE_ENVIRONMENT", "CREATURE_SOURCE")
        values(?, ?, ?, ?, ?, ?, ?, ?, ?)''', args=(_tableName, _dieRangeValue, _probValue, _row['NAME'], _row['TYPE'], _row['CR'], _row['ALIGNMENT'], _row['ENVIRONMENT'], _row['SOURCE']), commit=True)

    #Refresh relevant widgets
    self.loadDataIntoTableComboBox(combobox=self.loadTableComboBox)
    self.loadDataIntoTableComboBox(combobox=self.deleteTableComboBox)

  def removeEntryFromEncounterTable(self):
    _items = self.encounterTable.selectedItems()
    for _item in _items:
      self.encounterTable.removeRow(_item.row())

  def addEmptyRowToEncounterTable(self):
    self.encounterTable.setRowCount(self.encounterTable.rowCount() + 1)

  def defineEncounterCreationSettingsGroupBox(self):
    self.addDieColumnToEncounterTableCheckBox.setMinimumSize(30, 30)
    self.addDieColumnToEncounterTableCheckBox.checkStateChanged.connect(lambda: self.handleAddDieColumnToEncounterTableCheckBoxStateChanged(checked=self.addDieColumnToEncounterTableCheckBox.isChecked()))
    self.addDieColumnToEncounterTableCheckBox.setStyleSheet('QCheckBox::indicator::unchecked{border: 1px solid #777; color=white; width=15; height=15;} QCheckBox::indicator::checked{color=white; width=15; height=15;}')

    self.autoPopulateDieColumnCheckBox.setMinimumSize(30, 30)
    self.autoPopulateDieColumnCheckBox.setStyleSheet('QCheckBox::indicator::unchecked{border: 1px solid #777; color=white; width=15; height=15;} QCheckBox::indicator::checked{color=white; width=15; height=15;}')
    self.autoPopulateDieColumnCheckBox.checkStateChanged.connect(self.handleAutoPopulateDieColumnCheckBoxStateChanged)
    self.autoPopulateDieColumnCheckBox.setEnabled(False)

    self.dieAmountComboBox.setEnabled(False)
    for i in range(20):
      self.dieAmountComboBox.addItem(str(i + 1))
    self.dieAmountComboBox.currentIndexChanged.connect(self.handleDieComboBoxIndexChanged)

    self.dieComboBox.setEnabled(False)
    self.dieComboBox.setMaximumWidth(100)

    _dice = db.query('select * from DIE')
    self.dieComboBox.setPlaceholderText('Choose die')
    for _die in _dice:
      self.dieComboBox.addItem(_die['NAME'])
    self.dieComboBox.currentIndexChanged.connect(self.handleDieComboBoxIndexChanged)

    self.supplyDieRangesAsProbabilitiesCheckBox.setMinimumSize(30, 30)
    self.supplyDieRangesAsProbabilitiesCheckBox.checkStateChanged.connect(lambda: self.handleDieRangesProbabilitiesCheckBoxStateChanged(checked=self.supplyDieRangesAsProbabilitiesCheckBox.isChecked(),
                                                                            dieColumnPresent=self.addDieColumnToEncounterTableCheckBox.isChecked(),
                                                                            position=1))

    self.supplyDieRangesAsProbabilitiesCheckBox.setStyleSheet('QCheckBox::indicator::unchecked{border: 1px solid #777; color=white; width=15; height=15;} QCheckBox::indicator::checked{color=white; width=15; height=15;}')
    self.generateDieRangesFromProbabilitiesButton.setMaximumWidth(200)
    self.generateDieRangesFromProbabilitiesButton.clicked.connect(self.generateDieRangesFromProbabilities)
    self.generateDieRangesFromProbabilitiesButton.setEnabled(False)

    self.includeSpecialCheckBox.setStyleSheet('QCheckBox::indicator::unchecked{border: 1px solid #777; color=white; width=15; height=15;} QCheckBox::indicator::checked{color=white; width=15; height=15;}')
    self.includeSpecialCheckBox.stateChanged.connect(self.handleIncludeSpecialCheckboxStateChanged)
    self.includeRollTwoAndCombineCheckbox.setStyleSheet('QCheckBox::indicator::unchecked{border: 1px solid #777; color=white; width=15; height=15;} QCheckBox::indicator::checked{color=white; width=15; height=15;}')
    self.includeRollTwoAndCombineCheckbox.stateChanged.connect(self.handleIncludeRollTowAndCombineCheckboxStateChanged)

    _encounterCreationSettingsGroupBoxLayout = QGridLayout()
    _encounterCreationSettingsGroupBoxLayout.setSpacing(10)
    _encounterCreationSettingsGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    _encounterCreationSettingsGroupBoxLayout.addItem(QSpacerItem(10, 15), 0, 0)
    _encounterCreationSettingsGroupBoxLayout.addWidget(QLabel('Add Die Column To Encounter Table:'), 1, 0)
    _encounterCreationSettingsGroupBoxLayout.addWidget(self.addDieColumnToEncounterTableCheckBox, 1, 1, 1, 3)
    _encounterCreationSettingsGroupBoxLayout.addWidget(QLabel('Auto Populate Die Column:'), 2, 0)
    _encounterCreationSettingsGroupBoxLayout.addWidget(self.autoPopulateDieColumnCheckBox, 2, 1)
    _encounterCreationSettingsGroupBoxLayout.addWidget(self.dieAmountComboBox, 2, 2)
    _encounterCreationSettingsGroupBoxLayout.addWidget(self.dieComboBox, 2, 3)
    _encounterCreationSettingsGroupBoxLayout.addWidget(QLabel('Supply Die Ranges As Probabilities:'), 3, 0)
    _encounterCreationSettingsGroupBoxLayout.addWidget(self.supplyDieRangesAsProbabilitiesCheckBox, 3, 1)
    _encounterCreationSettingsGroupBoxLayout.addWidget(self.generateDieRangesFromProbabilitiesButton, 3, 2, 1, 2)
    _encounterCreationSettingsGroupBoxLayout.addWidget(QLabel('Include Special Row:'), 4, 0)
    _encounterCreationSettingsGroupBoxLayout.addWidget(self.includeSpecialCheckBox, 4, 1)
    _encounterCreationSettingsGroupBoxLayout.addWidget(QLabel('Include Roll Two And Combine Row:'), 5, 0)
    _encounterCreationSettingsGroupBoxLayout.addWidget(self.includeRollTwoAndCombineCheckbox, 5, 1)

    _encounterCreationSettingsGroupBox = QGroupBox('Settings')
    _encounterCreationSettingsGroupBox.setMaximumSize(500, 350)
    _encounterCreationSettingsGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    _encounterCreationSettingsGroupBox.setLayout(_encounterCreationSettingsGroupBoxLayout)

    return _encounterCreationSettingsGroupBox

  def defineSearchResultsGroupBox(self):
    _searchResultGroupBox = QGroupBox('Search Result')
    _searchResultGroupBoxLayout = QGridLayout()
    _searchResultGroupBoxLayout.setSpacing(15)
    _searchResultGroupBox.setMinimumWidth(800)

    # Add All To Export Button
    _addAllToEncounterButton = QPushButton('Add All To Export')
    _addAllToEncounterButton.setMaximumSize(150, 30)
    _addAllToEncounterButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _addAllToEncounterButton.clicked.connect(lambda clicked: self.addDataToEncounterTable(addSelection=False))

    # Add Selection To Export Button
    _addSelectionToEncounterButton = QPushButton('Add Selection To Export')
    _addSelectionToEncounterButton.setMaximumSize(195, 30)
    _addSelectionToEncounterButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _addSelectionToEncounterButton.clicked.connect(lambda clicked: self.addDataToEncounterTable(addSelection=True))

    # Clear Search Results Button
    _clearSearchResultButton = QPushButton('Clear')
    _clearSearchResultButton.setMaximumSize(80, 30)
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
    _searchResultGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0)
    _searchResultGroupBoxLayout.addWidget(_addAllToEncounterButton, 1, 0)
    _searchResultGroupBoxLayout.addWidget(_addSelectionToEncounterButton, 1, 1)
    _searchResultGroupBoxLayout.addWidget(_clearSearchResultButton, 1, 2)
    _searchResultGroupBoxLayout.addWidget(self.searchResultTable, 2, 0, 1, 4)
    _searchResultGroupBox.setLayout(_searchResultGroupBoxLayout)

    return _searchResultGroupBox

  def defineEncounterTableGroupBox(self):
    _encounterTableGroupBox = QGroupBox('Encounter Table')
    _encounterTableGroupBoxLayout = QGridLayout()
    _encounterTableGroupBoxLayout.setSpacing(15)

    _addEmptyRowToEncounterButton = QPushButton('Add Empty Row')
    _addEmptyRowToEncounterButton.setMaximumSize(130, 30)
    _addEmptyRowToEncounterButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _addEmptyRowToEncounterButton.clicked.connect(self.addEmptyRowToEncounterTable)

    _removeFromEncounterButton = QPushButton('Remove Entry')
    _removeFromEncounterButton.setMaximumSize(130, 30)
    _removeFromEncounterButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _removeFromEncounterButton.clicked.connect(self.removeEntryFromEncounterTable)

    _clearEncounterTableButton = QPushButton('Clear')
    _clearEncounterTableButton.setMaximumSize(80, 30)
    _clearEncounterTableButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
    _clearEncounterTableButton.clicked.connect(self.encounterTable.clearFilter)

    # Encounter Table
    self.encounterTable.addColumn(name='NAME', position=0, width=350, alignment=Qt.AlignmentFlag.AlignLeft)
    self.encounterTable.addColumn(name='TYPE', position=1, width=150, alignment=Qt.AlignmentFlag.AlignLeft)
    self.encounterTable.addColumn(name='CR', position=2, width=100, alignment=Qt.AlignmentFlag.AlignCenter)
    self.encounterTable.addColumn(name='ALIGNMENT', position=3, width=150, alignment=Qt.AlignmentFlag.AlignLeft)
    self.encounterTable.addColumn(name='ENVIRONMENT', position=4, width=350, alignment=Qt.AlignmentFlag.AlignLeft)
    self.encounterTable.addColumn(name='SOURCE', position=5, width=350, alignment=Qt.AlignmentFlag.AlignLeft)

    _encounterTableGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0)
    _encounterTableGroupBoxLayout.addWidget(_addEmptyRowToEncounterButton, 1, 0)
    _encounterTableGroupBoxLayout.addWidget(_removeFromEncounterButton, 1, 1)
    _encounterTableGroupBoxLayout.addWidget(_clearEncounterTableButton, 1, 2)
    _encounterTableGroupBoxLayout.addWidget(self.encounterTable, 2, 0, 1, 4)
    _encounterTableGroupBox.setLayout(_encounterTableGroupBoxLayout)

    return _encounterTableGroupBox

  def defineExportSettingsGroupBox(self):
    _exportSettingsGroupBox = QGroupBox('Export')
    _exportSettingsGroupBoxMainLayout = QGridLayout()
    _exportSettingsGroupBoxMainLayout.setVerticalSpacing(20)
    _exportSettingsGroupBoxMainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    self.includeHeaderCheckBox.setChecked(True)
    self.includeHeaderCheckBox.setMinimumSize(30, 30)
    self.includeHeaderCheckBox.setStyleSheet('QCheckBox::indicator::unchecked{border: 1px solid #777; color=white; width=15; height=15;} QCheckBox::indicator::checked{color=white; width=15; height=15;}')

    _chooseExportComboBox = QComboBox()
    _chooseExportComboBox.addItem('csv')
    _chooseExportComboBox.addItem('tsv')
    _chooseExportComboBox.addItem('json')

    self.exportToComboBox.addItem('File')
    self.exportToComboBox.addItem('Output Window')
    self.exportToComboBox.addItem('Clipboard')

    self.outputWidget.setWindowTitle('Output Window')
    self.outputWidget.setMinimumSize(1000, 600)
    _outputTextBox = QPlainTextEdit()
    _outputCloseButton = QPushButton('Close')
    _outputCloseButton.setMaximumWidth(60)
    _outputCloseButton.clicked.connect(self.outputWidget.close)
    _outputCopyToClipboardButton = QPushButton('Copy To Clipboard')
    _outputCopyToClipboardButton.setMaximumWidth(150)
    _outputCopyToClipboardButton.clicked.connect(lambda: self.copyToClipboard(text=_outputTextBox.toPlainText()))
    _outputWidgetLayout = QGridLayout()
    _outputWidgetLayout.addWidget(_outputTextBox, 0, 0, 1, 3)
    _outputWidgetLayout.addWidget(_outputCopyToClipboardButton, 1, 0)
    _outputWidgetLayout.addWidget(_outputCloseButton, 1, 1)
    self.outputWidget.setLayout(_outputWidgetLayout)

    _chooseExportFileButton = QPushButton('Choose Export File')
    _chooseExportFileButton.clicked.connect(self.chooseExportFile)

    _exportButton = QPushButton('Export')
    _exportButton.setMaximumWidth(100)
    _exportButton.clicked.connect(self.exportTable)

    _exportSettingsGroupBoxMainLayout.addWidget(QLabel('Include Header:'), 0, 0)
    _exportSettingsGroupBoxMainLayout.addWidget(self.includeHeaderCheckBox, 0, 1)
    _exportSettingsGroupBoxMainLayout.addWidget(QLabel('Export To: '), 1, 0)
    _exportSettingsGroupBoxMainLayout.addWidget(self.exportToComboBox, 1, 1)
    _exportSettingsGroupBoxMainLayout.addWidget(QLabel('Export Format: '), 2, 0)
    _exportSettingsGroupBoxMainLayout.addWidget(_chooseExportComboBox, 2, 1)
    _exportSettingsGroupBoxMainLayout.addWidget(QLabel('Export File: '), 3, 0)
    _exportSettingsGroupBoxMainLayout.addWidget(_chooseExportFileButton, 3, 1)
    _exportSettingsGroupBoxMainLayout.addWidget(self.exportFilenameLabel, 4, 0, 1, 2)
    _exportSettingsGroupBoxMainLayout.addWidget(_exportButton, 5, 0, 1, 2)
    _exportSettingsGroupBox.setLayout(_exportSettingsGroupBoxMainLayout)

    return _exportSettingsGroupBox

  def defineLogGroupBox(self):
    self.logList = QListWidget()

class RumorTableWidget(QWidget):
  def __init__(self):
    super().__init__()

class TableGenerator(QWidget):
  def __init__(self):
    super().__init__()

    self.encounterButton = QPushButton("Encounter Tables")
    self.rumorButton = QPushButton("Rumor Tables")

    self.menuWidget = QWidget()
    self.contentStackedWidget = QStackedWidget()

    self.tableGeneratorEncounterWidget = EncounterTableWidget()
    self.tableGeneratorRumorWidget = RumorTableWidget()

    self.defineMenuLayout()
    self.defineContentStackedWidget()

    _mainGridLayout = QGridLayout()
    _mainGridLayout.addWidget(self.menuWidget, 0, 0)
    _mainGridLayout.addWidget(self.contentStackedWidget, 0, 1)
    self.setLayout(_mainGridLayout)

  def defineMenuLayout(self):
    self.encounterButton.clicked.connect(lambda clicked: self.changeWidget(self.tableGeneratorEncounterWidget))
    self.rumorButton.clicked.connect(lambda clicked: self.changeWidget(self.tableGeneratorRumorWidget))

    menuLayout = QVBoxLayout()
    menuLayout.addWidget(self.encounterButton)
    menuLayout.addWidget(self.rumorButton)
    menuLayout.setSpacing(15)
    menuLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    self.menuWidget.setLayout(menuLayout)

  def defineContentStackedWidget(self):
    self.contentStackedWidget.addWidget(self.tableGeneratorEncounterWidget)
    self.contentStackedWidget.addWidget(self.tableGeneratorRumorWidget)
    self.contentStackedWidget.setCurrentIndex(0)

  def changeWidget(self, widget):
    self.contentStackedWidget.setCurrentWidget(widget)