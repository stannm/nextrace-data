
import streamlit as st
import pandas as pd
import zipfile
import io
import requests

st.set_page_config(page_title="Annuaire d'entreprises - Filtrage NAF", layout="centered")
st.title("📆 Annuaire d'entreprises par Code NAF et Département")

st.markdown("""
Entrez un **code NAF** (ex: `7112B`) et un **département** (ex: `07`) pour extraire un tableau d'entreprises depuis les données SIRENE officielles.

L'application télécharge automatiquement les données de l'INSEE et filtre ce qui t'intéresse.
""")

# Entrées utilisateur
naf_input = st.text_input("Code(s) NAF (séparés par une virgule s'il y en a plusieurs)", "7112B")
dep_input = st.text_input("Numéro de département (ex: 07)", "07")
launch = st.button("Rechercher les entreprises")

if launch:
    with st.spinner("Téléchargement et filtrage en cours..."):
        url = "https://files.data.gouv.fr/insee-sirene/StockEtablissement_utf8.zip"
        response = requests.get(url)
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            with z.open("StockEtablissement_utf8.csv") as f:
                df = pd.read_csv(f, dtype=str, sep=",")

        naf_list = [n.strip() for n in naf_input.upper().split(",")]
        df_filtered = df[
            df["activitePrincipaleEtablissement"].isin(naf_list) &
            df["codePostalEtablissement"].str.startswith(dep_input)
        ]

        cols_to_keep = [
            "siren", "nic", "denominationUniteLegale", "codePostalEtablissement",
            "libelleCommuneEtablissement", "adresseEtablissement", "activitePrincipaleEtablissement"
        ]
        df_result = df_filtered[cols_to_keep].rename(columns={
            "denominationUniteLegale": "Entreprise",
            "codePostalEtablissement": "Code Postal",
            "libelleCommuneEtablissement": "Ville",
            "adresseEtablissement": "Adresse",
            "activitePrincipaleEtablissement": "Code NAF"
        })

        st.success(f"{len(df_result)} entreprises trouvées.")
        st.dataframe(df_result)

        csv = df_result.to_csv(index=False).encode('utf-8')
        st.download_button("📁 Télécharger le fichier CSV", csv, "entreprises_filtrees.csv", "text/csv")
