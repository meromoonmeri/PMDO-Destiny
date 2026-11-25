# Bekipan — distribution du courrier

Source SpriteCollab `0279/0001` : animation historique `Special0` de
Pelipper distribuant le courrier dans la boîte aux lettres (9 frames,
durées 20, 3, 1, 3, 14, 3, 1, 3, 20 ticks ; les huit lignes de direction
sont identiques, l'animation étant pensée de face).

Dans PMDO, elle est rangée sous l'action libre `Special0` de
`GFXParams.xml` (FrameType 82). L'<Index> 13 de `AnimData.xml` est
uniquement l'InternalIndex SpriteCollab conservé dans le groupe du
`.chara` ; ce n'est pas la clé moteur.

Injection dans le payload normal du `.chara` de base, puis copie du
résultat en override Destiny et ajout de l'espèce 279 à
`game/Content/Chara/index.idx` :

```sh
git show HEAD:base/Content/Chara/279.chara > /tmp/279.chara
python3 tools/ajouter_pose_chara.py \
  --chara /tmp/279.chara \
  --sprites art/sprites/pelipper_courrier/0279_Pelipper \
  --anim Special0 --frame-type 82 \
  --out game/Content/Chara/279.chara
```
