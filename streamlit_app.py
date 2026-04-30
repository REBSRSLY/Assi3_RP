import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Creazione della connessione
conn = st.connection("gsheets", type=GSheetsConnection)

# Lettura dei dati (usa il nome del foglio se necessario)
df = conn.read(spreadsheet="https://docs.google.com/spreadsheets/d/16s_hXDtp5s8rkjFvoiD5JLrAXs8f-TKywNJSN3TzbAk/edit?gid=0#gid=0")

st.write("Ecco i dati dal mio Google Sheet:")
st.dataframe(df)
