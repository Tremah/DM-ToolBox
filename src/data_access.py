from pathlib import Path
from typing import Any
import logging
import pathlib as path

import helper as hlp
import app_config as apc

class GameSystemData:
  # Important file paths
  rulesPath = apc.ROOT_INPUT_PATH / 'rules'

  # Stores all available game systems
  gameSystems = ['ose']
  gameSystemDataStorage = {
    'ose': {
      'label': 'Old-School Essentials',
      'classDataPath': rulesPath / 'ose' / 'classes'
    }
  }

  def __init__(self):
    self.classDefinitions = {}
    self.classData = {}
    self.characterDefinition = {}

    self.initStorage()
    self.readAndRegisterClassFiles()
    self.registerCharacterDefinition(self.rulesPath / 'ose' / 'character_definition.json')

  # Checks if a class exists for a game system
  def classExistsForGameSystem(self, gameSystem : str, className : str) -> bool:
    if not self.gameSystemExists(gameSystem):
      return False

    return className.lower() in self.classData[gameSystem.lower()]

  # Checks if a game system exists
  def gameSystemExists(self, gameSystem : str) -> bool:
    return gameSystem.lower() in self.gameSystems

  # Returns all classes for a game system in a dictionary
  def getAllClassesForGameSystem(self, gameSystem : str) -> dict | None:
    return self.classData.get(gameSystem.lower())

  def getCharacterDefinition(self) -> dict | None:
    return self.characterDefinition

  # Returns a specific class for a game system in a dictionary
  def getClass(self, gameSystem : str, className : str) -> dict | None:
    _classes = self.getAllClassesForGameSystem(gameSystem)
    if _classes is None:
      return None

    return _classes.get(className.lower())

  def getClassDefinition(self, gameSystem : str) -> dict | None:
    return self.classDefinitions.get(gameSystem.lower())

  # Returns a specific property for a class
  def getClassProperty(self, gameSystem : str, className : str, propertyName : str) -> Any | None:
    _class = self.getClass(gameSystem, className)
    if _class is None:
      return None

    return _class.get(propertyName.lower())

  # Returns multiple properties for a class as a dict
  # If a property is not found, it is included in the result with a value of None
  def getClassProperties(self, gameSystem : str, className : str, propertyNames : tuple) -> dict[str, Any] | None:
    _class = self.getClass(gameSystem, className)
    if _class is None:
      return None

    _result = {}
    for _propertyName in propertyNames:
      _result[_propertyName] = _class.get(_propertyName.lower())

    return _result

  # Initializes the storage
  def initStorage(self):
    for _system in self.gameSystems:
      self.classData[_system] = {}
      self.registerClassDefinition(_system)

  def readAndRegisterClassFiles(self):
    for _system in self.gameSystems:
      _systemData = self.gameSystemDataStorage.get(_system)
      if _systemData is None:
        logging.error(f'Game system {_system} is not registered.')
        continue

      _filePath = _systemData.get('classDataPath')
      if _filePath is None:
        logging.error(f'No class data path found for game system {_systemData.get("label")}.')
        continue

      if not _filePath.exists():
        logging.error(f'Class data path {_filePath} does not exist for game system {_systemData.get("label")}.')
        continue

      for _file in hlp.getDirContents(_filePath):
        if _file.stem == '_definition':
          continue

        self.registerClass(_system, _file)

  # Registers a class for a game system
  def registerClass(self, gameSystem : str, filePath : Path) -> bool:
    _gameSystemLower = gameSystem.lower()
    _classDefinition = hlp.readJson(filePath)
    _classNameLower = _classDefinition['name'].lower()

    # Game system is not registered
    if not self.gameSystemExists(_gameSystemLower):
      logging.error(f'Game system {gameSystem} is not registered.')
      return False

    # Class already registered
    if self.classExistsForGameSystem(_gameSystemLower, _classNameLower):
      logging.error(f'Class "{_classNameLower.title()}" for game system {gameSystem} is already registered.')
      return False

    _classDefinition = hlp.readJson(filePath)
    if not self.verifyClassIntegrity(_gameSystemLower, _classNameLower, _classDefinition):
      logging.error(f'Class definition for class "{_classNameLower.title()}" for game system {_gameSystemLower} is not valid.')
      return False

    self.classData[_gameSystemLower][_classNameLower] = _classDefinition
    return True

  def registerCharacterDefinition(self, filePath : Path) -> dict | None:
    self.characterDefinition = hlp.readJson(filePath)

  def registerClassDefinition(self, gameSystem : str, definitionFileName : str = '_definition') -> dict | None:
    _gameSystemLower = gameSystem.lower()

    _definition = hlp.readJson(f'{self.rulesPath}/{gameSystem.lower()}/classes/{definitionFileName}.json')
    self.classDefinitions[_gameSystemLower] = _definition

  # Compares a class description file with the definition stored in the classDataStorage
  def verifyClassIntegrity(self, gameSystem, className, classData):
    if not self.gameSystemExists(gameSystem):
      return False

    _gameSystemClassDefinition = self.classDefinitions[gameSystem.lower()]
    if _gameSystemClassDefinition is None:
      logging.error(f'No class definition found for game system {gameSystem}. Class "{className.title()}" can not be verified.')
      return False

    for _key in _gameSystemClassDefinition:
      _value = classData.get(_key)
      if _value is None:
        logging.error(f'Class "{className.title()}" for game system {gameSystem} is missing key {_key}.')
        return False

    return True

# Crate singleton instance
gameSystemData = GameSystemData()

def getGameSystemData() -> GameSystemData:
  return gameSystemData


