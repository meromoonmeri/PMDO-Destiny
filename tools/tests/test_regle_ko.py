#!/usr/bin/env python3
"""Règle K.O. Destiny : tests Lua avec doubles et contrôles de branchement.
N'est pas un test en partie réelle ni une simulation du moteur de combat.
"""
from pathlib import Path
import json
from lupa import LuaRuntime

R = Path(__file__).resolve().parents[2]
script = R/'game/Data/Script/destiny/regle_ko.lua'
event = (R/'game/Data/Script/destiny/event.lua').read_text(encoding='utf-8')
assert "require 'destiny.regle_ko'" in event
base = json.loads((R/'base/Data/Universal.json').read_text(encoding='utf-8-sig'))
quest = json.loads((R/'game/Data/Universal.json').read_text(encoding='utf-8-sig'))
deaths = quest['Object']['OnDeaths']
added = [e for e in deaths if e['Value'].get('Script') == 'DestinyVerifierKO']
assert len(added)==1 and added[0]['Key']['str']==[10]
assert added[0]['Value']['$type']=='RogueEssence.Dungeon.SingleCharScriptEvent, RogueEssence'
deaths.remove(added[0]); assert quest == base
lua=LuaRuntime(unpack_returned_tuples=True)
lua.execute('assert(load(...))',script.read_text(encoding='utf8'))
lua.execute((R/'tools/tests/test_regle_ko.lua').read_text(encoding='utf8'),str(script),str(R/'game/Data/Script/destiny/zone'))
print('PASS : Universal Destiny, raccordement Lua, scénarios K.O. et sorties testés avec doubles ; partie réelle à vérifier.')
