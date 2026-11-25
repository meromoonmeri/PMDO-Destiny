#!/usr/bin/env python3
"""Aperçu des émotes des dix membres de la Guilde de Réverie Town.

Génère deux artefacts autonomes (aucune ressource externe au chargement) :

  apercu_emotes_guilde.html        aperçu interactif (canvas, temps du jeu à 60 i/s)
  apercu_emotes_guilde_banc.png    banc-titre statique : attente, les 6 images de la
                                   bouchée, puis l'émote de sortie, membre par membre

Sources lues dans le dépôt :
  game/Data/Script/destiny/guilde_effectif.lua             effectif (via Lupa)
  game/Content/Particle/Emote_Eating.dir                   émote de repas du mod
  base/Content/Particle/Emote_{Happy,Notice,Glowing}.dir   émotes de sortie

Planches de personnages : SpriteCollab (PMDCollab, CC BY-NC-SA), téléchargées au
premier lancement dans le cache local puis réutilisées :

  python tools/apercu_emotes_guilde.py                # cache ~/.cache/spritecollab
  SPRITECOLLAB_CACHE=/chemin python tools/apercu_emotes_guilde.py
  python tools/apercu_emotes_guilde.py --sortie /dossier
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import os
import struct
import urllib.request
from pathlib import Path
from xml.etree import ElementTree

from lupa import LuaRuntime
from PIL import Image, ImageDraw, ImageFont

RACINE = Path(__file__).resolve().parents[1]
SPRITES = Path(os.environ.get('SPRITECOLLAB_CACHE', Path.home() / '.cache/spritecollab'))
HTML = Path.home() / 'apercu_emotes_guilde.html'
BANC = Path.home() / 'apercu_emotes_guilde_banc.png'

# Numéros nationaux des dix membres, pour SpriteCollab.
DEX = {
    'Gardevoir': '0282', 'Canarticho': '0083', 'Simisage': '0512', 'Melofee': '0035',
    'Cizayox': '0212', 'Noctali': '0197', 'Dimoret': '0461', 'Draby': '0371',
    'Pandespiegle': '0674', 'Capumain': '0190',
}
FICHIERS = ['AnimData.xml', 'Idle-Anim.png', 'Eat-Anim.png', 'Pose-Anim.png']
URL = 'https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/sprite/{}/{}'


def telecharger_planches() -> None:
    """Récupère les planches manquantes (Idle obligatoire, Eat/Pose facultatives)."""
    for membre, dex in DEX.items():
        dossier = SPRITES / membre
        dossier.mkdir(parents=True, exist_ok=True)
        for fichier in FICHIERS:
            cible = dossier / fichier
            if cible.exists() and cible.stat().st_size > 0:
                continue
            try:
                with urllib.request.urlopen(URL.format(dex, fichier), timeout=30) as reponse:
                    cible.write_bytes(reponse.read())
            except Exception:
                # Eat/Pose n'existent pas pour toutes les espèces : ce n'est pas
                # une erreur, le code du jeu prévoit exactement ce repli.
                pass

POLICE = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
POLICE_GRAS = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'

EMOTES = {
    'eating': ('game/Content/Particle/Emote_Eating.dir', 3, 10),
    'reveil': ('game/Content/Particle/Emote_Reveil.dir', 4, 10),
    'pose_infirmiere': ('game/Content/Particle/Emote_Pose_Infirmiere.dir', 12, 6),
    'happy': ('base/Content/Particle/Emote_Happy.dir', 10, 16),
    'notice': ('base/Content/Particle/Emote_Notice.dir', 1, 4),
    'glowing': ('base/Content/Particle/Emote_Glowing.dir', 2, 4),
    'exclaim': ('base/Content/Particle/Emote_Exclaim.dir', 4, 10),
}

# Bandes montrées sous le titre : les trois émotes du mod.
PLANCHES = ['eating', 'reveil', 'pose_infirmiere']


def b64_png(image: Image.Image) -> str:
    tampon = io.BytesIO()
    image.save(tampon, format='PNG')
    return 'data:image/png;base64,' + base64.b64encode(tampon.getvalue()).decode()


def lire_dir(relatif: str) -> dict:
    octets = (RACINE / relatif).read_bytes()
    (taille_png,) = struct.unpack('<q', octets[:8])
    planche = Image.open(io.BytesIO(octets[8:8 + taille_png])).convert('RGBA')
    largeur, hauteur, _dirs, images = struct.unpack('<iiii', octets[8 + taille_png:8 + taille_png + 16])
    return {'image': planche, 'largeur': largeur, 'hauteur': hauteur, 'images': images}


def animation_sprite(membre: str, nom: str, fichier_anim: str) -> dict | None:
    """Extrait la rangée « vers le bas » (rangée 0) d'une planche SpriteCollab."""
    png = SPRITES / membre / fichier_anim
    xml = SPRITES / membre / 'AnimData.xml'
    if not png.exists() or not xml.exists():
        return None
    arbre = ElementTree.parse(xml)
    anim = None
    for noeud in arbre.iter('Anim'):
        if (noeud.findtext('Name') or '').lower() == nom.lower():
            anim = noeud
            break
    if anim is None:
        return None
    largeur = int(anim.findtext('FrameWidth'))
    hauteur = int(anim.findtext('FrameHeight'))
    durees = [int(d.text) for d in anim.findall('Durations/Duration')]
    planche = Image.open(png).convert('RGBA')
    colonnes = planche.width // largeur
    rangee = planche.crop((0, 0, colonnes * largeur, hauteur))
    return {
        'largeur': largeur, 'hauteur': hauteur, 'images': colonnes,
        'durees': durees[:colonnes] or [6] * colonnes,
        'uri': b64_png(rangee),
    }


