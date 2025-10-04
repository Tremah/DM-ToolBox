from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
  QPushButton,
  QGridLayout,
  QHBoxLayout,
  QSizePolicy,
  QSpacerItem,
  QAbstractItemView,
  QGroupBox,
  QComboBox, QTableView, QListView
)

import data_models as dm

class CreatureFilterGroupBox(QGroupBox):
  def __init__(self, title, applyFilterMethod, setCreatureModelMethod, resetFormMethod):
    super().__init__()

    # UI Control
    _standardWidth = 400
    _standardHeight = 250

    # Get relevant data models
    _dataModels = dm.getDataModels()

    # Define models and filter
    self.systemModel = _dataModels.model('GAME_SYSTEM')
    self.creatureModel = _dataModels.model('CREATURE_OSR')
    self.nameModel = _dataModels.defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_OSR')
    self.typeModel = _dataModels.model('CREATURE_TYPE')
    self.challengeRatingModel = _dataModels.model('CHALLENGE_RATING')
    self.alignmentModel = _dataModels.model('ALIGNMENT')
    self.environmentModel = _dataModels.model('ENVIRONMENT')
    self.creatureGameSystemModel = _dataModels.defineProxyModel(modelType=dm.CreatureGameSystemProxyModel, sourceModel='CREATURE_OSR')
    self.sourceModel = _dataModels.defineProxyModel(modelType=dm.CreatureSourceProxyModel, sourceModel='CREATURE_OSR')
    self.creatureEnvironmentModel = _dataModels.model('CREATURE_X_ENVIRONMENT')

    # Define filters
    self.systemFilter = self.defineFilter(QComboBox, self.systemModel, None, (_standardWidth, _standardHeight), 'NAME_SHORT')
    self.nameFilter = self.defineFilter(QListView, self.nameModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'NAME')
    self.typeFilter = self.defineFilter(QListView, self.typeModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'NAME')
    self.crFilter = self.defineFilter(QListView, self.challengeRatingModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'CR')
    self.alignmentFilter = self.defineFilter(QListView, self.alignmentModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'NAME')
    self.environmentFilter = self.defineFilter(QListView, self.environmentModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'NAME')
    self.sourceFilter = self.defineFilter(QListView, self.sourceModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'SOURCE')

    self.systemFilter.currentTextChanged.connect(lambda newValue: self.handleSystemComboBoxChanged(newValue=newValue))
    self.systemFilter.currentTextChanged.connect(lambda newValue: applyFilterMethod(filterValues=self.evaluateFilters()))
    self.systemFilter.currentTextChanged.connect(lambda newValue: setCreatureModelMethod(model=newValue))

    # Set default model for data table
    setCreatureModelMethod(model='OSE')

    # Define filter groups
    # System
    _systemFilterGroup = self.defineFilterGroup('Game System')
    self.addFilterToGroup(_systemFilterGroup, self.systemFilter)
    # Name
    _nameFilterGroup = self.defineFilterGroup('Creature Name')
    _nameFilterGroup.setMinimumWidth(400)
    self.addFilterToGroup(_nameFilterGroup, self.nameFilter)
    # Type
    _typeFilterGroup = self.defineFilterGroup('Type')
    self.addFilterToGroup(_typeFilterGroup, self.typeFilter)
    # CR
    self.crFilterGroup = self.defineFilterGroup('Challenge Rating')
    self.addFilterToGroup(self.crFilterGroup, self.crFilter)
    # Alignment
    _alignmentFilterGroup = self.defineFilterGroup('Alignment')
    self.addFilterToGroup(_alignmentFilterGroup, self.alignmentFilter)
    # Source
    _sourceFilterGroup = self.defineFilterGroup('Source')
    self.addFilterToGroup(_sourceFilterGroup, self.sourceFilter)
    # Environment
    _environmentFilterGroup = self.defineFilterGroup('Environment')
    self.addFilterToGroup(_environmentFilterGroup, self.environmentFilter)

    # Signals for filter widgets
    self.nameFilter.selectionModel().selectionChanged.connect(lambda selected, deselected : self.handleNameFilterSelectionChanged(selected, deselected))

    # Apply Filter button
    _applyFilterButton = QPushButton('Apply Filter')
    _applyFilterButton.setMinimumWidth(100)

    # First executes self.evaluateFilters() and then the method given via applyFilterMethod constructor argument
    _applyFilterButton.clicked.connect(lambda clicked: applyFilterMethod(filterValues=self.evaluateFilters()))

    # Reset Filter button
    _resetFilterButton = QPushButton('Reset Filter')
    _resetFilterButton.setMinimumWidth(100)
    _resetFilterButton.clicked.connect(self.resetFilter)

    # Clear Form button
    _clearFormButton = QPushButton('Clear All Fields And Tables')
    _clearFormButton.setMinimumWidth(200)
    _clearFormButton.clicked.connect(resetFormMethod)

    # Apply and Filter button layout
    _buttonHboxLayout = QHBoxLayout()
    _buttonHboxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    _buttonHboxLayout.setSpacing(20)
    _buttonHboxLayout.addWidget(_applyFilterButton)
    _buttonHboxLayout.addWidget(_resetFilterButton)
    _buttonHboxLayout.addWidget(_clearFormButton)
    _buttonHboxLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

    # Main grid layout
    _mainGridLayout = QGridLayout()
    _mainGridLayout.setSpacing(30)
    _mainGridLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
    _mainGridLayout.addWidget(_systemFilterGroup, 1, 0)
    _mainGridLayout.addWidget(_nameFilterGroup, 2, 0)
    _mainGridLayout.addWidget(_typeFilterGroup, 2, 1)
    _mainGridLayout.addWidget(_alignmentFilterGroup, 2, 2)
    _mainGridLayout.addWidget(_sourceFilterGroup, 2, 3)
    _mainGridLayout.addWidget(_environmentFilterGroup, 2, 4)
    _mainGridLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum), 2, 5)
    _mainGridLayout.addLayout(_buttonHboxLayout, 3, 0)
    _mainGridLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding), 4, 0)

    _mainGridLayout.setColumnStretch(0, 2)
    _mainGridLayout.setColumnStretch(1, 1)
    _mainGridLayout.setColumnStretch(2, 1)
    _mainGridLayout.setColumnStretch(3, 1)
    _mainGridLayout.setColumnStretch(4, 3)

    # Finish Setup
    self.setTitle(title)
    self.setLayout(_mainGridLayout)

    # Initialize UI-Elements
    self.handleSystemComboBoxChanged()

  def defineFilter(self, filterWidget, model, selectionMode, maximumSize, valueField):
    _filter = filterWidget()
    _filter.setModel(model)
    if model not in (self.nameModel, self.sourceModel):
      _filter.setModelColumn(model.record().indexOf(valueField))
    else:
      _filter.setModelColumn(model.sourceModel().record().indexOf(valueField))

    if filterWidget == QListView:
      _filter.setSelectionMode(selectionMode)

    return _filter

  def defineFilterGroup(self, title):
    _groupBoxLayout = QGridLayout()
    _groupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignLeft)

    _groupBox = QGroupBox()
    _groupBox.setTitle(title)
    _groupBox.setLayout(_groupBoxLayout)

    return _groupBox

  def getFilterItems(self):
    _items = {'GAME_SYSTEM': [self.systemModel.data(self.systemModel.index(self.systemFilter.currentIndex(), self.systemModel.record().indexOf('ID'), self.systemFilter.rootModelIndex()))], 'ID': []}

    _items['ID'] = []
    _colId = self.nameModel.sourceModel().record().indexOf('ID')
    for i in range(self.nameModel.rowCount()):
      _items['ID'].append(self.nameModel.data(self.nameModel.index(i, _colId)))

    _items['TYPE'] = dm.getDataModels().modelData(modelName='CREATURE_TYPE', columns=('NAME',))
    _items['CR'] = dm.getDataModels().modelData(modelName='CHALLENGE_RATING', columns=('CR',))
    _items['ALIGNMENT'] = dm.getDataModels().modelData(modelName='ALIGNMENT', columns=('NAME',))
    _items['ENVIRONMENT'] = dm.getDataModels().modelData(modelName='ENVIRONMENT', columns=('NAME',))
    _items['SOURCE'] = dm.getDataModels().modelData(modelName='ENVIRONMENT', columns=('NAME',))

    return _items

  def handleSystemComboBoxChanged(self, newValue='', logicalOp='and', append=True):
    ## Handle data changes based upon game system box ##

    # Select all creatures that belong to the selected system
    _gameSystemId = self.systemModel.data(self.systemModel.index(self.systemFilter.currentIndex(), self.systemModel.record().indexOf('ID'), self.systemFilter.rootModelIndex()))

    self.creatureGameSystemModel.setGameSystem(_gameSystemId)

    # Construct filter statement from creatures belonging to the selected game system
    # and apply to creature model
    _ids = {'ID': []}
    for i in range (self.creatureGameSystemModel.rowCount()):
      _ids['ID'].append(self.creatureGameSystemModel.data(self.creatureGameSystemModel.index(i, self.creatureGameSystemModel.sourceModel().record().indexOf('ID'))))

    _dataModels = dm.getDataModels()
    if self.systemFilter.currentText() in ('OSE', 'B/X'):
      self.creatureModel = _dataModels.model('CREATURE_OSR')
      self.nameModel = _dataModels.defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_OSR')
      self.creatureGameSystemModel = _dataModels.defineProxyModel(modelType=dm.CreatureGameSystemProxyModel, sourceModel='CREATURE_OSR')
      self.sourceModel = _dataModels.defineProxyModel(modelType=dm.CreatureSourceProxyModel, sourceModel='CREATURE_OSR')
    elif self.systemFilter.currentText() in ('D&D 5e'):
      self.creatureModel = _dataModels.model('CREATURE_5E')
      self.nameModel = _dataModels.defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_5E')
      self.creatureGameSystemModel = _dataModels.defineProxyModel(modelType=dm.CreatureGameSystemProxyModel, sourceModel='CREATURE_5E')
      self.sourceModel = _dataModels.defineProxyModel(modelType=dm.CreatureSourceProxyModel, sourceModel='CREATURE_5E')

    # Populate the name filter with data based on the game system combo box

    if len(_ids['ID']) > 0:
      self.nameModel.setFilterValues(_ids)
    else:
      self.nameModel.setFilterValues(None)

    self.nameFilter.setModel(self.nameModel)
    self.handleNameFilterSelectionChanged()
    ### Handle UI changes based on selected values

    if self.systemFilter.currentText() != 'D&D 5e':
      self.crFilterGroup.hide()
    else:
      self.crFilterGroup.show()

  def handleNameFilterSelectionChanged(self, oldSelection=None, newSelection=None):
    ## Type box
    _filterValues = self.getValuesFromColumn(columnName='TYPE')
    if _filterValues:
      _filter = 'creature_type.NAME in ("' + '","'.join([str(_value) for _value in _filterValues]) + '")'
      self.typeModel.setFilter(_filter)
    else:
      self.typeModel.setFilter('1=2')
    self.typeModel.select()

    ## Challenge Rating box
    _filterValues = self.getValuesFromColumn(columnName='CR')
    if _filterValues:
      _filter = 'challenge_rating.CR in ("' + '","'.join([str(_value) for _value in _filterValues]) + '")'
      self.challengeRatingModel.setFilter(_filter)
    else:
      self.challengeRatingModel.setFilter('1=2')
    self.challengeRatingModel.select()

    ## Alignment box
    _filterValues = self.getValuesFromColumn(columnName='ALIGNMENT')
    if _filterValues:
      _filter = 'alignment.NAME in ("' + '","'.join([str(_value) for _value in _filterValues]) + '")'
      self.alignmentModel.setFilter(_filter)
    else:
      self.alignmentModel.setFilter('1=2')
    self.alignmentModel.select()

    ## Environment box
    _creatures = self.getValuesFromColumn(columnName='ID')
    if _creatures:
      _filter = 'CREATURE in (' + ','.join([str(_creature) for _creature in _creatures]) + ')'
      self.creatureEnvironmentModel.setFilter(_filter)
    else:
      self.creatureEnvironmentModel.setFilter('1=2')
    self.creatureEnvironmentModel.select()

    while self.creatureEnvironmentModel.canFetchMore():
      self.creatureEnvironmentModel.fetchMore()

    # Select environments from environment model, based on the ids from the junction table above
    _environments = []
    for i in range(self.creatureEnvironmentModel.rowCount()):
      _value = self.creatureEnvironmentModel.data(self.creatureEnvironmentModel.index(i, self.creatureEnvironmentModel.record().indexOf('ENVIRONMENT')))
      if _value not in _environments:
        _environments.append(_value)

    if _environments:
      _environmentFilter = 'ID in (' + ','.join([str(_environment) for _environment in _environments]) + ')'
      self.environmentModel.setFilter(_environmentFilter)
    else:
      self.environmentModel.setFilter('1=2')

    self.environmentModel.select()

  def getColumnIdFromHeader(self, columnName):
    _colId = -1
    for i in range(self.creatureModel.record().count()):
      _header = self.creatureModel.headerData(i, Qt.Orientation.Horizontal)
      if _header == columnName:
        _colId = i
        break

    return _colId

  # Returns values from the creature model for the available creatures in the name filter
  def getValuesFromColumn(self, columnName):
    _colId = self.getColumnIdFromHeader(columnName)

    if _colId == -1:
      return []

    # Construct filter statement from selected creatures for given column
    _values = []
    for _index in self.nameFilter.selectionModel().selectedIndexes():
      _value = self.creatureModel.data(self.nameModel.index(_index.row(), _colId))
      if _value not in _values:
        _values.append(_value)

    # No creatures have been selected but the name filter box is not empty either
    # Select all values of given creatures from the model
    if not _values and self.nameModel.rowCount() != 0:
      for i in range(self.nameModel.rowCount()):
        # _colId = self.creatureModel.headerData(self.creatureModel.record().indexOf('TYPE'), Qt.Orientation.Horizontal)
        _value = self.creatureModel.data(self.creatureModel.index(i, _colId))
        if _value not in _values:
          _values.append(_value)

    return _values

  def addFilterToGroup(self, groupWidget, filterWidget):
    groupWidget.layout().addWidget(filterWidget)

  def resetFilter(self):
   self.nameFilter.clearSelection()

  def evaluateFilters(self):
    ## Gather all selected values from filter boxes

    _columns = {}
    for i in range(self.creatureModel.record().count()):
      _header = self.creatureModel.headerData(i, Qt.Orientation.Horizontal)
      _columns[_header] = i

    _filterValues = {}

    _filterValues['ID'] = []
    for _index in self.nameFilter.selectionModel().selectedIndexes():
      _value = self.nameModel.data(self.nameModel.index(_index.row(), self.creatureModel.record().indexOf('ID')))
      _filterValues['ID'].append(_value)

    if not _filterValues['ID']:
      _gameSystemId = self.systemModel.data(self.systemModel.index(self.systemFilter.currentIndex(), self.systemModel.record().indexOf('ID'), self.systemFilter.rootModelIndex()))
      for i in range(self.creatureGameSystemModel.rowCount()):
        _filterValues['ID'].append(self.creatureGameSystemModel.data(self.creatureGameSystemModel.index(i, self.creatureGameSystemModel.sourceModel().record().indexOf('CREATURE'))))

    _filterValues['TYPE'] = []
    for _index in self.typeFilter.selectionModel().selectedIndexes():
      _row = _index.row()
      _value = self.typeModel.data(self.typeModel.index(_index.row(), self.typeModel.record().indexOf('NAME')))
      _filterValues['TYPE'].append(_value)

    _filterValues['CR'] = []
    for _index in self.crFilter.selectionModel().selectedIndexes():
      _row = _index.row()
      _value = self.challengeRatingModel.data(self.challengeRatingModel.index(_index.row(), self.challengeRatingModel.record().indexOf('CR')))
      _filterValues['CR'].append(_value)

    _filterValues['ALIGNMENT'] = []
    for _index in self.alignmentFilter.selectionModel().selectedIndexes():
      _row = _index.row()
      _value = self.alignmentModel.data(self.alignmentModel.index(_index.row(), self.alignmentModel.record().indexOf('NAME')))
      _filterValues['ALIGNMENT'].append(_value)

    _filterValues['ENVIRONMENT'] = []
    for _index in self.environmentFilter.selectionModel().selectedIndexes():
      _row = _index.row()
      _value = self.environmentModel.data(self.environmentModel.index(_index.row(), self.environmentModel.record().indexOf('NAME')))
      _filterValues['ENVIRONMENT'].append(_value)

    return _filterValues

