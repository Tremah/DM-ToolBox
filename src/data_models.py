from typing import Any

from PySide6.QtCore import Qt, QSortFilterProxyModel, QModelIndex, QAbstractTableModel
from PySide6.QtSql import QSqlTableModel, QSqlRelationalTableModel, QSqlRelation, QSqlQueryModel

import src.database as db

class SortFilterModel(QSortFilterProxyModel):
  def __init__(self, sourceModel : QSqlTableModel | QSqlQueryModel | QSqlRelationalTableModel | None = None):
    super().__init__()

    self.filterColumns = []
    self.filterValues = []
    self.hiddenColumns = []

    if sourceModel:
      self.setSourceModel(sourceModel)

  def filterAcceptsRow(self, source_row, source_parent):
    _columnIds = []
    _sourceModel = self.sourceModel()
    _allFiltersMatch = False
    if self.filterColumns:
      for i, _column in enumerate(self.filterColumns) :
        # Search for current filter column
        for j in range(_sourceModel.columnCount()):
          if _sourceModel.headerData(j, Qt.Orientation.Horizontal) == _column:
            _value = _sourceModel.data(_sourceModel.index(source_row, j))
            if _value == self.filterValues[i]:
              if i == 0:
                _allFiltersMatch = True
              else:
                _allFiltersMatch = _allFiltersMatch and True
            break
    else:
      _allFiltersMatch = True

    return _allFiltersMatch

  def filterAcceptsColumn(self, source_column, source_parent):
    if not self.hiddenColumns:
      return True

    _columnName = self.sourceModel().headerData(source_column, Qt.Orientation.Horizontal)
    return not _columnName in self.hiddenColumns

  def showAllColumns(self):
    self.hiddenColumns = []
    self.invalidateFilter()

  def setHiddenColumns(self, hiddenColumns : list):
    self.hiddenColumns = hiddenColumns
    self.invalidateFilter()

  def setRowFilter(self, filterColumns : list, filterValues : list):
    self.filterColumns = filterColumns
    self.filterValues = filterValues
    self.invalidateFilter()

class CreatureGameSystemProxyModel(QSortFilterProxyModel):
  def __init__(self):
    super().__init__()

    self.gameSystem = -1

  def filterAcceptsRow(self, source_row, source_parent):
    if self.gameSystem == -1:
      return False

    _sourceModel = self.sourceModel()
    _colId = _sourceModel.record().indexOf('GAME_SYSTEM')
    _value = _sourceModel.index(source_row, _colId).data()
    if _value == self.gameSystem:
      return True

    return False

  def setGameSystem(self, gameSystem):
    self.gameSystem = gameSystem
    self.invalidateFilter()

class CreatureSourceProxyModel(QSortFilterProxyModel):
  def __init__(self):
    super().__init__()

    self.source = ''

  def filterAcceptsRow(self, source_row, source_parent):
    if self.source == -1:
      return False

    _sourceModel = self.sourceModel()
    _colId = _sourceModel.record().indexOf('SOURCE')
    _value = _sourceModel.index(source_row, _colId).data()
    if _value == self.source:
      return True

    return False

  def setSource(self, source):
    self.source = source
    self.invalidateFilter()

class CreatureNameProxyModel(QSortFilterProxyModel):
  def __init__(self):
    super().__init__()

    # Filled with lists holding filter values for the model columns
    # 3 possible states
    # None = No rows are shown
    # All inside lists empty = Show all
    # One or more lists filled = Filter rows accordingly
    self.filterValues = {}

  def filterAcceptsRow(self, source_row, source_parent):
    #No filter values supplied, show no rows (do nothing)
    if not self.filterValues:
      return False

    _sourceModel = self.sourceModel()

    for _key in self.filterValues.keys():
      # No filters for this column given
      if not self.filterValues[_key]:
        continue

      _colId = _sourceModel.record().indexOf(_key)
      _value = _sourceModel.data(_sourceModel.index(source_row, _colId))
      # Debug
      #if _value in (124, 1518, 1519):
        #pass

      if _key == 'ENVIRONMENT':
        _show = False
        _environments = str(_value).split(',')
        for _environment in _environments:
          if _environment.strip() in self.filterValues[_key]:
            _show = True
            break
      else:
        _show = True if _value in self.filterValues[_key] else False


      # Logical And
      if not _show:
        return False

    return True

  def setFilterValues(self, filterValues=None):
    # Only keep relevant values in filterValues
    if filterValues:
      _sourceModel = self.sourceModel()
      _filterValues = {}
      for _key in filterValues.keys():
        for i in range(_sourceModel.columnCount()):
          _name = _sourceModel.headerData(i, Qt.Orientation.Horizontal)
          if _name == _key:
            _filterValues[_key] = filterValues[_key]
            break
      self.filterValues = _filterValues
    else:
      self.filterValues = None

    self.invalidateFilter()

