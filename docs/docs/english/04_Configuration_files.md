# Configuration Files
!!! note "Note"
     The configuration files are located in the _config_ folder

###  layers_merging_order.csv
 This simple CSV file contains, on each line, the name of a layer provided by the ZABAGED WFS service. Their order determines the priority used for writing the polygon feature layers (or buffers for linear types) into the final Land Cover (Land Use) layer. Parts from each proccessed layer overlapping with previously listed layers are clipped out. The item denoted as *LPIS_layer* does not fetch a layer, it only specifies the position of the LPIS layer retrieved from a separately defined WFS service.

```csv
ZABAGED_POLOHOPIS:Budova_jednotlivá_nebo_blok_budov__plocha_
ZABAGED_POLOHOPIS:Kůlna__skleník__fóliovník__přístřešek
...
LPIS_layer
ZABAGED_POLOHOPIS:Lesní_průsek
ZABAGED_POLOHOPIS:Areál_účelové_zástavby
```

###  zabaged_to_LandUseCode_table.yaml
 This YAML file contains a mapping list of the key-value pairs. The key `keywords` contains a list of strings and the value `code` must hold a single integer.

 The file is used to assign the Land Cover (Land Use) codes to the simple-case input layers, which do not contain any specific attribute field applicable for detailed code differentiation of the layer's features (from the hydrological point of view). If at least one of the strings in a `keywords` list appears in the name of a ZABAGED layer, corresponding `code` value is assigned to all features within that layer.

 If `keywords` from multiple lines match, the resulting `code` from the last of them will be used (last match wins).

 This approach helps to ensure that the mapping remains functional even if the data provider makes minor changes in the layer names.

```yaml
land_use:
  - keywords: [Travní, travní, Travni, travni]
    code: 20000
  - keywords: [Lesní, lesní, Lesni, lesni]
    code: 32100 # platí pro Lesní průsek a Lesní půdu s křovinatým porostem
  - keywords: [Kosodřevinou, kosodřevinou, Kosodrevinou, kosodrevinou]
    code: 32200
```

###  ZABAGED.yaml
 This file contains information about layers downloaded from the ZABAGED WFS service and is used for their processing, specifically application of buffers and Land Cover (Land Use) codes assignment.

 The first line specifies the service URL under the `URL` key. 

 Next section *buffer layers* contains the list of layers intended for buffer application. Following parameters are defined:

 - `input_layer_name`: the ZABAGED layer name  
 - `controlling_atr_name`: name of the attribute field, that controls the buffer size
 - `default_buffer`: the buffer size in meters, applied if no controlling attribute is specified  
 - `buffer_levels`: a list of buffer levels based on values of controlling attribute  

 Each level in `buffer_levels` features:

 - `priority`: a number indicating priority - currently not utilized by the plugin  
 - `values`: a list with one or multiple values of the controlling attribute  
 - `distance`: the buffer size in meters  

 If `controlling_atr_name` is not provided ("NaN") or the field does not exist, `default_buffer` is applied to every feature.

 The second section *layers* defines how the Land Cover (Land Use) codes are assigned to more complex ZABAGED layers based on values of controlling attribute. For each of the listed layers, following parameters are defined:

 - `name`: ZABAGED layer name
 - `base_use_code`: the base Land Cover (Land Use) code assigned to every feature in the layer
 - `controlling_attribute`: name of the attribute field controlling adjustments of the code values
 - `value_increments`: pair values of controlling attribute and code increment; after the hashtag sign the final code and description may be listed for better readability

```yaml
URL: "https://ags.cuzk.cz/arcgis/services/ZABAGED_POLOHOPIS/MapServer/WFSServer"

buffer_layers:
  - input_layer_name: "ZABAGED_POLOHOPIS:Ulice"
    controlling_atr_name: "typulice_k"
    buffer_levels:
      - priority: "1"
        values: ["026", "926"] # US, USm - ulice sjízdná v sídle a mimo sídlo
        distance: 3.0
      - priority: "2"
        values: ["225"] # Uch - ulice typu chodník
        distance: 2.0
      - priority: "3"
        values: ["025"] # UN - ulice nesjízdná v sídle
        distance: 1.5
      - priority: "4"
        values: ["925"] # UNm - ulice nesjízdná mimo sídlo
        distance: 1.0
      - priority: "5"
        values: ["125"] # UX - ulice neexistující v terénu
        distance: 0.0
    default_buffer: 2.0

  - input_layer_name: "ZABAGED_POLOHOPIS:Silnice_neevidovaná"
    controlling_atr_name: "NaN"
    default_buffer: 2.5

layers:
  - name: "ZABAGED_POLOHOPIS:Železniční_točna__přesuvna"
    base_use_code: 40000  
    controlling_attribute: "TYPOBZEL_K"
    value_increments:
      TO: 2300 # 42.300 ~ točna
      PR: 1000 # 41.000 ~ přesuvna  
```

### LPIS.yaml
 `LPIS.yaml` contains specifications for the input layer downloaded from the LPIS WFS service. The `URL` key holds the WFS service address. It then defines:

 - `layer_name`: the name of the LPIS layer variant to download 
 - `layers`: a list containing the specification of a single layer marked as `LPIS_layer` (the name is assigned upon the download from the WFS service), which is consequently merged with ZABAGED layers in the order specified by the `layers_merging_order.csv`config file.

 Similarily as with ZABAGED, for the LPIS layer following parameters need to be specified:

 - `base_use_code`: the base Land Cover (Land Use) code assigned to every feature within the layer
 - `controlling_attribute`: name of the attribute field controlling adjustments of the code values
 - `value_increments`: pair values of controlling attribute and code increment; after the hashtag sign the final code and description may be listed for better readability

```yaml
URL: "https://mze.gov.cz/public/app/wms/plpis_wfs.fcgi"
layer_name: "LPIS_DPB_UCINNE"

layers:
  - name: "LPIS_layer"
    base_use_code: 10000 # ~ orná půda bez dalšího určení
    controlling_attribute: "kultura"
    value_increments:
      "chmelnice": 42001 # 52.001 ~ chmelnice na zemědělské půdě (LPIS)
      "jiná kultura": 43001 # 53.001 ~ ovocný sad na zemědělské půdě (LPIS)
      "jiná trvalá kultura": 43001 # 53.001 ~ ovocný sad na zemědělské půdě (LPIS)
      "mimoprodukční plocha": 51100 # 61.100 ~ ext. smíšené porosty, rozptýlené dřeviny s travním podrostem, s převahou křovin
      ...
```

###  Soil.yaml
 This file contains two items:

 - `URL`: the address of the WPS service providing soil data  
 - `process_identifier`: the identifier of the process that provides the HSG layer  


### Soil_template.xml
 This file is an XML template for communicating with the WPS service that provides the Hydrologic Soil Group layer. Coordinates of the AOI polygon and its attributes are inserted into the template before sending the request.

###  CN_table.csv
 This CSV table is used to assign CN values for the average moisture conditions (CN2) based on the combination of Land Cover (Land Use) code and Hydrologic Soil Group. It contains:

 - 1. Column: Land Cover (Land Use) code  
 - 2.–5. Columns: CN2 values for soil groups A, B, C, D  

 Advanced users may use customary look-up table, but the column-structure must be kept the same.

### WPS_config.yaml
 This file contains two values:

 - `URL`: the address of the WPS service providing data for hydrological modelling, operated at rain.fsv.cvut.cz
 - `process_identifier`: specification of the WPS sevrice process providing CSV files with 6-hour design rainfall data  
