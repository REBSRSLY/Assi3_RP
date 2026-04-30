import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configurazione Layout
st.set_page_config(page_title="Volley Dashboard", layout="wide")
df = df.replace('####', '100%')

st.title("🏐 Analisi Volley da Google Sheets")

# --- CONNESSIONE (Punto 2) ---
conn = st.connection("gsheets", type=GSheetsConnection)

df = conn.read(spreadsheet=st.secrets["public_gsheets_url"])

# Pulizia veloce: nell'immagine_0cd37e.png vedo colonne con nomi strani
# Rimuoviamo eventuali righe vuote o colonne totalmente nulle
df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)

st.sidebar.header("Filtri Dashboard")
lista_giocatori = df["Giocatore"].unique().tolist()
giocatore_scelto = st.sidebar.selectbox("Seleziona un Giocatore:", lista_giocatori)

df_giocatore = df[df["Giocatore"] == giocatore_scelto]

# --- Punto 3: Organizzazione con Container (Tabs) ---
tab_generale, tab_confronto, tab_visual = st.tabs(["Riepilogo", "Confronto Ruoli", "Grafici Avanzati"])

with tab_generale:
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

# Funzione per pulire le percentuali e renderle graficabili
def clean_pct(val):
    if isinstance(val, str):
        return float(val.replace('%', '').replace(',', '.'))
    return val

# Applichiamo la pulizia alle colonne delle percentuali
# Nota: Pandas rinomina le colonne duplicate come %, %.1, %.2, ecc.
# Basandoci sulla tua immagine, identifichiamo le colonne degli indici -, !, +
pct_columns = [col for col in df.columns if '%' in col]
for col in pct_columns:
    df[col] = df[col].apply(clean_pct)

st.title("🏐 Analisi Tecnica per Fondamentale")

# Lista dei 9 fondamentali basata sulla tua immagine
fondamentali = [
    "Battuta", "Ricezione", "Attacco", "Att dopo Ricez", 
    "Contrattacco", "Muro", "Difesa", "Free ball", "Alzata"
]

# --- SEZIONE GRAFICI AVANZATI ---
st.header("📈 Analisi Efficienza per Fondamentale")

# Punto 3: Organizzazione con Colonne (ne facciamo 3 per riga per averne 9 totali)
rows = [fondamentali[i:i + 3] for i in range(0, len(fondamentali), 3)]

for row in rows:
    cols = st.columns(3)
    for i, fond in enumerate(row):
        with cols[i]:
            st.subheader(f"{fond}")
            
            # Filtriamo i dati per il fondamentale specifico
            # Nota: se nel tuo DF la colonna Fondam. è vuota dopo la prima riga, 
            # dovresti usare df['Fondam.'].ffill() prima di questo passaggio
            df_fond = df[df['Fondam.'] == fond]
            
            if not df_fond.empty:
                # Punto 4: Charting Options (Bar Chart per confrontare i giocatori)
                # Visualizziamo la percentuale positiva '+' (solitamente la terza colonna % di ogni blocco)
                # Modifica l'indice della colonna in base a quale % vuoi visualizzare
                st.bar_chart(df_fond.set_index("Giocatore")[pct_columns[2]]) 
            else:
                st.info(f"Nessun dato per {fond}")

# Bonus: Expander per vedere i dati grezzi filtrati
with st.expander("Vedi Tabella Percentuali"):
    st.write(df[["Giocatore", "Fondam."] + pct_columns])
