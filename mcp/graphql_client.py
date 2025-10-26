"""
Simple GraphQL client for PKM database operations.
"""

import requests
import json
import logging
import os
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class GraphQLClient:
    """Simple client for GraphQL operations."""
    
    def __init__(self, graphql_url: str = "http://localhost:5001/graphql"):
        self.graphql_url = graphql_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def execute_gql_file(self, query_name: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a query from the .gql file by name."""
        try:
            # Load the .gql file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            gql_file_path = os.path.join(current_dir, '..', 'graphql', 'gql', 'models.gql')
            
            with open(gql_file_path, 'r') as f:
                content = f.read()
            
            # Find the query by name - more reliable approach
            import re
            
            # Find the start of the query
            start_pattern = rf'query\s+{query_name}(?:\([^)]*\))?\s*\{{'
            start_match = re.search(start_pattern, content, re.DOTALL)
            
            if not start_match:
                return {"success": False, "error": f"Query '{query_name}' not found"}
            
            # Find the matching closing brace by counting braces
            start_pos = start_match.start()
            brace_count = 0
            pos = start_pos
            
            while pos < len(content):
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Found the matching closing brace
                        query = content[start_pos:pos + 1]
                        break
                pos += 1
            else:
                return {"success": False, "error": f"Query '{query_name}' has unmatched braces"}
            
            # Extract all fragments from the file - need to handle nested braces
            def extract_fragment(content, start_pos):
                """Extract a complete fragment by counting braces."""
                brace_count = 0
                pos = start_pos
                
                while pos < len(content):
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            return content[start_pos:pos + 1]
                    pos += 1
                return None
            
            # Find all fragment starts
            fragment_starts = []
            for match in re.finditer(r'fragment\s+\w+\s+on\s+\w+\s*\{', content):
                fragment_starts.append(match.start())
            
            # Extract complete fragments
            all_fragments = {}
            for start_pos in fragment_starts:
                fragment = extract_fragment(content, start_pos)
                if fragment:
                    # Extract fragment name
                    name_match = re.search(r'fragment\s+(\w+)', fragment)
                    if name_match:
                        all_fragments[name_match.group(1)] = fragment
            
            # Find which fragments are used in the query
            used_fragments = []
            for fragment_name in all_fragments:
                if f'...{fragment_name}' in query:
                    used_fragments.append(all_fragments[fragment_name])
            
            # Combine only used fragments and query
            full_query = '\n\n'.join(used_fragments) + '\n\n' + query
            
            # Execute the query
            payload = {"query": full_query, "variables": variables or {}}
            response = self.session.post(self.graphql_url, json=payload)
            response.raise_for_status()
            
            result = response.json()
            
            if "errors" in result:
                return {"success": False, "error": "GraphQL errors", "details": result["errors"]}
            
            return {"success": True, "data": result.get("data", {})}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
# Global client instance
graphql_client = GraphQLClient()
