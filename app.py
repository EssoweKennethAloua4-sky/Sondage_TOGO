# app.py
# Sondage pour récolter des questions sur le Togo.
# Lancement : python app.py  puis ouvrir http://localhost:8000

import csv
import os
import threading
import uuid
from datetime import date

from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

DOSSIER = os.path.dirname(os.path.abspath(__file__))
FICHIER_REPONSES = os.path.join(DOSSIER, "reponses_sondage.csv")
# Fichiers joints : jamais servis par le site, à télécharger depuis PythonAnywhere (onglet Files)
DOSSIER_FICHIERS = os.path.join(DOSSIER, "fichiers_recus")
INDEX_FICHIERS = os.path.join(DOSSIER_FICHIERS, "liste_fichiers.csv")

COLONNES = ["Catégorie", "Question", "Option 1", "Option 2", "Option 3", "Réponse Correcte", "Proposé par", "Date"]
COLONNES_FICHIERS = ["Date", "Proposé par", "Catégorie", "Fichier enregistré", "Nom d'origine"]
CATEGORIES = {"Histoire", "Géographie", "Culture", "Sport", "Institutions"}

LONGUEUR_MAX_QUESTION = 200
LONGUEUR_MAX_REPONSE = 80
LONGUEUR_MAX_PSEUDO = 40

# Fichiers acceptés : documents, images, audio et vidéo (pas de programmes exécutables)
EXTENSIONS_AUTORISEES = {
    "pdf", "doc", "docx", "odt", "rtf", "txt", "csv", "xls", "xlsx", "ods", "ppt", "pptx", "odp",
    "jpg", "jpeg", "png", "gif", "webp", "heic",
    "mp3", "m4a", "ogg", "opus", "wav", "aac",
    "mp4", "mov", "3gp", "webm",
}
TAILLE_MAX_FICHIER = 10 * 1024 * 1024
# Le compte gratuit PythonAnywhere a 512 Mo : on garde de la marge
TAILLE_MAX_DOSSIER = 300 * 1024 * 1024

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = TAILLE_MAX_FICHIER + 100 * 1024
verrou = threading.Lock()


def lire_reponses():
    if not os.path.exists(FICHIER_REPONSES):
        return []
    with open(FICHIER_REPONSES, encoding="utf-8", newline="") as f:
        return [ligne for ligne in csv.DictReader(f) if ligne.get("Question")]


def ajouter_ligne(chemin, colonnes, ligne):
    nouveau_fichier = not os.path.exists(chemin)
    with open(chemin, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        if nouveau_fichier:
            writer.writerow(colonnes)
        writer.writerow(ligne)


def taille_dossier_fichiers():
    if not os.path.isdir(DOSSIER_FICHIERS):
        return 0
    return sum(e.stat().st_size for e in os.scandir(DOSSIER_FICHIERS) if e.is_file())


def nettoyer(texte, longueur_max):
    texte = " ".join(str(texte or "").split())
    # Empêche Excel d'interpréter le texte comme une formule
    texte = texte.lstrip("=+-@ ")
    return texte[:longueur_max]


def erreur(texte, code=400):
    return jsonify(ok=False, erreur=texte), code


@app.errorhandler(413)
def fichier_trop_gros(_):
    return erreur("Le fichier est trop lourd (10 Mo maximum).", 413)


@app.route("/")
def accueil():
    return send_from_directory(DOSSIER, "index.html")


@app.route("/envoyer", methods=["POST"])
def envoyer():
    donnees = request.form

    # Champ piège invisible : seuls les robots le remplissent
    if donnees.get("site_web"):
        return jsonify(ok=True)

    categorie = nettoyer(donnees.get("categorie"), 40)
    question = nettoyer(donnees.get("question"), LONGUEUR_MAX_QUESTION)
    options = [nettoyer(o, LONGUEUR_MAX_REPONSE) for o in donnees.getlist("options")][:3]
    pseudo = nettoyer(donnees.get("pseudo"), LONGUEUR_MAX_PSEUDO) or "Anonyme"
    fichier = request.files.get("fichier")
    if fichier and not fichier.filename:
        fichier = None

    # Une question est en cours de saisie dès qu'un de ses champs est rempli
    avec_question = bool(question or any(options))

    if not avec_question and not fichier:
        return erreur("Écrivez une question ou joignez un fichier.")
    if categorie not in CATEGORIES:
        return erreur("Choisissez une catégorie.")

    if avec_question:
        try:
            index_bonne = int(donnees.get("bonne_reponse"))
        except (TypeError, ValueError):
            index_bonne = -1

        if len(question) < 10:
            return erreur("La question est trop courte.")
        if len(options) != 3 or not all(options):
            return erreur("Remplissez les trois réponses.")
        if len({o.lower() for o in options}) != 3:
            return erreur("Les trois réponses doivent être différentes.")
        if index_bonne not in (0, 1, 2):
            return erreur("Cochez la bonne réponse.")

    if fichier:
        extension = fichier.filename.rsplit(".", 1)[-1].lower() if "." in fichier.filename else ""
        if extension not in EXTENSIONS_AUTORISEES:
            return erreur("Ce type de fichier n'est pas accepté (photos, documents, audio et vidéo uniquement).")

    with verrou:
        if avec_question and any(q["Question"].strip().lower() == question.lower() for q in lire_reponses()):
            return erreur("Cette question a déjà été proposée.")

        if fichier:
            if taille_dossier_fichiers() > TAILLE_MAX_DOSSIER:
                return erreur("Nous ne pouvons plus recevoir de fichiers pour le moment. Écrivez votre question dans le formulaire.", 507)

            os.makedirs(DOSSIER_FICHIERS, exist_ok=True)
            nom_propre = secure_filename(fichier.filename) or f"fichier.{extension}"
            nom_enregistre = f"{date.today().isoformat()}_{uuid.uuid4().hex[:8]}_{nom_propre}"
            fichier.save(os.path.join(DOSSIER_FICHIERS, nom_enregistre))
            ajouter_ligne(INDEX_FICHIERS, COLONNES_FICHIERS,
                          [date.today().isoformat(), pseudo, categorie, nom_enregistre, nettoyer(fichier.filename, 150)])

        if avec_question:
            ajouter_ligne(FICHIER_REPONSES, COLONNES,
                          [categorie, question, *options, options[index_bonne], pseudo, date.today().isoformat()])

    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 8000)))
