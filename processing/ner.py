import spacy
import sys
import os
from collections import Counter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Article, Entity, setup_db

# Load spaCy model with NER
nlp = spacy.load('en_core_web_sm')

def extract_entities(text):
    """Extract named entities from text using spaCy"""
    if not text:
        return []
    
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        # Filter out entities that are likely to be noise
        if len(ent.text) > 1 and not ent.text.isdigit():
            entities.append({
                'text': ent.text,
                'label': ent.label_
            })
    
    return entities

def process_entities():
    """Extract entities from all articles in the database"""
    session = setup_db()
    
    # Get articles that haven't been processed for entities yet
    articles = session.query(Article).outerjoin(Entity).filter(Entity.id.is_(None)).all()
    
    print(f"Found {len(articles)} articles to extract entities from")
    
    for article in articles:
        try:
            # Combine title and content for entity extraction
            full_text = f"{article.title} {article.content}"
            entities = extract_entities(full_text)
            
            # Count entity occurrences
            entity_counter = Counter([(e['text'], e['label']) for e in entities])
            
            for (entity_text, entity_label), count in entity_counter.items():
                entity = Entity(
                    article_id=article.id,
                    text=entity_text,
                    label=entity_label,
                    count=count
                )
                session.add(entity)
            
            print(f"Extracted {len(entity_counter)} unique entities from article: {article.title[:50]}...")
        except Exception as e:
            print(f"Error extracting entities from article {article.id}: {e}")
    
    session.commit()
    session.close()
    
    print("Entity extraction complete!")

if __name__ == "__main__":
    process_entities()