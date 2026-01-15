from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsTask, QgsMessageLog, Qgis

from .LayerEditor import LayerEditor, resolve_overlaping_buffers

class TASK_edit_layers(QgsTask):
    """Task to process WFS layers."""
    progressChanged_edit = pyqtSignal(int)
    taskCanceled_edit = pyqtSignal(bool)
    taskError_edit = pyqtSignal(str)
    taskFinished_edit = pyqtSignal(list)

    def __init__(self, attribute_template_path, LPIS_config_path, ZABAGED_config_path, stacking_template_path,
                 symbology_path, AreaFlag, polygon, ymin, xmin, ymax, xmax, progress_bar, abortButtton,
                 LandUseLayers):

        super().__init__("Edit WFS Layers", QgsTask.CanCancel)
        self.attribute_template_path = attribute_template_path
        self.LPIS_config_path = LPIS_config_path
        self.ZABAGED_config_path = ZABAGED_config_path
        self.stacking_template_path = stacking_template_path
        self.symbology_path = symbology_path
        self.AreaFlag = AreaFlag
        self.ymin, self.xmin, self.ymax, self.xmax = ymin, xmin, ymax, xmax
        self.polygon = polygon
        self.abortButton = abortButtton
        self.progressBar = progress_bar
        self.LandUseLayers = LandUseLayers
        self._is_canceled = False
        self.merged_layer = None
        if self.abortButton is not None:
            self.abortButton.clicked.connect(self.cancel)

    def _update_progress_bar(self, new_value):
        """Update the progress bar"""
        self.progressChanged_edit.emit(new_value)


    def finished(self, result):
        """Handle the completion of the task."""
        QgsMessageLog.logMessage("Task of editing layers completed.", "CzLandUseCN", level=Qgis.Info,
                                 notifyUser=False)
        self.taskFinished_edit.emit([self.merged_layer])

    def run(self):
        """Run the task to edit WFS layers."""
        QgsMessageLog.logMessage("Layer Editing task started.", "CzLandUseCN",
                                 level=Qgis.Info, notifyUser=False)
        try:
            layer_editor = LayerEditor(self.attribute_template_path, self.LPIS_config_path, self.ZABAGED_config_path,
                                       self.stacking_template_path,
                                       self.symbology_path, self.AreaFlag, self.polygon, self.ymin, self.xmin, self.ymax,
                                       self.xmax)

            self._update_progress_bar(10)

            # Add LandUse attribute to all layers in list
            self.LandUseLayers = layer_editor.add_landuse_attribute(self.LandUseLayers)

            if self._is_canceled:
                QgsMessageLog.logMessage("Task was canceled by user.", "CzLandUseCN", level=Qgis.Warning,
                                         notifyUser=True)

            self._update_progress_bar(20)

            # Add buffer line features to all layers in list
            self.LandUseLayers = layer_editor.buffer_layers(self.LandUseLayers)

            self._update_progress_bar(40)
            # Update LandUse code based on its attributes
            self.LandUseLayers = layer_editor.edit_landuse_code(self.LandUseLayers)

            self._update_progress_bar(60)
            # Clip all layer to the polygon or extent by AreaFlag (Used as clip after buffering)
            self.LandUseLayers = layer_editor.clip_layers_after_edits(self.LandUseLayers)

            self._update_progress_bar(80)
            # Resolve overlaping buffered lines
            self.LandUseLayers = resolve_overlaping_buffers(self.LandUseLayers, self.ZABAGED_config_path)

            self._update_progress_bar(90)
            # Store the merged layer as an instance attribute to keep it in scope
            self.merged_layer = layer_editor.stack_layers(self.LandUseLayers)

            return True

        except Exception as e:
            QgsMessageLog.logMessage(f"Error occurred: {e}", "CzLandUseCN", level=Qgis.Critical,
                                     notifyUser=True)
            self.taskError_edit.emit(str(e))
            return False

    def cancel(self):
        """Cancel the task."""
        super().cancel()
        self._is_canceled = True
        self.taskCanceled_edit.emit(True)
