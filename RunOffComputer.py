import csv

from PyQt5.QtCore import QVariant
from qgis.core import QgsMessageLog, Qgis, QgsField, edit, QgsVectorLayer, QgsProject, QgsVectorFileWriter
from qgis.utils import iface
from string import Template
from typing import List, Optional, Union, Dict, Tuple
import os
import requests
import tempfile
from owslib.wps import WebProcessingService, ComplexDataInput, monitorExecution
import processing


from osgeo import ogr as osgeo_ogr
try:
    from .PluginUtils import get_string_from_yaml
    from .LayerEditor import dissolve_polygon, buffer_QgsVectorLayer
except ImportError:
    from PluginUtils import get_string_from_yaml
    from LayerEditor import dissolve_polygon, buffer_QgsVectorLayer
class RunOffComputer:
    """
    Class to compute runoff volume and height based on curve numbers (CN2, CN3) and rainfall depth.
    """

    def __init__(self, cn_layer, reoccurence_intervals, RunOffFlag, user_defined_height, abstr_coeff, urlPath,
                 runoffLabel):
        self.cn_layer = cn_layer
        self.reoccurence_intervals = reoccurence_intervals
        self.RunOffFlag = RunOffFlag
        self.user_defined_height = user_defined_height
        self.abstr_coeff = abstr_coeff
        self.urlPath = urlPath
        self.runoffLabel = runoffLabel
        self.runoff_layer = None
        self.dissolved_layer = None
        self.url = None
        self.process_identifier = None
        self.csv_list = []

    @staticmethod
    def update_shape_area(layer: QgsVectorLayer) -> None:
        """
        Update the SHAPE_Area field in the layer with the area of each feature.
        """
        if not layer.isValid():
            raise ValueError("Layer is not valid")

        field_name = 'SHAPE_Area'
        idx = layer.fields().lookupField(field_name)
        if idx < 0:
            provider = layer.dataProvider()
            provider.addAttributes([QgsField(field_name, QVariant.Double)])
            layer.updateFields()
            idx = layer.fields().lookupField(field_name)

        if layer.fields().field(idx).type() != QVariant.Double:
            raise ValueError(f"Field '{field_name}' is not of type Double")

        # edit instead of startEditing
        with edit(layer):
            for feat in layer.getFeatures():
                geom = feat.geometry()
                if not geom:
                    layer.changeAttributeValue(feat.id(), idx, 0)
                    continue
                area = geom.area()
                if area < 0.009:
                    layer.deleteFeature(feat.id())
                else:
                    layer.changeAttributeValue(feat.id(), idx, area)
        # no manual commitChanges()

    def create_new_fields(self, layer: QgsVectorLayer) -> QgsVectorLayer:
        """
        Create new fields in the layer for runoff volume and height, within
        an explicit edit session so schema changes persist.
        """
        #  Validate that the layer is properly loaded
        if not layer.isValid():
            raise ValueError("Layer is not valid")

        # Start editing so that addAttribute() calls actually stick
        if not layer.startEditing():
            raise IOError("Could not start edit session on layer")

        # Build a list of all fields to add
        fields_to_add: List[QgsField] = []

        if self.RunOffFlag:
            # multiple heights or single
            for idx_height, height in enumerate(self.user_defined_height, start=1):

                # CN2/CN3 output fields
                suffixes = ["runoff_height_mm", "runoff_volume_m3"]
                for prefix in ("CN2", "CN3"):
                    for suf in suffixes:
                        fld = (f"{prefix}_{idx_height}_{suf}" if len(self.user_defined_height) > 1
                               else f"{prefix}_{suf}")
                        if layer.fields().indexFromName(fld) == -1:
                            fields_to_add.append(QgsField(fld, QVariant.Double))

        else:
            # no RunOffFlag: simpler pattern

            for rec in self.reoccurence_intervals:
                # volume
                fld = f"V_{rec}_m3"
                if layer.fields().indexFromName(fld) == -1:
                    fields_to_add.append(QgsField(fld, QVariant.Double))
                # CN2/CN3 outputs
                for prefix in ("CN2", "CN3"):
                    for suf in ("runoff_height_mm", "runoff_volume_m3"):
                        fld = f"{prefix}_{rec}_{suf}"
                        if layer.fields().indexFromName(fld) == -1:
                            fields_to_add.append(QgsField(fld, QVariant.Double))

        # Add all new fields in one go
        if fields_to_add:
            provider = layer.dataProvider()
            if not provider.addAttributes(fields_to_add):
                layer.rollBack()
                raise IOError("Failed to add new fields to provider")
            layer.updateFields()

        # 5. Commit the schema edits
        if not layer.commitChanges():
            raise IOError("Failed to commit new fields to layer")

        return layer

    def _calculate_runoff_volume(self, CN2: float, CN3: float, area: float, rainfall_depth: float) -> tuple[
        float, float, float, float]:
        """
        Calculate the runoff volume and height based on CN2, CN3, area (m²), and rainfall depth.
        """

        # Convert area to square millimeters
        area = area * 1000000  # Convert to mm²

        # Calculate potential maximum retention for CN2 and CN3
        A_CN2 = 25.4 * (1000 / CN2 - 10)  # mm
        A_CN3 = 25.4 * (1000 / CN3 - 10)

        # Calculate initial abstraction for CN2 and CN3
        Ia_CN2 = self.abstr_coeff * A_CN2
        Ia_CN3 = self.abstr_coeff * A_CN3

        # Calculate the runoff height for CN2 and CN3
        CN2_h = (rainfall_depth - Ia_CN2) ** 2 / (rainfall_depth - Ia_CN2 + A_CN2)
        CN3_h = (rainfall_depth - Ia_CN3) ** 2 / (rainfall_depth - Ia_CN3 + A_CN3)

        # Convert runoff height to volume in cubic meters
        CN2_vol = CN2_h * area / 1000000000  # Convert to m³
        CN3_vol = CN3_h * area / 1000000000  # Convert to m³

        return CN2_h, CN3_h, CN2_vol, CN3_vol

    def calculate_base_runoffs(self) -> None:
        """
        Calculate the base runoff values for CN2 and CN3.

        This method computes runoff heights and volumes for each feature in the runoff layer
        based on CN2, CN3, area, and rainfall depth. The results are stored in the corresponding
        fields of the layer.
        """

        # Validate that the layer is properly loaded
        if not self.runoff_layer.isValid():
            raise ValueError("Layer is not valid")

        # Start editing the layer to allow modifications
        self.runoff_layer.startEditing()

        # Decide on the list of rainfall heights and their occurrences
        heights: List[float] = self.user_defined_height if self.RunOffFlag else list(self._get_height_dict().values())
        occurrences = (
            range(1, len(heights) + 1)
            if self.RunOffFlag
            else self._get_height_dict().keys()
        )

        # Iterate over each height and occurrence
        for idx, occurrence in zip(heights, occurrences):
            # Build the field names for runoff height and volume
            if len(heights) > 1:
                fn_h2 = f"CN2_{occurrence}_runoff_height_mm"
                fn_h3 = f"CN3_{occurrence}_runoff_height_mm"
                fn_v2 = f"CN2_{occurrence}_runoff_volume_m3"
                fn_v3 = f"CN3_{occurrence}_runoff_volume_m3"
            else:
                fn_h2, fn_h3, fn_v2, fn_v3 = (
                    "CN2_runoff_height_mm",
                    "CN3_runoff_height_mm",
                    "CN2_runoff_volume_m3",
                    "CN3_runoff_volume_m3",
                )

            # Process each feature in the layer
            for feat in self.runoff_layer.getFeatures():
                # Safely extract numeric values for CN2 and CN3
                CN2: float = feat.attribute("CN2")
                CN3: float = feat.attribute("CN3")
                if CN2 <= 0 or CN3 <= 0:
                    QgsMessageLog.logMessage(
                        f"Invalid CN at feature {feat.id()}", "CzLandUseCN", Qgis.Warning
                    )
                    continue

                # Extract the area and rainfall depth
                area: float = feat.attribute("SHAPE_Area")
                rainfall: float = float(idx)

                # Compute runoff heights and volumes
                h2, h3, v2, v3 = self._calculate_runoff_volume(CN2, CN3, area, rainfall)

                # Assign the computed values back to the feature
                feat.setAttribute(fn_h2, h2)
                feat.setAttribute(fn_h3, h3)
                feat.setAttribute(fn_v2, v2)
                feat.setAttribute(fn_v3, v3)

                # Push the changes to the layer
                self.runoff_layer.updateFeature(feat)

        # Commit all edits to the layer
        self.runoff_layer.commitChanges()

    def _validate_layer(self) -> None:
        if not self.dissolved_layer or not self.dissolved_layer.isValid():
            raise ValueError("Dissolved layer is not valid.")

    def _export_layer_to_gml(self) -> bytes:
        """
        Exports the layer to GML format.

        This method validates the layer, creates a temporary directory,
        writes the layer to a GML file, and returns the GML data as bytes.
        """
        if not self.dissolved_layer or not self.dissolved_layer.isValid():
            raise ValueError("Dissolved layer is not valid or missing.")

        # Set the name of the dissolved layer
        self.dissolved_layer.setName("wpsinput")

        # Create a temporary directory for the GML file
        tmp_dir = tempfile.mkdtemp(prefix='wps_gml_')
        gml_path = os.path.join(tmp_dir, 'input.gml')

        if not os.path.exists(tmp_dir):
            raise IOError(f"Temporary directory not created: {tmp_dir}")

        # Configure GML export options
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = "GML"
        options.fileEncoding = "UTF-8"
        options.layerName = f"{self.process_identifier}_input"

        # Write the dissolved layer to GML format
        err, err_msg, output_path, layer_name = QgsVectorFileWriter.writeAsVectorFormatV3(
            self.dissolved_layer,
            gml_path,
            QgsProject.instance().transformContext(),
            options
        )

        # Check for errors during the GML export
        if err != QgsVectorFileWriter.NoError:
            raise IOError(f"Failed to write GML (error {err}): {err_msg}")

        # Verify the GML file was created
        if not os.path.exists(output_path):
            raise IOError(f"GML file not created: {output_path}")

        # Ensure the dissolved layer is not empty
        if self.dissolved_layer.featureCount() == 0:
            raise ValueError("Dissolved layer has no features to export.")

        # Read the GML file as bytes
        with open(output_path, 'rb') as f:
            gml_data = f.read()

        return gml_data

    def _prepare_wps(self, gml_bytes: bytes, return_period_list: Optional[Union[List[str], str]] = "N2") -> tuple:
        """
        Prepares the inputs and outputs for a Web Processing Service (WPS) request.
        """
        # Instantiate WPS client
        wps: WebProcessingService = WebProcessingService(self.url, version='1.0.0')
        complex_input: ComplexDataInput = ComplexDataInput(gml_bytes)  # omit mimeType for exact XML match

        # Ensure return_period_list is a list
        if isinstance(return_period_list, str):
            rp_list: List[str] = [return_period_list]
        else:
            # If None provided, default to an empty list
            rp_list: List[str] = return_period_list or []

        # Literal inputs for return periods
        literal_inputs: List[tuple] = [("return_period", rp) for rp in rp_list]

        # Other literal inputs
        other_literals: List[tuple] = [
            ("type", "A"), ("type", "B"), ("type", "C"),
            ("type", "D"), ("type", "E"), ("type", "F"),
            ("keycolumn", "ID"),
            ("area_red", "True"),
        ]

        # Combine all inputs
        inputs: List[tuple] = [("input", complex_input)] + literal_inputs + other_literals

        # Define outputs
        outputs: List[tuple] = [("output", True), ("output_shapes", True)]

        return wps, inputs, outputs

    def _execute_wps(self, wps: WebProcessingService, inputs: list, outputs: list) -> object:
        """
        Executes a Web Processing Service (WPS) request.
        """
        return wps.execute(
            identifier=self.process_identifier,
            inputs=inputs,
            output=outputs
        )

    def _wait_for_completion(self, execution) -> None:
        """
        Waits for the completion of a WPS execution process.

        This method continuously checks the status of the WPS execution
        and logs progress messages. It also updates the `runoffLabel`
        with the current status if the message length is below a threshold.
        """
        while not execution.isComplete():
            execution.checkStatus(sleepSecs=3)
            msg: str = f"{execution.statusMessage} - {execution.percentCompleted}%"
            QgsMessageLog.logMessage(
                msg,
                "CzLandUseCN", level=Qgis.Info
            )

            if len(msg) < 42 and self.runoffLabel is not None:
                self.runoffLabel.setText(f"WPS: {msg}")

    @staticmethod
    def _download_outputs(execution, output_dir: str, identifiers: list[str]) -> list[str]:
        """
        Download output files from a WPS execution..
        """

        file_paths: list[str] = []
        for ident in identifiers:
            local_path = os.path.join(output_dir, f"{ident}.csv")
            execution.getOutput(filepath=local_path, identifier=ident)
            if not os.path.exists(local_path):
                raise IOError(f"Missing output file for '{ident}'")
            file_paths.append(local_path)
        return file_paths

    @staticmethod
    def _load_csv_layers(file_paths: list[str]) -> None:
        """
        Load CSV files as layers into the QGIS project.
        """

        for path in file_paths:
            try:
                # Attempt to load the CSV file as a vector layer
                layer = QgsVectorLayer(path, os.path.basename(path), 'ogr')
                if not layer.isValid():
                    raise IOError("Invalid table layer")
                # Add the loaded layer to the QGIS project
                QgsProject.instance().addMapLayer(layer)
            except Exception as e:
                # Log a warning message if the layer could not be loaded
                QgsMessageLog.logMessage(
                    f"Could not load table {path}: {e}",
                    "CzLandUseCN", level=Qgis.Warning
                )

    def get_csvs_via_WPS(self) -> List[str]:
        """
        Retrieve CSV files via a Web Processing Service (WPS).
        """
        # Dissolve and buffer the CN layer
        self.dissolved_layer = dissolve_polygon(self.cn_layer)
        self.dissolved_layer = buffer_QgsVectorLayer(self.dissolved_layer, 0.01, 1)

        # Validate the dissolved layer
        self._validate_layer()

        # Export the dissolved layer to GML format
        gml_bytes = self._export_layer_to_gml()

        # Prepare and execute the WPS request
        wps, inputs, outputs = self._prepare_wps(gml_bytes=gml_bytes,
                                                 return_period_list=self.reoccurence_intervals)
        execution = self._execute_wps(wps, inputs, outputs)

        # Wait for the WPS execution to complete
        self._wait_for_completion(execution)

        # Download the resulting CSV files
        tmp_dir = tempfile.mkdtemp(prefix='wps_output_')
        file_paths = self._download_outputs(execution, tmp_dir, ["output", "output_shapes"])

        # Load the CSV files as layers into the QGIS project
        self._load_csv_layers(file_paths)

        return file_paths

    def _get_value_from_csv(self, attribute_name: str) -> float:
        """
        Retrieve a specific attribute value from the first row of the first CSV file in `self.csv_list`.
        """
        with open(self.csv_list[0], newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            first_row = next(reader)  # Read only the first data row
            if attribute_name in first_row:
                return float(first_row[attribute_name])
            else:
                raise ValueError(f"Attribute '{attribute_name}' not found in CSV.")

    def _get_height_dict(self) -> Dict[str, float]:
        """
        Reads the first CSV in `self.csv_list`, extracts height values for each recurrence interval,
        and returns a dictionary mapping each interval (e.g., 'N2') to its corresponding H_<interval>T360_mm value.
        """

        # Ensure the CSV list is not empty
        csv_file = self.csv_list[0]

        # Open the CSV and read into a DictReader for easy header-based access
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            try:
                # Read the first row of data
                row = next(reader)
            except StopIteration:
                # Return an empty dictionary if the CSV has no data rows
                return {}

        height_dict: Dict[str, float] = {}
        for interval in self.reoccurence_intervals:
            # Construct the column name for the current interval
            column_name = f"H_{interval}T360_mm"
            if column_name not in row:
                # Raise an error if the expected column is missing
                raise KeyError(f"Expected column '{column_name}' not found in CSV")
            try:
                # Convert the height value to a float and store it in the dictionary
                height_dict[interval] = float(row[column_name])
            except ValueError:
                # Handle invalid float conversion and log a critical message
                height_dict[interval] = 0
                QgsMessageLog.logMessage("Invalid CSV from WPS", "CzLandUseCN", level=Qgis.Critical)

        return height_dict

    def calculate_weighted_runoffs(self) -> None:
        """
        Calculate weighted runoff volumes for each reoccurrence interval.

        This method computes the weighted runoff volume for each feature in the runoff layer
        based on CN2 and CN3 volumes, shape probabilities, and other parameters retrieved
        from the CSV files. The results are stored in the corresponding fields of the layer.
        """

        self.runoff_layer.startEditing()

        for reoccurrence in self.reoccurence_intervals:
            for feat in self.runoff_layer.getFeatures():
                V = 0
                CN2_volume: Optional[float] = feat[f"CN2_{reoccurrence}_runoff_volume_m3"]
                CN3_volume: Optional[float] = feat[f"CN3_{reoccurrence}_runoff_volume_m3"]

                # Skip features with invalid or missing CN2/CN3 volumes
                if CN2_volume is None or CN3_volume is None or CN2_volume < 0 or CN3_volume < 0:
                    continue

                # Calculate weighted runoff volume for each shape
                for shape in ["A", "B", "C", "D", "E", "F"]:
                    P_shape: float = self._get_value_from_csv(f"P_{reoccurrence}tvar{shape}_%")
                    P_CN2: float = self._get_value_from_csv(f"QAPI_tvar{shape}")
                    P_CN3: float = 1 - P_CN2

                    CN2_part_V: float = P_CN2 * P_shape * CN2_volume
                    CN3_part_V: float = P_CN3 * P_shape * CN3_volume
                    V += CN2_part_V + CN3_part_V

                # Assign the total volume to the corresponding field
                field_name: str = f"V_{reoccurrence}_m3"
                if field_name not in self.runoff_layer.fields().names():
                    raise ValueError(f"Field '{field_name}' not found in layer")
                feat.setAttribute(field_name, V / 100)
                self.runoff_layer.updateFeature(feat)

        # Commit all edits to the layer
        self.runoff_layer.commitChanges()

    def get_runoff_volume(self) -> Optional[QgsVectorLayer]:
        """
        Main method to compute runoff volume and height.

        This method handles the process of:
        - Creating a WPS request and executing it (if required).
        - Processing the results to calculate runoff volumes and heights.
        - Adding the calculated values to the layer.
        """

        self.url = get_string_from_yaml(self.urlPath, "URL")
        self.process_identifier = get_string_from_yaml(self.urlPath, "process_identifier")
        self.runoff_layer = self.cn_layer.clone()

        try:
            # Update the shape area for the runoff layer
            self.update_shape_area(self.runoff_layer)

            # Create new fields in the runoff layer for storing runoff data
            self.runoff_layer = self.create_new_fields(self.runoff_layer)

            # If RunOffFlag is False, retrieve CSV data via WPS
            if not self.RunOffFlag:
                self.csv_list = self.get_csvs_via_WPS()

            # Calculate base runoff values (CN2 and CN3)
            self.calculate_base_runoffs()

            # If RunOffFlag is False, calculate weighted runoff values
            if not self.RunOffFlag:
                self.calculate_weighted_runoffs()

            return self.runoff_layer

        except Exception as e:
            # Log any errors that occur during the process
            QgsMessageLog.logMessage(f"Error in RunOffComputer: {str(e)}", "CzLandUseCN", level=Qgis.Critical)
            return None
