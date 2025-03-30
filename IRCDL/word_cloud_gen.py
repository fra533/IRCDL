import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import math
import os

file_path = r"C:\Users\franc\OneDrive - Alma Mater Studiorum Università di Bologna\Desktop\IRCDL\data\communities - Foglio2.csv"
df = pd.read_csv(file_path)

communities = df['Community'].unique()
colors = sns.color_palette("husl", len(communities))
community_colors = {community: colors[i] for i, community in enumerate(communities)}

def generate_word_cloud(text, color):
    def color_func(*args, **kwargs):
        r, g, b = [int(c * 255) for c in color]
        return f"rgb({r},{g},{b})"
    wordcloud = WordCloud(width=400, height=400, background_color='white',
                          color_func=color_func, collocations=False).generate(text)
    return wordcloud

cols = math.ceil(math.sqrt(len(communities)))
rows = math.ceil(len(communities) / cols)
plt.figure(figsize=(cols * 5, rows * 5))

for i, community in enumerate(communities, 1):
    words = ' '.join(df[df['Community'] == community]['Word'])
    wc = generate_word_cloud(words, community_colors[community])
    plt.subplot(rows, cols, i)
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(community)

os.makedirs('results', exist_ok=True)
plt.suptitle("Nuvole di parole per comunità", fontsize=16)
plt.savefig('results/word_clouds.png')
plt.show()
