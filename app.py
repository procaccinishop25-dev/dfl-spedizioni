import streamlit as st
from supabase import create_client


# -------------------------
# CONFIGURAZIONE PAGINA
# -------------------------

st.set_page_config(
    page_title="DFL Gestione Spedizioni",
    page_icon="📦"
)


# -------------------------
# CONNESSIONE SUPABASE
# -------------------------

SUPABASE_URL = "https://tinlardrswxsdiyhdiuc.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRpbmxhcmRyc3d4c2RpeWhkaXVjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODQzMTI1MjMsImV4cCI6MjA5OTg4ODUyM30.mwuk-A8eD6nFx_thX0S0wITOV3MieOtvhj5eOG_U9ko"


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# -------------------------
# MENU
# -------------------------

pagina = st.sidebar.selectbox(
    "Menu",
    [
        "Ricerca DFL",
        "Inserisci Ordine",
        "Carica LDV"
    ]
)



# ==================================================
# PAGINA DFL - RICERCA EAN
# ==================================================

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

            # Cerco prima gli ordini ancora da evadere

            ordini_aperti = [
                ordine
                for ordine in dati
                if ordine["stato"] == "NON EVASO"
            ]


            if ordini_aperti:

                # prende l'unico ordine aperto
                # se ce ne sono più di uno li vediamo

                if len(ordini_aperti) > 1:

                    st.warning(
                        "Trovati più ordini NON EVASI con questo EAN"
                    )


                    for ordine in ordini_aperti:

                        st.write(
                            "Ordine:",
                            ordine["ordine_id"]
                        )

                else:

                    ordine = ordini_aperti[0]


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


                    # Apertura LDV automatica

                    if ordine["ldv_url"]:


                        st.markdown(
                            f"""
                            <meta http-equiv="refresh" 
                            content="1;URL={ordine['ldv_url']}">
                            """,
                            unsafe_allow_html=True
                        )


                        # Aggiorno stato

                        supabase.table(
                            "ordini"
                        ).update(
                            {
                                "stato": "EVASO"
                            }
                        ).eq(
                            "id",
                            ordine["id"]
                        ).execute()


                    else:

                        st.warning(
                            "LDV non disponibile"
                        )


            else:

                # Tutti gli ordini con quell'EAN sono già evasi

                ordine = dati[0]


                st.warning(
                    "⚠️ ORDINE GIÀ EVASO"
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


                st.success(
                    "EVASO"
                )


        else:

            st.error(
                "Nessun ordine trovato"
            )



# ==================================================
# PAGINA INSERIMENTO ORDINE
# ==================================================

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



# ==================================================
# CARICAMENTO LDV
# ==================================================

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


                        # Upload PDF nel bucket LVD

                        supabase.storage.from_(
                            "LVD"
                        ).upload(
                            nome_file,
                            file.getvalue(),
                            {
                                "content-type": "application/pdf"
                            }
                        )


                        # URL pubblico

                        url = (
                            supabase
                            .storage
                            .from_("LVD")
                            .get_public_url(
                                nome_file
                            )
                        )


                        # Aggiornamento ordine

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
