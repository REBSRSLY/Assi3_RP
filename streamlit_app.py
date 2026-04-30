import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Volley Dashboard", layout="wide")

# Connessione
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(spreadsheet=st.secrets["public_gsheets_url"])

# Copia e pulizia iniziale
df = df_raw.copy()
df = df.replace('####', '100%')

# Riempimento fondamentali (fondamentale per i 9 grafici)
if 'Fondam.' in df.columns:
    df['Fondam.'] = df['Fondam.'].ffill()

# Nuova funzione di pulizia robusta
def clean_pct(val):
    if val is None or pd.isna(val): return 0.0
    val_str = str(val).replace('%', '').replace(',', '.').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

# Applichiamo la pulizia solo alle colonne che contengono '%' nel nome
pct_columns = [col for col in df.columns if '%' in str(col)]
for col in pct_columns:
    df[col] = df[col].apply(clean_pct)

st.title("🏐 Analisi Tecnica Volley")

# --- ORGANIZZAZIONE TABS ---
tab_riepilogo, tab_fondamentali = st.tabs(["📊 Riepilogo", "📈 Analisi Fondamentali"])

with tab_riepilogo:
    st.subheader("Database Completo")
    st.dataframe(df)

with tab_fondamentali:
    fondamentali = ["Battuta", "Ricezione", "Attacco", "Att dopo Ricez", 
                    "Contrattacco", "Muro", "Difesa", "Free ball", "Alzata"]
    
    # Griglia 3x3
    for i in range(0, len(fondamentali), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(fondamentali):
                fond = fondamentali[i + j]
                with cols[j]:
                    st.markdown(f"**{fond}**")
                    df_fond = df[df['Fondam.'] == fond]
                    if not df_fond.empty:
                        # Usiamo la terza colonna percentuale disponibile (+ %)
                        col_da_usare = pct_columns[2] if len(pct_columns) > 2 else pct_columns[0]
                        st.bar_chart(df_fond.set_index("Giocatore")[col_da_usare])
