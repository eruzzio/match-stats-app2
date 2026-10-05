
import streamlit as st
import pandas as pd
import os
import shutil
import requests
from datetime import datetime
import ffmpeg

# Initialisation de session
if "timeline" not in st.session_state:
    st.session_state.timeline = []
if "video_path" not in st.session_state:
    st.session_state.video_path = None
if "video_uploaded" not in st.session_state:
    st.session_state.video_uploaded = False
if "video_mode" not in st.session_state:
    st.session_state.video_mode = "Uploader un fichier"
if "start_time" not in st.session_state:
    st.session_state.start_time = None

st.title("🌟 Application Statistiques Match + Vidéo")

tabs = st.tabs(["📊 Statistiques Match", "🎥 Vidéo et Extraction"])

# Onglet 1 : Statistiques Match
with tabs[0]:
    st.subheader("⏱️ Chronomètre")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Démarrer le match"):
            st.session_state.start_time = datetime.now()
    with col2:
        if st.button("Arrêter le match"):
            st.session_state.start_time = None

    @st.fragment(run_every=1)
    def afficher_chrono():
        if st.session_state.start_time:
            elapsed = datetime.now() - st.session_state.start_time
            total = int(elapsed.total_seconds())
            st.success(f"Temps : {total // 60:02}:{total % 60:02}")
        else:
            st.info("Le match n'a pas commencé")

    afficher_chrono()

    st.subheader("🔹 Statistiques du match")
    actions = ["Tir", "But", "Faute", "Corner", "Arrêt", "Passe"]
    selected_action = st.selectbox("Choisir une action", actions)

    if st.button("Ajouter à la timeline"):
        if st.session_state.start_time:
            elapsed = datetime.now() - st.session_state.start_time
            total = int(elapsed.total_seconds())
            timestamp = f"{total // 60:02}:{total % 60:02}"
            st.session_state.timeline.append({"Timestamp": timestamp, "Action": selected_action})
            st.success(f"Ajouté : {selected_action} à {timestamp}")
        else:
            st.warning("Démarrez d'abord le chronomètre")

    if st.session_state.timeline:
        df = pd.DataFrame(st.session_state.timeline)
        st.dataframe(df)
        df.to_csv("timeline_match.csv", index=False)

# Onglet 2 : Vidéo et Extraction
with tabs[1]:
    st.subheader("🎥 Vidéo et Extraction")
    if st.session_state.timeline:
        st.session_state.video_mode = st.radio(
            "Choisissez une méthode pour fournir la vidéo :",
            ["Uploader un fichier", "Coller un lien"],
            index=["Uploader un fichier", "Coller un lien"].index(st.session_state.video_mode)
        )

        if st.session_state.video_mode == "Uploader un fichier":
            uploaded_file = st.file_uploader("Choisissez un fichier vidéo", type=["mp4", "mov", "avi"])
            if uploaded_file is not None:
                os.makedirs("videos", exist_ok=True)
                output_path = os.path.join("videos", f"match_{datetime.now():%Y%m%d_%H%M%S}.mp4")
                with open(output_path, "wb") as f:
                    f.write(uploaded_file.read())
                st.session_state.video_path = output_path
                st.session_state.video_uploaded = True
                st.success("Vidéo uploadée avec succès")
                st.video(output_path)

        elif st.session_state.video_mode == "Coller un lien":
            video_url = st.text_input("Collez ici le lien vers votre vidéo (Wormhole, Filemail, etc.)")
            if video_url:
                with st.spinner("Téléchargement en cours..."):
                    try:
                        response = requests.get(video_url, stream=True, timeout=60)
                        response.raise_for_status()
                        total_size = int(response.headers.get('content-length', 0))
                        chunk_size = 8192
                        os.makedirs("videos", exist_ok=True)
                        output_path = os.path.join("videos", f"match_{datetime.now():%Y%m%d_%H%M%S}.mp4")
                        with open(output_path, "wb") as f:
                            for data in response.iter_content(chunk_size):
                                f.write(data)
                        st.success(f"Vidéo téléchargée ({round(total_size / 1024**2)} Mo)")
                        st.session_state.video_path = output_path
                        st.session_state.video_uploaded = True
                        st.video(output_path)
                    except Exception as e:
                        st.error(f"Erreur : {e}")

    if st.session_state.video_uploaded and st.session_state.timeline:
        if st.button("Extraire les clips"):
            with st.spinner("Analyse en cours..."):
                shutil.rmtree("clips", ignore_errors=True)
                os.makedirs("clips")
                for i, entry in enumerate(st.session_state.timeline):
                    minutes, seconds = map(int, entry["Timestamp"].split(":"))
                    total_sec = minutes * 60 + seconds
                    start = max(total_sec - 5, 0)
                    duration = 10
                    out_clip = f"clips/clip_{i+1}_{entry['Action']}_{minutes:02}-{seconds:02}.mp4"

                    (
                        ffmpeg
                        .input(st.session_state.video_path, ss=start, t=duration)
                        .output(out_clip, vcodec="libx264", acodec="aac")
                        .run(overwrite_output=True, quiet=True)
                    )
                st.success(f"{len(st.session_state.timeline)} clips créés dans le dossier 'clips'")
    else:
        st.info("Créez d'abord une timeline depuis l'onglet précédent.")
