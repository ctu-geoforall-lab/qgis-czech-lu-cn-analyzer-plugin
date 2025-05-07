# Ovládání
!!! warning "Pozor"
    Před spuštěním stahování dat je nutné nastavit projektu __EPSG:5514__  <br>
	[Jak?](https://www.youtube.com/watch?v=OmPH1es1w1k)

## Záložka Stahování dat (Download)

- Nejprve je nutné vybrat zájmové území pro stažení dat
	- Pro stažení dat ve výřezu obrazovky vyberte možnost _Compute inside window extent_
	- Pro stažení dat uvnitř polygonu vyberte možnost _Compute inside polygon_
		- Tato akce umožní vybrat polygn z projektu v rozbalovacím okně níže

- Dále je možné vybrat jaká data stáhnout
	- Pro stažení dat využití území i dat hydrologických skupin půd vyberte _Land Use and Soil Groups_
	- Pro stažení pouze dat využití území vyberte _only Land Use_
	- Pro stažení pouze dat hydrologických skupin půd vyberte _only Hydrology Soil Groups_

- Pro zahájení stahování klikněte na tlačítko _Download_
- Pro zastavení procesu stahování klikněte na tlačítko _Abort_

<p align="center">
    <img src="../../img/ovl1.png" alt="ovl1" style="height: 60vh;">
</p>

## Záložka Propojení vrstev (Intersection)
 - V rozbalovacím okně _Select Land Use layer_ vyberte vrstvu využití území
	- Po jejím úspěšném stažení v předchozí záložce se do rozbalovacího okna nastaví sama
	- Pokud chcete použít vrstvu vlastní, musí tato vrstva obsahovat atribut s názvem _LandUse_code_ s celými čísly

- V rozbalovacím okně _Select Hydrology Soil Group layer_ vyberte vrstvu hydrologických skupin půd
	- Po jejím úspěšném stažení v předchozí záložce se do rozbalovacího okna nastaví sama
	- Pokud chcete použít vrstvu vlastní, musí tato vrstva obsahovat atribut s názvem _HSG_ s celými čísly, kde 
		- číslo 1 zastupuje skupinu A
		- číslo 2 zastupuje skupinu B
		- číslo 3 zastupuje skupinu C
		- číslo 4 zastupuje skupinu D
		- číslo 0 zastupuje skupinu vodní plochy
		
- Zahajte propojení vrstev tlačítkem _Intersect_

<p align="center">
    <img src="../../img/ovl2.png" alt="ovl2" style="height: 60vh;">
</p>

## Záložka Tvorby CN vrstvy (CN)
- V rozbalovacím okně _Select Land Use and HSF Intersected layer_ vyberte vrstvu využití území propojenou s vrstvou hydrologických skupin půd.
	- Po jejím úspěšném propojení v předchozí záložce se do rozbalovacího okna nastaví sama
	- Pokud chcete použít vrstvu vlastní, musí tato vrstva obsahovat atribut s názvem _LandUse_code_ s celými čísly a atribut s názvem _HSG_ s celými čísly.

- Řádek níže obsahuje cestu k CSV tabulce konverze CN hodnot
- Pro výběr úmístění vlastní CSV tabulky klikněte na ikonu tří teček vedle  tohoto řádku
- Pro vytvoření CN vrstvy klikněte na tlačítko _Create CN layer_

<p align="center">
    <img src="../../img/ovl3.png" alt="ovl3" style="height: 60vh;">
</p>

## Záložka Výpočtu objemu přímého odtoku (Run-off)
 - V rozbalovacím okně _Select CN layer_ vyberte vrstvu CN
	- Po jejím úspěšném získání v předchozí záložce se do rozbalovacího okna nastaví sama
	- Pokud chcete použít vrstvuu vlastní, musí tato vrstva obsahovat atribut s názvem _CN2_ s desítkovými čísly
		- může a nemusí obsahovat atribut s názvem _CN3_ s desítkovými čísly

- Níže v poli _Inital Abstraction Coefficient_ můžete vložit vlastní hodnotu poměrového koeficientu počáteční ztráty.
	- Ten je možný volit v rozmezí 0.1 - 0.3

- Pokud si přejete vypočíst objemy přímých odtoků z návrhových výšek úhrnů ze služby [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz) pro různé doby opakování vyberte možnost _Use rainfall depth from rain.fsv.cvut.cz_
	- Následně si vyberte požadované doby opakování zasškrtávacími tlačítky výše _Select Recurrence Intervals_

- Pokud si přejete vypočíst objemy přímých odtoků z vlastních návrhových výšek úhrnů zaškrtněte možnost _Define your own rainfall depth  [mm]_
	-  Následně vepište takovou hodnot v milimetrech do pole níže 
		- Pokud si přejete provést výpočet pro více návrhových výšek úhrnů najdenou, odělte je v tomto poli středníkem _;_

- Proces spustíte tlačítkem _Compute run-off_

<p align="center">
    <img src="../../img/ovl4.png" alt="ovl4" style="height: 60vh;">
</p>