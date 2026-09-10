# Bias-Pruefung von Testsets

Dieses Projekt untersucht, ob Testitems Hinweise auf Bias enthalten.

## Testsets

- **Real-Testset (`real_testset_300.xlsx`)**: Bezieht sich auf existierende Accounts. Die Faelle wurden haendisch geprueft.
- **Unreal-Testset (`unreal_testset_300.xlsx`)**: Bezieht sich auf hypothetische Kunden. Die Faelle wurden nicht haendisch geprueft.

## Statistikdateien

Die Statistikdateien dienen dazu, moegliche Verzerrungen (Bias) in den Testitems zu pruefen:

- `outputs_word_length/`: Wort- und Zeichenlaengen der Items, insgesamt sowie nach Skill und Branche.
- `outputs_repeated_phrases/`: Wiederkehrende Phrasen und die Items, in denen sie vorkommen. Die Vektordatei zeigt, welche Phrasen pro Item vorhanden sind.

## Skripte

- `analyze_turn_length.py`: Erstellt die Laengenstatistiken.
- `identify_repeated_phrases.py`: Findet Phrasen, die in mindestens drei Items vorkommen.

Beide Skripte lesen standardmaessig `real_testset_300.xlsx` aus dem Tabellenblatt `Testfaelle` ein.
