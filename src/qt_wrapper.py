import logging

from PySide6 import QtGui
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QTextCharFormat, QTextCursor, QTextBlockUserData, QCursor, QPainter, QColor
from PySide6.QtWidgets import (
  QPushButton,
  QGridLayout,
  QHBoxLayout,
  QSizePolicy,
  QSpacerItem,
  QAbstractItemView,
  QGroupBox,
  QComboBox, QTableView, QListView, QWidget, QTextEdit, QVBoxLayout, QMenu, QWidgetAction, QInputDialog, QLabel,
  QSpinBox, QDialog
)

from src import data_models as dm

class CreatureFilterGroupBox(QGroupBox):
  def __init__(self, title, applyFilterMethod, setCreatureModelMethod, resetFormMethod):
    super().__init__()

    # UI Control
    _standardWidth = 400
    _standardHeight = 250

    # Get relevant data models
    _dataModels = dm.dataModels

    # Define models and filter
    self.systemModel = _dataModels.model('GAME_SYSTEM')
    self.creatureModel = _dataModels.model('CREATURE_OSR')
    self.nameModel = _dataModels.defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_OSR')
    self.typeModel = _dataModels.model('CREATURE_TYPE')
    self.challengeRatingModel = _dataModels.model('CHALLENGE_RATING')
    self.alignmentModel = _dataModels.model('ALIGNMENT')
    self.environmentModel = _dataModels.model('ENVIRONMENT')
    self.creatureGameSystemModel = _dataModels.defineProxyModel(modelType=dm.CreatureGameSystemProxyModel, sourceModel='CREATURE_OSR')
    self.sourceModel = _dataModels.model('CONTENT_SOURCE')
    self.creatureEnvironmentModel = _dataModels.model('CREATURE_X_ENVIRONMENT')

    # Define filters
    self.systemFilter = self.defineFilter(QComboBox, self.systemModel, None, (_standardWidth, _standardHeight), 'NAME_SHORT')
    self.nameFilter = self.defineFilter(QListView, self.nameModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'NAME')
    self.typeFilter = self.defineFilter(QListView, self.typeModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'NAME')
    self.crFilter = self.defineFilter(QListView, self.challengeRatingModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'CR')
    self.alignmentFilter = self.defineFilter(QListView, self.alignmentModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'NAME')
    self.environmentFilter = self.defineFilter(QListView, self.environmentModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'NAME')
    self.sourceFilter = self.defineFilter(QListView, self.sourceModel, QAbstractItemView.SelectionMode.MultiSelection, (_standardWidth, _standardHeight), 'NAME')

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
    if model != self.nameModel:
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

    _items['TYPE'] = dm.dataModels.modelData(modelName='CREATURE_TYPE', columns=('NAME',))
    _items['CR'] = dm.dataModels.modelData(modelName='CHALLENGE_RATING', columns=('CR',))
    _items['ALIGNMENT'] = dm.dataModels.modelData(modelName='ALIGNMENT', columns=('NAME',))
    _items['ENVIRONMENT'] = dm.dataModels.modelData(modelName='ENVIRONMENT', columns=('NAME',))
    _items['SOURCE'] = dm.dataModels.modelData(modelName='CONTENT_SOURCE', columns=('NAME',))

    return _items

  def handleSystemComboBoxChanged(self):
    ## Handle data changes based upon game system box ##

    # Select all creatures that belong to the selected system
    _gameSystemId = self.systemModel.data(self.systemModel.index(self.systemFilter.currentIndex(), self.systemModel.record().indexOf('ID'), self.systemFilter.rootModelIndex()))

    self.creatureGameSystemModel.setGameSystem(_gameSystemId)

    # Construct filter statement from creatures belonging to the selected game system
    # and apply to creature model
    _ids = {'ID': []}
    for i in range (self.creatureGameSystemModel.rowCount()):
      _ids['ID'].append(self.creatureGameSystemModel.data(self.creatureGameSystemModel.index(i, self.creatureGameSystemModel.sourceModel().record().indexOf('ID'))))

    _dataModels = dm.dataModels
    if self.systemFilter.currentText() in ('OSE', 'B/X'):
      self.creatureModel = _dataModels.model('CREATURE_OSR')
      self.nameModel = _dataModels.defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_OSR')
      self.creatureGameSystemModel = _dataModels.defineProxyModel(modelType=dm.CreatureGameSystemProxyModel, sourceModel='CREATURE_OSR')
    elif self.systemFilter.currentText() in ('D&D 5e'):
      self.creatureModel = _dataModels.model('CREATURE_5E')
      self.nameModel = _dataModels.defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_5E')
      self.creatureGameSystemModel = _dataModels.defineProxyModel(modelType=dm.CreatureGameSystemProxyModel, sourceModel='CREATURE_5E')

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

    ## Source box
    _filterValues = self.getValuesFromColumn(columnName='SOURCE')
    if _filterValues:
      _filter = 'content_source.NAME in ("' + '","'.join([str(_value) for _value in _filterValues]) + '")'
      self.sourceModel.setFilter(_filter)
    else:
      self.sourceModel.setFilter('1=2')
    self.sourceModel.select()

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

    _filterValues['SOURCE'] = []
    for _index in self.sourceFilter.selectionModel().selectedIndexes():
      _row = _index.row()
      _value = self.sourceModel.data(self.sourceModel.index(_index.row(), self.sourceModel.record().indexOf('NAME')))
      _filterValues['SOURCE'].append(_value)

    _filterValues['ENVIRONMENT'] = []
    for _index in self.environmentFilter.selectionModel().selectedIndexes():
      _row = _index.row()
      _value = self.environmentModel.data(self.environmentModel.index(_index.row(), self.environmentModel.record().indexOf('NAME')))
      _filterValues['ENVIRONMENT'].append(_value)

    return _filterValues

