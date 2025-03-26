from flask import Flask, jsonify
import requests 
import networkx as nx
import os
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import re
import csv



app = Flask(__name__)

def extract_doi(identifier_string):
    doi_match = re.findall(r'doi:(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)', identifier_string)
    return doi_match[0] if doi_match else None



def get_bibliometric_data(doi_list, output_dir="results"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    for doi in doi_list:
        url = f"https://opencitations.net/meta/api/v1/metadata/doi:{doi}"
        try:
            response = session.get(url)
            response.raise_for_status()  
            data = response.json()
            file_path = os.path.join(output_dir, f"meta_{doi.replace('/', '_')}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except requests.exceptions.RequestException as e:
            print(f"Errore nell'API Meta per il DOI {doi}: {e}")

def get_citations_and_references(doi_list, output_dir="results"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    session = requests.Session()
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))

    for doi in doi_list:
        for citation_type in ["citations", "references"]:
            url = f"https://opencitations.net/index/api/v2/{citation_type}/doi:{doi}"
            try:
                response = session.get(url)
                response.raise_for_status()
                data = response.json()
                file_path = os.path.join(output_dir, f"{citation_type}_{doi.replace('/', '_')}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            except requests.exceptions.RequestException as e:
                print(f"Errore nell'API Index per il DOI {doi}: {e}")

def load_data(doi_list, input_dir="results", data_type="citations"):
    data = {}
    for doi in doi_list:
        file_path = os.path.join(input_dir, f"{data_type}_{doi.replace('/', '_')}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    loaded_data = json.load(f)
                    if isinstance(loaded_data, dict):  
                        data[doi] = [loaded_data]  
                    elif isinstance(loaded_data, list):  
                        data[doi] = loaded_data
                    else:
                        print(f"⚠️ Formato non riconosciuto per {file_path}: {type(loaded_data)}")
                        data[doi] = []
                except json.JSONDecodeError:
                    print(f"⚠️ Errore nel leggere il file JSON: {file_path}")
                    data[doi] = []
        else:
            print(f"⚠️ File {data_type} non trovato per il DOI {doi}")
            data[doi] = []
    return data



def create_graph_from_files(doi_list, bibliometric_data, citations_data, references_data):
    G = nx.DiGraph()
    node_mapping = {}
    counter = 1

    for doi in doi_list:
        if doi not in node_mapping:
            node_mapping[doi] = counter
            counter += 1
            meta = bibliometric_data.get(doi, [])
            title = meta[0].get("title", "") if meta else ""
            authors = meta[0].get("author", "") if meta else ""
            year = meta[0].get("pub_date", "") if meta else ""
            G.add_node(node_mapping[doi], label=title, authors=authors, year=year, seed=True)

        if doi in citations_data:
            for citation in citations_data[doi]:
                citing_doi = extract_doi(citation.get('citing', ''))
                if citing_doi not in node_mapping:
                    node_mapping[citing_doi] = counter
                    counter += 1
                    meta = bibliometric_data.get(citing_doi, [])
                    title = meta[0].get("title", "") if meta else ""
                    authors = meta[0].get("author", "") if meta else ""
                    year = meta[0].get("pub_date", "") if meta else ""
                    G.add_node(node_mapping[citing_doi], label=title, authors=authors, year=year, seed=False)
                G.add_edge(node_mapping[doi], node_mapping[citing_doi])


        if doi in references_data:
            for reference in references_data[doi]:
                cited_doi = extract_doi(reference.get('cited', ''))
                if cited_doi not in node_mapping:
                    node_mapping[cited_doi] = counter
                    counter += 1
                    meta = bibliometric_data.get(cited_doi, [])
                    title = meta[0].get("title", "") if meta else ""
                    authors = meta[0].get("author", "") if meta else ""
                    year = meta[0].get("pub_date", "") if meta else ""
                    G.add_node(node_mapping[cited_doi], label=title, authors=authors, year=year, seed=False)
                G.add_edge(node_mapping[doi], node_mapping[cited_doi])


    return G, node_mapping


def export_graph_to_gexf(G, output_dir="results"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    gexf_path = os.path.join(output_dir, "citation_graph.gexf")
    nx.write_gexf(G, gexf_path)

def export_graph_to_csv(G, node_mapping, output_dir="results"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    node_file = os.path.join(output_dir, "nodes.csv")
    edge_file = os.path.join(output_dir, "edges.csv")

    with open(node_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Id", "Label", "Authors", "Year", "Seed"])
        for node, data in G.nodes(data=True):
            writer.writerow([node, data.get("label", ""), data.get("authors", ""), data.get("year", ""), data.get("seed", False)])

    with open(edge_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Source", "Target"])
        for source, target in G.edges():
            writer.writerow([source, target])

def main():


    doi_list = ["10.1109/ICTAI56018.2022.00043", "10.1145/3589334.3645580", "10.23919/EECSI56542.2022.9946586", 
                "10.1109/TKDE.2020.3021256", "10.1007/s00521-020-05088-y", "10.48550/arXiv.2107.04382", 
                "10.1109/icdm50108.2020.00060", "10.1007/978-3-030-34223-4_34", "10.1007/978-981-99-8088-8_21", 
                "10.1007/s11390-023-2070-z", "10.18495/comengapp.v8i1.264", "10.1145/3502730", 
                "10.1109/bigdata47090.2019.9005458", "10.1007/s13042-022-01686-5", "10.1109/icws53863.2021.00071", 
                "10.1109/IJCNN52387.2021.9534125", "10.3390/e22040416", "10.1007/978-3-030-47426-3_29", 
                "10.3390/app14010192", "10.1109/bigdata55660.2022.10020229", "10.1007/978-3-319-67008-9_24", 
                "10.1145/3357384.3358153", "10.1109/ACCESS.2022.3190088", "10.1145/3219819.3219859", 
                "10.1007/s11192-022-04426-2", "10.1007/978-3-031-16802-4_16"]
    
    #get_citations_and_references(doi_list) 

    all_dois = set(doi_list)

    citations_data = load_data(doi_list, "results", "citations")
    references_data = load_data(doi_list, "results", "references")

    for doi in doi_list:
        if doi in citations_data:
            for citation in citations_data[doi]:
                citing_doi = extract_doi(citation.get('citing', ''))
                if citing_doi:
                    all_dois.add(citing_doi)

        if doi in references_data:
            for reference in references_data[doi]:
                cited_doi = extract_doi(reference.get('cited', ''))
                if cited_doi:
                    all_dois.add(cited_doi)

    
    #get_bibliometric_data(all_dois)

    bibliometric_data = load_data(all_dois, "results", "meta")
    G, node_mapping = create_graph_from_files(all_dois, bibliometric_data, citations_data, references_data)
    export_graph_to_csv(G, node_mapping)


if __name__ == "__main__":
    main()



