import streamlit as st
import requests
from sentence_transformers import SentenceTransformer, util

# Din AI-profil
user_profile = """
Jag är projektledare, QA manager och producer med erfarenhet inom iGaming och spelutveckling.
Söker roller som projektledare, manager, QA manager eller producer.
Vill jobba hemifrån, hybrid eller i Skövde, men kan även pendla till Göteborg eller Stockholm 1 gång/vecka.
Söker frihet, lön över 40 000 kr/mån, kreativ arbetsmiljö.
Gillar svenska företag, gärna baserade i Skövde.
Styrkor: ledarskap, tänka utanför boxen, kreativ, positiv, noggrann, strukturerad, QA, projektledning, inkluderande arbetssätt.
"""

# Initiera modellen
@st.cache_resource
def load_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = load_model()
profile_embedding = model.encode(user_profile, convert_to_tensor=True)

st.title("🤖 AI Jobbmatchare")

if st.button("Hämta annonser och analysera"):
    with st.spinner("🔍 Hämtar annonser och analyserar..."):

        # Hämta platsannonser från Arbetsförmedlingen
        url = "https://jobsearch.api.jobtechdev.se/search"
        params = {
            "q": "projektledare OR qa OR testledare OR producer OR manager",
            "limit": 20
        }
        headers = {
            "Accept": "application/json"
        }

        response = requests.get(url, params=params, headers=headers)
        data = response.json()
        job_ads = data.get("hits", [])

        results = []

        for job in job_ads:
            ad_text = job.get("description", {}).get("text", "")
            if not ad_text.strip():
                continue  # hoppa över tomma annonser

            ad_embedding = model.encode(ad_text, convert_to_tensor=True)
            score = util.cos_sim(profile_embedding, ad_embedding).item()

            title = job.get("headline", "Okänt jobbnamn")
            url = job.get("webpage_url", "Ingen länk tillgänglig")
            results.append((score, title, url))

        # Sortera efter högsta poäng
        results.sort(reverse=True, key=lambda x: x[0])

        st.success(f"Hittade {len(results)} relevanta annonser!")

        for score, title, url in results:
            st.markdown(f"### [{title}]({url})\nMatchning: **{score:.2f}**")
