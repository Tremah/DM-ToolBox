import random
from PySide6.QtCore import Qt
from PySide6.QtSql import QSqlQuery
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
  QLineEdit
)

import database as db

class DiceRoller(QWidget):
  def __init__(self):
    super().__init__()

    _diceRollGroupBoxLayout = QGridLayout()
    _diceRollGroupBoxLayout.setAlignment(Qt.AlignmentFlag.AlignTop)
    _diceRollGroupBoxLayout.setSpacing(10)
    _diceRollGroupBoxLayout.addItem(QSpacerItem(10,10), 0, 0)

    # Dice Roll Box

    _dice = db.query(statement='select * from DIE order by FACES')
    _layoutRow = 1
    _layoutColumn = 0
    for _die in _dice:
      # Predefine single roll button and 5 multiple roll buttons per die
      _buttonText = ''
      for _layoutColumn in range(0, 5):
        if _layoutColumn == 0:
          _buttonText = _die["NAME"]
        else:
          _buttonText = str(_layoutColumn + 1)
        _button = QPushButton(f'{_buttonText}')
        _button.setMaximumWidth(60)
        _button.clicked.connect(lambda _, _name=_die["NAME"], _faces=_die['FACES'], _rolls = _layoutColumn + 1: self.rollDie(die=_name, faces=_faces, rolls=_rolls))
        _diceRollGroupBoxLayout.addWidget(_button, _layoutRow, _layoutColumn)
      _customRollsLineEdit = QLineEdit()
      _customRollsLineEdit.setFont(QFont('Ubuntu Mono', 11))
      _customRollsLineEdit.setPlaceholderText('Custom amount')
      _customRollsLineEdit.setMaximumWidth(140)
      _customRollButton = QPushButton('Roll')
      _customRollButton.setMaximumWidth(60)
      _customRollButton.clicked.connect(lambda _, _name = _die["NAME"], _faces = _die['FACES'], _rolls = None, _customRollsLE=_customRollsLineEdit  : self.rollDie(die=_name, faces=_faces, rolls=_rolls, customRollsLineEdit=_customRollsLE))
      _diceRollGroupBoxLayout.addWidget(_customRollsLineEdit, _layoutRow, _layoutColumn + 1)
      _diceRollGroupBoxLayout.addWidget(_customRollButton, _layoutRow, _layoutColumn + 2)
      _layoutRow += 1

    #Custom die faces
    _layoutColumn = 0
    _customDieFacesEdit = QLineEdit()
    _customDieFacesEdit.setFont(QFont('Ubuntu Mono', 11))
    _customDieFacesEdit.setPlaceholderText('Number of faces')
    _customDieFacesEdit.setMaximumWidth(140)
    _customRollsLineEdit = QLineEdit()
    _customRollsLineEdit.setFont(QFont('Ubuntu Mono', 11))
    _customRollsLineEdit.setPlaceholderText('1')
    _customRollsLineEdit.setMaximumWidth(140)
    _customRollButton = QPushButton('Roll')
    _customRollButton.setMaximumWidth(60)
    _customRollButton.clicked.connect(lambda _, _name=f'Custom', _faces=_customDieFacesEdit.text(), _rolls=None, _customRollsLE=_customRollsLineEdit: self.rollDie(die=_name, faces=_faces, rolls=_rolls, facesLE=_customDieFacesEdit, customRollsLineEdit=_customRollsLE))
    _diceRollGroupBoxLayout.addWidget(_customRollsLineEdit, _layoutRow, _layoutColumn)
    _diceRollGroupBoxLayout.addWidget(_customDieFacesEdit, _layoutRow, _layoutColumn + 1)
    _diceRollGroupBoxLayout.addWidget(_customRollButton, _layoutRow, _layoutColumn + 2)

    _diceRollGroupBox = QGroupBox('Dice Roller')
    _diceRollGroupBox.setLayout(_diceRollGroupBoxLayout)

    # Dice Roll Log
    self.logList = QListWidget()
    self.logList.setFont(QFont('Ubuntu Mono', 12))
    _clearLogButton = QPushButton('Clear')
    _clearLogButton.setMaximumWidth(100)
    _clearLogButton.clicked.connect(self.logList.clear)

    _logGroupBoxLayout = QGridLayout()
    _logGroupBoxLayout.addWidget(self.logList, 0, 0)
    _logGroupBoxLayout.addWidget(_clearLogButton, 1, 0)
    _logGroupBox = QGroupBox('Dice Log')
    _logGroupBox.setMaximumWidth(450)
    _logGroupBox.setLayout(_logGroupBoxLayout)

    self.mainGridLayout = QGridLayout()
    self.mainGridLayout.setSpacing(30)
    self.mainGridLayout.addWidget(_diceRollGroupBox, 0, 0)
    self.mainGridLayout.addWidget(_logGroupBox, 0, 1)
    self.setLayout(self.mainGridLayout)

  def rollDie(self, die, faces, rolls, facesLE=None, customRollsLineEdit=None):
    _rolls = rolls
    _die = die

    if customRollsLineEdit is not None:
      _rolls = int(customRollsLineEdit.text())

    # Handle custom amount of faces on a die
    if facesLE is not None:
      faces = int(facesLE.text())
      _die = f'd{faces}'

    _resultsPerLine = 10
    _resultCount = 0
    _line = ''
    _sum = 0
    self.logList.addItem(QListWidgetItem(f'{_rolls}{_die}:'))
    for i in range(_rolls):
      _result = random.randint(1, faces)
      _sum += _result

      if _resultCount == 0:
        _line = f'{_result}'
      else:
        _line = f'{_line}, {_result}'

      if _resultCount in (_resultsPerLine - 1, _rolls - 1):
        self.logList.addItem(QListWidgetItem(_line))
        _line = ''
        _resultCount = 0
      else:
        _resultCount += 1

    if len(_line) != 0:
      self.logList.addItem(QListWidgetItem(_line))

    self.logList.addItem(QListWidgetItem(f'Sum: {_sum}'))
    self.logList.addItem(QListWidgetItem(''))