![plugin icon](https://github.com/ctu-geoforall-lab/qgis-zabaged-plugin/blob/main/docs/images/baner.png?raw=true) <br>
Načítání vrstev není úplně nejrychlejší. <br>
Pro správnou funkci je potřeba mít v projektu nastaven CRS na EPSG:5514 <br>
Testováno na MS Windows a Linux(Ubuntu). <br> <br>

## Funkce pluginu
- Plugin nyní stahuje požadované ZABAGED vrstvy uvnitř výřezu okna či polygonu, pomocí WFS služby. 
- Plugin připojuje LPIS WMS vrstvu
- Stahování probíhá na pozadí v jiném vlákně Qgisu
- Uživatel je informován o procesu stahování a je schopen ho tlačítkem ukončit
- Přířazení LandUse kódu dle názvu ZABAGED vrsty
- Zpřesnění LandUse kódu dle typu porostu v lesní kategorizované ploše (druh_k atribut)
- Na vrstvu silnic je aplikován buffer dle typu silnice
- Polygonové vrstvy ZABAGED jsou spojeny do jedné vrstvy dle dané priority vrstev
- Vstupní parametry jsou čteny z konfiguračních souborů.
- LPIS vrstva je připojena, ohodnocena dle typu parcely a sloučena do finální vrstvy dle priority.
- Dočasné vrstvy nejsou přidávány do projektu.
- **nově: Na výlsednou vrstvu LandUse je aplikován styl.** 

## Popis konfiguračních souborů
Tyto soubory se nachází ve složce *config* <br>
Slouží k uchování paramterů webových služeb (a k jejich editaci pro případ změn na straně poskytovatele) <br>
a pro případnou změnu některých výpočetních postupů <br> <br>

- **zabaged_WFS_URL.conf** - uchovává URL adresu, kde se nachází WFS služba poskytující ZABAGED data.
- **zabagedlayers.conf** - uchovává názvy stahovaných ZABAGED vrstev, které jsou dány poskytovatelem. Nachází se zde pouze vrstvy relevantní pro výpočet.
- **zabaged_to_LandUseCode_table.conf** - uchovává sadu čtyř klíčových slov, která pokud jsou obsažena v názvu ZABAGED vrstvy, tak jí je přiřazena Hodnota LandUse kódu z páté pozice řádku.
- **zabaged_atr_to_Buffer.yaml** - obsahuje názvy vrstev, které je potřeba bufferovat (liniové a bodové). Ty se bufferují dle nějakého atributu a jeho hodnoty v ZABAGED vrstvě. Pro jednotlivé hodnoty tohoto atributu jsou zvoleny vzdálenosti bufferů. (Šířka vozovky je dvojnásobek hodnoty *distance*)
- **zabaged_atr_to_LandUse.yaml** - obsahuje informace pro zpřesnění LandUse kódu ZABAGED vrstvy dle nějakého jejího atributu. K definované hlavní hodnotě LandUse kódu jsou přičítány definované přírůstky dle hodnot řídícího atributu.
- **layers_merging_order.conf** - obsahuje prioritu sloučení ZABAGED vrstev do jedné. Vrstvy uvedeny v souboru výše budou i ve finální vrstvě výše a díky tomu nemohou být překryty vrstvami uvedenými pod nimi. (soubor musí pro správnou funkci obsahovat stejné názvy jako v *zabagedlayers.conf* však v jinak definovaném pořadí a také umístění LPIS vrstvy)
- **LPIS_WFS_URL.conf** - obsahuje URL adresu, kde se nachází WFS služba poskytující LPIS data.
- **LPIS_layer_name.conf** - obsahuje název stahované LPIS vrstvy.
- **LPIS_atr_to_LandUse.yaml** - obsahuje řídící atribut pro změnu hodnoty LandUse kódu, typy atributů, základní hodnotu LandUse kódu a definované přírůstky.
  
## Další informace
- na další bodové a linové prvky je potřeba zvolit buffer
- Je nuntné doplnit další LandUse kódy pro více ZABAGED vrstev

<br><br>
Názvy ZABAGED vrstev, které plugin získává, jsou v souboru zabagedlayers.conf <br>
Některé požadované ZABAGED vrstvy není možné zahrnout kvůli následujícím problémům poskytovatele dat: <br>
- Usazovací nádrž - 2024-01-01: 1.07 USAZOVACÍ NÁDRŽ - objekt zrušen z kategorie 1. SÍDELNÍ, HOSPODÁŘSKÉ A KULTURNÍ OBJEKTY <br>
- Dobývací prostor - (*) Typ objektu bude publikován po smluvním zajištění dat od správce. <br>
- Chráněné ložiskové území -   (*) Typ objektu bude publikován po smluvním zajištění dat od správce. <br> <br>

**Zdroje dat pro jednotlivé atributy SoilVeg:** <br>
https://docs.google.com/spreadsheets/d/e/2PACX-1vTbRsC8YWkru4Eo5AAMdMwHh9P26WF7v6L3tRfg7hfBfB_dThkh3UN75LjTpiH177f-kNv2c5BtGxxq/pubhtml
