import random as rand
import re as re

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