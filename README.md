# Prep Desktop — Démo Python / PyQt6

Petit projet de test pour comparer concrètement avec le starter Electron+React,
avant de choisir la techno définitive pour Prep@udit Desktop.

## Ce que ça montre

- Une vraie fenêtre desktop (PyQt6), pas un site web
- Une boîte de dialogue **native Windows** pour choisir un fichier CSV
- Lecture et traitement du CSV avec **Pandas**
- Un tableau interactif avec recherche/filtre en temps réel
- Un mini dashboard (cartes de synthèse chiffrées)

## Prérequis

- Python 3.10 ou plus récent installé — vérifie avec :
  ```bash
  python --version
  ```

## Installation

Ouvre un terminal dans ce dossier, puis :

```bash
pip install -r requirements.txt
```

(Sur certains systèmes, utilise `pip3` au lieu de `pip`.)

## Lancer l'application

```bash
python main.py
```

## Tester

1. Clique sur **"Charger des données d'exemple"** pour voir immédiatement le tableau
   et le dashboard fonctionner
2. Ou clique sur **"Ouvrir un fichier CSV"** pour tester avec un vrai fichier
   (séparateur `;`, comme les exports bancaires français)
3. Tape dans la barre de recherche pour filtrer les lignes en direct

## Construire un exécutable (.exe)

Pour transformer ce script en un vrai fichier `.exe` installable, sans que
la personne ait besoin d'installer Python :

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "PrepDesktop" main.py
```

L'exécutable sera généré dans le dossier `dist/`.

- `--onefile` : un seul fichier .exe (plus simple à partager)
- `--windowed` : pas de console noire qui s'ouvre en arrière-plan

## Structure du projet

```
python-desktop-starter/
├── main.py             -> Toute l'application (interface + logique)
├── requirements.txt    -> Dépendances Python
└── README.md
```

## Comparaison rapide avec le starter Electron

| | Ce projet (Python/PyQt) | Starter Electron+React |
|---|---|---|
| Lignes de code pour la même démo | ~200 | ~250 (réparties en plusieurs fichiers) |
| Traitement CSV | Pandas (très concis) | PapaParse (plus verbeux) |
| Poids de l'exécutable final | ~40-60 Mo | ~120-150 Mo |
| Look par défaut | Correct, demande du style manuel (fait ici en CSS Qt) | Moderne par défaut |

## Prochaine étape

Si ce test te convainc, on pourra structurer le vrai projet Prep@udit Desktop
en Python avec :
- Les classes du diagramme de conception (ModuleAudit, Extraction, ThemeResultat...)
- Une base SQLite locale pour l'historique des extractions
- Un module par thème (Engagements, Garanties, etc.) avec ses propres règles
