# Symbologie
!!! note "Poznámka"
	Tabulky barev se nachází ve složce _colortables_
## Vrstva využití území (LandUse layer)
- soubor: __landuse.sld__
- řídící atribut: __LandUse_layer__

!!! note "Poznámka"
    V souboru jsou připraveny hodnoty i pro kódy využití území, které zásuvný modul negeneruje, ale jsou vytvořeny pro případ jeho rozšíření.
    První tabulka ukazuje hodnoty momentálně podporované a ta druhá všechny její obsahující hodnoty
### Tabulka momentálně podporovaných hodnot
| Barva                                                                                                          | Hex kód   | Hodnota řídícího atributu | Název                                                                                       |
|-----------------------------------------------------------------------------------------------------------------|-----------|:-------------------------:|:-------------------------------------------------------------------------------------------|
| <span style="display:inline-block; width:20px; height:20px; background-color:#ffc803;"></span>                 | `#ffc803` |           10000          | Orná půda                                                                                  |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0dff00;"></span>                 | `#0dff00` |           20000          | Travní porost                                                                              |
| <span style="display:inline-block; width:20px; height:20px; background-color:#40f736;"></span>                 | `#40f736` |           22200          | Extenzivní pastviny a louky – dobré hydrologické podmínky                                  |
| <span style="display:inline-block; width:20px; height:20px; background-color:#1d5220;"></span>                 | `#1d5220` |           30000          | Lesní porost                                                                               |
| <span style="display:inline-block; width:20px; height:20px; background-color:#03850d;"></span>                 | `#03850d` |           33100          | Lesní porost listnatý – střední hydrologické podmínky                                      |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00633f;"></span>                 | `#00633f` |           33200          | Lesní porost jehličnatý – špatné hydrologické podmínky                                     |
| <span style="display:inline-block; width:20px; height:20px; background-color:#08702c;"></span>                 | `#08702c` |           33300          | Lesní porost smíšený – dobré hydrologické podmínky                                         |
| <span style="display:inline-block; width:20px; height:20px; background-color:#47633a;"></span>                 | `#47633a` |           33500          | Lesní porost – křoviny                                                                     |
| <span style="display:inline-block; width:20px; height:20px; background-color:#8ac286;"></span>                 | `#8ac286` |           42000          | Zahrada                                                                                    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#626361;"></span>                 | `#626361` |           44100          | Nepropustné povrchy                                                                        |
| <span style="display:inline-block; width:20px; height:20px; background-color:#8a877f;"></span>                 | `#8a877f` |           44200          | Antropogenní polopropustné plochy                                                          |
| <span style="display:inline-block; width:20px; height:20px; background-color:#877f65;"></span>                 | `#877f65` |           44300          | Antropogenní propustné plochy                                                              |
| <span style="display:inline-block; width:20px; height:20px; background-color:#cf9357;"></span>                 | `#cf9357` |           55100          | Sady, vinice, chmelnice s desíkovaným mezíradím                                           |
| <span style="display:inline-block; width:20px; height:20px; background-color:#2c523b;"></span>                 | `#2c523b` |           66100          | Plochy s nedokonalým pokrytím – extenzivní sady, doprovodná vegetace komunikací a vodních toků |
| <span style="display:inline-block; width:20px; height:20px; background-color:#009c5f;"></span>                 | `#009c5f` |           66600          | Rašeliniště                                                                                |
| <span style="display:inline-block; width:20px; height:20px; background-color:#009c5f;"></span>                 | `#009c5f` |           66600          | Rašeliniště                                                                                |
| <span style="display:inline-block; width:20px; height:20px; background-color:#383efc;"></span>                 | `#383efc` |           77100          | Vodní tok                                                                                  |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0008ff;"></span>                 | `#0008ff` |           77200          | Vodní plocha – plocha                                                                      |
| <span style="display:inline-block; width:20px; height:20px; background-color:#999999;"></span>                 | `#999999` |           88200          | Skaly                                                                                      |


