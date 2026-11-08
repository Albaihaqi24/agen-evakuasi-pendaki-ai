"""A* dengan reopen dan stale-entry check; BFS meminimalkan jumlah sisi."""
import heapq
from itertools import count
from collections import deque
from .knowledge_base import heuristic


def _result(parent, costs, goal, trace, found):
    path = []
    if found:
        node = goal
        while node is not None:
            path.append(node)
            node = parent[node]
        path.reverse()
    return dict(found=found,path=path,cost=costs[goal] if found else None,
                steps=len(path)-1 if found else None,expanded=len(trace),trace=trace)


def astar(graph, start, goal, h=heuristic):
    if start not in graph or goal not in graph:
        raise ValueError('Pos awal atau tujuan tidak terdaftar')
    serial = count()
    frontier = [(h(start,goal),next(serial),start,0)]
    costs, parent, trace = {start: 0}, {start:None}, []
    while frontier:
        f, _, node, g = heapq.heappop(frontier)
        if g != costs[node]: continue
        trace.append(dict(node=node,g=g,h=h(node,goal),f=f))
        if node == goal: return _result(parent,costs,goal,trace,True)
        for neighbor,weight in graph[node]:
            if weight < 0: raise ValueError('A* memerlukan bobot nonnegatif')
            candidate = g + weight
            if candidate < costs.get(neighbor,float('inf')):
                costs[neighbor], parent[neighbor] = candidate, node
                heapq.heappush(frontier,(candidate+h(neighbor,goal),next(serial),neighbor,candidate))
    return _result(parent,costs,goal,trace,False)


def bfs(graph,start,goal):
    if start not in graph or goal not in graph:
        raise ValueError('Pos awal atau tujuan tidak terdaftar')
    queue, costs, parent, trace = deque([start]), {start:0}, {start:None}, []
    while queue:
        node = queue.popleft()
        trace.append(dict(node=node,g=costs[node],h=None,f=None))
        if node == goal: return _result(parent,costs,goal,trace,True)
        for neighbor,weight in graph[node]:
            if neighbor not in parent:
                parent[neighbor], costs[neighbor] = node, costs[node]+weight
                queue.append(neighbor)
    return _result(parent,costs,goal,trace,False)
