import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Set this in your environment variables or .env file
TINYBIRD_URL = "https://api.us-west-2.aws.tinybird.co"

def query_tinybird(sql_query: str):
    """
    Sends raw SQL to Tinybird and returns the JSON result.
    """
    url = f"{TINYBIRD_URL}/v0/sql"
    params = {
        "q": sql_query,
        "token": os.getenv("TINYBIRD_ADMIN_TOKEN")
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        print(response.text)
        return response.json()
    else:
        raise Exception(f"Tinybird Error {response.status_code}: {response.text}")

if __name__ == "__main__":
    # print(query_tinybird("SELECT count() FROM servings_apr_25"))

    sql = """
    SELECT 
        day, 
        sum(coalesce(sugars_g, 0)) as total_sugar
    FROM servings_apr_25
    GROUP BY day
    ORDER BY total_sugar DESC
    LIMIT 1
    """

    print(query_tinybird(sql))