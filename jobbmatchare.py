import streamlit as st
import requests

st.set_page_config(page_title="AI Jobbmatchare", layout="wide")
st.title("🤖 AI-jobbmatchare – hitta rätt jobb för dig!")

# ░█▀▀░█▀█░█▀█░█▀▀░█▀▀░█▀▀░█▀▄░█▀▀
# ░█▀▀░█▀█░█░█░█▀▀░▀▀█░█▀▀░█▀▄░█▀▀
# ░▀▀▀░▀░▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀░▀░▀▀▀

antal_annons = st.slider("📊 Hur många annonser vill du se?", 5, 30, 10)

oönskade_branscher = st.multiselect("🚫 Filtrera bort branscher du inte vill ha:",
    ["Bygg", "Snickeri", "Anläggning", "Lager", "Chaufför", "Vård", "Truck", "Industri", "Montör", "Mekaniker"],
    default=["Bygg", "Snickeri", "Anläggning", "Lager", "Chaufför", "Vård", "Truck", "Industri", "Montör", "Mekaniker"]
)
stopplista = [x.lower() for x in oönskade_branscher]

nyckelord = [
    "projektledare", "producer", "qa", "test", "speldesign", "scrum", 
    "agil", "skövde", "remote", "hybrid", "ledning", "spelutveckling", "iGaming"
]

res = requests.get("https://jobsearch.api.jobtechdev.se/search?q=projektledare&limit=100")
data = res.json()
annonser = data.get("hits", [])

results = []

for job in annonser:
    ad_text = job.get("description", {}).get("text", "").lower()
    score = sum(1 for k in nyckelord if k in ad_text)
    title = job.get("headline", "Annons utan titel")
    url = job.get("webpage_url", "#")
    results.append((score, title, url))

results.sort(reverse=True)

filtrerade = []
for score, title, url in results:
    combined = f"{title} {url}".lower()
    if any(ord in combined for ord in stopplista):
        continue
    filtrerade.append((score, title, url))

results = filtrerade[:antal_annons]

# ░█▀▀░█░█░█▀▀░█▀▀░█▀▀
# ░█▀▀░█░█░█▀▀░█░█░▀▀█
# ░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀

if "prioriterade" not in st.session_state:
    st.session_state.prioriterade = set()
if "bortvalda" not in st.session_state:
    st.session_state.bortvalda = set()

visade_resultat = list(enumerate(results))

def prioritetsordning(item):
    i, (score, title, url) = item
    job_id = f"{title}_{i}"
    return (job_id not in st.session_state.prioriterade, -score)

visade_resultat.sort(key=prioritetsordning)

st.markdown("## ✨ Dina jobbmatchningar")

for i, (score, title, url) in visade_resultat:
    job_id = f"{title}_{i}"

    if job_id in st.session_state.bortvalda:
        continue

    with st.container():
        st.markdown(f"**🔗 [{title}]({url})**  \n🎯 Matchning: `{score}`", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⭐ Prioritera", key=f"prio_{job_id}"):
                st.session_state.prioriterade.add(job_id)
                st.rerun()

        with col2:
            if st.button("🗑️ Ta bort", key=f"remove_{job_id}"):
                st.session_state.bortvalda.add(job_id)
                st.rerun()

        st.markdown("---")
