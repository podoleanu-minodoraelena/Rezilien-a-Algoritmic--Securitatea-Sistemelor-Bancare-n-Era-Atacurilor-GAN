import streamlit as st
import numpy as np
from copy import deepcopy
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

class HungarianSeminar:
    def __init__(self, C):
        self.original = np.array(C, dtype=int)
        self.C = self.original.copy()
        self.n = len(C)

        self.row_mins = []
        self.col_mins = []
        self.eps = []
        self.n0_hist = []

    # ============================================================
    # AFISARE (Adaptată pentru Streamlit)
    # ============================================================
    def show(self, title="", selected=None, crossed=None,
             cut_rows=None, cut_cols=None,
             marked_rows=None, marked_cols=None,
             rowmins=None, colmins=None):

        if selected is None: selected = set()
        if crossed is None: crossed = set()
        if cut_rows is None: cut_rows = set()
        if cut_cols is None: cut_cols = set()

        st.write(f"#### {title}")
        
        # Creăm o matrice vizuală folosind caracterele tale speciale
        display_matrix = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                v = self.C[i, j]
                if (i, j) in selected:
                    cell = "⓪"
                elif (i, j) in crossed:
                    cell = "✗"
                else:
                    cell = str(v)
                row.append(cell)
            
            if rowmins is not None:
                row.append(f"({rowmins[i]})")
            display_matrix.append(row)

        cols_names = [f"y{j+1}" for j in range(self.n)]
        if rowmins is not None: cols_names.append("MIN L")
        
        df = pd.DataFrame(display_matrix, 
                          index=[f"x{i+1}" for i in range(self.n)], 
                          columns=cols_names)
        st.table(df)

        if colmins is not None:
            st.write(f"**MIN C:** {list(colmins)}")

        if cut_rows or cut_cols:
            if cut_rows: st.info(f"Linii tăiate: {[f'l{i+1}' for i in sorted(cut_rows)]}")
            if cut_cols: st.info(f"Coloane tăiate: {[f'c{j+1}' for j in sorted(cut_cols)]}")

    def step1(self):
        st.markdown("### PAS 1 - Crearea zerourilor")
        rowmin = self.C.min(axis=1)
        self.row_mins.append(rowmin.copy())
        self.show("Matrice initiala (Reducere linii)", rowmins=rowmin)

        for i in range(self.n):
            self.C[i] -= rowmin[i]

        colmin = self.C.min(axis=0)
        self.col_mins.append(colmin.copy())
        self.show("Dupa scaderea minimelor pe linii (Reducere coloane)", colmins=colmin)

        for j in range(self.n):
            self.C[:, j] -= colmin[j]

        self.show("Matrice dupa Pasul 1")

    def label_zeros(self):
        zeros = [(i, j) for i in range(self.n)
                 for j in range(self.n) if self.C[i, j] == 0]
        selected = set()
        crossed = set()
        rows_left = set(range(self.n))

        while rows_left:
            zrows = {r: [z for z in zeros if z[0] == r and z not in selected and z not in crossed]
                for r in rows_left}
            zrows = {r: z for r, z in zrows.items() if z}
            if not zrows: break
            r = min(zrows, key=lambda x: len(zrows[x]))
            z = zrows[r][0]
            selected.add(z)
            rr, cc = z
            for zz in zeros:
                if zz != z and (zz[0] == rr or zz[1] == cc):
                    crossed.add(zz)
            rows_left.remove(r)
        return selected, crossed

    def step3(self):
        selected, crossed = self.label_zeros()
        self.show("PAS 2 - Procedura de etichetare", selected, crossed)
        return selected, crossed

    def step4(self, selected, crossed):
        marked_rows = {i for i in range(self.n)
            if not any((i, j) in selected for j in range(self.n))}
        marked_cols = set()
        changed = True
        while changed:
            changed = False
            for i in marked_rows:
                for j in range(self.n):
                    if (i, j) in crossed and j not in marked_cols:
                        marked_cols.add(j)
                        changed = True
            for j in marked_cols:
                for i in range(self.n):
                    if (i, j) in selected and i not in marked_rows:
                        marked_rows.add(i)
                        changed = True
        cut_rows = set(range(self.n)) - marked_rows
        cut_cols = marked_cols
        self.show("PAS 3 - Procedura de marcare (suport minimal)", selected, crossed, cut_rows, cut_cols)
        return cut_rows, cut_cols

    def step5(self, cut_rows, cut_cols):
        T1 = []
        for i in range(self.n):
            for j in range(self.n):
                cuts = int(i in cut_rows) + int(j in cut_cols)
                if cuts == 0:
                    T1.append(self.C[i, j])

        if not T1: return # Safety break
        eps = min(T1)
        self.eps.append(eps)
        for i in range(self.n):
            for j in range(self.n):
                cuts = int(i in cut_rows) + int(j in cut_cols)
                if cuts == 0: self.C[i, j] -= eps
                elif cuts == 2: self.C[i, j] += eps

        st.warning(f"ε = {eps}")
        self.show("PAS 4 - Dupa deplasarea zerourilor")

    def plot_bipartite_graph(self, selected):
        G = nx.Graph()
        left_nodes = [f"x{i + 1}" for i in range(self.n)]
        right_nodes = [f"y{j + 1}" for j in range(self.n)]
        G.add_nodes_from(left_nodes, bipartite=0)
        G.add_nodes_from(right_nodes, bipartite=1)
        edges = [(f"x{i + 1}", f"y{j + 1}") for i, j in selected]
        G.add_edges_from(edges)

        pos = {}
        pos.update((node, (1, self.n - 1 - index)) for index, node in enumerate(left_nodes))
        pos.update((node, (2, self.n - 1 - index)) for index, node in enumerate(right_nodes))

        fig, ax = plt.subplots(figsize=(8, 6))
        nx.draw_networkx_nodes(G, pos, nodelist=left_nodes, node_color='skyblue', node_size=800)
        nx.draw_networkx_nodes(G, pos, nodelist=right_nodes, node_color='lightgreen', node_size=800)
        nx.draw_networkx_edges(G, pos, width=2, edge_color='red')
        nx.draw_networkx_labels(G, pos, font_size=12)
        plt.axis('off')
        st.pyplot(fig)

    def solve(self):
        self.step1()
        iteration = 0
        while iteration < 10: # Limită de siguranță pentru web
            iteration += 1
            st.divider()
            st.subheader(f"ITERATIA {iteration}")
            selected, crossed = self.step3()
            n0 = len(selected)
            if n0 == self.n: break
            cut_rows, cut_cols = self.step4(selected, crossed)
            self.step5(cut_rows, cut_cols)

        st.success("### PAS 5 - Solutia finala (W_max)")
        val = 0
        sol = []
        for i, j in sorted(selected):
            sol.append(f"(x{i + 1},y{j + 1})")
            val += self.original[i, j]
        
        st.write(f"**W_max** = {{{', '.join(sol)}}}")
        st.write(f"**V(W_max)** = {val}")
        self.plot_bipartite_graph(selected)

# ============================================================
# INTERFAȚA STREAMLIT (Înlocuiește Citirea de la Tastatură)
# ============================================================
st.set_page_config(page_title="Metoda Ungară", layout="wide")
st.title("🧩 Rezolvare Algoritm Ungar")

n = st.sidebar.number_input("Dimensiunea matricei n", min_value=2, max_value=10, value=3)

st.write(f"Introduceți valorile pentru matricea {n}x{n}:")
input_matrix = []
for i in range(n):
    cols = st.columns(n)
    row_data = []
    for j in range(n):
        val = cols[j].number_input(f"x{i+1}, y{j+1}", value=0, key=f"r{i}c{j}", label_visibility="collapsed")
        row_data.append(val)
    input_matrix.append(row_data)

if st.button("🚀 Calculează"):
    solver = HungarianSeminar(input_matrix)
    solver.solve()