class DataTable(QTableView):
  def __init__(self, model='', lastSectionStretch=False):
    super().__init__()

    #self.setModel(dm.dataModels.defineProxyModel(modelType=dm.CreatureProxyModel, sourceModel='CREATURE_5E'))

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
      self.setModel(dm.dataModels.defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_OSR'))
    elif model in ('D&D 5e'):
      self.setModel(dm.dataModels.defineProxyModel(modelType=dm.CreatureNameProxyModel, sourceModel='CREATURE_5E'))

    self.hideColumns()

  def hideColumns(self):
    for _column in range(self.model().columnCount()):
      _columnName = self.model().headerData(_column, Qt.Orientation.Horizontal)

      if _columnName in ('ID', 'GAME_SYSTEM', 'SV_HD', 'ST_D', 'ST_W', 'ST_P', 'ST_B', 'ST_S', 'XP', 'DESCRIPTION', 'ALIGNMENT', 'TRAITS'):
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

class RichTextEditorTextEdit(QTextEdit):
  class BlockFormat(QTextBlockUserData):
    def __init__(self, type='', headingLevel=0, id=0):
      super().__init__()
      self.type = type
      self.headingLevel = headingLevel
      self.id = id

    def __str__(self):
      return f'type={self.type}, headingLevel={self.headingLevel}, id={self.id}'


  def __init__(self, parent=None):
    super().__init__(parent)

    # Fields

    # Keeps track of if a block is a heading or normal text
    # Fragment formats are being tracked with a mapping to html tags in the output text
    # TYPE = 'heading', 'text'
    self.blockFormats = []
    self.blockFormats.append(self.BlockFormat(type='text'))
    self.defaultFmt = self.textCursor().charFormat()

    self.setTabStopDistance(20)
    self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)

    self.setMinimumHeight(300)

  def applyFormatToCursor(self, cursor, fmtAction):
    _fmt = cursor.charFormat()
    if fmtAction == 'bold':
      _fmt.setFontWeight(QFont.Weight.Normal if _fmt.fontWeight() == QFont.Weight.Bold else QFont.Weight.Bold)
    elif fmtAction == 'italic':
      _fmt.setFontItalic(not _fmt.fontItalic())
    elif fmtAction == 'underline':
      _fmt.setFontUnderline(not _fmt.fontUnderline())

    cursor.mergeCharFormat(_fmt)
    self.mergeCurrentCharFormat(_fmt)
    self.setFocus()

  def applyFormatToCursorSelection(self, selectionStart, selectionEnd, fmtAction):
    _selectionStart = selectionStart
    _selectionEnd = selectionEnd

    _block = self.document().findBlock(_selectionStart)

    _selectionHasBold = False
    _selectionIsBold = True
    _selectionHasItalic = False
    _selectionIsItalic = True
    _selectionHasUnderlined = False
    _selectionIsUnderlined = True

    while _block.isValid():
      _blockStart = _block.position()
      _blockEnd = _blockStart + _block.length()

      _it = _block.begin()

      while not _it.atEnd():
        _fragment = _it.fragment()
        if _fragment.isValid():
          _fragmentText = _fragment.text()
          _fragmentStartPos = _fragment.position()
          _fragmentEndPos = _fragment.position() + _fragment.length()

          # Fragment is within the selection
          if (_fragmentStartPos < _selectionStart and _fragmentEndPos -1 < _selectionStart) or _fragmentStartPos + 1 > _selectionEnd:
            _it += 1
            continue

          _start = _fragmentStartPos
          _end = _selectionEnd
          if _fragmentStartPos < _selectionStart:
            _start = _selectionStart
          if _fragmentEndPos < _selectionEnd:
            _end = _fragmentEndPos

          _tmpCursor = QTextCursor(_block.document())
          _fmt = self.getSelectionFormat(_tmpCursor, _start, _end)

          _isBold = True if _fmt.fontWeight() == QFont.Weight.Bold else False
          _isItalic = _fmt.fontItalic()
          _isUnderline = _fmt.fontUnderline()

          if _isBold:
            _selectionHasBold = True
          else:
            _selectionIsBold = False
          if _isItalic:
            _selectionHasItalic = True
          else:
            _selectionIsItalic = False
          if _isUnderline:
            _selectionHasUnderlined = True
          else:
            _selectionIsUnderlined = False

        _it += 1

      _block = _block.next()

    _tmpCursor = QTextCursor(_block.document())
    _tmpCursor.setPosition(_selectionStart)
    _tmpCursor.setPosition(_selectionEnd, QTextCursor.MoveMode.KeepAnchor)
    _fmt = _tmpCursor.charFormat()

    if fmtAction == 'bold':
      if _selectionIsBold:
        _fmt.setFontWeight(QFont.Weight.Normal)
      elif _selectionHasBold:
        _fmt.setFontWeight(QFont.Weight.Bold)
      else:
        _fmt.setFontWeight(QFont.Weight.Bold)
    elif fmtAction == 'italic':
      if _selectionIsItalic:
        _fmt.setFontItalic(False)
      elif _selectionHasItalic:
        _fmt.setFontItalic(True)
      else:
        _fmt.setFontItalic(True)
    elif fmtAction == 'underline':
      if _selectionIsUnderlined:
        _fmt.setFontUnderline(False)
      elif _selectionHasUnderlined:
        _fmt.setFontUnderline(True)
      else:
        _fmt.setFontUnderline(True)

    _tmpCursor.mergeCharFormat(_fmt)

  def getSelectionFormat(self, cursor, selectionStart, selectionEnd):
    _tmpCursor = cursor
    _tmpCursor.setPosition(selectionStart)
    _tmpCursor.setPosition(selectionStart, QTextCursor.MoveMode.KeepAnchor)

    return _tmpCursor.charFormat()

  def handleDelete(self, cursorPosBeforeKeyPress):
    self.syncInternalBlockFormatWithDocument()
    self.blockFormats = self.blockFormats[0:self.document().blockCount()]

  def handleNewLine(self, cursorInHeading=False, atBlockStart=False):
    if len(self.blockFormats) == self.document().blockCount():
      return

    _cursor = self.getCursor()
    _docBlock = _cursor.block()

    if cursorInHeading:
      _blockFormat = _docBlock.blockFormat()
      _blockFormat.setHeadingLevel(0)

      if atBlockStart:
        _previousBlock = _docBlock.previous()
        _previousBlockFormat = _previousBlock.blockFormat()
        _docBlockHeadingLevel = _previousBlock.blockFormat().headingLevel()
        _blockFormat.setHeadingLevel(_docBlockHeadingLevel)

        _previousBlockFormat.setHeadingLevel(0)
        _previousCursor = QTextCursor(_previousBlock)
        _previousCursor.setBlockFormat(_previousBlockFormat)
        _cursor.setBlockFormat(_blockFormat)
      else:
        _cursor.setBlockFormat(_blockFormat)
        _fmt = self.defaultFmt
        _cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        _cursor.setCharFormat(_fmt)

    _docBlock = self.document().firstBlock()

    self.syncInternalBlockFormatWithDocument()

  def getCursor(self):
    return self.textCursor()

    ## OVERRIDES ##
  def insertFromMimeData(self, source):
    super().insertFromMimeData(source)
    self.syncInternalBlockFormatWithDocument()

  def keyPressEvent(self, event):
    # Save the cursor's position before QT handles the key event
    # Determine if the cursor was at the start or the end of the block ->
    # Important for handling new line on a block containing a heading

    _cursor = self.getCursor()
    _blockBeforeKeyPress = _cursor.block()
    _cursorPosBeforeKeyPress = _cursor.position()
    _cursorInHeading = True if _blockBeforeKeyPress.blockFormat().headingLevel() != 0 else False
    _atBlockStart = True if _cursor.position() == _blockBeforeKeyPress.position() else False

    super().keyPressEvent(event)

    if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
      self.handleNewLine(_cursorInHeading, _atBlockStart)
    elif event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
      self.handleDelete(_cursorPosBeforeKeyPress)

  def printBlock(self, block, blockFormat=None):
    logging.debug(f'Block {block.blockNumber()}:')
    logging.debug(f'QT block info: position={block.position()}, length={block.length()}, qt heading level={block.blockFormat().headingLevel()}')
    if blockFormat:
      logging.debug(f'Internal block format: {blockFormat}')
    else:
      logging.debug(f'Block {block.blockNumber()} has no internal block format')
    logging.debug(f'Text: {block.text()}')
    logging.debug('------------------------')

  def printBlocks(self):
    logging.debug(f'Document block count: {self.document().blockCount()}')
    _block = self.document().firstBlock()
    while _block.isValid():
      _blockNumber = _block.blockNumber()
      _blockFormat = next((_bf for _bf in self.blockFormats if _bf.id == _blockNumber), None)
      self.printBlock(_block, _blockFormat)
      _block = _block.next()

    logging.debug('======================')

  def syncInternalBlockFormatWithDocument(self):
    _docBlock = self.document().firstBlock()
    while _docBlock.isValid():
      _docBlockNum = _docBlock.blockNumber()
      _docBlockFormat = _docBlock.blockFormat()
      _blockFormatInternal = next((_bF for _bF in self.blockFormats if _bF.id == _docBlockNum), None)

      _docBlockHeadingLevel = _docBlock.blockFormat().headingLevel()
      _type = 'heading' if _docBlockHeadingLevel > 0 else 'text'

      if not _blockFormatInternal:
        _blockFormatInternal = self.BlockFormat(id=_docBlockNum, type=_type, headingLevel=_docBlockHeadingLevel)
        self.blockFormats.insert(_docBlockNum, _blockFormatInternal)
      else:
        self.blockFormats[_docBlockNum].id = _docBlockNum
        self.blockFormats[_docBlockNum].type = _type
        self.blockFormats[_docBlockNum].headingLevel = _docBlockHeadingLevel

      _docBlock = _docBlock.next()

  def setHtml(self, _htmlStr):
    # Set html via base method
    super().setHtml(_htmlStr)
    self.syncInternalBlockFormatWithDocument()

  def toHtml(self):
    if self.document().blockCount() > 0 and self.document().firstBlock().text():
      _blockCount = self.document().blockCount()

      _block = _block = self.document().firstBlock()
      _htmlStrTotal = ''
      while (_block.isValid() and _blockCount > 1) or (_block.isValid() and _block.text()):
        _blockFormatInternal = self.blockFormats[_block.blockNumber()]

        # Enrich text with HTML tags depending on their block data and format
        _htmlStrBlock = ''
        if _blockFormatInternal.type == 'heading':
          _headingLevel = _blockFormatInternal.headingLevel
          _headingString = f'<h{_headingLevel}>{_block.text()}</h{_headingLevel}>'
          _htmlStrTotal += f'{_headingString}'
        else:
          _htmlStrBlock += '<div>'
          # Loop over fragments in block and enrich based on char format
          _it = _block.begin()
          while not _it.atEnd():
            _fragment = _it.fragment()
            _fragmentText = _fragment.text()

            _fmt = _fragment.charFormat()
            _isBold = True if _fmt.fontWeight() == QtGui.QFont.Weight.Bold else False
            _isItalic = _fmt.fontItalic()
            _isUnderlined = _fmt.fontUnderline()

            _htmlStrBlock += '<b>' if _isBold else ''
            _htmlStrBlock += '<i>' if _isItalic else ''
            _htmlStrBlock += '<u>' if _isUnderlined else ''

            _htmlStrBlock += _fragmentText

            _htmlStrBlock += '</b>' if _isBold else ''
            _htmlStrBlock += '</i>' if _isItalic else ''
            _htmlStrBlock += '</u>' if _isUnderlined else ''

            _it += 1
          _htmlStrTotal += f'{_htmlStrBlock}</div>'
        _block = _block.next()
      return _htmlStrTotal

    return None


