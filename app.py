import streamlit as st
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Configurare pagină
st.set_page_config(page_title="Algoritmul Ungar", layout="wide")

class HungarianStreamlit:
    def __init__(self, C):
        self.original = np.array(C, dtype=int)
        self.C = self.original.copy()
        self.n = len(C)

    def show_st(self, title, selected=None, crossed=None, cut_rows=None, cut_cols=None):
        st.write(f"#### {title}")
        
        # Creăm un tabel colorat pentru browser
        df = pd.DataFrame(self.C, 
                          index=[f"x{i+1}" for i in range(self.n)],
                          columns=[f"y{j+1}" for j in range(self.n)])
        
        # Afișăm matricea
        st.table(df)
        
        if cut_rows or cut_cols:
            res = []
            if cut_rows: res.append(f"Linii tăiate: {', '.join([f'l{r+1}' for r in cut_rows])}")
            if cut_cols: res.append(f"Coloane tăiate: {', '.join([f'c{c+1}' for c in cut_cols])}")
            st.info(" | ".join(res))

    def label_zeros(self):
        zeros = [(i, j) for i in range(self.n) if self.C[i, j] == 0]
        selected, crossed = set(), set()
        rows_left = set(range(self.n))
        while rows_left:
            zrows = {r: [z for z in zeros if z[0] == r and z not in selected and z not in crossed] for r in rows_left}
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

    def solve(self):
        # Pas 1
        row_mins = self.C.min(axis=1)
        for i in range(self.n): self.C[i] -= row_mins[i]
        col_mins = self.C.min(axis=0)
        for j in range(self.n): self.C[:, j] -= col_mins[j]
        
        self.show_st("Matricea după reducerea costurilor (Pas 1)", None, None)

        iteration = 0
        while True:
            iteration += 1
            st.markdown(f"---")
            st.subheader(f"Iterația {iteration}")
            
            selected, crossed = self.label_zeros()
            n0 = len(selected)
            
            self.show_st("Etichetare zerouri (Pas 2)", selected, crossed)

            if n0 == self.n:
                return selected

            # Pas 3 & 4 (Marcare și Deplasare)
            marked_rows = {i for i in range(self.n) if not any((i, j) in selected for j in range(self.n))}
            marked_cols = set()
            changed = True
            while changed:
                changed = False
                for i in marked_rows:
                    for j in range(self.n):
                        if self.C[i,j] == 0 and (i,j) not in selected and j not in marked_cols:
                            marked_cols.add(j); changed = True
                for j in marked_cols:
                    for i in range(self.n):
                        if (i, j) in selected and i not in marked_rows:
                            marked_rows.add(i); changed = True
            
            cut_rows = set(range(self.n)) - marked_rows
            cut_cols = marked_cols
            
            # Deplasare
            T1 = [self.C[i,j] for i in range(self.n) for j in range(self.n) if i not in cut_rows and j not in cut_cols]
            eps = min(T1)
            for i in range(self.n):
                for j in range(self.n):
                    if i not in cut_rows and j not in cut_cols: self.C[i,j] -= eps
                    elif i in cut_rows and j in cut_cols: self.C[i,j] += eps
            
            st.write(f"Epsilon găsit: **{eps}**")

    def plot_graph(self, selected):
        G = nx.Graph()
        left = [f"x{i+1}" for i in range(self.n)]
        right = [f"y{j+1}" for j in range(self.n)]
        G.add_nodes_from(left, bipartite=0)
        G.add_nodes_from(right, bipartite=1)
        edges = [(f"x{i+1}", f"y{j+1}") for i, j in selected]
        G.add_edges_from(edges)
        pos = {**{n: (1, self.n-i) for i, n in enumerate(left)}, **{n: (2, self.n-i) for i, n in enumerate(right)}}
        fig, ax = plt.subplots(figsize=(6, 4))
        nx.draw(G, pos, with_labels=True, node_color=['skyblue']*self.n + ['lightgreen']*self.n, edge_color='red', width=2)
        st.pyplot(fig)

# --- INTERFAȚA STREAMLIT ---
st.title("🧩 Rezolvare: Metoda Ungară")

# Cerința profei: Schema logică e aici
with st.expander("Vezi Schema Logică a Algoritmului"):
    try:
        st.image("schema_logica.png")
    except:
        st.warning("Urcă fișierul schema_logica.png pe GitHub!")

st.sidebar.header("Setări Matrice")
n_val = st.sidebar.number_input("Dimensiune (n)", 2, 8, 3)

st.write("### Introduceți valorile matricei:")
grid = []
for i in range(n_val):
    cols = st.columns(n_val)
    row_vals = []
    for j in range(n_val):
        val = cols[j].number_input(f"x{i+1}, y{j+1}", value=0, key=f"{i}_{j}", label_visibility="collapsed")
        row_vals.append(val)
    grid.append(row_vals)

if st.button("🚀 Calculează Soluția"):
    solver = HungarianStreamlit(grid)
    final_selected = solver.solve()
    
    st.markdown("---")
    st.header("🏆 Rezultat Final")
    val_total = sum(solver.original[i,j] for i, j in final_selected)
    st.success(f"Valoarea optimă V(W_max) = {val_total}")
    solver.plot_graph(final_selected)