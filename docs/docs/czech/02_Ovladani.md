# Ovládání
!!! warning "Pozor"
    Před spuštěním stahování dat je nutné nastavit projektu __EPSG:5514__  <br>
	[Jak?](https://www.youtube.com/watch?v=OmPH1es1w1k)

## Záložka Stahování dat (Download)

- Nejprve je nutné vybrat zájmové území
	- Pro stažení dat pro aktuální rozsah mapového okna vyberte možnost _Current window extent_
	- Pro stažení dat pro území definované polygonovou vrstvou vyberte možnost _Polygon layer_
		- Tato akce umožní vybrat polygon z projektu v rozbalovací nabídce níže

- Dále je možné zvolit požadovaná data ke stažení
	- Pro stažení dat o půdním pokryvu (využití území) i hydrologických skupin půd vyberte _Land Use + Hydrologic Soil Groups_
	- Pro získání dat pouze o půdním pokryvu (využití území) vyberte _only Land Use_
	- Pro stažení pouze vrstvy hydrologických skupin půd vyberte _only Hydrologic Soil Groups_

- Pro zahájení stahování klikněte na tlačítko _Download_
- Pro zastavení procesu stahování klikněte na tlačítko _Abort_

<p align="center">
    <img src="../../img/ovl1.png" alt="ovl1" style="height: 60vh;">
</p>

## Záložka Propojení vrstev (Combine layers)
 - V rozbalovacím seznamu _Select Land Use layer_ vyberte vrstvu půdního pokryvu (využití území)
	- Po jejím úspěšném sestavení v předchozí záložce se do rozbalovacího okna nastaví jako výchozí volba
	- Pokud chcete použít vrstvu vlastní, musí tato vrstva obsahovat pole s názvem _LandUse_code_ s celočíselnými kódy

- V rozbalovacím seznamu _Select Hydrologic Soil Group layer_ vyberte vrstvu hydrologických skupin půd
	- Po jejím úspěšném stažení v předchozí záložce se do rozbalovacího okna nastaví jako výchozí volba
	- Pokud chcete použít vrstvu vlastní, musí tato vrstva obsahovat pole s názvem _HSG_ s celočíselnými kódy, kde:
		- hodnota 1 zastupuje skupinu A
		- hodnota 2 zastupuje skupinu B
		- hodnota 3 zastupuje skupinu C
		- hodnota 4 zastupuje skupinu D
		- hodnotou 0 je možné reprezentovat vodní plochy nebo plochy s nedefinovanou skupinou půd
		
- Zahajte propojení vrstev tlačítkem _Combine_

<p align="center">
    <img src="../../img/ovl2.png" alt="ovl2" style="height: 60vh;">
</p>

## Záložka Čísla odtokových křivek (CN)
- V rozbalovacím seznamu _Select layer combining Land Use and HSG_ vyberte vrstvu s propojením půdního pokryvu (využití území) a hydrologických skupin půd
	- Po jejím úspěšném propojení v předchozí záložce se do rozbalovacího okna nastaví jako výchozí volba
	- Pokud chcete použít vrstvu vlastní, musí obsahovat celočíselná pole s názvy _LandUse_code_ a _HSG_

- Řádek níže obsahuje cestu k CSV tabulce konverze CN hodnot
- Výchozí hodnota odkazuje na převodní tabulku hodnot CN sestavenou speciálně pro LU vrstvu na základě ZABAGED a LPIS 
- Pro výběr umístění vlastní převodní tabulky klikněte na ikonu tří teček vedle tohoto řádku
- Pro vytvoření nové polygonové vrstvy CN klikněte na tlačítko _Create CN layer_

<p align="center">
    <img src="../../img/ovl3.png" alt="ovl3" style="height: 60vh;">
</p>

## Záložka Výpočet objemu přímého odtoku (Runoff)
 - V rozbalovacím seznamu _Select CN layer_ vyberte vrstvu CN
	- Po jejím úspěšném získání v předchozí záložce se do rozbalovacího okna nastaví jako výchozí hodnota
	- Pokud chcete použít vrstvu vlastní, musí obsahovat pole s názvem _CN2_ s hodnotami v rozmezí (0.0 - 100.0>
		- může a nemusí obsahovat pole s názvem _CN3_ s hodnotami v rozmezí (0.0 - 100.0>

- Níže v poli _Inital Abstraction Coefficient (lambda)_ můžete zvolit vlastní hodnotu koeficientu počáteční ztráty
    - Přednastavená hodnota 0.2 pokrývá běžné případy bez bližší znalosti hydrologického chování území
	- V odůvodněných případech je možné koeficient měnit v rozmezí 0.05 - 0.3

- Pokud si přejete vyčíslit výšky a objemy přímého odtoku z návrhových 6hodinových srážkových úhrnů ze služby [rain.fsv.cvut.cz](https://www.rain.fsv.cvut.cz), vyberte možnost _Use 6-hour rainfall depth from rain.fsv.cvut.cz_
	- Následně zvolte požadované doby opakování použitím příslušných zaškrtávacích polí v sekci _Select Return Periods_

- Pokud si přejete vyčíslit výšky a objemy přímého odtoku z vlastních návrhových úhrnů, zaškrtněte možnost _User-defined rainfall depth  [mm]_
	-  Do níže umístěného textového pole vepište výšku vlastního návrhového úhrnu v milimetrech 
		- Pokud si přejete provést výpočet pro více návrhových úhrnů najednou, oddělte je v tomto poli středníkem _;_

- Proces výpočtu spustíte tlačítkem _Compute runoff volume_

<p align="center">
    <img src="../../img/ovl4.png" alt="ovl4" style="height: 60vh;">
</p>

## Dávkové spuštění

Dávkové spuštění umožňuje `run_batch.py` umístěný v adresáři
`scripts`. Nastavení dávkové úlohy je specifikováno konfiguračním
souborem ve formátu YAML. Příklad konfigurace je dostupná v souboru
`tests/batch.yaml`. Příklad spuštění:

```
python3 scripts/run_batch.py tests/batch.yaml
```

Pro OS MS Windows je určen dávkový soubor `run_batch.bat`, který
automaticky nastaví výpočetní prostředí QGIS. Před spuštěním upravte v
tomto souboru cestu k instalaci QGISu.

### Využití lokálních dat

Stáhněte data LPIS a ZABAGED a upravte cesty k datovým zdrojům (`URI`)
v konfiguračních souborech umístěných v adresáři
`config/local_data/`. Dále v nastavení dávkové úlohy změňte
`local_data` na `True`.
