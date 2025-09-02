import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.express as px
from datetime import date

# Load environment variables
load_dotenv()

# Initialize Supabase
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# -------------------------
# DATABASE FUNCTIONS
# -------------------------

# PROJECTS
def get_projects():
    response = supabase.table('projects').select('*').execute()
    return response.data

def add_project(project_data):
    return supabase.table('projects').insert(project_data).execute()

# SESSIONS
def get_sessions(project_code=None):
    query = supabase.table('sessions').select('*')
    if project_code:
        query = query.eq('project_code', project_code)
    response = query.execute()
    return response.data

def add_session(session_data):
    return supabase.table('sessions').insert(session_data).execute()

# PARTICIPANTS
def get_participants(session_code=None):
    query = supabase.table('session_participants').select('*')
    if session_code:
        query = query.eq('session_code', session_code)
    response = query.execute()
    return response.data

def add_participant(participant_data):
    return supabase.table('session_participants').insert(participant_data).execute()

# FEEDBACK
def add_feedback(feedback_data):
    return supabase.table('participant_feedback').insert(feedback_data).execute()

def get_feedback(session_code=None):
    query = supabase.table('participant_feedback').select('*')
    if session_code:
        query = query.eq('session_code', session_code)
    response = query.execute()
    return response.data

# IMPACT
def add_impact(impact_data):
    return supabase.table('session_impact').insert(impact_data).execute()

def get_impact(session_code=None):
    query = supabase.table('session_impact').select('*')
    if session_code:
        query = query.eq('session_code', session_code)
    response = query.execute()
    return response.data

# -------------------------
# STREAMLIT APP
# -------------------------

st.set_page_config(page_title="SLS Session Tracker", layout="wide")
st.title("📊 SLS Project & Session Tracker")

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a page", [
    "Add Project", 
    "Add Session", 
    "Register Participant", 
    "Record Feedback", 
    "Record Impact", 
    "Session Analytics", 
    "Dashboard"
])

