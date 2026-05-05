import urllib.request
import json
import pandas as pd
import time

TAXA_IDS = {"816": "Bacteroides", "838": "Prevotella", "216851": "Faecalibacterium", "166486": "Roseburia", "1730": "Eubacterium"}
API_BASE = 'https://gmrepo.humangut.info/api'

taxa_data = []
for taxon_id, name in TAXA_IDS.items():
    print(f"Fetching {name}...")
    url = f"{API_BASE}/getMicrobeAbundancesByPhenotypeMeshIDAndNCBITaxonID/"
    payload = {"mesh_id": "D006262", "ncbi_taxon_id": taxon_id}
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result and 'abundance_and_meta_data' in result:
                df = pd.DataFrame(result['abundance_and_meta_data'])
                if not df.empty:
                    taxa_data.append(df[['country']])
    except:
        pass
    time.sleep(0.5)

if taxa_data:
    df_all = pd.concat(taxa_data)
    print(df_all['country'].value_counts())
