#!/usr/bin/env python3
"""Hall réel → touche d'interaction Kaito → menus natifs → trappe et étage 1.
Seuls le point de départ et les repères/journaux sont imposés en QA. Aucune
case, sprite, carte, trajectoire ni étape du mécanisme ne sont simulés.
"""
from __future__ import annotations
import argparse,json,os,struct
from pathlib import Path
from filmer_cinematiques import qa, D, S, ORIGIN, ADD, MARK, rajouter, blob, capter, marque, remplacer

START='''local q={}
function q.Enter(map)
  if q.started then return end
  q.started=true
  GAME:FadeIn(1)
  local team=_DATA.Save.ActiveTeam
  GAME:SetTeamLeaderIndex(0)
  local n=$N
  while team.Players.Count>n do GAME:RemovePlayerTeam(team.Players.Count-1) end
  if team.Players.Count<n then
    local id=RogueEssence.Dungeon.MonsterID('riolu',0,'normal',Gender.Male)
    GAME:AddPlayerTeam(team:CreatePlayer(_DATA.Save.Rand,id,17,'',0))
  end
  assert(team.Players.Count==n)
  LTBL(team.Players[0]).Importance='Hero'
  if n==2 then LTBL(team.Players[1]).Importance='Partner' end
  if $INVERSE then GAME:SetTeamLeaderIndex(1) end
  GAME:EnterZone('town02_waterfallvillage',-1,17,3)
end
q.GameLoad=q.Enter
return q
'''


def script(c,rel,s=None):
    p=c/ORIGIN/rel;p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text((s if s is not None else blob(ADD/rel).decode('utf-8')).replace("'destiny.","'origin."),encoding='utf-8')
    return p