# ToDo: Removing text decoration doesn't work

class RichTextEditor(QWidget):

  def __init__(self, parent=None, mode='edit'):
    super().__init__(parent)

    # Fields
    self.headingProperties = {
      'H1': {
        'fontSize': 20,
        'bold': True,
        'margin': 10
      },
      'H2': {
        'fontSize': 18,
        'bold': True,
        'margin': 8
      },
      'H3': {
        'fontSize': 16,
        'bold': True,
      },
      'H4': {
        'fontSize': 14,
        'bold': False,
      }
    }

    self.mode = mode

    self.editor = RichTextEditorTextEdit(self)
    self.editor.setObjectName('richTextEditor')
    self.editor.cursorPositionChanged.connect(self.handleEditorCursorPosChanged)

    # Text Formatting Buttons
    _toolbarButtonMaxWidth = 25
    _toolbarButtonMaxHeight = 25

    self.boldButton = QPushButton('B')
    self.boldButton.clicked.connect(self.handleBoldButton)
    self.boldButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    self.boldButton.setFixedSize(_toolbarButtonMaxWidth, _toolbarButtonMaxHeight)
    self.boldButton.setToolTip('Bold')
    self.boldButton.setFont(QFont('', weight=QFont.Weight.Bold))
    self.boldButton.setCheckable(True)

    self.italicButton = QPushButton('I')
    self.italicButton.clicked.connect(self.handleItalicButton)
    self.italicButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    self.italicButton.setFixedSize(_toolbarButtonMaxWidth, _toolbarButtonMaxHeight)
    self.italicButton.setToolTip('Italic')
    self.italicButton.setFont(QFont('', italic=True))
    self.italicButton.setCheckable(True)

    self.underlineButton = QPushButton('U')
    self.underlineButton.clicked.connect(self.handleUnderlineButton)
    self.underlineButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    self.underlineButton.setFixedSize(_toolbarButtonMaxWidth, _toolbarButtonMaxHeight)
    self.underlineButton.setToolTip('Underline')

    _font = self.underlineButton.font()
    _font.setUnderline(True)
    self.underlineButton.setFont(_font)
    self.underlineButton.setCheckable(True)

    # Heading Combo Box
    self.headingComboBox = QComboBox()
    self.headingComboBox.setToolTip('Heading')
    self.headingComboBox.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    self.headingComboBox.addItem('Clear')
    self.headingComboBox.addItem('H1')
    self.headingComboBox.addItem('H2')
    self.headingComboBox.addItem('H3')
    self.headingComboBox.addItem('H4')
    self.headingComboBox.activated.connect(self.handleHeadingComboBoxActivated)
    self.headingComboBox.setCurrentIndex(1)

    # Table button
    self.insertTableButton = QPushButton('T')
    self.insertTableButton.clicked.connect(self.handleInsertTableButton)
    self.insertTableButton.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    self.insertTableButton.setFixedSize(_toolbarButtonMaxWidth, _toolbarButtonMaxHeight)
    self.insertTableButton.setToolTip('Table')

    # Finish Setup
    _toolbarLayout = QGridLayout()
    _toolbarLayout.setSpacing(2)
    _toolbarLayout.setContentsMargins(0, 0, 0, 0)
    _toolbarLayout.addWidget(self.boldButton, 0, 0)
    _toolbarLayout.addWidget(self.italicButton, 0, 1)
    _toolbarLayout.addWidget(self.underlineButton, 0, 2)
    _toolbarLayout.addWidget(self.headingComboBox, 0, 3)
    _toolbarLayout.addWidget(self.insertTableButton, 0, 4)
    _toolbarLayout.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum), 0, 5)

    _mainLayout = QVBoxLayout()
    _mainLayout.setContentsMargins(0, 0, 0, 0)
    _mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    if self.mode == 'edit':
      _mainLayout.addLayout(_toolbarLayout)
    else:
      self.editor.setReadOnly(True)
    _mainLayout.addWidget(self.editor)

    self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    self.setLayout(_mainLayout)

  def clear(self):
    self.editor.clear()

  def handleHeadingComboBoxActivated(self):
    if self.headingComboBox.currentText() == 'Clear':
      return

    _cursor = self.editor.getCursor()
    _block = _cursor.block()
    _selectedHeadingLevel = int(self.headingComboBox.currentText()[1:])

    _cursor.beginEditBlock()

    for _bF in self.editor.blockFormats:
      if _bF.id == _block.blockNumber():
        _bF.type = 'heading'
        _bF.headingLevel = _selectedHeadingLevel

        _qtBf = _block.blockFormat()
        _qtBf.setHeadingLevel(_selectedHeadingLevel)

        _cursor.setBlockFormat(_qtBf)

    _fmt = self.getHeadingFormat(_selectedHeadingLevel)

    _cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
    _cursor.setCharFormat(_fmt)

    _cursor.endEditBlock()

  def handleBoldButton(self):
    self.applyFormat(fmtAction='bold')

  def handleEditorCursorPosChanged(self):
    _cursor = self.editor.getCursor()
    _fmt = _cursor.charFormat()

    if _fmt.fontWeight() == QFont.Weight.Bold:
      self.boldButton.setChecked(True)
    else:
      self.boldButton.setChecked(False)

    if _fmt.fontItalic():
      self.italicButton.setChecked(True)
    else:
      self.italicButton.setChecked(False)

    if _fmt.fontUnderline():
      self.underlineButton.setChecked(True)
    else:
      self.underlineButton.setChecked(False)

  def handleItalicButton(self):
    self.applyFormat(fmtAction='italic')

  def handleUnderlineButton(self):
    self.applyFormat(fmtAction='underline')

  def handleInsertTableButton(self):
    _tableHelper = TableHelperWidget()

    _menu = QMenu(self)
    _action = QWidgetAction(_menu)
    _action.setDefaultWidget(_tableHelper)
    _menu.addAction(_action)

    _menu.exec(QCursor().pos())

  def applyFormat(self, fmtAction='None'):
    _cursor = self.editor.getCursor()
    _fmt = None
    if not _cursor.hasSelection():
      self.editor.applyFormatToCursor(_cursor, fmtAction)
    else:
      self.editor.applyFormatToCursorSelection(_cursor.selectionStart(), _cursor.selectionEnd(), fmtAction)

  def getHeadingFormat(self, headingLevel):
    _headingProperties = self.headingProperties[f'H{headingLevel}']

    _fmt = QTextCharFormat()
    _fmt.setFontWeight(QFont.Weight.Bold)
    _fmt.setFontPointSize(_headingProperties['fontSize'])

    return _fmt

  def setHtml(self, html : str):
    self.editor.setHtml(html)

  def toHtml(self):
    return self.editor.toHtml()

