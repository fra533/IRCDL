import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from matplotlib.colors import to_rgb

# Define the path to your CSV file
file_path = r"C:\Users\franc\OneDrive - Alma Mater Studiorum Università di Bologna\Desktop\IRCDL\results\keyword_analysis.csv"
df = pd.read_csv(file_path)

# Calculate total frequency per cluster to identify the 4 largest communities
cluster_totals = df.groupby('Cluster')['Frequency'].sum().reset_index()
top_clusters = cluster_totals.sort_values('Frequency', ascending=False).head(4)['Cluster'].tolist()
print(f"Top 4 clusters by frequency: {top_clusters}")

# Define colors for the 4 largest communities (using your specified colors)
community_colors = {
    0: "#FFB2BB",  # Pink/red - largest cluster
    1: "#8CE3AE",  # Green - second largest
    2: "#F7CB6F",  # Yellow/gold - third largest
    3: "#B9D3F8",  # Blue - fourth largest
}

def generate_word_cloud(community_df, color):
    # Create a dictionary of words and their frequencies
    word_freq = dict(zip(community_df['Keyword'], community_df['Frequency']))
    
    # Define color function
    rgb_color = to_rgb(color)
    r, g, b = [int(c * 255) for c in rgb_color]
    color_func = lambda *args, **kwargs: f"rgb({r},{g},{b})"
    
    # Generate the wordcloud
    wordcloud = WordCloud(
        width=800, 
        height=800, 
        background_color='white',
        color_func=color_func, 
        collocations=False,
        prefer_horizontal=0.9,
        max_words=100,
        min_font_size=8
    ).generate_from_frequencies(word_freq)
    
    return wordcloud

# Create a 2x2 grid for the 4 largest communities
fig, axes = plt.subplots(2, 2, figsize=(16, 16))
axes = axes.flatten()  # Flatten to make indexing easier

# Generate and plot wordclouds for only the top 4 communities
for i, community in enumerate(top_clusters):
    community_df = df[df['Cluster'] == community]
    
    # Skip if no data (shouldn't happen for top clusters)
    if community_df.empty:
        continue
        
    wc = generate_word_cloud(community_df, community_colors[community])
    
    # Use the flattened axes
    ax = axes[i]
    ax.imshow(wc, interpolation='bilinear')
    ax.axis('off')
    
    # Set title with consistent padding
    ax.set_title(f"Community {community}", fontsize=20, pad=20)

# Adjust the layout to have proper spacing between subplots and titles
plt.tight_layout(h_pad=5.0, w_pad=5.0)
plt.subplots_adjust(top=0.80, bottom=0.05, left=0.05, right=0.95)

# Save the combined figure
os.makedirs('results', exist_ok=True)
plt.savefig('results/top4_word_clouds.png', dpi=300)
plt.show()

# Generate individual high-resolution wordclouds for each top community
for community in top_clusters:
    community_df = df[df['Cluster'] == community]
    
    fig = plt.figure(figsize=(12, 12))
    wc = generate_word_cloud(community_df, community_colors[community])
    ax = plt.gca()
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    
    # Set a consistent title padding
    ax.set_title(f"Community {community}", fontsize=24, pad=30)
    
    # Adjust the layout for individual plots
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)
    
    plt.savefig(f'results/wordcloud_cluster_{community}.png', dpi=300)
    plt.close()

print("Wordclouds generated successfully!")