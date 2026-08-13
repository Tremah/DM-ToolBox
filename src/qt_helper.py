import json
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QGroupBox, QTableView, QStyledItemDelegate

# Classes


class TableViewColumnCenterContentDelegate(QStyledItemDelegate):

  def initStyleOption(self, option, index):
    super().initStyleOption(option, index)
    option.displayAlignment = Qt.AlignmentFlag.AlignCenter

class TableViewColumnLeftContentDelegate(QStyledItemDelegate):

  def initStyleOption(self, option, index):
    super().initStyleOption(option, index)
    option.displayAlignment = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

# Functions

def clearLayout(layout):
  while layout.count():
    _item = layout.takeAt(0)

    if _item.widget():
      _widget = _item.widget()
      _widget.setParent(None)
      _widget.deleteLater()
    elif _item.layout():
      clearLayout(_item.layout())
      _item.layout().setParent(None)

# Modifies the given layout and returns a modified, compacted copy of it
def deleteRowFromGridLayout(layout, row : int):
  if layout.count() == 0 or layout.rowCount() < row:
    return

  for i in reversed(range(layout.count())):
    _row, _column, _rowSpan, _columnSpan = layout.getItemPosition(i)

    if _row != row:
      continue

    _item = layout.takeAt(i)

    if _item.widget():
      _widget = _item.widget()
      _widget.setParent(None)
      _widget.deleteLater()
    elif _item.layout():
      _layout = _item.layout()
      clearLayout(_item.layout())

  # Rebuild the old layout into a new one to keep integrity
  return rebuildLayout(layout)

# Creates a QTableWidget from a dictionary representation
def deserializeTableWidgetFromDict(srcDict : dict):
  _columns = srcDict['COLUMNS']
  _rows = srcDict['ROWS']

  _tableWidget = QTableWidget()
  _tableWidget.setColumnCount(len(_columns))
  _tableWidget.setRowCount(len(_rows))
  _tableWidget.setHorizontalHeaderLabels(_columns)

  for _i, _row in enumerate(_rows):
    for _j, _value in enumerate(_row):
      _tableWidget.setItem(_i, _j, QTableWidgetItem(_value))

  return _tableWidget

# Creates a QTableWidget from a JSON string representation
def deserializeTableWidgetFromJson(jsonStr : str):
  _dict = json.loads(jsonStr)
  _columns = _dict['COLUMNS']
  _rows = _dict['ROWS']

  _tableWidget = QTableWidget()
  _tableWidget.setColumnCount(len(_columns))
  _tableWidget.setRowCount(len(_rows))
  _tableWidget.setHorizontalHeaderLabels(_columns)

  for _i, _row in enumerate(_rows):
    for _j, _value in enumerate(_row):
      _tableWidget.setItem(_i, _j, QTableWidgetItem(_value))

  return _tableWidget

def getColumnIdFromTableWidget(table : QTableWidget, columnName : str) -> int | None :
  for i in range(table.columnCount()):
    if table.horizontalHeaderItem(i).text() == columnName:
      return i

  return None

# Returns a single value (str) from a table widget cell
def getDataForTableWidgetCell(table : QTableWidget, rowId : int, columnName : str) -> Any:
  _columnId = getColumnIdFromTableWidget(table, columnName)

  _item = table.item(rowId, _columnId)
  if _item:
    return _item.text() or ''

  _widget = table.cellWidget(rowId, _columnId)
  if _widget:
    return _widget

  return None

# Returns a list of values for the given column
# The order of rows is guaranteed to be preserved
def getDataForTableWidgetColumn(table : QTableWidget, columnName : str) -> list:
  _data = []
  _columnId = getColumnIdFromTableWidget(table, columnName)
  for i in range(table.rowCount()):
    _cellContent = getDataForTableWidgetCell(table, i, columnName)
    _data.append(_cellContent)

  return _data

# Returns a dictionary with the column names as keys
def getDataForTableWidgetRow(table : QTableWidget, rowId : int) -> dict[str, Any]:
  _data = {}
  for i in range(table.columnCount()):
    _columnName = table.horizontalHeaderItem(i).text()
    _cellContent = getDataForTableWidgetCell(table, rowId, _columnName)
    _data[_columnName] = _cellContent

  return _data

# Returns a list of dictionaries with the column names as keys
# The order of rows is guaranteed to be preserved
def getDataForTableWidget(table: QTableWidget, columns : list[str] | None = None) -> list[dict[str, Any]]:
  _data = []
  for i in range(table.rowCount()):
    _row = {}
    for j in range(table.columnCount()):
      _columnName = table.horizontalHeaderItem(j).text()
      if columns and _columnName not in columns:
        continue
      _value = getDataForTableWidgetCell(table, i, _columnName)
      _row[_columnName] = _value

    _data.append(_row)

  return _data

def getItemsFromGridLayoutRow(layout : QGridLayout, row : int):
  _items = []
  for i in range(layout.count()):
    _row, _column, _rowSpan, _columnSpan = layout.getItemPosition(i)
    if _row == row:
      _items.append(layout.itemAt(i))

  return _items

def getSelectedRowsFromTable(table : QTableView | QTableWidget) -> list:
  _rows = []
  for _row in table.selectionModel().selectedRows():
    _rows.append(_row.row())

  return _rows

