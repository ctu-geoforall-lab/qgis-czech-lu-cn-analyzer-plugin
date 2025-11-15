import os

from qgis.core import QgsTask, QgsMessageLog, Qgis
from PyQt5.QtCore import pyqtSignal

from CNCreator import add_CN3_from_CN2, add_cn_symbology
from RunOffComputer import RunOffComputer


class TASK_RunOff(QgsTask):
    """Task to create Run-off layer from CN layer."""
    taskFinished_RunOff = pyqtSignal(list)
    taskError_RunOff = pyqtSignal(str)

    def __init__(self, CN_Layer, reoccurence_intervals,RunOffFlag, user_defined_height,abstr_coeff, runoffLabel,
                 wps_url_path):
        super().__init__("Run-off Computation.", QgsTask.CanCancel)
        self.CN_Layer = CN_Layer
        self.reoccurence_intervals = reoccurence_intervals
        self.RunOffFlag = RunOffFlag
        self.user_defined_height = user_defined_height
        self.abstr_coeff = abstr_coeff
        self.runoffLabel = runoffLabel
        self.wps_conf_path = wps_url_path
        self.RunOffLayer = None



    def finished(self,result):
        """Handle the completion of the task."""
        if result:
            QgsMessageLog.logMessage("Task of Run-off Computation completed.", "CzLandUseCN", level=Qgis.Info,
                                     notifyUser=False)
            self.taskFinished_RunOff.emit([self.RunOffLayer])
        else:
            QgsMessageLog.logMessage("Task of Run-off Computation failed.", "CzLandUseCN", level=Qgis.Warning,
                                     notifyUser=True)
            self.runoffLabel.setText("ERROR - check the message log.")
            self.taskError_RunOff.emit("Task of Run-off Computation failed.")

    def run(self):
        """Run the task to process Run-off layers."""

        try:
            # If CN3 is not present, create it from CN2
            if self.runoffLabel is not None:
                self.runoffLabel.setText("Checking attributes ...")
            if self.CN_Layer.fields().indexFromName("CN3") == -1:
                add_CN3_from_CN2(self.CN_Layer, "CN2")

            runoff_computer = RunOffComputer(self.CN_Layer, self.reoccurence_intervals, self.RunOffFlag,
                                             self.user_defined_height, self.abstr_coeff,self.wps_conf_path,
                                             self.runoffLabel)
            if self.runoffLabel is not None:
                self.runoffLabel.setText("Computing run-off height ...")
            self.RunOffLayer = runoff_computer.get_runoff_volume()
            self.RunOffLayer.setName("RunOff Layer")
            if self.RunOffLayer is None or not self.RunOffLayer.isValid():
                if self.runoffLabel is not None:
                    self.runoffLabel.setText("ERROR - check the message log.")
                QgsMessageLog.logMessage("Run-off layer is Invalid.", "CzLandUseCN", level=Qgis.Warning,
                                         notifyUser=True)
                return False

            try:
                if self.RunOffFlag:
                    if len(self.user_defined_height) > 1:
                        fld = "CN2_1_runoff_volume_m3"
                    else:
                        fld = "CN2_runoff_volume_m3"

                else:
                    last_reoccurence = self.reoccurence_intervals[-1]
                    fld = f"V_{last_reoccurence}_m3"
                if self.runoffLabel is not None:
                    self.runoffLabel.setText("Adding symbology...")
                add_cn_symbology(self.RunOffLayer, fld ,
                                 os.path.join(os.path.dirname(os.path.realpath(__file__)), "colortables",
                                              "RUNOFF_color_ramp.xml"), "RUNOFF")
            except Exception as e:
                if self.runoffLabel is not None:
                    self.runoffLabel.setText("ERROR - check the message log.")
                QgsMessageLog.logMessage(f"Error in CN symbology: {str(e)}", "CzLandUseCN", level=Qgis.Critical)

            return True


        except Exception as e:
            if self.runoffLabel is not None:
                self.runoffLabel.setText("ERROR - check the message log.")
            QgsMessageLog.logMessage(f"Error in Run-off Task: {str(e)}", "CzLandUseCN", level=Qgis.Critical,
                                     notifyUser=True)

            return False


