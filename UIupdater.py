# UIupdater.py

from qgis.core import QgsMessageLog, Qgis
from qgis.utils import iface
from PyQt5.QtCore import pyqtSignal, QObject

class UIUpdater(QObject):
    """Class to update the UI elements during processing."""
    progressChanged = pyqtSignal(int)

    def __init__(self, run_button, progress_bar, abort_button, label, polygon_button, extent_button, polygon_label,
                 mMapLayerComboBox, LUandSoilSelectButton, SoilSelectButton, LUSelectButton, mMapLayerComboBox_LU, mMapLayerComboBox_HSG):
        super().__init__()
        # tab_1
        self.runButton = run_button

        self.progressBar = progress_bar
        self.abortButton = abort_button
        self.label = label
        self.polygonButton = polygon_button
        self.extentButton = extent_button
        self.polygonLabel = polygon_label
        self.mMapLayerComboBox = mMapLayerComboBox
        self.LUandSoilSelectButton = LUandSoilSelectButton
        self.SoilSelectButton = SoilSelectButton
        self.LUSelectButton = LUSelectButton

        # tab_2
        self.mapLayerComboBox_LU = mMapLayerComboBox_LU
        self.mapLayerComboBox_HSG = mMapLayerComboBox_HSG

        self.AreaFlag = False
        self.plus_one_index = 0
        self.wfs_layers = []




    def ToggleChangeToPolygon(self):
        """Toggle the computation to the polygon layer."""
        self.AreaFlag = True
        self.polygonButton.setChecked(False)
        self.polygonLabel.setEnabled(True)
        self.mMapLayerComboBox.setEnabled(True)

    def ToggleChangeToExtent(self):
        """Toggle the computation to the extent of the map canvas."""
        self.AreaFlag = False
        self.extentButton.setChecked(False)
        self.polygonLabel.setEnabled(False)
        self.mMapLayerComboBox.setEnabled(False)

    def ErrorMsg(self, message):
        """Display an error message."""
        iface.messageBar().pushMessage("Error", message, level=Qgis.Critical, duration=5)

    def LoadingMsg(self, msg):
        """Display a loading message."""
        iface.messageBar().pushMessage("Loading", msg, level=Qgis.Info, duration=0)

    def CloseLoadingMsg(self):
        """Close messages."""
        iface.messageBar().clearWidgets()

    def setButtonstoDefault(self):
        """Set the UI buttons to their default state."""
        self.runButton.setEnabled(True)
        self.progressBar.setEnabled(False)
        self.abortButton.setEnabled(False)
        self.progressBar.setValue(0)
        self.label.setText("")
        self.polygonButton.setEnabled(True)
        self.extentButton.setEnabled(True)

    def freeze_ui(self):
        """Freeze the UI elements during processing."""
        self.runButton.setEnabled(False)
        self.extentButton.setEnabled(False)
        self.polygonButton.setEnabled(False)
        self.LUandSoilSelectButton.setEnabled(False)
        self.mMapLayerComboBox.setEnabled(False)
        self.SoilSelectButton.setEnabled(False)
        self.LUSelectButton.setEnabled(False)
        self.abortButton.setEnabled(True)
        self.progressBar.setEnabled(True)
        self.progressBar.setValue(0)
        self.label.setText("Downloading WFS layers...")

    def reset_panel(self):
        self.label.setStyleSheet("QLabel { color : black; }")  # Set the label color to black
        self.progressBar.setValue(0)  # Reset progress bar

    def updateProgressBar(self, value):
        """Signaled by task - Update the progress bar value based on the task progress."""
        self.progressBar.setValue(value)

    def _reset_ui(self, message, progress_value):
        """Reset the UI elements after task cancellation or completion."""
        self.progressBar.setValue(progress_value)
        self.runButton.setEnabled(True)
        self.abortButton.setEnabled(False)
        self.progressBar.setEnabled(False)
        self.polygonButton.setEnabled(True)
        self.extentButton.setEnabled(True)
        self.LUandSoilSelectButton.setEnabled(True)
        self.mMapLayerComboBox.setEnabled(True)
        self.SoilSelectButton.setEnabled(True)
        self.LUSelectButton.setEnabled(True)
        self.label.setText(message)
        iface.messageBar().clearWidgets()
        iface.messageBar().pushMessage("Exiting", message, level=Qgis.Critical, duration=5)

    def TaskCanceled(self):
        """Signaled by task - Handle the cancellation of the processing task."""
        iface.messageBar().clearWidgets()
        iface.messageBar().pushMessage("Warning", "Process was canceled by user", level=Qgis.Warning, duration=5)
        self._reset_ui("Land Use Task was canceled by user.", 0)
        QgsMessageLog.logMessage("Land Use Task was canceled by user.","CzLandUseCN", level=Qgis.Info, notifyUser=False)

    def TaskError(self, e):
        """Signaled by task - Handle errors that occurred during the processing task."""
        QgsMessageLog.logMessage(e,"CzLandUseCN",  level=Qgis.Critical, notifyUser=True)
        iface.messageBar().pushMessage("ERROR - LandUse:", str(e), level=Qgis.Critical, duration=5)
        self._reset_ui("Error occurred during LandUse processing.", 0)

    def TaskSuccess(self):
        """ Handle the successful completion of the processing task."""
        QgsMessageLog.logMessage("Editing layers.", "CzLandUseCN", level=Qgis.Info, notifyUser=False)
        self.label.setText("Editing ZABAGED layers...")

    def PluginSuccess(self):
        """ Modify the UI elements after task completion."""
        QgsMessageLog.logMessage("Plugin - Success!", "CzLandUseCN", level=Qgis.Info, notifyUser=False)
        self.progressBar.setValue(100)
        iface.messageBar().clearWidgets()
        self.runButton.setEnabled(True)
        self.abortButton.setEnabled(False)
        self.label.setStyleSheet("QLabel { color : green; }")
        self.label.setText("Completed :)")
        self.polygonButton.setEnabled(True)
        self.extentButton.setEnabled(True)
        self.LUandSoilSelectButton.setEnabled(True)
        if self.AreaFlag:
            self.mMapLayerComboBox.setEnabled(True)
        self.SoilSelectButton.setEnabled(True)
        self.LUSelectButton.setEnabled(True)
        iface.messageBar().pushMessage("Success", "Task completed successfully", level=Qgis.Success, duration=5)

    def TaskCanceled_Soil(self):
        """Signaled by task - Handle the cancellation of the HSG processing task."""
        iface.messageBar().clearWidgets()
        iface.messageBar().pushMessage("Warning", "Process was canceled by user", level=Qgis.Warning, duration=5)
        self._reset_ui("Soil Task was canceled by user.", 0)
        QgsMessageLog.logMessage("Soil Task was canceled by user.","CzLandUseCN", level=Qgis.Info, notifyUser=False)

    def TaskError_Soil(self):
        """Signaled by task - Handle errors that occurred during the HSG processing task."""
        iface.messageBar().pushMessage("ERROR Soil", "Error occurred during processing.", level=Qgis.Critical, duration=5)
        self._reset_ui("Error occurred during HSG processing.", 0)


