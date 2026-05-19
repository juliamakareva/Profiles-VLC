# 🏨 Villa La Coste — App Clients

Application locale de consultation des fiches clients.
Fonctionne **sans internet** une fois installée.

---

## ⚡ Installation (une seule fois)

### 1. Installer Python
Télécharger sur https://python.org (version 3.10+)
Cocher "Add Python to PATH" lors de l'installation.

### 2. Installer les dépendances
Ouvrir un terminal dans ce dossier, puis :
```
pip install flask pandas openpyxl
```

---

## 🚀 Lancer l'application

Double-cliquer sur **LANCER.bat** (Windows)
ou dans le terminal :
```
python app.py
```

Puis ouvrir dans le navigateur : **http://localhost:5000**

---

## 📂 Ajouter des fichiers Excel

1. Déposer vos fichiers `.xlsx` dans le dossier **`data/`**
2. Relancer l'application (`python app.py`)

Les fichiers doivent être des exports Mews au format "Rapport Réservations"
avec la feuille **"Réservations"** (feuilles : Paramètres, Réservations, Nuits...).

---

## 🔍 Fonctionnalités

- **Recherche instantanée** par nom, prénom, email, téléphone
- **Filtres** : Déjà venu / Paymaster / Bloqué / 3+ séjours
- **Fiche complète** : coordonnées, notes, historique
- **Détail de chaque séjour** (chambre, tarif, notes internes)
- **Pagination** — chargement rapide même avec 5000+ clients

---

## 🗂 Structure
```
vlc_app/
  app.py              ← Serveur (ne pas modifier)
  templates/
    index.html        ← Interface (ne pas modifier)
  data/
    fichier_2021.xlsx ← Vos exports Excel
    fichier_2022.xlsx
    fichier_2023.xlsx
    ...
  LANCER.bat          ← Double-clic pour lancer
  README.md           ← Ce fichier
```
