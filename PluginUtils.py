from qgis.core import QgsMessageLog, Qgis
import yaml
from typing import Optional


def get_string_from_yaml(path: str, key: str) -> Optional[str]:
    """ Get a string from a YAML file"""
    try:
        with open(path, 'r') as file:
            config = yaml.safe_load(file)
            return config.get(key)
    except Exception as e:
        QgsMessageLog.logMessage(f"Failed to load {key} from {path}: {e}", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)
        return None