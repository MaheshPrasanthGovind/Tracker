"""
Local Health Tracker - MANAK Inspire Award Submission
A community health monitoring system with authentication and admin management
Author: Created for MANAK Inspire Award
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import yaml
from yaml.loader import SafeLoader
import hashlib

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
    .login-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 2rem 0;
        color: white;
        text-align: center;
    }
    .admin-panel {
        background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
CREDENTIALS_FILE = "credentials.yaml"
DATA_FILE = "symptom_log.csv"
OUTBREAK_THRESHOLD = 10
OUTBREAK_DAYS = 7

# Authentication Functions
def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_default_credentials():
    """Create default credentials.yaml file if it doesn't exist"""
    if not os.path.exists(CREDENTIALS_FILE):
        config = {
            'credentials': {
                'usernames': {
                    'user1': {
                        'name': 'Health User',
                        'password': hash_password('userpass123'),
                        'role': 'user'
                    },
                    'admin1': {
                        'name': 'Health Admin',
                        'password': hash_password('adminpass123'),
                        'role': 'admin'
                    }
                }
            },
            'cookie': {
                'name': 'local_health_tracker',
                'key': 'health_tracker_key_2024',
                'expiry_days': 1
            }
        }
        
        with open(CREDENTIALS_FILE, 'w') as file:
            yaml.dump(config, file, default_flow_style=False)
        
        return config
    return None

def simple_authenticate(username, password):
    """Simple authentication without external libraries"""
    if not os.path.exists(CREDENTIALS_FILE):
        create_default_credentials()
    
    with open(CREDENTIALS_FILE, 'r') as file:
        config = yaml.load(file, Loader=SafeLoader)
    
    hashed_input = hash_password(password)
    
    if username in config['credentials']['usernames']:
        stored_password = config['credentials']['usernames'][username]['password']
        if hashed_input == stored_password:
            return True, config['credentials']['usernames'][username]
    
    return False, None

