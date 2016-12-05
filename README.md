# Arrows

Requires:
    Python 3.5
    MongoDb

# Docker
Installtion und Betrieb gehen am einfachsten per Dockercontainer.
Dazu kann das beiliegende Image + Scripte verwendet werden. Durch "docker build" wird dabei die komplette Installation übernommen.

## Installation

    $ cd src/
    $ pip install -r requirements.txt

## Anpassung der Config:

    $ vim src/config/local.cfg

 1. Cookie Secret ändern:
    $ < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c64

    Text als cookie_secret string setzen in local.cfg setzen.

 2. Admin Passwort erstellen:

    $ cd src/
    $ < /dev/urandom tr -dc _A-Z-a-z-0-9 | head -c8 > .secret

## Starten

1. MongoDB Server starten.
2. Webserver Starten:

    $ cd src/
    $ python server-fast.py

3. Sicherheit:
Evtl. Apache oder Nginx mit HTTPS vorschalten.


Datenauswertung
---------------

Die Daten jedes Teilnehmers liegen als XLSX Dateien vor. Jede Datei beinhaltet zwei Arbeitsblätter: "System Events" und "Trials".

Das Arbeitsblatt "System Events" zeigt eine Übersicht der Abfolge der Ereignisse, also wann die Anwendung gestartet und geschlossen wurde, etc.

Das Arbeitsblatt "Trials" zeigt eine Übersicht der Variablen jedes Durchlaufs:

```participant_id```:      Eindeutige ID des Datensatzes

```tag```:                 VPN Code (falls kein Code eingetragen wurde, entspricht dieses Feld der ID)

```timestamp```:           Datum + Zeit der Erzeugung des Eintrags, ISO Format

```delta```:               Unterschied zwischen linkem und rechtem Wertpapier

```p1```:                  Güte des linken Wertpapiers

```p2```:                  Güte des rechten Wertpapiers

```subrange_key```:        Spanne aus der der Deltawert gesampelt wurde

```sample_size```:         Größe der Stichprobe (12,18, etc)

```selected_right```:      Auswahl des Teilnehmers (0: Links, 1: Rechts)

```ticks```:               Anzahl an gesehenen Updates

```duration_ms```:         Dauer der Präsentation, in Millisekunden (1 ms = 1/1000 s)

```empirical_delta```:     Tatsächlicher Abstand zwischen den Wertpapieren. *

```empirical_p1```:        Tatsächlicher p Wert des linken Wertpapiers. *

```empirical_p2```:        Tatsächlicher p Wert des rechten Wertpapiers. *

```started_right```:       Welches Wertpapier wurde zuerst geupdated? (0: Links, 1: Rechts)

```last_left```:           Index des letzten gesehenen Elements der linken Seite
```last_right```:          Index des letzten gesehenen Elements der rechten Seite

```left```:                Tatsächliche Sequenz des Trials (0: Runter, 1: Rauf)

```right```:               Tatsächliche Sequenz des Trials (0: Runter, 1: Rauf)


*) Aufgrund von Rundungsfehlern kann der tatsächliche Abstand zwischen den Wertpapieren vom ursprünglichen Parameter, der für das Sampling verwendet wurde, abweichen.


Bitte beachten:
---------------

Das System prüft in den Rohdaten NICHT, ob die Auswahl des Teilnehmers RICHTIG war, sondern ob der Teilnehmer die RECHTE oder die LINKE Seite gewählt hat.

Das 'right' in selected_right bezieht sich also auf die RECHTE aktie (1 wenn diese gewählt wurde, 0 wenn nicht). Daher entspricht im Feld: selected_right: 0 Links und 1 Rechts.

RIGHT bedeutet NICHT, dass der Trial vom Teilnehmer korrekt bewertet wurde. Ob der Teilnehmer richtig gewählt hat, ergibt sich aus dem Abgleich mit dem empirischen p-Werten. Wenn das empirische p1 größer ist als das empirische p2, dann war die linke aktie besser. Der Trial ist dann korrekt, wenn

p1 > p2 UND selected_right = 0
ODER
p1 < p2 UND selected_right = 1

Diese Logik ist im Anzeigemodul vorhanden, sodass die Auszahlung stattfinden kann, jedoch wurde dies nicht für die Rohdatenausgabe implementiert (wg. Zeitmangel).