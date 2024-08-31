Načítání vrstev není úplně nejrychlejší. <br>
Pro správnou funkci je potřeba mít v projektu nastaven CRS na EPSG:5514 <br>
Testováno na MS Windows a Linux(Ubuntu). <br> <br>

## Funkce pluginu
- Plugin nyní stahuje požadované ZABAGED vrstvy uvnitř výřezu okna či polygonu, pomocí WFS služby. 
- Plugin připojuje LPIS WMS vrstvu
- **nově: Stahování probíhá na pozadí v jiném vlákně Qgisu**
- **nově: Uživatel je informován o procesu stahování a je schopen ho tlačítkem ukončit**

## Další informace
Názvy ZABAGED vrstev, které plugin získává, jsou v souboru zabagedlayers.conf <br>
Některé požadované ZABAGED vrstvy není možné zahrnout kvůli následujícím problémům poskytovatele dat: <br>
- Usazovací nádrž - 2024-01-01: 1.07 USAZOVACÍ NÁDRŽ - objekt zrušen z kategorie 1. SÍDELNÍ, HOSPODÁŘSKÉ A KULTURNÍ OBJEKTY <br>
- Dobývací prostor - (*) Typ objektu bude publikován po smluvním zajištění dat od správce. <br>
- Chráněné ložiskové území -   (*) Typ objektu bude publikován po smluvním zajištění dat od správce. <br>