def effectif() -> list[dict]:
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(f"module_guilde = dofile('{(RACINE / 'game/Data/Script/destiny/guilde_effectif.lua').as_posix()}')")
    table = lua.globals().module_guilde.MEMBRES
    sortie = []
    for i in range(1, len(table) + 1):
        m = table[i]
        sortie.append({
            'id': m['id'], 'nom': m['nom'], 'espece': m['espece'], 'role': m['role'],
            'type': m['type'], 'genre': 'Féminin' if m['genre'] == 'f' else 'Masculin',
            'caractere': m['caractere'], 'cycles': int(m['cycles']), 'delai': int(m['delai']),
            'apres': m['apres'], 'pose': bool(m['pose']),
        })
    return sortie


def construire_donnees() -> dict:
    telecharger_planches()
    emotes = {}
    for nom, (relatif, frame_time, loc_height) in EMOTES.items():
        info = lire_dir(relatif)
        emotes[nom] = {
            'largeur': info['largeur'], 'hauteur': info['hauteur'], 'images': info['images'],
            'frameTime': frame_time, 'locHeight': loc_height,
            'uri': b64_png(info['image']),
        }

    membres = []
    for m in effectif():
        sprite = SPRITES / m['id']
        idle = animation_sprite(m['id'], 'Idle', 'Idle-Anim.png')
        if idle is None:
            raise SystemExit(f'planche Idle manquante pour {m["id"]}')
        m['idle'] = idle
        m['manger'] = animation_sprite(m['id'], 'Eat', 'Eat-Anim.png')
        m['pose_anim'] = animation_sprite(m['id'], 'Pose', 'Pose-Anim.png')
        m['sommeil'] = animation_sprite(m['id'], 'Sleep', 'Sleep-Anim.png')
        m['reveil_anim'] = animation_sprite(m['id'], 'Wake', 'Wake-Anim.png')
        # Mélofée garde sa pose de service : on la montre avec sa vraie planche
        # si elle existe, sinon avec son attente (repli du code Lua).
        membres.append(m)

    return {'emotes': emotes, 'membres': membres, 'planches': PLANCHES}