class SelectTableSizeWidget(QDialog):
  def __init__(self, parent=None):
    super().__init__(parent)

    _rowLabel = QLabel('Rows: ')
    self.rowSpinBox = QSpinBox()
    self.rowSpinBox.setMinimum(1)
    self.rowSpinBox.setMaximum(99)
    _columnLabel = QLabel('Columns: ')
    self.columnSpinBox = QSpinBox()
    self.columnSpinBox.setMinimum(1)
    self.columnSpinBox.setMaximum(99)

    _insertTableButton = QPushButton('Insert Table')
    _insertTableButton.clicked.connect(self.accept)
    _cancelButton = QPushButton('Cancel')
    _cancelButton.clicked.connect(self.reject)

    _mainLayout = QGridLayout()
    _mainLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _mainLayout.setSpacing(5)
    _mainLayout.addWidget(_rowLabel, 0, 0)
    _mainLayout.addWidget(self.rowSpinBox, 0, 1)
    _mainLayout.addWidget(_columnLabel, 1, 0)
    _mainLayout.addWidget(self.columnSpinBox, 1, 1)
    _mainLayout.addWidget(_insertTableButton, 2, 0)
    _mainLayout.addWidget(_cancelButton, 2, 1)
    self.setLayout(_mainLayout)

    self.setWindowTitle('Select Table Size')
    self.setWindowModality(Qt.WindowModality.ApplicationModal)
    self.setMinimumSize(300, 200)

  def values(self):
    return self.rowSpinBox.value(), self.columnSpinBox.value()

  def handleInsertTableButton(self, index=None):
    self.close()

