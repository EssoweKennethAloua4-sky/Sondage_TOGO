# app.py
# Sondage pour récolter des questions sur le Togo.
# Lancement : python app.py  puis ouvrir http://localhost:8000

import csv
import os
import threading
from datetime import date

from flask import Flask, jsonify, request, send_from_directory

DOSSIER = os.path.dirname(os.path.abspath(__file__))
FICHIER_REPONSES = os.path.join(DOSSIER, "reponses_sondage.csv")

COLONNES = ["Catégorie", "Question", "Option 1", "Option 2", "Option 3", "Réponse Correcte", "Proposé par", "Date"]
CATEGORIES = {"Histoire", "Géographie", "Culture", "Sport", "Institutions"}

LONGUEUR_MAX_QUESTION = 200
LONGUEUR_MAX_REPONSE = 80
LONGUEUR_MAX_PSEUDO = 40

app = Flask(__name__)
verrou = threading.Lock()


def lire_reponses():
    if not os.path.exists(FICHIER_REPONSES):
        return []
    with open(FICHIER_REPONSES, encoding="utf-8", newline="") as f:
        return [ligne for ligne in csv.DictReader(f) if ligne.get("Question")]


def nettoyer(texte, longueur_max):
    texte = " ".join(str(texte or "").split())
    # Empêche Excel d'interpréter le texte comme une formule
    texte = texte.lstrip("=+-@ ")
    return texte[:longueur_max]


@app.route("/")
def accueil():
    return send_from_directory(DOSSIER, "index.html")


@app.route("/envoyer", methods=["POST"])
def envoyer():
    donnees = request.get_json(silent=True) or {}

    # Champ piège invisible : seuls les robots le remplissent
    if donnees.get("site_web"):
        return jsonify(ok=True)

    categorie = nettoyer(donnees.get("categorie"), 40)
    question = nettoyer(donnees.get("question"), LONGUEUR_MAX_QUESTION)
    options = [nettoyer(o, LONGUEUR_MAX_REPONSE) for o in donnees.get("options", [])][:3]
    pseudo = nettoyer(donnees.get("pseudo"), LONGUEUR_MAX_PSEUDO) or "Anonyme"

    try:
        index_bonne = int(donnees.get("bonne_reponse"))
    except (TypeError, ValueError):
        index_bonne = -1

    if categorie not in CATEGORIES:
        return jsonify(ok=False, erreur="Choisissez une catégorie."), 400
    if len(question) < 10:
        return jsonify(ok=False, erreur="La question est trop courte."), 400
    if len(options) != 3 or not all(options):
        return jsonify(ok=False, erreur="Remplissez les trois réponses."), 400
    if len({o.lower() for o in options}) != 3:
        return jsonify(ok=False, erreur="Les trois réponses doivent être différentes."), 400
    if index_bonne not in (0, 1, 2):
        return jsonify(ok=False, erreur="Cochez la bonne réponse."), 400

    with verrou:
        if any(q["Question"].strip().lower() == question.lower() for q in lire_reponses()):
            return jsonify(ok=False, erreur="Cette question a déjà été proposée."), 400

        nouveau_fichier = not os.path.exists(FICHIER_REPONSES)
        with open(FICHIER_REPONSES, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if nouveau_fichier:
                writer.writerow(COLONNES)
            writer.writerow([categorie, question, *options, options[index_bonne], pseudo, date.today().isoformat()])

    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
