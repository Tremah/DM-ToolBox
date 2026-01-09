import random as rand
import math
import re as re
from pathlib import Path

def rollDice(amount, faces):
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
  # Extract relevant parts of the statement
  # (\d+(?:d\d+)?) = die statement
  # ([+\-*x]\s?\d+)? = optional constant value
  # ?(.*) = unit, i.e. cp, levels, magic item
  _statement = ' '.join(statement.split())
  _regexPattern = r'(\d+(?:d\d+)?) ?([+\-*x]\s?\d+)? ?(.*)'
  _matches = re.findall(_regexPattern, _statement)

  _dieComponent = _matches[0][0]
  _constantValueComponent = _matches[0][1]
  _unitComponent = _matches[0][2]

  # Roll die
  if _dieComponent.find('d') != -1:
    _numberOfDice, _dieFaces = _dieComponent.split('d')
    _dieResult = rollDice(int(_numberOfDice), int(_dieFaces))
  else:
    _dieResult = int(_dieComponent)

  # Handle constant value part
  if len(_constantValueComponent) > 0:
    _operator, _constantValue = _constantValueComponent.split()
    if _operator == '+':
      _dieResult += int(_constantValue)
    elif _operator == '-':
      _dieResult -= int(_constantValue)
    elif _operator == '*' or _operator == 'x':
      _dieResult *= int(_constantValue)

  return [_dieResult, _unitComponent]

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