class GameParameterProxyModel(QSortFilterProxyModel):
  def __init__(self):
    super().__init__()

    self.name = ''
    self.id = -1

  def filterAcceptsRow(self, source_row, source_parent):
    if self.id == -1:
      return False

    if source_row == 95:
      pass
    _sourceModel = self.sourceModel()

    _columnId = _sourceModel.record().indexOf('TYPE')
    _id = _sourceModel.data(_sourceModel.index(source_row, _columnId))
    if _id == self.id:
      return True
    else:
      return False

  def setParameter(self, parameterName):
    self.name = parameterName
    self.id = db.query(statement='select ID from GAME_PARAMETER_TYPE where NAME = ?', args=(self.name,), one=True)['ID']

    if self.id > 0:
      self.invalidateFilter()
      # Force model to update since combobox does not request filtering automatically
      _rc = self.rowCount()

  def setParameterId(self, parameterId):
    self.id = parameterId

  def parameterId(self):
    return self.id if self.id != -1 else None

  def parameterName(self):
    return self.name if self.name != '' else None

  def columnId(self, columnName):
    _columnId = self.sourceModel().record().indexOf(columnName)
    return _columnId

class FoundryDocumentJsonExportModel(QAbstractTableModel):
  def __init__(self, data, parent=None):
    super().__init__()

    self._data = data

    self._columns = ['DOCUMENT_KEY', 'NAME', 'MODULE', 'MODULE_PACK', 'MODULE_FOLDER', 'MODULE_FOLDER_KEY', 'FOUNDRY_EXPORT_FILEPATH']
    #self._columns = list(self.data[0].keys() if self.data else [])

  def rowCount(self, parent=QModelIndex()):
    return len(self._data)

  def columnCount(self, parent=QModelIndex()):
    return len(self._columns)

  def data(self, index, role=Qt.ItemDataRole.DisplayRole):
    if not index.isValid():
      return None

    if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
      _row = index.row()
      _column = index.column()
      _key = self._columns[_column]

      #if _key == 'FOUNDRY_EXPORT_FILEPATH' and role==Qt.ItemDataRole.DisplayRole:
        #_filePathShort = hp.shortenFilePath(path=self._data[_row][_key], maxLen=80)

        #return _filePathShort

      return self._data[_row][_key]

    return None

  def headerData(self, section : int, orientation : Qt.Orientation, role=Qt.ItemDataRole.DisplayRole):
    if role != Qt.ItemDataRole.DisplayRole:
      return None

    if orientation == Qt.Orientation.Horizontal:
      return self._columns[section]
    else:
      return section + 1

  def getData(self):
    _data = []
    for _row in range(self.rowCount()):
      _rowData = {}
      for _col in range(self.columnCount()):
        _colName = self.headerData(_col, Qt.Orientation.Horizontal)
        _index = self.index(_row, _col)
        _value = self.data(_index, role=Qt.ItemDataRole.EditRole)
        _rowData[_colName] = _value
      _data.append(_rowData)

    return _data

