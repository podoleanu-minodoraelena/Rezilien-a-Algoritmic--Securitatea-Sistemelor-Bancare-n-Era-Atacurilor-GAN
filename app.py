import streamlit as st
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from copy import deepcopy

# ============================================================
# CONFIGURARE PAGINA
# ============================================================

st.set_page_config(
    page_title="Algoritmul Ungar - Securitate Bancară",
    page_icon="🏦",
    layout="wide"
)

# ============================================================
# STIL CSS
# ============================================================

st.markdown("""
<style>

.main {
    background: linear-gradient(to bottom right, #0f172a, #1e293b);
    color: white;
}

h1, h2, h3 {
    color: #f8fafc;
}

.stButton>button {
    background: linear-gradient(90deg,#16a34a,#22c55e);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.6rem 1.2rem;
    font-weight: bold;
}

.stDataFrame {
    border-radius: 12px;
}

.metric-box {
    background-color: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 16px;
    text-align: center;
}

.big-font {
    font-size:20px !important;
    font-weight:bold;
}

.bank-box {
    background: rgba(255,255,255,0.06);
    padding: 15px;
    border-radius: 15px;
    border: 1px solid rgba(255,255,255,0.1);
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# TITLU
# ============================================================

st.title("🏦 Algoritmul Ungar în Securitatea Bancară")
st.markdown("""
### Studiu de caz — Alocarea optimă a resurselor defensive

Această aplicație simulează:
- distribuirea echipelor de securitate;
- protejarea infrastructurii bancare;
- minimizarea costurilor de apărare cibernetică;
- optimizarea resurselor folosind **Algoritmul Ungar**.
""")

# ============================================================
# MATRICE PREDEFINITA
# ============================================================

default_matrix = np.array([
    [1, 7, 5, 9, 3, 4],
    [6, 7, 4, 8, 5, 1],
    [4, 6, 5, 7, 1, 4],
    [8, 9, 3, 1, 2, 8],
    [5, 2, 2, 4, 6, 6],
    [5, 1, 2, 10, 6, 3]
])

st.markdown("## 💳 Matricea costurilor")

st.markdown("""
Valorile reprezintă costurile de alocare ale resurselor de securitate:
- linii = echipe defensive;
- coloane = infrastructuri bancare / servicii.
""")

df = pd.DataFrame(
    default_matrix,
    columns=[f"y{i+1}" for i in range(6)],
    index=[f"x{i+1}" for i in range(6)]
)

edited_df = st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic"
)

# ============================================================
# CLASA ALGORITM
# ============================================================

class HungarianSeminar:

    def __init__(self, C):

        self.original = np.array(C, dtype=int)
        self.C = self.original.copy()
        self.n = len(C)

        self.steps = []

    def save_step(self, title):
        self.steps.append((title, self.C.copy()))

    # ------------------------------------------------------------

    def step1(self):

        rowmin = self.C.min(axis=1)

        for i in range(self.n):
            self.C[i] -= rowmin[i]

        self.save_step("Pas 1A - Scăderea minimelor pe linii")

        colmin = self.C.min(axis=0)

        for j in range(self.n):
            self.C[:, j] -= colmin[j]

        self.save_step("Pas 1B - Scăderea minimelor pe coloane")

    # ------------------------------------------------------------

    def label_zeros(self):

        zeros = [(i, j) for i in range(self.n)
                 for j in range(self.n) if self.C[i, j] == 0]

        selected = set()
        crossed = set()

        rows_left = set(range(self.n))

        while rows_left:

            zrows = {
                r: [z for z in zeros if z[0] == r
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

        return selected, crossed

    # ------------------------------------------------------------

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

    # ------------------------------------------------------------

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

    # ------------------------------------------------------------

    def solve(self):

        self.step1()

        while True:

            selected, crossed = self.label_zeros()

            if len(selected) == self.n:
                break

            cut_rows, cut_cols = self.step4(selected)

            self.step5(cut_rows, cut_cols)

        total = 0

        for i, j in selected:
            total += self.original[i, j]

        return selected, total

# ============================================================
# RULARE
# ============================================================

if st.button("🚀 Rulează Algoritmul Ungar"):

    matrix = edited_df.values

    solver = HungarianSeminar(matrix)

    selected, total = solver.solve()

    st.success("Algoritmul a fost executat cu succes.")

    # ========================================================
    # REZULTATE
    # ========================================================

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="metric-box">
        <h2>💰 Cost minim total</h2>
        <h1>{}</h1>
        </div>
        """.format(total), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="metric-box">
        <h2>🛡️ Resurse alocate</h2>
        <h1>{}</h1>
        </div>
        """.format(len(selected)), unsafe_allow_html=True)

    # ========================================================
    # CUPLAJ
    # ========================================================

    st.markdown("## 🔐 Cuplajul optim")

    for i, j in sorted(selected):

        cost = matrix[i][j]

        st.markdown(f"""
        <div class="bank-box">
        💳 Echipa <b>x{i+1}</b> protejează infrastructura <b>y{j+1}</b>
        <br>
        💵 Cost defensiv: <b>{cost}</b>
        </div>
        """, unsafe_allow_html=True)

    # ========================================================
    # PASI
    # ========================================================

    st.markdown("## 📊 Evoluția algoritmului")

    for title, mat in solver.steps:

        st.markdown(f"### {title}")

        df_step = pd.DataFrame(
            mat,
            columns=[f"y{i+1}" for i in range(solver.n)],
            index=[f"x{i+1}" for i in range(solver.n)]
        )

        st.dataframe(df_step, use_container_width=True)

    # ========================================================
    # GRAF BIPARTIT
    # ========================================================

    st.markdown("## 🌐 Graful bipartit al soluției")

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
        node_color='skyblue',
        node_size=2500
    )

    nx.draw_networkx_nodes(
        G,
        pos,
        nodelist=right_nodes,
        node_color='lightgreen',
        node_size=2500
    )

    nx.draw_networkx_edges(
        G,
        pos,
        width=3,
        edge_color='gold'
    )

    nx.draw_networkx_labels(
        G,
        pos,
        font_size=12,
        font_weight='bold'
    )

    plt.title(
        "Cuplajul optim al infrastructurii bancare",
        color="white",
        fontsize=16
    )

    plt.axis("off")

    st.pyplot(fig)

    st.balloons()

# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🏦 Sistem Bancar")

st.sidebar.markdown("""
### Despre aplicație

Aplicația modelează:
- centre de securitate;
- servere bancare;
- costuri defensive;
- infrastructuri critice.

### Tehnologii
- Streamlit
- NumPy
- NetworkX
- Matplotlib

### Algoritm utilizat
✔ Algoritmul Ungar
""")

st.sidebar.success("Securitatea infrastructurii este optimizată.")
