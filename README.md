# 📝 Sondage TOGO

Formulaire simple pour récolter des questions sur le Togo (Histoire, Géographie, Culture, Sport, Institutions).
Chaque réponse est enregistrée dans `reponses_sondage.csv`, au même format que `questions_togo.csv` du quiz,
avec deux colonnes en plus : « Proposé par » et « Date ».

## Lancer en local

```bash
pip install -r requirements.txt
python app.py
```

Puis ouvrir http://localhost:8000.

## Mettre en ligne sur PythonAnywhere

1. Onglet **Consoles** → **Bash** :

```bash
git clone https://github.com/EssoweKennethAloua4-sky/Sondage_TOGO.git
```

2. Onglet **Web** → **Add a new web app** → **Manual configuration** → **Python 3.13**
3. Section **Code** : **Source code** et **Working directory** = `/home/TONPSEUDO/Sondage_TOGO`
4. Ouvrir le **WSGI configuration file**, tout effacer et coller :

```python
import sys

sys.path.insert(0, "/home/TONPSEUDO/Sondage_TOGO")

from app import app as application
```

5. **Save**, puis onglet **Web** → **Reload**
6. Le lien à partager : `https://TONPSEUDO.pythonanywhere.com`

## Récupérer les réponses

Onglet **Files** → dossier `Sondage_TOGO` → télécharger `reponses_sondage.csv`.
Garder les bonnes lignes et les coller dans `questions_togo.csv` du quiz, **sans les deux dernières colonnes**.

### Import de plusieurs questions (modèle Excel / CSV)

En bas du formulaire, on peut télécharger un modèle (`/modele.xlsx` ou `/modele.csv`) avec les colonnes
`Catégorie, Question, Réponse 1, Réponse 2, Réponse 3, Bonne réponse`, le remplir (à la main ou avec une IA),
puis l'importer : chaque ligne valable est ajoutée à `reponses_sondage.csv`, comme si elle avait été tapée dans le formulaire.

- Catégorie : liste déroulante dans le modèle Excel (majuscules et accents tolérés).
- Bonne réponse : le texte de la bonne réponse, ou son numéro (1, 2 ou 3).
- La ligne d'exemple est ignorée. 500 questions maximum par fichier.
- Les lignes incorrectes ou déjà proposées sont refusées, avec leur numéro, et les autres sont quand même ajoutées.
- Les CSV enregistrés par Excel en français (séparateur `;`) sont acceptés.

### Fichiers joints

Les participants peuvent joindre un fichier (photo, document, audio ou vidéo, 10 Mo maximum, pas de programmes).
Ils arrivent dans le dossier `fichiers_recus/`, avec `liste_fichiers.csv` qui indique qui a envoyé quoi.
Les fichiers ne sont jamais visibles sur le site : on les télécharge depuis l'onglet **Files**.

Pour tout télécharger d'un coup, dans une console **Bash** :

```bash
cd Sondage_TOGO
zip -r fichiers_recus.zip fichiers_recus
```

Puis télécharger `fichiers_recus.zip` depuis l'onglet **Files**.
Au-delà de 300 Mo de fichiers reçus, le formulaire refuse les nouveaux fichiers (le compte gratuit a 512 Mo).
