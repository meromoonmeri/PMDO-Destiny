# Première étude d'animation IA — Pyro-Explosion

`image-01.png`, `image-02.png`, `image-02b.png`, `image-03.png`, `image-04.png` sont cinq poses produites séparément par le générateur d'images à partir d'une pose de référence issue de l'effet PMDO `Flamethrower_2`. `image-01b.png` est une autre génération non retenue dans cet assemblage. Les `pose-01` à `pose-04` sont les premiers essais de génération, rejetés car le modèle a reproduit le format allongé des planches de référence et ajouté des éléments indésirables.

Les fichiers `*-transparent-64.png` sont les poses sélectionnées, réduites au plus proche voisin et détourées par suppression du magenta. `Pyro-IA-explosion.None.png` est une planche horizontale 5 poses × 64 pixels ; son import moteur n'a pas été testé. C'est un effet d'impact radial, sans orientations différentes ; il ne couvre pas à lui seul le projectile et l'animation complète de la capacité.

`apercu-pyro-poses-ia.mp4` est une **maquette sans son**, créée en superposant ces images à une capture fixe du donjon. Elle ne représente pas une capture en jeu : ni timing, ni emplacement moteur, ni couches, ni fluidité n'ont été validés. Des poses intermédiaires et un test PMDO restent nécessaires. Références d'origine : [PMDCollab/RawAsset/Particle](https://github.com/PMDCollab/RawAsset/tree/0b88bbd7dec6f3373d5ec2b0f40bbdc3f44ce90c/Particle) et les fiches locales `fire_blast` / `flamethrower`.

Le travail est au stade Pyro seulement ; les 34 autres capacités n'ont pas été refaites avec cette méthode. Les prototypes précédents sont conservés.

## Essai natif suivant, avec son

Les cinq poses sélectionnées sont désormais testées comme impact radial PMDO à huit lignes identiques ; le projectile reste celui, orienté et créé par programme, de la V2. La vidéo `../../Pyro-Tourbillon-IA-8-directions-son-PMDO.mp4` montre le vrai banc en donjon, avec le son d'impact PMDO `DUN_Fire_Blast_2` ; huit cibles adjacentes, huit directions, dégâts et PP confirmés dans le journal correspondant. L'effet est au premier plan et peut masquer la cible. Les cinq poses restent à enrichir : ne pas confondre ce test avec une animation définitive fluide ou une capacité Z intégrée au menu. Cible et lancement par script, puissance 100, catégorie spéciale et PP 1 provisoires.

`apercu-pyro-poses-ia-avec-son.mp4` est la maquette précédente, sonorisée séparément avec le même effet sonore PMDO ; contrairement à la nouvelle capture en donjon, il s'agit d'un montage sur image fixe.
