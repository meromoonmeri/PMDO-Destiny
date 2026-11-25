# Pose « Moquerie » de la Team Dazzling

Sources SpriteCollab de la pose fixe utilisée lorsque Aria, Adagio et
Sonata se moquent du duo. Chaque feuille contient une seule frame de
30 ticks dans les huit directions.

Dans PMDO, cette animation Destiny est rangée sous l'action libre
`Special0` de `GFXParams.xml` (FrameType 82). L'<Index> 14 des fichiers
`AnimData.xml` est uniquement l'InternalIndex SpriteCollab conservé dans
le groupe du `.chara` ; ce n'est pas la clé moteur.

L'injection dans le payload normal des `.chara` se fait avec
`tools/ajouter_pose_chara.py`, par exemple :

```sh
python3 tools/ajouter_pose_chara.py \
  --chara game/Content/Chara/303.chara \
  --sprites art/sprites/team_dazzling_moquerie_v6/0303_Mawile \
  --anim Moquerie --frame-type 82 \
  --out /tmp/303.chara
```
