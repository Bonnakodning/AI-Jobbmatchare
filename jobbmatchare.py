import streamlit as st
import requests
from sentence_transformers import SentenceTransformer, util

st.title("AI-jobbmatchare 🔍💼")
st.markdown("Hittar jobbannonser som passar **din profil** – och låter dig sortera dem interaktivt!")

# Din profiltext – användaren fyller i denna
profiltext = st.text_area("🧠 Din erfarenhet, mål och önskemål:", 
    "Projektledare, QA manager, producer inom iGaming och spelutveckling. Söker jobb hemifrån eller hybrid, gärna i Skövde. Prioriterar frihet, lön över 40 000 kr, svenskt företag. Styrkor: ledarskap, kreativitet, struktur, QA, projektledning, inkluderande arbetssätt.")

# Hämta jobbannonser automatiskt
@st.cache_data
def hamta_jobbannonser():
    url = "https://jobsearch.api.jobtechdev.se/search?q=projektledare%20eller%20QA%20eller%20producer&limit=50"
    headers = {"Accept": "application/json"}
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        return []
    return resp.json().get("hits", [])

job_ads = hamta_jobbannonser()

# Ladda modellen
@st.cache_resource
def hamta_modell():
    return SentenceTransformer('all-MiniLM-L6-v2')

model = hamta_modell()
profile_embedding = model.encode(profiltext, convert_to_tensor=True)

# Matcha annonser mot profil
results = []
for job in job_ads:
    ad_text = job.get("description", {}).get("text", "")
    if not ad_text.strip():
        continue

    ad_embedding = model.encode(ad_text, convert_to_tensor=True)
    score = util.cos_sim(profile_embedding, ad_embedding).item()

    title = job.get("headline", "Okänt jobbnamn")
    url = job.get("webpage_url", "Ingen länk tillgänglig")
    results.append((score, title, url))

# Sortera på matchning först
results.sort(reverse=True)

# -----------------------
# Interaktiv checklista
# -----------------------

# Initiera session_state
if "prioriterade" not in st.session_state:
    st.session_state.prioriterade = set()
if "bortvalda" not in st.session_state:
    st.session_state.bortvalda = set()

# Lägg till ID för varje annons
visade_resultat = list(enumerate(results))

# Sortera: Prioriterade först
def prioritetsordning(item):
    i, (score, title, url) = item
    job_id = f"{title}_{i}"
    return (job_id not in st.session_state.prioriterade, -score)

visade_resultat.sort(key=prioritetsordning)

# Visa resultat
for i, (score, title, url) in visade_resultat:
    job_id = f"{title}_{i}"

    if job_id in st.session_state.bortvalda:
        continue

    cols = st.columns([5, 1, 1])
    with cols[0]:
        st.markdown(f"### [{title}]({url})\nMatchning: **{score:.2f}**")

    with cols[1]:
        if st.checkbox("🔼", key=f"prio_{job_id}"):
            st.session_state.prioriterade.add(job_id)

    with cols[2]:
        if st.checkbox("❌", key=f"remove_{job_id}"):
            st.session_state.bortvalda.add(job_id)
