"""
Competitive Research Agent for PitchIQ
Automatically researches companies and competitors when pitch decks are uploaded.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-flash-latest')


class CompetitiveResearchAgent:
    """
    Agent that performs competitive intelligence research on companies
    using web search and AI synthesis.
    """
    
    def __init__(self):
        self.model = model
    
    async def research_company(self, company_name: str, industry: str) -> Dict:
        """
        Perform comprehensive research on a company.
        
        Args:
            company_name: Name of the company to research
            industry: Industry sector (for context)
            
        Returns:
            Dict containing research findings
        """
        print(f"[RESEARCH] Researching: {company_name} ({industry})")
        
        # Compile research tasks
        tasks = [
            self._get_company_overview(company_name, industry),
            self._find_competitors(company_name, industry),
            self._get_recent_news(company_name),
        ]
        
        # Run research in parallel
        overview, competitors, news = await asyncio.gather(*tasks)
        
        # Synthesize findings
        synthesis = await self._synthesize_research(
            company_name, overview, competitors, news
        )
        
        return {
            "company_name": company_name,
            "industry": industry,
            "overview": overview,
            "competitors": competitors,
            "recent_news": news,
            "synthesis": synthesis,
            "timestamp": self._get_timestamp()
        }
    
    async def _get_company_overview(self, company_name: str, industry: str) -> str:
        """Get company overview using Gemini's grounding (web search)."""
        prompt = f"""
        Provide a brief overview of {company_name}, a company in the {industry} industry.
        Focus on:
        1. What they do (product/service)
        2. When they were founded
        3. Key milestones or achievements
        4. Current stage (Seed, Series A/B/C, Public, etc.)
        5. Any known funding or revenue information
        
        Be concise (2-3 paragraphs max).
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error fetching overview: {str(e)}"
    
    async def _find_competitors(self, company_name: str, industry: str) -> List[Dict]:
        """Identify key competitors using Gemini."""
        prompt = f"""
        Identify the top 3-5 direct competitors of {company_name} in the {industry} space.
        
        For each competitor, provide:
        {{
            "name": "Company Name",
            "description": "What they do (1 sentence)",
            "strength": "Their key competitive advantage",
            "weakness": "A potential weakness or area where {company_name} could differentiate"
        }}
        
        Return ONLY a JSON array of competitors, nothing else.
        """
        
        try:
            generation_config = {"response_mime_type": "application/json"}
            response = self.model.generate_content(prompt, generation_config=generation_config)
            competitors = json.loads(response.text)
            
            # Ensure it's a list
            if isinstance(competitors, dict) and "competitors" in competitors:
                return competitors["competitors"]
            elif isinstance(competitors, list):
                return competitors
            else:
                return []
        except Exception as e:
            print(f"Error finding competitors: {e}")
            return []
    
    async def _get_recent_news(self, company_name: str) -> List[Dict]:
        """Get recent news about the company."""
        prompt = f"""
        Find the most important recent news (last 90 days) about {company_name}.
        Focus on:
        - Funding rounds
        - Product launches
        - Partnerships or acquisitions
        - Major milestones
        
        Return up to 5 news items in this JSON format:
        [
            {{
                "headline": "Brief headline",
                "summary": "1-2 sentence summary",
                "significance": "Why this matters"
            }}
        ]
        
        If no recent news is found, return an empty array [].
        Return ONLY valid JSON.
        """
        
        try:
            generation_config = {"response_mime_type": "application/json"}
            response = self.model.generate_content(prompt, generation_config=generation_config)
            news = json.loads(response.text)
            
            # Handle different response formats
            if isinstance(news, dict) and "news" in news:
                return news["news"]
            elif isinstance(news, list):
                return news
            else:
                return []
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    async def _synthesize_research(
        self, 
        company_name: str, 
        overview: str, 
        competitors: List[Dict], 
        news: List[Dict]
    ) -> str:
        """Synthesize all research into actionable insights."""
        competitor_names = [c.get("name", "Unknown") for c in competitors]
        news_count = len(news)
        
        prompt = f"""
        Based on this competitive intelligence about {company_name}, provide a brief investment perspective (2-3 paragraphs):
        
        COMPANY OVERVIEW:
        {overview}
        
        COMPETITORS:
        {json.dumps(competitors, indent=2)}
        
        RECENT NEWS:
        {json.dumps(news, indent=2)}
        
        Provide insights on:
        1. Market positioning relative to competitors
        2. Recent momentum and traction
        3. Potential red flags or concerns
        4. Investment attractiveness (qualitative assessment)
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Unable to synthesize research: {str(e)}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def format_research_report(self, research: Dict) -> str:
        """Format research findings as markdown for storage."""
        md = f"# Competitive Intelligence: {research['company_name']}\n\n"
        md += f"**Industry:** {research['industry']}\n"
        md += f"**Research Date:** {research['timestamp']}\n\n"
        
        md += "## Company Overview\n\n"
        md += f"{research['overview']}\n\n"
        
        if research['competitors']:
            md += "## Competitors\n\n"
            for comp in research['competitors']:
                md += f"### {comp.get('name', 'Unknown')}\n"
                md += f"- **Description:** {comp.get('description', 'N/A')}\n"
                md += f"- **Strength:** {comp.get('strength', 'N/A')}\n"
                md += f"- **Weakness:** {comp.get('weakness', 'N/A')}\n\n"
        
        if research['recent_news']:
            md += "## Recent News\n\n"
            for item in research['recent_news']:
                md += f"**{item.get('headline', 'News Item')}**\n"
                md += f"{item.get('summary', 'No summary available')}\n"
                md += f"*Significance: {item.get('significance', 'N/A')}*\n\n"
        
        md += "## Investment Perspective\n\n"
        md += f"{research['synthesis']}\n"
        
        return md


# Example usage
async def main():
    """Test the research agent."""
    agent = CompetitiveResearchAgent()
    
    # Research a company
    research = await agent.research_company("Airbnb", "Travel Tech")
    
    # Format as report
    report = agent.format_research_report(research)
    print(report)
    
    # Save to file (in real use, would be stored in ChromaDB)
    with open("research_output.md", "w") as f:
        f.write(report)


if __name__ == "__main__":
    asyncio.run(main())
