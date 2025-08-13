"""
Local Health Tracker - MANAK Inspire Award Submission
A community health monitoring system for tracking symptoms and detecting outbreaks
Author: Created for MANAK Inspire Award
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from io import BytesIO
import base64

# Configure Streamlit page
st.set_page_config(
    page_title="Local Health Tracker",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for youth-friendly design
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .alert-banner {
        background: linear-gradient(90deg, #ff6b6b 0%, #ee5a24 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
        font-weight: bold;
        text-align: center;
    }
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
    .metric-card {
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Data file configuration
DATA_FILE = "symptom_log.csv"
OUTBREAK_THRESHOLD = 10  # Configurable threshold for outbreak detection
OUTBREAK_DAYS = 7  # Days to look back for outbreak detection

def initialize_data_file():
    """Initialize CSV file with headers if it doesn't exist"""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            'date', 'age_group', 'area', 'duration', 'symptoms', 'severity', 'timestamp'
        ])
        df.to_csv(DATA_FILE, index=False)

def load_data():
    """Load symptom data from CSV file"""
    try:
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except:
        return pd.DataFrame(columns=[
            'date', 'age_group', 'area', 'duration', 'symptoms', 'severity', 'timestamp'
        ])

def log_entry(date, age_group, area, duration, symptoms, severity):
    """Log a new health entry to the CSV file"""
    new_entry = {
        'date': date.strftime('%Y-%m-%d'),
        'age_group': age_group,
        'area': area,
        'duration': duration,
        'symptoms': ', '.join(symptoms),
        'severity': severity,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Append to CSV
    df_new = pd.DataFrame([new_entry])
    if os.path.exists(DATA_FILE):
        df_new.to_csv(DATA_FILE, mode='a', header=False, index=False)
    else:
        df_new.to_csv(DATA_FILE, index=False)
    
    return True

def analyze_trends(df):
    """Analyze health trends from the data"""
    if df.empty:
        return {}, {}, {}
    
    # Get last 7 days data
    last_week = datetime.now() - timedelta(days=7)
    recent_data = df[df['date'] >= last_week]
    
    # Symptom frequency analysis
    all_symptoms = []
    for symptoms_str in recent_data['symptoms'].dropna():
        symptoms_list = [s.strip() for s in str(symptoms_str).split(',')]
        all_symptoms.extend(symptoms_list)
    
    symptom_counts = pd.Series(all_symptoms).value_counts()
    
    # Age group analysis
    age_distribution = recent_data['age_group'].value_counts()
    
    # Daily trends for top symptoms
    top_symptoms = symptom_counts.head(3).index.tolist()
    daily_trends = {}
    
    for symptom in top_symptoms:
        daily_counts = []
        for i in range(30):  # Last 30 days
            check_date = datetime.now() - timedelta(days=i)
            day_data = df[df['date'].dt.date == check_date.date()]
            count = sum(symptom.lower() in str(row['symptoms']).lower() 
                       for _, row in day_data.iterrows())
            daily_counts.append(count)
        
        daily_trends[symptom] = list(reversed(daily_counts))
    
    return symptom_counts, age_distribution, daily_trends

def detect_outbreaks(df):
    """Rule-based outbreak detection system"""
    outbreaks = []
    
    if df.empty:
        return outbreaks
    
    # Check last OUTBREAK_DAYS for fever cases by area
    cutoff_date = datetime.now() - timedelta(days=OUTBREAK_DAYS)
    recent_data = df[df['date'] >= cutoff_date]
    
    # Group by area and check for fever cases
    for area in recent_data['area'].unique():
        area_data = recent_data[recent_data['area'] == area]
        fever_cases = 0
        
        for _, row in area_data.iterrows():
            if 'fever' in str(row['symptoms']).lower():
                fever_cases += 1
        
        if fever_cases >= OUTBREAK_THRESHOLD:
            outbreaks.append({
                'area': area,
                'cases': fever_cases,
                'symptom': 'Fever',
                'days': OUTBREAK_DAYS
            })
    
    return outbreaks

def create_download_link(df, filename, link_text):
    """Create a download link for CSV data"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

def main():
    """Main application function"""
    
    # Initialize data file
    initialize_data_file()
    
    # App Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Local Health Tracker</h1>
        <p><strong>MANAK Inspire Award Submission</strong></p>
        <p>Empowering communities through collaborative health monitoring</p>
        <p>📍 Track symptoms • 📊 Visualize trends • 🚨 Detect outbreaks • 📚 Learn & prevent</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.selectbox(
        "Choose a section:",
        ["🏠 Home & Data Entry", "📊 Health Dashboard", "🚨 Outbreak Alerts", "📚 Health Education", "📥 Data Export"]
    )
    
    # Load existing data
    df = load_data()
    
    if page == "🏠 Home & Data Entry":
        st.header("📝 Log Your Daily Health Status")
        st.write("Help your community by anonymously sharing your health information.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Data entry form
            with st.form("health_entry_form"):
                st.subheader("Health Information Form")
                
                # Form fields
                entry_date = st.date_input(
                    "📅 Date of symptoms:",
                    value=datetime.now().date(),
                    max_value=datetime.now().date()
                )
                
                age_group = st.selectbox(
                    "👥 Age Group:",
                    ["Child (0-12)", "Teen/Youth (13-24)", "Adult (25-59)", "Senior (60+)"]
                )
                
                area = st.text_input(
                    "📍 Area/Neighborhood:",
                    placeholder="Enter your area (e.g., Koramangala, MG Road)"
                )
                
                duration = st.selectbox(
                    "⏱️ Duration of symptoms:",
                    ["<1 day", "1-3 days", "4-7 days", ">1 week"]
                )
                
                symptoms = st.multiselect(
                    "🤒 Select your symptoms:",
                    ["Fever", "Cough", "Headache", "Fatigue", "Sore throat", 
                     "Running nose", "Muscle pain", "Rash", "Stomach pain", 
                     "Nausea", "Diarrhea", "Loss of taste/smell", "Breathing difficulty"]
                )
                
                severity = st.slider(
                    "📊 Severity (1=Mild, 10=Severe):",
                    min_value=1, max_value=10, value=5
                )
                
                submitted = st.form_submit_button("🚀 Submit Health Data")
                
                if submitted:
                    if area and symptoms:
                        success = log_entry(entry_date, age_group, area, duration, symptoms, severity)
                        if success:
                            st.success("✅ Thank you! Your health data has been recorded anonymously.")
                            st.balloons()
                        else:
                            st.error("❌ Error saving data. Please try again.")
                    else:
                        st.warning("⚠️ Please fill in your area and select at least one symptom.")
        
        with col2:
            st.markdown("""
            <div class="info-card">
                <h3>🎯 Why Track Health?</h3>
                <p>• Early outbreak detection</p>
                <p>• Community health awareness</p>
                <p>• Better healthcare planning</p>
                <p>• Anonymous & secure</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show recent stats
            if not df.empty:
                total_entries = len(df)
                recent_entries = len(df[df['date'] >= datetime.now() - timedelta(days=7)])
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📈 Community Stats</h4>
                    <p>Total Reports: {total_entries}</p>
                    <p>This Week: {recent_entries}</p>
                </div>
                """, unsafe_allow_html=True)
    
    elif page == "📊 Health Dashboard":
        st.header("📊 Community Health Dashboard")
        
        if df.empty:
            st.warning("📭 No data available yet. Please add some health entries first!")
            return
        
        # Analyze trends
        symptom_counts, age_distribution, daily_trends = analyze_trends(df)
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📋 Total Reports", len(df))
        
        with col2:
            recent_count = len(df[df['date'] >= datetime.now() - timedelta(days=7)])
            st.metric("📅 This Week", recent_count)
        
        with col3:
            active_areas = df['area'].nunique()
            st.metric("🏘️ Active Areas", active_areas)
        
        with col4:
            if not symptom_counts.empty:
                top_symptom = symptom_counts.index[0]
                st.metric("🔥 Top Symptom", top_symptom)
        
        # Chart 1: Symptom frequency (Bar chart)
        st.subheader("📊 Most Common Symptoms (Last 7 Days)")
        if not symptom_counts.empty:
            fig1 = px.bar(
                x=symptom_counts.index[:10], 
                y=symptom_counts.values[:10],
                title="Symptom Frequency",
                color=symptom_counts.values[:10],
                color_continuous_scale="viridis"
            )
            fig1.update_layout(
                xaxis_title="Symptoms",
                yaxis_title="Number of Reports",
                showlegend=False
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        # Chart 2: Daily trends (Line chart)
        st.subheader("📈 Symptom Trends (Last 30 Days)")
        if daily_trends:
            fig2 = go.Figure()
            dates = [(datetime.now() - timedelta(days=29-i)).strftime('%m-%d') for i in range(30)]
            
            for symptom, counts in daily_trends.items():
                fig2.add_trace(go.Scatter(
                    x=dates, y=counts, mode='lines+markers',
                    name=symptom, line=dict(width=3)
                ))
            
            fig2.update_layout(
                title="Daily Symptom Trends",
                xaxis_title="Date",
                yaxis_title="Number of Reports",
                hovermode='x unified'
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Chart 3: Age distribution (Pie chart)
        st.subheader("👥 Age Group Distribution")
        if not age_distribution.empty:
            fig3 = px.pie(
                values=age_distribution.values,
                names=age_distribution.index,
                title="Reports by Age Group",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig3.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig3, use_container_width=True)
        
        # Area-wise breakdown
        st.subheader("🗺️ Area-wise Health Reports")
        area_stats = df.groupby('area').size().sort_values(ascending=False)
        if not area_stats.empty:
            fig4 = px.bar(
                x=area_stats.values,
                y=area_stats.index,
                orientation='h',
                title="Reports by Area",
                color=area_stats.values,
                color_continuous_scale="blues"
            )
            fig4.update_layout(
                xaxis_title="Number of Reports",
                yaxis_title="Area",
                showlegend=False
            )
            st.plotly_chart(fig4, use_container_width=True)
    
    elif page == "🚨 Outbreak Alerts":
        st.header("🚨 Outbreak Detection & Alerts")
        
        # Configuration section
        with st.expander("⚙️ Alert Configuration"):
            col1, col2 = st.columns(2)
            with col1:
                threshold = st.number_input(
                    "Outbreak Threshold (minimum cases):",
                    min_value=5, max_value=50, value=OUTBREAK_THRESHOLD
                )
            with col2:
                days_back = st.number_input(
                    "Days to analyze:",
                    min_value=3, max_value=14, value=OUTBREAK_DAYS
                )
        
        # Detect outbreaks
        outbreaks = detect_outbreaks(df)
        
        if outbreaks:
            st.markdown("### 🚨 ACTIVE OUTBREAK ALERTS")
            
            for outbreak in outbreaks:
                st.markdown(f"""
                <div class="alert-banner">
                    <h3>⚠️ OUTBREAK DETECTED</h3>
                    <p><strong>Location:</strong> {outbreak['area']}</p>
                    <p><strong>Symptom:</strong> {outbreak['symptom']}</p>
                    <p><strong>Cases:</strong> {outbreak['cases']} in {outbreak['days']} days</p>
                    <p><strong>Threshold Exceeded:</strong> {outbreak['cases']} ≥ {threshold}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Recommended actions
            st.markdown("### 🎯 Recommended Actions")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 🏥 For Individuals:
                - Consult a doctor immediately
                - Stay hydrated and rest
                - Avoid crowded places
                - Wear masks in public
                - Monitor symptoms closely
                """)
            
            with col2:
                st.markdown("""
                #### 🏛️ For Community:
                - Inform local health authorities
                - Increase sanitization measures
                - Share health information
                - Support affected families
                - Follow official guidelines
                """)
        
        else:
            st.success("✅ No outbreak alerts at this time")
            st.info("🛡️ The system continuously monitors for unusual patterns in symptom reports.")
            
            # Show monitoring stats
            if not df.empty:
                st.subheader("📊 Monitoring Statistics")
                
                recent_data = df[df['date'] >= datetime.now() - timedelta(days=days_back)]
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    fever_cases = sum('fever' in str(row['symptoms']).lower() 
                                    for _, row in recent_data.iterrows())
                    st.metric("🌡️ Fever Cases", fever_cases)
                
                with col2:
                    st.metric("🏘️ Areas Monitored", recent_data['area'].nunique())
                
                with col3:
                    st.metric("📅 Days Analyzed", days_back)
    
    elif page == "📚 Health Education":
        st.header("📚 Health Education & Resources")
        
        tab1, tab2, tab3 = st.tabs(["🚨 Emergency Signs", "🧼 Prevention Tips", "📋 Health Guidelines"])
        
        with tab1:
            st.subheader("⚠️ When to See a Doctor Immediately")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 🚨 Seek Immediate Medical Care If:
                - **High fever** (>101°F/38.3°C) for >3 days
                - **Difficulty breathing** or chest pain
                - **Severe dehydration** (dizziness, no urination)
                - **Persistent vomiting** unable to keep fluids down
                - **Severe headache** with neck stiffness
                - **Rash** with fever
                - **Confusion** or altered mental state
                """)
            
            with col2:
                st.markdown("""
                #### 📞 Emergency Contacts
                - **National Emergency:** 108
                - **Medical Emergency:** 102
                - **Poison Control:** 1066
                - **Mental Health:** 9152987821
                
                #### 🏥 Nearby Hospitals
                Update this section with local hospital information
                """)
        
        with tab2:
            st.subheader("🛡️ Disease Prevention Tips")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 🧼 Personal Hygiene
                - Wash hands frequently with soap (20+ seconds)
                - Use hand sanitizer (60%+ alcohol)
                - Avoid touching face, eyes, nose
                - Cover coughs and sneezes
                - Clean frequently touched surfaces
                """)
                
                st.markdown("""
                #### 💧 Stay Healthy
                - Drink 8-10 glasses of water daily
                - Eat balanced diet with fruits/vegetables
                - Get 7-8 hours of sleep
                - Exercise regularly (30 min/day)
                - Manage stress through relaxation
                """)
            
            with col2:
                st.markdown("""
                #### 🏠 Home Safety
                - Maintain clean living environment
                - Ensure proper ventilation
                - Store food safely
                - Use clean drinking water
                - Keep first aid kit ready
                """)
                
                st.markdown("""
                #### 👨‍👩‍👧‍👦 Community Health
                - Share health information responsibly
                - Support sick community members
                - Report unusual health patterns
                - Participate in health initiatives
                - Follow public health guidelines
                """)
        
        with tab3:
            st.subheader("📋 Health Guidelines & Resources")
            
            st.markdown("""
            #### 🌡️ Common Symptoms Guide
            
            | Symptom | Possible Causes | When to Worry | Home Care |
            |---------|----------------|---------------|-----------|
            | Fever | Infection, heat exhaustion | >3 days, >101°F | Rest, fluids, paracetamol |
            | Cough | Cold, allergies, infection | Blood, breathing issues | Honey, warm water |
            | Headache | Tension, dehydration | Severe, with neck pain | Rest, hydrate |
            | Fatigue | Poor sleep, stress | Persistent >2 weeks | Regular sleep, exercise |
            | Stomach pain | Food, stress, infection | Severe, persistent | Light diet, fluids |
            """)
            
            st.markdown("""
            #### 📱 Useful Health Apps & Websites
            - **Aarogya Setu:** Government health app
            - **MyGov:** Official government health updates  
            - **WHO:** World Health Organization resources
            - **Local Health Department:** Check your state website
            """)
    
    elif page == "📥 Data Export":
        st.header("📥 Data Export & Reports")
        
        if df.empty:
            st.warning("📭 No data available for export.")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Export Options")
            
            # CSV download
            st.markdown("#### 📄 Download Raw Data")
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Complete Dataset (CSV)",
                data=csv_data,
                file_name=f"health_data_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # Filtered export options
            st.markdown("#### 🔍 Filtered Exports")
            
            date_range = st.date_input(
                "Select date range:",
                value=[datetime.now().date() - timedelta(days=30), datetime.now().date()],
                max_value=datetime.now().date()
            )
            
            if len(date_range) == 2:
                filtered_df = df[(df['date'].dt.date >= date_range[0]) & 
                               (df['date'].dt.date <= date_range[1])]
                
                if not filtered_df.empty:
                    filtered_csv = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="⬇️ Download Filtered Data",
                        data=filtered_csv,
                        file_name=f"filtered_health_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
        
        with col2:
            st.subheader("📈 Weekly Health Summary")
            
            # Generate summary statistics
            recent_df = df[df['date'] >= datetime.now() - timedelta(days=7)]
            
            if not recent_df.empty:
                st.markdown("#### 📊 This Week's Statistics")
                
                # Summary metrics
                total_reports = len(recent_df)
                unique_areas = recent_df['area'].nunique()
                avg_severity = recent_df['severity'].mean()
                
                st.write(f"**Total Reports:** {total_reports}")
                st.write(f"**Areas Covered:** {unique_areas}")
                st.write(f"**Average Severity:** {avg_severity:.1f}/10")
                
                # Top symptoms
                all_symptoms = []
                for symptoms_str in recent_df['symptoms'].dropna():
                    symptoms_list = [s.strip() for s in str(symptoms_str).split(',')]
                    all_symptoms.extend(symptoms_list)
                
                if all_symptoms:
                    symptom_counts = pd.Series(all_symptoms).value_counts().head(5)
                    st.markdown("**Top 5 Symptoms:**")
                    for symptom, count in symptom_counts.items():
                        st.write(f"• {symptom}: {count} reports")
                
                # Age distribution
                age_dist = recent_df['age_group'].value_counts()
                st.markdown("**Age Group Distribution:**")
                for age_group, count in age_dist.items():
                    percentage = (count / total_reports) * 100
                    st.write(f"• {age_group}: {count} ({percentage:.1f}%)")
            
            else:
                st.info("No data available for the past week.")
        
        # Data insights
        st.subheader("🧠 Data Insights")
        
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("""
                <div class="metric-card">
                    <h4>📅 Data Coverage</h4>
                    <p>First Report: """ + df['date'].min().strftime('%Y-%m-%d') + """</p>
                    <p>Latest Report: """ + df['date'].max().strftime('%Y-%m-%d') + """</p>
                    <p>Total Days: """ + str((df['date'].max() - df['date'].min()).days + 1) + """</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="metric-card">
                    <h4>🏘️ Geographic Coverage</h4>
                    <p>Total Areas: """ + str(df['area'].nunique()) + """</p>
                    <p>Most Active: """ + str(df['area'].mode().iloc[0] if not df['area'].mode().empty else 'N/A') + """</p>
                    <p>Avg Reports/Area: """ + str(round(len(df) / df['area'].nunique(), 1)) + """</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                most_common_duration = df['duration'].mode().iloc[0] if not df['duration'].mode().empty else 'N/A'
                st.markdown("""
                <div class="metric-card">
                    <h4>⏱️ Symptom Duration</h4>
                    <p>Most Common: """ + most_common_duration + """</p>
                    <p>Avg Severity: """ + str(round(df['severity'].mean(), 1)) + """/10</p>
                    <p>High Severity: """ + str(len(df[df['severity'] >= 7])) + """ reports</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
