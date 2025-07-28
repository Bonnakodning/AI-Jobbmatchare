import streamlit as st
import requests
from sentence_transformers import SentenceTransformer, util

# Din AI-profil
user_profile = """
Jag är projektledare, QA manager och producer med erfarenhet inom iGaming och spelutveckling.
Söker roller som projektledare, manager, QA manager eller producer.
Vill jobba hemifrån, hybrid eller i Skövde, men kan även pendla till Göteborg eller Stockholm 1 gång/vecka.
Söker frihet, lön över 40 000 kr/mån, kreativ arbetsmiljö.
Gillar svenska företag, gärna Skövdebaserade.
Styrkor: ledarskap, kreativitet, QA, struktur, positivitet, inkluderande arbetssätt.
"""

# Initiera AI-modell
model = SentenceTransformer("all-MiniLM-L6-v2")
profile_emb = model.encode(user_profile, convert_to_tensor=True)

st.set_page_config(page_title="AI-jobbmatchare", layout="centered")
st.title("🤖 AI-jobbmatchare")
st.write("Denna app hämtar automatiskt jobbannonser från Arbetsförmedlingen och rankar dem mot din profil.")

# Inställningar för sökning
st.subheader("🔍 Inställningar för import")
search_terms = st.text_input("Sökord (kommaseparerade)", "projektledare,QA,producer,manager")
location = st.text_input("Ort (frivillig, t.ex. Skövde eller Göteborg)", "")
limit = st.slider("Max antal annonser att analysera", 1, 30, 10)

if st.button("Hämta & analysera annonser"):
    q = " OR ".join([term.strip() for term in search_terms.split(",")])
    params = {
        "q": q,
        "limit": limit,
        "from": 0
    }
    if location:
        params["municipality"] = location

    # Hämta annonser från JobTech API
    url = "https://jobsearch.api.jobtechdev.se/search"
    headers = {"Accept": "application/json"}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        jobs = response.json().get("hits", [])
        if not jobs:
            st.warning("Inga jobb hittades med de inställningarna.")
        else:
            st.subheader("📊 Matchningsresultat:")
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


            sorted_results = sorted(results, key=lambda x: x[0], reverse=True)
            for i, (score, title, url) in enumerate(sorted_results, 1):
                st.markdown(f"**#{i} – {round(score*100, 1)}% match**\n[{title}]({url})\n---")
    else:
        st.error("Kunde inte hämta jobbannonser. Försök igen senare.")