class DataTable(QTableView):
  def __init__(self, model='', lastSectionStretch=False):
    super().__init__()

    #self.setModel(dm.getDataModels().defineProxyModel(modelType=dm.CreatureProxyModel, sourceModel='CREATURE_5E'))

    #_proxyModel = QSortFilterProxyModel()
    #_proxyModel.setSourceModel(dm.DataModels().model('CREATURE'))
    #self.setModel(_proxyModel)

    # Table layout and design
    self.setAlternatingRowColors(True)
    #if lastSectionStretch:
    self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
    self.horizontalHeader().setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
    self.horizontalHeader().setStretchLastSection(True)

  def setDataModel(self, model):
    if model in ('OSE', 'B/X'):
      self.setModel(dm.getDataModels().defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_OSR'))
    elif model in ('D&D 5e'):
      self.setModel(dm.getDataModels().defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_5E'))

    self.hideColumns()

  def hideColumns(self):
    for _column in range(self.model().columnCount()):
      _columnName = self.model().headerData(_column, Qt.Orientation.Horizontal)

      if _columnName in ('ID', 'GAME_SYSTEM', 'SV_HD', 'ST_D', 'ST_W', 'ST_P', 'ST_B', 'ST_S', 'XP', 'SOURCE', 'ALIGNMENT'):
        self.hideColumn(_column)

  def getColumnIndexFromName(self, name):
    return self.model().record().indexOf(name)

  def filterTable(self, filterValues=None):
    if not filterValues:
      return

    self.model().setFilterValues(filterValues)
    self.horizontalHeader().setStretchLastSection(True)

  def invalidateAllRows(self):
    self.model().setFilterValues(None)

  def getColumNameFromIndex(self, index):
    return ''

  def addColumn(self, name='', position=0, width=100, alignment=Qt.AlignmentFlag.AlignLeft):
    pass

  def removeColumn(self, name):
    pass

  def clearColumn(self, name):
    pass

  def columnExists(self, name):

    return False

  def getValueFromKey(self, table, valueField, keyField, keyValue):
    return 0

  def clearFilter(self):
    pass

  def getRows(self, onlySelectedRows=False, selectColumns=None):
    return []

  def addDataToTable(self, rows=(), clear=False):
   pass
