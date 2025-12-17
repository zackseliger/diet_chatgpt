import os
import requests
from dotenv import load_dotenv

load_dotenv()

TINYBIRD_URL = "https://api.us-west-2.aws.tinybird.co"
TINYBIRD_TOKEN = os.getenv("TINYBIRD_ADMIN_TOKEN")

def query_tinybird(sql_query: str):
    url = f"{TINYBIRD_URL}/v0/sql"
    # Ensure we get JSON
    if "FORMAT JSON" not in sql_query.upper():
        sql_query += " FORMAT JSON"

    params = {
        "q": sql_query,
        "token": TINYBIRD_TOKEN
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        # Try to return text if json fails, or error
        try:
            return response.json()
        except:
            raise Exception(f"Tinybird Error {response.status_code}: {response.text}")