# scrapriq/services/aggregator.py
from typing import List, Dict

def aggregate_employee_data(
    static_employees: List[Dict], 
    linkedin_employees: List[Dict]
) -> List[Dict]:
    """
    Aggregates employee data from various sources, deduplicates, and standardizes.
    
    Args:
        static_employees: List of employee dictionaries from static page scraping.
        linkedin_employees: List of employee dictionaries from LinkedIn search.
        
    Returns:
        A cleaned, deduplicated list of employee dictionaries.
    """
    
    combined_employees = {} # Use a dictionary for deduplication based on a unique key

    # Process static page employees
    for emp in static_employees:
        name = emp.get("name", "").strip().lower()
        title = emp.get("title", "").strip().lower()
        source = emp.get("source", "")

        # Create a unique key for deduplication (name + title + source, or just name)
        # For simplicity, we'll use a combination of name and title for initial deduplication.
        # This will need refinement for robust deduplication in a real-world scenario (e.g., matching similar names).
        key = f"{name}_{title}" 
        
        if key not in combined_employees:
            combined_employees[key] = {
                "name": emp.get("name", ""),
                "title": emp.get("title", ""),
                "guessed_email": [], # This will be populated by the email guesser later
                "source": source
            }
        # If a duplicate is found, you might want to merge information or prioritize sources.
        # For now, the first one encountered for a given key wins.
    
    # Process LinkedIn employees
    for emp in linkedin_employees:
        name = emp.get("name", "").strip().lower()
        title = emp.get("title", "").strip().lower()
        source = emp.get("source", "")
        
        key = f"{name}_{title}"

        # If LinkedIn provides more details or is considered a higher priority,
        # you might update existing records. For MVP, we're just adding new ones.
        if key not in combined_employees:
            combined_employees[key] = {
                "name": emp.get("name", ""),
                "title": emp.get("title", ""),
                "guessed_email": [], # To be populated by the email guesser
                "source": source
            }
        
    return list(combined_employees.values())

# Example Usage for testing:
if __name__ == "__main__":
    static_data = [
        {"name": "Jane Doe", "title": "Software Engineer", "source": "http://example.com/team"},
        {"name": "John Smith", "title": "Product Manager", "source": "http://example.com/about"},
    ]
    
    linkedin_data = [
        {"name": "Jane Doe", "title": "Software Engineer", "source": "https://linkedin.com/in/janedoe"},
        {"name": "Alice Brown", "title": "UX Designer", "source": "https://linkedin.com/in/alicebrown"},
    ]
    
    aggregated_results = aggregate_employee_data(static_data, linkedin_data)
    print("Aggregated Results:")
    for emp in aggregated_results:
        print(emp)