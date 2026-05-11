import streamlit as st
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from PIL import Image
import time

# ============================================================
# CONFIG PAGINA
# ============================================================

st.set_page_config(
    page_title="Algoritmul Ungar",
    page_icon="💰",
    layout="wide"
)

# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #0f172a, #111827, #1e293b);
    color: white;
}

h1, h2, h3 {
    color: white;
}

.block-container {
    padding-top: 2rem;
}

.stButton>button {
    width: 100%;
    background: linear-gradient(90deg,#16a34a,#22c55e);
    color: white;
    border: none;
    border-radius: 14px;
    height: 3.2em;
    font-size: 20px;
    font-weight: bold;
}

.stButton>button:hover {
    transform: scale(1.02);
}

.metric-card {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 18px;
    text-align: center;
    border: 1px solid rgba(255,255,255,0.1);
}

.assignment-box {
    background: rgba(255,255,255,0.06);
    padding: 15px;
    border-radius: 14px;
    margin-bottom: 12px;
    border-left: 5px solid #22c55e;
}



.money-rain {
    text-align:center;
    font-size:60px;
    animation: pulse 0.5s infinite alternate;
}

@keyframes pulse {
    from {transform: scale(1);}
    to {transform: scale(1.1);}
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# TITLU
# ============================================================

st.title("💰 Algoritmul Ungar")



# ============================================================
# DIMENSIUNE MATRICE
# ============================================================

# ============================================================
# DIMENSIUNE MATRICE
# ============================================================

st.markdown("## 📐 Dimensiunea matricei")

n = st.number_input(
    "Introdu dimensiunea matricei",
    min_value=2,
    value=6,
    step=1
)

n = int(n)

# ============================================================
# MATRICE INITIALA
# ============================================================

default_values = [
    [1, 7, 5, 9, 3, 4],
    [6, 7, 4, 8, 5, 1],
    [4, 6, 5, 7, 1, 4],
    [8, 9, 3, 1, 2, 8],
    [5, 2, 2, 4, 6, 6],
    [5, 1, 2, 10, 6, 3]
]

matrix_data = []

for i in range(n):

    row = []

    for j in range(n):

        if i < 6 and j < 6:
            row.append(default_values[i][j])
        else:
            row.append(0)

    matrix_data.append(row)

default_matrix = np.array(matrix_data)

# ============================================================
# MATRICE
# ============================================================

st.markdown("## ✏️ Matrice")

df = pd.DataFrame(
    default_matrix,
    columns=[f"y{i+1}" for i in range(n)],
    index=[f"x{i+1}" for i in range(n)]
)

edited_df = st.data_editor(
    df,
    use_container_width=True,
    key="matrix_editor"
)

# ============================================================
# CLASA
# ============================================================

class HungarianSeminar:

    def __init__(self, C):

        self.original = np.array(C, dtype=int)
        self.C = self.original.copy()
        self.n = len(C)

        self.steps = []

    # --------------------------------------------------------

    def save_step(self, title):
        self.steps.append((title, self.C.copy()))

    # --------------------------------------------------------

    def step1(self):

        rowmin = self.C.min(axis=1)

        for i in range(self.n):
            self.C[i] -= rowmin[i]

        self.save_step("Reducerea pe linii")

        colmin = self.C.min(axis=0)

        for j in range(self.n):
            self.C[:, j] -= colmin[j]

        self.save_step("Reducerea pe coloane")

    # --------------------------------------------------------

    def label_zeros(self):

        zeros = [(i, j)
                 for i in range(self.n)
                 for j in range(self.n)
                 if self.C[i, j] == 0]

        selected = set()
        crossed = set()

        rows_left = set(range(self.n))

        while rows_left:

            zrows = {
                r: [z for z in zeros
                    if z[0] == r
                    and z not in selected
                    and z not in crossed]
                for r in rows_left
            }

            zrows = {r: z for r, z in zrows.items() if z}

            if not zrows:
                break

            r = min(zrows, key=lambda x: len(zrows[x]))

            z = zrows[r][0]

            selected.add(z)

            rr, cc = z

            for zz in zeros:
                if zz != z and (zz[0] == rr or zz[1] == cc):
                    crossed.add(zz)

            rows_left.remove(r)

        return selected

    # --------------------------------------------------------

    def step4(self, selected):

        marked_rows = {
            i for i in range(self.n)
            if not any((i, j) in selected for j in range(self.n))
        }

        marked_cols = set()

        changed = True

        while changed:

            changed = False

            for i in marked_rows:
                for j in range(self.n):

                    if self.C[i, j] == 0 and j not in marked_cols:
                        marked_cols.add(j)
                        changed = True

            for j in marked_cols:
                for i in range(self.n):

                    if (i, j) in selected and i not in marked_rows:
                        marked_rows.add(i)
                        changed = True

        cut_rows = set(range(self.n)) - marked_rows
        cut_cols = marked_cols

        return cut_rows, cut_cols

    # --------------------------------------------------------

    def step5(self, cut_rows, cut_cols):

        T1 = []

        for i in range(self.n):
            for j in range(self.n):

                cuts = int(i in cut_rows) + int(j in cut_cols)

                if cuts == 0:
                    T1.append(self.C[i, j])

        eps = min(T1)

        for i in range(self.n):
            for j in range(self.n):

                cuts = int(i in cut_rows) + int(j in cut_cols)

                if cuts == 0:
                    self.C[i, j] -= eps

                elif cuts == 2:
                    self.C[i, j] += eps

        self.save_step(f"Deplasarea zerourilor (ε = {eps})")

    # --------------------------------------------------------

    def solve(self):

        self.step1()

        while True:

            selected = self.label_zeros()

            if len(selected) == self.n:
                break

            cut_rows, cut_cols = self.step4(selected)

            self.step5(cut_rows, cut_cols)

        total = 0

        for i, j in selected:
            total += self.original[i, j]

        return selected, total

# ============================================================
# BUTON
# ============================================================

if st.button("🚀 Rulează algoritmul"):

    # ========================================================
    # ANIMATIE BANI
    # ========================================================

    money_placeholder = st.empty()

    for _ in range(10):

        money_placeholder.markdown("""
        <div class="money-rain">
        💸 💰 💵 💳 🪙 💸 💰 💵
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.15)

        money_placeholder.empty()

        time.sleep(0.05)

    # ========================================================
    # EXECUTIE
    # ========================================================

    matrix = edited_df.values

    solver = HungarianSeminar(matrix)

    selected, total = solver.solve()

    # ========================================================
    # REZULTATE
    # ========================================================

    st.markdown("## 💰 Rezultate")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h2>💵 Cost total</h2>
        <h1>{total}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
        <h2>📊 Alocări</h2>
        <h1>{len(selected)}</h1>
        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # SOLUTIE
    # ========================================================

    st.markdown("## 🔗 Soluția optimă")

    for i, j in sorted(selected):

        cost = matrix[i][j]

        st.markdown(f"""
        <div class="assignment-box">
        <b>x{i+1}</b> → <b>y{j+1}</b>
        <br><br>
        💰 Cost: <b>{cost}</b>
        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # PASI
    # ========================================================

    st.markdown("## 📊 Pașii algoritmului")

    for title, mat in solver.steps:

        st.markdown(f"### {title}")

        df_step = pd.DataFrame(
            mat,
            columns=[f"y{i+1}" for i in range(solver.n)],
            index=[f"x{i+1}" for i in range(solver.n)]
        )

        st.dataframe(
            df_step,
            use_container_width=True
        )

    # ========================================================
    # GRAF
    # ========================================================

    st.markdown("## 🌐 Graful bipartit")

    G = nx.Graph()

    left_nodes = [f"x{i+1}" for i in range(solver.n)]
    right_nodes = [f"y{i+1}" for i in range(solver.n)]

    G.add_nodes_from(left_nodes, bipartite=0)
    G.add_nodes_from(right_nodes, bipartite=1)

    edges = [(f"x{i+1}", f"y{j+1}") for i, j in selected]

    G.add_edges_from(edges)

    pos = {}

    pos.update(
        (node, (1, solver.n - 1 - idx))
        for idx, node in enumerate(left_nodes)
    )

    pos.update(
        (node, (2, solver.n - 1 - idx))
        for idx, node in enumerate(right_nodes)
    )

    fig, ax = plt.subplots(figsize=(8, 6))

    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=left_nodes,
        node_color='#38bdf8',
        node_size=2600
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=right_nodes,
        node_color='#22c55e',
        node_size=2600
    )

    nx.draw_networkx_edges(
        G,
        pos,
        width=4,
        edge_color='gold'
    )

    nx.draw_networkx_labels(
        G,
        pos,
        font_size=12,
        font_weight='bold'
    )

    plt.axis("off")

    st.pyplot(fig)

# ============================================================
# SIDEBAR
# ============================================================

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Panou")

st.sidebar.markdown("""
✔ Matrice <br>
✔ Dimensiune <br>
✔ Execuție pas cu pas <br>
✔ Reprezentare grafică
""", unsafe_allow_html=True)
