# THE FOLLOWING VALUE ARE CONFIGURATION SETTINGS FOR THE APPLICATION
# DO NOT EDIT BELOW THIS LINE
from pathlib import Path

from PySide6.QtGui import QFontDatabase, QFont

ROOT_PATH = Path.cwd()

DB_PATH = Path(ROOT_PATH) / 'db'

ROOT_EXPORT_PATH = Path(ROOT_PATH) / 'data' / 'export'
ROOT_INPUT_PATH = Path(ROOT_PATH) / 'data' / 'input'
DB_SQL_EXPORT_PATH = Path(ROOT_EXPORT_PATH) / 'database'
JSON_EXPORT_PATH = Path(ROOT_EXPORT_PATH) / 'json'

# Foundry VTT
FOUNDRY_USER_DATA_PATH = Path('/home/patrick/.local/share/FoundryVTT/Data')
FOUNDRY_MODULE_ROOT_PATH = FOUNDRY_USER_DATA_PATH / 'modules'
OSR_EQUIPMENT_PACK_NAME = 'osr-armor-weapons-equipment'
OSR_EQUIPMENT_IMAGE_PATH = Path(FOUNDRY_MODULE_ROOT_PATH) / OSR_EQUIPMENT_PACK_NAME / 'data/images'

#LOGGING
DEBUG_MODE = True

class Icons:
  _fontId : int = -1
  _fontFamily : str | None = None
  ICONS = {
    'dice': '\uf522',
    'trash': '\uf1f8',
    'refresh': '\uf0e2',
    'list': '\uf03a',
    'search': '\uf002',
    'arrow-up': '\uf062',
    'arrow-down': '\uf063',
  }

  @classmethod
  def initialize(cls, rootPath : Path):
    # Already initialized
    if cls._fontFamily is not None:
      return

    # Font Awesome
    cls._fontId = QFontDatabase.addApplicationFont(str(rootPath / 'fonts' / 'Font Awesome 7 Free-Solid-900.otf'))
    families = QFontDatabase.applicationFontFamilies(cls._fontId)

    cls._fontFamily = families[1]


  @classmethod
  def font(cls, pointSize : int = 12):
    font = QFont(cls._fontFamily)
    font.setPointSize(pointSize)
    return font

  @classmethod
  def text(cls, iconName : str):
    return cls.ICONS[iconName]

