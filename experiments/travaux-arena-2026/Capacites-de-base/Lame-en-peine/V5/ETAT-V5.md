# Lame en Peine V5 — prototype à valider

## Ce qui a changé
Aucune distorsion ni réfraction du décor. Le banc utilise la DLL RogueEssence d'origine, identique au binaire extrait (SHA-256 `694cb88ef49aaea3155c8ac0bf34c7448429f42236592cd50227056264d0ec88`) ; ni crochet PliSpatial, ni appel de cet effet.

Seize slashs, chacun accompagné de sa rémanence, dessinent un prisme filaire effilé en volume : le générateur calcule des coordonnées tridimensionnelles, les oriente suivant les huit directions du lanceur et les projette en perspective en images PMD. Les traits pulsent ensemble puis leurs propres segments éclatent brusquement ; six feux follets apparaissent ensuite et convergent vers le lanceur. Les images se suivent au sein d'une seule animation. Un son de brisure est déclenché au début de la rupture.

Il s'agit d'une projection 3D précalculée dans des sprites 2D, pas d'objets réellement tridimensionnels dans le moteur PMD. La lisibilité du volume varie selon l'angle. La rupture fragmente les traits et non le décor, lequel ne subit aucune altération. Les slashs sont visuels : ils n'infligent pas seize dégâts distincts.

## Vérifications
Capture de banc dans une copie isolée : les huit directions ont atteint FIN OK. Les cibles passent de 202 à 31–45 PV, les témoins restent à 202, le soin est égal à la moitié des dégâts arrondie vers le bas, et les PP passent de 10 à 9. Les images ont été examinées sur les étapes de construction, pulsation et rupture ainsi qu'une direction diagonale ; la convergence visuelle des feux dans les huit directions n'a pas été vérifiée image par image. Le son enregistré est non silencieux, mais chaque bruitage n'a pas été isolé auditivement. Le script de test et les originaux ont été restaurés après capture, comparaison effectuée.

La fiche originale n'est pas publiée et ne comporte pas le soin, ajouté pour ce banc. L'animation précède la résolution et peut donc se jouer aussi sur une attaque ratée : non testé. Immunités, interruption et autres situations de jeu restent à tester ; aucune intégration définitive.

## Vidéo
`Malvalame-Lame-en-Peine-V5-60ips-son.mp4` : 51 s, 640 × 480, H.264 60 ips et AAC non silencieux. Galerie `bitter_blade_base_v5`. Le téléchargement depuis le cadre d'aperçu reste non confirmé et peut être bloqué par son sandbox.
