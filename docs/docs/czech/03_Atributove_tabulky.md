# Atributové tabulky

## Vrstva půdního povrchu / využití území (Land Use Layer)

!!! note "Poznámka"
    Pořadí se může mírně lišit v závislosti na stahovaných vrstvách nacházejících se v zájmovém území

| **OBJECT_ID** | **FID** | **FID_ZBG**      | **Shape_Length** | **Shape_Area**     | **source**                                                   | **LandUse_code** | **...** |
|---------------|---------|------------------|------------------|--------------------|--------------------------------------------------------------|------------------|---------|
| 474174        | 11390   | 9118867599130624 | 25.91594895      | 41.976849999744445 | ZABAGED_POLOHOPIS:Budova_jednotlivá_nebo_blok_budov__plocha_ | 41000            | ...     |
| _NULL_        | _NULL_  | _NULL_           | _NULL_           | _NULL_             | LPIS_layer                                                   | 12241            | ...     |
| _NULL_        | 9914363 | 474712196        | 738.75743744     | _NULL_             | ZABAGED_POLOHOPIS:Silnice__dálnice                           | 42100            | ...     |

- OBJECT_ID - indentifikátor poskytovatele
- FID - indentifikátor poskytovatelem
- FID_ZBG - jednoznačný identifikátor objektu v ZABAGED®
- Shape_Length - obvod původního prvku poskytnutého WFS službou
- Shape_Area - Plocha prvku poskytnutá WFS službou. Po získání vrstvy _neodpovídá_ reálné hodnotě a je přepočtena až v procesu výpočtu objemu přímého odtoku.
- __source__ - Název vrstvy poskytované WFS službou (ZABAGED), u dat LPIS DPB uvedeno pouze _LPIS_layer_
- __LandUse_code__ - Kód definující půdní pokryv, případně využití území. Přiřazen na základě konfiguračních souborů ([1](04_Konfiguracni_soubory.md#zabaged_to_landusecode_tableyaml), [2](04_Konfiguracni_soubory.md#zabagedyaml)). Je také využit v [tabulce CN hodnot](04_Konfiguracni_soubory.md#cn_tablecsv) pro přiřazení čísel CN. 

- ... - Další atributy v tabluce jsou převzaty ze stahovaných vrstev [ZABAGED](https://geoportal.cuzk.cz/Dokumenty/ZABAGED_katalog/CS/intro.html) a [LPIS](https://mze.gov.cz/public/portal/mze/-a20344---q65sdr4J/popis-atributu-ve-verejnych-exportech-dat-lpis?_linka=a492260) 

## Vrstva hydrologických skupin půd (Soil Layer HSG)
| **ID** | **HSG** | **fid** | **layer** | **path**                                            |
|--------|---------|---------|-----------|-----------------------------------------------------|
| 1      | 0       | _NULL_  | output    | MultiPolygon?crs=EPSG:5514&field=ID:integer(0,0)... |
| _NULL_ | 3       | 1       | output    | MultiPolygon?crs=EPSG:5514&field=ID:integer(0,0)... |
| _NULL_ | 2       | 2       | output    | MultiPolygon?crs=EPSG:5514&field=ID:integer(0,0)... |

- ID - hodnota 1 přiřazena podkladové vrstvě vyplňující plochy bez přiřazené hodnoty HSG.
- __HSG__ - číselný kód hydrologické skupiny půd (0 = plochy bez HSG, 1=A, 2=B, 3=C, 4=D).
- fid - Identifikátor prvku přiřazený WPS službou. 
- layer - text _output_ přiřazen při úspěšné polygonizaci vstupní rastrové vrstvy. Bez tohoto atributu může být geometrie prvku nevalidní.
- path - metadata vrstvy

## Propojené vrstvy (Intersected LandUse and HSG)
!!! note "Poznámka"
    Vrstva obsahuje stejné atributy jako obě předchozí, jelikož z nich vychází. Podstatné jsou opět atributy __HSG__ a __LandUse_code__. Pouze následující se liší. V rámci následujícího kroku přiřazení čísel CN dojde u této vrstvy k zahození nadbytečných atributových polí.
	
| **fid** | **fid_2** | **layer** | **path**                                            | **layer_2** | **path_2**                                          |
|---------|-----------|-----------|-----------------------------------------------------|-------------|-----------------------------------------------------|
| 32406   | _NULL_    | clipped   | MultiPolygon?crs=EPSG:5514&field=ID:integer(0,0)... | output      | MultiPolygon?crs=EPSG:5514&field=ID:integer(0,0)... |
| _NULL_  | 1         | clipped   | MultiPolygon?crs=EPSG:5514&field=ID:integer(0,0)... | output      | MultiPolygon?crs=EPSG:5514&field=ID:integer(0,0)... |

- fid -  indentifikátor poskytovatele ZABAGED/LPIS
- fid_2 - Identifikátor prvku přiřazený WPS službou poskytující vrstvu hydrologických skupin půd
- layer - text _clipped_ přiřazen při úspěšném oříznutí vrstev
- path - metadata vrstvy využití území
- layer_2 - text _output_ přiřazen při úspěšné polygonizaci vrstvy hydrologických skupin půd. Bez tohoto atributu může být geometrie prvku nevalidní.
- path_2 - metadata vrstvy hydrologických skupin půd



## Vrstva CN hodnot (CN Layer)
| **FID** | **Shape_Length** | **Shape_Area**  | **source**                                                     | **LandUse_code** | **OBJECTID** | **HSG** | **CN2** | **CN3**           |
|---------|------------------|-----------------|----------------------------------------------------------------|------------------|--------------|---------|---------|-------------------|
| 32406   | 2701.37014425    | 341856.95321526 | ZABAGED_POLOHOPIS:Vodní_plocha                                 | 77200            | NULL         | 0       | 99      | 99.56274595540009 |
| NULL    | 110.92570167     | 521.32182349    | ZABAGED_POLOHOPIS:Lesní_půda_se_stromy_kategorizovaná__plocha_ | 33300            | 2040918      | 2       | 50      | 69.6969696969697  |

- OBJECTID - Indentifikátor poskytovatele ZABAGED/LPIS.
- FID_ZBG - jednoznačný identifikátor původního objektu v ZABAGED®
- Shape_Length - Obvod původního prvku poskytnutého WFS službou.
- Shape_Area - Plocha prvku poskytnutá WFS službou. Po získání vrstvy _neodpovídá_ reálné hodnotě a je přepočtena až v procesu výpočtu objemu přímého odtoku.
- __source__ - Název vrstvy poskytované WFS službou (ZABAGED), u dat LPIS DPB uvedeno pouze _LPIS_layer_
- __LandUse_code__ - Kód definující půdní pokryv, případně způsob využití území. Přiřazen na základě konfiguračních souborů ([1](04_Konfiguracni_soubory.md#zabaged_to_landusecode_tableyaml), [2](04_Konfiguracni_soubory.md#zabagedyaml)). Je také využit v [tabulce CN hodnot](04_Konfiguracni_soubory.md#cn_tablecsv) pro jejich přiřazení. 
- __HSG__ - číselný kód hydrologické skupiny půd (0 = plochy bez HSG, 1=A, 2=B, 3=C, 4=D)
- __CN2__ - Hodnota CN přiřazena z [tabulky](04_Konfiguracni_soubory.md#cn_tablecsv). Představuje hodnotu pro průměrné podmínky předchozího nasycení. 
- __CN3__ - Hodnota CN vypočtena z hodnoty CN2. Reprezentuje podmínky vyššího předchozího nasycení.

	CN3 = CN2 / (0.4036 + 0.005964 x CN2)



## Vrstva výšek přímého odtoku (RunOff Layer)
!!! note "Poznámka"
    Všechny typy výsledných vrstev výšek a objemů přímého odtoku obsahují stejné atributy jako vrstva CN hodnot, jelikož z ní vychází. 

### Při použití 6h srážek na [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz)
!!! note "Poznámka"
	Ukázka obshuje výsledky pouze pro dvě doby opkování 2 a 5 let (N2, N5). 
	
	Pro jiné doby opakování budou názvy polí stejné, pouze část názvu odkazující na dobu opakování (N2, N5, N10, ..) se bude lišit

| **V_N2_m3**       | **CN2_N2_runoff_height_mm** | **CN2_N2_runoff_volume_m3** | **CN3_N2_runoff_height_mm** | **CN3_N2_runoff_volume_m3** | **V_N10_m3**     | **CN2_N10_runoff_height_mm** | **CN2_N10_runoff_volume_m3** | **CN3_N10_runoff_height_mm** | **CN3_N10_runoff_volume_m3** |
|-------------------|-----------------------------|-----------------------------|-----------------------------|-----------------------------|------------------|------------------------------|------------------------------|------------------------------|------------------------------|
| 2537.829236336099 | 24.743203117150543          | 2411.544190664504           | 26.305069501921043          | 2563.768209072887           | 4279.45426857832 | 42.4599316851946             | 4138.267834873376            | 44.08827672231118            | 4296.971055150222            |

- V_N2_m3 - objem přímého odtoku v m3 z daného prvku (polygonu) pro dobu opakování 2 roky vážený podle pravděpodobnosti zastoupení 6 tvarů hyetogramů a pravděpodobnosti abnormálního nasycení
- CN2_N2_runoff_height_mm - odtoková výška v milimetrech vypočtená z návrhového 6hodinového úhrnu v zájmové lokalitě získaného z WPS služby pro dobu opakování 2 roky a hodnoty CN2
- CN2_N2_runoff_volume_m3 - objem odtoku v m3 z daného prvku (polygonu) vypočtený z plochy prvku a odtokové výšky _CN2_N2_runoff_height_mm_ (pro průměrné podmínky dané CN2)
- CN3_N2_runoff_height_mm - odtoková výška v milimetrech vypočtená z návrhového 6hodinového úhrnu v zájmové lokalitě získaného z WPS služby pro dobu opakování 2 roky a hodnoty CN3
- CN3_N2_runoff_volume_m3 - objem odtoku v m3 z daného prvku (polygonu) vypočtený z plochy prvku a odtokové výšky _CN3_N2_runoff_height_mm_ (pro vlhké podmínky dané CN3)
 <br>  <br>
- V_N10_m3 - objem přímého odtoku v m3 z daného prvku (polygonu) pro dobu opakování 10 let vážený podle pravděpodobnosti zastoupení 6 tvarů hyetogramů a pravděpodobnosti abnormálního nasycení
- CN2_N10_runoff_height_mm - odtoková výška v milimetrech vypočtená z návrhového 6hodinového úhrnu v zájmové lokalitě získaného z WPS služby pro dobu opakování 10 let a hodnoty CN2
- CN2_N10_runoff_volume_m3 - objem odtoku v m3 z daného prvku (polygonu) vypočtený z plochy prvku a odtokové výšky _CN2_N10_runoff_height_mm_ (pro průměrné podmínky dané CN2)
- CN3_N10_runoff_height_mm - odtoková výška v milimetrech vypočtená z návrhového 6hodinového úhrnu v zájmové lokalitě získaného z WPS služby pro dobu opakování 10 let a hodnoty CN3
- CN3_N10_runoff_volume_m3 - objem odtoku v m3 z daného prvku (polygonu) vypočtený z plochy prvku a odtokové výšky _CN3_N10_runoff_height_mm_ (pro vlhké podmínky dané CN3)

### Při výpočtu z jednoho návrhového úhrnu zadaného uživatelem
| **CN2_runoff_height_mm** | **CN2_runoff_volume_m3** | **CN3_runoff_height_mm** | **CN3_runoff_volume_m3** |
|--------------------------|--------------------------|--------------------------|--------------------------|
| 13.45340226457616        | 42.854151425353045       | 37.43211159302552        | 119.23536863251337       |

- CN2_runoff_height_mm - odtoková výška v milimetrech vypočtená z návrhového úhrnu zadaného uživatelem při použití hodnot CN2
- CN2_runoff_volume_m3 - objem odtoku v m3 z daného prvku (polygonu) vypočtený z plochy prvku a odtokové výšky _CN2_runoff_height_mm_ (pro průměrné podmínky dané CN2)
- CN3_runoff_height_mm - odtoková výška v milimetrech vypočtená z návrhového úhrnu zadaného uživatelem při použití hodnot CN3
- CN3_runoff_volume_m3 - objem odtoku v m3 z daného prvku (polygonu) vypočtený z plochy prvku a odtokové výšky _CN3_runoff_height_mm_ (pro vlhké podmínky dané CN3)

### Při výpočtu z více návrhových úhrnů zadaných uživatelem
!!! note "Poznámka"
    Ukázka tabuky je pro dvě zadané hodnoty. Při více hodnotách se budou lišit pouze části názvu odkazující na pořadí zadaného návrhového úhrnu: 
	
	CN2_1_runoff_height_mm , CN2_2_runoff_height_mm , CN2_3_runoff_height_mm, ... 
	
	Výsledná pole obsahují stejné veličiny jako v předchozím případě, jen pro více vstupních návrhových úhrnů.
	
| **CN2_1_runoff_height_mm** | **CN2_1_runoff_volume_m3** | **CN3_1_runoff_height_mm** | **CN3_1_runoff_volume_m3** | **CN2_2_runoff_height_mm** | **CN2_2_runoff_volume_m3** | **CN3_2_runoff_height_mm** | **CN3_2_runoff_volume_m3** |
|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|----------------------------|
| 13.45340226457616          | 42.854151425353045         | 37.43211159302552          | 119.23536863251337         | 77.00143626535197          | 7504.782845589686          | 78.67677931229387          | 7668.066627931615          |
