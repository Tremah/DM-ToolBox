import logging
import sqlite3
import csv
from pathlib import Path

from PySide6 import QtGui
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QFont, QAction
from PySide6.QtWidgets import (
  QLabel,
  QPushButton,
  QGridLayout,
  QWidget,
  QVBoxLayout,
  QStackedWidget,
  QSizePolicy,
  QSpacerItem,
  QTableWidget,
  QTableWidgetItem,
  QGroupBox,
  QComboBox,
  QLineEdit,
  QCheckBox,
  QHBoxLayout,
  QPlainTextEdit, QMenu
)
import database as db
import log as log
import app_config as apc

class ManageDatabaseWidget(QWidget):
  def __init__(self):
    super().__init__()

    self.exportPath = 'data/export'
    self.jsonExportPath = f'{self.exportPath}/sql'

    # Header label
    _headerLabel = QLabel('Manage Database')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    # Export Button
    self.exportToSqlButton = QPushButton('Export Database To Sql File')
    self.exportToSqlButton.setMaximumSize(220, 30)
    self.exportToSqlButton.clicked.connect(self.handleExportToSqlButton)

    # Main GroupBox
    self.mainGroupBox = QGroupBox()
    _mainGroupBoxLayout = QVBoxLayout()
    _mainGroupBoxLayout.addWidget(self.exportToSqlButton)
    self.mainGroupBox.setLayout(_mainGroupBoxLayout)
    # Main layout
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    _mainGridLayout.addWidget(_headerLabel, 0, 0)
    _mainGridLayout.addWidget(self.mainGroupBox, 1, 0)

    self.setLayout(_mainGridLayout)

  def handleExportToSqlButton(self):
    # Compile structural information and export
    logging.info('Starting database export...')

    _tableStructures = db.getTableStructureForAllTables()
    _structureStatements = []
    logging.info('Exporting structural information...')
    for _table in _tableStructures.keys():
      _columnStatements = []
      for _column in _tableStructures[_table]['COLUMNS']:
        _columnStatement = f'{_column['COLUMN_NAME']} {_column['COLUMN_TYPE'].lower()}'
        if _column['IS_PRIMARY_KEY']:
          _columnStatement = f'{_columnStatement} primary key'
        if _column['NOT_NULL']:
          _columnStatement = f'{_columnStatement} not null'
        if _column['AUTOINCREMENT']:
          _columnStatement = f'{_columnStatement} autoincrement'
        _columnStatements.append(_columnStatement)

      _columnStatementsStr = ', '.join(_columnStatements)
      _tableStructureStatement = f'create table {_table} ({_columnStatementsStr}'

      if _tableStructures[_table]['FOREIGN_KEYS']:
        _foreignKeyStrings = []
        for _entry in _tableStructures[_table]['FOREIGN_KEYS']:
          _foreignKeyString = f'foreign key({_entry['THIS_COLUMNS']}) references {_entry['TABLE']}({_entry['OTHER_COLUMNS']})'
          _foreignKeyStrings.append(_foreignKeyString)

        _foreignKeyStringStatements = ', '.join(_foreignKeyStrings)
        _tableStructureStatement = f'{_tableStructureStatement}, {_foreignKeyStringStatements}'

      _structureStatements.append(f'-- {_table}\n')
      _structureStatements.append(_tableStructureStatement + ');\n')

    logging.info(f'Writing structural information to file {Path(apc.DB_SQL_EXPORT_PATH) / f'structure.sql'}...')
    with open(file=Path(apc.DB_SQL_EXPORT_PATH) / f'structure.sql', mode='w') as _sqlFile:
      for _statement in _structureStatements:
        _sqlFile.write(_statement)

    # Compile data and export
    _insertStatements = []
    logging.info('Exporting data...')
    for _table in _tableStructures.keys():
      _tableData = db.query(statement=f'select * from {_table}')
      _columnTypeAffinities = {}
      _columns = []
      for _entry in _tableStructures[_table]['COLUMNS']:
        _columns.append(_entry['COLUMN_NAME'])
        _columnTypeAffinities[_entry['COLUMN_NAME']] = _entry['COLUMN_TYPE_AFFINITY']


      _insertStatements.append(f'-- {_table}\n')
      for _row in _tableData:
        _values = []
        for _column in _columns:
          if _columnTypeAffinities[_column] == 'CHAR':
            _values.append(f"'{_row[_column]}'")
          else:
            _values.append(str(_row[_column]))
        _insertStatement = f'insert into {_table}({', '.join(_columns)}) values({','.join(_values)});\n'
        _insertStatements.append(_insertStatement)

      _insertStatements.append('\n')

    logging.info(f'Writing data to file {Path(apc.DB_SQL_EXPORT_PATH) / f'data.sql'}...')
    with open(file=Path(apc.DB_SQL_EXPORT_PATH) / f'data.sql', mode='w') as _sqlFile:
      for _statement in _insertStatements:
        _sqlFile.write(_statement)

