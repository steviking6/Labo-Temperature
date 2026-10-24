import json

from importlib import import_module
from pathlib import Path 

'''
donnees = json.loads(Path("data/taches.json").read_text(encoding="utf-8"))
tache_a = donnees["taches"]["A_factuelle"]
prompt_a = tache_a["prompt"].format(texte_source=tache_a["texte_source"])
'''

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

temperatures = [0.7, 1.5, 2]
modele = "llama3.2"

tour = 0
    
while True :
    tour += 1
    
    print(f"=================TOUR Numero : {tour} =====================")
    prompt = input(">Quelle est votre requete ?")
    if prompt == "exit":
        break 
    
    for i in range(len(temperatures)):
        response = generer(prompt, temperatures[i], modele)
        print (f"\nreponse pour la temperature {temperatures[i]}: \n {response}")
        
        