def check_authentication():
    """Handle user authentication"""
    # Check if already authenticated
    if st.session_state.get('authenticated', False):
        return True, st.session_state['name'], st.session_state['username'], st.session_state['user_role']
    
    # Show login form
    st.markdown("""
    <div class="login-container">
        <h1>🔐 Local Health Tracker</h1>
        <h3>MANAK Inspire Award Submission</h3>
        <p>Please Login to Continue</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")
        
        if login_button:
            is_valid, user_data = simple_authenticate(username, password)
            
            if is_valid:
                st.session_state['authenticated'] = True
                st.session_state['name'] = user_data['name']
                st.session_state['username'] = username
                st.session_state['user_role'] = user_data.get('role', 'user')
                st.success("✅ Login successful!")
                st.rerun()
            else:
                st.error("❌ Invalid username or password")
    
    # Show default credentials
    with st.expander("🔑 Default Login Credentials"):
        st.info("""
        **Regular User:** username: `user1`, password: `userpass123`  
        **Admin User:** username: `admin1`, password: `adminpass123`
        """)
    
    return False, None, None, None

# Data Management Functions
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
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            if not df.empty:
                df['date'] = pd.to_datetime(df['date'])
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        else:
            return pd.DataFrame(columns=[
                'date', 'age_group', 'area', 'duration', 'symptoms', 'severity', 'timestamp'
            ])
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
    
    # Get last 7 days data for symptom frequency
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
    
    # Daily trends for top symptoms over last 30 days
    top_symptoms = symptom_counts.head(3).index.tolist() if not symptom_counts.empty else []
    daily_trends = {}
    
    for symptom in top_symptoms:
        daily_counts = []
        for i in range(30):
            check_date = (datetime.now() - timedelta(days=29-i)).date()
            day_data = df[df['date'].dt.date == check_date]
            count = sum(symptom.lower() in str(row['symptoms']).lower() 
                       for _, row in day_data.iterrows())
            daily_counts.append(count)
        
        daily_trends[symptom] = daily_counts
    
    return symptom_counts, age_distribution, daily_trends

def detect_outbreaks(df):
    """Rule-based outbreak detection system"""
    outbreaks = []
    
    if df.empty:
        return outbreaks
    
    cutoff_date = datetime.now() - timedelta(days=OUTBREAK_DAYS)
    recent_data = df[df['date'] >= cutoff_date]
    
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

# Admin Panel Functions
def show_admin_panel():
    """Display admin panel for data management"""
    st.markdown("""
    <div class="admin-panel">
        <h2>🔧 Admin Control Panel</h2>
        <p>Manage health data, view analytics, and maintain system integrity</p>
    </div>
    """, unsafe_allow_html=True)
    
    df = load_data()
    
    if df.empty:
        st.warning("📭 No health data available in the system")
        return
    
    # Admin statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📊 Total Records", len(df))
    
    with col2:
        recent_count = len(df[df['date'] >= datetime.now() - timedelta(days=7)])
        st.metric("📅 This Week", recent_count)
    
    with col3:
        st.metric("🏘️ Areas Covered", df['area'].nunique())
    
    with col4:
        if len(df) > 0:
            avg_severity = df['severity'].mean()
            st.metric("📊 Avg Severity", f"{avg_severity:.1f}/10")
    
    # Data management section
    st.subheader("📋 Health Data Management")
    
    tab1, tab2 = st.tabs(["🔍 View Data", "🗑️ Delete Records"])
    
    with tab1:
        st.write("**All Health Records:**")
        
        # Add filters
        col1, col2 = st.columns(2)
        
        with col1:
            selected_areas = st.multiselect(
                "Filter by Area:",
                options=df['area'].unique(),
                default=df['area'].unique()
            )
        
        with col2:
            if not df.empty:
                date_range = st.date_input(
                    "Date Range:",
                    value=[df['date'].min().date(), df['date'].max().date()],
                    min_value=df['date'].min().date(),
                    max_value=df['date'].max().date()
                )
            else:
                date_range = [datetime.now().date(), datetime.now().date()]
        
        # Apply filters
        filtered_df = df.copy()
        if selected_areas:
            filtered_df = filtered_df[filtered_df['area'].isin(selected_areas)]
        
        if len(date_range) == 2:
            filtered_df = filtered_df[
                (filtered_df['date'].dt.date >= date_range[0]) & 
                (filtered_df['date'].dt.date <= date_range[1])
            ]
        
        st.dataframe(
            filtered_df.sort_values('timestamp', ascending=False),
            use_container_width=True,
            height=400
        )
    
    with tab2:
        st.write("**Delete Health Records:**")
        st.warning("⚠️ **Caution:** Record deletion is permanent and cannot be undone!")
        
        if not df.empty:
            # Simple deletion by index
            st.write("Enter row numbers to delete (comma-separated):")
            delete_indices = st.text_input("Row numbers (0, 1, 2, etc.):", "")
            
            if delete_indices:
                try:
                    indices_list = [int(x.strip()) for x in delete_indices.split(',')]
                    valid_indices = [i for i in indices_list if 0 <= i < len(df)]
                    
                    if valid_indices:
                        st.error(f"⚠️ You are about to delete {len(valid_indices)} records")
                        
                        if st.button("🗑️ Confirm Delete", type="primary"):
                            df_updated = df.drop(df.index[valid_indices])
                            df_updated.to_csv(DATA_FILE, index=False)
                            st.success(f"✅ Successfully deleted {len(valid_indices)} records")
                            st.rerun()
                except ValueError:
                    st.error("Please enter valid row numbers separated by commas")

def main():
    """Main application function"""
    
    # Initialize data file
    initialize_data_file()
    
    # Authentication check
    is_authenticated, name, username, user_role = check_authentication()
    
    if not is_authenticated:
        return
    
    # Show user info and logout in sidebar
    with st.sidebar:
        st.success(f"👋 Welcome, **{name}**!")
        st.info(f"🔑 Role: **{user_role.title()}**")
        
        if st.button("🚪 Logout"):
            st.session_state['authenticated'] = False
            for key in ['name', 'username', 'user_role']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    # App Header
    st.markdown(f"""
    <div class="main-header">
        <h1>🏥 Local Health Tracker</h1>
        <p><strong>MANAK Inspire Award Submission</strong></p>
        <p>Logged in as: <strong>{name}</strong> ({user_role.title()})</p>
        <p>📍 Track symptoms • 📊 Visualize trends • 🚨 Detect outbreaks • 📚 Learn & prevent</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    
    navigation_options = [
        "🏠 Home & Data Entry", 
        "📊 Health Dashboard", 
        "🚨 Outbreak Alerts", 
        "📚 Health Education", 
        "📥 Data Export"
    ]
    
    # Add admin panel for admin users
    if user_role == 'admin':
        navigation_options.append("🔧 Admin Panel")
    
    page = st.sidebar.selectbox("Choose a section:", navigation_options)
    
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
        
        # Chart 1: Symptom frequency
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
        
        # Chart 2: Daily trends
        st.subheader("📈 Symptom Trends (Last 30 Days)")
        if daily_trends:
            fig2 = go.Figure()
            dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(29, -1, -1)]
            
            for symptom, counts in daily_trends.items():
                fig2.add_trace(go.Scatter(
                    x=dates, y=counts, mode='lines+markers',
                    name=symptom, line=dict(width=3)
                ))
            
            fig2.update_layout(
                title="Daily Symptom Trends",
                xaxis_title="Date",
                yaxis_title="Number of Reports",
                hovermode='x unified',
                xaxis=dict(tickangle=45)
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Chart 3: Age distribution
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
        
        else:
            st.success("✅ No outbreak alerts at this time")
            st.info("🛡️ The system continuously monitors for unusual patterns in symptom reports.")
    
    elif page == "📚 Health Education":
        st.header("📚 Health Education & Resources")
        
        tab1, tab2, tab3 = st.tabs(["🚨 Emergency Signs", "🧼 Prevention Tips", "📋 Health Guidelines"])
        
        with tab1:
            st.subheader("⚠️ When to See a Doctor Immediately")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                #### 🚨 Emergency Warning Signs:
                - **High fever** (>101.3°F / 38.5°C) for more than 3 days
                - **Difficulty breathing** or shortness of breath
                - **Persistent chest pain** or pressure
                - **Severe headache** with neck stiffness
                - **Persistent vomiting** or inability to keep fluids down
                - **Signs of dehydration** (dizziness, dry mouth, little/no urination)
                - **Bluish lips or face**
                - **Severe abdominal pain**
                """)
            
            with col2:
                st.markdown("""
                #### 🏥 Seek Medical Care For:
                - **Fever** lasting more than 3 days
                - **Cough** with blood or lasting >2 weeks
                - **Rapid weight loss** without trying
                - **Persistent fatigue** affecting daily activities
                - **Changes in mental status**
                - **Severe dehydration symptoms**
                - **Worsening of chronic conditions**
                - **Any symptom causing concern**
                """)
            
            st.error("🆘 **Emergency Number: 108** (or your local emergency number)")
        
        with tab2:
            st.subheader("🛡️ Prevention is Better Than Cure")
            
            st.markdown("""
            #### 🧼 Basic Hygiene:
            - **Wash hands frequently** with soap for 20+ seconds
            - **Use hand sanitizer** when soap isn't available
            - **Cover coughs and sneezes** with elbow or tissue
            - **Avoid touching** face, eyes, nose with unwashed hands
            - **Clean and disinfect** frequently touched surfaces
            - **Maintain good oral hygiene**
            
            #### 🍎 Healthy Lifestyle:
            - **Balanced diet** with fruits and vegetables
            - **Regular exercise** and adequate sleep
            - **Stay hydrated** - drink plenty of water
            - **Manage stress** through relaxation techniques
            - **Avoid smoking and excessive alcohol**
            - **Get regular health check-ups**
            """)
        
        with tab3:
            st.subheader("📋 Health Guidelines & Resources")
            
            st.markdown("""
            #### 🌡️ Symptom Monitoring Guidelines:
            
            **🔴 High Priority (Seek immediate care):**
            - Temperature >101.3°F (38.5°C)
            - Difficulty breathing
            - Chest pain or pressure
            - Severe headache with stiff neck
            
            **🟡 Medium Priority (Monitor closely):**
            - Persistent cough >1 week
            - Moderate fever 100-101°F
            - Fatigue affecting daily activities
            - Mild breathing difficulty
            
            **🟢 Low Priority (Home care):**
            - Mild cold symptoms
            - Low-grade fever <100°F
            - Minor aches and pains
            - Mild fatigue
            """)
    
    elif page == "📥 Data Export":
        st.header("📥 Data Export & Reports")
        
        if df.empty:
            st.warning("📭 No data available for export")
            return
        
        st.subheader("📊 Export Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Custom Data Export")
            
            if not df.empty:
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="⬇️ Download All Data",
                    data=csv_data,
                    file_name=f"health_data_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv"
                )
                
                st.success(f"✅ Ready to export {len(df)} records")
        
        with col2:
            st.markdown("#### 📋 Summary Report")
            
            summary_text = f"""
HEALTH TRACKER SUMMARY REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW:
• Total Health Reports: {len(df)}
• Date Range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}
• Areas Covered: {df['area'].nunique()}

RECENT ACTIVITY (Last 7 days):
• Reports: {len(df[df['date'] >= datetime.now() - timedelta(days=7)])}

Note: This data is anonymized and aggregated for community health insights.
            """
            
            st.download_button(
                label="📋 Download Summary Report",
                data=summary_text,
                file_name=f"health_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
    
    elif page == "🔧 Admin Panel" and user_role == 'admin':
        show_admin_panel()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🏥 <strong>Local Health Tracker</strong> | MANAK Inspire Award 2024</p>
        <p>💡 <em>Innovation for Community Health • Empowering Data-Driven Healthcare</em></p>
        <p>⚠️ <strong>Disclaimer:</strong> This tool is for educational and monitoring purposes only. 
        Always consult healthcare professionals for medical advice and treatment.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
