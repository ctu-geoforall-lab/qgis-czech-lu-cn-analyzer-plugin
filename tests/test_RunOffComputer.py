# Ensure that qgis packages are imported to your python environment when running locally
# (/usr/lib/python3/dist-packages/qgis)

import pytest
import csv
from osgeo import ogr
import os
import sys

# Add the parent directory to PYTHONPATH for module imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qgis.core import QgsApplication, QgsVectorLayer
# Initialize QGIS application in the main thread
qgs = QgsApplication([], False)
qgs.initQgis()


from RunOffComputer import RunOffComputer
from LayerEditor import LayerEditor, dissolve_polygon

class TestRunOffComputer:

    @classmethod
    def teardown_class(cls):
        # Exit QGIS application
        qgs.exitQgis()

    def test_runoff_computer(self, tmp_path):
        """
        Tests for RunOffComputer methods in a single function.
        """

        print("")

        # 1. Test _calculate_runoff_volume with known manual values
        roc1 = RunOffComputer(None, None, True, [10.0], 0.2, None, None, )
        h2, h3, v2, v3 = roc1._calculate_runoff_volume(50.0, 60.0, 100.0, 10.0)
        # A_CN2=254, Ia_CN2=50.8 => h2≈7.806, v2≈0.7806
        assert pytest.approx(7.806, rel=1e-3) == h2
        assert pytest.approx(0.7808, rel=1e-4) == v2
        # A_CN3≈169.333, Ia_CN3≈33.867 => h3≈3.9158, v3≈0.3916
        assert pytest.approx(3.9158, rel=1e-3) == h3
        assert pytest.approx(0.3916, rel=1e-4) == v3
        print("[OK] Calculated runoff volume successfully")

        # 2. Test CSV value retrieval and error
        roc_csv = RunOffComputer(None, None, False, [], 0.2, None, None)
        csv_file = tmp_path / "test.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["A", "B"])
            writer.writeheader()
            writer.writerow({"A": "1.5", "B": "2.5"})
        roc_csv.csv_list = [str(csv_file)]
        assert roc_csv._get_value_from_csv("A") == pytest.approx(1.5)
        assert roc_csv._get_value_from_csv("B") == pytest.approx(2.5)
        print("[OK] Retrieved values from CSV successfully")
        with pytest.raises(ValueError):
            roc_csv._get_value_from_csv("C")

        # 3. Test _get_height_dict success and failure
        roc_ht = RunOffComputer(None, ["N2", "N5"], False, [], 0.2, None, None, )
        ht_file = tmp_path / "heights.csv"
        with open(ht_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["H_N2T360_mm", "H_N5T360_mm"])
            writer.writeheader()
            writer.writerow({"H_N2T360_mm": "5.0", "H_N5T360_mm": "15.0"})
        roc_ht.csv_list = [str(ht_file)]
        hd = roc_ht._get_height_dict()
        assert hd["N2"] == pytest.approx(5.0)
        assert hd["N5"] == pytest.approx(15.0)
        print("[OK] Retrieved height dictionary successfully")

        # missing column case
        bad_file = tmp_path / "bad.csv"
        with open(bad_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["H_N2T360_mm"])
            writer.writeheader()
            writer.writerow({"H_N2T360_mm": "5.0"})
        roc_ht.csv_list = [str(bad_file)]
        with pytest.raises(KeyError):
            roc_ht._get_height_dict()

            # Load the polygon layer
        base_folder = os.path.dirname(__file__)
        input_folder = os.path.join(base_folder, 'input_files', "testing_LayerEditor_data")
        plg_path = os.path.join(input_folder, 'low.gpkg')
        polygon = QgsVectorLayer(f"{plg_path}|layername=low", "low", "ogr")


        roc = RunOffComputer(None, ['X'], False, [], 0.2,
                             None, None)

        new_layer = roc.create_new_fields(polygon)
        # verify new fields
        for fld in ("V_X_m3", "CN2_X_runoff_height_mm", "CN3_X_runoff_volume_m3"):
            assert new_layer.fields().indexFromName(fld) >= 0, f"Missing field {fld}"

        print("[OK] Created new fields successfully")





