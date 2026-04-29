import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Creazione della connessione
conn = st.connection("gsheets", type=GSheetsConnection)

# Lettura dei dati (usa il nome del foglio se necessario)
df = conn.read(spreadsheet="Assi3RP")

st.write("Ecco i dati dal mio Google Sheet:")
st.dataframe(df)
