import requests
import json
import time
import feedparser
import re
from bs4 import BeautifulSoup
from newspaper import Article as NewspaperArticle
from datetime import datetime
import sys
import os
import random
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import Article, setup_db

def clean_text(text):
    if not text:
        return ""
    # Remove html tags
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()

def extract_article(url):
    """Extract article content using newspaper3k"""
    try:
        article = NewspaperArticle(url)
        article.download()
        article.parse()
        
        # If content is too short, it might be a restricted article
        if article.text and len(article.text) < 100:
            print(f"Article content too short, might be paywalled: {url}")
        
        return {
            'title': article.title,
            'content': article.text,
            'author': article.authors[0] if article.authors else None,
            'published_date': article.publish_date
        }
    except Exception as e:
        print(f"Error extracting article from {url}: {e}")
        return None

def get_random_user_agent():
    """Get a random user agent to avoid being blocked"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
    ]
    return random.choice(user_agents)

def scrape_rss_feed(session, feed_url, source_name):
    """Scrape news from an RSS feed"""
    print(f"Fetching RSS feed from {feed_url} for {source_name}...")
    
    try:
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            print(f"No entries found in RSS feed for {source_name}")
            return
            
        print(f"{source_name}: Found {len(feed.entries)} potential articles in RSS feed.")
        
        articles = []
        for entry in feed.entries[:15]:  # Limit to 15 articles per source
            article_url = entry.link
            
            # Check if article already exists in DB
            existing = session.query(Article).filter_by(url=article_url).first()
            if existing:
                print(f"{source_name}: Skipping existing article: {article_url}")
                continue
            
            # Try to get content from RSS first
            content = ""
            if hasattr(entry, 'content'):
                for content_item in entry.content:
                    content += content_item.value
            elif hasattr(entry, 'summary'):
                content = entry.summary
                
            # If content from RSS is very short, try to extract the full article
            if len(content) < 200:
                article_data = extract_article(article_url)
                if article_data and article_data.get('content'):
                    # Use data from article extraction
                    title = article_data['title']
                    content = article_data['content']
                    author = article_data['author']
                    published_date = article_data['published_date']
                else:
                    # Use data from RSS feed
                    title = entry.title
                    author = entry.get('author', None)
                    content = clean_text(content)
                    published_date = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
            else:
                # Use data from RSS feed directly
                title = entry.title
                author = entry.get('author', None)
                content = clean_text(content)
                published_date = datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.now()
                
            # Skip if content is too short (likely paywalled or restricted)
            if len(content) < 100:
                print(f"{source_name}: Content too short, skipping: {article_url}")
                continue
                
            new_article = Article(
                title=title,
                url=article_url,
                source=source_name,
                author=author,
                content=content,
                published_date=published_date
            )
            
            session.add(new_article)
            articles.append(new_article)
            print(f"{source_name}: Added article: {title}")
            time.sleep(1)  # Be respectful
        
        session.commit()
        print(f"Scraped {len(articles)} new articles from {source_name}")
    except Exception as e:
        print(f"Error scraping {source_name} RSS feed: {e}")
        session.rollback()

def scrape_seattle_pi_rss(session):
    """Scrape Seattle PI RSS feed"""
    feed_url = "https://www.seattlepi.com/rss/feed/Seattle-News-145.php"
    scrape_rss_feed(session, feed_url, "Seattle PI")

def scrape_komo_rss(session):
    """Scrape KOMO News RSS feed"""
    feed_url = "https://komonews.com/feed/rss2/news/local"
    scrape_rss_feed(session, feed_url, "KOMO News")

def scrape_my_northwest_rss(session):
    """Scrape MyNorthwest RSS feed"""
    feed_url = "https://mynorthwest.com/feed/"
    scrape_rss_feed(session, feed_url, "MyNorthwest")

def scrape_king5_rss(session):
    """Scrape KING5 News RSS feed"""
    feed_url = "https://www.king5.com/feeds/syndication/rss/news/local"
    scrape_rss_feed(session, feed_url, "KING5 News")

def scrape_seattle_medium_rss(session):
    """Scrape The Seattle Medium RSS feed"""
    feed_url = "https://seattlemedium.com/category/news/feed/"
    scrape_rss_feed(session, feed_url, "Seattle Medium")

def scrape_the_stranger_rss(session):
    """Scrape The Stranger RSS feed"""
    feed_url = "https://www.thestranger.com/syndication/rss-feed-with-images"
    scrape_rss_feed(session, feed_url, "The Stranger")

def create_sample_articles(session):
    """Create sample articles if no articles were scraped"""
    count = session.query(Article).count()
    if count > 0:
        print(f"Database already has {count} articles, skipping sample creation.")
        return
        
    print("Creating sample articles for testing purposes...")
    
    # Sample article 1
    article1 = Article(
        title="New Light Rail Extension Opens in Seattle",
        url="https://example.com/seattle-light-rail-extension",
        source="Sample News",
        author="Jane Doe",
        content="""The Seattle Light Rail system expanded today with a new extension connecting downtown to the northern suburbs. 
        The $3.2 billion project includes three new stations and is expected to serve an additional 50,000 riders daily.
        "This is a major milestone for our city's transportation infrastructure," said Mayor Johnson at the ribbon-cutting ceremony.
        The extension is part of the Sound Transit 3 plan approved by voters in 2016. Commuters can now travel from Northgate to 
        Sea-Tac Airport in approximately 45 minutes, bypassing the region's notorious traffic congestion.
        Local businesses near the new stations are already reporting increased foot traffic. "We've seen at least 30% more customers 
        since the soft opening last week," said Maria Chen, owner of Emerald Café near the Roosevelt station.""",
        published_date=datetime.now()
    )
    
    # Sample article 2
    article2 = Article(
        title="Local Tech Company Announces 500 New Jobs",
        url="https://example.com/seattle-tech-jobs",
        source="Sample News",
        author="John Smith",
        content="""Seattle-based software company Cascadia Tech announced plans to hire 500 new employees over the next year.
        The expansion comes after securing $50 million in Series C funding led by Pacific Northwest Ventures.
        "We're committed to growing our presence in the Seattle area," said CEO Sarah Williams. "The talent pool here is exceptional."
        The company specializes in artificial intelligence solutions for healthcare and will be primarily hiring software engineers, 
        data scientists, and product managers. They plan to lease an additional 60,000 square feet of office space in the South Lake Union area.
        Starting salaries for the new positions will range from $95,000 to $160,000, plus benefits and equity packages.""",
        published_date=datetime.now()
    )
    
    # Sample article 3
    article3 = Article(
        title="Storm Causes Widespread Power Outages Across Seattle",
        url="https://example.com/seattle-storm-outages",
        source="Sample News",
        author="Emma Wilson",
        content="""A powerful windstorm swept through the Seattle area last night, leaving approximately 120,000 residents without power.
        Wind gusts reached up to 60 mph, downing power lines and trees across the city. Seattle City Light crews have been working through the night 
        to restore service, but officials warn some areas may remain without electricity for up to 48 hours.
        "This was one of the most significant storm events we've seen this year," said Tom Miller, emergency management director.
        Particularly hard-hit neighborhoods include Ballard, Queen Anne, and areas of North Seattle. Several schools have announced closures for Monday,
        and residents are advised to check the Seattle Public Schools website for updates.
        The National Weather Service predicts calmer conditions for the remainder of the week, which should aid recovery efforts.""",
        published_date=datetime.now()
    )
    
    # Sample article 4
    article4 = Article(
        title="New Affordable Housing Complex Opens in Capitol Hill",
        url="https://example.com/seattle-affordable-housing",
        source="Seattle Daily",
        author="Robert Johnson",
        content="""A new affordable housing complex with 95 units opened today in Seattle's Capitol Hill neighborhood. The Cascade Commons development 
        will provide homes for low and middle-income residents in one of the city's most expensive areas.
        The project was developed through a partnership between the city and non-profit housing provider Emerald Housing Alliance, with funding from 
        the 2016 Housing Levy and state tax credits.
        "In our current housing crisis, every new affordable unit matters," said Councilmember Lisa Rodriguez. "This project demonstrates what we can accomplish 
        through public-private partnerships."
        Rents will range from $750 for studios to $1,650 for three-bedroom units, significantly below market rate for the neighborhood. Twenty units are 
        specifically reserved for formerly homeless individuals, and support services will be provided on-site.
        "I never thought I'd be able to live in this neighborhood," said new resident Marcus Thompson. "This changes everything for me and my daughter."
        Applications for the remaining available units are being accepted through the city's housing portal.""",
        published_date=datetime.now()
    )
    
    # Sample article 5 
    article5 = Article(
        title="Downtown Seattle Farmers Market Expands Days of Operation",
        url="https://example.com/farmers-market-expansion",
        source="Seattle Daily",
        author="Sandra Lee",
        content="""The popular Pike Place Farmers Market announced today it will expand to operating seven days a week year-round, up from its previous 
        five-day schedule during winter months.
        The decision comes after a record-breaking summer season that saw over 15 million visitors and renewed interest in supporting local food producers.
        "Our vendors have been asking for this for years," said market director James Peterson. "The consistent foot traffic we've seen recently makes 
        this expansion viable for even our smallest farmers."
        The expanded schedule will begin next month and is expected to create approximately 200 new jobs across the market's various vendors and 
        support services.
        Local restaurants have also welcomed the news. "Having access to fresh, local produce every day of the week will allow us to be more creative 
        with our seasonal menus," said chef Elena Rodriguez of Emerald City Bistro.
        Market officials also announced plans for new evening events on Thursdays during summer months, including live music and cooking demonstrations.""",
        published_date=datetime.now()
    )
    
    # Sample article 6
    article6 = Article(
        title="City Council Approves New Climate Action Plan",
        url="https://example.com/seattle-climate-plan",
        source="Northwest Report",
        author="Michael Chen",
        content="""Seattle's City Council unanimously approved an ambitious new climate action plan yesterday that aims to achieve carbon neutrality by 2040.
        The comprehensive plan includes phasing out natural gas in new construction, expanding the city's electric vehicle infrastructure, and increasing 
        investment in renewable energy.
        "Seattle has always been a leader in environmental policy, but this plan takes our commitment to a new level," said Mayor Johnson.
        A key component of the plan is a $500 million green bond initiative to fund climate resilience projects throughout the city, including shoreline 
        restoration and green infrastructure to manage increasing stormwater from more frequent heavy rain events.
        The plan also creates a new Office of Climate Justice to ensure environmental policies benefit all communities equally, especially those historically 
        affected by pollution and environmental hazards.
        Public reaction has been largely positive, though some business groups have expressed concerns about implementation costs. The city plans to begin 
        rolling out the first initiatives as early as next month.""",
        published_date=datetime.now()
    )
    
    # Sample article 7
    article7 = Article(
        title="Seattle Public Schools Announces New Superintendent",
        url="https://example.com/sps-superintendent",
        source="Northwest Report",
        author="Jennifer Taylor",
        content="""After a six-month nationwide search, the Seattle School Board has selected Dr. Marcus Washington as the next superintendent of Seattle Public Schools.
        Dr. Washington, currently the deputy superintendent of Atlanta Public Schools, will take over the role in July, replacing interim superintendent Dr. Janet Miller.
        "Dr. Washington's track record of improving student outcomes while advancing equity made him the unanimous choice," said School Board President David Chen.
        Washington brings 20 years of education experience, including successful efforts in Atlanta to close achievement gaps and expand early childhood education. 
        He holds a doctorate in education leadership from Harvard University and previously taught middle school mathematics.
        In his first statement after the appointment, Washington identified addressing pandemic learning loss and teacher retention as his top priorities.
        "I'm honored to join this community and look forward to working with students, families, educators, and community partners to build on Seattle's 
        commitment to excellent, equitable education," Washington said.
        The three-year contract includes a base salary of $315,000 and performance incentives tied to student achievement metrics.""",
        published_date=datetime.now()
    )
    
    session.add_all([article1, article2, article3, article4, article5, article6, article7])
    session.commit()
    print("Created 7 sample articles for testing")

def run_scraper():
    session = setup_db()
    print("Starting scraper...")
    
    # Try scraping from multiple RSS feeds
    scrape_seattle_pi_rss(session)
    scrape_komo_rss(session)
    scrape_my_northwest_rss(session)
    scrape_king5_rss(session)
    scrape_seattle_medium_rss(session)
    scrape_the_stranger_rss(session)
    
    # Create sample articles if no real articles were successfully scraped
    article_count = session.query(Article).count()
    if article_count == 0:
        create_sample_articles(session)
    
    session.close()
    print("Scraping completed.")

if __name__ == "__main__":
    run_scraper()