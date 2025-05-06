# Czech Land Use and CN Analyzer
![plugin icon](https://github.com/ctu-geoforall-lab/qgis-zabaged-plugin/blob/main/docs/images/baner.png?raw=true) <br>

[![Tests](https://github.com/ctu-geoforall-lab/qgis-zabaged-plugin/actions/workflows/main.yml/badge.svg)](https://github.com/ctu-geoforall-lab/qgis-zabaged-plugin/actions/workflows/main.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0) <br>

_Qgis plugin umožňuje automatizovaně generovat vrstvu využití území a vrstvu hydrologických skupin půd. Z této kombinace vrstev přiřazuje hodnotu CN a  dále je možné získat hodnotu objemu přímého odtoku ze srážkových úhrnů poskytovaných z [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz) či definovaných uživatelem._
<br><br>
📖 [**Dokumentace**](https://ctu-geoforall-lab.github.io/qgis-czech-lu-cn-analyzer-plugin/)
<br><br>
Pro správnou funkci je potřeba mít v projektu nastaven CRS na EPSG:5514 <br>
Testováno na MS Windows a Linux(Ubuntu). <br> <br>

## Funkce pluginu
- Plugin stahuje požadované ZABAGED vrstvy uvnitř výřezu okna či polygonu, pomocí WFS služby. 
- Stahování probíhá na pozadí v jiném vlákně Qgisu
- Uživatel je informován o procesu stahování a je schopen ho tlačítkem ukončit
- Přířazení LandUse kódu dle názvu ZABAGED vrsty
- Zpřesnění LandUse kódu dle řídícího atributu prvku
- Aplikování bufferu dle řídícího atributu prvku
- Polygonové vrstvy ZABAGED/LPIS jsou spojovány do jedné dle dané priority vrstev
- Vstupní parametry jsou čteny z konfiguračních souborů.
- Je umožněno stáhnout a polygonizovat HSG vrstvu.
- Vrsvty LandUse a HSG je monžné propojit do jedné.
- Spojené vrstvy je možné propojit s tabulkou CN hodnot a získat CN vrstvu (CN2,CN3).
- Je možno určit objem přímého odtoku z úhrnu definovaného uživatelem
- Uživateli je umožněno zadat více úhrnů a znich získat více výsledků
- Připojení WPS služby z rain.fsv.cvut.cz pro získání návrhových srážek pro různé doby opakování
- Výpočet sumy objemů vážených podle podílu zastoupení jednotlivých hyetogramů v dané lokalitě a pravděpodobnosti abnormálního nasycení

  
## Popis konfiguračních souborů
Tyto soubory se nachází ve složce *config* <br>
Slouží k uchování paramterů webových služeb (a k jejich editaci pro případ změn na straně poskytovatele) <br>
a pro případnou změnu některých výpočetních postupů <br> <br>

- **layers_merging_order.csv** - uchovává názvy stahovaných ZABAGED vrstev, které jsou dány poskytovatelem. Nachází se zde pouze vrstvy relevantní pro výpočet. Jsou uchovávány v pořadí dle priority sloučení do LandUse vrstvy. Priorita LPIS vrstvy je zde uvedena pod klíčovým slovem _LPIS_layer_.
- **LPIS.yaml** - obsahuje URL adresu, kde se nachází WFS služba poskytující LPIS data. Také název stahované LPIS vrstvy a  řídící atribut pro změnu hodnoty LandUse kódu, typy atributů, základní hodnotu LandUse kódu a definované přírůstky.
- **ZABAGED.yaml** -  obsahuje URL adresu, kde se nachází WFS služba poskytující ZABAGED data. Také  názvy vrstev, které je potřeba bufferovat (liniové a bodové). Ty se bufferují dle nějakého atributu a jeho hodnoty v ZABAGED vrstvě. Pro jednotlivé hodnoty tohoto atributu jsou zvoleny vzdálenosti bufferů. (Šířka vozovky je dvojnásobek hodnoty *distance*)
- **zabaged_to_LandUseCode_table.csv** - uchovává sadu čtyř klíčových slov, která pokud jsou obsažena v názvu ZABAGED vrstvy, tak jí je přiřazena Hodnota LandUse kódu z páté pozice řádku.
- **Soil.yaml** - Obsahuje URL adresu a identifikátor WPS služby poskytující hydrologické skupiny půd
- **Soil_template.xml** - Vzor XML dotatzu  WPS služby poskytující hydrologické skupiny půd
- **CN_table.csv** - Slouží jako referenční tabulka kódů využití území (LANDUSE_CODE) a jejich odpovídajících hodnot čísla odtokové křivky (CN) pro různé hydrologické skupiny půd (A, B, C, D)
- **WPS_config.yaml** - Obsahuje URL adresu a identifikátor WPS služby poskytující šest variant průběhu pětiminutových intenzit 6hodinových návrhových srážek a návrhové srážkové úhrnů pro určité doby opakování
  
## Další informace
- na další bodové a linové prvky je potřeba zvolit buffer
- Je nuntné doplnit další LandUse kódy pro více ZABAGED vrstev

<br><br>

Některé požadované ZABAGED vrstvy není možné zahrnout kvůli následujícím problémům poskytovatele dat: <br>
- Usazovací nádrž - 2024-01-01: 1.07 USAZOVACÍ NÁDRŽ - objekt zrušen z kategorie 1. SÍDELNÍ, HOSPODÁŘSKÉ A KULTURNÍ OBJEKTY <br>
- Dobývací prostor - (*) Typ objektu bude publikován po smluvním zajištění dat od správce. <br>
- Chráněné ložiskové území -   (*) Typ objektu bude publikován po smluvním zajištění dat od správce. <br> <br>

