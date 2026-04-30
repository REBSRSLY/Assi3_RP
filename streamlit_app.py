import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Volley Stats R-W", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(spreadsheet=st.secrets["public_gsheets_url"])

df = df_raw.iloc[:, [0, 1, 2, 3, 4] + list(range(17, 23))].copy() # (Colonne R a W) In pandas, se il foglio inizia dalla colonna A (0), le colonne R:W sono gli indici 17:23

# R=Impr(val), S=Impr(%), T=Err(val), U=Err(%), V=Buono(val), W=Buono(%)
df.columns = list(df.columns[:5]) + ["Impr_val", "Impr_pct", "Err_val", "Err_pct", "Buono_val", "Buono_pct"]
df = df.replace('####', '100%')

if 'Fondam.' in df.columns:
    df['Fondam.'] = df['Fondam.'].ffill()

def clean_pct(val):
    if pd.isna(val): return 0.0
    val_str = str(val).replace('%', '').replace(',', '.').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

for col in ["Impr_pct", "Err_pct", "Buono_pct"]:
    df[col] = df[col].apply(clean_pct)

# INTERFACCIA
st.title("🏐 Analisi Tecnica (Range R:W)")

tab1, tab2 = st.tabs(["9 Grafici Fondamentali", "Dati Estratti"])

with tab1:
    fondamentali = ["Battuta", "Ricezione", "Attacco", "Att dopo Ricez", 
                    "Contrattacco", "Muro", "Difesa", "Free ball", "Alzata"]
    
    # 9 fondamentali
    for i in range(0, len(fondamentali), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(fondamentali):
                fond = fondamentali[i + j]
                with cols[j]:
                    st.subheader(fond)
                    df_fond = df[df['Fondam.'] == fond]
                    if not df_fond.empty:
                        # Usiamo la colonna 'Buono_pct' (derivata dalla colonna W)
                        st.bar_chart(df_fond.set_index("Giocatore")["Buono_pct"])
                    else:
                        st.caption("Nessun dato")

with tab2:
    st.write("Dati filtrati (Colonne R-W originali):")
    st.dataframe(df)

# Bonus
st.sidebar.header("Dettaglio Giocatore")
player = st.sidebar.selectbox("Scegli:", df["Giocatore"].unique())
df_p = df[df["Giocatore"] == player]
st.sidebar.write(df_p[["Fondam.", "Impr_pct", "Err_pct", "Buono_pct"]])
