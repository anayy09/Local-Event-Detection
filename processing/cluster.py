import numpy as np
import json
import sys
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Article, Cluster, setup_db

def get_embeddings_tfidf(processed_texts):
    """Get TF-IDF embeddings for articles"""
    vectorizer = TfidfVectorizer(max_features=5000)
    return vectorizer.fit_transform(processed_texts)

def get_embeddings_transformer(processed_texts):
    """Get sentence transformer embeddings for articles"""
    model = SentenceTransformer('all-MiniLM-L6-v2')  # Smaller model for faster processing
    return model.encode(processed_texts)

def cluster_articles(embedding_type='tfidf', min_cluster_size=2):
    """Cluster articles based on their content"""
    session = setup_db()
    
    # Get articles that have been preprocessed but not assigned to clusters
    articles = session.query(Article).filter(
        Article.processed_content.isnot(None),
    ).all()
    
    if len(articles) < min_cluster_size:
        print(f"Not enough articles to form clusters. Found {len(articles)} articles.")
        session.close()
        return
    
    # Extract processed text and IDs
    article_ids = [article.id for article in articles]
    processed_texts = [article.processed_content for article in articles]
    
    # Get embeddings
    if embedding_type == 'transformer':
        embeddings = get_embeddings_transformer(processed_texts)
        # Convert to numpy array if not already
        embeddings = np.array(embeddings)
    else:  # Default to TF-IDF
        embeddings = get_embeddings_tfidf(processed_texts)
        # Convert sparse matrix to dense if using scikit-learn
        if hasattr(embeddings, 'toarray'):
            embeddings = embeddings.toarray()
    
    # Determine optimal number of clusters (simple heuristic)
    n_clusters = max(2, min(10, len(processed_texts) // 4))
    
    # Perform clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(embeddings)
    
    # Store embeddings and cluster assignments
    for i, article_id in enumerate(article_ids):
        article = session.query(Article).get(article_id)
        if article:
            article.cluster_id = int(cluster_labels[i])
            # Store embedding as JSON string
            article.embedding = json.dumps(embeddings[i].tolist())
    
    # Create or update cluster information
    cluster_counts = {}
    for label in cluster_labels:
        label_int = int(label)
        if label_int not in cluster_counts:
            cluster_counts[label_int] = 0
        cluster_counts[label_int] += 1
    
    for cluster_id, count in cluster_counts.items():
        cluster = session.query(Cluster).filter_by(id=cluster_id).first()
        if not cluster:
            cluster = Cluster(id=cluster_id, article_count=count)
            session.add(cluster)
        else:
            cluster.article_count = count
    
    session.commit()
    session.close()
    
    print(f"Clustering complete! Created {n_clusters} clusters.")

if __name__ == "__main__":
    cluster_articles()