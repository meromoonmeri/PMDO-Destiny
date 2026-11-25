# Validation de la base Destiny

Contrôles effectués le 24 octobre 2026.

## Arbre source

- 13 174 fichiers source, 568,8 Mio ;
- aucun pointeur Git LFS et aucune règle `filter=lfs` ;
- aucun sous-module Git ;
- aucun lien symbolique problématique ;
- plus gros fichier : 13,37 Mio, sous la limite GitHub de 100 Mio ;
- JSON, XML, zone, map de départ, scripts et titre contrôlés par `tools/validate.py`.

Commande :

```bash
python tools/validate.py
```

## Paquet Windows

- PMDC publié avec .NET SDK 8.0.426 pour `win-x64` ;
- quest Destiny fusionnée nativement avec `PMDC -quest Destiny -build` ;
- lancement final par `Destiny.exe`, sans argument `-quest`, sans sélecteur de quest et sans dossier `MODS` ;
- 10 428 fichiers dans le paquet ;
- `dist/PMDO-Destiny-Windows-x64.zip` : 378,0 Mio ;
- intégrité ZIP et présence des données, scripts, Ground, titre et indices universels vérifiés.

PMDC 0.8.12 omet `Data/Misc` lors de `MergeQuest`. Le script `tools/build_windows.py` restaure donc ces indices depuis les données de base, puis applique les éventuels remplacements de la quest. Sans eux, le standalone ne termine pas l'initialisation de ses données.

## Test runtime du standalone

Le même contenu fusionné a été lancé sous Linux avec le binaire portatif `Destiny`, en français, sans `MODS` et sans argument de quest. Le parcours suivant a été effectué graphiquement sous Xvfb :

1. notice fangame et écran-titre Destiny ;
2. menu principal et nouvelle partie ;
3. sélection du starter, du genre et saisie du pseudonyme ;
4. chargement de `destiny_hub` et de son script ;
5. affichage des deux dialogues de bienvenue ;
6. fermeture des dialogues et déplacement du personnage ;
7. ouverture du menu, choix de « Sauvegarder et continuer » ;
8. création effective de `SAVE/SAVE.rssv`.

Le journal de ce parcours final ne contient aucune exception.

### Limite du test

Le binaire Windows lui-même n'a pas été exécuté : l'environnement de test est Linux et ne dispose pas de Wine. La compilation Windows, la structure du paquet et l'intégrité du ZIP sont validées ; un dernier essai sur une machine Windows reste recommandé avant une diffusion publique plus large.
