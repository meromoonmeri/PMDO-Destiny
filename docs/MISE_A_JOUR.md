# 📜 Destiny — Journal des mises à jour

> **Ce document est « la mise à jour » : il est mis à jour à CHAQUE avancée du projet.**
> La dernière entrée sert de texte de release GitHub ; `tools/release_notes.py`
> l'extrait automatiquement. L'installation complète publiée à chaque version
> porte son numéro (fichier `VERSION`, ZIP `PMDO-Destiny-Windows-x64-<version>.zip`).

---

## 🌟 v0.3.5-dev-quiz — Quiz PMD Sky/Red, étoile au clic droit, prologue PMD (01/11/2026)

**📦 Installation complète : `PMDO-Destiny-Windows-x64-0.3.5-dev-quiz.zip`** (avec LISEZ_MOI versionné)
**🩹 Mise à jour depuis la 0.3.4 : `PMDO-Destiny-Mise-a-jour-0.3.5-dev-quiz.zip`**
**🔗 Release : https://github.com/meromoonmeri/PMDO-Destiny/releases/tag/v0.3.5-dev-quiz**

### ✨ Quiz de personnalité refondu — 20 questions façon PMD Sky / Red
- **20 questions** (au lieu de 15) avec **5 choix axés personnalité** sur la majorité d'entre elles, chaque choix correspondant à une nature différente
- **Situations parlantes** du quotidien d'explorateur (trésor dans une grotte sombre, blague nulle du partenaire, la veille de ta première grande aventure…)
- **Questions « Oui / Non »** incluses (3) et **réponses en plusieurs phrases** pour les questions sensibles
- **🚫 Aucun compteur « 12/20 »** dans le dialogue : le joueur vit les situations, pas un décompte
- Équilibrage vérifié : chacune des 16 natures est dominante d'au moins 3 choix

### 🎨 Animation de révélation — l'étoile forgée au clic droit
- Le joueur **MAINTIENT le clic droit** (repli : touche d'action) pour charger une **lumière pixel-art** qui forge une étoile (3 paliers d'animation)
- L'étoile terminée s'illumine **aux couleurs du type du starter** (19 étoiles, une par type) + fanfare
- **« Quelqu'un comme toi serait [Nom coloré selon son type] ! »** avec **son portrait**
- Secours intégré (60 s sans maintien) : personne ne reste bloqué
- Sprites générés de façon déterministe par `tools/generer_etoile_quiz.py` (22 DirSheet `Content/BG/quiz_star_*.dir`) ; séquence portée par `personality_test/revelation_etoile.lua`, zéro modification C#

### 🗡️ Prologue PMD complet (également dans cette version)
- Tutorials Lost Wood aller/retour à la Halcyon (narrateur neutre), rencontre 7 actes sur `zrv2_zone_reveil_nuit` (naming `NameMenu`, caméra montagne, portrait `'Inspired'`, menu multi-choix, invitation à **Réverie Town**), héros muet (pensées en `(…)`)
- `lost_wood` **facile** : niveau 3, rencontres douces, MaxFoes 3, objets de soin renforcés — garanti par tests
- Provisions de départ au départ du donjon (2 oran, 1 pomme, 1 leppa, 1 réveil)

### 🧪 Tests & validation
- 🆕 `test_quiz_revelation.lua` (données + séquence mockée complète) et `test_quiz_etoiles.py` (structure DirSheet, régénération pixel-identique, couleurs synchronisées)
- Suites Lua (5) + Python (7) au vert, `tools/validate.py` → VALIDATION OK
- CI : tests de quiz ajoutés au workflow Windows + tests Lua via lupa

### 🏷️ Versionnement de l'installation
- Fichier `VERSION` (source unique), version affichée dans `LISEZ_MOI.txt`, ZIP nommé avec la version
- Workflow `release-version.yml` : à chaque tag `v*`, build + `Mise-a-jour` + release GitHub versionnée automatiques

---

## 🌲 v0.3.4-dev-foret — Forêt aux lucioles et corrections validées (01/11/2026)

- Lost Wood refait : sept étages aux lucioles, ruines moussues, rivière et chemins inspirés de la référence
- Cliff : moulin et avant-plans corrigés, nuages animés ; halo de l'introduction validé ; portraits natifs au quiz ; teinte de nuit Ground
- 22 générations testées dans le moteur ; commit `0776258`

## 🏘️ v0.3.3-dev-reverie — Réverie Town, tutoriel et statue (31/10/2026)

- Visite de Réverie Town (caméra, dépôt, achat), tutoriel Lost Wood neutre aller/retour, statue Kangourex et ses leçons

## 🌲 v0.3.2-dev-lostwood — Lost Wood et réveil (31/10/2026)

- Donjon Lost Wood 7 étages, cinématique de réveil `zrv2_zone_reveil_nuit`, scène de la falaise (jour/nuit)

## 🎓 v0.3.1-dev-talents — Choix des talents (31/10/2026)

- `talents_depart.lua` : talents jouables par espèce **et forme**, talent caché, confirmations, dédoublonnage

## 🌈 v0.3.0-dev-source-376 — Source irisée (31/10/2026)

- Source irisée : carte, escalier, colonne pulsante 78 phases, évolution native et menu Méga ; QI individuel (formule adaptée d'Explorers)

## 🗺️ v0.2.0-dev-375 — Destiny unifié, 375 cartes (31/10/2026)

- Quest unique `destiny`, 375 cartes `.rsground`, payload compressé de `WaterfallVillageCapital`, ZIP Windows autonome

## 🎉 v0.1.0 — Base autonome (24/10/2026)

- Socle PMDO 0.8.12 autonome : moteur compilé, ressources de base, quest `destiny`, `destiny_hub`
