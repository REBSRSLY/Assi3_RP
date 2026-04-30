import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configurazione Layout
st.set_page_config(page_title="Volley Dashboard", layout="wide")

st.title("🏐 Analisi Volley da Google Sheets")

# --- CONNESSIONE (Punto 2) ---
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(spreadsheet=st.secrets["https://docs.google.com/spreadsheets/d/16s_hXDtp5s8rkjFvoiD5JLrAXs8f-TKywNJSN3TzbAk/edit?usp=sharing"])

# Pulizia veloce: nell'immagine_0cd37e.png vedo colonne con nomi strani
# Rimuoviamo eventuali righe vuote o colonne totalmente nulle
df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)

st.sidebar.header("Filtri Dashboard")
lista_giocatori = df["Giocatore"].unique().tolist()
giocatore_scelto = st.sidebar.selectbox("Seleziona un Giocatore:", lista_giocatori)

df_giocatore = df[df["Giocatore"] == giocatore_scelto]

# --- Punto 3: Organizzazione con Container (Tabs) ---
tab_generale, tab_confronto, tab_visual = st.tabs(["📊 Riepilogo", "⚔️ Confronto Ruoli", "📈 Grafici Avanzati"])

with tab_generale:
    # Punto 3: Uso di Colonne
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Totale Azioni", df_giocatore["Tot"].iloc[0])
    with col2:
        st.metric("Efficienza (E%)", df_giocatore["*E%"].iloc[0])
    with col3:
        st.metric("Performance (pC)", df_giocatore["pC"].iloc[0])

    st.divider()
    st.subheader(f"Statistiche complete per {giocatore_scelto}")
    st.dataframe(df_giocatore)

with tab_confronto:
    st.header("Analisi per Ruolo")
    with st.expander("Clicca per vedere la tabella per Ruolo"):
        ruolo_stats = df.groupby("Ruolo")["Tot"].sum().reset_index()
        st.table(ruolo_stats)
    
    # Punto 4: Bar Chart (Istogramma)
    st.subheader("Carico di lavoro per Ruolo (Totale azioni)")
    st.bar_chart(data=df, x="Ruolo", y="Tot")

with tab_visual:
    st.header("Visualizzazioni Dettagliate")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("Distribuzione Errori")
        # Punto 4: Area Chart
        st.area_chart(df.set_index("Giocatore")["#ERROR!"])
        
    with col_b:
        st.subheader("Efficienza Indice")
        # Punto 4: Line Chart
        st.line_chart(df.set_index("Giocatore")["Ind"])
