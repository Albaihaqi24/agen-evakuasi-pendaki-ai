import unittest
from math import inf, hypot
from src.knowledge_base import NODES,EDGES,SCENARIOS,heuristic
from src.reasoning_engine import infer,build_safe_graph
from src.search_agent import astar,bfs
from src.simulation import simulate

class AgentTests(unittest.TestCase):
    def test_tc01_rain_closes_steep_and_river(self):
        _,reports=build_safe_graph(True,False)
        blocked={(e['u'],e['v']) for e in reports if e['blocked']}
        self.assertEqual(blocked,{('S','C'),('C','D')})
        facts,trace,penalty=infer({'hujan_lebat','medan_curam'})
        self.assertIn('risiko_longsor',facts)
        self.assertIn('JALUR_DITUTUP',facts)
        self.assertTrue(any('R4' in line for line in trace))
        self.assertEqual(penalty,0)

    def test_tc02_clear(self):
        r=simulate('cerah')
        self.assertFalse(any(e['blocked'] for e in r['edges']))
        self.assertEqual(r['astar']['path'],['S','C','D','G'])
        self.assertEqual(r['astar']['cost'],3)

    def test_tc03_extreme(self):
        r=simulate('ekstrem')
        self.assertEqual(r['astar']['path'],['S','E','F','H','G'])
        self.assertEqual(r['astar']['cost'],12)
        self.assertEqual(r['astar']['steps'],4)
        self.assertEqual(r['bfs']['cost'],16)
        self.assertEqual(r['bfs']['steps'],3)

    def test_fog_negation_stratified(self):
        facts,_,penalty=infer({'kabut_tebal','tepi_jurang'})
        self.assertIn('JALUR_DITUTUP',facts)
        self.assertNotIn('PENALTI_KECEPATAN',facts)
        self.assertEqual(penalty,0)
        self.assertEqual(infer({'kabut_tebal'})[2],1)

    def test_isolated_start_and_identity(self):
        closures={frozenset((e.u,e.v)) for e in EDGES if 'S' in (e.u,e.v)}
        r=simulate(manual_closed=closures)
        for key in ['astar','bfs']:
            self.assertFalse(r[key]['found'])
            self.assertIsNone(r[key]['cost'])
            self.assertEqual(r[key]['path'],[])
        for search in [astar,bfs]:
            r=search({'S':[]},'S','S')
            self.assertEqual(r['path'],['S'])
            self.assertEqual(r['cost'],0)

    def test_all_pairs_against_floyd_warshall(self):
        # Independent shortest-path oracle across all weather and manual closures.
        for rain,fog in SCENARIOS.values():
            for closures in [set(),{frozenset(('E','F'))}]:
                graph,reports=build_safe_graph(rain,fog,closures)
                d={(u,v):(0 if u==v else inf) for u in NODES for v in NODES}
                for u,neighbors in graph.items():
                    for v,w in neighbors:d[u,v]=w
                for k in NODES:
                    for u in NODES:
                        for v in NODES:d[u,v]=min(d[u,v],d[u,k]+d[k,v])
                for start in NODES:
                    for goal in NODES:
                        a=astar(graph,start,goal);b=bfs(graph,start,goal)
                        self.assertEqual(a['cost'],None if d[start,goal]==inf else d[start,goal])
                        self.assertLessEqual(heuristic(start,goal),d[start,goal]+1e-9)
                        if a['found']:
                            self.assertLessEqual(a['cost'],b['cost'])
                            for u,v in zip(a['path'],a['path'][1:]):
                                edge=next(e for e in reports if {e['u'],e['v']}=={u,v})
                                self.assertFalse(edge['blocked'])
                        for v,w in graph[start]:
                            self.assertLessEqual(heuristic(start,goal),w+heuristic(v,goal)+1e-9)

    def test_heuristic_scale(self):
        for e in EDGES:
            _,x,y=NODES[e.u];_,xx,yy=NODES[e.v]
            self.assertGreaterEqual(e.distance+e.terrain_cost,hypot(x-xx,y-yy)/1000)

    def test_invalid_node(self):
        with self.assertRaises(ValueError):astar({'S':[]},'invalid','S')

if __name__=='__main__':unittest.main()
