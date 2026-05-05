import urllib.request
import urllib.error
import json
import sys

def test_api():
    # Adding trailing slash based on Django error message
    url = 'https://gmrepo.humangut.info/api/getAssociatedRunsByPhenotypeMeshIDLimit/'
    query = {"mesh_id": "D006262", "skip": 0, "limit": 2}
    
    print(f"Querying: {url}")
    try:
        req = urllib.request.Request(url, data=json.dumps(query).encode('utf-8'), headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            print(f"\nSuccess! Retrieved {len(data)} runs.")
            if len(data) > 0:
                print("\nSample run metadata (first item):")
                print(json.dumps(data[0], indent=2))
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code}")
        print(e.read().decode('utf-8', errors='ignore'))
        sys.exit(1)
    except Exception as e:
        print(f"Error querying API: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_api()
