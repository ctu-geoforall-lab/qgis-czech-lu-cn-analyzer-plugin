import os
from .CNCreator import CNCreator, add_cn_symbology,prune_cn_layer_fields

from qgis.core import QgsTask, QgsMessageLog, Qgis
from PyQt5.QtCore import pyqtSignal


class TASK_CN(QgsTask):
    """Task Intersect Soil and LandUse layers."""
    taskFinished_CN  = pyqtSignal(list)

    def __init__(self, IntLayer, CN_table_path):
        super().__init__("CN Creation.", QgsTask.CanCancel)
        self.IntLayer = IntLayer
        self.CN_table_path = CN_table_path
        self.CNLayer = None



    def finished(self,result):
        """Handle the completion of the task."""
        if result:
            QgsMessageLog.logMessage("Task of CN creation completed.", "CzLandUseCN", level=Qgis.Info,
                                     notifyUser=False)
            self.taskFinished_CN.emit([self.CNLayer])
        else:
            QgsMessageLog.logMessage("Task of processing layers failed.", "CzLandUseCN", level=Qgis.Warning,
                                     notifyUser=True)
    def run(self):
        """Run the task to process Soil layers."""
        try:

            prune_cn_layer_fields(self.IntLayer)
            # Create CN Creator instance
            cn_creator = CNCreator(self.IntLayer, self.CN_table_path)
            # Create CN layer

            self.CNLayer = cn_creator.CreateCNLayer()

            try:
                add_cn_symbology(self.CNLayer , "CN2",
                                 os.path.join(os.path.dirname(os.path.realpath(__file__)), "colortables",
                                              "CN_color_ramp.xml"), "CN")
            except Exception as e:
                QgsMessageLog.logMessage(f"Error in CN symbology: {str(e)}", "CzLandUseCN", level=Qgis.Warning)

            return True

        except Exception as e:
            QgsMessageLog.logMessage(f"Error in Intersection Task: {str(e)}", "CzLandUseCN", level=Qgis.Warning,
                                     notifyUser=True)
            return False