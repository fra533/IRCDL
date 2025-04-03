import requests
import json
import os

dois = [
    "10.48550/arxiv.1706.03762",
    "10.3390/app14010192",
    "10.48550/arXiv.2107.04382",
    "10.1007/s11390-023-2070-z",
    "10.3390/electronics13101927",
    "10.1007/s00799-024-00409-1",
    "10.26599/bdma.2023.9020037",
    "10.18495/comengapp.v11i1.398",
    "10.1007/s00799-024-00398-1",
    "10.1109/iccis59958.2023.10453721",
    "10.3390/info15060332",
    "10.1093/bioinformatics/btae672",
    "10.1145/3589334.3645596",
    "10.5281/zenodo.6309855",
    "10.5281/zenodo.5151264",
    "10.1016/j.knosys.2024.112624",
    "10.1145/3589334.3645580",
    "10.1002/cpe.8195",
    "10.1109/edm61683.2024.10615203",
    "10.48550/arxiv.1310.4546",
    "10.1007/978-981-99-8178-6_21",
    "10.1109/jcdl57899.2023.00047",
    "10.18495/comengapp.v8i1.264",
    "10.1007/978-981-99-8088-8_21"
]

def fetch_metadata(doi):
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            item = data.get("message", {})
            return {
                "title": item.get("title", ["N/A"])[0],
                "author": [a.get("given", "") + " " + a.get("family", "") for a in item.get("author", [])],
                "published": item.get("published-print", {}).get("date-parts", [["N/A"]])[0],
                "journal": item.get("container-title", ["N/A"])[0],
                "type": item.get("type", "N/A")
            }
        else:
            return {"error": f"Error {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# Crea cartella results
#os.makedirs("results", exist_ok=True)

# Interroga tutti i DOI e salva i risultati
metadata_list = {doi: fetch_metadata(doi) for doi in dois}
with open("results/metadata.json", "w") as f:
    json.dump(metadata_list, f, indent=2)

print("Metadati salvati in results/metadata.json")