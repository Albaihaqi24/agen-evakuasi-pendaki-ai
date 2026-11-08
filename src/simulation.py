from .knowledge_base import SCENARIOS
from .reasoning_engine import build_safe_graph
from .search_agent import astar,bfs

def simulate(scenario='ekstrem',start='S',goal='G',manual_closed=()):
    rain,fog = SCENARIOS[scenario]
    graph,reports = build_safe_graph(rain,fog,manual_closed)
    return dict(scenario=scenario,start=start,goal=goal,edges=reports,
                astar=astar(graph,start,goal),bfs=bfs(graph,start,goal))
