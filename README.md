# Client Research Agent

An AI-powered tool for gathering company intelligence before client meetings.

## Features

- **Real Web Search**: Searches for recent company news, financial updates, and AI trends
- **AI Analysis**: Uses Anthropic's Claude API to analyze findings and generate insights
- **Professional Briefings**: Creates structured markdown reports with key insights, pain points, and conversation starters
- **Automated Output**: Saves timestamped briefing files for easy reference

## Setup

1. **Create Virtual Environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up API Key** (Optional but recommended):
   ```bash
   cp .env.example .env
   # Edit .env and add your Anthropic API key
   ```

   Get your API key from: https://console.anthropic.com/

4. **Run the Script**:
   ```bash
   python3 client_research_agent.py
   ```

## Usage

1. Enter the company name when prompted
2. Specify the meeting type (discovery/follow-up/proposal)
3. The script will:
   - Search for recent company information
   - Analyze findings with AI (if API key is configured)
   - Generate a professional briefing
   - Save it as a markdown file

## Output

Creates a comprehensive briefing with:
- Key company insights
- Potential AI pain points to explore
- Strategic conversation starters
- Meeting preparation checklist
- Next steps recommendations

## Example

```bash
$ python3 client_research_agent.py
🤖 Client Research Prep Agent
========================================
Company name: Tesla
Meeting type: discovery

🔍 Researching Tesla for discovery meeting...
🔍 Searching for recent news...
🔍 Searching for financial updates...
🔍 Searching for ai trends...
🧠 Analyzing findings...
📝 Generating briefing...

✅ Research complete!
📄 Briefing saved as: tesla_briefing_20240831_1430.md
```

## Notes

- Works without API key (uses fallback analysis)
- Real-time web search results
- Respects search rate limits
- Professional output format
- Saves all briefings for reference

Perfect for AI consultants preparing for client meetings!