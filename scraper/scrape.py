import requests
import json
import time
from bs4 import BeautifulSoup
from newspaper import Article as NewspaperArticle
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Article, setup_db

def clean_text(text):
    if not text:
        return ""
    return text.strip()

def extract_article(url):
    """Extract article content using newspaper3k"""
    try:
        article = NewspaperArticle(url)
        article.download()
        article.parse()
        
        return {
            'title': article.title,
            'content': article.text,
            'author': article.authors[0] if article.authors else None,
            'published_date': article.publish_date
        }
    except Exception as e:
        print(f"Error extracting article from {url}: {e}")
        return None

def scrape_abc_local(session, location="seattle"):
    """Scrape ABC local news for a given location"""
    url = f"https://abc7news.com/{location}-news/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # Find article links - adjust selector based on actual site structure
        article_elements = soup.select('.article-feed__story')
        
        for article_elem in article_elements:
            link_elem = article_elem.select_one('a')
            if not link_elem:
                continue
                
            article_url = link_elem.get('href')
            if not article_url.startswith('http'):
                article_url = f"https://abc7news.com{article_url}"
            
            # Check if article already exists in DB
            existing = session.query(Article).filter_by(url=article_url).first()
            if existing:
                continue
                
            article_data = extract_article(article_url)
            if not article_data:
                continue
                
            new_article = Article(
                title=article_data['title'],
                url=article_url,
                source="ABC Local News",
                author=article_data['author'],
                content=article_data['content'],
                published_date=article_data['published_date'] or datetime.now()
            )
            
            session.add(new_article)
            articles.append(new_article)
        
        session.commit()
        print(f"Scraped {len(articles)} new articles from ABC Local News")
    except Exception as e:
        print(f"Error scraping ABC Local News: {e}")
        session.rollback()

def scrape_local_newspaper(session, newspaper_url="https://www.seattletimes.com"):
    """Scrape a local newspaper website"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(newspaper_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []
        
        # Find article links - adjust selector based on actual site structure
        article_links = soup.select('article a')
        
        for link in article_links[:15]:  # Limit to prevent too many requests
            article_url = link.get('href')
            if not article_url or not article_url.startswith('http'):
                if not article_url.startswith('/'):
                    continue
                article_url = f"{newspaper_url}{article_url}"
            
            # Check if article already exists in DB
            existing = session.query(Article).filter_by(url=article_url).first()
            if existing:
                continue
                
            article_data = extract_article(article_url)
            if not article_data or not article_data.get('content'):
                continue
                
            new_article = Article(
                title=article_data['title'],
                url=article_url,
                source="Seattle Times",
                author=article_data['author'],
                content=article_data['content'],
                published_date=article_data['published_date'] or datetime.now()
            )
            
            session.add(new_article)
            articles.append(new_article)
            time.sleep(1)  # Be respectful to the website
        
        session.commit()
        print(f"Scraped {len(articles)} new articles from local newspaper")
    except Exception as e:
        print(f"Error scraping local newspaper: {e}")
        session.rollback()

def run_scraper():
    session = setup_db()
    scrape_abc_local(session)
    scrape_local_newspaper(session)
    session.close()

if __name__ == "__main__":
    run_scraper()