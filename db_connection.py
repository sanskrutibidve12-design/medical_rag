from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.secrets("SUPABASE_URL")
SUPABASE_KEY = os.secrets("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)