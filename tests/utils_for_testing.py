import os
from osgeo import ogr
from qgis.core import QgsVectorLayer



def assert_layers_equal(layer1: QgsVectorLayer, layer2: QgsVectorLayer):
    """Assert that two QgsVectorLayers are identical."""

    # Check if layers are valid
    assert layer1.isValid(), "First layer is not valid."
    assert layer2.isValid(), "Second layer is not valid."

    # Check if the CRS is the same
    assert layer1.crs() == layer2.crs(), "CRS mismatch between layers."

    # Check if the field structure is the same
    fields1 = layer1.fields()
    fields2 = layer2.fields()
    assert fields1 == fields2, "Field definitions are different."

    # Compare features count
    assert layer1.featureCount() == layer2.featureCount(), "Feature count differs."

    # Compare geometries and attributes
    features1 = {f.id(): f for f in layer1.getFeatures()}
    features2 = {f.id(): f for f in layer2.getFeatures()}

    assert set(features1.keys()) == set(features2.keys()), "Feature IDs do not match."

    for fid, feature1 in features1.items():
        feature2 = features2[fid]

        # Compare geometries
        assert feature1.geometry().equals(feature2.geometry()), f"Geometry mismatch for feature {fid}."

        # Compare attributes
        assert feature1.attributes() == feature2.attributes(), f"Attribute mismatch for feature {fid}."


def check_gpkg_layers(gpkg_path, expected_layer_name):
    """Ensure the GeoPackage file exists and contains the expected layer."""
    assert os.path.exists(gpkg_path), f"GeoPackage file not found: {gpkg_path}"

    data_source = ogr.Open(gpkg_path)
    assert data_source is not None, f"Could not open GeoPackage: {gpkg_path}"

    layer_names = [data_source.GetLayer(i).GetName() for i in range(data_source.GetLayerCount())]
    assert expected_layer_name in layer_names, f"Layer '{expected_layer_name}' not found in {gpkg_path}. Available layers: {layer_names}"