def findChildByProperty(widget, searchType : Any, propertyName : str, propertyValue : Any) -> Any | None:
  for _child in widget.findChildren(searchType):
    if _child.property(propertyName) == propertyValue:
      return _child

  return None

def iterateLayoutWidgets(layout):
  for i in range(layout.count()):
    _item = layout.itemAt(i)
    if _item.widget():
      if type(_item.widget()) == QGroupBox:
        yield from iterateLayoutWidgets(_item.widget().layout())
      yield _item.widget()
      continue

    if _item.layout():
      yield from iterateLayoutWidgets(_item.layout())

def loadDataIntoTableWidget(table : QTableWidget, data : list[dict[str, Any]]):
  _rowCount = table.rowCount()
  for i, _data in enumerate(data):
    table.setRowCount(_rowCount + 1)
    for _key, _value in _data.items():
      if isinstance(_value, QWidget):
        table.setCellWidget(i, getColumnIdFromTableWidget(table, _key), _value)
      else:
        table.setItem(i, getColumnIdFromTableWidget(table, _key), QTableWidgetItem(str(_value)))
    _rowCount += 1

def printLayoutContents(layout):
  print(f'Layout type: {type(layout)}')

  _row=0
  _column=0
  _rowSpan=0
  _columnSpan=0

  for i in range(layout.count()):
    _item = layout.itemAt(i)
    _name = None
    if type(layout) == QGridLayout:
      _row, _column, _rowSpan, _columnSpan = layout.getItemPosition(i)
    _str = ''
    if _item.widget():
      _str = str(_item.widget())
    elif _item.layout():
      print('Entering sublayout')
      printLayoutContents(_item.layout())
      print('Exiting sublayout')
      _str = str(_item.layout())
    elif _item.spacerItem():
      _str = str(_item.spacerItem())

    if _item.widget() or _item.layout():
      _name = _item.widget().property('name') if _item.widget() else _item.layout().property('name')

    if type(layout) == QGridLayout:
      _str = f'(item: {_str}, row: {_row}, column: {_column}), rowspan: {_rowSpan}, colspan: {_columnSpan}, name: {_name}'
    else:
      _str = f'(item: {_str}), index: {i}, name: {_name}'
    print(_str)

def rebuildLayout(layout):
  _newLayout = type(layout)()
  _newLayout.setContentsMargins(layout.contentsMargins())
  _newLayout.setSpacing(layout.spacing())
  _newLayout.setAlignment(layout.alignment())

  for _property in layout.dynamicPropertyNames():
    _newLayout.setProperty(_property.data().decode(), layout.property(_property.data().decode()))

  _newGridRow = -1
  _currentOldGridRow = -1
  while layout.count():
    if type(layout) == QGridLayout:
      _row, _column, _rowSpan, _columnSpan = layout.getItemPosition(0)
      _item = layout.takeAt(0)

      if _currentOldGridRow != _row:
        _currentOldGridRow = _row
        _newGridRow += 1

      if _item.widget():
        _widget = _item.widget()
        _newLayout.addWidget(_widget, _newGridRow, _column, _rowSpan, _columnSpan)
      elif _item.layout():
        _newLayout.addLayout(rebuildLayout(_item.layout()), _newGridRow, _column, _rowSpan, _columnSpan)
      elif _item.spacerItem():
        _newLayout.addItem(_item.spacerItem(), _newGridRow, _column, _rowSpan, _columnSpan)
    elif type(layout) in (QHBoxLayout, QVBoxLayout):
      _item = layout.takeAt(0)
      if _item.widget():
        _newLayout.addWidget(_item.widget())
      elif _item.layout():
        _newLayout.addLayout(rebuildLayout(_item.layout()))
      elif _item.spacerItem():
        _newLayout.addItem(_item.spacerItem())

  return _newLayout

# Returns a dictionary representation of a QTableWidget
# The dictionary contains of a key "COLUMNS" and a key "ROWS"
# The "COLUMNS" key contains a list of column names in the order they appear in the table
# The "ROWS" key contains a list of lists, each containing the values of a row
def serializeTableWidgetToDict(tableWidget : QTableWidget):
  _columns = []
  for i in range(tableWidget.horizontalHeader().count()):
    _columns.append(tableWidget.horizontalHeaderItem(i).text())

  # Gather data
  _tableData = []
  _rowData = []
  for i in range(tableWidget.rowCount()):
    for j in range(len(_columns)):
      _value = tableWidget.item(i, j).text()
      _rowData.append(_value)
    _tableData.append(_rowData)
    _rowData = []

  _dict = {'COLUMNS': _columns, 'ROWS': _tableData}

  return _dict

# Returns a JSON string representation of a QTableWidget
# The JSON contains of a dictionary with keys "COLUMNS" and "ROWS"
def serializeTableWidgetToJson(tableWidget : QTableWidget):
  _dict = serializeTableWidgetToDict(tableWidget)
  _json = json.dumps(_dict, indent=2)
  return _json

def updateLayoutOnWidget(widget, layout):
  _tmpWidget = QWidget()
  _tmpWidget.setLayout(widget.layout())
  _tmpWidget.deleteLater()

  widget.setLayout(layout)

