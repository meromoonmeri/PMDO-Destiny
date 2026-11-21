"""Casting et mise en scène des finales, sans toucher aux élèves des étages.

Chaque entrée : maître, deux pré-évolutions (identifiants PMDO et capacités),
nom de la scène, pose de révélation (4 ticks/pose) et mouvement natif. Les
stades à trois Pokémon montrent les deux pré-évolutions, sinon deux cadets.
"""
from dojo_dtef import BOSS

FORMATION = (BOSS, (5, 4), (9, 4))
TROUPES = {
    'normal': ((('furret','quick_attack','defense_curl'), ('sentret','scratch'), ('sentret','quick_attack')),
               'Piste des échos', 5, 'walk'),
    'fire': ((('arcanine','ember','odor_sleuth'), ('growlithe','ember'), ('growlithe','bite')),
             'Fournaises', 7, 'idle'),
    'water': ((('floatzel','water_gun','quick_attack'), ('buizel','water_gun'), ('buizel','quick_attack')),
              'Couronne de ressac', 6, 'jump'),
    'grass': ((('breloom','absorb','stun_spore'), ('shroomish','tackle'), ('shroomish','absorb')),
              'Fougères déroulées', 8, 'idle'),
    'electric': ((('raichu','thunder_shock','tail_whip'), ('pikachu','thunder_shock'), ('pichu','thunder_shock')),
                 'Éclairs fourchus', 6, 'idle'),
    'ice': ((('beartic','powder_snow','growl'), ('cubchoo','powder_snow'), ('cubchoo','powder_snow')),
            'Éclats de glace', 7, 'walk'),
    'fighting': ((('primeape','karate_chop','leer'), ('mankey','low_kick'), ('mankey','scratch')),
                 'Bonds et onde de choc', 3, 'jump'),
    'poison': ((('arbok','acid','leer'), ('ekans','poison_sting'), ('ekans','poison_sting')),
               'Brume à bulles', 8, 'idle'),
    'ground': ((('flygon','mud_slap','feint_attack'), ('vibrava','mud_slap'), ('trapinch','bite')),
               'Fentes de sable', 7, 'idle'),
    'flying': ((('swellow','peck','focus_energy'), ('taillow','peck'), ('taillow','quick_attack')),
               'Piqués des alizés', 4, 'drop'),
    'psychic': ((('alakazam','confusion','kinesis'), ('kadabra','confusion'), ('abra','hidden_power')),
                'Téléportation prismatique', 6, 'warp'),
    'bug': ((('venomoth','silver_wind','tackle'), ('venonat','tackle'), ('venonat','confusion')),
            'Cocons fendus', 7, 'idle'),
    'rock': ((('probopass','rock_throw','tackle'), ('nosepass','tackle'), ('nosepass','rock_throw')),
             'Mégalithes fendus', 8, 'idle'),
    'ghost': ((('mismagius','astonish','psywave'), ('misdreavus','astonish'), ('misdreavus','psywave')),
              'Sortie des ombres', 7, 'shadow'),
    'dragon': ((('dragonite','twister','leer'), ('dragonair','twister'), ('dratini','twister')),
               'Volutes draconiques', 6, 'idle'),
    'dark': ((('honchkrow','feint_attack','haze'), ('murkrow','peck'), ('murkrow','astonish')),
             'Croissants nocturnes', 6, 'walk'),
    'steel': ((('bisharp','metal_claw','leer'), ('pawniard','metal_claw'), ('pawniard','scratch')),
              'Berceau magnétique', 8, 'idle'),
    'fairy': ((('florges','fairy_wind','lucky_chant'), ('floette','fairy_wind'), ('flabebe','tackle')),
              'Pluie de pétales de cerisier', 10, 'idle'),
}
POSES, TICKS = 16, 4


def departs(typ):
    mode = TROUPES[typ][3]
    if mode == 'warp':
        return ((6, 2), (4, 2), (10, 2))
    if typ == 'dark':
        return ((6, 3), (4, 4), (10, 4))
    if mode in ('walk','jump','shadow'):
        return tuple((x,y-1) for x,y in FORMATION)
    return FORMATION
