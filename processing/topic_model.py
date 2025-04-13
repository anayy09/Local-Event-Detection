import sys
import os
import numpy as np
import json
from bertopic import BERTopic
from sklearn.feature_extraction.text import CountVectorizer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Article, Cluster, setup_db

def extract_topics():
    """Extract topics from articles using BERTopic"""
    session = setup_db()
    
    # Get all articles with processed content
    articles = session.query(Article).filter(Article.processed_content.isnot(None)).all()
    
    if len(articles) < 5:  # Need a minimum number of documents
        print(f"Not enough articles for topic modeling. Found {len(articles)} articles.")
        session.close()
        return
    
    # Prepare data
    article_ids = [article.id for article in articles]
    processed_texts = [article.processed_content for article in articles]
    
    # Load custom vectorizer with English stop words
    vectorizer = CountVectorizer(stop_words="english")
    
    try:
        # Initialize and fit BERTopic model
        topic_model = BERTopic(vectorizer_model=vectorizer, min_topic_size=2)
        topics, probs = topic_model.fit_transform(processed_texts)
        
        # Get topic information
        topic_info = topic_model.get_topic_info()
        
        # Update cluster topics in database
        for i, article_id in enumerate(article_ids):
            article = session.query(Article).get(article_id)
            if article and article.cluster_id is not None:
                cluster = session.query(Cluster).filter_by(id=article.cluster_id).first()
                if cluster:
                    topic_id = topics[i]
                    if topic_id != -1:  # -1 is the outlier topic
                        topic_words = topic_model.get_topic(topic_id)
                        topic_label = ", ".join([word for word, _ in topic_words[:5]])
                        cluster.topic = topic_label
        
        session.commit()
        print(f"Topic modeling complete! Extracted topics using BERTopic.")
    except Exception as e:
        print(f"Error in topic modeling: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    extract_topics()