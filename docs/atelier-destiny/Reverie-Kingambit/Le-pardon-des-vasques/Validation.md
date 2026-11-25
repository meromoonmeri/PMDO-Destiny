# Le pardon des vasques

**[Cinématique complète en jeu — 39,07 s, avec le son natif](Le-pardon-des-vasques.mp4)**. La prise va du fondu d’après-duel au fondu des retrouvailles, sans coupe ni accélération. Les boîtes restent confirmées par le joueur : la durée inclut une lecture à rythme normal.

| Repère | Action |
|---|---|
| Ouverture | Dès le fondu, Kabutops est au milieu, entre le partenaire et le héros. Il reconnaît avoir accusé Nilo sans savoir. |
| 5,1 s | Il regarde vers les vasques et se souvient des familles qui venaient boire et des petits qui couraient sur le sable. Le thème de la grotte revient. |
| 15,3 s | Il présente ses excuses, à Nilo puis aux deux Pokémon venus le chercher. Nilo cesse de trembler, mais attend le départ de la garde avant de descendre. |
| 27–29,3 s | Les quatre Kabuto libèrent le passage par Tunnel, l’arrière d’abord, puis les flancs. Leur chef s’enfouit au centre et part le dernier. |
| 32–39,1 s | Nilo retrouve Lyra. Deux répliques, puis le fondu et le bilan de l’expédition. |

## Dialogues

- **Kabutops :** « Je me suis emporté trop vite. J’ai accusé Nilo sans savoir. »
- **Kabutops :** « Avant, on venait boire ici en famille. Les petits faisaient la course sur le sable. »
- **Kabutops :** « Depuis les crues, le moindre éclair m’effraie. Ce n’est pas une excuse. »
- **Kabutops :** « Pardon, Nilo. Et pardon à vous deux de vous avoir attaqués. »
- **Nilo :** « Alors… je peux rentrer avec maman ? »
- **Kabutops :** « Oui. Kabuto, laissez-leur le passage. »
- **Nilo, devant Lyra :** « Maman ! J’ai eu si peur… »
- **Lyra :** « Tu es là. C’est tout ce qui compte. »

## Vérification dans PMDO

- Le [K.O. du chef seul](Preuves/Chef-KO-garde-encore-la.png) ne déclenche rien. Le dénouement commence après le cinquième K.O. Les ombres restent alignées et les portraits ne recouvrent ni Nilo ni le trio. [Souvenir](Preuves/Souvenir-des-vasques.png) · [Excuses](Preuves/Pardon-a-Nilo-et-au-duo.png) · [Dernier Tunnel](Preuves/Le-dernier-Tunnel.png).
- Les [retrouvailles](Preuves/Nilo-retrouve-Lyra.png), le [bilan natif](Preuves/Bilan-natif.png), la sauvegarde et le dialogue de retour à Réverie ont été vérifiés. Des ressources du hub restent indisponibles dans le profil réduit ; ce n’est pas un contrôle visuel complet de la ville. [Trace](Preuves/Trace-victoire-et-dialogues.txt) · [Journal du moteur](Preuves/Journal-retour.txt).
- [Chronométrage](Preuves/Chronometrage.txt) · [Audio natif](Preuves/Audio-natif.txt) · [Tests Lua/Python et audits](Preuves/Tests-locaux.txt). Revanche déclenchée dans un profil de validation (duo niveau 50, Kabutops à 1 PV, les quatre Kabuto inchangés). Les sondes, sauvegardes et ressources de ce profil ne sont pas livrées. La carte, les positions d’arène et les surgissements précédents dans le sable n’ont pas été modifiés.

## Intégration locale

- Commit `920e5d51e4415fd1be9fa2b0279bf518c8891a5b`, sur `wip/reverie-integration-kingambit-cafe`.
- [Patch de cette scène](Le-pardon-des-vasques.patch), vérifié sur la base `24be5673a76e06a9824102c5f106f091eb07070a` (corrections sable et formation).
- [Bundle complet du chantier](Destiny-v0.7.6-Pardon.bundle) depuis la base publique `37138a7ca93be920e9c47963fea21441b153ec65` ; il contient également le lot précédent. [Contrôle d’import](Preuves/Integration.txt) · [Notes 0.7.6 actualisées](Notes-v0.7.6.md) · [SHA-256](SHA256SUMS.txt).

Cette scène est intégrée au candidat local. Aucun push, build Windows distant ni publication n’a été effectué pour ce commit.
