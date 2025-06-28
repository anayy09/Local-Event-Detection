# Local Event Detection and Summarization

An intelligent news aggregation and analysis system that automatically monitors local Seattle/Washington news sources, detects emerging events through clustering, and provides comprehensive summaries and insights. The system combines advanced NLP techniques with web scraping to deliver real-time event detection and analysis.

## 🚀 Features

### Core Functionality

- **Multi-Source News Scraping**: Automated collection from 10+ local Seattle news sources via RSS feeds
- **Intelligent Content Filtering**: Local relevance detection for Seattle/Washington area news
- **Advanced NLP Processing**: Text preprocessing with spaCy including lemmatization and stop word removal
- **Named Entity Recognition**: Extraction and tracking of people, organizations, and locations mentioned in articles
- **Content Clustering**: ML-based article clustering using TF-IDF and sentence transformers
- **Topic Modeling**: Automatic topic extraction using BERTopic for cluster labeling
- **AI-Powered Summarization**: Cluster summaries generated using Facebook's BART transformer model

### Web Interface

- **Interactive Dashboard**: Clean, responsive web interface built with Flask and Bootstrap
- **Event Exploration**: Detailed cluster views with articles, entities, and summaries
- **Analytics Dashboard**: Real-time statistics and visualizations
- **Data Visualizations**: Charts showing entity frequency, cluster distribution, and source analytics

### Automation

- **Scheduled Pipeline**: Automatic execution every 6 hours using APScheduler
- **Background Processing**: Non-blocking pipeline execution during web app operation
- **Sample Data Generation**: Fallback sample articles for testing and demonstration

## 🛠️ Tech Stack

### Backend & Core Processing
- **Python 3.9.5+**: Core programming language
- **Flask 2.3.2**: Web framework for the dashboard interface
- **SQLAlchemy 1.4+**: Database ORM with SQLite backend
- **APScheduler 3.9.1**: Background task scheduling

### Machine Learning & NLP
- **spaCy 3.5.2**: Natural language processing and named entity recognition
- **scikit-learn 1.2.2**: Machine learning algorithms for clustering and vectorization
- **sentence-transformers 2.2.2**: Semantic text embeddings for content similarity
- **BERTopic 0.14.1**: Advanced topic modeling using transformer models
- **transformers 4.21.3**: Hugging Face transformers for text summarization
- **PyTorch 1.13.1**: Deep learning framework backend

### Data Processing & Analysis
- **NLTK 3.8.1**: Text preprocessing and tokenization
- **NumPy 1.26.4**: Numerical computing and array operations
- **Pandas**: Data manipulation (via dependencies)
- **matplotlib 3.7.1**: Data visualization and chart generation
- **seaborn 0.12.2**: Statistical data visualization

### Web Scraping & Data Collection
- **requests 2.28.2**: HTTP library for web requests
- **BeautifulSoup 4.11.1**: HTML parsing and content extraction
- **newspaper3k 0.2.8**: Article extraction and processing
- **feedparser 6.0.11**: RSS feed parsing and processing
- **lxml_html_clean 0.4.2**: HTML cleaning and sanitization

### News Sources Monitored
- Seattle PI
- KOMO News
- MyNorthwest
- KING5 News
- Seattle Medium
- The Stranger
- Crosscut
- South Seattle Emerald
- Capitol Hill Seattle Blog
- Google News (Seattle-focused)

## 📋 Installation

### Prerequisites

- Python 3.9.5+
- Windows 10/11
- Git

### Setup

1. Clone the repository:

   ```powershell
   git clone https://github.com/anayy09/Local-Event-Detection.git
   cd Local-Event-Detection
   ```

2. Create and activate a virtual environment:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install required packages:

   ```powershell
   pip install -r requirements.txt
   ```

4. Download required NLTK data and spaCy model:

   ```powershell
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
   python -m spacy download en_core_web_sm
   ```

## 🚀 Usage

### Quick Start

Ensure your virtual environment is activated (`.\venv\Scripts\Activate.ps1`).

1. **Setup the database:**

   ```powershell
   python .\database\setup_db.py
   ```

2. **Run the complete pipeline:**

   ```powershell
   # Scrape articles from news sources
   python .\scraper\scrape.py
   
   # Process the articles
   python .\processing\preprocess.py
   python .\processing\ner.py
   python .\processing\cluster.py
   python .\processing\topic_model.py
   
   # Generate summaries and visualizations
   python .\summarization\summarize.py
   python .\analysis\visualize.py
   ```

3. **Launch the web application:**

   ```powershell
   python .\webapp\app.py
   ```

   Open your browser and navigate to: `http://127.0.0.1:5000`