class ManageTablesWidget(QWidget):
  def __init__(self):
    super().__init__()

    # Header label
    _headerLabel = QLabel('Manage Database Tables')
    _headerLabel.setFont(QFont('Ubuntu Sans', 14))
    _headerLabel.setMaximumSize(500, 20)

    # View Table GroupBox
    self.mainViewTableGroupBox = QGroupBox()
    self.tableComboBox = QComboBox()
    self.structureTable = QTableWidget()
    self.dataTable = QTableWidget()
    self.defineViewTableGroup()

    # Manage Table GroupBox
    self.customSqlPlainText = QPlainTextEdit()
    self.customSqlCsvCheckBox = QCheckBox()
    self.customSqlSubmitButton = QPushButton('Submit SQL')
    self.manageGroupBox = QGroupBox()
    self.defineManageGroup()

    # Main layout
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    _mainGridLayout.addWidget(_headerLabel, 0, 0)
    _mainGridLayout.addWidget(self.mainViewTableGroupBox, 1, 0)
    _mainGridLayout.addWidget(self.manageGroupBox, 2, 0)

    self.setLayout(_mainGridLayout)

  def defineViewTableGroup(self):
    _tableComboBoxLabel = QLabel('Table:')
    _tableComboBoxLabel.setFont(QFont('Ubuntu Sans', 12))
    _tableComboBoxLabel.setMaximumSize(50, 20)

    self.tableComboBox.setMaximumSize(300, 30)
    self.tableComboBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    self.tableComboBox.textActivated.connect(self.handleTableComboBoxSelect)
    self.loadDataIntoTableComboBox()

    _tableComboBoxLayout = QHBoxLayout()
    _tableComboBoxLayout.setSpacing(20)
    _tableComboBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    _tableComboBoxLayout.addWidget(_tableComboBoxLabel)
    _tableComboBoxLayout.addWidget(self.tableComboBox)
    _tableComboBoxLayout.addStretch(200)

    self.structureTable.setAlternatingRowColors(True)
    self.structureTable.horizontalHeader().setStretchLastSection(True)
    self.structureTable.verticalHeader().hide()
    self.structureTable.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    self.structureTable.setColumnCount(6)

    self.structureTable.setHorizontalHeaderItem(0, QTableWidgetItem('TABLE'))
    self.structureTable.setHorizontalHeaderItem(1, QTableWidgetItem('COLUMN'))
    self.structureTable.setHorizontalHeaderItem(2, QTableWidgetItem('TYPE'))
    self.structureTable.setHorizontalHeaderItem(3, QTableWidgetItem('PRIMARY KEY'))
    self.structureTable.setHorizontalHeaderItem(4, QTableWidgetItem('NOT NULL'))
    self.structureTable.setHorizontalHeaderItem(5, QTableWidgetItem('AUTOINCREMENT'))
    self.structureTable.setColumnWidth(0, 250)
    self.structureTable.setColumnWidth(1, 250)
    self.structureTable.setColumnWidth(2, 200)
    self.structureTable.setColumnWidth(3, 110)
    self.structureTable.setColumnWidth(4, 110)
    self.structureTable.setColumnWidth(5, 140)

    _structureGroupBoxLayout = QHBoxLayout()
    _structureGroupBoxLayout.addWidget(self.structureTable)
    _structureGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    _structureGroupBox = QGroupBox('Table Structure')
    _structureGroupBox.setLayout(_structureGroupBoxLayout)
    _structureGroupBox.setMinimumWidth(1100)
    _structureGroupBox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    self.loadDataIntoTable(dbTable=self.tableComboBox.currentText())

    self.dataTable.setAlternatingRowColors(True)
    self.dataTable.horizontalHeader().setStretchLastSection(True)
    self.dataTable.verticalHeader().hide()
    self.dataTable.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    self.dataTable.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    self.dataTable.customContextMenuRequested.connect(self.handleContextMenuOnDataTable)

    _dataGroupBoxLayout = QHBoxLayout()
    _dataGroupBoxLayout.addWidget(self.dataTable)
    _dataGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    _dataGroupBox = QGroupBox('Table Data')
    _dataGroupBox.setLayout(_dataGroupBoxLayout)
    _dataGroupBox.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

    # Main layout
    _mainViewTableGroupBoxGridLayout = QGridLayout()
    _mainViewTableGroupBoxGridLayout.setVerticalSpacing(20)
    _mainViewTableGroupBoxGridLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    _mainViewTableGroupBoxGridLayout.setContentsMargins(10, 10, 10, 10)

    _mainViewTableGroupBoxGridLayout.addItem(QSpacerItem(10, 10), 0, 0)
    _mainViewTableGroupBoxGridLayout.addLayout(_tableComboBoxLayout, 1, 0)
    _mainViewTableGroupBoxGridLayout.addWidget(_structureGroupBox, 2, 0)
    _mainViewTableGroupBoxGridLayout.addWidget(_dataGroupBox, 2, 1)

    self.mainViewTableGroupBox.setTitle('View Table')
    self.mainViewTableGroupBox.setMinimumHeight(450)
    self.mainViewTableGroupBox.setLayout(_mainViewTableGroupBoxGridLayout)

  def loadDataIntoTableComboBox(self):
    _tables = db.query('select distinct t.name as NAME from sqlite_master as t where t.type = "table" and t.name <> "sqlite_sequence" order by t.name')
    self.tableComboBox.clear()

    for _table in _tables:
      self.tableComboBox.addItem(_table['NAME'])

  def handleTableComboBoxSelect(self, value):
    self.loadDataIntoTable(value)

  def handleContextMenuOnDataTable(self, mouseCoordinates=None):
    _contextMenu = QMenu()
    _deleteAction = QAction('Delete')
    _deleteAction.triggered.connect(lambda : self.handleDeleteActionOnDataTable(rowIndex=self.dataTable.indexAt(mouseCoordinates)))
    _contextMenu.addAction(_deleteAction)

    _contextMenu.exec_(self.dataTable.viewport().mapToGlobal(mouseCoordinates))
    pass

  def handleDeleteActionOnDataTable(self, rowIndex=None):
    if not rowIndex:
      return

    # Gather selected rows
    _rows = []
    for _range in self.dataTable.selectedRanges():
      for i in range(_range.topRow(), _range.bottomRow() + 1):
        _rows.append(i)

    _tableStructure = db.getTableStructure(self.tableComboBox.currentText())

    # Check if table has primary keys defined and extract them
    _relevantColumns = []
    _hasPrimaryKey = False
    for _column in _tableStructure['COLUMNS']:
      if _column['IS_PRIMARY_KEY']:
        _relevantColumns.append(_column)
        _hasPrimaryKey = True

    _relevantColumns = _relevantColumns if _hasPrimaryKey else _tableStructure

    # Compile condition for deletion

    for _row in _rows:
      _tableRow = _row
      _deleteCondition = ''
      for i in range(len(_relevantColumns)):
        # Find column position in data table
        _columnName = _relevantColumns[i]['COLUMN_NAME']
        _columnPosition = -1
        for j in range(self.dataTable.columnCount()):
          _dataTableColumnName = self.dataTable.horizontalHeaderItem(j).text()
          if _dataTableColumnName == _columnName:
            _columnPosition = j
            break

        _columnValue = self.dataTable.item(_tableRow, _columnPosition).text()
        _singleDeleteCondition = f'{_columnName} = '

        _formattedValue = ''
        _formattedValue = f'{_columnValue}' if _relevantColumns[i]['COLUMN_TYPE'] == 'NUM' else f"'{_columnValue}'"


        _singleDeleteCondition = f'{_columnName} = {_formattedValue}'
        _deleteCondition = _deleteCondition + _singleDeleteCondition + ' and ' if i < len(_relevantColumns) - 1 else _deleteCondition + _singleDeleteCondition

      _deleteStatement = f'delete from {self.tableComboBox.currentText()} where {_deleteCondition}'
      db.query(statement=_deleteStatement, commit=True)

    self.dataTable.clearSelection()
    self.loadDataIntoTable(dbTable=self.tableComboBox.currentText())

  def loadDataIntoTable(self, dbTable):
    # Fill structure table
    _tableStructure = db.getTableStructure(dbTable)
    self.structureTable.setRowCount(len(_tableStructure['COLUMNS']))

    _rowIndex = 0
    _tableColumns = []
    for _row in _tableStructure['COLUMNS']:
      self.structureTable.setItem(_rowIndex, 0, QTableWidgetItem(dbTable))
      self.structureTable.setItem(_rowIndex, 1, QTableWidgetItem(_row['COLUMN_NAME']))
      self.structureTable.setItem(_rowIndex, 2, QTableWidgetItem(str.upper(_row['COLUMN_TYPE'])))

      _pk = 'No'
      if _row['IS_PRIMARY_KEY'] == 1:
        _pk = 'Yes'
      self.structureTable.setItem(_rowIndex, 3, QTableWidgetItem(_pk))

      _notNull = 'No'
      if _row['NOT_NULL'] == 1:
        _notNull = 'Yes'
      self.structureTable.setItem(_rowIndex, 4, QTableWidgetItem(_notNull))

      _autoIncrement = 'No'
      if _row['AUTOINCREMENT'] == 1:
        _autoIncrement = 'Yes'
      self.structureTable.setItem(_rowIndex, 5, QTableWidgetItem(_autoIncrement))

      _tableColumns.append(_row['COLUMN_NAME'])

      _rowIndex += 1


    # Set data table header items
    self.dataTable.setColumnCount(len(_tableColumns))
    _columnIndex = 0
    for _column in _tableColumns:
      self.dataTable.setHorizontalHeaderItem(_columnIndex, QTableWidgetItem(_column))
      _columnIndex += 1

    # Fill data table
    _tableData = db.query(f'select * from {dbTable} order by {','.join(db.getPrimaryKeyColumnsForTable(dbTable))}')

    self.dataTable.setRowCount(len(_tableData))

    _rowIndex = 0
    for _row in _tableData:
      _columnIndex = 0
      for _column in _tableColumns:
        _item = QTableWidgetItem(str(_row[_column]))
        self.dataTable.setItem(_rowIndex, _columnIndex, _item)
        _columnIndex += 1
      _rowIndex += 1

  def defineManageGroup(self):
    # New Table
    _tableNameLabel = QLabel('Table Name: ')
    _tableNameLineEdit = QLineEdit()
    _tableNameLineEdit.setPlaceholderText('Table name here...')

    _tableColumnsLabel = QLabel('Columns: ')

    _columnNameLineEdit = QLineEdit()
    _columnTypeComboBox = QComboBox()
    _columnTypeComboBox.addItem('INTEGER')
    _columnTypeComboBox.addItem('VARCHAR')
    _columnLengthLineEdit = QLineEdit()
    _pkCheckBox = QCheckBox()
    _pkCheckBox.setStyleSheet('QCheckBox::indicator::unchecked{border: 1px solid #777; color=white; width=15; height=15;} QCheckBox::indicator::checked{color=white; width=15; height=15;}')

    _newTableGroupBoxLayout = QGridLayout()
    _newTableGroupBoxLayout.setSpacing(20)
    _newTableGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0, 1, 5)
    _newTableGroupBoxLayout.addWidget(_tableNameLabel, 1, 0)
    _newTableGroupBoxLayout.addWidget(_tableNameLineEdit, 1, 1)
    _newTableGroupBoxLayout.addWidget(_tableColumnsLabel, 2, 0, 1, 5)
    _newTableGroupBoxLayout.addWidget(_columnNameLineEdit, 3, 0)
    _newTableGroupBoxLayout.addWidget(_columnTypeComboBox, 3, 1)
    _newTableGroupBoxLayout.addWidget(_columnLengthLineEdit, 3, 2)
    _newTableGroupBoxLayout.addWidget(_pkCheckBox, 3, 3)

    _newTableGroupBox = QGroupBox('New Table')
    _newTableGroupBox.setMinimumWidth(400)
    _newTableGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    _newTableGroupBox.setLayout(_newTableGroupBoxLayout)

    # Alter Table
    _alterTableGroupBoxLayout = QGridLayout()
    _alterTableGroupBoxLayout.setSpacing(20)
    _alterTableGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0, 1, 2)

    _alterTableGroupBox = QGroupBox('Alter Table')
    _alterTableGroupBox.setMinimumWidth(400)
    _alterTableGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    _alterTableGroupBox.setLayout(_alterTableGroupBoxLayout)

    # Delete Table
    _deleteTableGroupBoxLayout = QGridLayout()
    _deleteTableGroupBoxLayout.setSpacing(20)
    _deleteTableGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0, 1, 2)

    _deleteTableGroupBox = QGroupBox('Delete Table')
    _deleteTableGroupBox.setMinimumWidth(400)
    _deleteTableGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    _deleteTableGroupBox.setLayout(_deleteTableGroupBoxLayout)

    # Custom SQL
    self.customSqlSubmitButton.setMaximumWidth(130)
    self.customSqlSubmitButton.clicked.connect(self.submitCustomSql)
    _customSqlCsvCheckBoxLabel = QLabel('CSV:')
    _customSqlCsvCheckBoxLabel.setMaximumWidth(30)
    self.customSqlCsvCheckBox.setStyleSheet('QCheckBox::indicator::unchecked{border: 1px solid #777; color=white; width=15; height=15;} QCheckBox::indicator::checked{color=white; width=15; height=15;}')

    _customSqlTableGroupBoxLayout = QGridLayout()
    _customSqlTableGroupBoxLayout.setSpacing(20)
    _customSqlTableGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0, 1, 4)
    _customSqlTableGroupBoxLayout.addWidget(self.customSqlPlainText , 1, 0, 1, 4)
    _customSqlTableGroupBoxLayout.addWidget(self.customSqlSubmitButton, 2, 0)
    _customSqlTableGroupBoxLayout.addWidget(_customSqlCsvCheckBoxLabel, 2, 1)
    _customSqlTableGroupBoxLayout.addWidget(self.customSqlCsvCheckBox, 2, 2)

    _customSqlTableGroupBox = QGroupBox('Custom SQL')
    _customSqlTableGroupBox.setMinimumWidth(400)
    _customSqlTableGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    _customSqlTableGroupBox.setLayout(_customSqlTableGroupBoxLayout)

    _manageGroupBoxLayout = QGridLayout()
    _manageGroupBoxLayout.setSpacing(30)
    _manageGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    _manageGroupBoxLayout.addItem(QSpacerItem(10, 10), 0, 0, 1, 5)
    _manageGroupBoxLayout.addWidget(_newTableGroupBox, 1, 0)
    _manageGroupBoxLayout.addWidget(_alterTableGroupBox, 1, 2)
    _manageGroupBoxLayout.addWidget(_deleteTableGroupBox, 1, 3)
    _manageGroupBoxLayout.addWidget(_customSqlTableGroupBox, 1, 4)


    self.manageGroupBox.setTitle('Manage Tables')
    self.manageGroupBox.setLayout(_manageGroupBoxLayout)
    self.manageGroupBox.setMinimumHeight(600)
    self.manageGroupBox.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

  def submitCustomSql(self):
    if not self.customSqlCsvCheckBox.isChecked():
      _queryStr = self.customSqlPlainText.toPlainText().replace('\n', '')
      _queryList = _queryStr.split(';')
      try:
        for _query in _queryList:
          if len(_query) > 0:
            db.query(_query + ';', commit=True)
        self.loadDataIntoTableComboBox()
      except sqlite3.Error as err:
        print(f'Error occurred during execution of statement:\n "{_query}"')
        print(f'Error Name: {err.sqlite_errorname}')
        print(f'Error Code: {err.sqlite_errorcode}')
        print(f'Error Message: {err}')
    else:
      csvRawData = self.customSqlPlainText.toPlainText().splitlines()
      _tableName = csvRawData[0]
      csvRawData.pop(0)
      csvRows = csv.DictReader(csvRawData, delimiter=';')

      _fields = ','.join(csvRows.fieldnames)
      _queryStr = f'INSERT INTO {_tableName}({_fields})'
      pass

