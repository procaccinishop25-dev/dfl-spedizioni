import streamlit as st
from supabase import create_client


# CONFIGURAZIONE PAGINA
st.set_page_config(
    page_title="DFL Gestione Spedizioni",
    page_icon="📦"
)


st.title("📦 Gestione Spedizioni DFL")


# Collegamento Supabase
SUPABASE_URL = "https://tinlardrswxsdiyhdiuc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRpbmxhcmRyc3d4c2RpeWhkaXVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQzMTI1MjMsImV4cCI6MjA5OTg4ODUyM30.mwuk-A8eD6nFx_thX0S0wITOV3MieOtvhj5eOG_U9ko"


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# Campo scansione EAN

ean = st.text_input(
    "Scansiona EAN"
)


if ean:

    risultato = (
        supabase
        .table("ordini")
        .select("*")
        .eq("ean", ean)
        .execute()
    )


    dati = risultato.data


    if dati:

        ordine = dati[0]

        st.success("Ordine trovato")


        st.write(
            "Ordine:",
            ordine["ordine_id"]
        )

        st.write(
            "Cliente:",
            ordine["cliente"]
        )

        st.write(
            "Articolo:",
            ordine["articolo"]
        )

        st.write(
            "Stato:",
            ordine["stato"]
        )

    else:

        st.error(
            "Nessun ordine trovato"
        )
