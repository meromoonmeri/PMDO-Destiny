#!/usr/bin/env python3
"""Crée une maquette de données isolée, jamais une modification du jeu."""
from pathlib import Path
import copy, json, sys
here=Path(__file__).resolve().parent
source=here/'tsareena-source.json'
out=here/'tsareena-BROUILLON-NON-JOUABLE.json'
obj=json.loads(source.read_text(encoding='utf-8-sig'))
forms=obj['Object']['Forms']
if len(forms)!=1 or forms[0]['FormName']['DefaultText']!='Tsareena':
    sys.exit('La référence a changé : arrêter et revoir la forme avant de continuer.')
mega=copy.deepcopy(forms[0])
mega['FormName']={'DefaultText':'Mega Tsareena','LocalTexts':{'fr':'Méga-Sucreine'}}
mega['Released']=False
mega['Temporary']=True
# Stats, talent, types, attaques, dimensions : copiés de la base UNIQUEMENT
# comme placeholders. Aucune valeur Méga ni condition de transformation décidée.
forms.append(mega)
assert forms[0]['FormName']['DefaultText']=='Tsareena' and forms[0]['Released'] is True
assert len(forms)==2 and forms[1]['Released'] is False and forms[1]['Temporary'] is True
out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Brouillon isolé créé :',out.name)
