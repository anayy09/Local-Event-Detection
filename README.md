# Local Event Detection and Summarization

This project automatically scrapes local news websites, extracts and clusters event information, and generates summaries for each detected event cluster.

## Features

- Automated news scraping from multiple local news sources
- Advanced NLP processing with named entity recognition
- Article clustering based on content similarity
- Topic modeling using BERTopic
- Automatic summarization of each event cluster
- Web interface for exploring events and summaries
- Analytics dashboard with visualizations

## Installation

### Prerequisites

- Python 3.9.5+
- Windows 10/11

### Setup

1.  Clone the repository:
    ````powershell
    git clone https://github.com/yourusername/local-event-detection.git
    cd local-event-detection
    ````
2.  Create and activate a virtual environment:
    ````powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ````
3.  Install required packages:
    ````powershell
    pip install -r requirements.txt
    ````
4.  Download NLTK data:
    ````powershell
    python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
    ````

## Usage

Make sure your virtual environment is activated (`.\venv\Scripts\Activate.ps1`).

1.  **Setup the database:**
    ````powershell
    python .\database\setup_db.py
    ````
2.  **Run the scraper to collect news articles:**
    ````powershell
    python .\scraper\scrape.py
    ````
3.  **Process the articles:**
    ````powershell
    python .\processing\preprocess.py
    python .\processing\ner.py
    python .\processing\cluster.py
    python .\processing\topic_model.py
    ````
4.  **Generate summaries:**
    ````powershell
    python .\summarization\summarize.py
    ````
5.  **Create visualizations:**
    ````powershell
    python .\analysis\visualize.py
    ````
6.  **Run the web application:**
    ````powershell
    python .\webapp\app.py
    ````
    Open your browser and navigate to: `http://127.0.0.1:5000`

## Scheduled Operation

The web application includes a scheduler that automatically runs the full pipeline (scraping, processing, summarization, analysis) every 6 hours. The scheduler starts automatically when you run the web application (`python .\webapp\app.py`).

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.