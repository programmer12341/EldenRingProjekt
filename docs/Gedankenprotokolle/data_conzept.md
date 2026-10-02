0. Wie der Boss funktioniert:
AUSGANGSLAGE -> Random einer der 3 Attakcne oder stepback -> schwert in ausgangslage bringen -> Attacke


1. Angriff-Animation / Andere Animation
Die Idee ist es standbilder aus dem spiel aufzunehmen und dann diese zu kategorisieren in GEGNER MACHT GERADE EINE ANGRIFF-ANIMATION oder GEGNER MACHT GERADE KEINE ANGRIFFS-ANIMATION

Wenn meine KI erkennt das der Gegner keine Angriffs Animation macht dann kann ich ihn dort hitten ganz simpel.

Probleme: 
- es fuehlt sich irgendwie nicht richtig an (nicht klar definiert)
- es hilft nicht direkt den Boss zu besiegen
- eigentlich macht der Boss IMMER eine Animation
- keine Farbbilder
- standbilder eignen sich nicht so gut - bewegungsinformationen
- zu viel bewegt im gameplay ?
- zum labeln die Bilder noch nicht runterskalieren 

Besser Definiert:

Es gibt folgende Animationen
M MOVEMENT - laufen, drehen , position ändern 
A ATTACK - aktiv mit dem Schwert ausholen und schlagen (auch kombos)
R RECOVERY - schwert wieder hochheben
P PAUSE - kurzes cooldown bis nächster angriff kommt 

2. Wann muss ich Blocken?
Die Idee ist es nochmals gameplay aufzunehmen wo ich den Boss perfect mit dem Schild Blocke. 

Fuer die Trainingsdaten gebe ich dem netze 3 frames und die aufgabe: wird im naechsten frame geblockt ja oder nein? in den daten kann ich dann nachschauen und haette so meine labels.