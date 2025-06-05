import streamlit as st
import pandas as pd
import io
import requests

st.set_page_config(page_title="Annuaire d'entreprises - Filtrage NAF", layout="centered")
st.title("📆 Annuaire d'entreprises par Code NAF et Département")

st.markdown("""
Entrez un **code NAF** (ex: `7112B`) et un **département** (ex: `07`) pour extraire un tableau d'entreprises depuis un fichier SIRENE *léger* de test.
""")

naf_input = st.text_input("Code(s) NAF (séparés par une virgule s'il y en a plusieurs)", "7112B")
dep_input = st.text_input("Numéro de département (ex: 07)", "07")
launch = st.button("Rechercher les entreprises")

if launch:
    with st.spinner("Chargement de l'échantillon..."):
        # Exemple de fichier test léger hébergé (à remplacer par ton propre lien si besoin)
        url = "https://raw.githubusercontent.com/charlesdedampierre/datasets/main/sirene_sample.csv"
        response = requests.get(url)
        df = pd.read_csv(io.StringIO(response.content.decode('utf-8')), dtype=str)

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
