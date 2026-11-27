# Destiny · Atelier de pose dans les huit sens

Décompresse **tout** `Atelier-Immobilier-Destiny-8-Sens.zip` dans un dossier, puis ouvre **`Atelier.html`** dans ton navigateur. Tu peux l’utiliser hors ligne. La vidéo MP4, fournie à part, montre le résultat sans ouvrir l’atelier.

1. Recherche un nom ou un code et choisis un objet. Tu peux filtrer par famille.
2. Clique sur **Poser sur le plan**, puis dans une salle ou sur le **Plateau d’essai**. La grille de pose suit les tuiles de 8 px.
3. Clique sur l’objet posé. Change la direction avec une des huit flèches, ou tourne de 45° avec **R**. **Miroir** (**M**) retourne exactement l’image courante de gauche à droite autour du même pivot. Le meuble ne change pas de case quand il tourne ou se retourne. Tu peux le glisser si tu veux changer sa place.
4. **Sprite PNG** exporte le dessin transparent de la pose voulue. **PNG de la salle** exporte la composition. Un plan JSON mémorise les positions, les orientations et le miroir. Tu peux aussi importer `Exemple-Bibliotheque.json`.

| Vues de la banque |
| --- |
| `Down` ↓ · `DownRight` ↘ · `Right` → · `UpRight` ↗ |
| `Up` ↑ · `UpLeft` ↖ · `Left` ← · `DownLeft` ↙ |

L’atelier couvre **1 108 entrées posables, variantes de couleur incluses**, soit **8 864 vues**. Il reprend les 693 entrées de l’atelier guilde (les huit vues d’un comptoir et d’un étendard sont regroupées en deux modèles), les 360 modèles du kit PMU Destiny, et les 135 ressources natives `Guilde_Imm*.dir` après dédoublonnage des correspondances. Les plans fixes, murs et escaliers du décor ne sont pas des meubles. La face fournie reste fidèle à la source ; les angles absents ont été reconstitués et plusieurs vues d’un objet symétrique peuvent coïncider. Les étendards déjà animés et les deux foyers du réfectoire restent animés. La bibliothèque garde ses rayonnages.

Le plateau libre permet d’essayer toutes les poses. Dans une salle, un pivot trop proche d’un bord ou d’un passage doit être déplacé avant de tourner. Ces vérifications de maquette ne remplacent pas les collisions du jeu. Aucun fichier de Destiny ni sauvegarde n’est installé ou modifié. Les fichiers `Atelier/Page-*.js` sont les planches d’images que lit l’atelier et ne servent pas de scripts de jeu. Les mesures de pivot sont dans `Index-poses.csv`, à l’échelle native, coordonnées depuis l’angle supérieur gauche du PNG.