class TableHelperWidget(QWidget):
  sizeSelected = Signal(int, int)

  def __init__(self, maxRows=10, maxColumns=10, cellSize=20, parent=None):
    super().__init__(parent)

    self.maxRows = maxRows
    self.maxColumns = maxColumns
    self.cellSize = cellSize

    self.currentHoveredRow = 0
    self.currentHoveredColumn = 0

    self.setMouseTracking(True)
    self.setFixedSize(maxColumns * cellSize, maxRows * cellSize)

  def mouseMoveEvent(self, event):
    self.currentHoveredColumn = (event.position().x() // self.cellSize) + 1
    self.currentHoveredRow = (event.position().y() // self.cellSize) + 1
    self.update()

  def leaveEvent(self, event):
    self.currentHoveredRow = self.currentHoveredRow = 0
    self.update()

  def mousePressEvent(self, event):
    if self.currentHoveredRow and self.currentHoveredColumn:
      self.sizeSelected.emit(self.currentHoveredRow, self.currentHoveredColumn)

  def paintEvent(self, event):
    _painter = QPainter(self)
    for _row in range(self.maxRows):
      for _column in range(self.maxColumns):
        x = _column * self.cellSize
        y = _row * self.cellSize

        if _row < self.currentHoveredRow and _column < self.currentHoveredColumn:
          # Fills the rects to highlight the dimensions of the current selection
          _painter.fillRect(x, y, self.cellSize -1, self.cellSize -1, QColor("#cce4ff"))
        _painter.drawRect(x, y, self.cellSize -1, self.cellSize -1)