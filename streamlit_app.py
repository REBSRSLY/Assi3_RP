import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configurazione Layout
st.set_page_config(page_title="Volley Analysis Dashboard", layout="wide")

# 2. Connessione ai dati
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(spreadsheet=st.secrets["public_gsheets_url"])

# --- PULIZIA E PREPARAZIONE DATI ---
df = df_raw.copy()
# Sostituiamo l'errore di formattazione #### con 100%
df = df.replace('####', '100%')

# Riempimento dei fondamentali per riga (necessario per filtrare i 9 grafici)
if 'Fondam.' in df.columns:
    df['Fondam.'] = df['Fondam.'].ffill()

# Funzione robusta per convertire le stringhe "%" in numeri utilizzabili dai grafici
def clean_pct(val):
    if val is None or pd.isna(val): return 0.0
    # Gestione di casi non numerici (come intestazioni ripetute nel foglio)
    val_str = str(val).replace('%', '').replace(',', '.').strip()
    try:
        return float(val_str)
    except ValueError:
        return 0.0

# Identifichiamo le colonne delle percentuali nel giusto ordine
# Pandas rinomina i duplicati come %, %.1, %.2
pct_columns = [col for col in df.columns if '%' in str(col)]
for col in pct_columns:
    df[col] = df[col].apply(clean_pct)

# Mappatura corretta in base alla tua indicazione:
# pct_columns[0] -> Imprecise (-)
# pct_columns[1] -> Errori (!)
# pct_columns[2] -> Buone (+)

st.title("🏐 Dashboard Tecnica Pallavolo")

# --- ORGANIZZAZIONE IN CONTAINER (Tabs e Columns) ---
tab_riepilogo, tab_fondamentali = st.tabs(["📊 Riepilogo Giocatore", "📈 Analisi per Fondamentale"])

with tab_riepilogo:
    # Bonus: Componente interattivo per filtrare il giocatore
    giocatore_scelto = st.selectbox("Seleziona un Giocatore:", df["Giocatore"].unique())
    df_gioc = df[df["Giocatore"] == giocatore_scelto]
    
    col1, col2, col3 = st.columns(3)
    if not df_gioc.empty:
        # Visualizziamo le percentuali medie del giocatore scelto nelle tre categorie
        col1.metric("Media Imprecise (-)", f"{df_gioc[pct_columns[0]].mean():.1f}%")
        col2.metric("Media Errori (!)", f"{df_gioc[pct_columns[1]].mean():.1f}%")
        col3.metric("Media Buone (+)", f"{df_gioc[pct_columns[2]].mean():.1f}%")
    
    st.divider()
    st.dataframe(df_gioc)

with tab_fondamentali:
    st.header("Analisi Efficienza (+) per ogni Fondamentale")
    
    fondamentali = ["Battuta", "Ricezione", "Attacco", "Att dopo Ricez", 
                    "Contrattacco", "Muro", "Difesa", "Free ball", "Alzata"]
    
    # 3. & 4. Organizzazione in griglia 3x3 con grafici a barre
    for i in range(0, len(fondamentali), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(fondamentali):
                fond = fondamentali[i + j]
                with cols[j]:
                    st.subheader(f"{fond}")
                    df_fond = df[df['Fondam.'] == fond]
                    
                    if not df_fond.empty:
                        # Utilizziamo la terza percentuale (Palle Buone +) come richiesto
                        st.bar_chart(df_fond.set_index("Giocatore")[pct_columns[2]])
                    else:
                        st.caption("Dati non disponibili")

with st.expander("🔍 Legenda e Dati Raw"):
    st.write("Le colonne percentuali sono state mappate come segue:")
    st.write("- **%**: Imprecise | **% .1**: Errori | **% .2**: Buone (+)")
    st.dataframe(df)
