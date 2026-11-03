# Team Dazzling — Pose V2

Sources SpriteCollab de l'animation `Pose` (index moteur 13) intégrée aux
`.chara` de Destiny.

| Membre | Dossier | Cellule | Durées (ticks 1/60 s) |
|---|---|---:|---|
| Aria / Mawile | `0303_Mawile/` | 56×56 | 4, 1, 2, 4, 2, 1, 2 |
| Sonata / Lopunny | `0428_Lopunny/` | 40×56 | 4, 3, 3, 6 |
| Adagio / Tsareena | `0763_Tsareena/` | 40×56 | 4, 4, 6 |

Chaque dossier conserve `AnimData.xml` et le trio `Pose-Anim.png`,
`Pose-Shadow.png`, `Pose-Offsets.png` en huit directions. Les autres
animations des feuilles SpriteCollab d'origine ne sont pas redupliquées ici.

L'injection dans le payload normal des conteneurs PMDO est reproductible
avec `tools/ajouter_pose_chara.py`. Elle préserve les formes et les autres
animations déjà présentes. En cinématique, les poses sont entourées des
petites étoiles PMDO `Lucky_Chant_Star_Yellow`.
