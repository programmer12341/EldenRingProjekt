Was ist das Ziel:

    Ich möchte der KI beibringen den Zustand Base und Not_Base zu erkennen

    Der Base zustand ist der zusatnd wo alle Angriffs animationen beginnen. Diesen soll die KI klassifizieren.


Wie bin ich vorgegangen:

    - Daten sammeln 
    - Schneiden im CapCup
    - in data gespeichert
    - in images zerlegt 
    - labeling 
    - label checker (95% accuracy)
    - daten analyse #1
    - daten splitten #2
    




Ergebnis:











#Daten analyse

1. Class Imbalance 
Base:      ca. 14 %
Not_Base:  ca. 83 %
uncertain: ca. 3 %

-> fürs training unbeding 50% 50% verteilung

2. Genug Varianz in den Daten
Auf den bildern gibt es deutliche unterschiede in_
    - Helligkeit
    - abstand Boss zu spieler
    - rotation von Boss/spieler
    - Hintergründe und boden 

-> ich brauche genug daten wo die Ki alle fälle im training gesehen hatte
-> e

3. Die Label definition noch schärfen anhand der uncertain data

4. Fazig: Mit mehr daten würde ich beide Probleme lösen hihi

#2 Splitt 

Base: 632 
Not_Base_ 632 

Base_Val: 63
Not_Base_Val: 63

Base_Test: 63
Not_Base_Test: 63
