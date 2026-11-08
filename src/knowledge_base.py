"""Data sintetis untuk demonstrasi; bukan peta gunung nyata."""
from dataclasses import dataclass
from math import hypot

NODES = {
    'S': ('Puncak Bayangan', 450, 70),
    'A': ('Pos Batu', 205, 220), 'B': ('Pos Punggungan', 155, 430),
    'C': ('Pos Cemara', 450, 235), 'D': ('Pos Sungai', 560, 420),
    'E': ('Pos Hutan', 700, 200), 'F': ('Pos Landai', 760, 365),
    'H': ('Pos Shelter', 680, 525), 'G': ('Basecamp Utama', 450, 630),
}

@dataclass(frozen=True)
class Edge:
    u: str
    v: str
    distance: float
    terrain_cost: float = 0
    facts: frozenset = frozenset()

# Bobot = km simulasi + indeks medan. Semua sisi dua arah.
EDGES = [
    Edge('S','A',3,1), Edge('A','B',4,1), Edge('B','G',4,0),
    Edge('S','E',1.5,.5), Edge('E','F',1.5,.5),
    Edge('F','H',1.5,.5), Edge('H','G',1.5,.5),
    Edge('S','C',1,0,frozenset({'medan_curam'})),
    Edge('C','D',1,0,frozenset({'jalur_sungai'})),
    Edge('D','G',1,0), Edge('C','F',2,1,frozenset({'tepi_jurang'})),
]
SCENARIOS = {
    'cerah': (False, False),
    'hujan': (True, False),
    'kabut': (False, True),
    'ekstrem': (True, True),
}
FOG_PENALTY = 1.0

def heuristic(node, goal='G'):
    """Jarak skematik / 1000, dalam satuan indeks cost.

    Setiap bobot dasar sisi >= jarak skematik sisi / 1000.
    Ketaksamaan segitiga membuat h admissible dan konsisten untuk
    setiap goal, sekalipun sisi ditutup atau cost ditambah.
    """
    _, x, y = NODES[node]
    _, gx, gy = NODES[goal]
    return hypot(x-gx, y-gy) / 1000
