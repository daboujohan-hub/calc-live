# CALC · Termux Live Calculator

> Une calculatrice vivante dans le terminal : le résultat se calcule pendant que tu tapes.

**by AbouDev Labs** · Abidjan, Côte d'Ivoire
TikTok : Aboujohan.dev · GitHub : daboujohan-hub · daboujohan@gmail.com

CALC est écrite en Python et tourne dans Termux, directement sur téléphone Android.
Elle est pensée pour la Côte d'Ivoire et l'Afrique de l'Ouest : FCFA, usage en boutique, interface en français.

## Ce qu'elle fait

- **Calcul** : fonctions scientifiques, conversions d'unités, devises FCFA / EUR / USD
- **Boutique** : prix et bénéfice, monnaie, ventes, dettes, stock, rappels, factures
- **Mesure de terrain** : surface, hauteur, distance GPS entre deux téléphones
- **Sécurité** : PIN, sauvegarde chiffrée AES-256
- **Interface** : résultat en grand (style LED), graphiques ASCII, thèmes clair et sombre, barre d'état, boutons tactiles, coin « machine » qui montre le calcul en direct

## Installation

### Sur Android (Termux), recommandé

    pkg install -y git
    git clone https://github.com/daboujohan-hub/calc-live
    cd calc-live
    bash install.sh

Puis, depuis n'importe quel dossier :

    calc-live

L'installeur ajoute Python et OpenSSL si besoin. Pour les mesures GPS (facultatif) :
`pkg install termux-api` et l'application Termux:API.

### Sur Linux ou macOS

Python 3.9+ est requis (OpenSSL pour la sauvegarde chiffrée). CALC a été développée et testée sur Termux ;
Linux et macOS devraient fonctionner mais n'ont pas été testés.

    git clone https://github.com/daboujohan-hub/calc-live
    cd calc-live
    bash install.sh

Si `calc-live` est introuvable, ajoute `~/.local/bin` à ton PATH.

### Mise à jour

    cd calc-live && git pull && bash install.sh

### Désinstallation

    bash install.sh --remove

Tes données personnelles (taux, ventes, PIN...) restent sur ton téléphone.

## Utilisation

Tape un calcul : le résultat apparaît en direct. **Entrée** valide, **Esc** quitte, **Ctrl+L** efface.
Tape `aide` pour toutes les commandes, `apropos` pour la présentation du projet.

### Calcul
- `sqrt(144)`, `sin`, `cos`, `tan`, `log`, `log2`, `log10`, `exp`, `fact`, `gcd`, `lcm`, `hypot`, `max`, `min`
- Constantes : `pi`, `e`, `tau` · Puissance : `x**n`
- `mode deg` / `mode rad` : unité des angles
- `100 km to miles`, `37 c to f`, `70 kg to lbs`
- `5000 cfa to eur`, `taux usd 600` (régler un taux)
- `plot sin(x)`, `plot x**2 -5 5` : graphique ASCII

### Boutique
- `prix 5000 benefice 20%`, `5000 + 20%`, `20% de 5000`
- `monnaie 10000 - 7500`
- `vente riz 2500 x3`, `ventes`
- `dette awa 5000`, `dettes`
- `stock riz +10`, `stock`
- `rappel 17h appeler`, `rappels`
- `facture riz 2500x3, huile 1000x2`

### Mesure
- `surface 5x4`, `hauteur 10 angle 35`
- `point`, `terrain`, `terrain efface`
- `mesure serveur` et `mesure connecte IP CODE` : distance entre deux téléphones sur le même Wi-Fi
- `mesure enregistre nom`, `mesures`

### Sécurité et apparence
- `pin`, `pin off` : verrouiller ou déverrouiller l'outil
- `sauvegarde`, `export`, `restaure`
- `theme clair`, `theme sombre`
- `tactile on` / `tactile off` : boutons tactiles

### Commandes avancées
- `restaure NOM` : restaurer une sauvegarde précise
- `hauteur 10 angle 35 oeil 1.6` : même mesure, avec la hauteur de tes yeux

### Aboudev (langage d'AbouDev Labs)
CALC sait lancer **Aboudev**, un langage de programmation en français créé par AbouDev Labs. Il s'installe à part : une commande `aboudev`, ou le fichier `~/aboudev/aboudev.py`. Tes programmes (`.a`) vivent dans `~/aboudev`. Exemple, un programme d'une ligne : `affiche Bonjour le monde !`
- `ab affiche Bonjour` : exécuter une ligne
- `ab prog.a` : lancer un programme
- `ab edite prog` : écrire un programme avec nano, puis le lancer
- `ab liste` : voir tes programmes
- `ab anim` : revoir l'animation

**Attention :** Aboudev peut exécuter des commandes, lire, écrire et supprimer des fichiers, et utiliser le réseau. Ne lance que des programmes dont tu connais le contenu.
Chaque programme est arrêté au bout de 20 secondes et sa sortie est limitée à 500 lignes.

## Comment ça marche

- Le code est découpé en morceaux dans `parts/` (calcul, boutique, PIN, mesure, interface...), assemblés au lancement par le petit chargeur `calc.py`. Il est écrit avec la bibliothèque standard de Python et `curses`.
- À chaque touche, l'expression est analysée avec `ast` puis calculée, et le résultat s'affiche aussitôt.
- Le PIN est stocké sous forme de hash PBKDF2-SHA256 (200 000 itérations) avec un sel.
- La sauvegarde utilise OpenSSL en AES-256-CBC avec dérivation PBKDF2. Sans le mot de passe, elle est impossible à rouvrir.
- La mesure entre deux téléphones ouvre une connexion locale protégée par un code à 4 chiffres : adresses privées uniquement, 3 essais, 120 secondes.
- Les taux de change sont enregistrés dans `~/.calc_taux.json`.

## Ce que CALC écrit sur ton téléphone

Les données sont stockées sur ton appareil, dans ton dossier personnel. Les principaux fichiers :
- `~/calc_historique.txt` : l'historique de tes calculs
- `~/.calc_data.json` : tes données (ventes, dettes, stock, rappels...)
- `~/.calc_taux.json` : les taux de change que tu as réglés
- `~/.calc_config.json` : tes réglages (thème...)
- `~/.calc_pin.json` : ton PIN, sous forme de hash (jamais en clair)
- `~/calc_sauvegardes` et `~/calc_factures` : sauvegardes et factures
- `~/aboudev` : tes programmes Aboudev

Pour effacer tes données, supprime ces fichiers.

## Contact

Une idée, un bug ? Ouvre une *issue* sur GitHub ou écris à daboujohan@gmail.com.
