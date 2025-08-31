#!/usr/bin/env python3
"""
Client Research Prep Agent
Gathers recent company intel for pre-meeting preparation
"""

import anthropic
import os
import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from googlesearch import search
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ClientResearchAgent:
    def __init__(self):
        self.anthropic_client = None
        if os.getenv('ANTHROPIC_API_KEY'):
            self.anthropic_client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
    
    def search_company_info(self, company_name: str) -> Dict[str, Any]:
        """Search for company information using web search"""
        searches = {
            'recent_news': f"{company_name} news 2024 recent developments",
            'financial_updates': f"{company_name} financial results earnings revenue growth 2024",
            'ai_trends': f"{company_name} AI artificial intelligence technology adoption digital transformation"
        }
        
        results = {}
        for category, query in searches.items():
            print(f"🔍 Searching for {category.replace('_', ' ')}...")
            try:
                results[category] = self.perform_google_search(query)
            except Exception as e:
                print(f"⚠️  Search failed for {category}: {e}")
                results[category] = self.simulate_search_results(query)
        
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
            message = self.anthropic_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"⚠️  AI analysis failed: {e}")
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
    
    def save_briefing(self, briefing: str, company_name: str) -> str:
        """Save briefing to markdown file"""
        filename = f"{company_name.lower().replace(' ', '_')}_briefing_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(briefing)
        
        return filename

def main():
    agent = ClientResearchAgent()
    
    print("🤖 Client Research Prep Agent")
    print("=" * 40)
    
    # Get input from user
    company_name = input("Company name: ").strip()
    meeting_type = input("Meeting type (discovery/follow-up/proposal): ").strip()
    
    if not company_name:
        print("❌ Company name is required")
        return
    
    print(f"\n🔍 Researching {company_name} for {meeting_type} meeting...")
    
    # Search for company information
    search_results = agent.search_company_info(company_name)
    
    # Analyze findings
    print("🧠 Analyzing findings...")
    analysis = agent.analyze_findings(company_name, meeting_type, search_results)
    
    # Generate briefing
    print("📝 Generating briefing...")
    briefing = agent.generate_briefing(company_name, meeting_type, analysis)
    
    # Save to file
    filename = agent.save_briefing(briefing, company_name)
    
    print(f"\n✅ Research complete!")
    print(f"📄 Briefing saved as: {filename}")
    print(f"\n{briefing}")

if __name__ == "__main__":
    main()