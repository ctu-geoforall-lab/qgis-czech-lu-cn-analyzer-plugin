import os

from .LayerEditor import clip_larger_layer_to_smaller
from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsProject, QgsMapLayerProxyModel
from PyQt5.QtCore import pyqtSignal
import processing


class TASK_Intersection(QgsTask):
    """Task Intersect Soil and LandUse layers."""
    taskFinished_Intersection  = pyqtSignal(list)

    def __init__(self, Soil_layer, LandUse_layer, mMapLayerComboBox_Int, runButton_Int):
        super().__init__("Layer intersection.", QgsTask.CanCancel)
        self.Soil_layer = Soil_layer
        self.LandUse_layer = LandUse_layer
        self.mMapLayerComboBox_Int = mMapLayerComboBox_Int
        self.runButton_Int = runButton_Int
        self.combined_layer = None


    def finished(self,result):
        """Handle the completion of the task."""
        if result:
            QgsMessageLog.logMessage("Task of processing layers completed.", "CzLandUseCN", level=Qgis.Info,
                                     notifyUser=False)
            self.taskFinished_Intersection .emit([self.combined_layer])
        else:
            QgsMessageLog.logMessage("Task of processing layers failed.", "CzLandUseCN", level=Qgis.Warning,
                                     notifyUser=True)
    def run(self):
        """Run the task to process Soil layers."""
        try:
            # Clip the layers to the same extent (smaller layer defines the final AOI if they are not the same size)
            self.Soil_layer, self.LandUse_layer = clip_larger_layer_to_smaller(self.Soil_layer, self.LandUse_layer)

            # Union the layers
            self.combined_layer = processing.run("native:union", {
                'INPUT': self.LandUse_layer,
                'OVERLAY': self.Soil_layer,
                'OUTPUT': 'memory:'
            })['OUTPUT']

            # Set the symbology of the combined layer
            symbology_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "colortables",
                                          "intersection.qml")
            self.combined_layer.setName("Intersected LandUse and HSG")
            self.combined_layer.loadNamedStyle(symbology_path)
            self.runButton_Int.setEnabled(True)

            return True





        except Exception as e:
            QgsMessageLog.logMessage(f"Error in Intersection Task: {str(e)}", "CzLandUseCN", level=Qgis.Warning,
                                     notifyUser=True)
            self.runButton_Int.setEnabled(True)
            return False