# --------------------------------------------------------------------------- #
#  HTML interactif                                                            #
# --------------------------------------------------------------------------- #
GABARIT = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aperçu des émotes — Guilde de Réverie Town</title>
<style>
  :root{
    --fond:#0f151b; --bande:#172029; --bande2:#1d2831; --trait:#2b3a46;
    --texte:#e8eef4; --doux:#8fa6b8; --accent:#7ed9b0; --or:#f0c470; --rose:#e08cbe;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--fond);color:var(--texte);
       font-family:"DejaVu Sans",system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
  header{padding:28px 32px 6px}
  h1{margin:0 0 6px;font-size:26px;letter-spacing:-.2px}
  .sous{color:var(--doux);font-size:14px;margin:0 0 18px;max-width:1100px;line-height:1.5}
  .barre{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:18px}
  button{background:var(--bande2);color:var(--texte);border:1px solid var(--trait);
         border-radius:8px;padding:8px 14px;font-size:14px;cursor:pointer;font-family:inherit}
  button:hover{border-color:var(--accent);color:var(--accent)}
  select{background:var(--bande2);color:var(--texte);border:1px solid var(--trait);
         border-radius:8px;padding:8px 10px;font-size:14px;font-family:inherit}
  .horloge{color:var(--doux);font-size:13px;font-variant-numeric:tabular-nums;
           background:var(--bande);border:1px solid var(--trait);border-radius:8px;padding:8px 12px}
  .grille{display:grid;grid-template-columns:repeat(auto-fill,minmax(232px,1fr));
          gap:16px;padding:0 32px 8px}
  .carte{background:var(--bande);border:1px solid var(--trait);border-radius:14px;
         padding:14px 14px 12px;display:flex;flex-direction:column;gap:10px}
  .entete{display:flex;justify-content:space-between;align-items:baseline;gap:8px}
  .nom{font-weight:700;font-size:16px}
  .role{color:var(--doux);font-size:11.5px;text-align:right;line-height:1.3}
  .scene{position:relative;background:radial-gradient(circle at 50% 62%,#22303b 0%,#161f27 70%);
         border-radius:10px;border:1px solid #23303a;overflow:hidden}
  canvas{display:block;width:100%;height:auto}
  .etat{position:absolute;left:8px;top:7px;font-size:11px;padding:3px 7px;border-radius:6px;
        background:rgba(11,17,22,.78);color:var(--accent);letter-spacing:.2px}
  .chips{display:flex;flex-wrap:wrap;gap:6px;font-size:11px;color:var(--doux)}
  .chip{border:1px solid var(--trait);border-radius:999px;padding:2px 8px;white-space:nowrap}
  .chip.or{color:var(--or);border-color:#4a3f24}
  .chip.rose{color:var(--rose);border-color:#4a2438}
  .chip.vert{color:var(--accent);border-color:#26473a}
  .caractere{font-size:11.5px;color:var(--doux);line-height:1.45;margin:0}
  .notes{margin:26px 32px 40px;padding:20px 22px;background:var(--bande);border:1px solid var(--trait);
         border-radius:14px;color:var(--doux);font-size:13.5px;line-height:1.6}
  .notes b{color:var(--texte)}
  .notes code{background:#0b1116;border:1px solid var(--trait);border-radius:5px;padding:1px 5px;
              font-size:12.5px;color:var(--accent)}
  .reveil{margin:6px 32px 20px;background:var(--bande);border:1px solid var(--trait);
          border-radius:14px;padding:16px 18px}
  .reveil h2{margin:0 0 4px;font-size:17px}
  .reveil .sous{margin:0 0 10px}
  .reveil canvas{display:block;width:100%;height:auto;background:radial-gradient(circle at 50% 70%,#22303b 0%,#161f27 72%);
                 border-radius:10px;border:1px solid #23303a}
  .planche{display:flex;gap:12px;flex-wrap:wrap;margin:0 32px 6px}
  .planche figure{margin:0;background:var(--bande);border:1px solid var(--trait);border-radius:12px;
                  padding:10px}
  .planche figcaption{color:var(--doux);font-size:11px;margin-top:6px;text-align:center}
  .planche img{display:block;image-rendering:pixelated}
</style>
</head>
<body>
<header>
  <h1>Aperçu des émotes — les dix membres de la Guilde</h1>
  <p class="sous">
    Chaque carte rejoue le repas tel que le jeu l'exécute : l'émote <b>eating</b> du mod
    (6 images × 3 images de durée = 18 images par bouchée, posée 10 px au-dessus du centre),
    le nombre de bouchées et le délai de départ propres au membre, puis son émote de sortie.
    Sprites et animations de corps : planches SpriteCollab (rangée « vers le bas »).
  </p>
  <div class="barre">
    <button id="pause">Pause</button>
    <button id="relancer">Relancer le repas</button>
    <label style="color:var(--doux);font-size:14px">Vitesse
      <select id="vitesse">
        <option value="0.25">0,25×</option>
        <option value="0.5">0,5×</option>
        <option value="1" selected>1× (temps du jeu)</option>
        <option value="2">2×</option>
      </select>
    </label>
    <span class="horloge" id="horloge">t = 0 image</span>
  </div>
  <p class="sous" style="margin:0 0 10px">
    Les trois premières images de l'émote ne montrent qu'une étincelle de 1 px : c'est
    l'asset d'origine, copié d'Halcyon. Les miettes n'apparaissent qu'aux images 4 à 6 —
    l'émote est donc discrète à l'écran, comme dans le jeu.
  </p>
</header>

<div class="planche" id="planche"></div>

<section class="reveil">
  <h2>Séquence de réveil — <code>guilde_reveil.Reveiller()</code></h2>
  <p class="sous">Mélofée prend la pose de service, fait sonner la cloche (2 cycles de 32 images),
  Draby passe de <b>Sleep</b> à <b>Wake</b>, puis le calot d'infirmière reprend sa place : la cloche
  et le calot ne peuvent pas se superposer, un personnage ne porte qu'une émote à la fois.</p>
  <canvas id="scene-reveil" width="1120" height="300"></canvas>
</section>

<section class="grille" id="grille"></section>

<section class="notes">
  <b>Trois choses à lire sur cet aperçu.</b><br>
  1. <b>La désynchronisation est réelle</b> : les dix convives ne démarrent pas ensemble.
  Draby attaque à 2 images, Simisage à 22 (il sert avant de s'asseoir). Cliquez sur
  « Relancer le repas » pour voir l'étagement.<br>
  2. <b>Le nombre de bouchées raconte le personnage</b> : Gardevoir, Canarticho et Mélofée
  mangent en continu ; Cizayox et Noctali prennent une seule bouchée ; Draby en engloutit trois.<br>
  3. <b>Hauteurs d'émote différentes</b> : <code>eating</code> flotte à 10 px, <code>happy</code> à 16 px,
  <code>notice</code> et <code>glowing</code> à 4 px — c'est la donnée de chaque émote, pas un choix d'affichage.<br><br>
  <b>Animations de corps.</b> Seuls Noctali, Draby et Capumain possèdent une animation
  <code>Eat</code> dans les planches SpriteCollab ; ailleurs le personnage garde son attente et seule
  l'émote joue — c'est exactement le repli du code (<code>GetReferencedAnimIndex</code>). Même logique
  pour <code>Pose</code> : Mélofée n'a pas de pose dédiée dans ces planches, son état de repos
  affiche donc son attente, et le code retombe sur <code>Pose</code> puis <code>Idle</code> en jeu.<br><br>
  <b>Crédits.</b> Émotes et logique : mod Destiny (émote <code>eating</code> calquée sur Halcyon).
  Sprites et animations de corps : <b>PMDCollab / SpriteCollab</b>, licence CC BY-NC-SA —
  aperçu local, usage non commercial.
</section>

<script>
const DONNEES = __DONNEES__;

const IMAGES = {};
function charger(uri){
  if(!IMAGES[uri]){
    const img = new Image();
    img.src = uri;
    IMAGES[uri] = img;
  }
  return IMAGES[uri];
}
for(const e of Object.values(DONNEES.emotes)) charger(e.uri);
for(const m of DONNEES.membres){
  charger(m.idle.uri);
  if(m.manger) charger(m.manger.uri);
  if(m.pose_anim) charger(m.pose_anim.uri);
  if(m.sommeil) charger(m.sommeil.uri);
  if(m.reveil_anim) charger(m.reveil_anim.uri);
}

const TICK = 1000/60;          // une image du jeu = 1/60 s
const REPOS = 42;              // images de répit avant de reprendre le repas
const ECHELLE = 2;

class Convive{
  constructor(donnees, index){
    this.d = donnees;
    this.canvas = null;
    this.ctx = null;
    this.reinitialiser();
  }
  reinitialiser(){
    this.t = 0;
    this.phase = 'attente';
    this.phaseT = 0;
    this.bouchee = 0;
    this.etat = 'attend ' + this.d.delai + ' img';
  }
  get continu(){ return this.d.cycles === 0; }
  get dureeBouchee(){ return DONNEES.emotes.eating.images * DONNEES.emotes.eating.frameTime; }

  avancer(){
    this.t += 1; this.phaseT += 1;
    const e = DONNEES.emotes;

    if(this.phase === 'attente'){
      if(this.phaseT >= this.d.delai){ this.phase = 'repas'; this.phaseT = 0; this.bouchee = 0; }
      this.etat = 'attend ' + Math.max(0, this.d.delai - this.phaseT) + ' img';
      return;
    }
    if(this.phase === 'repas'){
      const totale = this.continu ? Infinity : this.d.cycles * this.dureeBouchee;
      this.bouchee = Math.min(this.d.cycles || 0, Math.floor(this.phaseT / this.dureeBouchee) + 1);
      this.etat = this.continu ? 'repas continu' : 'bouchée ' + this.bouchee + '/' + this.d.cycles;
      if(!this.continu && this.phaseT >= totale){
        if(this.d.apres){ this.phase = 'sortie'; this.phaseT = 0; this.etat = this.d.apres; }
        else { this.phase = 'repos'; this.phaseT = 0; this.etat = this.d.pose ? 'pose de service' : 'au repos'; }
      }
      return;
    }
    if(this.phase === 'sortie'){
      const em = e[this.d.apres];
      const duree = em.images * em.frameTime;
      this.etat = this.d.apres;
      if(this.phaseT >= duree){
        this.phase = 'repos'; this.phaseT = 0;
        this.etat = this.d.pose ? 'pose de service' : 'au repos';
      }
      return;
    }
    if(this.phase === 'repos'){
      this.etat = this.d.pose ? 'pose de service' : 'au repos';
      if(this.phaseT >= REPOS){ this.phase = 'repas'; this.phaseT = 0; this.bouchee = 0; }
    }
  }

  // --- dessin -------------------------------------------------------------
  dessinerScene(){
    const ctx = this.ctx, L = this.canvas.width, H = this.canvas.height;
    ctx.clearRect(0,0,L,H);
    // sol
    ctx.strokeStyle = 'rgba(126,217,176,.16)';
    ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(18, H-28); ctx.lineTo(L-18, H-28); ctx.stroke();

    const idle = this.d.idle;
    const solY = H - 26;
    const cx = L/2;

    // cadre du sprite : centre du personnage
    let anim = idle, tAnim = this.t;
    if((this.phase === 'repas' || this.phase === 'sortie') && this.d.manger){
      anim = this.d.manger;
      tAnim = this.phaseT;
    } else if(this.phase === 'repos' && this.d.pose && this.d.pose_anim){
      anim = this.d.pose_anim;
      tAnim = this.phaseT;
    }
    const index = this.imageDe(anim, tAnim);
    const lw = anim.largeur * ECHELLE, lh = anim.hauteur * ECHELLE;
    const spriteX = cx - lw/2, spriteY = solY - lh;
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(charger(anim.uri), index*anim.largeur, 0, anim.largeur, anim.hauteur,
                  spriteX, spriteY, lw, lh);

    // émote
    let emote = null, tEmote = 0;
    if(this.phase === 'repas'){ emote = DONNEES.emotes.eating; tEmote = this.phaseT; }
    else if(this.phase === 'sortie'){ emote = DONNEES.emotes[this.d.apres]; tEmote = this.phaseT; }
    else if(this.phase === 'repos' && this.d.pose){
      // Pose de service : le calot reste posé tant qu'elle est de garde.
      emote = DONNEES.emotes.pose_infirmiere; tEmote = this.phaseT;
    }

    if(emote){
      const i = Math.floor(tEmote / emote.frameTime) % emote.images;
      const ew = emote.largeur * ECHELLE, eh = emote.hauteur * ECHELLE;
      // Le moteur ancre l'émote sur le point « tête » de la planche, puis la
      // remonte de LocHeight (GroundChar.Draw : ActionPointType.Head).
      const tete = spriteY + lh * 0.30;
      const centreY = tete - emote.locHeight * ECHELLE;
      ctx.drawImage(charger(emote.uri), i*emote.largeur, 0, emote.largeur, emote.hauteur,
                    cx - ew/2, centreY - eh/2, ew, eh);
    }
  }

  imageDe(anim, t){
    if(!anim.durees || !anim.durees.length) return 0;
    const total = anim.durees.reduce((a,b)=>a+b,0);
    let r = t % total;
    for(let i=0;i<anim.durees.length;i++){
      if(r < anim.durees[i]) return i;
      r -= anim.durees[i];
    }
    return 0;
  }
}

const convives = [];
const grille = document.getElementById('grille');
DONNEES.membres.forEach((m, i) => {
  const carte = document.createElement('article');
  carte.className = 'carte';
  const anims = [];
  if(m.manger) anims.push('Eat');
  if(m.pose_anim) anims.push('Pose');
  carte.innerHTML = `
    <div class="entete"><span class="nom">${m.nom}</span><span class="role">${m.role}</span></div>
    <div class="scene"><canvas width="200" height="176"></canvas><span class="etat"></span></div>
    <div class="chips">
      <span class="chip">${m.type}</span>
      <span class="chip">${m.genre}</span>
      <span class="chip ${m.cycles===0?'or':''}">${m.cycles===0?'continu':m.cycles+' bouchée'+(m.cycles>1?'s':'')}</span>
      <span class="chip">délai ${m.delai} img</span>
      ${m.apres?`<span class="chip vert">sortie ${m.apres}</span>`:''}
      ${m.pose?`<span class="chip rose">pose de service</span>`:''}
    </div>
    <p class="caractere">${m.caractere}</p>
  `;
  grille.appendChild(carte);

  const convive = new Convive(m, i);
  convive.canvas = carte.querySelector('canvas');
  convive.ctx = convive.canvas.getContext('2d');
  convive.champEtat = carte.querySelector('.etat');
  convives.push(convive);
});

// --- scène de réveil -------------------------------------------------------
class SceneReveil{
  constructor(){
    this.melofee = DONNEES.membres.find(m => m.id === 'Melofee');
    this.dormeur = DONNEES.membres.find(m => m.id === 'Draby');
    this.canvas = document.getElementById('scene-reveil');
    this.ctx = this.canvas.getContext('2d');
    this.reinitialiser();
  }
  reinitialiser(){ this.t = 0; this.phase = 'sommeil'; this.phaseT = 0; this.etat = 'sommeil'; }
  avancer(){
    this.t += 1; this.phaseT += 1;
    if(this.phase === 'sommeil'){
      this.etat = 'Draby dort · Mélofée veille';
      if(this.phaseT >= 60){ this.phase = 'cloche'; this.phaseT = 0; }
    } else if(this.phase === 'cloche'){
      this.etat = 'la cloche sonne (2 cycles)';
      if(this.phaseT >= 64){ this.phase = 'reveil'; this.phaseT = 0; }
    } else if(this.phase === 'reveil'){
      this.etat = 'Draby se réveille';
      if(this.phaseT >= 48){ this.phase = 'service'; this.phaseT = 0; }
    } else {
      this.etat = 'reprise du service';
      if(this.phaseT >= 90){ this.reinitialiser(); }
    }
  }
  image(anim, t){
    if(!anim || !anim.durees || !anim.durees.length) return 0;
    const total = anim.durees.reduce((a,b)=>a+b,0);
    let r = t % total;
    for(let i=0;i<anim.durees.length;i++){ if(r < anim.durees[i]) return i; r -= anim.durees[i]; }
    return 0;
  }
  personnage(anim, index, cx, sol, emote, emoteIndex, echelle){
    const ctx = this.ctx;
    const lw = anim.largeur*echelle, lh = anim.hauteur*echelle;
    const x = cx - lw/2, y = sol - lh;
    ctx.drawImage(charger(anim.uri), index*anim.largeur, 0, anim.largeur, anim.hauteur, x, y, lw, lh);
    if(emote){
      const ew = emote.largeur*echelle, eh = emote.hauteur*echelle;
      const tete = y + lh*0.30;
      ctx.drawImage(charger(emote.uri), emoteIndex*emote.largeur, 0, emote.largeur, emote.hauteur,
                    cx - ew/2, tete - emote.locHeight*echelle - eh/2, ew, eh);
    }
  }
  dessiner(){
    const ctx = this.ctx, L = this.canvas.width, H = this.canvas.height, E = 4;
    ctx.clearRect(0,0,L,H);
    const sol = H - 62;
    ctx.strokeStyle = 'rgba(126,217,176,.20)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(40, sol); ctx.lineTo(L-40, sol); ctx.stroke();
    ctx.imageSmoothingEnabled = false;

    // Mélofée : pose de service, cloche pendant l'appel
    const e = DONNEES.emotes;
    const mel = this.melofee;
    const animMel = (mel.pose_anim && this.phase !== 'sommeil') ? mel.pose_anim : mel.idle;
    const cloche = e.reveil;
    const enCloche = this.phase === 'cloche' || this.phase === 'reveil';
    const emoteMel = enCloche ? cloche : (this.phase === 'service' || this.phase === 'sommeil' ? e.pose_infirmiere : null);
    const tEmote = enCloche ? this.phaseT + (this.phase === 'reveil' ? 64 : 0) : this.phaseT;
    this.personnage(animMel, this.image(animMel, this.t),
                    L*0.33, sol,
                    emoteMel, emoteMel ? Math.floor(tEmote / emoteMel.frameTime) % emoteMel.images : 0, E);
    ctx.fillStyle = '#8fa6b8'; ctx.font = '13px "DejaVu Sans",system-ui'; ctx.textAlign = 'center';
    ctx.fillText(mel.nom + ' — pose de service', L*0.33, sol + 30);

    // Draby : sommeil, réveil, debout
    const dr = this.dormeur;
    let animDr = dr.idle, tAnim = this.t, emoteDr = null, tEmoteDr = 0;
    if(this.phase === 'sommeil' && dr.sommeil){ animDr = dr.sommeil; }
    else if(this.phase === 'cloche' && dr.sommeil){ animDr = dr.sommeil; }
    else if(this.phase === 'reveil'){
      if(dr.reveil_anim){ animDr = dr.reveil_anim; tAnim = this.phaseT; }
      else { emoteDr = e.exclaim; tEmoteDr = this.phaseT; }
    }
    this.personnage(animDr, this.image(animDr, tAnim), L*0.66, sol,
                    emoteDr, emoteDr ? Math.floor(tEmoteDr / emoteDr.frameTime) % emoteDr.images : 0, E);
    ctx.fillText(dr.nom + ' — ' + (this.phase === 'sommeil' || this.phase === 'cloche' ? 'endormi' :
                 this.phase === 'reveil' ? 'se réveille' : 'debout'), L*0.66, sol + 30);

    ctx.textAlign = 'left';
    ctx.fillStyle = '#7ed9b0'; ctx.font = 'bold 14px "DejaVu Sans",system-ui';
    ctx.fillText('t = ' + this.t + ' images · ' + this.etat, 20, 28);
  }
}

// bande des 6 images de l'émote de repas
const planche = document.getElementById('planche');
for(const nom of DONNEES.planches){
  const em = DONNEES.emotes[nom];
  const titre = document.createElement('div');
  titre.style.cssText = 'flex-basis:100%;color:#8fa6b8;font-size:12px;margin:6px 0 -2px';
  titre.textContent = nom + ' — ' + em.images + ' images · FrameTime ' + em.frameTime +
                      ' · LocHeight ' + em.locHeight;
  planche.appendChild(titre);
  for(let i=0;i<em.images;i++){
    const fig = document.createElement('figure');
    const c = document.createElement('canvas');
    c.width = em.largeur*4; c.height = em.hauteur*4;
    const ctx = c.getContext('2d');
    ctx.imageSmoothingEnabled = false;
    const img = charger(em.uri);
    const dessiner = () => {
      ctx.clearRect(0,0,c.width,c.height);
      ctx.fillStyle = '#22303b'; ctx.fillRect(0,0,c.width,c.height);
      ctx.drawImage(img, i*em.largeur, 0, em.largeur, em.hauteur, 0,0,c.width,c.height);
    };
    img.complete ? dessiner() : img.addEventListener('load', dessiner);
    fig.appendChild(c);
    const leg = document.createElement('figcaption');
    leg.textContent = 'image ' + (i+1) + ' · t=' + (i*em.frameTime) + '→' + ((i+1)*em.frameTime);
    fig.appendChild(leg);
    planche.appendChild(fig);
  }
}

const sceneReveil = new SceneReveil();

// --- boucle ---------------------------------------------------------------
let enPause = false, vitesse = 1, accumulation = 0, dernier = performance.now(), images = 0;
const btnPause = document.getElementById('pause');
const btnRelancer = document.getElementById('relancer');
const selecteur = document.getElementById('vitesse');
const horloge = document.getElementById('horloge');

btnPause.addEventListener('click', () => {
  enPause = !enPause;
  btnPause.textContent = enPause ? 'Reprendre' : 'Pause';
});
btnRelancer.addEventListener('click', () => {
  images = 0;
  convives.forEach(c => c.reinitialiser());
});
selecteur.addEventListener('change', () => { vitesse = parseFloat(selecteur.value); });

function boucle(maintenant){
  const ecoule = maintenant - dernier;
  dernier = maintenant;
  if(!enPause){
    accumulation += ecoule * vitesse;
    while(accumulation >= TICK){
      convives.forEach(c => c.avancer());
      sceneReveil.avancer();
      images += 1;
      accumulation -= TICK;
    }
    convives.forEach(c => { c.dessinerScene(); c.champEtat.textContent = c.etat; });
    sceneReveil.dessiner();
    horloge.textContent = 't = ' + images + ' image' + (images>1?'s':'') + ' · ' + (images/60).toFixed(1) + ' s';
  }
  requestAnimationFrame(boucle);
}
convives.forEach(c => c.dessinerScene());
sceneReveil.dessiner();
requestAnimationFrame(boucle);
</script>
</body>
</html>
"""


def ecrire_html(donnees: dict) -> None:
    charge = json.dumps(donnees, ensure_ascii=False)
    HTML.write_text(GABARIT.replace('__DONNEES__', charge), encoding='utf-8')


# --------------------------------------------------------------------------- #
#  Banc-titre statique de contrôle                                            #
# --------------------------------------------------------------------------- #
def ecrire_banc(donnees: dict) -> None:
    """Une ligne par membre : attente, les 6 images de la bouchée, puis la sortie."""
    emotes = donnees['emotes']
    marge_g, marge_d = 300, 32
    haut, LIGNE_H, CELL = 152, 130, 96
    COLONNES = 10  # 0 = attente, 1..6 = bouchée, 7..9 = sortie
    L = marge_g + COLONNES * (CELL + 8) + marge_d
    H = haut + len(donnees['membres']) * LIGNE_H + 76
    img = Image.new('RGB', (L, H), (15, 21, 27))
    d = ImageDraw.Draw(img)
    fonte_titre = ImageFont.truetype(POLICE_GRAS, 26)
    fonte = ImageFont.truetype(POLICE, 14)
    fonte_petite = ImageFont.truetype(POLICE, 12)
    fonte_gras = ImageFont.truetype(POLICE_GRAS, 15)

    cache: dict[str, Image.Image] = {}

    def planche_de(uri: str) -> Image.Image:
        if uri not in cache:
            cache[uri] = Image.open(io.BytesIO(base64.b64decode(uri.split(',')[1]))).convert('RGBA')
        return cache[uri]

    def cellule(x: int, y: int, anim: dict, index_anim: int,
                emote_nom: str | None, index_emote: int, hauteur_cellule: int = CELL) -> None:
        d.rounded_rectangle((x, y, x + CELL, y + hauteur_cellule), radius=8, fill=(34, 48, 59),
                            outline=(46, 62, 76))
        planche = planche_de(anim['uri'])
        case = planche.crop((index_anim * anim['largeur'], 0,
                             (index_anim + 1) * anim['largeur'], anim['hauteur']))
        facteur = min(58 / case.width, 62 / case.height, 2.0)
        case = case.resize((max(1, int(case.width * facteur)), max(1, int(case.height * facteur))),
                           Image.NEAREST)
        sol = y + hauteur_cellule - 16
        cx = x + CELL // 2
        img.paste(case, (cx - case.width // 2, sol - case.height), case)
        if emote_nom:
            em = emotes[emote_nom]
            ep = planche_de(em['uri'])
            ec = ep.crop((index_emote * em['largeur'], 0,
                          (index_emote + 1) * em['largeur'], em['hauteur']))
            ech = 1.6
            ec = ec.resize((int(ec.width * ech), int(ec.height * ech)), Image.NEAREST)
            centre = (sol - case.height) + case.height // 2 - int(em['locHeight'] * ech) - 6
            img.paste(ec, (cx - ec.width // 2, centre - ec.height // 2), ec)

    d.text((40, 32), "Aperçu des émotes — Guilde de Réverie Town", font=fonte_titre, fill=(232, 238, 244))
    d.text((40, 70),
           "une ligne par membre : attente · les 6 images de la bouchée (18 images de jeu) · émote de sortie",
           font=fonte, fill=(143, 166, 184))

    titres = ['attente'] + [f'bouchée {i + 1}/6' for i in range(6)] + ['sortie 1', 'sortie 2', 'sortie 3']
    for i, titre in enumerate(titres):
        x = marge_g + i * (CELL + 8)
        couleur = (126, 217, 176) if 1 <= i <= 6 else (143, 166, 184)
        d.text((x + 2, haut - 26), titre, font=fonte_petite, fill=couleur)

    for ligne, m in enumerate(donnees['membres']):
        y = haut + ligne * LIGNE_H
        if ligne % 2 == 0:
            d.rounded_rectangle((16, y + 6, L - 16, y + LIGNE_H - 6), radius=10, fill=(23, 32, 41))
        d.text((40, y + 18), m['nom'], font=fonte_gras, fill=(232, 238, 244))
        d.text((40, y + 40), m['role'][:34], font=fonte_petite, fill=(143, 166, 184))
        second = ('repas continu' if m['cycles'] == 0 else f"{m['cycles']} bouchée" + ('s' if m['cycles'] > 1 else '')) \
                 + f" · délai {m['delai']} img"
        d.text((40, y + 60), second, font=fonte_petite,
               fill=(240, 196, 112) if m['cycles'] == 0 else (200, 216, 228))
        if m['apres']:
            d.text((40, y + 78), 'sortie ' + m['apres'], font=fonte_petite, fill=(126, 217, 176))
        if m['pose']:
            d.text((40, y + 96), 'pose de service', font=fonte_petite, fill=(224, 140, 190))

        y_cellule = y + 10
        cellule(marge_g, y_cellule, m['idle'], 0, None, 0)
        anim = m['manger'] or m['idle']
        for i in range(6):
            cellule(marge_g + (1 + i) * (CELL + 8), y_cellule,
                    anim, i % anim['images'], 'eating', i)
        if m['apres']:
            for i in range(3):
                cellule(marge_g + (7 + i) * (CELL + 8), y_cellule,
                        m['idle'], 0, m['apres'], i % emotes[m['apres']]['images'])
        else:
            d.text((marge_g + 7 * (CELL + 8) + 26, y + LIGNE_H // 2 - 6), '—',
                   font=fonte, fill=(110, 128, 142))

    d.text((40, H - 46),
           "Émote de repas : 6 images × 3 = 18 images par bouchée, posée 10 px au-dessus du centre du personnage. "
           "SpriteCollab pour les planches ; Eat uniquement Noctali, Draby, Capumain.",
           font=fonte_petite, fill=(143, 166, 184))
    img.save(BANC)
    print(BANC, img.size)


def main() -> None:
    global HTML, BANC
    analyseur = argparse.ArgumentParser(description=__doc__)
    analyseur.add_argument('--sortie', type=Path, default=None,
                           help='dossier de destination (défaut : dossier personnel)')
    arguments = analyseur.parse_args()
    if arguments.sortie is not None:
        arguments.sortie.mkdir(parents=True, exist_ok=True)
        HTML = arguments.sortie / HTML.name
        BANC = arguments.sortie / BANC.name
    donnees = construire_donnees()
    ecrire_html(donnees)
    print(HTML)
    ecrire_banc(donnees)


if __name__ == '__main__':
    main()
