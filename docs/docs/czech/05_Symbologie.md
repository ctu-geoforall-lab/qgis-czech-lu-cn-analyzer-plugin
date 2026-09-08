# Symbologie
!!! note "Poznámka"
	Styly zobrazení jednotlivých výstupních vrstev se nachází ve složce _colortables_
## Vrstva půdního pokryvu / využití území (LandUse Layer)
- soubor: __landuse.qml__
- řídicí atribut: __LandUse_code__

### Tabulka momentálně podporovaných hodnot

| Barva | Hex kód | Vzor | Hodnota řídicího atributu | Název |
|--------|--------|:---:|:---:|--------|
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` |  | 10000 | orná půda (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFFF;"></span> | `#FFFFFF` | X | 11100 | úhor černý |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFFF;"></span> | `#FFFFFF` | / | 11111 | úhor; posklizňové zbytky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFFF;"></span> | `#FFFFFF` | / | 11112 | úhor; posklizňové zbytky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` | / | 12111 | širokořádkové plodiny, přímé řádky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` | / | 12112 | širokořádkové plodiny, přímé řádky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` | / | 12121 | širokořádkové plodiny, přímé řádky, posklizňové zbytky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` |  | 12122 | širokořádkové plodiny, přímé řádky, posklizňové zbytky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` | / | 12131 | širokořádkové plodiny, vrstevnicové řádky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` |  | 12132 | širokořádkové plodiny, vrstevnicové řádky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` | / | 12141 | širokořádkové plodiny, vrstevnicové řádky, posklizňové zbytky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` |  | 12142 | širokořádkové plodiny, vrstevnicové řádky, posklizňové zbytky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` |  | 12151 | širokořádkové plodiny, vrstevnicové řádky, terasové uspořádání (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` |  | 12152 | širokořádkové plodiny, vrstevnicové řádky, terasové uspořádání (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` |  | 12161 | širokořádkové plodiny, terasové uspořádání, vrstevnicové řádky, posklizňové zbytky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` |  | 12162 | širokořádkové plodiny, terasové uspořádání, vrstevnicové řádky, posklizňové zbytky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` | / | 12211 | úzkořádkové plodiny, přímé řádky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` | / | 12212 | úzkořádkové plodiny, přímé řádky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` | / | 12221 | úzkořádkové plodiny, přímé řádky, posklizňové zbytky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` |  | 12222 | úzkořádkové plodiny, přímé řádky, posklizňové zbytky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` | / | 12231 | úzkořádkové plodiny, vrstevnicové řádky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` |  | 12232 | úzkořádkové plodiny, vrstevnicové řádky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` |  | 12241 | úzkořádkové plodiny, vrstevnicové řádky, posklizňové zbytky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` |  | 12242 | úzkořádkové plodiny, vrstevnicové řádky, posklizňové zbytky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` |  | 12251 | úzkořádkové plodiny, vrstevnicové řádky, terasové uspořádání (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` |  | 12252 | úzkořádkové plodiny, vrstevnicové řádky, terasové uspořádání (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` |  | 12261 | úzkořádkové plodiny, vrstevnicové řádky, terasové uspořádání, posklizňové zbytky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFD37F;"></span> | `#FFD37F` |  | 12262 | úzkořádkové plodiny, vrstevnicové řádky, terasové uspořádání, posklizňové zbytky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFEBBE;"></span> | `#FFEBBE` | / | 13111 | víceleté pícniny, přímé řádky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFEBBE;"></span> | `#FFEBBE` |  | 13112 | víceleté pícniny, přímé řádky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFEBBE;"></span> | `#FFEBBE` | / | 13121 | víceleté pícniny, vrstevnicové řádky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFEBBE;"></span> | `#FFEBBE` |  | 13122 | víceleté pícniny, vrstevnicové řádky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFEBBE;"></span> | `#FFEBBE` |  | 13131 | víceleté pícniny, vrstevnicové řádky, posklizňové zbytky (špatné hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFEBBE;"></span> | `#FFEBBE` |  | 13132 | víceleté pícniny, vrstevnicové řádky, posklizňové zbytky (dobré hydrologické podmínky) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFBE;"></span> | `#FFFFBE` |  | 20000 | souvislý travní porost (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#CDF57A;"></span> | `#CDF57A` |  | 21100 | přirozené louky, bez seče a pastvy |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E9FFBE;"></span> | `#E9FFBE` |  | 21200 | extenzivní louky, chráněné před pastvou, nejvýše 1x ročně sečené |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E9FFBE;"></span> | `#E9FFBE` | / | 21300 | extenzivní pastviny, pokryv > 75 %, s lehkou nebo příležitostnou pastvou |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFBE;"></span> | `#FFFFBE` |  | 22000 | souvislý travní porost; intenzivní (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFBE;"></span> | `#FFFFBE` | / | 22100 | intenzivní pastviny, pokryv 50 - 75 % bez intenzivní pastvy |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFBE;"></span> | `#FFFFBE` | X | 22200 | intenzivní pastviny, pokryv < 50 % nebo intenzivní pastva bez ochrany mulčem |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFBE;"></span> | `#FFFFBE` |  | 22300 | trvalý travní porost; intenzivní; pravidelně sečený |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFBE;"></span> | `#FFFFBE` | / | 22400 | zatravněná orná půda |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFF00;"></span> | `#FFFF00` |  | 23100 | travní porost se specifickým využitím; s nízkým zatížením (letiště mimo runway, golf, areály FVE aj.) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFF00;"></span> | `#FFFF00` | / | 23200 | travní porost se specifickým využitím; se zvýšeným zatížením (parkur a jiná sportoviště) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#4C7300;"></span> | `#4C7300` |  | 30000 | souvislé porosty dřevin (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#4C7300;"></span> | `#4C7300` |  | 31000 | les se stromy (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#4C7300;"></span> | `#4C7300` |  | 31100 | les se stromy; listnatý (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#70A800;"></span> | `#70A800` |  | 31110 | les se stromy; listnatý, výška do 2.5 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#70A800;"></span> | `#70A800` |  | 31120 | les se stromy; listnatý, výška od 2.5 m do 8 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#4C7300;"></span> | `#4C7300` |  | 31130 | les se stromy; listnatý, výška od 8 m do 22 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#4C7300;"></span> | `#4C7300` |  | 31140 | les se stromy; listnatý, výška nad 22 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#4C7300;"></span> | `#4C7300` |  | 31200 | les se stromy; smíšený (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ABCD66;"></span> | `#ABCD66` |  | 31210 | les se stromy; smíšený, výška do 2.5 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#70A800;"></span> | `#70A800` |  | 31220 | les se stromy; smíšený, výška od 2.5 m do 8 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#70A800;"></span> | `#70A800` |  | 31230 | les se stromy; smíšený, výška od 8 m do 22 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#4C7300;"></span> | `#4C7300` |  | 31240 | les se stromy; smíšený, výška nad 22 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#70A800;"></span> | `#70A800` |  | 31300 | les se stromy; jehličnatý (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ABCD66;"></span> | `#ABCD66` |  | 31310 | les se stromy; jehličnatý, výška do 2.5 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ABCD66;"></span> | `#ABCD66` |  | 31320 | les se stromy; jehličnatý, výška od 2.5 m do 8 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#70A800;"></span> | `#70A800` |  | 31330 | les se stromy; jehličnatý, výška od 8 m do 22 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#70A800;"></span> | `#70A800` |  | 31340 | les se stromy; jehličnatý, výška nad 22 m |
| <span style="display:inline-block; width:20px; height:20px; background-color:#ABCD66;"></span> | `#ABCD66` | / | 31400 | zalesněná orná půda |
| <span style="display:inline-block; width:20px; height:20px; background-color:#A8A800;"></span> | `#A8A800` |  | 32100 | nízké dřeviny; křoviny |
| <span style="display:inline-block; width:20px; height:20px; background-color:#A8A800;"></span> | `#A8A800` | / | 32200 | nízké dřeviny; kosodřevina |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00734C;"></span> | `#00734C` |  | 33000 | lesní školka (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00734C;"></span> | `#00734C` | / | 33100 | lesní školka; na orné půdě |
| <span style="display:inline-block; width:20px; height:20px; background-color:#894465;"></span> | `#894465` |  | 34000 | rychle rostoucí dřeviny; bez dalšího určení |
| <span style="display:inline-block; width:20px; height:20px; background-color:#894465;"></span> | `#894465` | / | 34100 | rychle rostoucí dřeviny; na orné půdě |
| <span style="display:inline-block; width:20px; height:20px; background-color:#828282;"></span> | `#828282` |  | 40000 | antropogenní plochy (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#343434;"></span> | `#343434` |  | 41000 | budovy a zastřešené objekty; nepropustné, bez známé retence |
| <span style="display:inline-block; width:20px; height:20px; background-color:#B2B2B2;"></span> | `#B2B2B2` |  | 42000 | dopravní plochy (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#828282;"></span> | `#828282` |  | 42100 | dopravní plochy; nepropustné (asfalt, beton) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#B2B2B2;"></span> | `#B2B2B2` |  | 42200 | dopravní plochy; zhutněné, polopropustné (panely, dlažba) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E1E1E1;"></span> | `#E1E1E1` |  | 42300 | dopravní plochy; zhutněné, propustné (štěrk, drť) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#C8B48C;"></span> | `#C8B48C` |  | 42400 | dopravní plochy; přírodní, propustné (zhutněná zemina) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#AAFF00;"></span> | `#AAFF00` |  | 43000 | udržovaná sídelní zeleň (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E9FF00;"></span> | `#E9FF00` |  | 43100 | udržovaná sídelní zeleň; roztroušená nebo s převahou travních ploch, nízký podíl zpevněných ploch |
| <span style="display:inline-block; width:20px; height:20px; background-color:#AAFF00;"></span> | `#AAFF00` |  | 43200 | udržovaná sídelní zeleň; souvislá nebo s převahou dřevin, nízký podíl zpevněných ploch |
| <span style="display:inline-block; width:20px; height:20px; background-color:#AAFF00;"></span> | `#AAFF00` | / | 43300 | udržovaná sídelní zeleň; roztroušená s vyšším podílem zpevněných ploch |
| <span style="display:inline-block; width:20px; height:20px; background-color:#A80000;"></span> | `#A80000` |  | 44000 | těžební plochy (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#A80000;"></span> | `#A80000` | X | 44100 | těžební plochy; skalní těžba |
| <span style="display:inline-block; width:20px; height:20px; background-color:#A80000;"></span> | `#A80000` | / | 44200 | těžební plochy; s mělkou HPV (štěrkopísky, rašelina) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#A80000;"></span> | `#A80000` |  | 44300 | těžební plochy; ostatní nesoudržné materiály |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FF0000;"></span> | `#FF0000` |  | 45000 | úložné plochy (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FF0000;"></span> | `#FF0000` | X | 45100 | úložné plochy; haldy a odvaly |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FF0000;"></span> | `#FF0000` | / | 45200 | úložné plochy; skládky materiálu |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FF0000;"></span> | `#FF0000` |  | 45210 | úložné plochy; skládky odpadu |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFBEE8;"></span> | `#FFBEE8` |  | 46000 | ostatní sídelní plochy (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFDDE8;"></span> | `#FFDDE8` |  | 46100 | ostatní sídelní plochy; převaha propustných ploch |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFBEE8;"></span> | `#FFBEE8` |  | 46200 | ostatní sídelní plochy; smíšené povrchy |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FF95E8;"></span> | `#FF95E8` |  | 46300 | ostatní sídelní plochy; převaha zpevněných ploch |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFFF;"></span> | `#FFFFFF` | ▼ | 51000 | vinice (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFFF;"></span> | `#FFFFFF` | ▼ | 51001 | vinice; dle evidence LPIS |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFEBAF;"></span> | `#FFEBAF` | ▼ | 52000 | chmelnice (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFEBAF;"></span> | `#FFEBAF` | ▼ | 52001 | chmelnice; dle evidence LPIS |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFFF;"></span> | `#FFFFFF` | ○ | 53000 | ovocný sad (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFFF;"></span> | `#FFFFFF` | ○ | 53001 | ovocný sad; dle evidence LPIS |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E6E600;"></span> | `#E6E600` |  | 60000 | extenzivní smíšené porosty (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E6E600;"></span> | `#E6E600` |  | 61100 | extenzivní porosty; rozptýlené dřeviny s travním podrostem; s převahou křovin |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E6E600;"></span> | `#E6E600` |  | 61200 | extenzivní porosty; rozptýlené dřeviny s travním podrostem; s převahou vyšších dřevin |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E6E600;"></span> | `#E6E600` | / | 62100 | extenzivní porosty; mozaika souvislých porostů dřevin a travního porostu; s převahou křovin |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E6E600;"></span> | `#E6E600` | / | 62200 | extenzivní porosty; mozaika souvislých porostů dřevin a travního porostu; s převahou vyšších dřevin |
| <span style="display:inline-block; width:20px; height:20px; background-color:#E6E600;"></span> | `#E6E600` | X | 63000 | extenzivní porosty; stromo-křovinné a sukcesní porosty |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0084A8;"></span> | `#0084A8` |  | 71000 | vodní toky |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00C5FF;"></span> | `#00C5FF` |  | 72000 | vodní plochy (bez dalšího určení) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00C5FF;"></span> | `#00C5FF` |  | 72100 | vodní plochy; zemní nádrže hospodářské nebo rekreační |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00C5FF;"></span> | `#00C5FF` |  | 72200 | vodní plochy; s významnou retencí (přehradní nádrže) |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00C5FF;"></span> | `#00C5FF` |  | 72300 | vodní plochy; nádrže s řízeným vypouštěním |
| <span style="display:inline-block; width:20px; height:20px; background-color:#AFC5FF;"></span> | `#AFC5FF` |  | 72400 | vodní plochy; odkaliště a další izolované prvky |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0096F0;"></span> | `#0096F0` |  | 72500 | vodní plochy; přírodní a přírodě blízké |
| <span style="display:inline-block; width:20px; height:20px; background-color:#0084A8;"></span> | `#0084A8` | / | 73000 | bažina, močál |
| <span style="display:inline-block; width:20px; height:20px; background-color:#71704A;"></span> | `#71704A` | / | 74000 | rašeliniště |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFFF;"></span> | `#FFFFFF` | X | 82100 | skalní útvary |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFFFFF;"></span> | `#FFFFFF` | • | 82200 | sutě, kamenná pole |
| <span style="display:inline-block; width:20px; height:20px; background-color:transparent; color:#FF0000; text-align:center; line-height:20px; font-size:18px;">○</span> | `#FF0000` (bodový vzor; bez výplně) | ○ | NULL | NO LAND USE DATA |
| <span style="display:inline-block; width:20px; height:20px; background-color:transparent; color:#FF0000; text-align:center; line-height:20px; font-size:18px;">×</span> | `#FF0000` (bodový vzor; bez výplně) | × | ELSE | OTHER LandUse class |


## Vrstva hydrologických skupin půd (Soil Layer HSG)
- soubor: __soil.qml__
- řídicí atribut: __HSG__

| Barva                                                      | Hex kód   | Hodnota řídicího atributu | Název |
|------------------------------------------------------------|-----------|:------:|:------:|
| <span style="display:inline-block; width:20px; height:20px; background-color:#38A800;"></span> | `#38A800` |   0   |   Plochy bez půdních dat   |
| <span style="display:inline-block; width:20px; height:20px; background-color:#B0E000;"></span> | `#B0E000` |   1   |   A    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FFAA00;"></span> | `#FFAA00` |   2   |   B    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#FF0000;"></span> | `#FF0000` |   3   |   C    |
| <span style="display:inline-block; width:20px; height:20px; background-color:#00FFFF;"></span> | `#00FFFF` |   4   |   D    |


## Propojené vrstvy (Intersected LandUse and HSG)
- soubor: __intersection.qml__
- řídící atributy: __LandUse_code__ , __HSG__

!!! note "Poznámka"
    Symbologie se pro většinu tříd přebírá z vrstvy _LandUse Layer_.
    Navíc je přidán symbol _NO HSG DATA_, jeho styl je stejný jako v případě _NO LandUse data", liší se jen barvou symbolu.

    
## Vrstva CN hodnot (CN Layer)
- soubor: __CN_color_ramp.xml__
- řídicí atribut: __CN2__

Symbologie s barevným přechodem založeným na kvantilech pro číselné prvky a červenou barvou pro prvky s nenumerickými (nebo NULL) hodnotami. Funguje tak, že vypočítá kvantilové hranice pro číselné hodnoty a rozdělí je do patnácti tříd.

<p align="center">
    <img src="../../img/CNramp.png" alt="CNramp" style="height: 5vh;">
</p>
 - chybějící a nevalidní hodnoty - <span style="display:inline-block; width:20px; height:20px; background-color:#ff0000;"></span>


## Vrstva výšek přímého odtoku (RunOff Layer)
- soubor: __RUNOFF_color_ramp.xml__
- řídicí atributy: 

    - Při výpočtu z jedné výšky úhrnů zadané uživatelem - __CN2_runoff_height_mm__   
    - Při výpočtu z více výšek úhrnů zadaných uživatelem - __CN2_1_runoff_height_mm__
    - Při výpočtu z dob opakování na [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz) - __CN2_N100_runoff_height_mm__ (Nebo pro nejvyšší použitou dobu opakování)


    Symbologie s barevným přechodem založeným na kvantilech pro číselné prvky a červenou barvu pro prvky s nenumerickými (nebo NULL) hodnotami. Funguje tak, že vypočítá kvantilové hranice pro číselné hodnoty a rozdělí je do patnácti tříd.
    
<p align="center">
    <img src="../../img/RNramp.png" alt="RNramp" style="height: 5vh;">
</p>
 - chybějící a nevalidní hodnoty - <span style="display:inline-block; width:20px; height:20px; background-color:#ff0000;"></span>
