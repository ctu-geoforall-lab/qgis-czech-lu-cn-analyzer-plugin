
from qgis.core import QgsMessageLog, Qgis


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


