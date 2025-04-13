import sqlite3
import os
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    url = Column(String(512), unique=True, nullable=False)
    source = Column(String(100), nullable=False)
    author = Column(String(100), nullable=True)
    published_date = Column(DateTime, default=datetime.now)
    content = Column(Text, nullable=False)
    processed_content = Column(Text, nullable=True)
    cluster_id = Column(Integer, nullable=True)
    embedding = Column(Text, nullable=True)  # Store as JSON string
    
    entities = relationship("Entity", back_populates="article")
    
class Entity(Base):
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    text = Column(String(255), nullable=False)
    label = Column(String(50), nullable=False)  # PERSON, ORG, LOC, etc.
    count = Column(Integer, default=1)
    
    article = relationship("Article", back_populates="entities")
    
class Cluster(Base):
    __tablename__ = 'clusters'
    
    id = Column(Integer, primary_key=True)
    created_date = Column(DateTime, default=datetime.now)
    topic = Column(String(255), nullable=True)
    article_count = Column(Integer, default=0)
    
class Summary(Base):
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, nullable=False)
    summary_text = Column(Text, nullable=False)
    created_date = Column(DateTime, default=datetime.now)
    
def setup_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'event_data.db')
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    session = setup_db()
    print("Database setup complete!")