# -------------------------
# PAGE: ADD PROJECT
# -------------------------
if page == "Add Project":
    st.header("Add New Project")
    with st.form("add_project_form"):
        project_name = st.text_input("Project Name")
        project_code = st.text_input("Project Code (unique)")
        submitted = st.form_submit_button("Add Project")
        if submitted:
            if project_name and project_code:
                try:
                    add_project({'project_name': project_name, 'project_code': project_code})
                    st.success(f"Project '{project_name}' added successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.error("Fill in both Project Name and Project Code.")

# -------------------------
# PAGE: ADD SESSION
# -------------------------
elif page == "Add Session":
    st.header("Add Session to Project")
    projects = get_projects()
    if not projects:
        st.warning("Add a project first.")
    else:
        project_options = {p['project_name']: p['project_code'] for p in projects}
        with st.form("add_session_form"):
            selected_project = st.selectbox("Select Project", list(project_options.keys()))
            session_name = st.text_input("Session Name")
            session_code = st.text_input("Session Code (unique)")
            session_date = st.date_input("Session Date", value=date.today())
            hours_delivered = st.number_input("Hours Delivered", min_value=0.0, step=0.5)
            facilitators = st.text_area("Facilitators (comma-separated)")
            submitted = st.form_submit_button("Add Session")
            if submitted:
                if session_name and session_code:
                    try:
                        add_session({
                            'session_name': session_name,
                            'session_code': session_code,
                            'project_code': project_options[selected_project],
                            'session_date': session_date.isoformat(),
                            'hours_delivered': hours_delivered,
                            'facilitators': facilitators
                        })
                        st.success(f"Session '{session_name}' added to project '{selected_project}'.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Provide session name and code.")

# -------------------------
# PAGE: REGISTER PARTICIPANT
# -------------------------
elif page == "Register Participant":
    st.header("Register Participant for a Session")
    sessions = get_sessions()
    if not sessions:
        st.warning("Add a session first.")
    else:
        session_options = {s['session_name']: s['session_code'] for s in sessions}
        with st.form("register_participant_form"):
            selected_session = st.selectbox("Select Session", list(session_options.keys()))
            participant_name = st.text_input("Participant Name")
            hours_contributed = st.number_input("Hours Contributed", min_value=0.0, step=0.5)
            submitted = st.form_submit_button("Register Participant")
            if submitted:
                if participant_name:
                    try:
                        add_participant({
                            'session_code': session_options[selected_session],
                            'participant_name': participant_name,
                            'hours_contributed': hours_contributed
                        })
                        st.success(f"Participant '{participant_name}' registered successfully.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("Participant name required.")

# -------------------------
# PAGE: RECORD FEEDBACK
# -------------------------
elif page == "Record Feedback":
    st.header("Record Feedback for Participants")
    sessions = get_sessions()
    if not sessions:
        st.warning("Add a session first.")
    else:
        session_options = {s['session_name']: s['session_code'] for s in sessions}
        selected_session = st.selectbox("Select Session", list(session_options.keys()))
        participants = get_participants(session_options[selected_session])
        if not participants:
            st.warning("Register participants first.")
        else:
            participant_options = [p['participant_name'] for p in participants]
            selected_participant = st.selectbox("Select Participant", participant_options)
            with st.form("feedback_form"):
                hours_contributed = st.number_input("Hours Contributed", min_value=0.0, step=0.5)
                knowledge_pre = st.slider("Knowledge Pre", 1, 5, 3)
                confidence_pre = st.slider("Confidence Pre", 1, 5, 3)
                knowledge_post = st.slider("Knowledge Post", 1, 5, 3)
                confidence_post = st.slider("Confidence Post", 1, 5, 3)
                action_step = st.checkbox("Action Step?")
                new_contact = st.checkbox("New Contact?")
                satisfaction = st.slider("Satisfaction", 1, 5, 3)
                nps = st.slider("NPS", 0, 10, 5)
                notes = st.text_area("Notes")
                submitted = st.form_submit_button("Submit Feedback")
                if submitted:
                    try:
                        add_feedback({
                            'session_code': session_options[selected_session],
                            'participant_name': selected_participant,
                            'hours_contributed': hours_contributed,
                            'knowledge_pre': knowledge_pre,
                            'confidence_pre': confidence_pre,
                            'knowledge_post': knowledge_post,
                            'confidence_post': confidence_post,
                            'action_step': action_step,
                            'new_contact': new_contact,
                            'satisfaction': satisfaction,
                            'nps': nps,
                            'notes': notes
                        })
                        st.success(f"Feedback recorded for {selected_participant}.")
                    except Exception as e:
                        st.error(f"Error: {e}")

# -------------------------
# PAGE: RECORD IMPACT
# -------------------------
elif page == "Record Impact":
    st.header("Record Session Impact")
    sessions = get_sessions()
    if not sessions:
        st.warning("Add a session first.")
    else:
        session_options = {s['session_name']: s['session_code'] for s in sessions}
        selected_session = st.selectbox("Select Session", list(session_options.keys()))
        with st.form("impact_form"):
            action_taken = st.checkbox("Action Taken?")
            new_contacts_formed = st.number_input("New Contacts Formed", min_value=0)
            individuals_impacted = st.number_input("Individuals Impacted", min_value=0)
            member_contributions = st.number_input("Member Contributions", min_value=0)
            engagement_hours = st.number_input("Engagement Hours", min_value=0.0, step=0.5)
            other_notes = st.text_area("Other Impact Notes")
            submitted = st.form_submit_button("Submit Impact")
            if submitted:
                try:
                    add_impact({
                        'session_code': session_options[selected_session],
                        'action_taken': action_taken,
                        'new_contacts_formed': new_contacts_formed,
                        'individuals_impacted': individuals_impacted,
                        'member_contributions': member_contributions,
                        'engagement_hours': engagement_hours,
                        'other_impact_notes': other_notes
                    })
                    st.success("Impact recorded successfully!")
                except Exception as e:
                    st.error(f"Error: {e}")

# -------------------------
# PAGE: SESSION ANALYTICS
# -------------------------
elif page == "Session Analytics":
    st.header("Session Analytics")
    sessions = get_sessions()
    if not sessions:
        st.warning("Add sessions first.")
    else:
        session_options = {s['session_name']: s['session_code'] for s in sessions}
        selected_session = st.selectbox("Select Session", list(session_options.keys()))
        
        feedback = get_feedback(session_options[selected_session])
        if feedback:
            df = pd.DataFrame(feedback)
            st.subheader("Participant Feedback Data")
            st.dataframe(df, use_container_width=True)
            
            # ------------------------
            # Compute KPIs
            # ------------------------
            df['knowledge_gain'] = df['knowledge_post'] - df['knowledge_pre']
            df['confidence_gain'] = df['confidence_post'] - df['confidence_pre']
            
            kpi1 = df['knowledge_gain'].mean()
            kpi2 = df['confidence_gain'].mean()
            kpi3 = df['action_step'].mean() * 100
            kpi4 = df['new_contact'].mean() * 100
            kpi5 = df['satisfaction'].mean()
            kpi6 = df['nps'].mean()
            kpi7 = df['hours_contributed'].sum()
            
            st.subheader("Session KPIs")
            st.markdown(f"""
            **Average Knowledge Gain:** {kpi1:.2f} / 4  
            **Average Confidence Gain:** {kpi2:.2f} / 4  
            **% Participants Taking Action:** {kpi3:.1f}%  
            **% Participants Making New Contacts:** {kpi4:.1f}%  
            **Average Satisfaction:** {kpi5:.2f} / 5  
            **Average NPS:** {kpi6:.2f} / 10  
            **Total Hours Contributed:** {kpi7:.1f} hrs
            """)
            
            # ------------------------
            # Visualizations
            # ------------------------
            
            # Knowledge Gain Distribution
            fig1 = px.histogram(df, x='knowledge_gain', nbins=5, title="Knowledge Gain Distribution")
            st.plotly_chart(fig1, use_container_width=True)
            
            # Confidence Gain Distribution
            fig2 = px.histogram(df, x='confidence_gain', nbins=5, title="Confidence Gain Distribution")
            st.plotly_chart(fig2, use_container_width=True)
            
            # Action Step & New Contacts
            action_counts = df[['action_step', 'new_contact']].sum()
            fig3 = px.bar(x=action_counts.index, y=action_counts.values, title="Actions & Networking")
            st.plotly_chart(fig3, use_container_width=True)
            
            # Satisfaction & NPS distributions
            fig4 = px.histogram(df, x='satisfaction', nbins=5, title="Satisfaction Distribution")
            fig5 = px.histogram(df, x='nps', nbins=10, title="NPS Distribution")
            st.plotly_chart(fig4, use_container_width=True)
            st.plotly_chart(fig5, use_container_width=True)
            
        else:
            st.info("No feedback yet for this session.")
elif page == "Dashboard":
    st.header("Overall Dashboard")
    
    projects = get_projects()
    sessions = get_sessions()
    
    # Feedback
    feedback = get_feedback()
    
    if feedback:
        df_feedback = pd.DataFrame(feedback)
        
        st.subheader("Project-Level KPIs")
        project_codes = df_feedback['session_code'].map(lambda x: next((s['project_code'] for s in sessions if s['session_code']==x), None))
        df_feedback['project_code'] = project_codes
        
        project_kpis = df_feedback.groupby('project_code').agg(
            avg_knowledge_gain=('knowledge_post', lambda x: (x - df_feedback['knowledge_pre']).mean()),
            avg_confidence_gain=('confidence_post', lambda x: (x - df_feedback['confidence_pre']).mean()),
            pct_action_step=('action_step', 'mean'),
            pct_new_contact=('new_contact', 'mean'),
            avg_satisfaction=('satisfaction', 'mean'),
            avg_nps=('nps', 'mean'),
            total_hours=('hours_contributed', 'sum')
        ).reset_index()
        
        # Convert percentages
        project_kpis['pct_action_step'] *= 100
        project_kpis['pct_new_contact'] *= 100
        
        st.dataframe(project_kpis, use_container_width=True)