class DatabaseManager(QWidget):
  def __init__(self):
    super().__init__()

    self.manageTablesWidget = ManageTablesWidget()
    self.manageDatabaseWidget = ManageDatabaseWidget()

    self.manageTablesButton = QPushButton("Manage Tables")
    self.manageDatabaseButton = QPushButton("Manage Database")

    self.menuWidget = QWidget()

    self.contentStackedWidget = QStackedWidget()

    self.defineMenuLayout()
    self.defineContentStackedWidget()

    self.mainGridLayout = QGridLayout()
    self.mainGridLayout.addWidget(self.menuWidget, 0, 0)
    self.mainGridLayout.addWidget(self.contentStackedWidget, 0, 1)

    self.mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    self.setLayout(self.mainGridLayout)

  def defineMenuLayout(self):
    self.manageDatabaseButton.setMinimumWidth(170)
    self.manageDatabaseButton.clicked.connect(lambda clicked: self.changeWidget(self.manageDatabaseWidget))
    self.manageTablesButton.clicked.connect(lambda clicked: self.changeWidget(self.manageTablesWidget))
    self.manageTablesButton.setMinimumWidth(170)

    menuLayout = QVBoxLayout()
    menuLayout.addWidget(self.manageTablesButton)
    menuLayout.addWidget(self.manageDatabaseButton)
    menuLayout.setSpacing(15)
    menuLayout.setAlignment(Qt.AlignmentFlag.AlignTop)

    self.menuWidget.setLayout(menuLayout)

  def defineContentStackedWidget(self):
    self.contentStackedWidget.addWidget(self.manageTablesWidget)
    self.contentStackedWidget.addWidget(self.manageDatabaseWidget)
    self.contentStackedWidget.setCurrentIndex(1)

  def changeWidget(self, widget):
    self.contentStackedWidget.setCurrentWidget(widget)
