# Attribute Tables  
  
## Land Cover (Land Use) Layer  
 
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
 - Shape_Area – Area of the feature provided by the WFS service. After retrieving the layer, this does _not_ reflect the real value and is recalculated during the direct runoff volume computation process.  
 - **source** – Name of the layer provided by the WFS service (ZABAGED); for LPIS DPB data, only _LPIS_layer_ is shown  
 - **LandUse_code** – Code defining the Land Cover (in some locations Land Use) type. Assigned based on configuration files ([1](04_Configuration_files.md#zabaged_to_landusecode_tableyaml), [2](04_Configuration_files.md#zabagedyaml)). It is also used in the [CN values table](04_Configuration_files.md#cn_tablecsv) for assigning the CN values.  
 - ... – Additional attribute fields are inherited from downloaded [ZABAGED](https://geoportal.cuzk.cz/Dokumenty/ZABAGED_katalog/CS/intro.html) and [LPIS](https://mze.gov.cz/public/portal/mze/-a20344---q65sdr4J/popis-atributu-ve-verejnych-exportech-dat-lpis?_linka=a492260) layers  
  

## Hydrologic Soil Groups layer (Soil Layer HSG) 

| **ID** | **HSG** | **fid** | **layer** | **path**                                           |
|--------|---------|---------|-----------|----------------------------------------------------|
| 1      | 0       | _NULL_  | output    | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |
| _NULL_ | 3       | 1       | output    | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |
| _NULL_ | 2       | 2       | output    | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |

- ID - value 1 is assigned to NoData areas in the source HSG raster layer provided by the WPS service
- __HSG__ - numeric code for Hydrologic Soil Group (0 = areas without HSG, 1=A, 2=B, 3=C, 4=D).
- fid - Identifier assigned by the WPS service. 
- layer - the string _output_ assigned when polygon is succesfully created from the original raster layer. Features with different value in this field may have invalid geometry.
- path - layer metadata


## Combined layer with Land Cover and HSG data (Intersected LandUse and HSG)  
!!! note "Note"  
     This layer contains attribute fields inherited from both parent layers. Key attributes again are **HSG** and **LandUse_code**. Only the below listed fields differ. During the next step (CN assignment), all extra fields are deleted.
	
| **fid** | **fid_2** | **layer** | **path**                                           | **layer_2** | **path_2**                                         |
|---------|-----------|-----------|----------------------------------------------------|-------------|----------------------------------------------------|
| 32406   | _NULL_    | clipped   | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... | output      | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |
| _NULL_  | 1         | clipped   | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... | output      | MultiPolygon?crs=EPSG:5514field=ID:integer(0,0)... |

  
 - fid – provider identifier from ZABAGED/LPIS  
 - fid_2 – feature identifier assigned by the WPS service providing the Soil Hydrologic Groups layer  
 - layer – the string _clipped_ assigned once the input layer is successfuly clipped and appended to the layers with higher priority
 - path – metadata of Land Cover (Land Use) layer  
 - layer_2 – the string _output_ assigned when polygon is succesfully created from the original HSG raster layer. Features with different value in this field may have invalid geometry.  
 - path_2 – metadata of Hydrologic Soil Groups layer  
  

## Curve Number (CN) Layer  

| **FID** | **Shape_Length** | **Shape_Area**  | **source**                                                     | **LandUse_code** | **OBJECTID** | **HSG** | **CN2** | **CN3**           |
|---------|------------------|-----------------|----------------------------------------------------------------|------------------|--------------|---------|---------|-------------------|
| 32406   | 2701.37014425    | 341856.95321526 | ZABAGED_POLOHOPIS:Vodní_plocha                                 | 77200            | NULL         | 0       | 99      | 99.56274595540009 |
| NULL    | 110.92570167     | 521.32182349    | ZABAGED_POLOHOPIS:Lesní_půda_se_stromy_kategorizovaná__plocha_ | 33300            | 2040918      | 2       | 50      | 69.6969696969697  |

 - FID – provider identifier from ZABAGED/LPIS  
 - Shape_Length – perimeter of the original feature provided by the WFS service  
 - Shape_Area – area of the feature provided by the WFS service. After retrieving the layer, this does _not_ reflect the real value and is recalculated during the direct runoff volume computation process.  
 - **source** – Name of the layer provided by the WFS service (ZABAGED); for LPIS DPB data, only _LPIS_layer_ is shown  
 - **LandUse_code** – Code defining the Land Cover (in some locations Land Use) type. Assigned based on configuration files ([1](04_Configuration_files.md#zabaged_to_landusecode_tableyaml), [2](04_Configuration_files.md#zabagedyaml)). It is also used in the [CN values table](04_Configuration_files.md#cn_tablecsv) for assigning the CN values.  
 - **HSG** – numeric code for Hydrologic Soil Group (0 = areas without HSG, 1=A, 2=B, 3=C, 4=D).
 - **CN2** – CN value assigned from the [table](04_Configuration_files.md#cn_tablecsv). It represents average antecedent moisture conditions  
 - **CN3** – CN value calculated from CN2 using the formula below. It represents wet antecedent moisture conditions: 
  
     CN3 = CN2 / (0.4036 + 0.005964 x CN2)  
  
## Runoff Volume Layer  
!!! note "Note"  
     All types of direct runoff depth and volume layers inherit all the attribute fields from the parent CN layer.  
  
### Design 6-hour rainfall depths from [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz)  
!!! note "Note"  
     The example shows results only for 2- and 5-year return periods (N2, N5). 

     For more/different return periods, the attribute field names remain the same; only the part refering to the return period (N2, N5, N10, ...) will differ.  
  
  

| **V_N2_m3**       | **CN2_N2_runoff_height_mm** | **CN2_N2_runoff_volume_m3** | **CN3_N2_runoff_height_mm** | **CN3_N2_runoff_volume_m3** | **V_N10_m3**     | **CN2_N10_runoff_height_mm** | **CN2_N10_runoff_volume_m3** | **CN3_N10_runoff_height_mm** | **CN3_N10_runoff_volume_m3** |
|-------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|------------------|------------------------------|------------------------------|------------------------------|------------------------------|
| 2537.829236336099 | 24.743203117150543          | 2411.544190664504           | 26.305069501921043          | 2563.768209072887           | 4279.45426857832 | 42.4599316851946             | 4138.267834873376            | 44.08827672231118            | 4296.971055150222            |

 - V_N2_m3 – direct runoff volume [m3] from particular feature (polygon) for a 2-year return period, weighted by the occurence probabilities of hyetograph types and the abnormaly wet initial conditions)  
 - CN2_N2_runoff_height_mm – direct runoff depth [mm] from the 6-hour design rainfall within the area of interest derived by the WPS service for the 2-year return period with use of CN2  
 - CN2_N2_runoff_volume_m3 – direct runoff volume [m3] from particular feature (polygon) calculated from the feature’s area and the runoff depth _CN2_N2_runoff_height_mm_ (in the average moisture conditions represented with CN2) 
 - CN3_N2_runoff_height_mm – direct runoff depth [mm] from the 6-hour design rainfall within the area of interest derived by the WPS service for the 2-year return period with use of CN3  
 - CN3_N2_runoff_volume_m3 – direct runoff volume [m3] from particular feature (polygon) calculated from the feature’s area and the runoff depth _CN3_N2_runoff_height_mm_ (in the wet initial conditions represented with CN3)  
 <br>  <br>  
 - V_N10_m3 – direct runoff volume [m3] from particular feature (polygon) for a 10-year return period, weighted by the occurence probabilities of hyetograph types and the abnormaly wet initial conditions)  
 - CN2_N10_runoff_height_mm – direct runoff depth [mm] from the 6-hour design rainfall within the area of interest derived by the WPS service for the 10-year return period with use of CN2  
 - CN2_N10_runoff_volume_m3 – direct runoff volume [m3] from particular feature (polygon) calculated from the feature’s area and the runoff depth _CN2_N10_runoff_height_mm_ (in the average moisture conditions represented with CN2) 
 - CN3_N10_runoff_height_mm – direct runoff depth [mm] from the 6-hour design rainfall within the area of interest derived by the WPS service for the 10-year return period with use of CN3  
 - CN3_N10_runoff_volume_m3 – direct runoff volume [m3] from particular feature (polygon) calculated from the feature’s area and the runoff depth _CN3_N10_runoff_height_mm_ (in the wet initial conditions represented with CN3) 

### Calculation using a single user-defined runoff depth

| **CN2_runoff_height_mm** | **CN2_runoff_volume_m3** | **CN3_runoff_height_mm** | **CN3_runoff_volume_m3** |
|--------------------------|--------------------------|--------------------------|--------------------------|
| 13.45340226457616        | 42.854151425353045       | 37.43211159302552        | 119.23536863251337       |

  
 - CN2_runoff_height_mm – direct runoff depth [mm] calculated from the user-defined rainfall depth with use of CN2  
 - CN2_runoff_volume_m3 – direct runoff volume [m3] from particular feature (polygon) calculated from the feature’s area and the runoff depth _CN2_runoff_height_mm_ (for average moisture conditions represented with CN2)
 - CN3_runoff_height_mm – direct runoff depth [mm] calculated from the user-defined rainfall depth with use of CN3  
 - CN3_runoff_volume_m3 – direct runoff volume [m3] from particular feature (polygon) calculated from the feature’s area and the runoff depth _CN3_runoff_height_mm_ (for wet initial conditions represented with CN3) 
  
### Calculation using multiple user-defined runoff depths
!!! note "Note"  
     The example shows an output table for two input rainfall depths. With more inputs, only the name parts refering to the position of a rainfall depth in the sequence will differ:  
  
     CN2_1_runoff_height_mm, CN2_2_runoff_height_mm, CN2_3_runoff_height_mm, …  
  
     Resulting attribute table contains the same fields as in the previous case, but for multiple rainfall depths as input.  
  
	
| **CN2_1_runoff_height_mm** | **CN2_1_runoff_volume_m3** | **CN3_1_runoff_height_mm** | **CN3_1_runoff_volume_m3** | **CN2_2_runoff_height_mm** | **CN2_2_runoff_volume_m3** | **CN3_2_runoff_height_mm** | **CN3_2_runoff_volume_m3** |
|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|
| 13.45340226457616          | 42.854151425353045         | 37.43211159302552          | 119.23536863251337         | 77.00143626535197          | 7504.782845589686          | 78.67677931229387          | 7668.066627931615          |

