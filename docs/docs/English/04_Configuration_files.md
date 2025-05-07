# Configuration Files
!!! note "Note"
     The configuration files are located in the _config_ folder

###  layers_merging_order.csv
 This simple CSV file contains, on each line, the name of a layer provided by the ZABAGED WFS service. Their order determines the sequence in which they will be merged into a single land use layer. Layers listed earlier will be overlaid above those listed later. The designation *LPIS_layer* does not fetch a layer but only specifies the position of the LPIS WFS layer.

 ~~~csv
 ZABAGED_POLOHOPIS:Heliport
 ZABAGED_POLOHOPIS:Budova_jednotlivá_nebo_blok_budov__plocha_
 ZABAGED_POLOHOPIS:Silnice__dálnice
 LPIS_layer
 ZABAGED_POLOHOPIS:Okrasná_zahrada__park
 ~~~

###  zabaged_to_LandUseCode_table.yaml
 This YAML file contains a list of maps with the keys `keywords` and `code`. `keywords` holds a list of strings and `code` is a single integer.

 The file is used to map land use codes. If at least one of the strings in a `keywords` list appears in the name of a ZABAGED layer, that layer is assigned the corresponding `code` value.

 This approach ensures that the mapping remains functional even if the provider changes layer names.

 ~~~yaml
 land_use:
   - keywords: [Orná, orná, Orna, orna]
     code: 10000
   - keywords: [Travní, travní, Travni, travni]
     code: 20000
   - keywords: [Lesní, lesní, Lesni, lesni]
     code: 30000
 ~~~

###  ZABAGED.yaml
 This file contains information about layers downloaded from the ZABAGED WFS service and is used for their processing, specifically applying buffers and refining land use codes.

 The first line specifies the service URL under the `URL` key. Next is a list of buffer layers, where each entry has:

 - `input_layer_name`: the layer name  
 - `controlling_atr_name`: the attribute name that determines the object type  
 - `default_buffer`: the buffer distance in meters, used if no other is specified  
 - `buffer_levels`: a list of buffer levels based on attribute values  

 Each level in `buffer_levels` includes:

 - `priority`: a number indicating priority  
 - `values`: a list of attribute values  
 - `distance`: the buffer size in meters  

 If `controlling_atr_name` is not provided, only `default_buffer` is applied.

 The file also contains a list of layers for which land use codes can be refined using:

 - `base_use_code`: the base land use code  
 - `controlling_attribute`: the attribute name  
 - `value_increments`: a map of attribute values to code increments  

 ~~~yaml
 URL: "https://ags.cuzk.cz/arcgis/services/ZABAGED_POLOHOPIS/MapServer/WFSServer"

 buffer_layers:
   - input_layer_name: "ZABAGED_POLOHOPIS:Silnice__dálnice"
     controlling_atr_name: "typsil_k"
     buffer_levels:
       - priority: "1"
         values: ["D1", "D2", "M", "D1p", "Mp", "Mv"]
         distance: 20
       - priority: "2"
         values: ["S1", "S1v", "S1p"]
         distance: 12.5
       - priority: "3"
         values: ["S2", "S3", "D2p", "S2p", "S2v", "S3p", "S3v"]
         distance: 10
     default_buffer: 7.5

   - input_layer_name: "ZABAGED_POLOHOPIS:Silnice_neevidovaná"
     controlling_atr_name: "NaN"
     default_buffer: 7.5

 layers:
   - name: "ZABAGED_POLOHOPIS:Lesní_půda_se_stromy_kategorizovaná__plocha_"
     base_use_code: 30000
     controlling_attribute: "druh_k"
     value_increments:
       N: 0
       J: 3200   #jehlicnaty
       L: 3100   #listnaty
       S: 3300   #smiseny
 ~~~

### LPIS.yaml
 `LPIS.yaml` contains information about the layer downloaded from the LPIS WFS service. The `URL` key holds the WFS service address. It then defines:

 - `layer_name`: the name of the layer to download  
 - `layers`: a list containing the specification of the layer marked as `LPIS_layer`, which will be merged according to the defined order  

 As with ZABAGED, it assigns:

 - `base_use_code`: the base land use code  
 - `controlling_attribute`: the attribute used for decision-making  
 - `value_increments`: a map of attribute values to code increments  

 ~~~yaml
 URL: "https://mze.gov.cz/public/app/wms/plpis_wfs.fcgi"
 layer_name: "LPIS_DPB_UCINNE"

 layers:
   - name: "LPIS_layer"
     base_use_code: 10000
     controlling_attribute: "kultura"
     value_increments:
       "standartní orná půda": 0
       "chmelnice": 3100
       "vinice": 3200
 ~~~

###  Soil.yaml
 This file contains two values:

 - `URL`: the address of the WPS service providing HSP data  
 - `process_identifier`: the identifier of the process that provides the HSP layer  

  Soil_template.xml
 This file is an XML template for communicating with the WPS service that provides the hydrological soil group layer. Coordinates of the polygon and its attributes are inserted into the template before sending the request.

###  CN_table.csv
 This CSV table is used to assign CN values based on the combination of land use code and hydrological soil group. It contains:

 1. Column: land use code  
 2.–5. Columns: CN values for groups A, B, C, D  

 Some values may be decimals for greater precision. Users can supply an alternative table with the same structure.

  WPS_config.yaml
 This file contains two values:

 - `URL`: the address of the WPS service providing six-hour precipitation data  
 - `process_identifier`: the identifier of the process that provides CSV files for further calculations  
