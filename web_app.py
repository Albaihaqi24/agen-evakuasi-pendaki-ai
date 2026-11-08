"""Streamlit dashboard for the academic mountain evacuation simulation."""
import json

import streamlit as st

from src.knowledge_base import EDGES, NODES
from src.simulation import simulate


st.set_page_config(
    page_title="Agen Evakuasi Pendaki",
    page_icon="⛰️",
    layout="wide",
)

st.title("Agen Evakuasi Pendaki")
st.caption(
    "Dashboard simulasi akademik dengan Forward Chaining, A*, dan BFS. "
    "Seluruh pos, jalur, dan bobot adalah data sintetis, bukan panduan "
    "evakuasi atau kondisi lapangan nyata."
)

edge_labels = {
    f"{edge.u} ↔ {edge.v}": frozenset((edge.u, edge.v))
    for edge in EDGES
}

with st.sidebar:
    st.header("Pengaturan simulasi")
    scenario = st.selectbox(
        "Cuaca",
        ("cerah", "hujan", "kabut", "ekstrem"),
        index=3,
    )
    start = st.selectbox("Pos awal", tuple(NODES), index=tuple(NODES).index("S"))
    goal = st.selectbox("Tujuan", tuple(NODES), index=tuple(NODES).index("G"))
    selected_route = st.radio("Rute yang ditampilkan pada graf", ("A*", "BFS"))
    manual_labels = st.multiselect(
        "Tutup jalur secara manual",
        options=list(edge_labels),
        help="Hapus pilihan untuk membuka penutupan manual. Bahaya yang terdeteksi otomatis tetap menutup jalur.",
    )
    st.caption("Peta dan kondisi ini hanya untuk tugas akademik.")

manual_closed = {edge_labels[label] for label in manual_labels}
result = simulate(scenario, start, goal, manual_closed)
active_key = "astar" if selected_route == "A*" else "bfs"
active = result[active_key]

summary_columns = st.columns(2)
for column, label, key in zip(summary_columns, ("A*", "BFS"), ("astar", "bfs")):
    search = result[key]
    with column:
        st.subheader(label)
        if search["found"]:
            st.metric("Cost", f'{search["cost"]:g}')
            st.write("Rute:", " → ".join(search["path"]))
            st.write(
                f'Langkah: {search["steps"]} · '
                f'Ekspansi: {search["expanded"]}'
            )
        else:
            st.error(f"{label}: TIDAK ADA RUTE TERSEDIA")
            st.write("Tidak ada jalur terbuka yang menghubungkan pos awal dan tujuan.")
            st.write(f'Ekspansi: {search["expanded"]}')


def quote_dot(value):
    return value.replace("\\", "\\\\").replace('"', '\\"')


route_edges = {
    frozenset((u, v))
    for u, v in zip(active["path"], active["path"][1:])
}
dot_lines = [
    "graph evacuation {",
    '  graph [rankdir=TB, bgcolor="transparent", pad="0.3", nodesep="0.6", ranksep="0.8"];',
    '  node [shape=box, style="rounded,filled", fillcolor="#e8eef5", color="#64748b", fontname="Arial"];',
    '  edge [fontname="Arial", fontsize=10, color="#64748b", fontcolor="#334155"];',
]
for node, (name, _, _) in NODES.items():
    dot_lines.append(
        f'  "{node}" [label="{quote_dot(node)}\\n{quote_dot(name)}"];'
    )
for edge in result["edges"]:
    pair = frozenset((edge["u"], edge["v"]))
    if edge["blocked"]:
        color, style, penwidth, label_color = "#dc2626", "dashed", 2, "#b91c1c"
    elif pair in route_edges:
        color, style, penwidth, label_color = "#059669", "solid", 4, "#047857"
    else:
        color, style, penwidth, label_color = "#94a3b8", "solid", 1, "#475569"
    dot_lines.append(
        f'  "{edge["u"]}" -- "{edge["v"]}" '
        f'[label="{edge["cost"]:g}", color="{color}", fontcolor="{label_color}", '
        f'style="{style}", penwidth="{penwidth}"];'
    )
dot_lines.append("}")

graph_column, rules_column = st.columns([1.25, 1])
with graph_column:
    st.subheader(f"Graf jalur — rute {selected_route}")
    st.graphviz_chart("\n".join(dot_lines))
    st.caption("Hijau: rute terpilih · Abu-abu: terbuka · Merah putus: ditutup")
with rules_column:
    st.subheader("Aturan dan alasan status jalur")
    for edge in result["edges"]:
        status = "DITUTUP" if edge["blocked"] else "TERBUKA"
        with st.expander(f'{edge["u"]} ↔ {edge["v"]} — {status}'):
            st.write(
                f'Cost: {edge["distance"]:g} jarak + {edge["terrain"]:g} '
                f'medan + {edge["penalty"]:g} penalti = {edge["cost"]:g}'
            )
            st.write("Fakta:", ", ".join(edge["facts"]) or "tidak ada fakta bahaya")
            if edge["trace"]:
                for line in edge["trace"]:
                    st.code(line, language=None)
            else:
                st.write("Tidak ada aturan bahaya yang terpenuhi.")

if not result["astar"]["found"] and not result["bfs"]["found"]:
    st.warning("Tidak tersedia rute untuk A* maupun BFS pada konfigurasi ini.")
elif not active["found"]:
    st.warning(f"Tidak tersedia rute untuk algoritma {selected_route}.")

st.subheader("Ekspor hasil")
export_result = dict(result)
export_result["manual_closed"] = sorted([sorted(pair) for pair in manual_closed])
st.download_button(
    "Unduh hasil JSON",
    data=json.dumps(export_result, ensure_ascii=False, indent=2),
    file_name=f"hasil_evakuasi_{scenario}.json",
    mime="application/json",
)
