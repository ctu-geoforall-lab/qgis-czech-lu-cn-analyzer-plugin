

from .WFSdownloader import WFSDownloader
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsTask, QgsMessageLog, Qgis, QgsVectorLayer, QgsFeature, QgsFeatureRequest, QgsWkbTypes, QgsGeometry
from .PluginUtils import get_string_from_yaml
import os
from owslib.wps import WebProcessingService, monitorExecution
from qgis.core import QgsRasterLayer, QgsProject, QgsApplication, QgsVectorLayer
import urllib.request
from osgeo import gdal
import tempfile
from pathlib import Path

from .SoilDownloader import SoilDownloader, load_tiff_from_zip, polygonize_raster


class TASK_process_soil_layer(QgsTask):
    """Task to process WFS layers."""
    progressChanged_Soil = pyqtSignal(int)
    taskCanceled_Soil = pyqtSignal(bool)
    taskError_Soil = pyqtSignal(str)
    taskFinished_Soil = pyqtSignal(str)

    def __init__(self, polygon_Soil, ymin_s, xmin_s, ymax_s, xmax_s, extent, label_Soil, progressBar_Soil, runButton_Soil, abortButton_Soil):
        super().__init__("Process Soil Layer", QgsTask.CanCancel)
        self.polygon_Soil = polygon_Soil
        self.ymin_s, self.xmin_s, self.ymax_s, self.xmax_s = ymin_s, xmin_s, ymax_s, xmax_s
        self.extent = extent
        self.label_Soil, self.progressBar_Soil = label_Soil, progressBar_Soil
        self.runButton_Soil, self.abortButton_Soil = runButton_Soil, abortButton_Soil
        self.SoilLayer = None
        self.SoilGPKGPath = None
        self._is_canceled = False

        self.abortButton_Soil.clicked.connect(self.cancel)

    def _update_progress_bar(self, new_value):
        """Update the progress bar"""
        self.progressChanged_Soil.emit(new_value)

    def finished(self, result):
        """Handle the completion of the task."""
        QgsMessageLog.logMessage("Task of processing soil layers completed.", "CzLandUseCN", level=Qgis.Info, notifyUser=False)
        self.taskFinished_Soil.emit(self.SoilGPKGPath)



    def run(self):
        """Run the task to process Soil layers."""

        self._update_progress_bar(10)
        try:
            URL = get_string_from_yaml(os.path.join(os.path.dirname(__file__), 'config', 'Soil.yaml'), "URL")
            process_identifier = get_string_from_yaml(os.path.join(os.path.dirname(__file__), 'config', 'Soil.yaml'), "process_identifier")
            XML_template = os.path.join(os.path.dirname(__file__), 'config', 'Soil_template.xml')

            soil_downloader = SoilDownloader(URL, XML_template, process_identifier, self.polygon_Soil, self.ymin_s, self.xmin_s, self.ymax_s, self.xmax_s)

            if self._is_canceled:
                return False

            self._update_progress_bar(20)
            # Execute the WPS request
            output_files = soil_downloader.execute_wps_request()

            if self._is_canceled:
                return False

            self._update_progress_bar(50)
            # Load the tiff from the output file .zip
            soil_raster = load_tiff_from_zip(output_files)

            if self._is_canceled:
                return False

            self._update_progress_bar(70)
            # Polygonize the raster
            self.SoilGPKGPath = polygonize_raster(soil_raster)



            self.finished(True)

            return True

        except Exception as e:
            QgsMessageLog.logMessage(f"Error in Soil Task: {str(e)}", "CzLandUseCN", level=Qgis.Warning, notifyUser=True)
            self.taskError_Soil.emit(str(e))
            self.cancel(True)
            return False

    def cancel(self):
        """Cancel the task."""
        super().cancel()
        self._is_canceled = True
        self.taskCanceled_Soil.emit(True)
