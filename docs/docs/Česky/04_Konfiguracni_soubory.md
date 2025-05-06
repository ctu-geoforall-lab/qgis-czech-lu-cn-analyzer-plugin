# Konfigurační soubory
!!! note "Poznámka"
	Konfigurační soubory se nachází ve složce _config_

### layers_merging_order.csv
Tento jednoduchý CSV soubor obsahuje v každém řádku název vrstvy poskytované ZABAGED WFS službou. Jejich pořadí určuje pořadí, ve kterém budou spojeny do jedné vrstvy využití území. Vrstvy uvedené dříve budou připojeny nad vrstvy pod nimi. Označení *LPIS_layer* neslouží ke stažení vrstvy, ale pouze určuje pořadí vrstvy z WFS LPIS služby.

```csv
ZABAGED_POLOHOPIS:Heliport
ZABAGED_POLOHOPIS:Budova_jednotlivá_nebo_blok_budov__plocha_
ZABAGED_POLOHOPIS:Silnice__dálnice
LPIS_layer
ZABAGED_POLOHOPIS:Okrasná_zahrada__park
```

### zabaged_to_LandUseCode_table.yaml
Toto je YAML soubor, který obsahuje seznam map s klíči `keywords` a `code`. `Keywords` obsahuje seznam řetězců a `code` jedno celé číslo.

Soubor je využit k mapování kódů využití území. Pokud se alespoň jeden řetězec uvnitř seznamu `keywords` nachází v názvu získané ZABAGED vrstvy, je takové vrstvě přiřazen kód využití území z korespondujícího klíče `code`.

Tento postup je zvolen tak, aby při změně názvů vrstev poskytovatelem bylo toto přiřazení stále funkční.

```yaml
land_use:
  - keywords: [Orná, orná, Orna, orna]
    code: 10000
  - keywords: [Travní, travní, Travni, travni]
    code: 20000
  - keywords: [Lesní, lesní, Lesni, lesni]
    code: 30000
```

### ZABAGED.yaml
Tento soubor obsahuje informace o vrstvách stahovaných ze ZABAGED WFS služby a slouží k jejich úpravě, konkrétně aplikaci bufferu a zpřesnění kódu využití území.

První řádek obsahuje URL adresu služby pod klíčem `URL`. Dále následuje seznam vrstev s buffery, kde každá má:

- `input_layer_name`: název vrstvy
- `controlling_atr_name`: název atributu, který určuje typ objektu
- `default_buffer`: hodnota bufferu v metrech, pokud není jiná určena
- `buffer_levels`: seznam úrovní bufferů dle hodnot atributu

Každá úroveň v `buffer_levels` má:

- `priority`: číslo určující prioritu
- `values`: seznam hodnot atributu
- `distance`: velikost bufferu v metrech

Pokud `controlling_atr_name` není uveden, použije se pouze `default_buffer`.

Dále soubor obsahuje seznam vrstev, kterým je možné zpřesnit hodnotu kódu využití území pomocí:

- `base_use_code`: základní kód využití území
- `controlling_attribute`: název atributu
- `value_increments`: mapa hodnot atributu a přírůstků ke kódu

```yaml
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
      J: 3200  # jehličnatý
      L: 3100  # listnatý
      S: 3300  # smíšený
```

### LPIS.yaml
`LPIS.yaml` obsahuje informace o vrstvě stahované z LPIS WFS služby. Klíč `URL` obsahuje adresu WFS služby. Dále se definuje:

- `layer_name`: název vrstvy ke stažení
- `layers`: seznam obsahující specifikaci vrstvy označené jako `LPIS_layer`, která se následně sloučí s ostatními dle pořadí.

Stejně jako u ZABAGED se přiřazuje:

- `base_use_code`: základní hodnota kódu využití území
- `controlling_attribute`: atribut, dle kterého se rozhoduje
- `value_increments`: mapa hodnot atributu a přírůstků ke kódu

```yaml
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
```

### Soil.yaml
Tento soubor obsahuje dvě hodnoty:

- `URL`: adresa WPS služby poskytující data HSP
- `process_identifier`: název požadovaného procesu poskytující HSP vrstvu


### Soil_template.xml
Tento soubor je šablonou XML pro komunikaci s WPS službou, která poskytuje vrstvu hydrologických skupin půd. Do šablony se doplňují souřadnice polygonu a jeho atributy před odesláním požadavku.

### CN_table.csv
Tato CSV tabulka slouží pro přiřazení hodnot CN dle kombinace kódu využití území a typu hydrologické skupiny půd. Obsahuje:

- 1) sloupec: kód využití území
- 2)–5) sloupec: hodnoty CN pro skupiny A, B, C, D

Některé hodnoty mohou být desetinné pro větší přesnost. Uživatel může použít jinou tabulku se stejnou strukturou.

### WPS_config.yaml
Tento soubor obsahuje dvě hodnoty:

- `URL`: adresa WPS služby poskytující data o šestihodinových srážkách
- `process_identifier`: název požadovaného procesu služby poskytující CSV soubory pro další výpočet
