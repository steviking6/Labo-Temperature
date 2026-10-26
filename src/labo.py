import json
import re 
import csv
import pandas as pd
import matplotlib.pyplot as plt 

from pathlib import Path
from tqdm.auto import tqdm 
from importlib import import_module
from pathlib import Path 


donnees = json.loads(Path("data/taches.json").read_text(encoding="utf-8"))
tache_a = donnees["taches"]["A_factuelle"]
prompt_a = tache_a["prompt"].format(texte_source=tache_a["texte_source"])


def generer(prompt:str, temperature:float, modele:str)->str:    
    try:
        ollama = import_module("ollama")
    except ModuleNotFoundError as exc:
        if exc.name == "ollama":
            raise RuntimeError("Install the Ollama Python package with 'pip install ollama'.") from exc
        raise

    r = ollama.chat(model=modele,
                    messages = [{"role":"user", "content":prompt}],
                    options={"temperature":temperature})
    texte = r["message"]["content"]
    return texte 

import json
from pathlib import Path

def stocker_sortie_a(
    chemin: str | Path,
    tour :int,
    prompt: str,
    temperature: float,
    reponse_obtenue: str,
    reponse_attendue: str,
) -> None:
    chemin = Path(chemin)                                  # accepte str ou Path
    chemin.parent.mkdir(parents=True, exist_ok=True)       # crée data/ si besoin, ne fait rien sinon

    ligne = {
        "tour":tour,
        "data":{
            "prompt": prompt,
            "temperature": temperature,
            "reponse_obtenue": reponse_obtenue,
            "reponse_attendue": reponse_attendue,
        }
    }

    with open(chemin, "a", encoding="utf-8") as file:     # "a" = créer OU ajouter
        file.write(json.dumps(ligne, ensure_ascii=False, indent=2) + "\n")


def extraire_montant(reponse: str) -> int | None:
    match = re.search(r"\d[\d\s\u00a0]*", reponse)
    if match is None:
        return None
    nombre_propre = match.group().replace(" ", "").replace("\u00a0", "")
    return int(nombre_propre)

def exporter_csv(lignes: list[dict], chemin: Path)->None:
    if not lignes:
        return 
    with open(chemin, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=lignes[0].keys())
        writer.writeheader()
        writer.writerows(lignes)
        


def calculer_taux_reussite(chemin_csv_entree: Path, chemin_csv_sortie: Path) -> pd.DataFrame:
    """
    Lit le CSV des résultats bruts et calcule le taux de bonnes réponses
    par température (toutes les tentatives de tous les tours agrégées).
    """
    df = pd.read_csv(chemin_csv_entree)

    # colonne booléenne : True si la réponse est correcte
    df["correct"] = df["reponse_obtenue"] == df["reponse_attendue"]

    # on regroupe par température et on calcule les stats
    stats = df.groupby("temperature").agg(
        nb_essais=("correct", "count"),
        nb_corrects=("correct", "sum"),
        taux_reussite=("correct", "mean"),   # mean d'un booléen = proportion de True
    ).reset_index()

    # convertit en pourcentage pour la lisibilité
    stats["taux_reussite"] = (stats["taux_reussite"] * 100).round(1)

    stats.to_csv(chemin_csv_sortie, index=False, encoding="utf-8")
    return stats

def tracer_taux_reussite(stats: pd.DataFrame, chemin_image: Path | None = None) -> None:
    """Trace le taux de réussite en fonction de la température."""
    fig, ax = plt.subplots(figsize=(9, 5))

    # bar chart avec couleur selon le taux (gradient visuel)
    bars = ax.bar(
        stats["temperature"].astype(str),         # str sinon matplotlib traite les T comme numériques
        stats["taux_reussite"],
        color=plt.cm.RdYlGn(stats["taux_reussite"] / 100),   # rouge → vert
        edgecolor="black",
    )

    # affiche la valeur sur chaque barre
    for barre, taux, n in zip(bars, stats["taux_reussite"], stats["nb_essais"]):
        ax.text(
            barre.get_x() + barre.get_width() / 2,
            barre.get_height() + 1,
            f"{taux}%\n(n={n})",
            ha="center", va="bottom", fontsize=9,
        )

    ax.set_xlabel("Température")
    ax.set_ylabel("Taux de bonnes réponses (%)")
    ax.set_title("Impact de la température sur la précision du modèle")
    ax.set_ylim(0, 110)   # marge en haut pour les labels
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    if chemin_image:
        plt.savefig(chemin_image, dpi=150)
    plt.show()

'''
def compresser_texte(texte: str, max_chars: int = 80) -> str:
    """Tronque un texte long pour l'affichage, en gardant début + fin."""
    if len(texte) <= max_chars:
        return texte
    moitie = (max_chars - 5) // 2            # -5 pour les " ... " du milieu
    return f"{texte[:moitie]} ... {texte[-moitie:]}"


def compresser_ligne(ligne: dict, max_chars: int = 80) -> dict:
    """Renvoie une COPIE de la ligne avec les champs texte raccourcis."""
    return {
        cle: compresser_texte(valeur, max_chars) if isinstance(valeur, str) else valeur
        for cle, valeur in ligne.items()
    }
'''

def lancer_experience(temperatures, modele, tour, max_t):
    lignes = []
    max_tours = max_t
    with tqdm(desc=f"Progression pour {modele}", unit="tour") as pbar:
        
        try :
            while True :
                tour += 1
                
                
                print(f"\n=================TOUR Numero : {tour} =====================")
                #prompt_utilisateur = input(">Entre ton prompt: ") 
                if tour+1 == max_tours:
                    break 
                
                prompt = prompt_a + "\nle texte source : " + "\n\n"+ tache_a["texte_source"]
                for i in range (len(temperatures)):
                    response = generer(prompt, temperatures[i], modele)
                    montant = extraire_montant(response)
                    lignes.append({
                        "chemin" : Path("data/sortie_a.jsonl"),
                        "tour" : tour,
                        "prompt" :prompt_a,
                        "temperature" : temperatures[i],
                        "reponse_obtenue" :montant,
                        "reponse_attendue" : tache_a["reponse_attendue"],
                    })
                    
                    stocker_sortie_a(
                        chemin=Path("data/sortie_a.jsonl"),
                        tour=tour,
                        prompt=prompt_a,
                        temperature=temperatures[i],
                        reponse_obtenue=montant,
                        reponse_attendue=tache_a["reponse_attendue"],
                    )
                    tqdm.write(f"\nreponse pour la temperature {temperatures[i]}: \n {response}")
                pbar.update(1)
        finally:
             exporter_csv(lignes, Path("data/sortie.csv"))
             print("CSV sauvégardé")
    
            
def main():
    temperatures = [0, 0.3, 0.7, 1.5, 2]
    modele = "llama3.2"
    tour = 0
    
    lancer_experience(temperatures=temperatures, modele=modele, tour=tour, max_t=60)
    
    stats = calculer_taux_reussite(
        chemin_csv_entree=Path("data/sortie.csv"),
        chemin_csv_sortie=Path("data/stats.csv"),
    )
    print(stats)

    tracer_taux_reussite(stats, chemin_image=Path("data/graph.png"))

if __name__ == "__main__":
    main()
    

    
        

