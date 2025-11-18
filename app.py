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
                    model="claude-sonnet-4-20250514",
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
    
    # Custom CSS styling - SkyeStaq Brand Guidelines
    st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Montserrat+Alternates:wght@600&family=Manrope:wght@600&display=swap" rel="stylesheet">

    <style>
    /* ==================== CSS Variables - Brand Colors ==================== */
    :root {
        --summit-slate: #333447;
        --glen-fire: #CC6651;
        --highland-sand: #D8C3A5;
        --white: #ffffff;
        --light-bg: #f9f8f6;
        --light-gray: #e8e6e2;
    }

    /* ==================== Typography - Brand Guidelines ==================== */
    /* H1: Main headers - Montserrat Alternates Semibold 600 */
    h1, .stTitle {
        font-family: 'Montserrat Alternates', sans-serif !important;
        font-weight: 600 !important;
        font-size: 2.67rem !important;
        letter-spacing: -0.5px !important;
        color: var(--glen-fire) !important;
    }

    /* H2-H6: Section headers - Manrope Semibold 600 */
    h2, h3, h4, h5, h6, .stHeader {
        font-family: 'Manrope', sans-serif !important;
        font-weight: 600 !important;
        color: var(--glen-fire) !important;
    }

    h2 {
        font-size: 2rem !important;
        letter-spacing: -0.5px !important;
    }

    /* Body text - Arial/Helvetica with enhanced readability */
    body, .stMarkdown, p, div, span, label {
        font-family: Arial, Helvetica, sans-serif !important;
        font-size: 1.125rem !important;
        line-height: 1.7 !important;
        color: var(--summit-slate) !important;
    }

    /* ==================== Main App Layout ==================== */
    .stApp {
        background-color: var(--highland-sand);
    }

    /* Main content area with proper spacing */
    .main .block-container {
        padding-top: 3rem;
        padding-bottom: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
        background-color: var(--highland-sand);
    }

    /* Header/Title area - Summit Slate background */
    header[data-testid="stHeader"] {
        background-color: var(--summit-slate) !important;
    }

    /* Top toolbar area */
    [data-testid="stToolbar"] {
        background-color: var(--summit-slate) !important;
    }

    /* Main title section background */
    .main .block-container > div:first-child {
        background-color: var(--summit-slate);
        margin: -3rem -2rem 1rem -2rem;
        padding: 2rem 2rem 1.5rem 2rem;
        border-radius: 0 0 16px 16px;
    }

    /* Subtitle/italics in title section - keep white on dark background */
    .main .block-container > div:first-child em,
    .main .block-container > div:first-child .stMarkdown em {
        color: var(--highland-sand) !important;
    }

    /* Reduce spacing after divider following title */
    .main .block-container > div:first-child hr {
        margin-bottom: 0.5rem !important;
    }

    /* ==================== Sidebar Styling ==================== */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: var(--summit-slate);
        padding: 2rem 1rem;
        width: 400px !important;
        min-width: 400px !important;
    }

    /* Sidebar headings - reduced sizes for legibility */
    [data-testid="stSidebar"] h2 {
        color: var(--glen-fire) !important;
        font-size: 1.5rem !important;
        letter-spacing: 0px !important;
        margin-bottom: 0.5rem !important;
        margin-top: 0.5rem !important;
    }

    [data-testid="stSidebar"] h3 {
        color: var(--glen-fire) !important;
        font-size: 1.25rem !important;
        letter-spacing: 0px !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Sidebar text and labels - keep white text in sidebar */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown {
        font-size: 0.95rem !important;
        line-height: 1.5 !important;
        color: var(--white) !important;
    }

    /* Sidebar captions - keep light color */
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.85rem !important;
        color: var(--highland-sand) !important;
    }

    /* Sidebar logo - 50% width, centered */
    [data-testid="stSidebar"] img {
        width: 50% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        display: block !important;
        margin-bottom: 0.5rem !important;
    }

    /* Sidebar dividers - tighter spacing */
    [data-testid="stSidebar"] hr {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Sidebar status messages - tighter spacing */
    [data-testid="stSidebar"] .stSuccess,
    [data-testid="stSidebar"] .stInfo,
    [data-testid="stSidebar"] .stWarning,
    [data-testid="stSidebar"] .stError {
        margin-bottom: 0.25rem !important;
        padding: 0.5rem !important;
    }

    /* ==================== Input Elements ==================== */
    /* Text inputs with proper spacing */
    .stTextInput > div > div > input {
        background-color: var(--white);
        color: var(--summit-slate);
        border: 2px solid var(--light-gray);
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 1.125rem;
        transition: all 0.3s ease;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--glen-fire);
        box-shadow: 0 0 0 3px rgba(204, 102, 81, 0.1);
    }

    /* Select box styling */
    .stSelectbox > div > div {
        background-color: var(--white);
        border-radius: 8px;
    }

    .stSelectbox > div > div > div {
        color: var(--summit-slate);
        padding: 0.75rem 1rem;
    }

    /* ==================== Buttons - Brand Styled CTAs ==================== */
    /* Primary button - Glen Fire */
    .stButton > button {
        background-color: var(--glen-fire);
        color: var(--white);
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.125rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(204, 102, 81, 0.2);
    }

    .stButton > button:hover {
        background-color: #d47561;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(204, 102, 81, 0.3);
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: var(--glen-fire);
        color: var(--white);
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(204, 102, 81, 0.2);
    }

    .stDownloadButton > button:hover {
        background-color: #d47561;
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(204, 102, 81, 0.3);
    }

    /* ==================== Cards and Panels ==================== */
    /* Content cards with brand-specified styling */
    [data-testid="stExpander"],
    [data-testid="stAlert"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(51, 52, 71, 0.1);
        border: 1px solid rgba(216, 195, 165, 0.1);
    }

    /* Expandable sections */
    .streamlit-expanderHeader {
        background-color: rgba(204, 102, 81, 0.1);
        color: var(--glen-fire) !important;
        border-radius: 8px;
        padding: 1rem;
        font-weight: 600;
    }

    .streamlit-expanderHeader:hover {
        background-color: rgba(204, 102, 81, 0.2);
    }

    /* ==================== Status Messages ==================== */
    /* Success/Info/Warning/Error with proper brand styling */
    .stSuccess {
        background-color: rgba(204, 102, 81, 0.1);
        border-left: 4px solid var(--glen-fire);
        border-radius: 8px;
        padding: 1rem;
    }

    .stInfo {
        background-color: rgba(216, 195, 165, 0.1);
        border-left: 4px solid var(--highland-sand);
        border-radius: 8px;
        padding: 1rem;
    }

    .stWarning {
        background-color: rgba(255, 183, 77, 0.1);
        border-left: 4px solid #ffb74d;
        border-radius: 8px;
        padding: 1rem;
    }

    .stError {
        background-color: rgba(239, 83, 80, 0.1);
        border-left: 4px solid #ef5350;
        border-radius: 8px;
        padding: 1rem;
    }

    /* ==================== Progress Indicators ==================== */
    .stProgress > div > div > div > div {
        background-color: var(--glen-fire);
    }

    .stSpinner > div {
        border-top-color: var(--glen-fire) !important;
    }

    /* ==================== Dividers and Spacing ==================== */
    hr {
        border: none;
        border-top: 2px solid var(--light-gray);
        margin: 2rem 0;
        opacity: 0.2;
    }

    /* ==================== Code and Pre-formatted Text ==================== */
    .stCode, code, pre {
        background-color: rgba(51, 52, 71, 0.8);
        color: var(--highland-sand);
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid var(--light-gray);
    }

    /* ==================== Captions and Helper Text ==================== */
    .stCaption, caption, small {
        color: var(--highland-sand) !important;
        font-size: 0.9rem !important;
        line-height: 1.5 !important;
    }

    /* ==================== Links ==================== */
    a {
        color: var(--glen-fire) !important;
        text-decoration: none;
        transition: all 0.3s ease;
    }

    a:hover {
        color: var(--highland-sand) !important;
        text-decoration: underline;
    }

    /* ==================== Metric Cards ==================== */
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(204, 102, 81, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(51, 52, 71, 0.1);
    }

    /* ==================== Animations ==================== */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .main .block-container > div {
        animation: fadeIn 0.8s ease;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.title("Client Research Agent")
    st.markdown("*AI-powered client intelligence for consulting meetings*")
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        # Logo
        st.image("logo.png", use_container_width=True)
        st.markdown("---")

        st.markdown("## LLM Configuration")

        # API Key Input
        st.markdown("### 🔑 Anthropic API Key")
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-api03-...",
            help="Enter your Anthropic API key for AI-powered analysis. Leave blank to use basic analysis.",
            label_visibility="collapsed"
        )

        # API Key Status
        if api_key:
            if api_key.startswith('sk-ant-'):
                st.success("API Key Format Valid")
                st.caption("AI analysis will be enabled")
            else:
                st.error("Invalid API Key Format")
                st.caption("Should start with 'sk-ant-'")
        elif os.getenv('ANTHROPIC_API_KEY'):
            st.info("Using Environment Variable")
            st.caption("AI analysis enabled")
        else:
            st.warning("No API Key Provided")
            st.caption("Using fallback analysis")

        st.markdown("---")
        st.markdown("### Security Note")
        st.caption("API keys are not stored or logged. They're only used for this session.")

        st.markdown("---")
        st.markdown("### Get API Key")
        st.markdown("[Get Free API Key](https://console.anthropic.com/)")
        st.caption("Anthropic offers free tier with generous limits")

        st.markdown("---")
        st.markdown("### Instructions")
        st.markdown("1. Enter API key (optional)")
        st.markdown("2. Fill company details")
        st.markdown("3. Generate research")
        st.markdown("4. Download briefing")
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Meeting Details")
        
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
        st.header("Research Status")
        
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
        st.header(f"Researching {company_name}{location_text}")
        
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