
from qgis.core import QgsMessageLog, Qgis
import csv
from typing import Optional



def is_valid_cn_csv(filepath):
    """Check if the CSV file is valid for CN calculation."""
    import csv

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader) # Skip header

        for row in reader:  # Skip header
            # Skip empty lines
            if not row or all(cell.strip() == "" for cell in row):
                continue

            # Check row has exactly 5 values
            if len(row) != 5:
                return False

            try:
                # First value should be an integer code
                int(row[0].strip())

                # Next 4 values should be numeric (int or float)
                for val in row[1:]:
                    float(val.strip())

            except ValueError:
                return False

    return True

def overlap_check(layer1, layer2):
    """Check if two layers have overlapping features."""
    overlap_found = False

    for feat1 in layer1.getFeatures():
        geom1 = feat1.geometry()

        for feat2 in layer2.getFeatures():
            geom2 = feat2.geometry()

            if geom1.intersects(geom2):  # Checks if any geometry intersects
                overlap_found = True
                break  # Exit early if overlap is found

    if overlap_found:
       return True
    else:
        return False

class InputChecker:
    """Class to check the input from the user and state of Qgis project"""
    def __init__(self, polygon, ymin, xmin, ymax, xmax, wfs_layers, qgs_project,map_combo_box, ui_updater, area_flag,
                 soil_flag):
        self.polygon = polygon
        self.ymin, self.xmin, self.ymax, self.xmax = ymin, xmin, ymax, xmax
        self.wfs_layers = wfs_layers
        self.qgs_project = qgs_project
        self.ui_updater = ui_updater
        self.mMapLayerComboBox = map_combo_box
        self.AreaFlag = area_flag
        self.SoilFlag = soil_flag




    def check_crs(self):
        """Check if the CRS is set to EPSG:5514."""
        crs = self.qgs_project.instance().crs().authid()
        if crs != 'EPSG:5514':
            self.ui_updater.CloseLoadingMsg()
            self.ui_updater.ErrorMsg("Please change CRS to EPSG:5514")
            self.ui_updater.setButtonstoDefault()
            return False
        return True

    def check_CR_boundary(self):
        """Check if the extent is out of bounds od Czech Republic"""
        if not (-1230000 <= self.ymin <= -920000) or not (-1230000 <= self.ymax <= -920000) or not (
                -920000 <= self.xmin <= -420000) or not (-920000 <= self.xmax <= -420000):
            QgsMessageLog.logMessage("Extent is out of Czech Republic boundaries", "CzLandUseCN",
                                     level=Qgis.Critical, notifyUser=True)
            self.ui_updater.CloseLoadingMsg()
            self.ui_updater.ErrorMsg("Extent is out of Czech Republic boundaries")
            self.ui_updater.setButtonstoDefault()
            return False
        return True

    def check_polygon_layer(self):
        """Get the polygon layer if AreaFlag is set."""

        if not self.AreaFlag:  # do not check if computing in extent mode
            return True

        if (self.polygon and self.polygon.crs().authid() != 'EPSG:5514'
                or self.SoilFlag and self.polygon.crs().authid() != 'EPSG:5514'):
            self.ui_updater.CloseLoadingMsg()
            self.ui_updater.ErrorMsg("Please change the polygon layer CRS to EPSG:5514")
            self.ui_updater.setButtonstoDefault()
            return False

        return True

    def check_wfs_errors(self):
        """Handle errors related to WFS layers."""
        if self.wfs_layers == "ERR_missingconffile":
            self.ui_updater.CloseLoadingMsg()
            self.ui_updater.ErrorMsg("Missing or corrupted configuration file (zabagedlayers.conf)")
            self.ui_updater.setButtonstoDefault()
            QgsMessageLog.logMessage("WFS layer error handling failed.", "CzLandUseCN",
                                     level=Qgis.Critical, notifyUser=True)
            return False

        if self.wfs_layers == "ERR_plg":
            self.ui_updater.CloseLoadingMsg()
            self.ui_updater.ErrorMsg("Please select a polygon layer")
            self.ui_updater.setButtonstoDefault()
            QgsMessageLog.logMessage("WFS layer error handling failed.", "CzLandUseCN",
                                     level=Qgis.Critical, notifyUser=True)
            return False

        return True

    def check_size_of_Area(self):
        """Check if the area of the polygon is lesser than 20 km2. Used for dissolved polygons."""

        if self.AreaFlag:
            total_area = sum([feature.geometry().area() for feature in self.polygon.getFeatures()])
            if total_area > 20000000:
                self.ui_updater.CloseLoadingMsg()
                self.ui_updater.ErrorMsg("The area of the polygon is greater than 20 km2")
                self.ui_updater.setButtonstoDefault()
                QgsMessageLog.logMessage("The area of the polygon is greater than 20 km2", "CzLandUseCN",
                              level=Qgis.Critical, notifyUser=True)
                return False
        else:
            # compute area from extent
            area = (self.ymax - self.ymin) * (self.xmax - self.xmin)
            if area > 20000000:
                self.ui_updater.CloseLoadingMsg()
                self.ui_updater.ErrorMsg("The area of the extent is greater than 20 km2")
                self.ui_updater.setButtonstoDefault()
                QgsMessageLog.logMessage("The area of the extent is greater than 20 km2", "CzLandUseCN",
                                         level=Qgis.Critical, notifyUser=True)
                return False
        return True

    def validate_user_defined_height(self, input_str: str) -> Optional[list[float]]:
        """
        Validates the user-defined rainfall depth input, allowing multiple values separated by semicolons.

        Args:
            input_str (str): The user-defined rainfall depth as a string, possibly containing multiple values separated by ';'.

        Returns:
            list of float: The validated rainfall depths if all values are valid and > 0.
            None: If any input value is invalid or <= 0.
        """
        # Normalize decimal separator
        input_str = input_str.replace(",", ".")

        # Split by semicolon to allow multiple values
        parts = input_str.split(";")
        heights = []

        for part in parts:
            part = part.strip()
            if not part:
                self.ui_updater.ErrorMsg("Empty value detected in rainfall depths list.")
                QgsMessageLog.logMessage(
                    "Empty value detected in rainfall depths list.",
                    "CzLandUseCN",
                    level=Qgis.Critical
                )
                return None
            try:
                value = float(part)
                if value <= 0:
                    self.ui_updater.ErrorMsg(
                        "User defined rainfall depth must be greater than 0."
                    )
                    QgsMessageLog.logMessage(
                        "User defined rainfall depth must be greater than 0.",
                        "CzLandUseCN",
                        level=Qgis.Critical
                    )
                    return None
                heights.append(value)
            except ValueError:
                self.ui_updater.ErrorMsg(
                    "User defined rainfall depth is not a number."
                )
                QgsMessageLog.logMessage(
                    "User defined rainfall depth is not a number.",
                    "CzLandUseCN",
                    level=Qgis.Critical
                )
                return None

        return heights

    def validate_abstraction_coefficient(self,abstr_coeff):
        """
        Validates the initial abstraction coefficient.

        Args:
            abstr_coeff (str): The abstraction coefficient as a string.

        Returns:
            float: The validated abstraction coefficient if valid.
            None: If the input is invalid.
        """
        # Replace comma with dot
        abstr_coeff = abstr_coeff.replace(",", ".")
        try:
            abstr_coeff = float(abstr_coeff)
            if abstr_coeff <= 0:
                self.ui_updater.ErrorMsg("Initial abstraction coefficient must be greater than 0.")
                QgsMessageLog.logMessage("Initial abstraction coefficient must be greater than 0.", "CzLandUseCN",
                                         level=Qgis.Critical)
                return None

            if abstr_coeff <= 0.1 or abstr_coeff >= 0.3:
                self.ui_updater.ErrorMsg("Initial abstraction coefficient should be 0.1 - 0.3.")
                QgsMessageLog.logMessage("Initial abstraction coefficient should be 0.1 - 0.3.", "CzLandUseCN",
                                         level=Qgis.Warning)
                return None

            return abstr_coeff

        except ValueError:
            self.ui_updater.ErrorMsg("Initial abstraction coefficient is not a number.")
            QgsMessageLog.logMessage("Initial abstraction coefficient is not a number.", "CzLandUseCN",
                                     level=Qgis.Critical)
            return None