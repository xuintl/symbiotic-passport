import streamlit as st
import pandas as pd
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from openai import OpenAI

# --- Configuration ---
st.set_page_config(
    page_title="Symbiotic Passport",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- State Initialization ---
if "origin_region" not in st.session_state:
    st.session_state.origin_region = None
if "dest_region" not in st.session_state:
    st.session_state.dest_region = None

# --- Data Loading ---
@st.cache_data
def load_global_atlas():
    path = os.path.join("data", "processed", "global_atlas_regions.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

@st.cache_data
def load_priors():
    migration_path = os.path.join("data", "priors", "migration_priors.json")
    habits_path = os.path.join("data", "priors", "habit_rules.json")
    
    migration_priors = {}
    habit_rules = {}
    
    if os.path.exists(migration_path):
        with open(migration_path, "r") as f:
            migration_priors = json.load(f)
            
    if os.path.exists(habits_path):
        with open(habits_path, "r") as f:
            habit_rules = json.load(f)
            
    return migration_priors, habit_rules

# --- Main App ---
def main():
    st.title("🦠 Symbiotic Passport")
    st.markdown("""
    **Course Edition Prototype.** Explore how gut microbiome functions 
    differ across regions, how moving changes them, and discover Balancing Habits.
    """)
    
    # Load data
    atlas_data = load_global_atlas()
    migration_priors, habit_rules = load_priors()
    
    if not atlas_data:
        st.warning("Atlas data not found. Please run the data aggregation script.")
        st.stop()
        
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["0. Global Atlas", "1. Transition Map", "2. Balancing Habits", "3. Nutritionist"])
    
    # Display current selections in sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("Your Journey")
    orig_name = atlas_data[st.session_state.origin_region]["region_name"] if st.session_state.origin_region else "None"
    dest_name = atlas_data[st.session_state.dest_region]["region_name"] if st.session_state.dest_region else "None"
    st.sidebar.write(f"**Origin:** {orig_name}")
    st.sidebar.write(f"**Destination:** {dest_name}")
    
    if page == "0. Global Atlas":
        render_global_atlas(atlas_data)
            
    elif page == "1. Transition Map":
        render_transition_map(atlas_data, migration_priors)
        
    elif page == "2. Balancing Habits":
        render_balancing_habits(habit_rules)
        
    elif page == "3. Nutritionist":
        render_ai_nutritionist(atlas_data)

def render_balancing_habits(habit_rules):
    st.header("Function 2: Niche Stability & Balancing Habits")
    st.markdown("Personalized habit recommendations to buffer at-risk functional axes.")
    
    if "identified_risks" not in st.session_state or not st.session_state.identified_risks:
        st.info("No immediate risks identified yet. Complete the **Transition Map** simulation to see personalized recommendations.")
        # We can still show all habits if no risks
        risks_to_address = ["low_scfa", "low_diversity"] # Default to showing everything
    else:
        risks_to_address = st.session_state.identified_risks
        st.warning(f"**Identified Risks from Transition:** {', '.join(risks_to_address).replace('_', ' ').title()}")
        
    st.subheader("Your Preferences")
    col1, col2 = st.columns(2)
    with col1:
        diet_pref = st.selectbox("Dietary Constraints", ["None", "Vegetarian", "Vegan"])
    with col2:
        effort_pref = st.selectbox("Maximum Effort Level", ["High", "Medium", "Low"])
        
    # Effort mapping for filtering (Low effort should only show low. Medium shows low/medium. High shows all)
    effort_levels = {"Low": 1, "Medium": 2, "High": 3}
    user_effort_val = effort_levels[effort_pref]
    
    st.subheader("Recommended Habits")
    
    shown_habits = 0
    for habit in habit_rules:
        # Constraint checking
        habit_diet = habit.get("constraints", {}).get("diet", ["none"])
        habit_effort = habit.get("constraints", {}).get("effort_level", "low").capitalize()
        habit_effort_val = effort_levels.get(habit_effort, 1)
        
        # Filter by diet (if user is vegan, habit must allow vegan. None allows anything)
        if diet_pref.lower() != "none" and diet_pref.lower() not in [d.lower() for d in habit_diet]:
            continue
            
        # Filter by effort
        if habit_effort_val > user_effort_val:
            continue
            
        # Filter by relevance to risks (simple mapping)
        is_relevant = False
        if "low_scfa" in risks_to_address and habit.get("adjustments", {}).get("scfa_proxy", 0) > 0:
            is_relevant = True
        if "low_diversity" in risks_to_address and habit.get("adjustments", {}).get("diversity", 0) > 0:
            is_relevant = True
            
        if not is_relevant and st.session_state.get("identified_risks"):
             continue # Skip if it doesn't address a risk, unless there are no risks
             
        shown_habits += 1
        with st.container():
            st.markdown(f"### 🛡️ {habit.get('target_function', 'Balancing Habit')}")
            st.markdown(f"**Mechanism:** {habit.get('mechanism', '')}")
            st.markdown("**Actions:**")
            for action in habit.get('actions', []):
                st.markdown(f"- {action}")
                
            # Show adjustments as badges/pills
            adj = habit.get('adjustments', {})
            adj_cols = st.columns(len(adj))
            for i, (axis, val) in enumerate(adj.items()):
                with adj_cols[i]:
                    color = "normal" if val > 0 else "inverse"
                    st.metric(axis.replace("_", " ").title(), f"{'+' if val > 0 else ''}{val}", delta_color=color)
            st.markdown("---")
            
    if shown_habits == 0:
        st.info("No habits match your current constraints. Try relaxing your dietary or effort preferences.")

def render_transition_map(atlas_data, migration_priors):
    st.header("Function 1: Transition Map (Origin → Destination)")
    
    if not st.session_state.origin_region or not st.session_state.dest_region:
        st.warning("Please set both an Origin and a Destination region in the Global Atlas first!")
        return
        
    orig_profile = atlas_data[st.session_state.origin_region]
    dest_profile = atlas_data[st.session_state.dest_region]
    
    if st.session_state.origin_region == st.session_state.dest_region:
        st.info("Origin and Destination are the same! Try selecting different regions to see a transition.")
        return
    
    st.markdown(f"**Simulating shift from {orig_profile['region_name']} to {dest_profile['region_name']} over 12 months.**")
    
    diet_choice = st.radio(
        "What dietary pattern will you adopt after moving?",
        ["Mix of both", "Keep traditional high-fiber diet", "Adopt local Westernized diet"]
    )
    
    # Calculate target differences
    orig_axes = orig_profile["axes"]
    dest_axes = dest_profile["axes"]
    
    # Apply modifiers based on diet choice
    diet_modifiers = migration_priors.get("diet_modifiers", {})
    scfa_mult = 1.0
    div_mult = 1.0
    if diet_choice == "Keep traditional high-fiber diet":
        scfa_mult = diet_modifiers.get("keep_traditional", {}).get("scfa_multiplier", 0.5)
        div_mult = diet_modifiers.get("keep_traditional", {}).get("diversity_multiplier", 0.5)
    elif diet_choice == "Adopt local Westernized diet":
        scfa_mult = diet_modifiers.get("adopt_western", {}).get("scfa_multiplier", 1.5)
        div_mult = diet_modifiers.get("adopt_western", {}).get("diversity_multiplier", 1.5)
        
    # Generate 12 months of data
    months = list(range(13))
    trajectory = {"Month": months, "SCFA Proxy": [], "Westernization Score": [], "Diversity Proxy": []}
    
    # Simple linear interpolation with diet modulation towards the destination
    for month in months:
        progress = month / 12.0
        
        # Calculate raw delta towards destination
        delta_scfa = (dest_axes["scfa_proxy"] - orig_axes["scfa_proxy"]) * progress
        delta_west = (dest_axes["westernization_score"] - orig_axes["westernization_score"]) * progress
        delta_div = (dest_axes["diversity_proxy"] - orig_axes["diversity_proxy"]) * progress
        
        # Modulate deltas if they are negative (losing good things) or positive (gaining bad things)
        if delta_scfa < 0: delta_scfa *= scfa_mult
        if delta_div < 0: delta_div *= div_mult
        # Westernization increases faster if adopting western diet
        if delta_west > 0 and diet_choice == "Adopt local Westernized diet": delta_west *= 1.5
        elif delta_west > 0 and diet_choice == "Keep traditional high-fiber diet": delta_west *= 0.5
        
        curr_scfa = max(0.0, min(1.0, orig_axes["scfa_proxy"] + delta_scfa))
        curr_west = max(0.0, min(1.0, orig_axes["westernization_score"] + delta_west))
        curr_div = max(0.0, min(1.0, orig_axes["diversity_proxy"] + delta_div))
        
        trajectory["SCFA Proxy"].append(curr_scfa)
        trajectory["Westernization Score"].append(curr_west)
        trajectory["Diversity Proxy"].append(curr_div)
        
    df_traj = pd.DataFrame(trajectory)
    
    # Plotly Line Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_traj["Month"], y=df_traj["SCFA Proxy"], mode='lines+markers', name='SCFA Proxy', line=dict(color='#2ca02c')))
    fig.add_trace(go.Scatter(x=df_traj["Month"], y=df_traj["Westernization Score"], mode='lines+markers', name='Westernization Score', line=dict(color='#d62728')))
    fig.add_trace(go.Scatter(x=df_traj["Month"], y=df_traj["Diversity Proxy"], mode='lines+markers', name='Diversity Proxy', line=dict(color='#1f77b4')))
    
    fig.update_layout(
        title="Projected Microbiome Functional Axes Over Time",
        xaxis_title="Months After Move",
        yaxis_title="Proxy Score (0.0 - 1.0)",
        yaxis=dict(range=[0, 1.1]),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Identify Risks
    final_scfa = trajectory["SCFA Proxy"][-1]
    final_div = trajectory["Diversity Proxy"][-1]
    
    st.subheader("Trajectory Highlights")
    risks = []
    if final_scfa < orig_axes["scfa_proxy"] - 0.05:
        st.error(f"⚠️ You are likely to lose a significant portion of your SCFA producers unless mitigated.")
        risks.append("low_scfa")
    if final_div < orig_axes["diversity_proxy"] - 0.05:
        st.warning(f"⚠️ Microbial diversity is projected to decline.")
        risks.append("low_diversity")
    if not risks and final_scfa >= orig_axes["scfa_proxy"] and final_div >= orig_axes["diversity_proxy"]:
        st.success(f"🌱 Your microbiome functions are projected to remain stable or improve!")
    elif not risks:
        st.info("🔄 Your microbiome functions will undergo a moderate shift, but remain relatively balanced.")
        
    st.session_state.identified_risks = risks

def render_global_atlas(atlas_data):
    st.header("Function 0: Global Functional Atlas")
    st.markdown("Visual overview of region-wise differences derived from the GMrepo 'healthy adult gut' data.")
    
    # Prepare data for Plotly
    df_atlas = pd.DataFrame([{
        "id": k,
        "Country": v["region_name"],
        "Samples": v["n_samples"],
        "SCFA Proxy": v["axes"]["scfa_proxy"],
        "Westernization": v["axes"]["westernization_score"],
        "Diversity Proxy": v["axes"]["diversity_proxy"]
    } for k, v in atlas_data.items()])
    
    # Create map
    fig = px.choropleth(
        df_atlas,
        locations="Country",
        locationmode="country names",
        color="Westernization",
        hover_name="Country",
        hover_data=["Samples", "SCFA Proxy", "Diversity Proxy"],
        color_continuous_scale=px.colors.diverging.Tealrose,
        title="Global Microbiome Functional Proxies (Color: Westernization Score)"
    )
    fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, geo=dict(showcoastlines=True))
    st.plotly_chart(fig, use_container_width=True)
    
    # Selection area
    st.subheader("Explore a Region")
    
    with st.expander("📖 What do these metrics mean?", expanded=True):
        st.markdown("""
        * **SCFA Proxy (0-1):** Short-Chain Fatty Acids (SCFAs) are crucial nutrients produced when bacteria ferment fiber. Higher scores indicate a microbiome rich in beneficial SCFA-producers (e.g., *Faecalibacterium*), linked to reduced inflammation and strong gut barriers.
        * **Westernization Score (0-1):** Reflects the balance between *Bacteroides* and *Prevotella* bacteria. Scores closer to **1.0** indicate a Westernized diet (high fat/sugar, low fiber). Scores closer to **0.0** indicate a traditional, agrarian lifestyle (high complex carbohydrates).
        * **Diversity Proxy (0-1):** Measures the richness and evenness of the microbial community. Higher diversity is universally considered a hallmark of a robust, resilient, and healthy gut ecosystem.
        """)
        
    col1, col2 = st.columns([1, 2])
    
    region_options = {v["region_name"]: k for k, v in atlas_data.items()}
    
    with col1:
        selected_name = st.selectbox("Select Region Profile:", list(region_options.keys()))
        selected_id = region_options[selected_name]
        profile = atlas_data[selected_id]
        
        st.metric("Sample Count (GMrepo)", profile["n_samples"])
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Set as Origin"):
                st.session_state.origin_region = selected_id
                st.success(f"Origin set to {selected_name}!")
        with c2:
            if st.button("Set as Destination"):
                st.session_state.dest_region = selected_id
                st.success(f"Destination set to {selected_name}!")
                
    with col2:
        # Radar chart for the 3 axes
        axes = profile["axes"]
        fig_radar = go.Figure(data=go.Scatterpolar(
            r=[axes["scfa_proxy"], axes["westernization_score"], axes["diversity_proxy"]],
            theta=['SCFA Proxy', 'Westernization Score', 'Diversity Proxy'],
            fill='toself',
            name=selected_name
        ))
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 1])
            ),
            showlegend=False,
            title=f"Functional Axes: {selected_name}",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(fig_radar, use_container_width=True)

