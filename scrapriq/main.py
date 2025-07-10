# scrapriq/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid # For generating unique IDs if needed before DB insertion

from scrapriq.supabase import get_supabase_client
from scrapers.static_scraper import scrape_static_pages
from scrapers.linkedin_scraper import search_linkedin_profiles
from utils.email_guesser import generate_email_guesses
from services.aggregator import aggregate_employee_data

app = FastAPI(title="ScraprIQ Backend MVP")
supabase = get_supabase_client()

# Pydantic models for API input/output validation
class EmployeeOutput(BaseModel):
    name: str
    title: Optional[str] = None
    guessed_email: List[str]
    source: str

class CompanyResult(BaseModel):
    domain: str
    name: Optional[str] = None
    scraped_at: str
    employees: List[EmployeeOutput]

@app.post("/scrape")
async def scrape_domain(domain: str):
    """
    Triggers the scraping process for a given company domain.
    """
    if not domain:
        raise HTTPException(status_code=400, detail="Domain parameter is required.")

    print(f"Starting scrape for domain: {domain}")

    # 1. Scrape Static Pages
    static_employees = scrape_static_pages(domain)
    print(f"Static scraper found {len(static_employees)} employees.")

    # 2. Scrape LinkedIn via Google Search
    linkedin_employees = search_linkedin_profiles(domain)
    print(f"LinkedIn scraper found {len(linkedin_employees)} employees.")

    # 3. Aggregate and Deduplicate Data
    all_employees = aggregate_employee_data(static_employees, linkedin_employees)
    print(f"Aggregator produced {len(all_employees)} unique employee records.")

    # 4. Generate Email Guesses for each employee
    for emp in all_employees:
        # Basic name splitting for email guessing. Will need robust name parsing for production.
        name_parts = emp["name"].strip().split(' ', 1) 
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""
        
        if first_name and last_name: # Only guess if both parts are available
            emp["guessed_email"] = generate_email_guesses(first_name, last_name, domain)
        else:
            emp["guessed_email"] = [] # No guess if name is incomplete

    # 5. Store results in Supabase
    try:
        # Insert or update company record
        company_data, count = supabase.from_('companies').upsert(
            {"domain": domain, "name": domain.split('.')[0], "scraped_at": "now()"}, # Basic name from domain
            on_conflict="domain" # Use domain as unique key for upsert
        ).execute()
        
        # Get the company_id for the inserted/updated company
        company_id = company_data[1][0]['id']
        print(f"Company '{domain}' (ID: {company_id}) processed in Supabase.")

        # Prepare employee records for bulk insertion
        employee_records_to_insert = []
        for emp in all_employees:
            # Ensure email_guess is a list of strings, join if needed for storage
            email_guesses_str = ",".join(emp.get("guessed_email", []))

            employee_records_to_insert.append({
                "company_id": str(company_id), # Ensure it's a string for UUID type in Supabase
                "name": emp.get("name", ""),
                "title": emp.get("title", ""),
                "email_guess": email_guesses_str, # Store as comma-separated string
                "source": emp.get("source", ""),
                "found_at": "now()"
            })
        
        if employee_records_to_insert:
            # Clear existing employees for this company before inserting new ones to avoid duplicates on re-scrape
            supabase.from_('employees').delete().eq('company_id', company_id).execute()
            print(f"Cleared existing employees for company ID: {company_id}")

            # Insert new employee records in bulk
            inserted_employees, count_emp = supabase.from_('employees').insert(employee_records_to_insert).execute()
            print(f"Inserted {count_emp[1]} employee records for {domain}.")
        else:
            print(f"No employee records to insert for {domain}.")

        return {"message": "Scraping initiated and results stored.", "domain": domain, "employees_found": len(all_employees)}

    except Exception as e:
        print(f"Error storing data to Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to store results: {str(e)}")

@app.get("/results/{domain}", response_model=CompanyResult)
async def get_results(domain: str):
    """
    Fetches stored employee results for a given company domain.
    """
    if not domain:
        raise HTTPException(status_code=400, detail="Domain parameter is required.")
    
    try:
        # Fetch company details
        company_res = supabase.from_('companies').select('*').eq('domain', domain).limit(1).execute()
        company_data = company_res.data
        
        if not company_data:
            raise HTTPException(status_code=404, detail=f"No results found for domain: {domain}")

        company = company_data[0]

        # Fetch employees associated with this company
        employees_res = supabase.from_('employees').select('*').eq('company_id', company['id']).execute()
        employees_data = employees_res.data
        
        output_employees = []
        for emp in employees_data:
            output_employees.append(EmployeeOutput(
                name=emp['name'],
                title=emp['title'],
                # Convert comma-separated string back to list
                guessed_email=emp['email_guess'].split(',') if emp['email_guess'] else [],
                source=emp['source']
            ))

        return CompanyResult(
            domain=company['domain'],
            name=company['name'],
            scraped_at=company['scraped_at'],
            employees=output_employees
        )

    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")

# To run the API locally:
# In your terminal, navigate to the `scrapriq` directory and run:
# uvicorn main:app --reload --port 8000