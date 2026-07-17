import streamlit as st
from supabase import create_client
import requests


# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="DFL Gestione Spedizioni",
    page_icon="📦"
)


# =========================
# SUPABASE
# =========================

SUPABASE_URL = "INSERISCI_URL_SUPABASE"
SUPABASE_KEY = "INSERISCI_KEY_SUPABASE"


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)



# =========================
# MENU
# =========================

pagina = st.sidebar.selectbox(
    "Menu",
    [
        "Ricerca DFL",
        "Inserisci Ordine",
        "Carica LDV"
    ]
)



# ==================================================
# PAGINA OPERATORE DFL
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
            .eq("stato", "NON EVASO")
            .order("id")
            .limit(1)
            .execute()
        )


        dati = risultato.data



        if dati:


            ordine = dati[0]


            st.success(
                "Ordine trovato"
            )


            st.write(
                "📦 Ordine:",
                ordine["ordine_id"]
            )


            st.write(
                "👤 Cliente:",
                ordine["cliente"]
            )


            st.write(
                "🛋 Articolo:",
                ordine["articolo"]
            )


            st.write(
                "📌 Stato:",
                ordine["stato"]
            )



            if ordine["ldv_url"]:


                # Scarica PDF

                try:

                    pdf = requests.get(
                        ordine["ldv_url"]
                    ).content



                    st.download_button(

                        label="⬇️ Scarica LDV",

                        data=pdf,

                        file_name=ordine["ldv_file"],

                        mime="application/pdf"

                    )


                    # Aggiorna stato dopo visualizzazione

                    if st.button(
                        "Conferma stampa LDV"
                    ):


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



                        st.success(
                            "Ordine segnato come EVASO"
                        )


                except Exception as e:


                    st.error(
                        f"Errore download LDV: {e}"
                    )


            else:


                st.warning(
                    "LDV non ancora caricata"
                )



        else:


            controllo = (
                supabase
                .table("ordini")
                .select("*")
                .eq("ean", ean)
                .execute()
            )


            if controllo.data:


                st.warning(
                    "⚠️ Ordine già EVASO"
                )

            else:

                st.error(
                    "EAN non trovato"
                )





# ==================================================
# INSERIMENTO ORDINE
# ==================================================

if pagina == "Inserisci Ordine":


    st.title(
        "⚙️ Inserimento Ordine"
    )


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



    if st.button(
        "Salva Ordine"
    ):


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
            "Ordine salvato"
        )





# ==================================================
# CARICAMENTO LDV
# ==================================================

if pagina == "Carica LDV":


    st.title(
        "📄 Caricamento LDV"
    )


    ordine_id = st.text_input(
        "Numero ordine"
    )



    if ordine_id:


        risultato = (
            supabase
            .table("ordini")
            .select("*")
            .eq(
                "ordine_id",
                ordine_id
            )
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



                if st.button(
                    "Carica LDV"
                ):


                    try:


                        supabase.storage.from_(
                            "LVD"
                        ).upload(

                            nome_file,

                            file.getvalue(),

                            {
                                "content-type":
                                "application/pdf"
                            }

                        )



                        url = (
                            supabase
                            .storage
                            .from_("LVD")
                            .get_public_url(
                                nome_file
                            )
                        )



                        supabase.table(
                            "ordini"
                        ).update(

                            {

                                "ldv_file":
                                nome_file,


                                "ldv_url":
                                url

                            }

                        ).eq(

                            "id",
                            ordine["id"]

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
