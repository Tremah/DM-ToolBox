import math

from .ose_rules_data import *
from src.datatypes import *

class BaseCharacterDataModel:
  def __init__(self):
    self.name = TextField()
    #class is a keyword
    self.clas = TextField()
    self.race = TextField()
    self.sex = TextField()
    self.age = IntegerField()
    self.height = IntegerField()
    self.weight = IntegerField()

    self.level = IntegerField()
    self.xp = IntegerField()

    self.hp = IntegerRangeField()
    self.ac = IntegerField()

class OseMovementField:
  def __init__(self, explorationMovementValue=120):
    self.exploration = IntegerField(value=explorationMovementValue)
    self.overland = IntegerField()
    self.encounter = IntegerField()

    self.calculate()

  def calculate(self):
    self.overland.set(math.floor(self.exploration.get() / 5))
    self.encounter.set(math.floor(self.exploration.get() / 3))

  def set(self, explorationMovementValue=120):
    self.exploration.set(explorationMovementValue)
    self.calculate()

  def get(self):
    return{
      'exploration': self.exploration,
      'overland': self.overland,
      'encounter': self.encounter
    }


class OseCharacterDataModel(BaseCharacterDataModel):
  def __init__(self):
    super().__init__()
    self.alignment = TextField()
    self.title = TextField()
    self.startingWealth = IntegerField()

    self.aac = IntegerField()
    self.acBonus = IntegerField()
    self.acUnarmored = IntegerField()
    self.hd = TextField()
    self.hp = IntegerRangeField()
    self.thac0 = IntegerField()
    self.attackMatrix = []
    self.meleeBonus = IntegerField()
    self.missileBonus = IntegerField()

    self.movement = OseMovementField()
    self.saves = {
      'death': IntegerField(),
      'wands': IntegerField(),
      'paralysis': IntegerField(),
      'breath': IntegerField(),
      'spells': IntegerField()
    }
    self.abilities = OseAbilityScores()
    self.adventuringSkills = {
      'forage': IntegerField(),
      'room_trap': IntegerField(),
      'hunt': IntegerField(),
      'listen_door': IntegerField(),
      'open_door': IntegerField(),
      'find_door': IntegerField()
    }
    self.treasure = {
      'cp': IntegerField(),
      'sp': IntegerField(),
      'ep': IntegerField(),
      'gp': IntegerField(),
      'pp': IntegerField()
    }
    self.inventory = [
      {
        'name': TextField(),
        'quantity': QuantityField(),
        'weight': IntegerField()
      }
    ]

  def createCharacter(self):
    self.initCharacter()

  def initCharacter(self, name='', race='', clas='', alignment='', sex='', age=None, height=None, weight=None, level=None, xp=None, hp=None, ac=None):
    self.name.set(name)
    self.race.set(race)
    self.clas.set(clas)
    self.alignment.set(alignment)
    self.sex.set(sex)
    self.age.set(age)
    self.height.set(height)
    self.weight.set(weight)
    self.level.set(level)
    self.xp.set(xp)
    self.hp.set(hp)
    self.ac.set(ac)

  def generateAbilityScores(self):
    self.abilities.generate()

  def getFinalAc(self):
    # ToDo: Move to settings
    #_acType = 'Descending'
    _acType = 'Ascending'

    if _acType == 'Ascending':
      _unArmoredAc = 9
    else:
      _unArmoredAc = 10