def installer(c,lot,row,mode):
    rajouter(c,lot)
    for p in ('dojo_kingambit_types.lua','dojo_kingambit_sceau.lua','suivi_interieurs.lua','equipe_scene.lua','zone/dojo_kingambit_dedales/init.lua'):
        script(c,Path(p))
    if not (c/'Data/Script/origin/zone/town02_waterfallvillage/init.lua').exists():
        script(c,Path('zone/town02_waterfallvillage/init.lua'),'return {}\n')
    hall='Data/Ground/dojo_kingambit.rsground'
    zone='Data/Zone/town02_waterfallvillage.json'
    for p in ('Content/Tile/Kingambit_Accueil_Natif.tile',hall,zone):
        (c/p).write_bytes(blob(Path('game')/p))
    banks=c/'Content/Tile'; paths=sorted(banks.glob('*.tile'))
    data=bytearray(struct.pack('<i',len(paths)))
    for p in paths:
        key=p.stem.encode('utf-8');assert len(key)<128
        with p.open('rb') as f:
            head=f.read(8);_,entries=struct.unpack('<ii',head)
            data+=bytes([len(key)])+key+head+f.read(entries*16)
    (banks/'index.idx').write_bytes(data)
    idx=c/'Data/Zone/index.idx';doc=json.loads(idx.read_text());j=doc['Object']
    z=json.loads((c/zone).read_bytes())['Object']
    j['town02_waterfallvillage']={**j['dojo_kingambit_dedales'],'Grounds':z['GroundMaps'],'Maps':[],
        'CountedFloors':0,'Name':z['Name'],'SortOrder':303}
    idx.write_text(json.dumps(doc,ensure_ascii=False),encoding='utf-8')
    k=row['id']; n=1 if mode=='solo' else 2
    for x in ('Sol','Rebord'):
        p=Path('Content/Particle')/f'Kingambit_Trappe_{k}_{x}.dir';(c/p).write_bytes(blob(Path('game')/p))
    (c/qa.START_REL).write_text(START.replace('$N',str(n)).replace('$INVERSE','true' if mode=='inverse' else 'false'),encoding='utf-8')
    f=Path('ground/dojo_kingambit/init.lua');s=blob(ADD/f).decode('utf-8')
    s=remplacer(s,'return dojo_kingambit\n','''local entre=dojo_kingambit.Enter
function dojo_kingambit.Enter(map)
  -- Placement QA, adjacent au personnage ; l'événement d'action est réel.
  GROUND:TeleportTo(CH('PLAYER'),376,200,Direction.Up)
  entre(map)
  assert(CH('Kingambit').Position.X==376 and CH('Kingambit').Position.Y==184)
  PrintInfo('KINGAMBIT_SCENE INTERACTION')
end
return dojo_kingambit
''')
    script(c,f,s)
    f=c/ORIGIN/'dojo_kingambit_entrainement.lua';s=f.read_text(encoding='utf-8')
    s=remplacer(s,"  UI:BeginMultiPageMenu(","  "+marque('CHOIX')+"\n  UI:BeginMultiPageMenu(")
    s=remplacer(s,"  UI:BeginChoiceMenu(","  "+marque('CONFIRMER')+"\n  UI:BeginChoiceMenu(")
    s=remplacer(s,"  return ok and i-1 or nil", "  PrintInfo('KINGAMBIT_SCENE CONFIRMER_FIN ok='..tostring(ok))\n  return ok and i-1 or nil")
    s=remplacer(s,"  local kaito = maitre.Position", "  assert(segment=="+str(row['slot'])+")\n  local kaito = maitre.Position")
    s=remplacer(s,"  mecanisme.Jouer(t[1], participants, sceau.X, sceau.Y)",'''  assert(#participants=='''+str(n)+''')
  for i,c in ipairs(participants) do assert(c.Position.Y==258 and c.Position.X==(i==1 and '''+str(376 if n==1 else 388 if mode=='inverse' else 364)+''' or '''+str(364 if mode=='inverse' else 388)+''')) end
  local ombres={}
  for i,c in ipairs(participants) do ombres[i]=c.HideShadow end
  mecanisme.Jouer(t[1], participants, sceau.X, sceau.Y)
  assert(maitre.Position.X==376 and maitre.Position.Y==184 and maitre.LocHeight==0)
  assert(GAME:IsCameraOnChar())
  for i,c in ipairs(participants) do assert(c.LocHeight==0 and c.HideShadow==ombres[i]) end
  PrintInfo('KINGAMBIT_SCENE RESTAURE acteurs='..#participants..' Kaito=immobile')
''')
    f.write_text(s,encoding='utf-8')
    f=c/ORIGIN/'dojo_kingambit_mecanisme.lua';s=f.read_text(encoding='utf-8')
    for match,token in [("  lancer(pref..'Sol',f,c.DrawLayer.Bottom,x,y)",'MECANISME'),
                       ("    SOUND:PlayBattleSE('EVT_Chest_Click')",'PENE_GAUCHE'),
                       ("    SOUND:PlayBattleSE('_UNK_DUN_Clank')",'PENE_DROIT'),
                       ("  SOUND:PlayBattleSE('EVT_EP_Pitfall_Fall')",'CHUTE')]:
        s=remplacer(s,match,'  '+marque(token)+'\n'+match)
    f.write_text(s,encoding='utf-8')
    f=c/ORIGIN/'zone/dojo_kingambit_dedales/init.lua';s=f.read_text(encoding='utf-8')
    s=remplacer(s,"  if map == 0 then SOUND:PlayBattleSE('EVT_EP_Pitfall_Land') end",'''  if map == 0 then
    assert(not _DATA.Save.CutsceneMode and _segment=='''+str(row['slot'])+''')
    SOUND:PlayBattleSE('EVT_EP_Pitfall_Land')
    PrintInfo('KINGAMBIT_SCENE ALL DONE atterrissage=étage-1 '.._segment)
  end''');f.write_text(s,encoding='utf-8')


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--lot',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
    p.add_argument('--mode',choices=['duo','solo','inverse'],default='duo');p.add_argument('--type',default='normal');a=p.parse_args()
    assert os.environ.get('DISPLAY'),'lancer sous xvfb-run';a.out.mkdir(parents=True,exist_ok=True)
    r=next(x for x in qa.rows() if x['id']==a.type);qa.QA=D/'prebatailles-pmd/banques'
    c,profil=qa.prepare(a.out,[r]);installer(c,a.lot,r,a.mode);capter(a.out,c,profil,[r],mode='trappe')


if __name__=='__main__':main()
