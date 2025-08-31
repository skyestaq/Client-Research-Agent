# Client Research Agent

AI-powered client intelligence tool for consulting meetings. Features real-time web search, AI analysis, and professional briefing generation.

## Features

- **Real Web Search**: Searches for recent company news, financial updates, and AI trends
- **Location Targeting**: City/State/Zip input to disambiguate companies
- **AI Analysis**: Uses Anthropic's Claude API to analyze findings and generate insights
- **Professional Briefings**: Creates structured markdown reports with key insights, pain points, and conversation starters
- **Web Interface**: Streamlit app with professional UI and download functionality
- **CLI Tool**: Command-line version for quick research

## Quick Start

### Web App (Recommended)
```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your Anthropic API key

# Run
streamlit run app.py
```
Open http://localhost:8501

### CLI Tool
```bash
python3 client_research_agent.py
```

## Usage

1. **Enter company details**: Name and location (optional)
2. **Select meeting type**: discovery/follow-up/proposal  
3. **Generate research**: Real-time web search with progress tracking
4. **Download briefing**: Professional markdown report with insights

## Output

Creates comprehensive briefings with:
- Key company insights
- Potential AI pain points to explore
- Strategic conversation starters
- Meeting preparation checklist
- Next steps recommendations

## Deployment

Deploy the web app to:
- **Streamlit Cloud** (free)
- **Railway** (`railway deploy`)  
- **Heroku** (`git push heroku main`)
- **Render** (connect GitHub repo)

Perfect for AI consultants preparing for client meetings!
