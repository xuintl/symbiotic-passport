import urllib.request
import json
import time
import os
import pandas as pd

# The regions we are profiling
REGIONS = {
    "china_urban": {"country": "China"},
    "japan_urban": {"country": "Japan"},
    "usa_urban": {"country": "United States of America"},
    "netherlands_urban": {"country": "Netherlands"},
    "italy_urban": {"country": "Italy"},
    "uk_urban": {"country": "United Kingdom"},
    "india_mix": {"country": "India"},
    "australia_urban": {"country": "Australia"},
    "mali_rural": {"country": "Mali"},
    "peru_rural": {"country": "Peru"},
    "uae_urban": {"country": "United Arab Emirates"},
    "egypt_mix": {"country": "Egypt"},
    "iran_mix": {"country": "Iran"},
    "russia_mix": {"country": "Russia"}
}

# The taxa we care about for our axes
TAXA_IDS = {
    "816": "Bacteroides",       # Associated with Western diets
    "838": "Prevotella",        # Associated with high-fiber/traditional diets
    "216851": "Faecalibacterium", # SCFA producer
    "166486": "Roseburia",      # SCFA producer
    "1730": "Eubacterium"       # SCFA producer
}

API_BASE = 'https://gmrepo.humangut.info/api'

def fetch_json(url, payload):
    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'), 
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"API Error at {url}: {e}")
        return None

def build_atlas():
    print("Starting Atlas Data Aggregation...")
    
    # 1. First, fetch the relative abundances of our key taxa across ALL healthy samples
    print("Fetching taxa abundance data...")
    taxa_data = []
    
    for taxon_id, name in TAXA_IDS.items():
        print(f"  Fetching {name} ({taxon_id})...")
        url = f"{API_BASE}/getMicrobeAbundancesByPhenotypeMeshIDAndNCBITaxonID/"
        payload = {"mesh_id": "D006262", "ncbi_taxon_id": taxon_id}
        
        result = fetch_json(url, payload)
        if result and 'abundance_and_meta_data' in result:
            df = pd.DataFrame(result['abundance_and_meta_data'])
            if not df.empty:
                # We only need run_id, country, and relative_abundance
                df = df[['run_id', 'country', 'relative_abundance']]
                df['taxon'] = name
                taxa_data.append(df)
        time.sleep(1)
        
    if not taxa_data:
        print("Failed to fetch any taxa data.")
        return
        
    # Combine all taxa data into one big dataframe
    df_all = pd.concat(taxa_data, ignore_index=True)
    
    # 2. Pivot the data so each run has a column for each taxon
    print("Pivoting data...")
    df_pivot = df_all.pivot_table(
        index=['run_id', 'country'], 
        columns='taxon', 
        values='relative_abundance', 
        fill_value=0.0
    ).reset_index()
    
    # 3. Calculate scores per region
    atlas_output = {}
    
    print("Calculating functional metrics per region...")
    for region_id, meta in REGIONS.items():
        target_country = meta["country"]
        region_df = df_pivot[df_pivot['country'] == target_country]
        
        n_samples = len(region_df)
        if n_samples == 0:
            print(f"  Skipping {region_id} (No samples found)")
            continue
            
        print(f"  Processed {region_id} (n={n_samples})")
        
        # Means
        means = region_df.mean(numeric_only=True)
        
        # SCFA Proxy (Sum of the three SCFA producers)
        # Note: GMrepo uses percentage (0-100), we normalize loosely
        scfa_raw = means.get('Faecalibacterium', 0) + means.get('Roseburia', 0) + means.get('Eubacterium', 0)
        # Assuming max raw sum is around 25% relative abundance, we scale it ~0-1
        scfa_proxy = min(scfa_raw / 25.0, 1.0)
        
        # Westernization Score (Bacteroides vs Prevotella ratio concept)
        bact = means.get('Bacteroides', 0.001) # Avoid div by zero
        prev = means.get('Prevotella', 0.001)
        # Log ratio scaled roughly 0-1
        ratio = bact / (prev + bact)
        westernization = min(max(ratio, 0.0), 1.0)
        
        # Diversity (Mock baseline proxy for the prototype, since full shannon calculation takes 10,000 API calls)
        # We estimate baseline diversity slightly higher in rural/high prevotella
        diversity_proxy = 0.6 + (0.3 * (1 - westernization))
        
        atlas_output[region_id] = {
            "region_name": target_country,
            "region_id": region_id,
            "n_samples": n_samples,
            "axes": {
                "scfa_proxy": round(scfa_proxy, 3),
                "westernization_score": round(westernization, 3),
                "diversity_proxy": round(diversity_proxy, 3)
            },
            "taxa_means": {
                "Bacteroides": round(means.get('Bacteroides', 0), 2),
                "Prevotella": round(means.get('Prevotella', 0), 2),
                "Faecalibacterium": round(means.get('Faecalibacterium', 0), 2)
            }
        }
        
    # 4. Save to JSON
    out_path = os.path.join("data", "processed", "global_atlas_regions.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    
    with open(out_path, 'w') as f:
        json.dump(atlas_output, f, indent=2)
        
    print(f"\nDone! Atlas data saved to {out_path}")

if __name__ == "__main__":
    build_atlas()
