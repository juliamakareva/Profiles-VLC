"""
Villa La Coste — App de consultation clients
Lancer : python app.py
Ouvrir  : http://localhost:5000
"""
import os, glob, json
from flask import Flask, render_template, jsonify, request
import pandas as pd
app = Flask(__name__)
from datetime import datetime

# ── Dossier des fichiers Excel ──────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ── Parsing d'un fichier Excel Mews ────────────────────────────────────
def parse_excel(path: str) -> list[dict]:
    """Parse un rapport Mews et retourne une liste de réservations."""
    try:
        df_raw = pd.read_excel(path, sheet_name="Réservations", header=None)
    except Exception as e:
        print(f"  ⚠ Impossible de lire {path} : {e}")
        return []

    cols = None
    current_group = None
    records = []

    for i in range(len(df_raw)):
        row = df_raw.iloc[i].tolist()
        non_null = [x for x in row if pd.notna(x) and str(x).strip()]

        # Ligne de groupe (ex: "Déjà venu")
        if len(non_null) == 1:
            val = str(non_null[0]).strip()
            if "Nom de famille" not in val and val != "Total":
                current_group = val
            continue

        # Ligne d'en-tête
        if "Nom de famille" in str(row):
            cols = [str(x) if pd.notna(x) else "" for x in row]
            continue

        # Ligne de données
        if cols and len(non_null) > 3:
            try:
                num = row[0]
                if pd.notna(num) and str(num).replace(".0", "").isdigit():
                    rec = dict(zip(cols, row))
                    rec["Classification"] = current_group or ""
                    records.append(rec)
            except Exception:
                pass

    return records

def safe_str(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    try:
        f = float(v)
        return str(int(f)) if f == int(f) else str(round(f, 2))
    except Exception:
        return str(v).strip()
def parse_date(v):
    try:
        if not v:
            return None
        if hasattr(v, "strftime"):
            return v
        return datetime.strptime(str(v)[:10], "%d/%m/%Y")
    except:
        return None
def safe_date(v) -> str:
    try:
        if pd.isna(v):
            return ""
    except Exception:
        pass
    try:
        if hasattr(v, "strftime"):
            return v.strftime("%d/%m/%Y")
        s = str(v)
        return s[:10] if len(s) >= 10 else s
    except Exception:
        return ""
def is_valid_sejour(row) -> bool:
    statut = safe_str(row.get("Statut", "")).strip().lower()
    return statut not in ("annulé", "annule", "cancelled", "canceled")
# ── Construction du dictionnaire clients ───────────────────────────────
def build_clients(all_records: list[dict]) -> list[dict]:
    clients: dict[tuple, dict] = {}

    for row in all_records:
        nom    = safe_str(row.get("Nom de famille", ""))
        prenom = safe_str(row.get("Prénom", ""))
        key    = (nom.upper(), prenom.upper())

        if key not in clients:
            clients[key] = {
                "nom":            nom,
                "prenom":         prenom,
                "email":          safe_str(row.get("E-mail", "")),
                "telephone":      safe_str(row.get("Téléphone", "")),
                "adresse":        safe_str(row.get("Adresse", "")),
                "nationalite":    safe_str(row.get("Nationalité du client", "")),
                "classification": safe_str(row.get("Classification", "")),
                "notes_client":   safe_str(row.get("Notes du client", "")),
                "sejours":        [],
            }

        c = clients[key]
        # Enrichir les infos manquantes
        for field, col in [("email","E-mail"), ("telephone","Téléphone"),
                           ("adresse","Adresse"), ("notes_client","Notes du client")]:
            if not c[field]:
                c[field] = safe_str(row.get(col, ""))

        if not is_valid_sejour(row):
            continue

        c["sejours"].append({
            "numero":    safe_str(row.get("Numéro", "")),
            "arrivee":   safe_date(row.get("Arrivée", "")),
            "depart":    safe_date(row.get("Départ", "")),
            "nuits":     safe_str(row.get("Nombre (nuits)", "")),
            "personnes": safe_str(row.get("Nombre de personnes", "")),
            "chambre":   safe_str(row.get("Numéro d'espace", "")),
            "categorie": safe_str(row.get("Catégorie d'espace", "")),
            "tarif":     safe_str(row.get("Tarif", "")),
            "montant":   safe_str(row.get("Montant total", "")),
            "statut":    safe_str(row.get("Statut", "")),
            "notes":     safe_str(row.get("Notes", "")),
            "source":    safe_str(row.get("Origine", "")),
        })

    result = list(clients.values())
    for c in result:
        c["nb_sejours"] = len(c["sejours"])
        # Trier les séjours par date d'arrivée (plus récent en premier)
        c["sejours"].sort(
            key=lambda s: parse_date(s["arrivee"]) or datetime.min,
            reverse=True
        )

    result.sort(key=lambda c: c["nb_sejours"], reverse=True)
    return result

# ── Chargement au démarrage ─────────────────────────────────────────────
print("\n🏨  Villa La Coste — Chargement des données...\n")

all_records = []
excel_files = glob.glob(os.path.join(DATA_DIR, "*.xlsx")) + \
              glob.glob(os.path.join(DATA_DIR, "*.xls"))

if not excel_files:
    print(f"  ⚠ Aucun fichier Excel trouvé dans : {DATA_DIR}")
else:
    for f in excel_files:
        print(f"  📂 Lecture : {os.path.basename(f)}")
        recs = parse_excel(f)
        all_records.extend(recs)
        print(f"     → {len(recs)} réservations trouvées")

CLIENTS = build_clients(all_records)
TOTAL_SEJOURS = sum(
    len([s for s in c["sejours"] if s.get("statut","").lower() not in ("annulé","annule","cancelled","canceled")])
    for c in CLIENTS
)
NATIONS = len(set(c["nationalite"] for c in CLIENTS if c["nationalite"]))

print(f"\n✅ {len(CLIENTS)} clients · {TOTAL_SEJOURS} séjours · {NATIONS} nationalités")
print(f"🌐 Ouvrir : http://localhost:5001\n")

# ── Routes ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html",
        nb_clients=len(CLIENTS),
        nb_sejours=TOTAL_SEJOURS,
        nb_nations=NATIONS,
        nb_fichiers=len(excel_files),
    )

