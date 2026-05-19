import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# Configuração da interface
st.set_page_config(layout="wide", page_title="Simulador Macro: Economia Aberta")
st.title("Modelo Keynesiano Simplificado: Economia Aberta")

# --- Dicionário de Valores Padrão (Floats) ---
default_values = {
    'a': 100.0, 'b': 0.7, 'I_aut': 150.0, 'i': 0.05, 'd': 500.0, 
    'G': 200.0, 'T_aut': 50.0, 't': 0.2,
    'X_aut': 80.0, 'M_aut': 40.0, 'm': 0.1, 'E': 5.0, 'v': 20.0
}

if 'base_params' not in st.session_state:
    st.session_state.base_params = default_values.copy()

def calcular_modelo(p):
    # Efeito do câmbio no setor externo
    X_cambio = p['X_aut'] + (p['v'] * p['E'])
    M_cambio = max(0.0, p['M_aut'] - (p['v'] * 0.5 * p['E']))
    
    # Denominador (Multiplicador): 1 - b(1 - t) + m
    denominador = 1.0 - p['b'] * (1.0 - p['t']) + p['m']
    
    # Investimento considerando a sensibilidade (d) e os juros (i)
    I_total = p['I_aut'] - (p['d'] * p['i'])
    
    # Numerador (Componentes Autônomos)
    numerador = p['a'] - (p['b'] * p['T_aut']) + I_total + p['G'] + X_cambio - M_cambio
    
    y_eq = numerador / denominador
    return y_eq, I_total, denominador, X_cambio, M_cambio

# --- Sidebar: Controles com Number Input (+ e -) ---
st.sidebar.header("🕹️ Controles do Sistema")

if st.sidebar.button("🔄 Resetar Modelo (Padrão)"):
    st.session_state.base_params = default_values.copy()
    st.rerun()

st.sidebar.divider()

st.sidebar.subheader("🏠 Consumo e Investimento")
a = st.sidebar.number_input("Consumo Autônomo (a)", value=float(default_values['a']), step=10.0)
b = st.sidebar.number_input("Propensão Marginal (b)", value=float(default_values['b']), step=0.01, format="%.2f")
I_aut = st.sidebar.number_input("Investimento Autônomo (I_aut)", value=float(default_values['I_aut']), step=10.0)
taxa_juros = st.sidebar.number_input("Taxa de Juros (i) %", value=float(default_values['i']*100), step=0.5) / 100
d = st.sidebar.number_input("Sensibilidade aos Juros (d)", value=float(default_values['d']), step=50.0)

st.sidebar.subheader("🏛️ Setor Público")
G = st.sidebar.number_input("Gastos do Governo (G)", value=float(default_values['G']), step=10.0)
T_aut = st.sidebar.number_input("Tributo Autônomo (T_aut)", value=float(default_values['T_aut']), step=10.0)
t = st.sidebar.number_input("Alíquota de Imposto (t)", value=float(default_values['t']), step=0.01, format="%.2f")

st.sidebar.subheader("🌎 Setor Externo e Câmbio")
X_aut = st.sidebar.number_input("Exportação Autônoma (X_aut)", value=float(default_values['X_aut']), step=10.0)
M_aut = st.sidebar.number_input("Importação Autônoma (M_aut)", value=float(default_values['M_aut']), step=10.0)
E = st.sidebar.number_input("Taxa de Câmbio (E)", value=float(default_values['E']), step=0.1, format="%.1f")
m = st.sidebar.number_input("Propensão a Importar (m)", value=float(default_values['m']), step=0.01, format="%.2f")
v = st.sidebar.number_input("Sensibilidade ao Câmbio (v)", value=float(default_values['v']), step=1.0)

params = {
    'a': a, 'b': b, 'I_aut': I_aut, 'i': taxa_juros, 'd': d, 
    'G': G, 'T_aut': T_aut, 't': t, 
    'X_aut': X_aut, 'M_aut': M_aut, 
    'm': m, 'E': E, 'v': v
}

if st.sidebar.button("📌 Definir Atual como Referência"):
    st.session_state.base_params = params.copy()
    st.sidebar.success("Referência Gravada!")

# --- Processamento ---
y_eq_at, I_at, den_at, X_at, M_at_eff = calcular_modelo(params)
y_eq_bs, I_bs, den_bs, X_bs, M_bs_eff = calcular_modelo(st.session_state.base_params)

y_max = max(y_eq_at, y_eq_bs, 1000.0) * 1.3
y_range = np.linspace(0, y_max, 250)

def gerar_curvas(p, yr, X_eff, M_eff):
    T = p['T_aut'] + p['t'] * yr
    C = p['a'] + p['b'] * (yr - T)
    I = p['I_aut'] - (p['d'] * p['i'])
    M = M_eff + p['m'] * yr
    DA = C + I + p['G'] + X_eff - M
    Vaz = ((yr - T) - C) + T + M
    Inj = I + p['G'] + X_eff
    return DA, Vaz, Inj, C

da_at, vaz_at, inj_at, c_at = gerar_curvas(params, y_range, X_at, M_at_eff)
da_bs, vaz_bs, inj_bs, c_bs = gerar_curvas(st.session_state.base_params, y_range, X_bs, M_bs_eff)

# --- Visualização ---
fig, ax = plt.subplots(figsize=(12, 7))

# Referência (Cinza pontilhado)
ax.plot(y_range, da_bs, color="gray", alpha=0.4, label="DA Referência")
ax.axvline(y_eq_bs, color="gray", linestyle="--", alpha=0.3)

# Atual (Sólido)
ax.plot(y_range, da_at, color="#1f77b4", lw=3, label="Demanda Agregada Atual (C+I+G+NX)")
ax.plot(y_range, c_at, color="#2ca02c", lw=2, label="Consumo (C)") 
ax.plot(y_range, vaz_at, color="#ff7f0e", lw=1.5, label="Vazamentos (S+T+M)")
ax.axhline(inj_at, color="#9467bd", lw=1.5, label="Injeções (I+G+X)")
ax.plot(y_range, y_range, color="black", alpha=0.2, linestyle="--", label="Y = DA (45°)")

# Ponto de Equilíbrio
ax.scatter(y_eq_at, y_eq_at, color="red", s=100, zorder=5, label=f"Equilíbrio: {y_eq_at:.1f}")

ax.set_title("Simulador Keynesiano: Economia Aberta", fontsize=16)
ax.set_xlabel("Renda Nacional (Y)")
ax.set_ylabel("DA / Injeções / Vazamentos")
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
ax.grid(True, alpha=0.15)

st.pyplot(fig)

# --- Métricas ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Renda de Equilíbrio (Y*)", f"{y_eq_at:.2f}", f"{y_eq_at - y_eq_bs:.2f}")
m2.metric("Multiplicador Aberto", f"{1/den_at:.2f}")
m3.metric("Balança Comercial (NX)", f"{X_at - (M_at_eff + m*y_eq_at):.2f}")
m4.metric("Investimento Realizado (I)", f"{I_at:.2f}")

st.caption("Fórmulas: C = a + b(Y - T) | I = I_aut - d*i | T = T_aut + t*Y | M = M_aut + m*Y | DA = C + I + G + X - M")
