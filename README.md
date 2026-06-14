# Projekt informatika 2026: Naključni generator zemljevidov

## Kazalo

- [Opis projekta](#opis-projekta)
- [Namen projekta](#namen-projekta)
- [Končni izdelek](#končni-izdelek)
- [Glavne funkcionalnosti](#glavne-funkcionalnosti)
- [Uporabljene tehnologije](#uporabljene-tehnologije)
- [Zgradba projekta](#zgradba-projekta)
- [Kako deluje algoritem](#kako-deluje-algoritem)
- [Predstavitev mreže](#predstavitev-mreže)
- [BSP razdeljevanje prostora](#bsp-razdeljevanje-prostora)
- [Ustvarjanje sob](#ustvarjanje-sob)
- [Povezovanje sob s hodniki](#povezovanje-sob-s-hodniki)
- [Preverjanje poti z BFS](#preverjanje-poti-z-bfs)
- [Semena za ponovljivost](#semena-za-ponovljivost)
- [Uporaba programa](#uporaba-programa)
- [Namestitev](#namestitev)
- [Testiranje](#testiranje)
- [Možne izboljšave](#možne-izboljšave)
- [Zaključek](#zaključek)

## Opis projekta

Ta projekt je program za naključno ustvarjanje zemljevidov oziroma preprostih ječ. Zemljevid je predstavljen kot dvodimenzionalna mreža, kjer je vsako polje lahko zid, tla, začetna točka ali končna točka. Program najprej ustvari prazen zemljevid, nato ga z algoritmi postopoma spremeni v povezan sistem sob in hodnikov.

Projekt je namenoma osredotočen predvsem na matematiko, logiko in algoritme, ne na kompleksno grafiko. Vizualni del je preprost: zemljevid je prikazan s kvadratki v oknu Pygame ali kot ASCII izpis v terminalu.

## Namen projekta

Namen projekta je prikazati, kako lahko s programiranjem ustvarimo smiseln naključen svet, ki ni samo vizualno zanimiv, ampak je tudi pravilno povezan. Pri takšnem generatorju ni dovolj, da sobe in hodniki izgledajo naključno. Pomembno je tudi, da lahko igralec dejansko pride od začetka do konca in da ni nedosegljivih sob.

Projekt vključuje več pomembnih programerskih konceptov:

- delo z dvodimenzionalnimi seznami,
- rekurzivno oziroma postopno deljenje prostora,
- naključno generiranje z uporabo semena,
- grafe in povezovanje vozlišč,
- iskanje poti z algoritmom BFS,
- preverjanje pravilnosti ustvarjenega zemljevida,
- osnovno interaktivno grafično predstavitev s Pygame.

## Končni izdelek

Končni izdelek je aplikacija, ki uporabniku omogoča ustvarjanje naključnih zemljevidov. Uporabnik lahko določi velikost mreže, število sob in odstotek dodatne povezanosti. Program nato ustvari sobe, jih poveže s hodniki, določi začetno in končno točko ter preveri, ali med njima obstaja veljavna pot.

Program ima dva načina uporabe:

- grafični način s Pygame,
- besedilni ASCII način, ki deluje tudi brez Pygame.

ASCII način je uporaben za hitro testiranje, grafični način pa omogoča bolj pregleden prikaz zemljevida.

## Glavne funkcionalnosti

- Naključno ustvarjanje zemljevida na mreži.
- Nastavljiva širina in višina zemljevida.
- Nastavljivo število sob.
- Nastavljiva dodatna povezanost med sobami.
- Uporaba algoritma BSP za razdelitev prostora.
- Samodejno ustvarjanje sob.
- Samodejno povezovanje sob s hodniki.
- Izbira začetne in končne točke.
- Preverjanje poti med začetkom in koncem z BFS.
- Možnost prikaza najdene poti.
- Podpora za seme, zato lahko isti zemljevid ustvarimo večkrat.
- Testi za preverjanje osnovne pravilnosti algoritma.

## Uporabljene tehnologije

Projekt je napisan v programskem jeziku Python.

Uporabljene knjižnice:

- `pygame` za grafični prikaz zemljevida,
- `argparse` za branje argumentov iz ukazne vrstice,
- `random` za naključno generiranje,
- `collections.deque` za učinkovito izvajanje algoritma BFS,
- `unittest` za testiranje.

> Opomba: Pygame trenutno morda ne deluje pravilno s Python 3.14, ker za to različico ni nujno na voljo pripravljeno kolesce za namestitev. Priporočena je uporaba Python 3.12 ali Python 3.13.

## Zgradba projekta

```text
.
├── main.py
├── map_generator.py
├── test_map_generator.py
├── requirements.txt
└── README.md
```

### `main.py`

Datoteka `main.py` vsebuje uporabniški del programa. Skrbi za:

- branje argumentov iz ukazne vrstice,
- zagon grafičnega okna Pygame,
- prikaz zemljevida,
- prikaz vnosnih polj,
- odzivanje na tipke in klike,
- ASCII izpis zemljevida, če uporabnik uporabi možnost `--ascii`.

### `map_generator.py`

Datoteka `map_generator.py` vsebuje glavno logiko generatorja. V njej so funkcije in podatkovne strukture za:

- predstavitev pravokotnikov,
- ustvarjanje zemljevida,
- razdeljevanje prostora z BSP,
- ustvarjanje sob,
- povezovanje sob,
- ustvarjanje hodnikov,
- iskanje poti z BFS,
- pretvorbo zemljevida v ASCII obliko.

### `test_map_generator.py`

Datoteka `test_map_generator.py` vsebuje teste, ki preverijo:

- ali je ustvarjena pot med začetkom in koncem,
- ali BFS pot res obstaja,
- ali isti seed vedno ustvari isti zemljevid.

### `requirements.txt`

Datoteka `requirements.txt` vsebuje zunanjo knjižnico, ki jo program potrebuje za grafični način:

```text
pygame>=2.5.0
```

## Kako deluje algoritem

Generator deluje v več korakih:

1. Ustvari prazno mrežo, polno zidov.
2. Z algoritmom BSP razdeli prostor na manjše pravokotne regije.
3. V vsaki regiji ustvari eno sobo.
4. Izračuna središča sob.
5. Sobe poveže s hodniki.
6. Doda začetno in končno točko.
7. Z algoritmom BFS preveri, ali pot res obstaja.
8. Če zemljevid ni veljaven, poskusi ponovno.

Ta postopek zagotavlja, da rezultat ni samo naključen, ampak tudi uporaben.

## Predstavitev mreže

Zemljevid je predstavljen kot dvodimenzionalni seznam:

```python
grid[y][x]
```

Vsako polje ima številčno vrednost:

| Vrednost | Pomen |
| --- | --- |
| `0` | zid |
| `1` | tla |
| `2` | začetek |
| `3` | konec |

Takšna predstavitev je preprosta in učinkovita, saj lahko program hitro preveri, kaj je na določeni koordinati.

## BSP razdeljevanje prostora

BSP pomeni *Binary Space Partitioning*. To je metoda, pri kateri večji pravokotnik postopoma delimo na dva manjša pravokotnika. Postopek se ponavlja, dokler ne dobimo dovolj regij za sobe.

V projektu se BSP uporablja zato, da sobe niso postavljene popolnoma neurejeno. Vsaka soba dobi svoj del prostora, zato se sobe praviloma ne prekrivajo in so bolj enakomerno razporejene po zemljevidu.

Primer ideje:

```text
+-----------------------+
|           |           |
|           |           |
|-----------+           |
|     |     |           |
|     |     |           |
+-----------------------+
```

Vsak manjši pravokotnik lahko nato vsebuje eno sobo.

## Ustvarjanje sob

Ko BSP ustvari regije, program znotraj vsake regije ustvari sobo. Soba je manjša od regije, zato med sobami ostane nekaj prostora za zidove in hodnike.

Soba je predstavljena s pravokotnikom, ki vsebuje:

- koordinato `x`,
- koordinato `y`,
- širino,
- višino.

Program nato v mreži spremeni ustrezna polja iz zidov v tla.

## Povezovanje sob s hodniki

Ko so sobe ustvarjene, mora program zagotoviti, da so povezane. Vsaka soba ima središčno točko, ki deluje kot vozlišče v grafu. Program izračuna razdalje med sobami in jih poveže podobno kot pri minimalnem vpetem drevesu.

Minimalno vpeto drevo poskrbi, da so vse sobe povezane z najmanjšim potrebnim številom povezav. To pomeni, da ni nedosegljivih sob.

Parameter `connectivity` določa, koliko dodatnih povezav program doda poleg osnovnih povezav. Večja vrednost pomeni več alternativnih poti in bolj odprt zemljevid.

Primer:

- `0 %` pomeni osnovno povezan zemljevid,
- `25 %` pomeni nekaj dodatnih povezav,
- `100 %` pomeni veliko dodatnih povezav.

Hodniki so ustvarjeni med središči sob. Program se premika po mreži proti ciljni sobi in sproti spreminja zidove v tla.

## Preverjanje poti z BFS

BFS pomeni *Breadth-First Search* oziroma iskanje v širino. To je algoritem za iskanje poti v grafu ali mreži.

V tem projektu BFS deluje tako:

1. Začne pri začetni točki.
2. Pregleda sosednja prehodna polja.
3. Nato pregleda sosede teh polj.
4. Postopek ponavlja, dokler ne najde konca ali dokler ne zmanjka možnosti.

BFS je primeren za ta projekt, ker na mreži brez uteži najde najkrajšo pot glede na število korakov.

Program BFS uporablja za dve pomembni preverjanji:

- ali je mogoče priti od začetka do konca,
- ali so središča vseh sob dosegljiva.

Če zemljevid tega ne izpolnjuje, program ustvari nov poskus.

## Semena za ponovljivost

Naključni generator uporablja seme oziroma `seed`. Seme je število, ki določa zaporedje naključnih odločitev.

Če uporabimo isti seed in iste parametre, dobimo isti zemljevid. To je koristno za:

- testiranje,
- odpravljanje napak,
- deljenje zanimivih zemljevidov,
- ponovljivo predstavitev projekta.

Primer:

```powershell
python main.py --ascii --seed 42
```

## Uporaba programa

### Grafični način

Grafični način zaženemo z ukazom:

```powershell
python main.py
```

V oknu lahko uporabnik spreminja:

- širino mreže,
- višino mreže,
- število sob,
- odstotek povezanosti.

Kontrole:

| Tipka ali dejanje | Pomen |
| --- | --- |
| `G` | ustvari nov zemljevid |
| klik na gumb `Ustvari` | ustvari nov zemljevid |
| `Space` | prikaže ali skrije najdeno pot |
| `Esc` | zapre program |

### ASCII način

ASCII način deluje brez Pygame:

```powershell
python main.py --ascii
```

Primer z dodatnimi parametri:

```powershell
python main.py --ascii --width 80 --height 45 --rooms 18 --connectivity 25 --seed 42
```

Pomen znakov:

| Znak | Pomen |
| --- | --- |
| `#` | zid |
| `.` | tla |
| `S` | začetek |
| `E` | konec |
| `*` | najdena pot |

## Namestitev

Priporočena je uporaba virtualnega okolja.

### Windows

Če imate nameščen Python 3.13:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python main.py
```

Če Pygame ne deluje, lahko vseeno zaženete ASCII način:

```powershell
python main.py --ascii
```

## Testiranje

Testi se zaženejo z ukazom:

```powershell
python -m unittest -v
```

Trenutni testi preverijo osnovne lastnosti generatorja:

- zemljevid ima pot od začetka do konca,
- BFS najde pot,
- isti seed ustvari enak zemljevid.

Testiranje je pomembno, ker je projekt naključen. Brez testov bi se lahko zgodilo, da program v nekaterih primerih ustvari neveljaven zemljevid, tega pa ne bi takoj opazili.

## Možne izboljšave

Projekt bi bilo mogoče nadgraditi na več načinov:

- dodajanje različnih vrst sob,
- dodajanje vrat,
- dodajanje pasti ali zakladov,
- ustvarjanje več nadstropij,
- uporaba algoritma A* za dodatno primerjavo z BFS,
- izvoz zemljevida v sliko,
- shranjevanje in nalaganje zemljevidov,
- bolj napreden uporabniški vmesnik,
- možnost izbire med BSP in Cellular Automata algoritmom.

## Zaključek

Projekt prikazuje, kako lahko z uporabo algoritmov ustvarimo naključen, vendar logično pravilen zemljevid. Glavni poudarek ni na grafiki, ampak na notranjem delovanju programa: predstavitvi podatkov, razdeljevanju prostora, povezovanju sob in preverjanju dosegljivosti.

Končni program je uporaben primer povezave med matematiko, algoritmi in praktičnim programiranjem. Zaradi grafičnega prikaza je rezultat enostavno razumljiv, zaradi ASCII načina in testov pa ga je mogoče preverjati tudi brez dodatnih grafičnih knjižnic.