### Pipeline Components

| Component | Purpose | Output |
|-----------|---------|---------|
| `scraper/scrape.py` | Collect articles from RSS feeds | Raw articles in database |
| `processing/preprocess.py` | Clean and tokenize text | Processed content |
| `processing/ner.py` | Extract named entities | Entities with counts |
| `processing/cluster.py` | Group similar articles | Article clusters |
| `processing/topic_model.py` | Generate topic labels | Topic descriptions |
| `summarization/summarize.py` | Create cluster summaries | AI-generated summaries |
| `analysis/visualize.py` | Generate charts | PNG visualizations |

### Web Interface Features

- **Home Dashboard**: Overview of all detected event clusters
- **Cluster Details**: Deep dive into specific events with articles and entities
- **Analytics**: System statistics and data visualizations
- **About Page**: Project information and methodology

## ⚙️ Automated Operation

The web application includes a built-in scheduler that automatically runs the complete data pipeline every 6 hours. This ensures fresh content and up-to-date event detection without manual intervention.

**Pipeline Schedule:**

- Runs every 6 hours starting when the web app launches
- Processes: Scraping → NLP → Clustering → Summarization → Visualization
- Background execution allows continuous web app operation

## 🗂️ Project Structure

```text
Local-Event-Detection/
├── database/           # Database models and setup
│   ├── models.py      # SQLAlchemy model definitions
│   └── setup_db.py    # Database initialization
├── scraper/           # News collection module
│   └── scrape.py      # RSS feed scraping logic
├── processing/        # NLP and ML pipeline
│   ├── preprocess.py  # Text cleaning and preprocessing
│   ├── ner.py         # Named entity recognition
│   ├── cluster.py     # Article clustering algorithms
│   └── topic_model.py # Topic modeling with BERTopic
├── summarization/     # Text summarization
│   └── summarize.py   # BART-based summarization
├── analysis/          # Data visualization
│   └── visualize.py   # Chart generation
├── webapp/           # Flask web application
│   ├── app.py        # Main Flask application
│   ├── templates/    # HTML templates
│   └── static/       # CSS, images, charts
├── event_data.db     # SQLite database (created at runtime)
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## 🔧 Configuration & Customization

### Adding New News Sources

To add new RSS feeds, modify `scraper/scrape.py`:

```python
def scrape_new_source_rss(session):
    feed_url = "https://example.com/rss"
    return scrape_rss_feed(session, feed_url, "Source Name", local_only=True)
```

### Adjusting Pipeline Parameters

- **Clustering**: Modify `min_cluster_size` in `processing/cluster.py`
- **Scheduling**: Change interval in `webapp/app.py` scheduler setup
- **Summarization**: Adjust `max_length` and `min_length` in `summarization/summarize.py`

### Database Schema

The system uses SQLite with the following main tables:
- `articles`: Stores scraped news articles
- `entities`: Named entities extracted from articles
- `clusters`: Article cluster information
- `summaries`: AI-generated cluster summaries

## 🔍 Key Algorithms & Methodologies

### Content Clustering
- **TF-IDF Vectorization**: Traditional bag-of-words approach for baseline clustering
- **Sentence Transformers**: Modern semantic embeddings using 'all-MiniLM-L6-v2'
- **K-Means Clustering**: Primary clustering algorithm with automatic k selection

### Text Summarization
- **BART Model**: Facebook's BART-large-CNN for abstractive summarization
- **Entity Integration**: Top entities automatically included in summaries
- **Content Aggregation**: Multiple articles combined for comprehensive cluster summaries

### Local Relevance Detection
- **Geographic Filtering**: 20+ Seattle/Washington-specific terms
- **Title Prioritization**: Stronger weighting for title mentions
- **Content Scanning**: Analysis of article opening paragraphs

## 🚨 Troubleshooting

### Common Issues

**No articles scraped:**
- Check internet connection
- Verify RSS feed URLs are accessible
- Some sources may have rate limiting

**Clustering fails:**
- Ensure minimum number of articles (2+) are available
- Check that articles have processed content

**Web app won't start:**
- Verify all dependencies are installed
- Check that port 5000 is available
- Ensure virtual environment is activated

**Missing visualizations:**
- Run `python .\analysis\visualize.py` manually
- Check write permissions in `webapp/static/` directory

## 📈 Performance & Scalability

- **Processing Time**: ~2-5 minutes for 50 articles (full pipeline)
- **Memory Usage**: ~500MB during ML processing
- **Storage**: SQLite database grows ~1MB per 100 articles
- **Concurrency**: Single-threaded by design for reliability

## 📄 License

This project is licensed under the MIT License - see the `LICENSE` file for details.