"""Forward chaining positif sampai fixed point, dilanjutkan aturan R5.

Negasi R5 dievaluasi setelah inferensi bahaya selesai (stratified negation),
agar sisi yang belakangan ditutup tidak terlanjur diberi status aman.
"""
from .knowledge_base import EDGES, NODES, FOG_PENALTY

RULES = [
    ('R1', {'hujan_lebat','medan_curam'}, 'risiko_longsor'),
    ('R2', {'hujan_lebat','jalur_sungai'}, 'risiko_banjir_bandang'),
    ('R3', {'kabut_tebal','tepi_jurang'}, 'risiko_tersesat_jatuh'),
    ('R4', {'risiko_longsor'}, 'JALUR_DITUTUP'),
    ('R4', {'risiko_banjir_bandang'}, 'JALUR_DITUTUP'),
    ('R4', {'risiko_tersesat_jatuh'}, 'JALUR_DITUTUP'),
]

def infer(facts):
    known, trace = set(facts), []
    changed = True
    while changed:
        changed = False
        for rule, premises, conclusion in RULES:
            if premises <= known and conclusion not in known:
                known.add(conclusion)
                trace.append(f'{rule}: {" AND ".join(sorted(premises))} → {conclusion}')
                changed = True
    penalty = 0
    if 'JALUR_DITUTUP' not in known and 'kabut_tebal' in known:
        penalty = FOG_PENALTY
        known.add('PENALTI_KECEPATAN')
        trace.append(f'R5: kabut_tebal AND NOT JALUR_DITUTUP → penalti +{penalty:g}')
    return known, trace, penalty

def build_safe_graph(rain=False, fog=False, manual_closed=(), edges=None):
    graph = {n: [] for n in NODES}
    reports = []
    for edge in EDGES if edges is None else edges:
        facts = set(edge.facts)
        if rain: facts.add('hujan_lebat')
        if fog: facts.add('kabut_tebal')
        if frozenset((edge.u,edge.v)) in manual_closed:
            facts.add('JALUR_DITUTUP')
        inferred, trace, penalty = infer(facts)
        blocked = 'JALUR_DITUTUP' in inferred
        if 'JALUR_DITUTUP' in facts:
            trace.insert(0, 'MANUAL: jalur ditutup oleh operator simulasi')
        cost = edge.distance + edge.terrain_cost + penalty
        reports.append(dict(u=edge.u,v=edge.v,distance=edge.distance,
                            terrain=edge.terrain_cost,penalty=penalty,cost=cost,
                            blocked=blocked,facts=sorted(inferred),trace=trace))
        if not blocked:
            graph[edge.u].append((edge.v,cost))
            graph[edge.v].append((edge.u,cost))
    return graph, reports
