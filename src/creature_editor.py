import csv
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
  QFileDialog
)

import database as db
import qt_wrapper as qtw


class CreatureEditorImportWidget(QWidget):
  def __init__(self):
    super().__init__()

    mainGridLayout = QGridLayout()
    buttonHboxLayout = QHBoxLayout()
    self.contentTextBox = QPlainTextEdit()

    reviewButton = QPushButton('Review')
    saveButton = QPushButton('Save')
    clearButton = QPushButton('Clear')
    self.reviewTable = qtw.DataTable()
    self.logList = QListWidget()

    mainGridLayout.setSpacing(30)
    mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    headerLabel = QLabel('Import Creatures')
    headerLabel.setFont(QFont('Ubuntu Sans', 14))
    headerLabel.setMaximumSize(500, 20)

    self.contentTextBox.setPlaceholderText("CSV-data here...")
    self.contentTextBox.setMinimumSize(1200, 1000)
    self.contentTextBox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    self.reviewTable.setMinimumSize(1200, 1000)
    self.reviewTable.setAlternatingRowColors(True)
    self.reviewTable.horizontalHeader().setStretchLastSection(True)
    self.reviewTable.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    reviewButton.setMinimumSize(150, 30)
    reviewButton.clicked.connect(self.readCsv)
    reviewButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    saveButton.setMinimumSize(150, 30)
    saveButton.clicked.connect(self.writeImportToDatabase)
    saveButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    clearButton.setMinimumSize(150, 30)
    clearButton.clicked.connect(self.clearTable)
    clearButton.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    buttonHboxLayout.addWidget(reviewButton)
    buttonHboxLayout.addWidget(saveButton)
    buttonHboxLayout.addWidget(clearButton)
    buttonHboxLayout.addItem(QSpacerItem(5000, 10))
    buttonHboxLayout.setSpacing(20)
    buttonHboxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    logLabel = QLabel('Log')
    logLabel.setFont(QFont('Ubuntu Sans', 12))
    logLabel.setMaximumSize(500, 20)

    mainGridLayout.addWidget(headerLabel, 0, 0)
    mainGridLayout.addWidget(self.contentTextBox, 1, 0)
    mainGridLayout.addWidget(self.reviewTable, 1, 1)
    mainGridLayout.addLayout(buttonHboxLayout, 2, 0, 1, 2)
    mainGridLayout.addWidget(logLabel, 3, 0, 1, 2)
    mainGridLayout.addWidget(self.logList, 4, 0, 1, 2)

    self.setLayout(mainGridLayout)

  def clearTable(self):
    self.contentTextBox.clear()
    self.reviewTable.clear()
    self.reviewTable.setRowCount(0)
    self.reviewTable.setColumnCount(0)

  def readCsv(self):
    csvRawData = self.contentTextBox.toPlainText().splitlines()
    csvRows = csv.DictReader(csvRawData, delimiter=';')

    self.reviewTable.setColumnCount(len(csvRows.fieldnames))
    self.reviewTable.setRowCount(len(csvRawData) - 1)
    i = 0
    # Set headers
    for field in csvRows.fieldnames:
      item = QTableWidgetItem(field)
      if field == 'CR':
        self.reviewTable.setColumnWidth(i, 100)
      else:
        self.reviewTable.setColumnWidth(i, 200)

      self.reviewTable.setHorizontalHeaderItem(i, item)
      i = i + 1

    # Prepare Data
    i = 0
    j = 0
    for row in csvRows:
      for attrib in row:
        item = QTableWidgetItem(row[attrib])
        if attrib == 'CR':
          item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reviewTable.setItem(i, j, item)
        j += 1
      i += 1
      j = 0

    self.reviewTable.show()

  def writeImportToDatabase(self):
    _nameColumn = 0
    _typeColumn = 1
    _crColumn = 2
    _alignmentColumn = 3
    _environmentColumn = 4
    _sourceColumn = 5

    _errorCount = 0
    _errorData = []
    _datasetCount = 0
    for i in range(0, self.reviewTable.rowCount()):
      _error = False
      _datasetCount += 1

      _name = self.reviewTable.item(i, _nameColumn).text().strip()
      _source = self.reviewTable.item(i, _sourceColumn).text()

      _typeValue = self.reviewTable.item(i, _typeColumn).text()
      _typeKey = db.query('select ID from CREATURE_TYPE where NAME = ?', (_typeValue.strip(),), one=True)['ID']

      _crValue = self.reviewTable.item(i, _crColumn).text()

      if _crValue == '¼':
        _crValue = '1/4'
      elif _crValue == '½':
        _crValue = '1/2'

      _crKey = db.query('select ID from CHALLENGE_RATING where CR = ?', (_crValue.strip(),), one=True)['ID']

      _alignmentValue = self.reviewTable.item(i, _alignmentColumn).text().strip()
      _result = db.query('select ID from ALIGNMENT where NAME = ?', (_alignmentValue.strip(),), one=True)

      _alignmentKey = None
      if _result is not None:
        _alignmentKey = _result['ID']
      else:
        _error = True

      if not _error:
        _newId = db.query('select max(ID) as ID from CREATURE', one=True)['ID']
        if _newId is None:
          _newId = 1
        else:
          _newId += 1

        _rowId = None
        _query = 'insert into CREATURE(ID, NAME, TYPE, CR, ALIGNMENT, SOURCE) values(?, ?, ?, ?, ?, ?);'
        try:
          _rowId = db.execute(_query, (_newId, _name, _typeKey, _crKey, _alignmentKey, _source), commit=True)
        except sqlite3.Error as err:
          print(f'Error occurred during execution of statement:\n {_query}')
          print(f'Error Name: {err.sqlite_errorname}')
          print(f'Error Code: {err.sqlite_errorcode}')
          print(f'Error Message: {err}')

        _error = True
        if _rowId is not None:
          _error = False
          _envNameList = self.reviewTable.item(i, _environmentColumn).text().strip()
          # envNameList = envNameList.replace(' ', '')
          _envNameList = _envNameList.split(',')
          for envName in _envNameList:
            _result = db.query('select ID from ENVIRONMENT where NAME = ?', (envName.strip(),), one=True)
            _error = True
            if _result is not None:
              _error = None
              envKey = _result['ID']
              _query = 'insert into CREATURE_X_ENVIRONMENT(CREATURE_ID, ENVIRONMENT_ID) values(?, ?);'
              _rowId = None
              try:
                _rowId = db.execute(_query, (_newId, envKey), commit=True)
              except sqlite3.Error as err:
                print(f'Error occurred during execution of statement:\n {_query}')
                print(f'Error Name: {err.sqlite_errorname}')
                print(f'Error Code: {err.sqlite_errorcode}')
                print(f'Error Message: {err}')
                _error = True

      if _error:
        _errorCount += 1
        _errorData.append(dict(name=_name, typeKey=_typeKey, crKey=_crKey, alignmentKey=_alignmentKey,
                               envNameList=self.reviewTable.item(i, _environmentColumn).text().strip(), source=_source))
    self.logList.clear()
    _logItem = QListWidgetItem(str(_datasetCount) + ' data sets have been supplied.')
    self.logList.addItem(_logItem)

    if _errorCount == 0:
      db.commitChanges()
      _logItem = QListWidgetItem('No errors occurred during insertion.')
      _logItem.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
      self.logList.addItem(_logItem)
    else:
      _logItem = QListWidgetItem(
        'No data was written, ' + str(_errorCount) + ' errors were encountered during insertion:')
      _logItem.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
      self.logList.addItem(_logItem)
      for item in _errorData:
        _logItem = QListWidgetItem(str(item))
        _logItem.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
        self.logList.addItem(_logItem)

class CreatureEditorListWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Header Label
    _headerLabel = QLabel('List Creatures')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    # Data Table
    self.dataTable = qtw.DataTable(lastSectionStretch=True)

    # Filter Group Box
    self.mainFilterGroupBox = qtw.CreatureFilterGroupBox(title='Filters', applyFilterMethod=self.dataTable.filterTable, resetFormMethod=self.resetForm)

    # Finish setup
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.addWidget(_headerLabel, 0, 0)
    _mainGridLayout.addWidget(self.mainFilterGroupBox, 1, 0)
    _mainGridLayout.addWidget(self.dataTable, 2, 0)
    self.setLayout(_mainGridLayout)

    _filterValues = self.mainFilterGroupBox.getFilterItems()
    self.dataTable.filterTable(_filterValues)

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
    self._mainFilterGroupBox = qtw.CreatureFilterGroupBox(title='Filters', applyFilterMethod=self.searchResultTable.filterTable, resetFormMethod=self.resetForm)

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
    _searchResultGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0)
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

    _previewTableGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0)
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
    self.listButton = QPushButton("List")
    self.importButton = QPushButton("Import")
    self.exportButton = QPushButton("Export")

    self.menuWidget = QWidget()
    self.contentStackedWidget = QStackedWidget()

    self.creatureEditorNewWidget = CreatureEditorNewWidget()
    self.creatureEditorListWidget = CreatureEditorListWidget()
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
    self.listButton.clicked.connect(lambda clicked: self.changeWidget(self.creatureEditorListWidget))
    self.exportButton.clicked.connect(lambda clicked: self.changeWidget(self.creatureEditorExportWidget))

    menuLayout = QVBoxLayout()
    menuLayout.addWidget(self.newButton, 0)
    menuLayout.addWidget(self.editButton)
    menuLayout.addWidget(self.listButton)
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
