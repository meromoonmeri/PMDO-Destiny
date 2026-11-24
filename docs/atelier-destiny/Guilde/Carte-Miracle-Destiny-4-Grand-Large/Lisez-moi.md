# Carte Miracle de Destiny 4 — Grand Large

**Ouvrir `Carte-Miracle-Destiny-4.html`**. Aucun serveur ni accès réseau n’est nécessaire. La carte part de Réverie. Le circuit **Grand Large** propose une escale dans chacun des huit nouveaux ensembles ; les 50 nouveaux lieux se choisissent individuellement dans **Destination**.

## L’ajout

- **Quatre grandes îles** : Nacrebrune, Grand-Frimas, Cendres d’Or et Sylverive.
- **Quatre archipels** : Sillons, Îles de l’Aube, Caps de Cuivre et Couronne de Jade.
- **50 lieux dessinés et visitables** : grottes, ruines, vergers, cascades, terrasses, lacs et reliefs. Les formes et les lieux sont peints dans quatre bruts mis en prolongement des bords de la carte DS. Le détourage et le raccord des pigments se font sur la grille native. La planche fournie sert également au détourage de **20 petits motifs fixes**, et à la reprise des aplats en hachures de terrain, notamment autour du lac gelé.
- `Carnet-des-50-lieux.html` montre le détail du dessin de chaque lieu, sans montrer la géographie du monde d’un seul tenant. `Extension-EoS-Grand-Large.png` est le raccord d’atelier, pas le déblocage du lecteur : les **504 × 336 pixels** de la carte centrale EoS sont identiques à la source. Les terres de Destiny 4 restent également pixel-identiques, translatées d’un seul tenant.

## Les nuages

- Le lecteur reprend les **poses WAN 15, 0 et 1**, l’ordre de dessin, les coordonnées 8.8 et les vitesses de `s01p01a1.wan` / **6 → 7, Île Blizzard**. Données de la reconstitution SkyTemple et [source de la carte EoS](https://github.com/pret/pmd-sky/blob/9fa563873cec324993a614ea8ce03433add10e46/asm/overlay_11_022ECD24_data.s). Noir de sortie et de retour en 16 ticks, 240 ticks d’objets dont 30 d’attente, soit environ **4,28 s** par ouverture. Seuls l’origine et l’échelle des sprites sont adaptées à chaque zone Destiny.
- Le voile reste **opaque** sur les zones non visitées. **Carte entière** n’est activable qu’après la dernière levée des **32 zones**. Recharger pendant une levée la reprend, sans contourner le verrou. Les 95 repères ne doivent pas tous être visités pour accéder à la vue d’ensemble. Le réglage d’accessibilité mouvement réduit omet l’animation sans omettre l’arrivée. La vitesse 4× accélère la marche et la traversée, pas les ticks des nuages.
- `Destiny-4-Levee-des-nuages.mp4` montre deux arrivées réelles : Chute de Sylverive et Grotte du Grand-Frimas. Son de découverte au terme de chaque levée, pas de dévoilement général dans la vidéo.

## Sources et vérification

- `Generations/Extension-EoS/Denses/` contient les quatre bruts retenus. `Sources/Extension-EoS/Lieux.json` associe chaque dessin à son repère. `Atlas.json` contient les circuits, trajets et calques. Les quatre rapports `Verification-*.json` couvrent pixels, navigation, lecteur, et vidéo.
- Avec Python, Pillow, SciPy et NumPy : `python Sources/DecouperExtension.py`, `python Sources/Monde.py`, `python Sources/Autonome.py`. Les entrées nécessaires au calcul sont dans `Generations/` et `Sources/Bases/`. `python Sources/Carnet.py` reconstruit le carnet. Les scripts Playwright utilisent `PLAYWRIGHT` et `CHROME` si nécessaires ; l’encodeur vidéo utilise FFmpeg.
- Extension indépendante. Aucun fichier de ROM ni de jeu n’est inclus ou modifié. Les lieux et leurs noms sont originaux pour Destiny ; sprites et ressources DS demeurent à leurs ayants droit.
