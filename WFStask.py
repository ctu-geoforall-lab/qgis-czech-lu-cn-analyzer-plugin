from .WFSdownloader import WFSDownloader
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsTask, QgsMessageLog, Qgis
from .PluginUtils import get_string_from_yaml
import os

class TASK_process_wfs_layer(QgsTask):
    """Task to process WFS layers."""
    progressChanged = pyqtSignal(int)
    taskCanceled = pyqtSignal(bool)
    taskError = pyqtSignal(str)
    taskFinished = pyqtSignal(list)

    def __init__(self, wfs_layers, ymin, xmin, ymax, xmax, current_extent, polygon, flag, label, progress_bar,
                 run_button, abort_button, polygon_button, extent_button, LandUseLayers):

        super().__init__("Process WFS Layers", QgsTask.CanCancel)
        self.wfs_layers = wfs_layers
        self.ymin, self.xmin, self.ymax, self.xmax = ymin, xmin, ymax, xmax
        self.current_extent, self.polygon, self.AreaFlag = current_extent, polygon, flag
        self.label, self.progressBar = label, progress_bar
        self.runButton, self.abortButton = run_button, abort_button
        self.polygonButton, self.extentButton = polygon_button, extent_button
        self._is_canceled, self.plus_one_index, self.layer = False, 0, None
        self.LandUseLayers = LandUseLayers
        self.abortButton.clicked.connect(self.cancel)

    def _update_progress_bar(self):
        """Update the progress bar based on the number of WFS layers in config."""
        percentage = int(round(100 / len(self.wfs_layers)))
        increment = percentage + (1 if self.plus_one_index % 2 else 0) - 1
        new_value = min(self.progressBar.value() + increment, 99)
        self.progressChanged.emit(new_value)
        self.plus_one_index += 1

    def finished(self, result):
        """Handle the completion of the task."""
        QgsMessageLog.logMessage("Task of processing layers completed.", "CzLandUseCN", level=Qgis.Info,
                                 notifyUser=False)
        self.taskFinished.emit(self.LandUseLayers)

    def run(self):
        """Run the task to process WFS layers."""
        wfs_downloader = WFSDownloader(os.path.join(os.path.dirname(__file__), 'config', 'layers_merging_order.csv'),
                                       self.AreaFlag, self.polygon)

        self._update_progress_bar()
        LPISconfigpath = os.path.join(os.path.dirname(__file__), 'config', 'LPIS.yaml')
        LPISURL = get_string_from_yaml(LPISconfigpath, "URL")
        LPISlayername = get_string_from_yaml(LPISconfigpath, "layer_name")
        self.LandUseLayers = wfs_downloader.GetLPISLayer(LPISURL, LPISlayername, LPISconfigpath, self.ymin, self.xmin,
                                                         self.ymax, self.xmax, self.current_extent, self.LandUseLayers)
        try:
            zabaged_URL = get_string_from_yaml(os.path.join(os.path.dirname(__file__), 'config', 'ZABAGED.yaml'),
                                               "URL")

            i = 1
            for self.layer in self.wfs_layers:
                if self._is_canceled:
                    return False
                if i > 1:
                    self._update_progress_bar()
                i += 1
                wfsLayer = wfs_downloader.process_wfs_layer(self.layer, self.ymin, self.xmin, self.ymax, self.xmax,
                                                            self.current_extent, zabaged_URL)
                if wfsLayer.featureCount() == 0:
                    continue
                if self.AreaFlag and self.polygon:
                    clippedLayer = wfs_downloader.ClipByPolygon(wfsLayer)
                    if clippedLayer is None:
                        QgsMessageLog.logMessage("Invalid input polygon layer!", "CzLandUseCN",
                                                 level=Qgis.Warning, notifyUser=True)
                        continue
                    self.LandUseLayers.append(clippedLayer)
                else:
                    self.LandUseLayers.append(wfsLayer)
            self.finished(True)
            return True
        except Exception as e:
            QgsMessageLog.logMessage(f"Error occurred: {e}", "CzLandUseCN", level=Qgis.Warning,
                                     notifyUser=True)
            self.taskError.emit(str(e))
            return None

    def cancel(self):
        """Cancel the task."""
        super().cancel()
        self._is_canceled = True
        self.taskCanceled.emit(True)