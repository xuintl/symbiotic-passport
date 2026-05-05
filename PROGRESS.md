# 📈 Development Progress Log

This document serves as a historical record of the step-by-step development process used to build the Symbiotic Passport prototype. It details the phases, technical decisions, and iterations made during the project.

## Phase 0: Project Initialization & API Validation
- **Objective:** Validate the primary data source (GMrepo) and set up the local development environment.
- **Actions Taken:**
  - Wrote a test Python script (`test_gmrepo.py`) using `urllib` to query the GMrepo REST API for the "Healthy" phenotype (MeSH ID `D006262`).
  - Encountered and resolved a Django `APPEND_SLASH` 500 error by ensuring all API endpoint URLs included a trailing slash.
  - Successfully retrieved sample metadata, confirming fields like `country`, `run_id`, and `project_id`.
  - Initialized the project directory structure (`data/raw/`, `data/processed/`, `data/priors/`, `notebooks/`, `src/`).
  - Created `requirements.txt` with `streamlit`, `pandas`, `requests`, and `plotly`.
  - Initialized a Python virtual environment using `uv`.
  - Created placeholder JSON files for scientific priors (`migration_priors.json` and `habit_rules.json`).
  - Wrote the initial Streamlit scaffold in `app.py` with sidebar navigation.

## Phase 1: Data Acquisition and Preprocessing
- **Objective:** Mine the GMrepo database to establish regional baselines for the Global Functional Atlas.
- **Actions Taken:**
  - Developed `scout_countries.py` to iteratively query tens of thousands of "Healthy" runs and tally them by country, ensuring we selected regions with statistically significant sample sizes.
  - Expanded the scout script to explicitly search for MENA (Middle East and North Africa) and Central Asian representation at the user's request.
  - Finalized a list of 14 diverse regions (including China, USA, Japan, Mali, UAE, Egypt, Iran, and Russia).
  - Wrote `build_atlas.py`, a comprehensive aggregation script that:
    - Fetches exact relative abundances for key taxa (*Bacteroides*, *Prevotella*, *Faecalibacterium*, *Roseburia*, *Eubacterium*).
    - Pivots the data by region and calculates regional means.
    - Computes derived functional proxies: **SCFA Proxy** (sum of producers), **Westernization Score** (Bacteroides/Prevotella ratio), and a baseline **Diversity Proxy**.
  - Outputted the aggregated data to `data/processed/global_atlas_regions.json`.

## Phase 2: Building the Global Functional Atlas UI
- **Objective:** Render the aggregated data into an interactive visual experience.
- **Actions Taken:**
  - Updated `app.py` to include a Plotly Choropleth world map colored by the Westernization Score.
  - Added a "Region Profiler" utilizing a Plotly Radar Chart to visualize the three functional axes.
  - Implemented Streamlit Session State to allow the user to lock in their "Origin" and "Destination" choices for the journey.
  - *Iterative Improvement:* Based on user feedback, added a prominent, educational expander to explicitly define the biological meaning of the SCFA Proxy, Westernization Score, and Diversity Proxy, making the metrics highly intelligible.

## Phase 3 (Part 1): Building the Transition Map Simulator
- **Objective:** Simulate a 12-month microbiome trajectory based on scientific migration priors.
- **Actions Taken:**
  - Implemented logic in `app.py` to interpolate between the Origin and Destination baseline scores over 12 months.
  - Added a dietary choice modifier (Keep traditional, Adopt Western, Mix).
  - Applied mathematical dampeners/accelerators from `migration_priors.json` based on the user's diet choice.
  - Visualized the 12-month trajectory using a multi-line Plotly graph.
  - Added logic at "Month 12" to evaluate the final scores against the origin baselines to identify specific risks (e.g., "low_scfa" or "low_diversity"), saving these risks to the session state.

## Phase 3 (Part 2): Niche Stability & Balancing Habits
- **Objective:** Provide actionable, constraint-based dietary interventions.
- **Actions Taken:**
  - Read the identified risks from the Transition Map session state.
  - Implemented UI dropdowns for user constraints (Dietary preference, Effort level).
  - Built a filtering engine that cross-references the `habit_rules.json` database against the user's constraints and specific microbiome risks.
  - Rendered visually distinct "Habit Cards" detailing mechanisms, actions, and quantitative axis adjustments using Streamlit metric badges.

## Phase 4: Integrating the AI Microbiome Nutritionist
- **Objective:** Add a personalized, AI-driven deep-dive using the Gemini API.
- **Actions Taken:**
  - Installed the `google-genai` SDK and resolved hot-reloading import conflicts by restarting the Streamlit environment.
  - Added a new tab: "3. Microbiome Nutritionist".
  - Designed an interface for the user to input their Gemini API key and select a primary health goal.
  - Crafted a highly-structured prompt that ingested the Origin, Destination, Health Goal, and flagged risks.
  - *Iterative Improvement:* Enforced strict formatting in the prompt to require Markdown tables (for "Microbiome Impact" and "Intermediary Foods") and checklists for the "Quantitative Action Plan", making the AI output highly specific, clinical, and visually structured.
  - Hooked the prompt up to the `gemini-2.5-flash` model utilizing the Google Search grounding tool for up-to-date dietary references.

## Phase 5: Finalization & Documentation
- **Objective:** Wrap up the project with comprehensive documentation.
- **Actions Taken:**
  - Wrote a detailed `README.md` defining the scope, features, project structure, and deployment instructions.
  - Appended all academic literature and API resources used during development to the README.
  - Created this `PROGRESS.md` file to log the developmental journey.