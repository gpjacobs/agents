from crewai.tools import BaseTool
from typing import Type, Optional, Any
from pydantic import BaseModel, Field
import os
import requests
import json


class SearchToolInput(BaseModel):
    """Input schema for SearchTool."""
    query: str = Field(..., description="The search query string to search the internet")


class DebugSearchTool(BaseTool):
    name: str = "search_the_internet"
    description: str = (
        "A tool to search the internet. "
        "Input is a search query string. "
        "Returns search results from the internet."
    )
    args_schema: Type[BaseModel] = SearchToolInput

    def _run(self, query: str = "", **kwargs) -> str:
        """Execute the search with debugging"""
        print(f"\n=== DEBUG: Search tool called ===")
        print(f"Query received: '{query}'")
        print(f"All kwargs: {kwargs}")
        
        # Check all possible parameter variations
        search_query = query or kwargs.get('query') or kwargs.get('search_query') or kwargs.get('q', '')
        
        print(f"Final search query: '{search_query}'")
        print(f"Query type: {type(search_query)}")
        
        if not search_query or not search_query.strip():
            error_msg = f"Error: No search query provided. Query='{query}', Kwargs={kwargs}"
            print(f"=== DEBUG: {error_msg} ===\n")
            return error_msg
        
        api_key = os.getenv('SERPER_API_KEY')
        if not api_key:
            return "Error: SERPER_API_KEY not found in environment variables"
        
        print(f"API Key found: {api_key[:10]}...")
        
        try:
            url = "https://google.serper.dev/search"
            payload = json.dumps({"q": search_query, "num": 3})
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            
            print(f"Making request to Serper API...")
            response = requests.post(url, headers=headers, data=payload)
            print(f"Response status: {response.status_code}")
            
            if response.status_code == 200:
                results = response.json()
                
                # Format results
                output = f"Search results for: {search_query}\n\n"
                
                # Add organic results
                if 'organic' in results:
                    for i, result in enumerate(results['organic'][:3], 1):
                        output += f"{i}. {result.get('title', 'No title')}\n"
                        output += f"   {result.get('snippet', 'No snippet')}\n"
                        output += f"   URL: {result.get('link', 'No link')}\n\n"
                
                print(f"=== DEBUG: Search successful, returning {len(output)} characters ===\n")
                return output
            else:
                error_msg = f"Error: API returned status {response.status_code}: {response.text}"
                print(f"=== DEBUG: {error_msg} ===\n")
                return error_msg
                
        except Exception as e:
            error_msg = f"Error executing search: {str(e)}"
            print(f"=== DEBUG: {error_msg} ===\n")
            return error_msg