### Kompletní tabulka všech hodnot
 | Barva                                                     | Hex kód  | Hodnota řídícího atributu | Název |
|------------------------------------------------------------|-----------|:------:|:------:|
| <span style="display:inline-block; width:20px; height:20px; background-color:#ffc803;"></span> | `#ffc803` |   10000    |   OrnaPuda    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#f2dc8d;"></span> | `#f2dc8d` |   11100    |   neoseto-DobreHydrologickePodminky-PoskliznoveZbytky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#dbac02;"></span> | `#dbac02` |   11200    |   LetniUzkoradkovePlodiny    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#fad75a;"></span> | `#fad75a` |   11300    |   OziméUzkoradkovePlodiny    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#e0bd3d;"></span> | `#e0bd3d` |   11400    |   SirokoradkovePlodiny    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#d6b12b;"></span> | `#d6b12b` |   11500    |   ViceletePicniny-TravniPorostNaOrnePude    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#cfbf86;"></span> | `#cfbf86` |   11600    |   MimoprodukcniPlochaANavrhnutaTechnickaOpatreniNaOP    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ba9306;"></span> | `#ba9306` |   11700    |   SirokoradkovePlodiny-SpatneHydrologickePodminky-PrimeRadky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#b8961d;"></span> | `#b8961d` |   11800    |   SirokoradkovePlodiny-DobreHydrologickePodminky-VrstevnicoveRadky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#b3962e;"></span> | `#b3962e` |   11900    |   ViceletePicniny-VrstevnicoveRadky-DobreHydrologickePodminky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#8a6c01;"></span> | `#8a6c01` |   12200    |   UhorCerny    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#d3de04;"></span> | `#d3de04` |   12100    |   SkolkaNaOrnePude    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#f7df07;"></span> | `#f7df07` |   19900    |   OrnaPuda-CORINE    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#e3d97b;"></span> | `#e3d97b` |   11101    |   Neoseto-UhorUdrzovany    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#bfb660;"></span> | `#bfb660` |   11102    |   Neoseto-UhorNeudrzovany    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#5c540f;"></span> | `#5c540f` |   11116    |   Neoseto-SitoveLoze    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#e0a904;"></span> | `#e0a904` |   11203    |   JecmenJarni    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#faaf00;"></span> | `#faaf00` |   11205    |   PseniceJarni    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#dbfc9d;"></span> | `#dbfc9d` |   11210    |   Pohanka    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#99a877;"></span> | `#99a877` |   11220    |   Proso    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#cca435;"></span> | `#cca435` |   11225    |   OvesJarni    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ffee00;"></span> | `#ffee00` |   11208    |   HrachPolniJarni    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#b3a702;"></span> | `#b3a702` |   11229    |   HrachRolniJarni    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#a3de4b;"></span> | `#a3de4b` |   11218    |   BobObecny    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#c990f5;"></span> | `#c990f5` |   11221    |   Lupina    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#9fab74;"></span> | `#9fab74` |   11222    |   HrachRolni    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ffa200;"></span> | `#ffa200` |   11230    |   Mrkev    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#f7ce52;"></span> | `#f7ce52` |   11304    |   JecmenOzimy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#f7cc65;"></span> | `#f7cc65` |   11406    |   PseniceOzima    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ba926c;"></span> | `#ba926c` |   11524    |   zitoOzime    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#c7a854;"></span> | `#c7a854` |   11626    |   OvesOzimy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#bda402;"></span> | `#bda402` |   11711    |   RepkaOzima    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#faf1b4;"></span> | `#faf1b4` |   11809    |   HorciceBila    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#b3a702;"></span> | `#b3a702` |   11914    |   HrachPolniOzimy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#9c9533;"></span> | `#9c9533` |   12028    |   HrachRolniOzimy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#cfa9e8;"></span> | `#cfa9e8` |   12115    |   Svazenka    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#b892fc;"></span> | `#b892fc` |   12219    |   LenSety    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#94703e;"></span> | `#94703e` |   11417    |   Brambory    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ffcc00;"></span> | `#ffcc00` |   11407    |   Slunecnice    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#cca41f;"></span> | `#cca41f` |   11412    |   Kukurice    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#f7ce97;"></span> | `#f7ce97` |   11427    |   Cirok    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ff0066;"></span> | `#ff0066` |   11431    |   Repa    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#fa4b88;"></span> | `#fa4b88` |   11513    |   Vojtezka    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#f067eb;"></span> | `#f067eb` |   11532    |   Jetel    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#c6db3d;"></span> | `#c6db3d` |   11523    |   JilekVytrvaly    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0dff00;"></span> | `#0dff00` |   20000    |   TravniPorost    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#2fa828;"></span> | `#2fa828` |   22100    |   IntenzivniPastviny-SpatneHydrologickePodminky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#40f736;"></span> | `#40f736` |   22200    |   ExtenzivniPastvinyALouky-DobreHydrologickePodminky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#099e02;"></span> | `#099e02` |   23200    |   TravniKulturyNaMelkychPudach-HorskeLouky-Vrchoviste-Vresoviste-NasycenePudy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00ff80;"></span> | `#00ff80` |   29900    |   TravniPorostCORINE    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#1d5220;"></span> | `#1d5220` |   30000    |   LesniPorost    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#03850d;"></span> | `#03850d` |   33100    |   LesniPorostListnaty-StredniHydrologickePodminky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00633f;"></span> | `#00633f` |   33200    |   LesniPorostJehlicnaty-SpatneHydrologickePodmink    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#08702c;"></span> | `#08702c` |   33300    |   LesniPorostSmiseny-DobreHydrologickePodminky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#3a633a;"></span> | `#3a633a` |   33400    |   LesniPorostNeurceny    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#47633a;"></span> | `#47633a` |   33500    |   LesniPorostKroviny    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#528556;"></span> | `#528556` |   34100    |   SkolkaARychlerostouciDreviny    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#01852f;"></span> | `#01852f` |   35100    |   LesniPorost-DobreHydrologickePodminky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#478501;"></span> | `#478501` |   35200    |   LesniPorost-SpatneHydrologickePodminky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#8b8c89;"></span> | `#8b8c89` |   40000    |   AntropogeniAZpevnenePlochy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#626361;"></span> | `#626361` |   44100    |   NeprospustnePovrchy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#8a877f;"></span> | `#8a877f` |   44200    |   AntropogenniPolopropustnePlochy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#877f65;"></span> | `#877f65` |   44300    |   AntropogenniPropustnePlochy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#fab36b;"></span> | `#fab36b` |   50000    |   SadyViniceChmelnice    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#cf9357;"></span> | `#cf9357` |   55100    |   SadyViniceChmelniceSDesikovanymMeziradim    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#c97f34;"></span> | `#c97f34` |   55200    |   SadyViniceChmelniceSObdelavanymMeziradim    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0f3b00;"></span> | `#0f3b00` |   60000    |   ExtenzivniSmisenePorosty    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#2c523b;"></span> | `#2c523b` |   66100    |   PlochySNedokonalymPokrytim-ExtenzivniSady-DoprovodnaVegetaceKomunikaciAVodnichToku    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#02f069;"></span> | `#02f069` |   66200    |   UpravenePlochySDobrymPokrytim-Zahrady-Parky-ZapojenySmisenyPorost    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0cb376;"></span> | `#0cb376` |   66300    |   TrvaleZamokrenePlochy-Mokrady-ZamokreneLouky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#47613e;"></span> | `#47613e` |   66400    |   RidkaVegetace    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0008ff;"></span> | `#0008ff` |   70000    |   VodniPlocha    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#383efc;"></span> | `#383efc` |   77100    |   VodniTok    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0008ff;"></span> | `#0008ff` |   77200    |   VodniPlochaPlocha    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#7acaf5;"></span> | `#7acaf5` |   77300    |   LedovceAStalySnih    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ffffff;"></span> | `#ffffff` |   80000    |   OstatniPlochy    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ffe278;"></span> | `#ffe278` |   88100    |   PlazeDunyPisky    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#999999;"></span> | `#999999` |   88200    |   Skaly    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#736147;"></span> | `#736147` |   88300    |   Spaleniste    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#8ac286;"></span> | `#8ac286` |   42000    |   Zahrada    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#7e9120;"></span> | `#7e9120` |   35000    |   LesniPudaSKorvinatymPorostem    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#009c5f;"></span> | `#009c5f` |   66600    |   Raseliniste    |



