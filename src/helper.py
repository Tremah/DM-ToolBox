import random as rand
import math
import re as re
import json
import csv
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QDialog, QVBoxLayout, QLabel, QDialogButtonBox, QApplication, QMainWindow
from pypdf import PdfReader, PdfWriter

# Classes
class OkCancelDialog(QDialog):
  def __init__(self, title='', text=''):
    super().__init__()

    self.setWindowTitle(title)

    _buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    _buttons.accepted.connect(self.accept)
    _buttons.rejected.connect(self.reject)

    _layout = QVBoxLayout(self)
    _layout.addWidget(QLabel(text))
    _layout.addWidget(_buttons)

# Functions

def coalesce(*values):
  for _value in values:
    if _value:
      return _value

  return None

def fillSqlPlaceholders(statement, values=()):
  _statement = statement
  for _value in values:
    _statement = _statement.replace('?', repr(_value), 1)

  return _statement

def getDirContents(path : Path) -> list:
  return [f for f in path.iterdir()]

def getMainWindow():
  for _widget in QApplication.topLevelWidgets():
    if isinstance(_widget, QMainWindow):
      return _widget

  return None

def isStringAnInteger(string):
  try:
    int(string)
    return True
  except ValueError:
    return False

def makeFileDialog(acceptedFileExtensions : str | list = '', multipleFiles : bool = False, acceptMode : QFileDialog.AcceptMode = QFileDialog.AcceptMode.AcceptOpen, saveFileName : str = '') -> list | None:
  _fileDialog = QFileDialog()

  if acceptedFileExtensions:
    if type(acceptedFileExtensions) is str:
      _fileDialog.setNameFilter(acceptedFileExtensions)
    else:
      _fileDialog.setNameFilters(acceptedFileExtensions)

  _fileDialog.setAcceptMode(acceptMode)

  if acceptMode == QFileDialog.AcceptMode.AcceptOpen:
    _fileDialog.setFileMode(QFileDialog.FileMode.ExistingFile)
    if multipleFiles:
      _fileDialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
  elif acceptMode == QFileDialog.AcceptMode.AcceptSave:
    _fileDialog.setFileMode(QFileDialog.FileMode.AnyFile)

  _fileNames = []
  if _fileDialog.exec_():
    _filenames = _fileDialog.selectedFiles()
    return _filenames

  return None

def readJson(filePath):
  with open(filePath, "r", encoding="utf-8") as _f:
    return json.load(_f)

def readPdf(filePath):
  _pdfReader = PdfReader(filePath)
  _pageCount = len(_pdfReader.pages)

  _fields = _pdfReader.get_fields()
  _listFormatted = '\n'.join(list(_fields.keys()))
  with open('/home/patrick/Desktop/ose_cs_pdf_fields.txt', "w", encoding="utf-8") as _f:
    _f.write(_listFormatted)

  _pages = _pdfReader.pages

  _p = _pdfReader.get_pages_showing_field(_fields['Equipment'])

  _pdfWriter = PdfWriter()
  _pdfWriter.append(_pdfReader)

  _pdfWriter.update_page_form_field_values(_pdfWriter.pages[0], {"Name": "John Doe"}, auto_regenerate=False) #, flatten=True)
  #_pdfWriter.remove_annotations(subtypes='/Widget')

  _pdfWriter.write('/home/patrick/Desktop/test.pdf')
  pass

def rollDice(amount : int, faces : int) -> int:
  if faces == 1:
    return amount

  _sum = 0
  for i in range(amount):
    _dieResult = rand.randint(1, faces) if faces > 1 else 1
    _sum += _dieResult

  return _sum

def rollAbilityScore(mode='3d6DownTheLine', rerollThreshold=5):
  _score = 0
  if mode == '3d6DownTheLine':
    while _score <= rerollThreshold:
      _score = rollDice(3, 6)

  return _score

def shortenFilePath(path, maxLen=50):
  _maxLenHalf = math.floor(maxLen / 2)
  return path if len(path) < maxLen else f'{path[0:_maxLenHalf]}...{path[len(path) - _maxLenHalf:len(path)]}'

def splitDiceRollFormula(formula=''):
  _regexPattern = r'^(\d+)d(\d+)?'
  _parts = re.findall(_regexPattern, formula)

  if _parts:
    return int(_parts[0][0]), int(_parts[0][1])

  return None

# Splits value statement into its components, statement = <die roll>{1} <arithm. operator>{+} <unit>{1}
def splitAndProcessValueStatement(statement=''):
  # Check if statement contains a text at the end and extract/remove it
  _statement = statement.strip()
  _regexPattern = r'.+?\s([a-zA-Z]+)'
  _matches = re.findall(_regexPattern, _statement)

  _appendix = ''
  _appendixLength = 0
  if _matches:
    _appendixLength = len(''.join(_matches))
    _appendix = ' '.join(_matches)

  _statement = _statement[0 : len(_statement) - _appendixLength].strip()

  # Process statement
  _operators = ['+', '-', '*']
  _statementParts = []
  _operator = None
  while True:
    _operatorPos = -1
    for _op in _operators:
      _operator = _op
      _operatorPos = _statement.find(_operator)
      if _operatorPos != -1:
        break

    # No valid operator found
    if _operatorPos == -1:
      _run = False
      break

    _statementParts.append(_statement[0:_operatorPos])
    _statementParts.append(_statement[_operatorPos+1:])
    break

  _dieStatement = ''
  _constantValue = ''
  for _part in _statementParts:
    _regexPattern = r'[0-9]+d[0-9]+'
    _matches = re.findall(_regexPattern, _part)
    if _matches:
      _dieStatement = _matches[0].replace(' ','')
      continue

    _regexPattern = r'[0-9]+'
    _matches = re.findall(_regexPattern, _part)
    if _matches:
      _constantValue = int(_matches[0].replace(' ',''))
      continue

  _sum = 0
  if _dieStatement:
    _amount, _faces = _dieStatement.split('d')
    _sum = rollDice(int(_amount), int(_faces))

  if _constantValue:
    if _operator == '+':
      _sum += _constantValue
    elif _operator == '-':
      _sum -= _constantValue
    elif _operator == '*':
      _sum *= _constantValue

  return [_sum, _appendix]

# Determines contents of a directory recursively
# Returns a list with full file names, including their path as Path()
def traversePath(path):
  _files = [f for f in path.iterdir()]
  _filesInPath = []
  for _file in _files:
    if _file.is_dir():
      _filesInPath.extend(traversePath(_file))
    else:
      _filesInPath.append(_file)

  return _filesInPath

def writeDictToCsv(data : dict, filePath : Path, delimiter : str = ';'):
  with open(filePath, 'w', newline='', encoding='utf-8') as _file:
    _writer = csv.DictWriter(_file, fieldnames=data.keys(), delimiter=delimiter)
    _writer.writeheader()
    _writer.writerow(data)

def writeDictToJson(data : dict, filePath : Path):
  with open(filePath, 'w', encoding='utf-8') as _file:
    json.dump(data, _file, indent=2)

def writeDictToYaml(data : dict, filePath : Path):
  _finalYamlStr = ''
  for _key in data.keys():
    _str = f'{_key}: {str(data[_key])}'
    _finalYamlStr += _str + '\n'

  with open(filePath, 'w', encoding='utf-8') as _file:
    _file.write(_finalYamlStr)