import streamlit as st
import numpy as np
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

    def show_st(self, title, selected=None, crossed=None, cut_rows=None, cut_cols=None, rowmins=None, colmins=None):
        st.write(f"#### 📋 {title}")
        
        # Construim matricea pentru afișare [cite: 3, 5, 6]
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
        if rowmins is not None: 
            cols_names.append("MIN L")
        
        df = pd.DataFrame(display_matrix, 
                          index=[f"x{i+1}" for i in range(self.n)], 
                          columns=cols_names)
        
        st.dataframe(df.style.set_properties(**{'text-align': 'center', 'font-size': '18px'}))

        if colmins is not None:
            st.write(f"**📉 MIN C:** `{list(colmins)}`")

        if cut_rows or cut_cols:
            cols = st.columns(2)
            if cut_rows: cols[0].error(f"Linii tăiate: {', '.join([f'l{i+1}' for i in sorted(cut_rows)])}")
            if cut_cols: cols[1].error(f"Coloane tăiate: {', '.join([f'c{j+1}' for j in sorted(cut_cols)])}")

    def solve(self):
        # Pas 1 - Reducere [cite: 10, 11]
        st.divider()
        st.subheader("🏁 Etapa 1: Pregătirea matricii")
        rowmin = self.C.min(axis=1)
        self.show_st("Reducere pe linii", rowmins=rowmin)
        for i in range(self.n): self.C[i] -= rowmin[i]

        colmin = self.C.min(axis=0)
        self.show_st("Reducere pe coloane (Matricea Redusă)", colmins=colmin)
        for j in range(self.n): self.C[:, j] -= colmin[j]

        iteration = 0
        while iteration < 10:
            iteration += 1
            st.divider()
            st.subheader(f"🔄 Iterația {iteration}")
            
            selected, crossed = self.label_zeros() [cite: 12]
            n0 = len(selected)
            self.show_st("Etichetare zerouri", selected, crossed) [cite: 16]

            if n0 == self.n:
                break

            # Marcare și Deplasare [cite: 17, 21]
            cut_rows, cut_cols = self.step4(selected, crossed)
            
            T1 = [self.C[i,j] for i in range(self.n) for j in range(self.n) if i not in cut_rows and j not in cut_cols]
            if not T1: break
            eps = min(T1)
            
            st.warning(f"S-a ales valoarea minimă neacoperită: ε = {eps}")
            for i in range(self.n):
                for j in range(self.n):
                    if i not in cut_rows and j not in cut_cols: self.C[i, j] -= eps
                    elif i in cut_rows and j in cut_cols: self.C[i, j] += eps
            self.show_st("Matricea după deplasarea zerourilor")

        # Soluția finală [cite: 30, 31]
        st.divider()
        st.balloons()
        st.header("🏆 Rezultate Finale")
        val = sum(self.original[i, j] for i, j in selected)
        sol = [f"(x{i+1}, y{j+1})" for i, j in sorted(selected)]
        
        c1, c2 = st.columns(2)
        c1.metric("Valoare Optimă V(W_max)", val)
        c2.write("**Muchii selectate:**")
        c2.info(", ".join(sol))
        
        st.write("#### 🕸️ Vizualizare Graf Bipartit")
        self.plot_bipartite_graph(selected)

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
        self.show_st("Procedura de marcare (Suport Minimal)", selected, crossed, cut_rows, cut_cols)
        return cut_rows, cut_cols

    def plot_bipartite_graph(self, selected):
        G = nx.Graph()
        left = [f"x{i+1}" for i in range(self.n)]
        right = [f"y{j+1}" for j in range(self.n)]
        G.add_nodes_from(left, bipartite=0)
        G.add_nodes_from(right, bipartite=1)
        G.add_edges_from([(f"x{i+1}", f"y{j+1}") for i, j in selected])
        pos = {**{n: (1, self.n-i) for i, n in enumerate(left)}, **{n: (2, self.n-i) for i, n in enumerate(right)}}
        fig, ax = plt.subplots(figsize=(8, 5))
        nx.draw(G, pos, with_labels=True, node_color=['#3498db']*self.n + ['#2ecc71']*self.n, 
                edge_color='#e74c3c', width=2, node_size=1000, font_weight='bold')
        st.pyplot(fig)

# --- UI STREAMLIT ---
st.set_page_config(page_title="Metoda Ungară", page_icon="🧩", layout="centered")
st.title("🧩 Algorirmul Ungar")

# Secțiune dedicată schemei logice
with st.expander("📖 Vezi Schema Logică și Explicația Algoritmului"):
    st.write("Algoritmul urmează pașii clasici ai Metodei Ungare pentru optimizarea costurilor:")
    
    st.image("schema_logica.png", caption="Fluxul logic al implementării")

st.sidebar.header("⚙️ Configurare")
n = st.sidebar.number_input("Dimensiunea matricei (n)", 2, 8, 3)

st.write("### 🖋️ Introdu matricea de costuri:")
grid = []
for i in range(n):
    cols = st.columns(n)
    row = []
    for j in range(n):
        val = cols[j].number_input(f"x{i+1}, y{j+1}", value=0, key=f"r{i}c{j}", label_visibility="collapsed")
        row.append(val)
    grid.append(row)

if st.button("🚀 Lansează Calculele"):
    solver = HungarianSeminar(grid)
    solver.solve()