## Vrstva hydrologických skupin půd (Soil Layer HSG)
- soubor: __soil.sld__
- řídící atribut: __HSG__

 | Barva                                                     | Hex kód  | Hodnota řídícího atributu | Název |
|------------------------------------------------------------|-----------|:------:|:------:|
| <span style="display:inline-block; width:20px; height:20px; background-color:#00ffff;"></span> | `#00ffff` |   0   |   Vodní plocha   |
| <span style="display:inline-block; width:20px; height:20px; background-color:#09ff00;"></span> | `#09ff00`  |   1    |   A    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#9af571;"></span> | `#9af571` |   2    |   B   |
| <span style="display:inline-block; width:20px; height:20px; background-color:#e5ff00;"></span> | `#e5ff00` |   3    |   C    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ff0000;"></span> | `#ff0000` |   4   |   D    |


## Propojené vrstvy (Intersected LandUse and HSG)
- soubor: __intersection.qml__
- řídící atributy: __LandUse_code__ , __HSG__

!!! note "Poznámka"
    Symbologie vzniká kombinací dvou předchozích.
    Spodní barva polygonu vychází z barev vrstvy využití území.
    Šrafy nad touto plochou odpovídají barvám vrstvy hydrologických skupin půd
    


## Vrstva CN hodnot (CN Layer)
- soubor: __CN_color_ramp.xml__
- řídící atribut: __CN2__

