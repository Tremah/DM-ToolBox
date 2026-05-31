import logging
import re

from PySide6.QtSql import QSqlDatabase, QSqlQuery

def openConnection(driver, path):
  _database = QSqlDatabase.addDatabase(driver)
  _database.setDatabaseName(path)

  if not _database.open():
    print(f'Error! Could not open database {path}')

def closeConnection():
  QSqlDatabase.database().close()

def beginTransaction():
  _database = QSqlDatabase.database()
  _database.transaction()

def delete(statement, args=(), commit=False):
  return query(statement, args, commit)

def endTransaction():
  commitChanges()

def commitChanges():
  return QSqlDatabase.database().commit()

def rollbackChanges():
  return QSqlDatabase.database().rollback()

def printError(error):
  logging.error(f'Error Type: {error.type()}')
  logging.error(f'Error Message: {error.text()}')

  print(f'Error Type: {error.type()}')
  print(f'Error Message: {error.text()}')

def printLastError(message=''):
  if message:
    logging.error(message)

  printError(QSqlDatabase.database().lastError())

def getTableColumnInfo(table, column):
  _tableStructure = getTableStructure(table)

  for _column in _tableStructure['COLUMNS']:
    if _column['COLUMN_NAME'] == column:
      return _column

  return {}

def getGameParameterTypeId(parameterName=None):
  _result = query(statement=f'select ID from GAME_PARAMETER_TYPE where NAME = ?', args=(parameterName,), one=True)
  _id = _result['ID']
  return _id

def getGameParameterValueFieldId(parameterName=None, parameterValueColumn=None, parameterValue=None):
  _parameterId = getGameParameterTypeId(parameterName=parameterName)

  _statement = f'select ID from GAME_PARAMETER where TYPE = ? and {parameterValueColumn} = ?'
  _result = query(statement=_statement, args=(_parameterId, parameterValue), one=True)
  _id = _result['ID']
  return _id

def getPrimaryKeyColumnsForTable(table=None):
  if not table:
    return []

  _tableStructure = getTableStructure(table)

  _primKeys = []
  for _column in _tableStructure['COLUMNS']:
    if _column['IS_PRIMARY_KEY']:
      _primKeys.append(_column['COLUMN_NAME'])

  return _primKeys

def getTableStructure(table=None):
  if not table:
    return

  _tableStructure = query(statement=f'PRAGMA table_info({table});')
  _hasAutoIncrement = query(statement=f'select NAME from sqlite_sequence where NAME = ?', args=(table,), one=True)
  _foreignKeyStructure = query(statement=f'PRAGMA foreign_key_list({table});')

  # Prepare foreign key data
  _foreignKeys = []
  _columnsThisTable = []
  _columnsOtherTable = []
  for i in range(len(_foreignKeyStructure)):
    _columnsThisTable.append(_foreignKeyStructure[i]['from'])
    _columnsOtherTable.append(_foreignKeyStructure[i]['to'])

    # Group handling for foreign key target tables
    if i < len(_foreignKeyStructure) - 1:
      if _foreignKeyStructure[i]['table'] != _foreignKeyStructure[i + 1]['table']:
        _foreignKey = {'TABLE': _foreignKeyStructure[i]['table'], 'THIS_COLUMNS': ', '.join(_columnsThisTable), 'OTHER_COLUMNS': ', '.join(_columnsOtherTable)}
        _foreignKeys.append(_foreignKey)
        _columnsThisTable.clear()
        _columnsOtherTable.clear()
    else:
      _foreignKey = {'TABLE': _foreignKeyStructure[i]['table'], 'THIS_COLUMNS': ', '.join(_columnsThisTable), 'OTHER_COLUMNS': ', '.join(_columnsOtherTable)}
      _foreignKeys.append(_foreignKey)
      _columnsThisTable.clear()
      _columnsOtherTable.clear()

  _columns = []
  for _column in _tableStructure:
    _entry = {'COLUMN_NAME': _column['name']}

    _typeAffinity = 'NUM'
    if (re.search('CHAR', _column['type'].upper()) is not None or
        re.search('TEXT', _column['type'].upper()) is not None or
        re.search('CLOB', _column['type'].upper()) is not None):
      _typeAffinity = 'CHAR'
    _entry['COLUMN_TYPE_AFFINITY'] = _typeAffinity

    _entry['COLUMN_TYPE'] = _column['type']
    _entry['IS_PRIMARY_KEY'] = _column['pk']
    _entry['NOT_NULL'] = _column['notnull']

    _entry['AUTOINCREMENT'] = 0
    if _hasAutoIncrement and _entry['IS_PRIMARY_KEY']:
      _entry['AUTOINCREMENT'] = 1

    _columns.append(_entry)

  _result = {'COLUMNS': _columns, 'FOREIGN_KEYS': _foreignKeys}

  return _result

def getTableStructureForAllTables(excludeSqliteTables=True):
  _tableList = query(statement=f'PRAGMA table_list;')
  _tableStructureAllTables = {}
  for _table in _tableList:
    if excludeSqliteTables and _table['name'].upper().startswith('SQLITE_'):
      continue
    _tableStructureAllTables[_table['name']] = getTableStructure(_table['name'])

  return _tableStructureAllTables

def update(statement, args=(), commit=False):
  return query(statement, args, commit)

def insert(statement, args=(), commit=False):
  return query(statement, args, commit)

def query(statement, args=(), commit=False, one=False):
  _query = QSqlQuery()

  _isSelect = statement.lstrip().lower().startswith('select')
  _isInsert = statement.lstrip().lower().startswith('insert')
  _isUpdate = statement.lstrip().lower().startswith('update')
  _isAlter  = statement.lstrip().lower().startswith('alter')
  _isDelete = statement.lstrip().lower().startswith('delete')

  if not _query.prepare(statement):
    printError(_query.lastError())
    _query.finish()

    if not _isSelect:
      return -1

    return []

  for _arg in args:
    _query.addBindValue(_arg)

  # Returns true if an error is set
  if _query.isValid():
    printError(_query.lastError())
    _query.finish()

    if not _isSelect:
      return -1

    return []

  if not _query.exec():
    printError(_query.lastError())
    _query.finish()

    if not _isSelect:
      return -1

    return []

  if _isUpdate or _isDelete or _isAlter or _isInsert:
    if commit:
      commitChanges()
    _query.finish()

    return 0

  _fields = []
  _fieldCount = 0
  for i in range(_query.record().count()):
    _fields.append(_query.record().fieldName(i))
    _fieldCount += 1

  _resultList = []
  while _query.next():
    _row = {}
    for i in range(_fieldCount):
      _value = _query.value(i)
      _row[_fields[i]] = _value
    _resultList.append(_row)

  _query.finish()

  return _resultList[0] if len(_resultList) > 0 and one else _resultList
