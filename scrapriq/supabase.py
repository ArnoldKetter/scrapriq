# supabase.py
from supabase import create_client, Client
from .config import SUPABASE_URL, SUPABASE_KEY

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client():
    """Returns the initialized Supabase client."""
    return supabase

# You can add functions here later to interact with your tables, e.g.,
# def insert_company(domain, name=None):
#     data, count = supabase.from_('companies').insert({"domain": domain, "name": name}).execute()
#     return data[1][0] # Returns the inserted record