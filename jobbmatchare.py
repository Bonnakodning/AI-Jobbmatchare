import streamlit as st
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

# Modell för AI-matchning
model = SentenceTransformer("all-MiniLM-L6-v2")
profile_embedding = model.encode(user_profile, convert_to_tensor=True)

# Streamlit-gränssnitt
st.set_page_config(page_title="AI-jobbmatchare", layout="centered")
st.title("🤖 AI-jobbmatchare")
st.write("Klistra in jobbannonser nedan, en per rad. Klicka på *Analysera* för att se vilka som passar dig bäst.")

input_text = st.text_area("📋 Jobbannonser", height=200, placeholder="Exempel:\nProducent till spelstudio i Göteborg...\nQA Manager till fintechbolag i Stockholm...")

if st.button("Analysera"):
    if input_text.strip() == "":
        st.warning("Du måste klistra in minst en jobbannons.")
    else:
        ads = [line.strip() for line in input_text.strip().split('\n') if line.strip()]
        results = []
        for ad in ads:
            ad_embedding = model.encode(ad, convert_to_tensor=True)
            score = util.cos_sim(profile_embedding, ad_embedding).item()
            results.append((score, ad))
        sorted_results = sorted(results, key=lambda x: x[0], reverse=True)

        st.subheader("📊 Matchningsresultat:")
        for i, (score, ad) in enumerate(sorted_results, 1):
            st.markdown(f"**#{i} – Matchning: {round(score*100, 1)}%**\n\n{ad}\n---")