# Accepts a dictionary of dictionaries or a list of dictionaries and a list of column names
# If a dictionary is supplied, it is converted to a list of dictionaries, preserving the key for each sub-dictionary under the key '_key'
# Creates a model that can be used to display data in a table view
class TabularDataModel(QAbstractTableModel):
  def __init__(self, data : dict[str, dict[str, Any]] | list[dict[str, Any]] | None = None, columns : list | None = None, parent=None):
    super().__init__(parent=parent)

    if isinstance(data, dict):
      self._data = self._dictToList(data)
    else:
      self._data = data or []

    self._columns = columns or []

    if not self._columns and self._data:
      self._columns = list(self._data[0].keys())

  def columnCount(self, parent= ...):
    return len(self._columns)

  def data(self, index, role = Qt.ItemDataRole.DisplayRole) -> Any:
    if not index.isValid():
      return None

    if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
      _row = index.row()
      _column = index.column()
      _key = self._columns[_column]
      return self._data[_row][_key]

    return None

  def getData(self) -> list[dict[str, Any]]:
    _data = []
    for i in range(self.rowCount()):
      _rowData = {}
      for j in range(self.columnCount()):
        _columnName = self.headerData(j, Qt.Orientation.Horizontal)
        _value = self.data(self.index(i, j))
        _rowData[_columnName] = _value

      _data.append(_rowData)

    return _data

  def headerData(self, section : int, orientation : Qt.Orientation, role : int = Qt.ItemDataRole.DisplayRole):
    if role != Qt.ItemDataRole.DisplayRole:
      return None

    if orientation == Qt.Orientation.Horizontal:
      return self._columns[section]
    else:
      return section + 1

  def rowCount(self, parent= ...):
    return len(self._data)

  def _dictToList(self, data : dict | None = None):
    _result = []
    for _key, _subDict in data.items():
      _row = {'_key': _key}
      _row.update(_subDict)
      _result.append(_row)

    return _result

