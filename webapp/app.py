import sys
import os
import json
from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Article, Cluster, Summary, Entity, setup_db
from scraper.scrape import run_scraper
from processing.preprocess import preprocess_articles
from processing.ner import process_entities
from processing.cluster import cluster_articles
from processing.topic_model import extract_topics
from summarization.summarize import generate_cluster_summaries
from analysis.visualize import generate_all_visualizations
from sqlalchemy import func

app = Flask(__name__)

@app.route('/')
def index():
    """Home page showing clusters and summaries"""
    session = setup_db()
    
    # Get all clusters with their summaries
    clusters = session.query(Cluster).all()
    
    cluster_data = []
    for cluster in clusters:
        summary = session.query(Summary).filter_by(cluster_id=cluster.id).first()
        article_count = cluster.article_count
        
        # Get a sample article from the cluster
        sample_article = session.query(Article).filter_by(cluster_id=cluster.id).first()
        
        if summary and sample_article:
            cluster_data.append({
                'id': cluster.id,
                'topic': cluster.topic or f"Cluster {cluster.id}",
                'summary': summary.summary_text,
                'article_count': article_count,
                'sample_title': sample_article.title
            })
    
    session.close()
    return render_template('index.html', clusters=cluster_data)

@app.route('/cluster/<int:cluster_id>')
def cluster_detail(cluster_id):
    """Detail page for a specific cluster"""
    session = setup_db()
    
    # Get cluster info
    cluster = session.query(Cluster).filter_by(id=cluster_id).first()
    if not cluster:
        session.close()
        return "Cluster not found", 404
    
    # Get cluster summary
    summary = session.query(Summary).filter_by(cluster_id=cluster_id).first()
    
    # Get articles in this cluster
    articles = session.query(Article).filter_by(cluster_id=cluster_id).all()
    
    # Get top entities for this cluster
    top_entities = []
    if articles:
        article_ids = [article.id for article in articles]
        
        top_entities = session.query(
            Entity.text, Entity.label, Entity.count
        ).filter(
            Entity.article_id.in_(article_ids)
        ).order_by(
            Entity.count.desc()
        ).limit(15).all()
    
    session.close()
    
    return render_template(
        'cluster_detail.html',
        cluster=cluster,
        summary=summary.summary_text if summary else "No summary available",
        articles=articles,
        entities=top_entities
    )

@app.route('/analytics')
def analytics():
    """Analytics page"""
    # Generate visualizations
    generate_all_visualizations()
    
    session = setup_db()
    
    # Get some statistics
    stats = {
        'total_articles': session.query(Article).count(),
        'total_clusters': session.query(Cluster).count(),
        'total_entities': session.query(Entity).count()
    }
    
    # Get article count by source
    sources = session.query(
        Article.source, func.count(Article.id).label('count')
    ).group_by(
        Article.source
    ).all()
    
    source_stats = {source.source: source.count for source in sources}
    
    session.close()
    
    return render_template('analytics.html', stats=stats, sources=source_stats)

def run_pipeline():
    """Run the full data pipeline"""
    print("Running data pipeline...")
    run_scraper()
    preprocess_articles()
    process_entities()
    cluster_articles()
    extract_topics()
    generate_cluster_summaries()
    generate_all_visualizations()
    print("Pipeline completed at", datetime.now())

def setup_scheduler():
    """Set up the scheduler to run the pipeline periodically"""
    scheduler = BackgroundScheduler()
    # Run every 6 hours
    scheduler.add_job(run_pipeline, 'interval', hours=6)
    scheduler.start()
    print("Scheduler started!")

if __name__ == "__main__":
    # Optionally run the pipeline once before starting the app
    # run_pipeline()
    
    # Setup scheduler
    setup_scheduler()
    
    # Start Flask app
    app.run(debug=True)