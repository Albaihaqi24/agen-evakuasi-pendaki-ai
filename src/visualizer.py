"""Dashboard Tkinter offline. Klik sisi untuk membuka/menutup manual."""
import json
import tkinter as tk
from tkinter import ttk,filedialog,messagebox
from .knowledge_base import NODES
from .simulation import simulate

BG='#0c1726'
CARD='#14253a'
TEXT='#e7eef6'
MUTED='#9badc4'
GREEN='#48dbb1'

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Mountain SAR • Agen Evakuasi Pendaki • Mini Project AI')
        self.geometry('1250x900')
        self.minsize(1000,760)
        self.configure(bg=BG)
        self.closed=set()
        self.result=None
        self.scenario=tk.StringVar(value='ekstrem')
        self.start=tk.StringVar(value='S')
        self.goal=tk.StringVar(value='G')
        self.mode=tk.StringVar(value='A*')
        style=ttk.Style(self)
        style.theme_use('clam')
        style.configure('TCombobox',fieldbackground=CARD,background=CARD,foreground=TEXT)
        header=tk.Frame(self,bg=BG)
        header.pack(fill='x',padx=24,pady=(20,12))
        tk.Label(header,text='MOUNTAIN / SAR',fg=GREEN,bg=BG,font=('Segoe UI',11,'bold')).pack(anchor='w')
        tk.Label(header,text='Agen Evakuasi Pendaki',fg=TEXT,bg=BG,font=('Segoe UI',24,'bold')).pack(anchor='w')
        tk.Label(header,text='Forward Chaining + A* Search   •   Simulasi akademik, data sintetis',fg=MUTED,bg=BG,font=('Segoe UI',11)).pack(anchor='w',pady=(4,0))
        bar=tk.Frame(self,bg=CARD,padx=12,pady=12)
        bar.pack(fill='x',padx=24)
        for title,var,values,width in [('Cuaca',self.scenario,['cerah','hujan','kabut','ekstrem'],12),('Awal',self.start,list(NODES),5),('Tujuan',self.goal,list(NODES),5),('Rute di peta',self.mode,['A*','BFS'],6)]:
            tk.Label(bar,text=title,bg=CARD,fg=MUTED).pack(side='left',padx=(4,6))
            box=ttk.Combobox(bar,textvariable=var,values=values,state='readonly',width=width)
            box.pack(side='left',padx=(0,12))
            box.bind('<<ComboboxSelected>>',lambda e:self.run())
        self.button(bar,'Analisis ulang',self.run)
        self.button(bar,'Reset',self.reset)
        self.button(bar,'Ekspor JSON',self.export)
        self.stats=tk.Label(self,text='',fg=GREEN,bg=BG,font=('Segoe UI',12,'bold'),anchor='w')
        self.stats.pack(fill='x',padx=24,pady=12)
        body=tk.PanedWindow(self,orient='horizontal',bg=BG,sashwidth=12)
        body.pack(fill='both',expand=True,padx=24,pady=(0,12))
        left=tk.Frame(body,bg=CARD)
        self.canvas=tk.Canvas(left,bg=CARD,highlightthickness=0,width=650,height=520)
        self.canvas.pack(fill='both',expand=True)
        self.canvas.bind('<Configure>',lambda e:self.draw())
        tk.Label(left,text='Hijau: rute   •   Merah putus: ditutup   •   Abu: terbuka\nKlik garis untuk menutup / membuka jalur secara manual.',fg=MUTED,bg=CARD,pady=10).pack()
        right=tk.Frame(body,bg=CARD)
        tk.Label(right,text='HASIL & JEJAK PENALARAN',font=('Segoe UI',11,'bold'),fg=GREEN,bg=CARD,pady=12).pack(anchor='w',padx=12)
        self.log=tk.Text(right,bg=CARD,fg=TEXT,relief='flat',wrap='word',font=('Consolas',10),width=48,padx=12,pady=8)
        scroll=ttk.Scrollbar(right,command=self.log.yview)
        scroll.pack(side='right',fill='y')
        self.log.configure(yscrollcommand=scroll.set)
        self.log.pack(fill='both',expand=True)
        body.add(left,stretch='always',minsize=470)
        body.add(right,stretch='always',minsize=370)
        tk.Label(self,text='Bobot = jarak + beban medan + penalti kabut. Peta skematik; bukan panduan evakuasi nyata.',fg=MUTED,bg=BG,font=('Segoe UI',10)).pack(pady=(0,12))
        self.run()

    def button(self,parent,text,command):
        tk.Button(parent,text=text,command=command,bg='#23425b',fg=TEXT,activebackground='#32607e',activeforeground='white',relief='flat',padx=10,pady=6,cursor='hand2').pack(side='left',padx=4)

    def reset(self):
        self.closed.clear()
        self.scenario.set('ekstrem'); self.start.set('S'); self.goal.set('G')
        self.mode.set('A*'); self.run()

    def run(self):
        self.result=simulate(self.scenario.get(),self.start.get(),self.goal.get(),self.closed)
        r=self.result
        a,b=r['astar'],r['bfs']
        cost=lambda x: f"{x['cost']:g}" if x['found'] else 'tidak ada rute'
        blocked=sum(e['blocked'] for e in r['edges'])
        self.stats.config(text=f"A* cost: {cost(a)}     /     BFS cost: {cost(b)}     /     Jalur ditutup: {blocked} dari {len(r['edges'])}")
        lines=[]
        for label,key in [('A* SEARCH','astar'),('BREADTH-FIRST SEARCH','bfs')]:
            result=r[key]
            lines += [label, ' → '.join(result['path']) if result['found'] else 'TIDAK ADA RUTE TERSEDIA',f"Cost: {cost(result)} | Langkah: {result['steps']} | Ekspansi: {result['expanded']}",'']
        if a['found'] and b['found'] and b['cost']:
            lines += [f"Penghematan cost A*: {(b['cost']-a['cost'])/b['cost']*100:.1f}%",'']
        lines += ['DETAIL RUTE YANG DIPILIH']
        active=r['astar' if self.mode.get()=='A*' else 'bfs']
        for u,v in zip(active['path'],active['path'][1:]):
            edge=next(e for e in r['edges'] if {e['u'],e['v']}=={u,v})
            lines += [f"{u} → {v}: {edge['distance']:g} + {edge['terrain']:g} + {edge['penalty']:g} = {edge['cost']:g}"]
        lines += ['', 'INFERENSI PER JALUR']
        for edge in r['edges']:
            lines += [f"{edge['u']} ↔ {edge['v']}  {'DITUTUP' if edge['blocked'] else 'TERBUKA'}",'Fakta: '+(', '.join(edge['facts']) or 'medan landai / cuaca cerah')]
            lines += edge['trace'] or ['Tidak ada aturan bahaya yang terpenuhi.']
            lines += ['']
        lines += ['JEJAK EKSPANSI A*','Node      g       h       f']
        for step in a['trace']:
            lines += [f"{step['node']:<5} {step['g']:7.2f} {step['h']:7.2f} {step['f']:7.2f}"]
        lines += ['', 'Heuristic = jarak skematik ke tujuan / 1000.', 'h tidak melebihi sisa cost minimum.', 'BFS memilih jumlah sisi paling sedikit.', 'A* memilih total bobot minimum.']
        self.log.config(state='normal');self.log.delete('1.0','end');self.log.insert('1.0','\n'.join(lines));self.log.config(state='disabled')
        self.draw()

    def toggle(self,u,v):
        edge=frozenset((u,v))
        if edge in self.closed: self.closed.remove(edge)
        else: self.closed.add(edge)
        self.run()

    def draw(self):
        if not self.result:return
        c=self.canvas;c.delete('all')
        w,h=max(c.winfo_width(),470),max(c.winfo_height(),400)
        scale=min(w/900,h/710)
        ox=(w-900*scale)/2; oy=(h-710*scale)/2
        pos={k:(ox+x*scale,oy+y*scale) for k,(_,x,y) in NODES.items()}
        route=self.result['astar' if self.mode.get()=='A*' else 'bfs']['path']
        pairs={frozenset((u,v)) for u,v in zip(route,route[1:])}
        for i,e in enumerate(self.result['edges']):
            u,v=e['u'],e['v'];x,y=pos[u];xx,yy=pos[v]
            chosen=frozenset((u,v)) in pairs
            color='#f47c80' if e['blocked'] else GREEN if chosen else '#52667e'
            tag=f'edge{i}'
            c.create_line(x,y,xx,yy,fill=color,width=5 if chosen else 3,dash=(5,5) if e['blocked'] else (),tags=tag)
            mx,my=(x+xx)/2,(y+yy)/2
            c.create_rectangle(mx-17,my-11,mx+17,my+11,fill=CARD,outline='',tags=tag)
            c.create_text(mx,my,text='×' if e['blocked'] else f"{e['cost']:g}",fill=color,font=('Segoe UI',10,'bold'),tags=tag)
            c.tag_bind(tag,'<Button-1>',lambda event,u=u,v=v:self.toggle(u,v))
        for k,(x,y) in pos.items():
            selected=k in route
            c.create_oval(x-16,y-16,x+16,y+16,fill=GREEN if selected else '#29425e',outline='#93b4ce',width=1)
            c.create_text(x,y,text=k,fill=BG if selected else TEXT,font=('Segoe UI',11,'bold'))
            c.create_text(x,y+29,text=NODES[k][0],fill=TEXT,font=('Segoe UI',9))

    def export(self):
        path=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('JSON','*.json')],initialfile='hasil_evakuasi.json')
        if path:
            try:
                with open(path,'w',encoding='utf-8') as f:json.dump(self.result,f,ensure_ascii=False,indent=2)
                messagebox.showinfo('Ekspor','Hasil simulasi berhasil disimpan.')
            except OSError as e:messagebox.showerror('Gagal menyimpan',str(e))

def launch():
    Dashboard().mainloop()
