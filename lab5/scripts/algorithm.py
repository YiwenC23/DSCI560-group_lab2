from gensim.models import Doc2Vec
from gensim.utils import simple_preprocess
from gensim.models.doc2vec import TaggedDocument
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA


# Example messages (each message is a document)
messages = [
    "This is a sample document about Python programming.",
    "Another document for training on machine learning.",
    "Python is great for data science and machine learning.",
    "I love working with Python and Java.",
    "Machine learning is the future of technology.",
    "Data science involves statistics, programming, and domain knowledge."
]

# Step 2: Train a Doc2Vec model for document embeddings
def train_doc2vec(messages):
    # Tokenize messages: "This is a sample document about Python programming!" --> ['this', 'is', 'sample', 'document', 'about', 'python', 'programming']
    tokenized_messages = [simple_preprocess(message) for message in messages]

    # Prepare tagged documents for doc2vec: ['this', 'is', 'sample', 'document', 'about', 'python', 'programming'] --> TaggedDocument(words=['this', 'is', 'sample', 'document', 'about', 'python', 'programming'], tags=['0'])
    tagged_data = [TaggedDocument(words=words, tags=[str(i)]) for i, words in enumerate(tokenized_messages)]

    # Train doc2vec model
    model = Doc2Vec(vector_size=50, min_count=2, epochs=40)
    model.build_vocab(tagged_data)
    model.train(tagged_data, total_examples=model.corpus_count, epochs=model.epochs)

    return model

# Train the model
doc2vec_model = train_doc2vec(messages)

# Step 3: Generate embeddings for each document
def generate_embeddings(model, messages):
    embeddings = [model.infer_vector(simple_preprocess(message)) for message in messages]
    return embeddings

# Generate embeddings
embeddings = generate_embeddings(doc2vec_model, messages)

# Step 4: Cluster the Embeddings (K-means Example)
def perform_clustering(embeddings, max_clusters=10):
    best_score = -1  # Silhouette Score ranges from -1 to 1
    optimal_clusters = 2  # At least 2 clusters are needed for Silhouette Score
    best_kmeans = None
    best_clusters = None

    # Evaluate Silhouette Score for different numbers of clusters
    for i in range(2, max_clusters + 1):
        kmeans = KMeans(n_clusters=i, random_state=42)
        clusters = kmeans.fit_predict(embeddings)
        score = silhouette_score(embeddings, clusters)

        # Update the best score and corresponding model
        if score > best_score:
            best_score = score
            optimal_clusters = i
            best_kmeans = kmeans
            best_clusters = clusters

    return best_clusters, best_kmeans, optimal_clusters

clusters, kmeans, optimal_clusters = perform_clustering(embeddings, max_clusters=10)

# Step 5: Extract Keywords for Each Cluster (TF-IDF Example)
def extract_keywords(messages, clusters):
    cluster_messages = {i: [] for i in range(max(clusters) + 1)}
    for i, cluster in enumerate(clusters):
        cluster_messages[cluster].append(messages[i])

    # Extract keywords using TF-IDF
    cluster_keywords = {}
    for cluster, messages_in_cluster in cluster_messages.items():
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(messages_in_cluster)
        feature_names = vectorizer.get_feature_names_out()
        tfidf_scores = tfidf_matrix.sum(axis=0).A1
        top_keywords = [feature_names[i] for i in tfidf_scores.argsort()[-5:][::-1]]  # Top 5 keywords
        cluster_keywords[cluster] = top_keywords

    return cluster_keywords

cluster_keywords = extract_keywords(messages, clusters)

def visualize_clusters(embeddings, clusters, cluster_keywords, messages, top_n_samples=3):

    # Step 1: Reduce dimensionality using PCA
    pca = PCA(n_components=2)
    reduced_embeddings = pca.fit_transform(embeddings)

    # Step 2: Plot clusters
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(reduced_embeddings[:, 0], reduced_embeddings[:, 1], c=clusters, cmap='viridis', alpha=0.6)

    # Step 3: Annotate clusters with top keywords
    for cluster in cluster_keywords:
        # Get the centroid of the cluster
        cluster_indices = [i for i, c in enumerate(clusters) if c == cluster]
        centroid = reduced_embeddings[cluster_indices].mean(axis=0)

        # Annotate the centroid with top keywords
        keywords = ", ".join(cluster_keywords[cluster])
        plt.text(centroid[0], centroid[1], f"Cluster {cluster}\nKeywords: {keywords}", 
                 fontsize=10, ha='center', va='center', bbox=dict(facecolor='white', alpha=0.8))

    # Add legend and labels
    plt.legend(*scatter.legend_elements(), title="Clusters")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.title("Cluster Visualization with Keywords")
    plt.show()

    # Step 4: Verify cluster similarity by displaying sample messages
    print("\nVerifying Cluster Similarity:")
    cluster_messages = {i: [] for i in range(max(clusters) + 1)}
    for i, cluster in enumerate(clusters):
        cluster_messages[cluster].append(messages[i])

    for cluster, messages_in_cluster in cluster_messages.items():
        print(f"\nCluster {cluster} Sample Messages:")
        for message in messages_in_cluster[:top_n_samples]:
            print(f" - {message}")

visualize_clusters(embeddings, clusters, cluster_keywords, messages, top_n_samples=3)