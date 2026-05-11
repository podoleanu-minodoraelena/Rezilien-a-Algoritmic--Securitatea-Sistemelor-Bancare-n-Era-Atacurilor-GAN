import streamlit as st
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd

# Clasa ta originală - LOGICA RĂMÂNE NEMODIFICATĂ
class HungarianSeminar:
    def __init__(self, C):
        self.original = np.array(C, dtype=int)
        self.C = self.original.copy()
        self.n = len(C)

    def show_st(self, title, selected=None, crossed=None, cut_rows=None, cut_cols=None, rowmins=None, colmins=None):
        st.write(f"#### 📑 {title}")
        
        display_matrix = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                v = self.C[i, j]
                if selected and (i, j) in selected:
                    cell = "⓪"
                elif crossed and (i, j) in crossed:
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
            st.write(f"**💰 MIN C:** `{list(colmins)}`")

        if cut_rows or cut_cols:
            c1, c2 = st.columns(2)
            if cut_rows: c1.error(f"Linii tăiate: {', '.join([f'l{i+1}' for i in sorted(cut_rows)])}")
            if cut_cols: c2.error(f"Coloane tăiate: {', '.join([f'c{j+1}' for j in sorted(cut_cols)])}")

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
            for zz in zeros:
                if zz != z and (zz[0] == z[0] or zz[1] == z[1]): crossed.add(zz)
            rows_left.remove(r)
        return selected, crossed

    def step4(self, selected, crossed):
        marked_rows = {i for i in range(self.n) if not any((i, j) in selected for j in range(self.n))}
        marked_cols = set()
        changed = True
        while changed:
            changed = False
            for i in marked_rows:
                for j in range(self.n):
                    if (i, j) in crossed and j not in marked_cols:
                        marked_cols.add(j); changed = True
            for j in marked_cols:
                for i in range(self.n):
                    if (i, j) in selected and i not in marked_rows:
                        marked_rows.add(i); changed = True
        cut_rows = set(range(self.n)) - marked_rows
        cut_cols = marked_cols
        self.show_st("Pas 3: Marcare suport minimal", selected, crossed, cut_rows, cut_cols)
        return cut_rows, cut_cols

    def solve(self):
        # ETAPA 1
        st.divider()
        st.subheader("🏦 Etapa 1: Reducerea Costurilor")
        rmin = self.C.min(axis=1)
        self.show_st("Minime pe linii", rowmins=rmin)
        for i in range(self.n): self.C[i] -= rmin[i]

        cmin = self.C.min(axis=0)
        self.show_st("Minime pe coloane", colmins=cmin)
        for j in range(self.n): self.C[:, j] -= cmin[j]

        iteration = 0
        while iteration < 10:
            iteration += 1
            st.divider()
            st.subheader(f"🔄 Iterația {iteration}")
            selected, crossed = self.label_zeros()
            self.show_st("Etichetare zerouri", selected, crossed)

            if len(selected) == self.n: break

            cut_rows, cut_cols = self.step4(selected, crossed)
            T1 = [self.C[i,j] for i in range(self.n) for j in range(self.n) if i not in cut_rows and j not in cut_cols]
            if not T1: break
            eps = min(T1)
            
            st.warning(f"💸 Ajustare costuri cu ε = {eps}")
            for i in range(self.n):
                for j in range(self.n):
                    if i not in cut_rows and j not in cut_cols: self.C[i, j] -= eps
                    elif i in cut_rows and j in cut_cols: self.C[i, j] += eps

        # FINAL
        st.divider()
        st.snow() # Efect de ninsoare (seamănă cu confetti/bani căzând)
        st.header("💎 Rezultat Optimizat")
        val = sum(self.original[i, j] for i, j in selected)
        sol = [f"(x{i+1}, y{j+1})" for i, j in sorted(selected)]
        
        c1, c2 = st.columns(2)
        c1.metric("Profit/Cost Final", f"{val} $")
        c2.success(f"Cuplaj Optim: {', '.join(sol)}")
        
        self.plot_graph(selected)

    def plot_graph(self, selected):
        G = nx.Graph()
        left = [f"x{i+1}" for i in range(self.n)]; right = [f"y{j+1}" for j in range(self.n)]
        G.add_nodes_from(left, bipartite=0); G.add_nodes_from(right, bipartite=1)
        G.add_edges_from([(f"x{i+1}", f"y{j+1}") for i, j in selected])
        pos = {**{n: (1, self.n-i) for i, n in enumerate(left)}, **{n: (2, self.n-i) for i, n in enumerate(right)}}
        fig, ax = plt.subplots(figsize=(8, 5))
        nx.draw(G, pos, with_labels=True, node_color=['#1f77b4']*self.n + ['#2ca02c']*self.n, 
                edge_color='#ff7f0e', width=3, node_size=1200)
        st.pyplot(fig)

# --- INTERFAȚĂ ---
st.set_page_config(page_title="Optimizare Ungară", page_icon="💸")
st.title("💸 Metoda Ungară: Optimizarea Alocării")

with st.expander("📖 Schema Logică"):
    st.image("schema_logica.png")

# Matricea ta default
def_mat = [[1, 7, 5, 9, 3, 4], [6, 7, 4, 8, 5, 1], [4, 6, 5, 7, 1, 4], 
           [8, 9, 3, 1, 2, 8], [5, 2, 2, 4, 6, 6], [5, 1, 2, 10, 6, 3]]

n = st.sidebar.number_input("Dimensiune", 2, 6, 6)
grid = []
st.write("### 🖋️ Matricea de Costuri")
for i in range(n):
    cols = st.columns(n)
    row = []
    for j in range(n):
        val = cols[j].number_input(f"x{i+1}y{j+1}", value=def_mat[i][j] if n==6 else 0, key=f"r{i}{j}", label_visibility="collapsed")
        row.append(val)
    grid.append(row)

if st.button("🚀 Calculează Profitul Maxim"):
    HungarianSeminar(grid).solve()
