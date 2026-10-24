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
