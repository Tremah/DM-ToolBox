from PySide6.QtCore import Qt, QSortFilterProxyModel, QModelIndex
from PySide6.QtSql import QSqlTableModel, QSqlRelationalTableModel, QSqlRelation, QSqlQueryModel

import database as db

class CreatureProxyModel(QSortFilterProxyModel):
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

      _colId = -1
      for i in range(_sourceModel.columnCount()):
        _name = _sourceModel.headerData(i, Qt.Orientation.Horizontal)
        if _name == _key:
          _colId = i
          break

      _value = _sourceModel.data(_sourceModel.index(source_row, _colId))
      # Debug
      if _value in (124, 1518, 1519):
        pass

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

class DataModels:
  def __init__(self):
    self.models = {}

  def defineModels(self):

    # Simple models
    self.models['ALIGNMENT'] = self.defineModel(table='ALIGNMENT')
    self.models['CHALLENGE_RATING'] = self.defineModel(table='CHALLENGE_RATING')
    self.models['CLIMATE'] = self.defineModel(table='CLIMATE')
    self.models['CLIMATE_X_MONTH_X_PRECIPITATION_CLASS'] = self.defineModel(table='CLIMATE_X_MONTH_X_PRECIPITATION_CLASS')
    self.models['CREATURE_TYPE'] = self.defineModel(table='CREATURE_TYPE')
    self.models['ENVIRONMENT'] = self.defineModel(table='ENVIRONMENT')
    self.models['GAME_SYSTEM'] = self.defineModel(table='GAME_SYSTEM')
    self.models['GAME_PARAMETER'] = self.defineModel(table='GAME_PARAMETER')
    self.models['GAME_PARAMETER_TYPE'] = self.defineModel(table='GAME_PARAMETER_TYPE')
    self.models['MONTH'] = self.defineModel(table='MONTH')
    self.models['PRECIPITATION_CLASS'] = self.defineModel(table='PRECIPITATION_CLASS')

    # Models with foreign key support
    self.models['CREATURE'] = self.defineCreatureModel()
    self.models['CREATURE_X_GAME_SYSTEM'] = self.defineModel(table='CREATURE_X_GAME_SYSTEM')
    self.models['CREATURE_X_ENVIRONMENT'] = self.defineModel(table='CREATURE_X_ENVIRONMENT')

  def columnId(self, modelName, columnName):
    _columnId = self.models[modelName].record().indexOf(columnName)
    return _columnId

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
    _model.setSourceModel(getDataModels().model(sourceModel))

    while _model.canFetchMore(QModelIndex()):
      _model.fetchMore(QModelIndex())

    return _model

  def defineCreatureModel(self):

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

  def model(self, name):
    if name not in self.models:
      return None

    return self.models[name]

  def modelData(self, modelName, columns=(), one=False):
    if modelName not in self.models:
      return None


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
      for _column in columns:
        _colId = self.models[modelName].record().indexOf(_column)
        _row[_column] = self.models[modelName].data(self.models[modelName].index(i, _colId))

      _data.append(_row)

    return _data



dataModels = DataModels()

def getDataModels():
  return dataModels