Symbologie s barevným přechodem založeným na kvantilech pro číselné prvky a červenou barvu pro prvky s nenumerickými (nebo NULL) hodnotami. Funguje tak, že vypočítá kvantilové hranice pro číselné hodnoty a rozdělí je do patnácti tříd.

<p align="center">
    <img src="../../img/CNramp.png" alt="CNramp" style="height: 5vh;">
</p>
 - chybějící a nevalidní hodnoty - <span style="display:inline-block; width:20px; height:20px; background-color:#ff0000;"></span>
## Vrstva objemů přímých odtoků (RunOff Layer)
- soubor: __RUNOFF_color_ramp.xml__
- řídící atributy: 

    - Při výpočtu z jedné výšky úhrnů zadané uživatelem - __CN2_runoff_volume_m3__   
    - Při výpočtu z více výšek úhrnů zadaných uživatelem - __CN2_1_runoff_volume_m3__
    - Při výpočtu z dob opakování na [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz) - __CN2_N100_runoff_volume_m3__ (Nebo pro další nejvyšší dobu opakování)


    Symbologie s barevným přechodem založeným na kvantilech pro číselné prvky a červenou barvu pro prvky s nenumerickými (nebo NULL) hodnotami. Funguje tak, že vypočítá kvantilové hranice pro číselné hodnoty a rozdělí je do patnácti tříd.
    
<p align="center">
    <img src="../../img/RNramp.png" alt="RNramp" style="height: 5vh;">
</p>
 - chybějící a nevalidní hodnoty - <span style="display:inline-block; width:20px; height:20px; background-color:#ff0000;"></span>
