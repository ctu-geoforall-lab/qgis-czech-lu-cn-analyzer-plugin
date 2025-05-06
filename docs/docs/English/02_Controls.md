# Control  
!!! warning "Attention"  
     Before starting data download, it is necessary to set the project to __EPSG:5514__<br>
     [How?](https://www.youtube.com/watch?v=OmPH1es1w1k)  

## Data Download Tab (Download)  
 - First, you must select the area of interest for data download  
     - To download data within the current map view, select _Compute inside window extent_  
     - To download data inside a polygon, select _Compute inside polygon_  
         - This action will allow you to pick a polygon from the project in the dropdown below  

 - Next, you can choose which data to download  
     - To download both land use data and hydrologic soil group data, select _Land Use and Soil Groups_  
     - To download only land use data, select _only Land Use_  
     - To download only hydrologic soil group data, select _only Hydrology Soil Groups_  

 - To start the download, click the _Download_ button  
 - To stop the download process, click the _Abort_ button  

 <p align="center">  
     <img src="../../img/ovl1.png" alt="ovl1" style="height: 60vh;">  
 </p>  

## Intersection Tab (Intersection)  
 - In the _Select Land Use layer_ dropdown, choose the land use layer  
     - If it was successfully downloaded in the previous tab, it will be set automatically  
     - If you wish to use your own layer, it must contain an attribute named _LandUse_code_ with integer values  

 - In the _Select Hydrology Soil Group layer_ dropdown, choose the hydrologic soil group layer  
     - If it was successfully downloaded in the previous tab, it will be set automatically  
     - If you wish to use your own layer, it must contain an attribute named _HSG_ with integer values, where  
         - 1 represents group A  
         - 2 represents group B  
         - 3 represents group C  
         - 4 represents group D  
         - 0 represents water bodies  

 - Start the intersection by clicking the _Intersect_ button  

 <p align="center">  
     <img src="../../img/ovl2.png" alt="ovl2" style="height: 60vh;">  
 </p>  

## CN Layer Creation Tab (CN)  
 - In the _Select Land Use and HSF Intersected layer_ dropdown, choose the layer resulting from the intersection of land use and hydrologic soil groups  
     - If it was successfully intersected in the previous tab, it will be set automatically  
     - If you wish to use your own layer, it must contain attributes named _LandUse_code_ (integer) and _HSG_ (integer)  

 - The line below shows the path to the CSV file for CN value conversion  
 - To choose the location of your own CSV file, click the three-dot icon next to this line  
 - To create the CN layer, click the _Create CN layer_ button  

 <p align="center">  
     <img src="../../img/ovl3.png" alt="ovl3" style="height: 60vh;">  
 </p>  

## Run-off Volume Calculation Tab (Run-off)  
 - In the _Select CN layer_ dropdown, choose the CN layer  
     - If it was successfully created in the previous tab, it will be set automatically  
     - If you wish to use your own layer, it must contain an attribute named _CN2_ with decimal values  
         - It may also contain an optional attribute named _CN3_ with decimal values  

 - In the _Initial Abstraction Coefficient_ field below, you can enter a custom initial loss ratio coefficient  
     - This can be chosen in the range 0.1 – 0.3  

 - If you wish to calculate run-off volumes using design rainfall depths from the [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz) service for various return periods, select _Use rainfall depth from rain.fsv.cvut.cz_  
     - Then choose the desired return periods via the checkboxes in the _Select Recurrence Intervals_ section above  

 - If you wish to calculate run-off volumes using your own design rainfall depths, select _Define your own rainfall depth  [mm]_  
     - Then enter the values in millimeters in the field below  
         - To perform calculations for multiple depths, separate them with a semicolon _;_  

 - Start the process by clicking the _Compute run-off_ button  

 <p align="center">  
     <img src="../../img/ovl4.png" alt="ovl4" style="height: 60vh;">  
 </p>  
