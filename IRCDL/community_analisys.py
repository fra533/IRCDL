import pandas as pd
import re
from collections import Counter
import os

STOPWORDS = set([
    "author", "name", "disambiguation", "the", "and", "is", "in", "it", "of", "to", "a", "an", "that", "for", "on", "with", "as", "by", "at", "from", "about", "into", "over", "after", "before", "under", "between", "among", "through", "during", "above", "below", "without", "within", "along", "across", "behind", "beyond", "toward", "upon", "against", "out", "up", "down", "off", "over", "under", "again", "further", "then", "once"
])

def extract_keywords(title):
    tokens = re.findall(r"\b\w+\b", title.lower())  # Tokenizzazione semplice
    tokens = [word for word in tokens if word not in STOPWORDS and len(word) > 2]
    return tokens

def analyze_keywords_by_cluster(input_csv):
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(r"C:\Users\franc\OneDrive - Alma Mater Studiorum Università di Bologna\Desktop\IRCDL\data\communities.csv")
    print("Colonne trovate nel CSV:", df.columns)

    cluster_keywords = {}

    for _, row in df.iterrows():
        title = str(row['Label'])
        cluster = row['Cluster']
        keywords = extract_keywords(title)

        if cluster not in cluster_keywords:
            cluster_keywords[cluster] = []

        cluster_keywords[cluster].extend(keywords)

    keyword_summary = {}
    for cluster, keywords in cluster_keywords.items():
        keyword_counts = Counter(keywords).most_common(10)
        keyword_summary[cluster] = keyword_counts

    output_file = os.path.join(output_dir, "keyword_analysis.csv")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("Cluster,Keyword,Frequency\n")
        for cluster, keywords in keyword_summary.items():
            for keyword, freq in keywords:
                f.write(f"{cluster},{keyword},{freq}\n")

    print("Analisi completata! Risultato salvato in results/keyword_analysis.csv")

analyze_keywords_by_cluster("results/communities.csv")
