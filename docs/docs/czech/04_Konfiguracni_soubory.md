# Konfigurační soubory
!!! note "Poznámka"
	Konfigurační soubory se nachází ve složce _config_

### layers_merging_order.csv
Tento jednoduchý CSV soubor obsahuje v každém řádku název vrstvy poskytované ZABAGED WFS službou. Jejich pořadí určuje prioritu, podle níž jsou polygonové vrstvy (nebo obálky v případě liniových vrstev) zapisovány do výsledné vrstvy půdního pokryvu (využití území). Z vrstev uvedených později jsou odstraněny překrývající se části s dříve uvedenými vrstvami. Označení *LPIS_layer* neslouží ke stažení vrstvy, ale pouze určuje prioritu vrstvy z WFS LPIS služby.

```csv
ZABAGED_POLOHOPIS:Budova_jednotlivá_nebo_blok_budov__plocha_
ZABAGED_POLOHOPIS:Kůlna__skleník__fóliovník__přístřešek
...
LPIS_layer
ZABAGED_POLOHOPIS:Lesní_průsek
ZABAGED_POLOHOPIS:Areál_účelové_zástavby
```

### zabaged_to_LandUseCode_table.yaml
Tento YAML soubor obsahuje mapovací seznam s dvojicí klíčových hodnot `keywords` a `code`. `Keywords` obsahuje seznam textových řetězců a `code` jedno celé číslo.

Soubor je využit k mapování kódů půdního pokryvu (využití území) u jednoznačných vstupních vrstev, které neobsahují atributové pole využitelné pro detailní, hydrologicky relevantní, diferenciaci objektů dané vrstvy. Pokud se alespoň jeden řetězec uvnitř seznamu `keywords` nachází v názvu získané ZABAGED vrstvy, je takové vrstvě přiřazen kód využití území z příslušného klíče `code`. 

Pokud je v názvu libovolné vrstvy nalezena shoda dle více mapovacích pravidel, bude výsledná hodnota klíče `code` odpovídat poslední nalezené shodě.  

Tento postup je zvolen tak, aby při drobné změně názvů vrstev poskytovatelem bylo toto přiřazení stále funkční.

```yaml
land_use:
  - keywords: [Travní, travní, Travni, travni]
    code: 20000
  - keywords: [Lesní, lesní, Lesni, lesni]
    code: 32100 # platí pro Lesní průsek a Lesní půdu s křovinatým porostem
  - keywords: [Kosodřevinou, kosodřevinou, Kosodrevinou, kosodrevinou]
    code: 32200
```

### ZABAGED.yaml
Tento soubor obsahuje informace o vrstvách stahovaných ze ZABAGED WFS služby a slouží k jejich úpravě, konkrétně aplikaci bufferu a přiřazení detailního kódu půdního pokryvu (využití území).

První řádek obsahuje URL adresu služby pod klíčem `URL`. 

Následuje sekce *buffer leyers*, která obsahuje seznam vrstev pro aplikaci funkce buffer. Ten definuje hodnoty:

- `input_layer_name`: název vrstvy ZABAGED
- `controlling_atr_name`: název atributového pole, které řídí velikost geometrické obálky (bufferu)
- `default_buffer`: hodnota bufferu v metrech, pokud řídicí atribut nestanoví jinak
- `buffer_levels`: seznam úrovní bufferů dle hodnot řídicího atributu

Každá úroveň v `buffer_levels` zahrnuje:

- `priority`: číslo určující prioritu - aktuálně plugin nevyužívá
- `values`: seznam jedné nebo více hodnot řídicího atributu
- `distance`: velikost bufferu v metrech

Pokud `controlling_atr_name` není uveden ("NaN") nebo pole není nalezeno, použije se `default_buffer`.

Dále navazuje sekce *layers*, ve které jsou přiřazeny hodnoty kódu půdního pokryvu (vyvyužití území) objektům ve vrstvách ZABAGED na základě hodnot řídicího atributu. Pro každou z uvedených vrstev jsou dále definovány hodnoty:

- `name`: název vrstvy ZABAGED
- `base_use_code`: základní kód půdního pokryvu (využití území) přiřazený všem objektům vrstvy
- `controlling_attribute`: název řídicího atributu pro upřesnění kódu
- `value_increments`: mapa dvojic hodnot řídicího atributu a přírůstků pro opravu základního kódu, za hashtagem výsledný kód pro lepší čitelnost a význam kódu

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
`LPIS.yaml` obsahuje informace o vrstvě stahované z LPIS WFS služby. Klíč `URL` obsahuje adresu WFS služby. Dále se definuje:

- `layer_name`: název varianty LPIS vrstvy ke stažení
- `layers`: seznam obsahující specifikaci jediné vrstvy označené jako `LPIS_layer` (název přiřazen při stažení WFS službou), která se následně sloučí s vrstvami ze ZABAGED dle pořadí v souboru `layers_merging_order.csv`.

Stejně jako u ZABAGED se přiřazuje:

- `base_use_code`: základní hodnota kódu půdního pokryvu (využití území) přiřazená všem objektům vrstvy
- `controlling_attribute`: název řídicího atributu pro upřesnění kódu
- `value_increments`: mapa dvojic hodnot řídicího atributu a přírůstků pro opravu základního kódu, za hashtagem výsledný kód pro lepší čitelnost a význam kódu

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

### Soil.yaml
Tento soubor obsahuje dvě hodnoty:

- `URL`: adresa WPS služby poskytující data o půdách
- `process_identifier`: název požadovaného procesu poskytující vrstvu hydrologických skupin půd (HSG)


### Soil_template.xml
Tento soubor je šablonou XML pro komunikaci s WPS službou, která poskytuje vrstvu hydrologických skupin půd. Do šablony se doplňují souřadnice polygonu a jeho atributy před odesláním požadavku.

### CN_table.csv
Tato CSV tabulka slouží pro přiřazení hodnot CN pro průměrný stav nasycení (CN2) dle kombinace kódu půdního pokryvu (využití území) a hydrologické skupiny půd. Obsahuje:

- 1) sloupec: kód půdního pokryvu (využití území)
- 2)–5) sloupec: hodnoty CN2 pro skupiny A, B, C, D

Profesionální uživatel může použít jinou převodní tabulku se stejnou strukturou datových polí.

### WPS_config.yaml
Tento soubor obsahuje dvě hodnoty:

- `URL`: adresa WPS služby poskytující data pro hydrologické modelování ze serveru rain.fsv.cvut.cz
- `process_identifier`: specifikace procesu WPS služby poskytující CSV soubory s daty o šestihodinových návrhových srážkách
