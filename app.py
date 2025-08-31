#!/usr/bin/env python3
"""
Client Research Agent - Streamlit Web App
Professional web interface for AI-powered client research
"""

import streamlit as st
import anthropic
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from googlesearch import search
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

class ClientResearchAgent:
    def __init__(self, api_key: str = None):
        self.anthropic_client = None
        # Try API key from parameter first, then environment variable
        key_to_use = api_key or os.getenv('ANTHROPIC_API_KEY')
        if key_to_use:
            try:
                self.anthropic_client = anthropic.Anthropic(api_key=key_to_use)
            except Exception as e:
                st.error(f"Invalid API key: {e}")
                self.anthropic_client = None
    
    def search_company_info(self, company_name: str, location: str = "") -> Dict[str, Any]:
        """Search for company information using web search"""
        location_query = f" {location}" if location.strip() else ""
        
        searches = {
            'recent_news': f"{company_name}{location_query} news 2024 recent developments",
            'financial_updates': f"{company_name}{location_query} financial results earnings revenue growth 2024",
            'ai_trends': f"{company_name}{location_query} AI artificial intelligence technology adoption digital transformation"
        }
        
        results = {}
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, (category, query) in enumerate(searches.items()):
            status_text.text(f"🔍 Searching for {category.replace('_', ' ')}...")
            progress_bar.progress((i + 1) / len(searches))
            
            try:
                results[category] = self.perform_google_search(query)
            except Exception as e:
                st.warning(f"Search failed for {category}: {e}")
                results[category] = self.simulate_search_results(query)
        
        status_text.text("✅ Search complete!")
        return results
    
    def perform_google_search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """Perform actual Google search using googlesearch-python"""
        search_results = []
        
        try:
            # Get search results
            urls = list(search(query, num_results=num_results, sleep_interval=1))
            
            for i, url in enumerate(urls):
                # For each URL, try to get title and snippet
                try:
                    response = requests.get(url, timeout=5, headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                    })
                    
                    # Extract title from HTML (basic extraction)
                    title = "Search Result"
                    if '<title>' in response.text:
                        start = response.text.find('<title>') + 7
                        end = response.text.find('</title>', start)
                        if end > start:
                            title = response.text[start:end].strip()
                    
                    search_results.append({
                        "title": title[:100] + "..." if len(title) > 100 else title,
                        "snippet": f"Search result {i+1} for: {query}",
                        "url": url,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
                except Exception as e:
                    # If we can't fetch the page, still include the URL
                    search_results.append({
                        "title": f"Search Result {i+1}",
                        "snippet": f"Found via search for: {query}",
                        "url": url,
                        "date": datetime.now().strftime("%Y-%m-%d")
                    })
        
        except Exception as e:
            print(f"Google search failed: {e}")
            return self.simulate_search_results(query)
        
        return search_results if search_results else self.simulate_search_results(query)
    
    def simulate_search_results(self, query: str) -> List[Dict[str, str]]:
        """Simulate search results - fallback when real search fails"""
        return [
            {
                "title": f"Sample result for: {query}",
                "snippet": "This would contain actual search result content from a real search API.",
                "url": "https://example.com",
                "date": "2024-08-31"
            }
        ]
    
    def analyze_findings(self, company_name: str, meeting_type: str, search_results: Dict[str, Any]) -> str:
        """Use AI to analyze search results and generate insights"""
        if not self.anthropic_client:
            return self.generate_fallback_analysis(company_name, meeting_type, search_results)
        
        prompt = f"""
        Analyze the following research about {company_name} for a {meeting_type} meeting with an AI consulting firm.

        Research Results:
        {json.dumps(search_results, indent=2)}

        Please provide:
        1. Key Company Insights (3-5 bullet points)
        2. Potential AI Pain Points to Explore (3-4 specific areas)
        3. Conversation Starters (3-4 strategic questions)

        Format the response as clear, actionable insights for a consulting meeting.
        """
        
        try:
            with st.spinner("🧠 Analyzing findings with AI..."):
                message = self.anthropic_client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
        except Exception as e:
            st.warning(f"AI analysis failed: {e}")
            return self.generate_fallback_analysis(company_name, meeting_type, search_results)
    
    def generate_fallback_analysis(self, company_name: str, meeting_type: str, search_results: Dict[str, Any]) -> str:
        """Generate basic analysis without AI when API is unavailable"""
        return f"""
# Analysis for {company_name}

## Key Company Insights
- Research indicates recent activity in the market
- Company appears to be in growth/development phase
- Multiple news sources covering company developments

## Potential AI Pain Points to Explore
- Data management and analytics optimization
- Process automation opportunities
- Customer experience enhancement through AI
- Operational efficiency improvements

## Conversation Starters
- "What are your biggest operational challenges right now?"
- "How are you currently handling data analysis and insights?"
- "What manual processes are taking up most of your team's time?"
- "How do you see AI fitting into your industry's future?"

*Note: This analysis was generated without AI assistance. For deeper insights, configure ANTHROPIC_API_KEY.*
        """
    
    def generate_briefing(self, company_name: str, meeting_type: str, analysis: str) -> str:
        """Generate the final client briefing document"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        briefing = f"""# Client Research Briefing: {company_name}

**Meeting Type**: {meeting_type.title()}  
**Date Prepared**: {timestamp}  
**Prepared for**: AI Consulting Meeting

---

{analysis}

---

## Meeting Preparation Checklist
- [ ] Review company website and recent announcements
- [ ] Prepare questions about current tech stack
- [ ] Research key decision makers and attendees
- [ ] Bring relevant case studies from similar companies
- [ ] Prepare AI readiness assessment questions

## Next Steps
1. Schedule follow-up research if needed
2. Customize presentation materials
3. Prepare technical demonstrations
4. Set meeting objectives and success metrics

*Generated by Client Research Agent*
"""
        return briefing

# Streamlit Web Interface
def main():
    st.set_page_config(
        page_title="Client Research Agent",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS styling
    st.markdown("""
    <style>
    /* Main app background */
    .stApp {
        background-color: #333447;
    }
    
    /* Sidebar background */
    .css-1d391kg {
        background-color: #333447;
    }
    
    /* Header text styling */
    .stTitle, h1, h2, h3 {
        color: #D8C3A5 !important;
    }
    
    /* Main content area */
    .main .block-container {
        background-color: #333447;
    }
    
    /* Text inputs styling */
    .stTextInput > div > div > input {
        background-color: #CC6651;
        color: white;
        border: 1px solid #D8C3A5;
    }
    
    /* Select box styling */
    .stSelectbox > div > div > div {
        background-color: #CC6651;
        color: white;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #CC6651;
        color: white;
        border: 1px solid #D8C3A5;
    }
    
    .stButton > button:hover {
        background-color: #D8C3A5;
        color: #333447;
        border: 1px solid #CC6651;
    }
    
    /* Sidebar elements */
    .stSidebar .stTextInput > div > div > input {
        background-color: #CC6651;
        color: white;
        border: 1px solid #D8C3A5;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background-color: #CC6651;
    }
    
    /* Success/warning/error messages */
    .stSuccess, .stWarning, .stError, .stInfo {
        background-color: rgba(204, 102, 81, 0.1);
        border-left: 4px solid #CC6651;
    }
    
    /* Markdown content */
    .stMarkdown {
        color: white;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background-color: #CC6651;
        color: white;
        border: 1px solid #D8C3A5;
    }
    
    .stDownloadButton > button:hover {
        background-color: #D8C3A5;
        color: #333447;
    }
    
    /* Expandable sections */
    .streamlit-expanderHeader {
        background-color: #CC6651;
        color: white;
    }
    
    /* Code blocks */
    .stCode {
        background-color: #CC6651;
        color: white;
    }
    
    /* Metric cards */
    .css-1xarl3l {
        background-color: rgba(204, 102, 81, 0.1);
        border: 1px solid #CC6651;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("🤖 Client Research Agent")
    st.markdown("*AI-powered client intelligence for consulting meetings*")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Configuration")
        
        # API Key Input
        st.markdown("### 🔑 Anthropic API Key")
        api_key = st.text_input(
            "API Key (Optional)",
            type="password",
            placeholder="sk-ant-api03-...",
            help="Enter your Anthropic API key for AI-powered analysis. Leave blank to use basic analysis."
        )
        
        # API Key Status
        if api_key:
            if api_key.startswith('sk-ant-'):
                st.success("✅ API Key Format Valid")
                st.caption("AI analysis will be enabled")
            else:
                st.error("❌ Invalid API Key Format")
                st.caption("Should start with 'sk-ant-'")
        elif os.getenv('ANTHROPIC_API_KEY'):
            st.info("🔧 Using Environment Variable")
            st.caption("AI analysis enabled")
        else:
            st.warning("⚠️ No API Key Provided")
            st.caption("Using fallback analysis")
        
        st.markdown("---")
        st.markdown("### 🔒 Security Note")
        st.caption("API keys are not stored or logged. They're only used for this session.")
        
        st.markdown("---")
        st.markdown("### 🆓 Get API Key")
        st.markdown("[Get Free API Key](https://console.anthropic.com/)")
        st.caption("Anthropic offers free tier with generous limits")
        
        st.markdown("---")
        st.markdown("### 📖 Instructions")
        st.markdown("1. Enter API key (optional)")
        st.markdown("2. Fill company details")
        st.markdown("3. Generate research")
        st.markdown("4. Download briefing")
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Meeting Details")
        
        # Input form
        company_name = st.text_input(
            "Company Name",
            placeholder="e.g., Tesla, Microsoft, Acme Corp",
            help="Enter the name of the company you're researching"
        )
        
        location = st.text_input(
            "Location (Optional)",
            placeholder="e.g., Austin TX, New York NY, 10001",
            help="City, State or Zip Code to narrow search results"
        )
        
        meeting_type = st.selectbox(
            "Meeting Type",
            ["discovery", "follow-up", "proposal"],
            help="Select the type of meeting you're preparing for"
        )
        
        # Generate button
        generate_button = st.button(
            "🔍 Generate Research",
            type="primary",
            disabled=not company_name.strip()
        )
    
    with col2:
        st.header("📊 Research Status")
        
        # Status area
        if not company_name.strip():
            st.info("👆 Enter a company name to begin research")
        else:
            location_text = f" in {location}" if location.strip() else ""
            st.success(f"Ready to research: **{company_name}**{location_text}")
            st.info(f"Meeting type: **{meeting_type}**")
    
    # Generate research
    if generate_button and company_name.strip():
        st.markdown("---")
        location_text = f" in {location}" if location.strip() else ""
        st.header(f"🔍 Researching {company_name}{location_text}")
        
        # Initialize agent with API key from sidebar
        agent = ClientResearchAgent(api_key=api_key)
        
        # Perform research
        search_results = agent.search_company_info(company_name, location)
        
        # Analyze findings
        analysis = agent.analyze_findings(company_name, meeting_type, search_results)
        
        # Generate briefing
        briefing = agent.generate_briefing(company_name, meeting_type, analysis)
        
        # Display results
        st.markdown("---")
        st.header("📄 Generated Briefing")
        
        # Show briefing content
        st.markdown(briefing)
        
        # Download functionality
        st.markdown("---")
        st.header("💾 Download Options")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Create filename
            filename = f"{company_name.lower().replace(' ', '_')}_briefing_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
            
            # Download button
            st.download_button(
                label="📥 Download Briefing (Markdown)",
                data=briefing,
                file_name=filename,
                mime="text/markdown"
            )
        
        with col2:
            st.success("✅ Research Complete!")
            st.caption(f"Briefing ready for {meeting_type} meeting")
        
        # Show search results (expandable)
        with st.expander("🔍 View Raw Search Results"):
            st.json(search_results)

if __name__ == "__main__":
    main()