class Models:
  def __init__(self):
    self.models = {}

  def defineModels(self):

    # Simple models
    self.models['ALIGNMENT'] = self.defineModel(table='ALIGNMENT')
    self.models['CHALLENGE_RATING'] = self.defineModel(table='CHALLENGE_RATING')
    self.models['CHARACTER'] = self.defineModel(table='CHARACTER')
    self.models['CHARACTER_PROPERTY'] = self.defineModel(table='CHARACTER_PROPERTY')
    self.models['CHARACTER_X_CHARACTER_PROPERTY'] = self.defineModel(table='CHARACTER_X_CHARACTER_PROPERTY')
    self.models['CLASS'] = self.defineClassModel()
    self.models['CLASS_PROPERTY'] = self.defineModel(table='CLASS_PROPERTY')
    self.models['CLIMATE'] = self.defineModel(table='CLIMATE')
    self.models['CLIMATE_X_MONTH_X_PRECIPITATION_CLASS'] = self.defineModel(table='CLIMATE_X_MONTH_X_PRECIPITATION_CLASS')
    self.models['CREATURE_NAME'] = self.defineModel(table='CREATURE_NAME')
    self.models['CREATURE_TYPE'] = self.defineModel(table='CREATURE_TYPE')
    self.models['CREATURE_X_GAME_SYSTEM'] = self.defineModel(table='CREATURE_X_GAME_SYSTEM')
    self.models['CREATURE_X_ENVIRONMENT'] = self.defineModel(table='CREATURE_X_ENVIRONMENT')
    self.models['CONTENT_SOURCE'] = self.defineModel(table='CONTENT_SOURCE')
    self.models['ENVIRONMENT'] = self.defineModel(table='ENVIRONMENT')
    self.models['GAME_SYSTEM'] = self.defineModel(table='GAME_SYSTEM')
    self.models['GAME_PARAMETER'] = self.defineModel(table='GAME_PARAMETER')
    self.models['GAME_PARAMETER_TYPE'] = self.defineModel(table='GAME_PARAMETER_TYPE')
    self.models['ITEM'] = self.defineModel(table='ITEM')
    self.models['ITEM_TYPE'] = self.defineModel(table='ITEM_TYPE')
    self.models['ITEM_PROPERTY'] = self.defineModel(table='ITEM_PROPERTY')
    self.models['ITEM_X_ITEM_PROPERTY'] = self.defineModel(table='ITEM_X_ITEM_PROPERTY')
    self.models['MONTH'] = self.defineModel(table='MONTH')
    self.models['PRECIPITATION_CLASS'] = self.defineModel(table='PRECIPITATION_CLASS')
    self.models['RACE'] = self.defineModel(table='RACE')

    # Models with foreign key support
    self.models['CREATURE_5E'] = self.define5eCreatureModel()
    self.models['CREATURE_OSR'] = self.defineOsrCreatureModel()

    # Other
    self.models['FOUNDRY_DOCUMENTS_DATABASE_ITEMS'] = self.defineFoundryDocumentsDatabaseItemsModel()

  def getColumnIdFromName(self, model, columnName : str) -> int:
    for i in range(model.columnCount()):
      if columnName == model.headerData(i, Qt.Orientation.Horizontal):
        return i

    return -1

  def getColumnNameFromId(self, model, columnId : int) -> str | None:
    return model.headerData(columnId, Qt.Orientation.Horizontal)

  # Returns the value for one specific index
  # The row is determined by applying filterColumns and filterValue
  def getDataForModelIndex(self, model : Any, columnName : str, filterColumns : tuple, filterValues : tuple) -> str | int | bool | None:
    _model = model
    for i in range(_model.rowCount()):
      # Loop over filter columns and determine if the row contains the searched-for value
      _filterValuesFound = 0
      for j, _filterColumn in enumerate(filterColumns):
        _filterColumnId = self.getColumnIdFromName(_model, _filterColumn)
        _value = _model.data(_model.index(i, _filterColumnId))
        if _value == filterValues[j]:
          _filterValuesFound += 1

      if _filterValuesFound == len(filterColumns):
        _dataColumnId = self.getColumnIdFromName(_model, columnName)
        _tValue = _model.data(_model.index(i, _dataColumnId))
        return _tValue

    return None

  # Returns the data for an entire model column
  # Potential filters can be applied to select certain rows from the model
  def getDataForModelColumn(self, model : Any, columnName : str, filterColumn : str ='', filterValue : str ='') -> list:
    _model = model
    _columnId = self.getColumnIdFromName(_model, columnName)
    _valueList = []

    _filterColumnId = -1
    if filterColumn and filterValue:
      _filterColumnId = self.getColumnIdFromName(_model, filterColumn)

    for i in range(_model.rowCount()):
      if filterColumn and filterValue:
        _value = _model.data(_model.index(i, _filterColumnId))
        if _value != filterValue:
          continue

      _value = _model.data(_model.index(i, _columnId))
      _valueList.append(_value)

    return _valueList

  # Returns either
  #   A list of dictionaries containing the data for each column, with the column's names as their keys
  #   A dictionary containing the data, with the column's names as their keys
  def getDataForModelColumns(self, model : Any, columns : list, filterColumn : str ='', filterValue : str ='') -> list | dict:
    _model = model

    _result = []
    _rowData = {}
    for _row in range(_model.rowCount()):
      # Get data for the entire row
      _rowDataRaw = self.getDataForModelRow(model=model, rowIndex=_row, filterColumn=filterColumn, filterValue=filterValue)
      if not _rowDataRaw:
        continue

      if filterColumn:
        if _rowDataRaw[filterColumn] != filterValue:
          continue

      # Filter data by applying the supplied list of columns
      for _key in _rowDataRaw.keys():
        if _key in columns:
          _rowData[_key] = _rowDataRaw[_key]
      _result.append(_rowData)
      _rowData = {}

    if len(_result) == 1:
      return _result[0]
    else:
      return _result

  # Returns the data for an entire model row
  # The row can be selected by either supplying a row index or a filter column and value
  # Both are mutually exclusive while row Index will be treated as a priority
  def getDataForModelRow(self, model : Any, rowIndex : int = -1, filterColumn : str ='', filterValue : str ='') -> dict | None:
    _model = model
    _columnCount = _model.columnCount()
    _rowData = {}

    if rowIndex != -1:
      for i in range(_columnCount):
        _index = _model.index(rowIndex, i)
        _data = _model.data(_index)
        _rowData[_model.headerData(i, Qt.Orientation.Horizontal)] = _data

      return _rowData
    elif filterColumn and filterValue:
      for i in range(_model.columnCount()):
        _columnName = _model.headerData(i, Qt.Orientation.Horizontal)
        _data = self.getDataForModelIndex(model=_model, columnName=_columnName, filterColumns=(filterColumn,), filterValues=(filterValue,))
        _rowData[_columnName] = _data

      return _rowData

    return _rowData

  def defineModel(self, modelType=QSqlTableModel, table=None, fetchAll=True, editStrategy=QSqlTableModel.EditStrategy.OnManualSubmit):
    _model = modelType()
    _model.setTable(table)
    _model.setEditStrategy(editStrategy)
    _model.select()

    for i in range(_model.record().count()):
      _model.setHeaderData(i, Qt.Orientation.Horizontal, _model.record().fieldName(i))

    if fetchAll:
      while _model.canFetchMore():
        _model.fetchMore()

    return _model

  def defineProxyModel(self, modelType=QSortFilterProxyModel, sourceModel=None):
    _model = modelType()
    _model.setSourceModel(dataModels.model(sourceModel))

    while _model.canFetchMore(QModelIndex()):
      _model.fetchMore(QModelIndex())

    return _model

  def define5eCreatureModel(self):
    _gameSystemParameterTypeId = db.getGameParameterTypeId('GAME_SYSTEM')

    _model = QSqlQueryModel()
    _query = f'''
      select
        c.ID,
        c.NAME,
        ct.NAME as TYPE,
        cr.CR as CR,
        a.NAME as ALIGNMENT,
        c.SOURCE,
        ce.ENVIRONMENT_LIST as ENVIRONMENT
      from
        CREATURE c
        left join CREATURE_X_GAME_SYSTEM cgs on c.ID = cgs.CREATURE
        inner join GAME_PARAMETER gp on cgs.GAME_SYSTEM = gp.ID and gp.TYPE = {_gameSystemParameterTypeId} and gp.VALUE_2 = 'D&D 5e'
        left join CREATURE_TYPE ct on c.TYPE = ct.ID
        left join ALIGNMENT a on c.ALIGNMENT = a.ID
        left join CHALLENGE_RATING cr on c.CR = cr.ID
        left join (
          select
            ce.CREATURE,
            group_concat(NAME, ', ') as ENVIRONMENT_LIST
          from
            CREATURE_X_ENVIRONMENT ce
            left join ENVIRONMENT e on ce.ENVIRONMENT = e.ID
          group by
            ce.CREATURE
        ) ce on c.ID = ce.CREATURE        
      order by
        c.ID
    '''
    _model.setQuery(_query)
    _model.setHeaderData(0, Qt.Orientation.Horizontal, 'ID')
    _model.setHeaderData(1, Qt.Orientation.Horizontal, 'NAME')
    _model.setHeaderData(2, Qt.Orientation.Horizontal, 'TYPE')
    _model.setHeaderData(3, Qt.Orientation.Horizontal, 'CR')
    _model.setHeaderData(4, Qt.Orientation.Horizontal, 'ALIGNMENT')
    _model.setHeaderData(5, Qt.Orientation.Horizontal, 'SOURCE')
    _model.setHeaderData(6, Qt.Orientation.Horizontal, 'ENVIRONMENT')

    while _model.canFetchMore():
      _model.fetchMore()

    return _model

  def defineOsrCreatureModel(self):
    _relevantGameSystemNames = "'OSE', 'B/X'"
    _osrGameSystems = db.query(statement=f'select ID from GAME_SYSTEM where NAME_SHORT in ({_relevantGameSystemNames})')
    _osrGameSystemsList = []
    for _system in _osrGameSystems:
      _osrGameSystemsList.append(_system['ID'])

    # Prepare attribute statements
    _gameSystemProperties = db.query(statement=f'''
      select
        gscp.PROPERTY
      from
        GAME_SYSTEM_X_CREATURE_PROPERTY gscp
        inner join GAME_SYSTEM gs on gscp.GAME_SYSTEM = gs.ID and gs.NAME_SHORT in ({_relevantGameSystemNames})
      order by
        gscp.PROPERTY''')

    _propertySqlStatements  = []
    for _property in _gameSystemProperties:
      _statement = f'max(case when gscp.PROPERTY = "{_property['PROPERTY']}" then cgsp.VALUE end) as {_property['PROPERTY']}'
      _propertySqlStatements.append(_statement)

    _propertySqlStatementsStr = ','.join(_propertySqlStatements)

    _query = f'''      
      select distinct
        c.ID,
        c.NAME,
        c.DESCRIPTION,
        c.TRAITS,
        c.GAME_SYSTEM,
        ct.NAME as TYPE,
		    max(case when gscp.PROPERTY = "HD" then cgsp.VALUE end) as HD,
		    max(case when gscp.PROPERTY = "AC" then cgsp.VALUE end) as AC,
		    max(case when gscp.PROPERTY = "ATTACKS" then cgsp.VALUE end) as ATTACKS,
		    max(case when gscp.PROPERTY = "THAC0" then cgsp.VALUE end) as THAC0,
		    max(case when gscp.PROPERTY = "XP" then cgsp.VALUE end) as XP,
		    max(case when gscp.PROPERTY = "SV_HD" then cgsp.VALUE end) as SV_HD,
		    max(case when gscp.PROPERTY = "ST_D" then cgsp.VALUE end) as ST_D,
		    max(case when gscp.PROPERTY = "ST_W" then cgsp.VALUE end) as ST_W,
		    max(case when gscp.PROPERTY = "ST_P" then cgsp.VALUE end) as ST_P,
		    max(case when gscp.PROPERTY = "ST_B" then cgsp.VALUE end) as ST_B,
		    max(case when gscp.PROPERTY = "ST_S" then cgsp.VALUE end) as ST_S,
		    max(case when gscp.PROPERTY = "ALIGNMENT" then cgsp.VALUE end) as ALIGNMENT,
		    replace(group_concat(distinct e.NAME), ',', ', ') as ENVIRONMENT,
        cs.NAME as SOURCE
      from
        GAME_SYSTEM gs
        inner join CREATURE c on gs.ID = c.GAME_SYSTEM		 
		    left join GAME_SYSTEM_X_CREATURE_PROPERTY gscp on gs.ID = gscp.GAME_SYSTEM  
        left join CREATURE_X_GAME_SYSTEM_PROPERTY cgsp on c.ID = cgsp.CREATURE and gscp.ID = cgsp.PROPERTY
        left join CREATURE_TYPE ct on c.TYPE = ct.ID
        left join CONTENT_SOURCE cs on c.SOURCE = cs.ID
		    left join CREATURE_X_ENVIRONMENT ce on c.ID = ce.CREATURE
		    inner join ENVIRONMENT e on ce.ENVIRONMENT = e.ID
		  where 
		    gs.NAME_SHORT in ('OSE', 'B/X')		
      group by
        c.NAME     
      order by
        c.ID
    '''

    _model = QSqlQueryModel()
    _model.setQuery(_query)
    _rc = _model.rowCount()
    while _model.canFetchMore():
      _model.fetchMore()

    return _model

  def defineClassModel(self):
    _query = f'''
      select
        cl.ID,
        cl.NAME,
        cl.USES_MAGIC,
        cl.CUSTOM,
        cl.GAME_SYSTEM
      from
        CLASS cl
      order by
        cl.NAME
    '''

    _model = QSqlQueryModel()
    _model.setQuery(_query)
    _rc = _model.rowCount()
    while _model.canFetchMore():
      _model.fetchMore()

    return _model

  def defineFoundryDocumentsDatabaseItemsModel(self):

    _query = f'''      
      select distinct
        fdk.DOCUMENT_KEY,
        it.NAME,
        itt.NAME as ITEM_TYPE,
        it.CATEGORY, it.COST, it.WEIGHT, it.ATTRIBUTES, it.AC, it.DAMAGE, it.RANGE_SHORT, it.RANGE_MEDIUM, it.RANGE_LONG   
      from
        FOUNDRY_DOCUMENTS fdk
        inner join ITEM it on fdk.ITEM_ID = it.ID
        left join ITEM_TYPE itt on it.TYPE = itt.ID
      order by
        it.NAME;
    '''

    _model = QSqlQueryModel()
    _model.setQuery(_query)
    _rc = _model.rowCount()
    while _model.canFetchMore():
      _model.fetchMore()

    return _model

  def defineTabularDataModel(self, data : list[dict[str, Any]] | None = None, columns : list | None = None):
    return TabularDataModel(data, columns)

  def model(self, name : str) -> QSqlQueryModel | QSqlTableModel | QSqlRelationalTableModel | QSortFilterProxyModel | None:
    if name not in self.models.keys():
      return None

    return self.models[name]

  def modelData(self, modelName, columns=(), one=False):
    if modelName not in self.models:
      return None

    _columns = columns
    if len(_columns) == 0:
      _columns = []
      for i in range(self.models[modelName].columnCount()):
        _colName = self.models[modelName].record().fieldName(i)
        _columns.append(_colName)


    # If only the first row is requested, return a dictionary
    if one and self.models[modelName].rowCount() > 0:
      _data = {}

      for _column in columns:
        _colId = self.models[modelName].record().indexOf(_column)
        _data[_column] = self.models[modelName].data(self.models[modelName].index(0, _colId))

      return _data

    # If all rows are requested, return a list of dictionaries
    _data = []
    for i in range(self.models[modelName].rowCount()):
      _row = {}
      if len(columns) > 0:
        for _column in columns:
          _colId = self.models[modelName].record().indexOf(_column)
          _row[_column] = self.models[modelName].data(self.models[modelName].index(i, _colId))
      else:
        for i in range(self.models[modelName].columnCount()):
          _colId = self.models[modelName].record().indexOf(i)

      _data.append(_row)

    return _data

dataModels = Models()