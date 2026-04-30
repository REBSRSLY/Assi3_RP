import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# 1. Configurazione Layout
st.set_page_config(page_title="Volley Dashboard", layout="wide")

# 2. Connessione ai dati (Punto 2)
conn = st.connection("gsheets", type=GSheetsConnection)
df_raw = conn.read(spreadsheet=st.secrets["public_gsheets_url"])

# --- PULIZIA DATI ---
# Rimuoviamo righe/colonne vuote e sistemiamo l'errore ####
df = df_raw.dropna(how='all', axis=0).dropna(how='all', axis=1).copy()
df = df.replace('####', '100%')

# Riempliamo i nomi dei fondamentali (fondamentale per i 9 grafici)
if 'Fondam.' in df.columns:
    df['Fondam.'] = df['Fondam.'].ffill()

# Funzione per pulire le percentuali
def clean_pct(val):
    if isinstance(val, str):
        return float(val.replace('%', '').replace(',', '.'))
    return val

# Identifichiamo le colonne delle percentuali e le convertiamo in numeri
pct_columns = [col for col in df.columns if '%' in col]
for col in pct_columns:
    df[col] = df[col].apply(clean_pct)

# --- INTERFACCIA UTENTE (Bonus: Interattività) ---
st.title("🏐 Volley Performance Analytics")

st.sidebar.header("Filtri")
lista_giocatori = df["Giocatore"].unique().tolist()
giocatore_scelto = st.sidebar.selectbox("Seleziona un Giocatore per il Riepilogo:", lista_giocatori)

# --- ORGANIZZAZIONE IN CONTAINER (Punto 3) ---
tab_generale, tab_confronto, tab_visual = st.tabs(["📊 Riepilogo", "👥 Confronto Ruoli", "📈 Analisi Fondamentali"])

with tab_generale:
    df_giocatore = df[df["Giocatore"] == giocatore_scelto]
    if not df_giocatore.empty:
        col1, col2, col3 = st.columns(3)
        # Usiamo i dati reali dalle tue colonne (Immagine 0cd37e.png)
        col1.metric("Totale Azioni", int(df_giocatore["Tot"].sum()))
        col2.metric("Indice Efficienza", df_giocatore["Ind"].iloc[0])
        col3.metric("Performance (pC)", df_giocatore["pC"].iloc[0])
        
        st.divider()
        st.subheader(f"Dettaglio azioni: {giocatore_scelto}")
        st.dataframe(df_giocatore)

with tab_confronto:
    st.header("Carico di lavoro per Ruolo")
    # Punto 4: Bar Chart
    ruolo_stats = df.groupby("Ruolo")["Tot"].sum().reset_index()
    st.bar_chart(data=ruolo_stats, x="Ruolo", y="Tot")
    
    with st.expander("Vedi tabella dati per ruolo"):
        st.table(ruolo_stats)

with tab_visual:
    st.header("Efficienza Positiva (+) per Fondamentale")
    
    fondamentali = [
        "Battuta", "Ricezione", "Attacco", "Att dopo Ricez", 
        "Contrattacco", "Muro", "Difesa", "Free ball", "Alzata"
    ]
    
    # Punto 3 & 4: 9 Grafici organizzati in griglia 3x3
    rows = [fondamentali[i:i + 3] for i in range(0, len(fondamentali), 3)]
    
    for row in rows:
        cols = st.columns(3)
        for i, fond in enumerate(row):
            with cols[i]:
                st.markdown(f"**{fond}**")
                df_fond = df[df['Fondam.'] == fond]
                
                if not df_fond.empty:
                    # Visualizziamo la terza colonna percentuale (quella del '+')
                    # pct_columns[2] corrisponde alla colonna '+ %'
                    st.bar_chart(df_fond.set_index("Giocatore")[pct_columns[2]])
                else:
                    st.caption("Nessun dato")

with st.expander("🔍 Ispeziona Database Completo (Percentuali Pulite)"):
    st.dataframe(df)
