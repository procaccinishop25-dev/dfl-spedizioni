import streamlit as st
from supabase import create_client


st.set_page_config(
    page_title="DFL Gestione Spedizioni",
    page_icon="📦"
)

SUPABASE_URL = "https://tinlardrswxsdiyhdiuc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRpbmxhcmRyc3d4c2RpeWhkaXVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQzMTI1MjMsImV4cCI6MjA5OTg4ODUyM30.mwuk-A8eD6nFx_thX0S0wITOV3MieOtvhj5eOG_U9ko"

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


pagina = st.sidebar.selectbox(
    "Menu",
    [
        "Ricerca DFL",
        "Inserisci Ordine",
        "Carica LDV"
    ]
)


# -------------------------
# PAGINA DFL
# -------------------------

if pagina == "Ricerca DFL":

    st.title("📦 Gestione Spedizioni DFL")


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

            st.success(
                "Ordine trovato"
            )


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


# -------------------------
# PAGINA ADMIN
# -------------------------

if pagina == "Inserisci Ordine":

    st.title("⚙️ Inserimento Ordine")


    ordine_id = st.text_input(
        "Numero ordine"
    )

    cliente = st.text_input(
        "Cliente"
    )

    ean = st.text_input(
        "EAN"
    )

    articolo = st.text_input(
        "Articolo"
    )


    if st.button("Salva Ordine"):


        nuovo_ordine = {

            "ordine_id": ordine_id,
            "cliente": cliente,
            "ean": ean,
            "articolo": articolo,
            "stato": "NON EVASO"

        }


        supabase.table(
            "ordini"
        ).insert(
            nuovo_ordine
        ).execute()


        st.success(
            "Ordine salvato!"
        )
# -------------------------
# CARICAMENTO LDV
# -------------------------

if pagina == "Carica LDV":

    st.title("📄 Caricamento LDV")

    ordine_id = st.text_input(
        "Numero ordine"
    )

    if ordine_id:

        risultato = (
            supabase
            .table("ordini")
            .select("*")
            .eq("ordine_id", ordine_id)
            .execute()
        )

        dati = risultato.data

        if dati:

            ordine = dati[0]

            st.write(
                "Cliente:",
                ordine["cliente"]
            )

            st.write(
                "EAN:",
                ordine["ean"]
            )


            file = st.file_uploader(
                "Carica PDF LDV",
                type=["pdf"]
            )


            if file:

                nome_file = (
                    f"Ordine_{ordine['ordine_id']}_"
                    f"{ordine['ean']}.pdf"
                )


                st.write(
                    "Nome file:",
                    nome_file
                )


                if st.button("Carica LDV"):

                    try:

                        # Upload PDF su Supabase Storage
                        supabase.storage.from_(
                            "LVD"
                        ).upload(
                            nome_file,
                            file.getvalue(),
                            {
                                "content-type": "application/pdf"
                            }
                        )


                        # Creo URL pubblico
                        url = (
                            supabase
                            .storage
                            .from_("LVD")
                            .get_public_url(nome_file)
                        )


                        # Salvo collegamento nel database
                        supabase.table(
                            "ordini"
                        ).update(
                            {
                                "ldv_file": nome_file,
                                "ldv_url": url
                            }
                        ).eq(
                            "ordine_id",
                            ordine["ordine_id"]
                        ).execute()


                        st.success(
                            "LDV caricata correttamente"
                        )


                    except Exception as e:

                        st.error(
                            f"Errore caricamento LDV: {e}"
                        )


        else:

            st.error(
                "Ordine non trovato"
            )
