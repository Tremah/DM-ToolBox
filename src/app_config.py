# THE FOLLOWING VALUE ARE CONFIGURATION SETTINGS FOR THE APPLICATION
# DO NOT EDIT BELOW THIS LINE
from pathlib import Path
import platform

ROOT_PATH = Path.cwd()

ROOT_EXPORT_PATH = Path(ROOT_PATH) / 'data' / 'export'
ROOT_INPUT_PATH = Path(ROOT_PATH) / 'data' / 'input'
DB_SQL_EXPORT_PATH = Path(ROOT_EXPORT_PATH) / 'database'
JSON_EXPORT_PATH = Path(ROOT_EXPORT_PATH) / 'json'

# Foundry VTT
FOUNDRY_INSTALL_DATA_PATH = '/home/patrick/.local/share/FoundryVTT/Data'
FOUNDRY_MODULE_ROOT_PATH = Path(f'modules')
OSR_EQUIPMENT_PACK_NAME = 'osr-armor-weapons-equipment'
OSR_EQUIPMENT_IMAGE_PATH = Path(FOUNDRY_MODULE_ROOT_PATH) / OSR_EQUIPMENT_PACK_NAME / 'data/images'
