# 🦠 Symbiotic Passport (Course Edition)

Symbiotic Passport is an interactive, browser-based web tool designed to help users explore how gut microbiome "functions" differ across global regions, how moving between those regions might shift those functions, and which precise, science-backed dietary habits can buffer those changes.

This project was built to demonstrate the integration of live database mining ([GMrepo](https://gmrepo.humangut.info/)), literature-derived scientific priors, and generative AI (Gemini API) into a cohesive educational narrative.

A detailed development progress log may be accessed [here](/PROGRESS.md).

---

## 🎯 Scope and Goals

**Target Scope:** Single-user, interactive UI designed for educational value and biological transparency.

**Data Foundation:** Real microbiome taxonomic profiles aggregated from the GMrepo REST API, heavily synthesized to run instantly on the client side.

**Simulation Logic:** Literature-derived priors dictating the physiological drift of Short-Chain Fatty Acid (SCFA) producers, microbial diversity, and "Westernization" (Bacteroides/Prevotella ratios) based on user diet choices over a 12-month migration.

**Personalization:** A Gemini-powered "Microbiome Nutritionist" that provides highly specific, quantitative, and culturally relevant dietary bridging strategies.

---

## ✨ Features

The application is structured into four distinct sequential functions:

### 1. Global Functional Atlas (Function 0)
- **Interactive Choropleth Map:** Visualizes a curated set of 14 global regions colored by their baseline "Westernization" score.
- **Data-Driven Baselines:** Underlying data was aggregated from over 35,000 "Healthy" gut microbiome sequencing runs via the GMrepo API.
- **Radar Profiling:** Instantly view the balance of SCFA Proxies, Westernization Scores, and Diversity Proxies for any selected region.

### 2. Transition Map (Function 1)
- **12-Month Simulator:** Simulates the physiological shift when moving from a selected Origin to a Destination.
- **Dietary Modulation:** The trajectory is dynamically altered based on whether the user chooses to "Keep a traditional high-fiber diet", "Adopt a local Westernized diet", or mix both.
- **Risk Identification:** Automatically flags dangerous drops in microbial diversity or SCFA production for the next stage.

### 3. Niche Stability & Balancing Habits (Function 2)
- **Constraint-Based Filtering:** Reads identified risks from the Transition Map and filters a database of clinical interventions based on the user's dietary restrictions (e.g., Vegan) and effort tolerance.
- **Actionable Metrics:** Displays clear habit cards detailing biological mechanisms, culinary actions, and exact expected quantitative boosts to functional axes.

### 4. Nutritionist (Function 3)
- **Generative AI Integration:** Powered by the `gemini-2.5-flash` model.
- **Culinary Bridging:** Analyzes the exact culinary shift between the Origin and Destination countries to suggest culturally relevant "bridging foods".
- **Structured Output:** Delivers rich Markdown tables outlining macro/micro-nutrient shifts, affected taxa, and precise quantitative targets tailored to the user's specific health goal.

---

## 📂 Project Structure

```text
symbiotic_passport/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python package dependencies
├── build_atlas.py              # Script to mine GMrepo and compile JSON atlas
├── scout_countries.py          # Script used to identify top represented countries
├── data/
│   ├── processed/
│   │   └── global_atlas_regions.json  # Pre-computed region profiles (Function 0)
│   ├── priors/
│   │   ├── migration_priors.json      # Literature priors for trajectory simulation
│   │   └── habit_rules.json           # Constraint-based intervention database
```

---

## 🚀 Setup and Development

You are encouraged to confer with an AI model if you have encountered any issues in deployment and development. 

### Prerequisites
- Python 3.10+
- `uv` (recommended) or `pip`

### Local Installation

1. **Clone the repository and enter the directory:**
   
   ```bash
   cd symbiotic_passport
   ```

3. **Create a virtual environment and install dependencies:**
   Using `uv` (faster):
   
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```
   
   Or using standard `pip`:
   
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Set your API Key (For Function 3):**
   To use the Microbiome Nutritionist, you need a Google Gemini API Key. You can either enter it directly into the application UI, or set it as an environment variable:
   
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

### Running the Application

Launch the interactive Streamlit server:

```bash
streamlit run app.py
```

The application will automatically open in your default web browser at `http://localhost:8501`.

---

## 🧬 Data Pipeline (Re-building the Atlas)

The `global_atlas_regions.json` file is already included so the app runs instantly. However, if you wish to rebuild the dataset, modify the regions, or pull fresh GMrepo data:

1. Ensure your virtual environment is active.
2. Run the aggregation script:
   
   ```bash
   python build_atlas.py
   ```
   
*Note: This script makes hundreds of API calls to GMrepo to fetch taxonomic abundances and averages them. It takes a few minutes to complete.*

---

## 📚 Resources and References

**Databases & APIs:**
- [GMrepo v2 Database](https://gmrepo.humangut.info/)
- [GMrepo Programmable Access (GitHub)](https://github.com/evolgeniusteam/GMrepoProgrammableAccess)
- [GMrepo Original Publication (Nucleic Acids Research)](https://academic.oup.com/nar/article/48/D1/D545/5559685)

**Scientific Literature (Priors for Simulation & Habits):**
- Vangay et al., *US immigration Westernizes the human gut microbiome* (Hmong/Karen populations). [PMC6498444](https://pmc.ncbi.nlm.nih.gov/articles/PMC6498444/)
- *South Asian migration to Canada and the microbiome*. [PMC8023248](https://pmc.ncbi.nlm.nih.gov/articles/PMC8023248/)
- *Urbanization gradients and microbial diversity in Africa*. [Africanews](https://www.africanews.com/2025/06/27/african-gut-study-reveals-urbanization-threatens-microbial-diversity/)
- *Microbiota-based personalized nutrition trials*. [PMC11214429](https://pmc.ncbi.nlm.nih.gov/articles/PMC11214429/)
- *Reviews linking dietary patterns to SCFA and diversity*. [PMC10917618](https://pmc.ncbi.nlm.nih.gov/articles/PMC10917618/)

**Tech Stack:**
- [Streamlit](https://streamlit.io/) (Frontend & State Management)
- [Plotly](https://plotly.com/python/) (Interactive Visualizations)
- [Google Gemini API](https://ai.google.dev/) (Generative AI Nutritionist)
