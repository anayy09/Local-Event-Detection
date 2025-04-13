import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import Counter
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Article, Entity, Cluster, setup_db

def create_entity_frequency_chart(output_dir='webapp/static'):
    """Create a chart showing the most frequent entities"""
    session = setup_db()
    
    # Get top entities
    top_entities = session.query(
        Entity.text, Entity.label, func.sum(Entity.count).label('total_count')
    ).group_by(
        Entity.text, Entity.label
    ).order_by(
        func.sum(Entity.count).desc()
    ).limit(20).all()
    
    if not top_entities:
        print("No entities found.")
        session.close()
        return
    
    # Prepare data for plotting
    df = pd.DataFrame([(e.text, e.label, e.total_count) for e in top_entities], 
                      columns=['Entity', 'Type', 'Count'])
    
    # Create figure
    plt.figure(figsize=(12, 8))
    sns.set_style("whitegrid")
    
    # Create bar plot
    sns.barplot(data=df, x='Count', y='Entity', hue='Type')
    
    plt.title('Most Frequent Entities', fontsize=16)
    plt.xlabel('Frequency', fontsize=12)
    plt.ylabel('Entity', fontsize=12)
    
    # Save figure
    os.makedirs(output_dir, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'entity_frequency.png'), dpi=100)
    plt.close()
    
    print("Entity frequency chart created!")

def create_cluster_distribution_chart(output_dir='webapp/static'):
    """Create a chart showing the distribution of articles in clusters"""
    session = setup_db()
    
    # Get cluster counts
    clusters = session.query(Cluster.id, Cluster.article_count, Cluster.topic).all()
    
    if not clusters:
        print("No clusters found.")
        session.close()
        return
    
    # Prepare data for plotting
    df = pd.DataFrame([(c.id, c.article_count, c.topic if c.topic else f"Cluster {c.id}") 
                       for c in clusters], 
                      columns=['ID', 'Articles', 'Topic'])
    
    # Create figure
    plt.figure(figsize=(10, 8))
    sns.set_style("whitegrid")
    
    # Create bar plot
    ax = sns.barplot(data=df, x='ID', y='Articles')
    
    # Add topic labels
    for i, topic in enumerate(df['Topic']):
        ax.text(i, 0.5, topic, rotation=90, ha='center', fontsize=10)
    
    plt.title('Article Distribution by Cluster', fontsize=16)
    plt.xlabel('Cluster ID', fontsize=12)
    plt.ylabel('Number of Articles', fontsize=12)
    
    # Save figure
    os.makedirs(output_dir, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'cluster_distribution.png'), dpi=100)
    plt.close()
    
    print("Cluster distribution chart created!")

def create_source_distribution_chart(output_dir='webapp/static'):
    """Create a chart showing the distribution of articles by source"""
    session = setup_db()
    
    # Get article source counts
    sources = session.query(
        Article.source, func.count(Article.id).label('count')
    ).group_by(
        Article.source
    ).all()
    
    if not sources:
        print("No sources found.")
        session.close()
        return
    
    # Prepare data for plotting
    df = pd.DataFrame([(s.source, s.count) for s in sources], 
                      columns=['Source', 'Count'])
    
    # Create figure
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    
    # Create pie chart
    plt.pie(df['Count'], labels=df['Source'], autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    plt.title('Article Distribution by Source', fontsize=16)
    
    # Save figure
    os.makedirs(output_dir, exist_ok=True)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'source_distribution.png'), dpi=100)
    plt.close()
    
    print("Source distribution chart created!")

def generate_all_visualizations():
    """Generate all visualizations"""
    create_entity_frequency_chart()
    create_cluster_distribution_chart()
    create_source_distribution_chart()

if __name__ == "__main__":
    generate_all_visualizations()