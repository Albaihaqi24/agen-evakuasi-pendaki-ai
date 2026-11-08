"""Jalankan python main.py untuk dashboard, atau --cli untuk terminal."""
import argparse
import json
import sys
from pathlib import Path
from src.knowledge_base import NODES,SCENARIOS
from src.simulation import simulate


if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def main():
    parser=argparse.ArgumentParser(description='Simulasi Agen Evakuasi Pendaki: Forward Chaining + A*')
    parser.add_argument('--cli',action='store_true',help='Mode terminal tanpa GUI')
    parser.add_argument('--scenario',choices=SCENARIOS,default='ekstrem')
    parser.add_argument('--start',choices=NODES,default='S')
    parser.add_argument('--goal',choices=NODES,default='G')
    parser.add_argument('--output',type=Path,help='Simpan hasil CLI sebagai JSON')
    args=parser.parse_args()
    if not args.cli:
        try:
            from src.visualizer import launch
            launch()
        except (ImportError, RuntimeError) as e:
            parser.exit(1,f'GUI tidak tersedia: {e}\nGunakan python main.py --cli\n')
        except Exception as e:
            # TclError biasanya muncul pada mesin tanpa display.
            if e.__class__.__name__ != 'TclError': raise
            parser.exit(1,f'Display/Tkinter tidak tersedia: {e}\nGunakan python main.py --cli\n')
        return
    result=simulate(args.scenario,args.start,args.goal)
    print(f"SKENARIO: {args.scenario.upper()} | {args.start} -> {args.goal}")
    for name,key in [('A*','astar'),('BFS','bfs')]:
        r=result[key]
        print(f"{name}: {' -> '.join(r['path']) or 'TIDAK ADA RUTE'} | cost={r['cost']} | langkah={r['steps']} | ekspansi={r['expanded']}")
    for e in result['edges']:
        print(f"\n{e['u']} <-> {e['v']}: {'DITUTUP' if e['blocked'] else 'TERBUKA'}, cost={e['cost']:g}")
        for line in e['trace']:print(' ',line)
    if args.output:
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'\nTersimpan: {args.output}')

if __name__=='__main__':main()
