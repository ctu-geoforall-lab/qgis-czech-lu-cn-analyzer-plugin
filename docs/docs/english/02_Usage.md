# Usage  
!!! warning "Attention"  
     Before starting data download, it is necessary to set the project's CRS to __EPSG:5514__<br>
     [How?](https://www.youtube.com/watch?v=OmPH1es1w1k)  

## Data Download Tab (Download)  
 - First, the area of interest must be specified  
     - To download data within the current map view, select _Current window extent_  
     - To download data defined by a polygon layer, select _Polygon layer_  
         - This action will allow you to pick a polygon from the project in the dropdown below  

 - Next, data for download may be selected  
     - To download both Land Cover (Land Use) data and Hydrologic soil groups data, select _Land Use + Hydrologic Soil Groups_  
     - To download only Land Cover (Land Use) data, select _only Land Use_  
     - To download only Hydrologic soil groups data, select _only Hydrologic Soil Groups_

 - To start the download, click the _Download_ button  
 - To stop the download process, click the _Abort_ button  

 <p align="center">  
     <img src="../../img/ovl1.png" alt="ovl1" style="height: 60vh;">  
 </p>  

## Layers combination tab (Combine layers)  
 - In the _Select Land Use layer_ dropdown, choose the Land Cover (Land Use) layer  
     - If it was successfully downloaded in the previous tab, it will be set automatically as default choice  
     - If you wish to use your own layer, it must contain an attribute field named _LandUse_code_ with integer code values  

 - In the _Select Hydrologic Soil Group layer_ dropdown, choose the Hydrologic soil groups layer  
     - If it was successfully downloaded in the previous tab, it will be set automatically as default choice  
     - If you wish to use your own layer, it must contain an attribute field named _HSG_ with integer values, where:  
         - 1 represents group A  
         - 2 represents group B  
         - 3 represents group C  
         - 4 represents group D  
         - 0 may represent water bodies or unsurveyed areas with undefined soil group  

 - Start combining the layers by clicking the _Combine_ button  

 <p align="center">  
     <img src="../../img/ovl2.png" alt="ovl2" style="height: 60vh;">  
 </p>  

## Curve Number Tab (CN)  
 - In the _Select layer combining Land Use and HSG_ dropdown, choose the layer combined from the Land Cover (Land Use) and Hydrologic soil groups layers
     - If it was successfully created in the previous tab, it will be set automatically as default choice  
     - If you wish to use your own layer, it must contain integer attribute fields named _LandUse_code_ and _HSG_  

 - The string field below shows the path to the CSV file for CN value assignment
 - Default path points to a CSV with CN values derived specifically for the Land Cover layer based on ZABAGED and LPIS data  
 - To choose the location of your own CSV file, click the three-dot icon next to this field  
 - To create the CN layer, click the _Create CN layer_ button  

 <p align="center">  
     <img src="../../img/ovl3.png" alt="ovl3" style="height: 60vh;">  
 </p>  

## Direct Runoff Volume Calculation Tab (Runoff)  
 - In the _Select CN layer_ dropdown, choose the CN layer  
     - If it was successfully created in the previous tab, it will be set automatically as default choice  
     - If you wish to use your own layer, it must contain an attribute field named _CN2_ with values within the range (0.0 - 100.0>  
         - Optionally, it may also contain an attribute field named _CN3_ with values within the range (0.0 - 100.0> 

 - In the _Initial Abstraction Coefficient (lambda)_ field below, you can enter a custom value of Initial Abstraction coefficient  
     - Default value 0.2 is reasonable for most cases without any deeper knowledge of the hydrologic behaviour of the study area
     - Based on deeper knowledge, the Ia coefficient may be set to a different value, preferably within the tange 0.05 – 0.3  

 - If you wish to calculate runoff depths and volumes produced by 6-hour design rainfall depths from the [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz) service, select _Use 6-hour rainfall depth from rain.fsv.cvut.cz_ option  
     - Using the checkboxes in the _Select Return Periods_ section choose the desired return periods of the rainfall depth  

 - If you wish to calculate runoff depths and volumes using your own design rainfall depths, select _User-defined rainfall depth  [mm]_ option  
     - In the string field below enter the depth of the rainfall depth in millimeters  
         - To perform calculations for multiple depths, separate them with a semicolon _;_  

 - Start the calculation by clicking the _Compute runoff volume_ button  

 <p align="center">  
     <img src="../../img/ovl4.png" alt="ovl4" style="height: 60vh;">  
 </p>  

## Batch Execution

Batch execution is enabled by `run_batch.py` located in the `scripts` directory. The batch job configuration is specified using a YAML configuration file. An example configuration is available in `tests/batch.yaml`. Example execution:

```
python3 scripts/run_batch.py tests/batch.yaml
```

For MS Windows, a batch file `run_batch.bat` is provided, which automatically sets up the QGIS runtime environment. Before running it, adjust the path to your QGIS installation in this file.

### Using Local Data

Download LPIS and ZABAGED datasets and update the data source paths (`URI`) in the configuration files located in the `config` directory.
