# Labo-Temperature

Expérience sur l'effet du paramètre `temperature` d'un LLM local (`llama3.2` via Ollama) sur deux types de tâches : une tâche factuelle et une tâche créative, dans un contexte d'assurance.

## Arborescence

```text
Labo-Temperature/
├── data/
│   └── Taches.json
├── src/
│   └── labo.py
├── venv/
├── README.md
└── requirements.txt
```

## Hypothèse

- Tâche factuelle : une température basse (0) devrait donner une réponse correcte et stable ; une température élevée (1.5) devrait augmenter les erreurs d'extraction.
- Tâche créative : une température basse devrait donner des slogans répétitifs et une température élevée des slogans plus variés, au risque de ne plus respecter la contrainte de longueur.

## Ce qui a été fait

### `data/Taches.json` : définition de l'expérience

- Paramètres : modèle `llama3.2`, températures `[0, 0.7, 1.5]`, 10 essais par condition.
- **Tâche A (factuelle)** : extraire le montant total des dommages d'une déclaration de sinistre « dégât des eaux » (courrier fictif).
  - Réponse attendue : `1850`.
  - Le prompt demande uniquement un nombre, sans phrase.
  - Le texte contient 7 « pièges » numériques pour détecter les mauvaises extractions : `HAB-2026-48213` (n° de contrat), `12/10/2026` (date du sinistre), `18` (surface en m²), `2019` (année du parquet), `150` (franchise), `15/10/2026` (date du devis) et `6` (nombre de photos).
- **Tâche B (créative)** : slogan pour une assurance auto jeune conducteur, 10 mots maximum (`contrainte_mots_max`), réponse limitée au slogan.

### `src/labo.py` : appel du modèle

- `generer(prompt, temperature, modele)` appelle `ollama.chat` avec la température passée dans `options` et renvoie le texte de la réponse.
- L'import d'`ollama` est fait dans la fonction, avec un message d'erreur explicite (`pip install ollama`) si le paquet est absent.
- Boucle interactive : à chaque tour, l'utilisateur saisit une requête (`exit` pour quitter) et le script affiche la réponse du modèle pour chaque température de la liste `[0.7, 1.5, 2]`.

### Environnement et versionnage

- `requirements.txt` figé avec `pip freeze` (`ollama`, `pandas`, `numpy`, `matplotlib`, `pytest`, `httpx`, `pydantic`, etc.) et environnement virtuel `venv/`.
- Dépôt git propre au projet, avec deux commits : `Initial commit`, puis l'ajout de `Taches.json` et des premiers essais des réponses de llama3.2 en faisant varier la température.

## Ce qui n'est pas encore fait

- **L'expérience elle-même** : `labo.py` ne lit pas `Taches.json` (le chargement est en commentaire), donc les 10 essais par condition ne sont jamais lancés. Le script actuel est un banc d'essai manuel, pas le protocole décrit dans le JSON.
- **Le scoring** : rien ne compare la réponse à `1850`, ne détecte un piège repris à la place du montant, ni ne compte les mots du slogan.
- **L'analyse** : pandas et matplotlib sont installés mais pas utilisés (aucun tableau de résultats, aucun graphique). Aucun résultat n'est donc disponible et l'hypothèse reste à valider.
- **Les tests** : pytest est installé mais le projet ne contient aucun fichier de test, malgré la mention de « tests » dans le dernier commit.

## Incohérences et points à corriger

1. **Températures** : `[0, 0.7, 1.5]` dans le JSON, `[0.7, 1.5, 2]` dans le code. Le code n'inclut pas la température 0, qui est pourtant la référence pour la tâche factuelle. De plus, 2 est la borne haute de ce qu'Ollama accepte en pratique et produit souvent du texte incohérent : à éviter si l'on veut comparer des conditions exploitables.
2. **Chemin du JSON** : le commentaire utilise `data/taches.json` alors que le fichier s'appelle `Taches.json`. Sous Linux/WSL (sensible à la casse), cela provoquerait une erreur. Le chemin est aussi relatif : le script doit être lancé depuis la racine du projet.
3. **`requirements.txt` en UTF-16** (probablement un `pip freeze` redirigé depuis PowerShell) : `pip install -r` risque d'échouer. À régénérer en UTF-8. La liste contient aussi beaucoup de dépendances indirectes inutiles à l'expérience.
4. **Pas de `.gitignore`** : `venv/` risque d'être versionné. À ignorer avec les caches Python.
5. **Reproductibilité** : avec des températures > 0 les résultats varient d'une exécution à l'autre. Le paramètre `seed` d'Ollama permet de la limiter, à documenter.

## Prochaines étapes suggérées

1. Aligner les températures du code sur celles du JSON, en chargeant la configuration depuis `Taches.json`.
2. Boucler sur tâches x températures x essais et stocker chaque réponse brute (CSV ou JSON).
3. Scorer la tâche A (taux de réponses égales à 1850, taux de réponses égales à un piège) et la tâche B (nombre de mots, respect de la contrainte, diversité des slogans, par exemple en nombre de slogans distincts sur 10).
4. Tracer le taux de réussite et la diversité en fonction de la température, puis conclure sur l'hypothèse.
5. Relier la conclusion à l'usage assurance : température basse pour l'extraction d'information dans les sinistres, plus élevée pour la rédaction marketing.
