import sys
import os
import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Article, Cluster, Summary, setup_db

def load_summarizer():
    """Load the summarization model"""
    # Use smaller model for resource efficiency
    model_name = "facebook/bart-large-cnn"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    
    # Use GPU if available
    device = 0 if torch.cuda.is_available() else -1
    summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=device)
    
    return summarizer

def get_top_entities(session, article_ids, limit=10):
    """Get top entities mentioned in a cluster of articles"""
    from sqlalchemy import func
    from database.models import Entity
    
    # Query to get the most frequent entities across the articles
    top_entities = session.query(
        Entity.text, Entity.label, func.sum(Entity.count).label('total_count')
    ).filter(
        Entity.article_id.in_(article_ids)
    ).group_by(
        Entity.text, Entity.label
    ).order_by(
        func.sum(Entity.count).desc()
    ).limit(limit).all()
    
    return top_entities

def generate_cluster_summaries():
    """Generate summaries for each cluster"""
    session = setup_db()
    
    # Get all clusters with at least 2 articles
    clusters = session.query(Cluster).filter(Cluster.article_count >= 2).all()
    
    if not clusters:
        print("No clusters found to summarize.")
        session.close()
        return
    
    try:
        summarizer = load_summarizer()
        
        for cluster in clusters:
            # Check if summary already exists
            existing_summary = session.query(Summary).filter_by(cluster_id=cluster.id).first()
            if existing_summary:
                print(f"Summary for cluster {cluster.id} already exists.")
                continue
            
            # Get all articles in this cluster
            articles = session.query(Article).filter_by(cluster_id=cluster.id).all()
            article_ids = [article.id for article in articles]
            
            if len(articles) < 2:
                continue
            
            # Get top entities
            top_entities = get_top_entities(session, article_ids, limit=5)
            entity_text = ""
            if top_entities:
                persons = [e.text for e in top_entities if e.label == "PERSON"][:2]
                locations = [e.text for e in top_entities if e.label == "LOC" or e.label == "GPE"][:2]
                organizations = [e.text for e in top_entities if e.label == "ORG"][:2]
                
                entity_text = ""
                if persons:
                    entity_text += f"People: {', '.join(persons)}. "
                if locations:
                    entity_text += f"Locations: {', '.join(locations)}. "
                if organizations:
                    entity_text += f"Organizations: {', '.join(organizations)}. "
            
            # Prepare text for summarization
            combined_text = ""
            for article in articles:
                combined_text += f"{article.title}. {article.content[:500]} "
            
            # Truncate to fit model's max input length (typically 1024 tokens)
            max_length = 4000  # Characters, not tokens, but a safe estimate
            if len(combined_text) > max_length:
                combined_text = combined_text[:max_length]
            
            # Generate summary
            try:
                summary = summarizer(combined_text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
                
                # Add entity information if available
                if entity_text:
                    summary = f"{summary} {entity_text}"
                
                # Store summary
                new_summary = Summary(
                    cluster_id=cluster.id,
                    summary_text=summary
                )
                session.add(new_summary)
                print(f"Generated summary for cluster {cluster.id}")
            except Exception as e:
                print(f"Error generating summary for cluster {cluster.id}: {e}")
        
        session.commit()
        print("Summary generation complete!")
    except Exception as e:
        print(f"Error in summarization process: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    generate_cluster_summaries()