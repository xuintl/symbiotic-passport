import urllib.request
import json
import time
from collections import Counter

def scout_countries():
    url = 'https://gmrepo.humangut.info/api/getAssociatedRunsByPhenotypeMeshIDLimit/'
    
    # We will grab 5000 runs to get a representative sample of geographic distribution
    limit = 1000 
    max_runs = 100000
    
    country_counter = Counter()
    total_fetched = 0
    
    print("Scouting GMrepo for 'Healthy' (D006262) samples...")
    
    for skip in range(0, max_runs, limit):
        query = {"mesh_id": "D006262", "skip": skip, "limit": limit}
        req = urllib.request.Request(
            url, 
            data=json.dumps(query).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
                
                if not data:
                    break
                
                for run in data:
                    country = run.get('country')
                    if country:
                        country_counter[country] += 1
                        
                total_fetched += len(data)
                print(f"Fetched {total_fetched} runs...")
                time.sleep(0.5) # Be nice to the API
                
        except Exception as e:
            print(f"Error fetching data at skip={skip}: {e}")
            break

    print("\n--- All Countries with 'Healthy' Samples ---")
    for country, count in country_counter.most_common():
        print(f"{country}: {count} samples")

if __name__ == "__main__":
    scout_countries()
