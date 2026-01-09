import src.helper as hlp
from src.datatypes import *

OseClasses = [
  'Cleric',
  'Dwarf',
  'Elf',
  'Fighter',
  'Halfling',
  'Magic-User'
  'Thief',
]

OseAbilityScoreLinks = {
  'strength': [
    {
      'name': 'skills.open_door',
      'values': {
        8: 1,
        12: 2,
        15: 3,
        17: 4,
        18: 5
      }
    },
    {
      'name': 'combat.melee.bonus',
      'values': {
        3: -3,
        5: -2,
        8: -1,
        12: 0,
        15: 1,
        17: 2,
        18: 3
      }
    }
  ],
  'intelligence': [
    {
      'name': 'literacy.label',
      'values': {
        5: 'Illiterate',
        8: 'Basic',
        18: 'Literate'
      }
    },
    {
      'name': 'literacy.speech',
      'values': {
        3: 'Native (broken speech)',
        18: 'Native',

      }
    },
    {
      'name': 'literacy.additional_languages',
      'values': {
        12: 0,
        15: 1,
        17: 2,
        18: 1,
      }
    }
  ],
  'wisdom': [
    {
      'name': 'saves.magic.bonus',
      'values': {
        3: -3,
        5: -2,
        8: -1,
        12: 0,
        15: 1,
        17: 2,
        18: 3
      }
    }
  ],
  'dexterity': [
    {
      'name': 'combat.ac.bonus',
      'values': {
        3: -3,
        5: -2,
        8: -1,
        12: 0,
        15: 1,
        17: 2,
        18: 3
      }
    },
    {
      'name': 'combat.missile.bonus',
      'values': {
        3: -3,
        5: -2,
        8: -1,
        12: 0,
        15: 1,
        17: 2,
        18: 3
      }
    },
    {
      'name': 'combat.initiative.bonus',
      'values': {
        3: -2,
        8: -1,
        12: 0,
        17: 1,
        18: 2
      }
    }
  ],
  'constitution': [
    {
      'name': 'hp',
      'values': {
        3: -3,
        5: -2,
        8: -1,
        12: 0,
        15: 1,
        17: 2,
        18: 3
      }
    }
  ],
  'charisma': [
    {
      'name': 'npc.reactions',
      'values': {
        3: -2,
        8: -1,
        12: 0,
        17: 1,
        18: 2
      }
    },
    {
      'name': 'retainers.max',
      'values': {
        3: 1,
        5: 2,
        8: 3,
        12: 4,
        15: 5,
        17: 6,
        18: 7
      }
    },
    {
      'name': 'retainers.loyalty',
      'values': {
        3: 4,
        5: 5,
        8: 6,
        12: 7,
        15: 8,
        17: 9,
        18: 10
      }
    }
  ]
}

OseSavingThrows = [
  {
    'class': 'cleric',
    'saves': {
      4: [11, 12, 14, 16, 15],
      8: [9, 10, 12, 14, 12],
      12: [6, 7, 9, 11, 9],
      14: [3, 5, 7, 8, 7]
    }
  },
  {
    'class': 'dwarf',
    'saves': {
      3: [8, 9, 10, 13, 12],
      6: [6, 7, 8, 10, 10],
      9: [4, 5, 6, 7, 8],
      12: [2, 3, 4, 4, 6]
    }
  },
  {
    'class': 'elf',
    'saves': {
      3: [12, 13, 13, 15, 15],
      6: [10, 11, 11, 13, 12],
      9: [8, 9, 9, 10, 10],
      10: [6, 7, 8, 8, 8]
    }
  },
  {
    'class': 'fighter',
    'saves': {
      3: [12, 13, 14, 15, 16],
      6: [10, 11, 12, 13, 14],
      9: [8, 9, 10, 10, 12],
      12: [6, 7, 8, 8, 10],
      14: [4, 5, 6, 5, 8],
    }
  },
  {
    'class': 'halfling',
    'saves': {
      3: [8, 9, 10, 13, 12],
      6: [6, 7, 8, 10, 10],
      7: [4, 5, 6, 7, 8],
    }
  },
  {
    'class': 'magic-user',
    'saves': {
      5: [13, 14, 13, 16, 15],
      10: [11, 12, 11, 14, 12],
      14: [8, 9, 8, 11, 8],
    }
  },
  {
    'class': 'thief',
    'saves': {
      4: [13, 14, 13, 16, 15],
      8: [12, 13, 11, 14, 13],
      12: [10, 11, 9, 12, 10],
      14: [8, 9, 7, 10, 8]
    }
  }
]

'''
self.adventuringSkills = {
  'forage': IntegerField(),
  'room_trap': IntegerField(),
  'hunt': IntegerField(),
  'listen_door': IntegerField(),
  'open_door': IntegerField(),
  'find_door': IntegerField()
}
'''

class OseAbilityScoreLink:
  def __init__(self, name=None, value=None):
    self.name = TextField()
    self.value = TextField()
    self.name.set(name)
    self.value.set(value)

  def set(self, name, value):
    self.value.set(value)
    self.name.set(name)

  def get(self):
    return {
      'name': self.name.get(),
      'value': self.value.get()
    }

class OseAbilityScore:
  def __init__(self, name=None, score=None):
    self.name = TextField()
    self.score = IntegerField()
    self.links = []

    self.name.set(name if name else self.name.default())
    self.score.set(score if score else self.score.default())

  def set(self, name, score):
    self.name.set(name)
    self.score.set(score)
    self.links = OseAbilityScoreLinks[self.name.get()]

  def addLink(self, link):
    self.links.append(OseAbilityScoreLink(link.get['name'], link.get['value']))

  def get(self):
    return {
      'name': self.name.get(),
      'score': self.score.get(),
      'links': self.links
    }

class OseAbilityScores:
  def __init__(self, generate=False):
    self.scores = {
      'strength': OseAbilityScore(),
      'intelligence': OseAbilityScore(),
      'wisdom': OseAbilityScore(),
      'dexterity': OseAbilityScore(),
      'constitution': OseAbilityScore(),
      'charisma': OseAbilityScore()
    }
    self.formula = '3d6'

    if generate:
      self.generate()

  def set(self, scores=None):
    if scores:
      self.scores = scores

  def get(self):
    return self.scores

  def generate(self):
    _formulaParts = hlp.splitDiceRollFormula(self.formula)
    for _key in self.scores.keys():
      self.scores[_key].set(name=_key, score=hlp.rollDice(_formulaParts[0], _formulaParts[1]))