def render_ai_nutritionist(atlas_data):
    st.header("Function 3: Nutritionist")
    st.markdown("A highly specific, scientific deep-dive into your culinary microbial transition, powered by OpenAI API.")
    
    if not st.session_state.origin_region or not st.session_state.dest_region:
        st.warning("Please set both an Origin and a Destination region in the Global Atlas first!")
        return
        
    orig_profile = atlas_data[st.session_state.origin_region]
    dest_profile = atlas_data[st.session_state.dest_region]
    
    st.subheader("Plan Parameters")
    
    col1, col2 = st.columns(2)
    with col1:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="Enter your OpenAI API key (optional if set in env)")
    with col2:
        health_goal = st.selectbox("Your Primary Health Goal", [
            "Maximize SCFA Production (Gut Barrier Focus)", 
            "Boost Overall Microbial Diversity", 
            "Maintain Traditional Niche (Resist Westernization)",
            "Reduce Inflammation"
        ])
        
    if st.button("Generate Personalized Nutrition Plan"):
        if not api_key and not os.environ.get("OPENAI_API_KEY"):
            st.error("Please provide an OpenAI API key or set OPENAI_API_KEY in your environment.")
            return
            
        with st.spinner("Analyzing culinary shifts and generating personalized recommendations..."):
            try:
                # Initialize client
                client = OpenAI(api_key=api_key if api_key else os.environ.get("OPENAI_API_KEY"))
                
                # Fetch risks if available
                risks = st.session_state.get("identified_risks", [])
                risk_str = ", ".join(risks).replace("_", " ") if risks else "None specifically identified."
                
                orig_country = orig_profile["region_name"]
                dest_country = dest_profile["region_name"]
                
                prompt = f"""
You are an expert microbiome nutritionist and clinical microbiologist.
Your client is moving from {orig_country} to {dest_country}.
Their primary health goal during this transition is: {health_goal}.
Current microbiome risks flagged by their transition simulator: {risk_str}.

Provide a highly specific, scientific, and quantitative nutrition plan.
Your response MUST include the following structured sections:

1. Culinary Shift Analysis: Briefly contrast the common cuisines and staple foods in {orig_country} versus {dest_country}.
2. Microbiome Impact (Table format): Create a markdown table identifying specific macro/micro-nutrient shifts (e.g., fiber types, resistant starches, fat profiles) and their exact physiological effects on key taxa (like Bacteroides, Prevotella, and specific SCFA producers like Faecalibacterium or Roseburia). Use columns: Nutrient Shift, Affected Taxa, Physiological Effect.
3. Intermediary Foods (Table format): Suggest 3-4 specific bridging foods or meal concepts available in {dest_country} that ease the microbiome transition while satisfying the palate. Use columns: Bridging Food, Microbiome Benefit, Culinary Context.
4. Quantitative Action Plan: Provide 3 concrete, quantitative dietary targets to achieve the "{health_goal}" (e.g., "consume 15g of inulin per day from chicory root", "eat 300g of fermented foods per week"). Use checklists or visually distinct formatting.

Format the output clearly using markdown headings, rich tables, bullet points, and bold text for scientific precision. Be actionable, down-to-earth, and highly specific. Do not use generic advice like "eat more vegetables."
"""
                
                response = client.responses.create(
                    model='gpt-5-mini',
                    input=prompt,
                    tools=[{"type": "web_search"}]
                )
                
                st.success("Plan Generated Successfully!")
                st.markdown("---")
                st.markdown(response.output_text)
                
            except Exception as e:
                st.error(f"Error generating plan: {e}")

if __name__ == "__main__":
    main()