@app.route("/api/clients")
def api_clients():
    """Retourne la liste allégée pour la sidebar (sans les notes longues)."""
    q           = request.args.get("q", "").strip().lower()
    filtre      = request.args.get("filtre", "all")
    page        = int(request.args.get("page", 1))
    per_page    = 50

    results = []
    for c in CLIENTS:
        # Filtre classification
        if filtre == "multi" and c["nb_sejours"] < 3:
            continue
        if filtre not in ("all", "multi") and c["classification"] != filtre:
            continue
        # Recherche texte
        if q:
            haystack = " ".join([
                c["nom"], c["prenom"], c["email"],
                c["telephone"], c["adresse"], c["nationalite"]
            ]).lower()
            if q not in haystack:
                continue
        results.append({
            "nom":            c["nom"],
            "prenom":         c["prenom"],
            "email":          c["email"],
            "telephone":      c["telephone"],
            "nationalite":    c["nationalite"],
            "classification": c["classification"],
            "nb_sejours":     c["nb_sejours"],
        })

    total = len(results)
    start = (page - 1) * per_page
    page_data = results[start : start + per_page]

    return jsonify({
        "total":   total,
        "page":    page,
        "pages":   (total + per_page - 1) // per_page,
        "clients": page_data,
    })

@app.route("/api/client/<nom>/<prenom>")
def api_client_detail(nom, prenom):
    """Retourne la fiche complète d'un client."""
    key = (nom.upper(), prenom.upper())
    for c in CLIENTS:
        if (c["nom"].upper(), c["prenom"].upper()) == key:
            return jsonify(c)
    return jsonify({"error": "Client non trouvé"}), 404

@app.route("/api/stats")
def api_stats():
    """Statistiques globales."""
    from collections import Counter
    nat_counter = Counter(c["nationalite"] for c in CLIENTS if c["nationalite"])
    classif_counter = Counter(c["classification"] for c in CLIENTS)
    return jsonify({
        "nb_clients":   len(CLIENTS),
        "nb_sejours":   TOTAL_SEJOURS,
        "nb_nations":   NATIONS,
        "nb_fichiers":  len(excel_files),
        "fichiers":     [os.path.basename(f) for f in excel_files],
        "nationalites": nat_counter.most_common(10),
        "classifications": dict(classif_counter),
    })

if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )


