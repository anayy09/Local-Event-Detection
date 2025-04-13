import spacy
import sys
import os
import json
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Article, setup_db

# Load spaCy model
nlp = spacy.load('en_core_web_sm')
stop_words = set(stopwords.words('english'))

def clean_text(text):
    """Basic text cleaning"""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove special characters and digits
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    return text

def preprocess_text(text):
    """Preprocess text using spaCy"""
    if not text:
        return ""
    
    # Clean text
    text = clean_text(text)
    
    # Process with spaCy
    doc = nlp(text)
    
    # Extract lemmas, excluding stopwords and punctuation
    tokens = [token.lemma_.lower() for token in doc 
              if not token.is_stop and not token.is_punct and len(token.text) > 2]
    
    return " ".join(tokens)

def preprocess_articles():
    """Preprocess all articles in the database"""
    session = setup_db()
    
    # Get articles that haven't been processed yet
    articles = session.query(Article).filter(Article.processed_content.is_(None)).all()
    
    print(f"Found {len(articles)} articles to preprocess")
    
    for article in articles:
        try:
            # Combine title and content for preprocessing
            full_text = f"{article.title} {article.content}"
            processed_text = preprocess_text(full_text)
            
            article.processed_content = processed_text
            print(f"Preprocessed article: {article.title[:50]}...")
        except Exception as e:
            print(f"Error preprocessing article {article.id}: {e}")
    
    session.commit()
    session.close()
    
    print("Preprocessing complete!")

if __name__ == "__main__":
    preprocess_articles()