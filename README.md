# match-stats-app2

> **Dépôt archivé : ancien prototype, remplacé par [Orion](https://github.com/eruzzio/Orion).**
> Plus aucun développement ici. L'application actuelle de codage et d'analyse vidéo de matchs est Orion.

Prototype Streamlit de statistiques de match avec extraction de clips vidéo.

- **Statistiques :** chronomètre de match et horodatage des actions (tir, but, faute, corner, arrêt, passe).
- **Vidéo :** envoi d'un fichier ou lien, puis découpe d'un clip de 10 secondes autour de chaque action avec ffmpeg.

## Lancer le prototype

```
pip install -r requirements.txt   # ffmpeg doit être installé sur la machine
streamlit run app.py
```
