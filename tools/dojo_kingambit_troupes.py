"""Casting et mise en scène des finales, sans toucher aux élèves des étages.

Chaque entrée : maître, deux pré-évolutions (identifiants PMDO et capacités),
nom de la scène, pose de révélation (4 ticks/pose) et mouvement natif. Les
stades à trois Pokémon montrent les deux pré-évolutions, sinon deux cadets.
"""
from dojo_dtef import BOSS

FORMATION = (BOSS, (5, 4), (9, 4))
TROUPES = {
    'normal': ((('lopunny', 'pound', 'quick_attack'), ('buneary', 'pound'), ('buneary', 'quick_attack')), 'Piste des échos', 5, 'walk'),
    'fire': ((('blaziken', 'ember', 'double_kick'), ('combusken', 'ember'), ('torchic', 'scratch')), 'Fournaises célestes', 6, 'column'),
    'water': ((('blastoise', 'water_gun', 'withdraw'), ('wartortle', 'water_gun'), ('squirtle', 'tackle')), 'Colonnes de chute', 6, 'column'),
    'grass': ((('sceptile', 'absorb', 'quick_attack'), ('grovyle', 'absorb'), ('treecko', 'pound')), 'Fougères déroulées', 8, 'idle'),
    'electric': ((('manectric', 'spark', 'leer'), ('electrike', 'tackle'), ('electrike', 'thunder_wave')), 'Foudre et champ statique', 5, 'storm'),
    'ice': ((('glalie', 'powder_snow', 'leer'), ('snorunt', 'powder_snow'), ('snorunt', 'ice_shard')), 'Voile de poudreuse', 6, 'whiteout'),
    'fighting': ((('lucario', 'quick_attack', 'force_palm'), ('riolu', 'quick_attack'), ('riolu', 'endure')), 'Bonds et onde de choc', 3, 'jump'),
    'poison': ((('gengar', 'lick', 'disable'), ('haunter', 'lick'), ('gastly', 'astonish')), 'Brume du Col Céleste', 8, 'mist'),
    'ground': ((('swampert', 'mud_slap', 'tackle'), ('marshtomp', 'mud_slap'), ('mudkip', 'tackle')), 'Brèches de sable', 6, 'emerge'),
    'flying': ((('charizard', 'wing_attack', 'growl'), ('charmeleon', 'ember'), ('charmander', 'scratch')), 'Piqués des alizés', 4, 'drop'),
    'psychic': ((('alakazam', 'confusion', 'kinesis'), ('kadabra', 'confusion'), ('abra', 'hidden_power')), 'Téléportation prismatique', 6, 'warp'),
    'bug': ((('beedrill', 'fury_attack', 'focus_energy'), ('kakuna', 'harden'), ('weedle', 'poison_sting')), 'Cocons fendus', 7, 'idle'),
    'rock': ((('tyranitar', 'smack_down', 'leer'), ('pupitar', 'bite'), ('larvitar', 'bite')), 'Mégalithes soulevés', 6, 'emerge'),
    'ghost': ((('banette', 'astonish', 'spite'), ('shuppet', 'astonish'), ('shuppet', 'night_shade')), 'Sortie des ombres', 7, 'shadow'),
    'dragon': ((('altaria', 'dragon_breath', 'growl'), ('swablu', 'peck'), ('swablu', 'astonish')), 'Volutes draconiques', 6, 'idle'),
    'dark': ((('houndoom', 'bite', 'howl'), ('houndour', 'ember'), ('houndour', 'bite')), 'Croissants nocturnes', 6, 'walk'),
    'steel': ((('metagross', 'metal_claw', 'confusion'), ('metang', 'metal_claw'), ('beldum', 'take_down')), 'Berceau magnétique', 8, 'idle'),
    'fairy': ((('gardevoir', 'disarming_voice', 'growl'), ('kirlia', 'disarming_voice'), ('ralts', 'confusion')), 'Pluie de pétales de cerisier', 10, 'idle')
}
MEGA_STONES = {'normal': 'mega_lopunnite', 'fire': 'mega_blazikenite', 'water': 'mega_blastoisinite', 'grass': 'mega_sceptilite', 'electric': 'mega_manectite', 'ice': 'mega_glalitite', 'fighting': 'mega_lucarionite', 'poison': 'mega_gengarite', 'ground': 'mega_swampertite', 'flying': 'mega_charizardite_x', 'psychic': 'mega_alakazite', 'bug': 'mega_beedrillite', 'rock': 'mega_tyranitarite', 'ghost': 'mega_banettite', 'dragon': 'mega_altarianite', 'dark': 'mega_houndoominite', 'steel': 'mega_metagrossite', 'fairy': 'mega_gardevoirite'}
POSES, TICKS = 16, 4


def departs(typ):
    mode = TROUPES[typ][3]
    if mode == 'warp':
        return ((6, 2), (4, 2), (10, 2))
    if typ == 'dark':
        return ((6, 3), (4, 4), (10, 4))
    if mode in ('walk','jump','shadow','column','emerge'):
        return tuple((x,y-1) for x,y in FORMATION)
    return FORMATION
