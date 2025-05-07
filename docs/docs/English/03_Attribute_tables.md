# Attribute Tables  
  
## Land Use Layer  
 
!!! note "Note" 
    The order may vary slightly depending on which layers are downloaded within the area of interest 


| **OBJECT_ID** | **FID** | **FID_ZBG**      | **Shape_Length** | **Shape_Area**     | **source**                                                   | **LandUse_code** | **...** |
|---------------|---------|------------------|------------------|--------------------|--------------------------------------------------------------|------------------|---------|
| 474174        | 11390   | 9118867599130624 | 25.91594895      | 41.976849999744445 | ZABAGED_POLOHOPIS:Budova_jednotlivá_nebo_blok_budov__plocha_ | 44100            | ...     |
| _NULL_        | _NULL_  | _NULL_           | _NULL_           | _NULL_             | LPIS_layer                                                   | 20000            | ...     |
| _NULL_        | 9914363 | 474712196        | 738.75743744     | _NULL_             | ZABAGED_POLOHOPIS:Silnice__dálnice                           | 44100            | ...     |


 - OBJECT_ID – provider identifier  
 - FID – provider identifier  
 - FID_ZBG – unique object identifier in ZABAGED®  
 - Shape_Length – perimeter of the original feature provided by the WFS service  
 - Shape_Area – area of the feature provided by the WFS service. After retrieving the layer, this does _not_ reflect the real value and is recalculated during the direct runoff volume computation process.  
 - **source** – Name of the layer provided by the WFS service (ZABAGED); for LPIS DPB data, only _LPIS_layer_ is shown  
 - **LandUse_code** – Code defining the land use type. Assigned based on configuration files ([1](04_Configuration_files.md#zabaged_to_landusecode_tableyaml), [2](04_Configuration_files.md#zabagedyaml)). It is also used in the [CN values table](04_Configuration_files.md#cn_tablecsv) for their assignment.  
 - ... – Additional attributes in the table are taken from downloaded [ZABAGED](https://geoportal.cuzk.cz/Dokumenty/ZABAGED_katalog/CS/intro.html) and [LPIS](https://mze.gov.cz/public/portal/mze/-a20344---q65sdr4J/popis-atributu-ve-verejnych-exportech-dat-lpis?_linka=a492260) layers  
  
## Soil Hydrologic Group Layer (HSG) 

| **ID** | **HSG** | **fid** | **layer** | **path**                                            |
|--------|---------|---------|-----------|-----------------------------------------------------|
| 1      | 0       | _NULL_  | output    | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |
| _NULL_ | 3       | 1       | output    | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |
| _NULL_ | 2       | 2       | output    | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |

## Intersected Land Use and HSG Layer  
!!! note "Note"  
     This layer contains the same attributes as both previous layers, since it is derived from them. Key attributes again are **HSG** and **LandUse_code**. Only the following differ.  
	
| **fid**    | **fid_2**  | **layer**         | **path**                                                | **layer_2** | **path_2**                                              |
|--------|--------|---------------|-----------------------------------------------------|---------|-----------------------------------------------------|
| 32406  | _NULL_ | clean_clipped | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... | output  | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |
| _NULL_ | 1      | clean_clipped | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... | output  | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |

  
 - fid – provider identifier from ZABAGED/LPIS  
 - fid_2 – feature identifier assigned by the WPS service providing the soil hydrologic group layer  
 - layer – text _clean_clipped_ assigned upon successful clipping of layers  
 - path – land use layer metadata  
 - layer_2 – text _output_ assigned upon successful polygonization of the soil hydrologic group layer. Without this attribute, the feature’s geometry may be invalid.  
 - path_2 – soil hydrologic group layer metadata  
  
## Curve Number (CN) Layer  

| **FID** | **Shape_Length** | **Shape_Area**  | **source**                                                     | **LandUse_code** | **OBJECTID** | **HSG** | **CN2** | **CN3**           |
|---------|------------------|-----------------|----------------------------------------------------------------|------------------|--------------|---------|---------|-------------------|
| 32406   | 2701.37014425    | 341856.95321526 | ZABAGED_POLOHOPIS:Vodní_plocha                                 | 77200            | NULL         | 0       | 99      | 99.56274595540009 |
| NULL    | 110.92570167     | 521.32182349    | ZABAGED_POLOHOPIS:Lesní_půda_se_stromy_kategorizovaná__plocha_ | 33300            | 2040918      | 2       | 50      | 69.6969696969697  |

 - FID – provider identifier from ZABAGED/LPIS  
 - Shape_Length – perimeter of the original feature provided by the WFS service  
 - Shape_Area – area of the feature provided by the WFS service. After retrieving the layer, this does _not_ reflect the real value and is recalculated during the direct runoff volume computation process.  
 - **source** – Name of the layer provided by the WFS service (ZABAGED); for LPIS DPB data, only _LPIS_layer_ is shown  
 - **LandUse_code** – Code defining the land use type. Assigned based on configuration files ([1](04_Configuration_files.md#zabaged_to_landusecode_tableyaml), [2](04_Configuration_files.md#zabagedyaml)). It is also used in the [CN values table](04_Configuration_files.md#cn_tablecsv) for their assignment.  
 - OBJECTID – provider identifier from ZABAGED/LPIS  
 - **HSG** – soil hydrologic group value (0 = water body, 1 = A, 2 = B, 3 = C, 4 = D)  
 - **CN2** – CN value assigned from the [table](04_Configuration_files.md#cn_tablecsv) representing average saturation conditions  
 - **CN3** – CN value calculated from CN2 for wet saturation conditions using:  
  
     CN3 = (23 × CN2) / (10 + 0.13 × CN2)  
  
## Runoff Volume Layer  
!!! note "Note"  
     All types of direct runoff volume layers contain the same attributes as the CN layer from which they derive.  
  
### Computed from recurrence intervals at [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz)  
!!! note "Note"  
     The example shows results only for 2- and 5-year return periods (N2, N5). For more periods, the attributes remain the same; only the suffixes indicating the return period (N2, N5, N10, ...) will differ.  
  
  

| **V_N2_m3**       | **CN2_N2_runoff_height_mm** | **CN2_N2_runoff_volume_m3** | **CN3_N2_runoff_height_mm** | **CN3_N2_runoff_volume_m3** | **V_N10_m3**     | **CN2_N10_runoff_height_mm** | **CN2_N10_runoff_volume_m3** | **CN3_N10_runoff_height_mm** | **CN3_N10_runoff_volume_m3** |
|-------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|------------------|------------------------------|------------------------------|------------------------------|------------------------------|
| 2537.829236336099 | 24.743203117150543          | 2411.544190664504           | 26.305069501921043          | 2563.768209072887           | 4279.45426857832 | 42.4599316851946             | 4138.267834873376            | 44.08827672231118            | 4296.971055150222            |


 - V_N2_m3 – Weighted direct runoff volume for a two-year return period (weighted by hyetograph shape probabilities and abnormal saturation likelihood)  
 - CN2_N2_runoff_height_mm – total precipitation depth derived from the WPS service’s direct runoff height for 2-year return period and CN2  
 - CN2_N2_runoff_volume_m3 – runoff volume calculated from the feature’s area and the _CN2_N2_runoff_height_mm_  
 - CN3_N2_runoff_height_mm – total precipitation depth derived from the WPS service’s direct runoff height for 2-year return period and CN3  
 - CN3_N2_runoff_volume_m3 – runoff volume calculated from the feature’s area and the _CN3_N2_runoff_height_mm_  
  
 - V_N10_m3 – Weighted direct runoff volume for a ten-year return period (weighted by hyetograph shape probabilities and abnormal saturation likelihood)  
 - CN2_N10_runoff_height_mm – total precipitation depth derived from the WPS service’s direct runoff height for 10-year return period and CN2 (in mm)  
 - CN2_N10_runoff_volume_m3 – runoff volume calculated from the feature’s area and the _CN2_N10_runoff_height_mm_  
 - CN3_N10_runoff_height_mm – total precipitation depth derived from the WPS service’s direct runoff height for 10-year return period and CN3 (in mm)  
 - CN3_N10_runoff_volume_m3 – runoff volume calculated from the feature’s area and the _CN3_N10_runoff_height_mm_  
### Computed from a single user-provided runoff depth  


| **CN2_runoff_height_mm** | **CN2_runoff_volume_m3** | **CN3_runoff_height_mm** | **CN3_runoff_volume_m3** |
|--------------------------|--------------------------|--------------------------|--------------------------|
| 13.45340226457616        | 42.854151425353045       | 37.43211159302552        | 119.23536863251337       |

  
 - CN2_runoff_height_mm – total precipitation depth calculated from the user-provided runoff height and CN2  
 - CN2_runoff_volume_m3 – runoff volume calculated from the feature’s area and the _CN2_runoff_height_mm_  
 - CN3_runoff_height_mm – total precipitation depth calculated from the user-provided runoff height and CN3  
 - CN3_runoff_volume_m3 – runoff volume calculated from the feature’s area and the _CN3_runoff_height_mm_  
  
### Computed from multiple user-provided runoff depths  
!!! note "Note"  
     The table example is for two input values. With more inputs, only the suffixes will change according to the sequence number:  
  
     CN2_1_runoff_height_mm, CN2_2_runoff_height_mm, CN2_3_runoff_height_mm, …  
  
     Attributes contain the same values as in the previous case, just for multiple inputs.  
  
	
| **CN2_1_runoff_height_mm** | **CN2_1_runoff_volume_m3** | **CN3_1_runoff_height_mm** | **CN3_1_runoff_volume_m3** | **CN2_2_runoff_height_mm** | **CN2_2_runoff_volume_m3** | **CN3_2_runoff_height_mm** | **CN3_2_runoff_volume_m3** |
|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|
| 13.45340226457616          | 42.854151425353045         | 37.43211159302552          | 119.23536863251337         | 77.00143626535197          | 7504.782845589686          | 78.67677931229387          | 7668.066627931615          |

