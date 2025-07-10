# scrapriq/scrapers/linkedin_scraper.py
import requests
import os # To access environment variables or config
from urllib.parse import urlparse, parse_qs
from config import SERP_API_KEY # Assuming SERP_API_KEY is in config.py

def search_linkedin_profiles(domain: str) -> list[dict]:
    """
    Searches Google for LinkedIn profiles associated with the given domain using SerpAPI.
    Parses SERP results for name and title.
    """
    if not SERP_API_KEY:
        print("SERP_API_KEY is not configured. Skipping LinkedIn search.")
        return []

    query = f'site:linkedin.com/in "{domain}"'
    api_url = "https://serpapi.com/search"
    
    params = {
        "api_key": SERP_API_KEY,
        "engine": "google",
        "q": query,
        "hl": "en",
        "num": 20 # Number of results to fetch per page
    }

    employees_found = []
    
    try:
        response = requests.get(api_url, params=params, timeout=15)
        response.raise_for_status()
        search_results = response.json()

        # Parse organic results
        for result in search_results.get("organic_results", []):
            link = result.get("link")
            title = result.get("title") # This often contains name and title

            if link and "linkedin.com/in/" in link:
                # Attempt to parse name and title from the SERP title
                name, role = parse_name_and_role_from_linkedin_title(title)
                if name:
                    employees_found.append({
                        "name": name,
                        "title": role,
                        "source": link
                    })
        
    except requests.exceptions.RequestException as e:
        print(f"Error during SerpAPI request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during LinkedIn search: {e}")

    return employees_found

def parse_name_and_role_from_linkedin_title(title: str) -> tuple[str, str]:
    """
    Attempts to extract name and role from a LinkedIn SERP title.
    Example: "John Doe | Senior Software Engineer at Company Name"
    """
    name = ""
    role = ""
    parts = title.split(' | ')
    if len(parts) > 0:
        name = parts[0].strip()
        if len(parts) > 1:
            role_part = parts[1].strip()
            # Try to extract role before "at Company Name"
            if " at " in role_part:
                role = role_part.split(" at ")[0].strip()
            else:
                role = role_part
    return name, role

# Example Usage (for testing locally):
if __name__ == "__main__":
    # Ensure you have a SERP_API_KEY set in your config.py for this to work
    # Or temporarily set it as an environment variable for testing
    # os.environ["SERP_API_KEY"] = "YOUR_TEST_SERP_API_KEY"
    
    test_domain = "google.com" # Use a well-known company for better results
    employees = search_linkedin_profiles(test_domain)
    if employees:
        print(f"\nFound {len(employees)} potential employees via LinkedIn search for {test_domain}:")
        for emp in employees:
            print(emp)
    else:
        print(f"\nNo employees found via LinkedIn search for {test_domain}. Check SERP_API_KEY and domain validity.")