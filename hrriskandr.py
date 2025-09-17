import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib
from fpdf import FPDF
from datetime import datetime
from io import BytesIO
import json
import docx
import PyPDF2
import re

# --- SECURE AUTHENTICATION ---
STORED_USERNAME = "admin"
STORED_PASSWORD_HASH = "ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f"  # SHA-256 of 'password123'

def authenticate(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return username == STORED_USERNAME and password_hash == STORED_PASSWORD_HASH

# --- REPORT GENERATION FUNCTION ---
def generate_report(df, title, metrics=None):
    """Generate downloadable Excel report with data and metrics"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)
        
        if metrics:
            pd.DataFrame(metrics.items()).to_excel(
                writer, sheet_name='Metrics', index=False, header=False
            )
        
        # Add chart if department data exists
        if 'Department' in df.columns:
            workbook = writer.book
            worksheet = writer.sheets['Data']
            
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'categories': f"=Data!$C$2:$C${len(df)+1}",
                'values': f"=Data!$A$2:$A${len(df)+1}",
            })
            worksheet.insert_chart('G2', chart)
    
    output.seek(0)
    return output

# --- TRAINING REPORT GENERATION FUNCTION ---
def generate_training_report(data, title, metrics):
    """Generate enhanced training report"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary sheet
        summary_df = pd.DataFrame(list(metrics.items()), columns=['Metric', 'Value'])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Detailed data
        data.to_excel(writer, sheet_name='Raw Data', index=False)
        
        # Department analysis
        dept_analysis = data.groupby('Department').agg({
            'TrainingsCompleted': ['mean', 'sum', 'count'],
            'AvgSkillGain': ['mean', 'std'],
            'ROI_per_training': 'mean'
        }).round(2)
        dept_analysis.to_excel(writer, sheet_name='Department Analysis')
        
        # Recommendations
        rec_df = pd.DataFrame({
            'Recommendation': [
                "Focus on departments with below-average ROI",
                "Increase training for high-potential employees",
                "Align training with performance goals",
                "Monitor skill application on the job"
            ],
            'Priority': ['High', 'Medium', 'Medium', 'High']
        })
        rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
    
    return output.getvalue()

# --- POLICY GENERATOR ---
def policy_generator():
    st.header("📝 Policy Generator")

    company_name = st.text_input("Company Name")
    country = st.selectbox("Country", ["Kenya", "USA", "UK", "India"])
    industry = st.text_input("Industry", "Technology")
    employee_count = st.number_input("Number of Employees", min_value=1, step=1)

    if st.button("🚀 Generate Policy Handbook"):
        st.success(f"Policy handbook generated for {company_name}")

        # Example generated text
        policy_text = f"""
        {company_name} - HR Policy Handbook
        Country: {country}
        Industry: {industry}
        Employees: {employee_count}

        1. Code of Conduct
        2. Leave Policy
        3. Health & Safety
        4. Termination Procedures
        """

        st.download_button(
            "📥 Download Handbook (TXT)",
            data=policy_text,
            file_name="policy_handbook.txt"
        )

        # JSON summary
        report_data = {
            "company": company_name,
            "country": country,
            "industry": industry,
            "employee_count": employee_count,
            "sections": ["Code of Conduct", "Leave Policy", "Health & Safety", "Termination"]
        }

        st.download_button(
            "📥 Download Summary (JSON)",
            data=json.dumps(report_data, indent=2),
            file_name="policy_summary.json"
        )

# --- SAMPLE HR DATA (FIXED) ---
SAMPLE_HR_DATA = {
    "EmployeeID": [101, 102, 103, 104, 105],
    "Name": ["John Doe", "Jane Smith", "Mike Johnson", "Sarah Williams", "David Brown"],
    "Department": ["Sales", "Engineering", "Marketing", "Engineering", "HR"],
    "TenureYears": [3, 5, 2, 7, 4],
    "EngagementScore": [4.2, 3.8, 4.5, 2.9, 3.5],
    "Attrition": ["No", "Yes", "No", "Yes", "No"],
    "TrainingsCompleted": [3, 5, 2, 1, 4],
    "AvgSkillGain": [1.2, 1.8, 0.9, 0.5, 1.5],
    "PerformanceRating": [4, 3, 5, 2, 4],
    "AppliedOnJobRatio": [0.8, 0.9, 0.7, 0.5, 0.85],
    "SalaryKES": [120000, 150000, 110000, 130000, 100000]
}

# --- AUTHENTICATION UI ---
st.title("HR Risk & Retention")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials. Username: admin, Password: password123")
    st.stop()

# --- MAIN DASHBOARD ---
st.sidebar.success(f"Welcome {st.session_state.username}")
if st.sidebar.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()

# Module selection
module = st.sidebar.selectbox(
    "Select module",
    ["Recruitment Funnel", "Attrition Risk & Cost", "Training ROI", 
     "Policy Compliance Auditor", "HR Policy Generator Pro"]
)

# --- RECRUITMENT FUNNEL ---
if module == "Recruitment Funnel":
    st.header("Recruitment Funnel Analytics")
    st.write("Connect to an ATS (Greenhouse, Workable, BambooHR) or upload recruitment CSV exports.")
    
    # File Uploader
    uploaded_file = st.file_uploader(
        "Upload recruitment export (CSV)",
        type="csv",
        help="Drag and drop file here\nLimit 200MB per file • CSV"
    )
    
    if uploaded_file:
        try:
            recruitment_data = pd.read_csv(uploaded_file)
            st.success("Recruitment data loaded successfully!")
            
            # Convert date columns to datetime if they exist
            date_columns = ['HireDate', 'ApplicationDate', 'OfferDate']
            for col in date_columns:
                if col in recruitment_data.columns:
                    recruitment_data[col] = pd.to_datetime(recruitment_data[col], errors='coerce')
            
            # Calculate key metrics
            total_hires = len(recruitment_data)
            
            # Hiring Rate calculation (if we have department data)
            hiring_rate = "N/A"
            if 'Department' in recruitment_data.columns:
                dept_hires = recruitment_data['Department'].value_counts()
                hiring_rate = f"{(dept_hires / dept_hires.sum() * 100).iloc[0]:.1f}%"
            
            # Average Time to Hire calculation
            avg_time_to_hire = "N/A"
            if 'TimeToHireDays' in recruitment_data.columns:
                avg_time_to_hire = f"{recruitment_data['TimeToHireDays'].mean():.1f} days"
            elif all(col in recruitment_data.columns for col in ['ApplicationDate', 'HireDate']):
                # Calculate from date columns if TimeToHireDays doesn't exist
                recruitment_data['TimeToHireCalc'] = (recruitment_data['HireDate'] - recruitment_data['ApplicationDate']).dt.days
                avg_time_to_hire = f"{recruitment_data['TimeToHireCalc'].mean():.1f} days"
            
            # Cost per Hire
            avg_cost_per_hire = "N/A"
            if 'CostPerHire' in recruitment_data.columns:
                avg_cost_per_hire = f"KES {recruitment_data['CostPerHire'].mean():,.0f}"
            
            # Show metrics
            st.subheader("Key Recruitment Metrics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Hires", total_hires)
            col2.metric("Hiring Rate", hiring_rate)
            col3.metric("Avg Time to Hire", avg_time_to_hire)
            col4.metric("Avg Cost per Hire", avg_cost_per_hire)
            
            # Visualizations
            if 'Department' in recruitment_data.columns:
                st.subheader("Hiring Distribution by Department")
                dept_counts = recruitment_data['Department'].value_counts().reset_index()
                dept_counts.columns = ['Department', 'Hires']
                fig1 = px.bar(dept_counts, x='Department', y='Hires', 
                             title='Number of Hires by Department')
                st.plotly_chart(fig1)
            
            if 'TimeToHireDays' in recruitment_data.columns or 'TimeToHireCalc' in recruitment_data.columns:
                st.subheader("Time to Hire Analysis")
                time_col = 'TimeToHireDays' if 'TimeToHireDays' in recruitment_data.columns else 'TimeToHireCalc'
                if 'Department' in recruitment_data.columns:
                    time_by_dept = recruitment_data.groupby('Department')[time_col].mean().reset_index()
                    fig2 = px.bar(time_by_dept, x='Department', y=time_col,
                                 title='Average Time to Hire by Department (Days)')
                    st.plotly_chart(fig2)
                else:
                    fig2 = px.histogram(recruitment_data, x=time_col, 
                                       title='Distribution of Time to Hire')
                    st.plotly_chart(fig2)
            
            if 'RecruitmentSource' in recruitment_data.columns:
                st.subheader("Recruitment Sources")
                source_counts = recruitment_data['RecruitmentSource'].value_counts().reset_index()
                source_counts.columns = ['Source', 'Count']
                fig3 = px.pie(source_counts, values='Count', names='Source',
                             title='Hires by Recruitment Source')
                st.plotly_chart(fig3)
            
            # Show raw data preview
            st.subheader("Data Preview")
            st.dataframe(recruitment_data.head())
            
            # Download button for processed data
            csv = recruitment_data.to_csv(index=False)
            st.download_button(
                label="Download Processed Data",
                data=csv,
                file_name="processed_recruitment_data.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"Error loading recruitment data: {str(e)}")
    else:
        st.warning("No recruitment data loaded. Use API connectors for live data or upload CSV exports.")
    
    # Next Steps Section
    st.markdown("---")
    st.subheader("Next steps:")
    st.markdown("""
    - Wire LLM for policy rewrites (OpenAI / Llama)
    - Add authentication for client deployments  
    - Implement scheduled data syncs for recruitment APIs
    - Add candidate pipeline stage tracking
    - Integrate offer acceptance rate metrics
    """)

# --- ATTRITION RISK & COST ---
elif module == "Attrition Risk & Cost":
    st.header("Attrition Risk & Cost Analysis")
    
    # File Uploader
    uploaded_file = st.file_uploader(
        "Upload HR Data (CSV)",
        type="csv",
        help="Upload employee data with columns like TenureYears, EngagementScore, PerformanceRating, etc."
    )
    
    if uploaded_file:
        try:
            hr_data = pd.read_csv(uploaded_file)
            st.success(f"HR data loaded successfully! {len(hr_data)} employees")
            
            # Convert Yes/No to 1/0 if needed
            if 'Attrition' in hr_data.columns:
                hr_data['Attrition'] = hr_data['Attrition'].map({'Yes': 1, 'No': 0, 'yes': 1, 'no': 0})
            
            # Calculate Risk Scores
            if all(col in hr_data.columns for col in ['EngagementScore', 'PerformanceRating', 'TenureYears']):
                # Simple risk scoring algorithm
                hr_data['RiskScore'] = (
                    (10 - hr_data['EngagementScore']) * 0.4 +  # Low engagement = higher risk
                    (5 - hr_data['PerformanceRating']) * 0.3 +  # Low performance = higher risk
                    (hr_data['TenureYears'] < 2) * 0.3  # New employees = higher risk
                ).round(2)
                
                # Categorize risk levels
                hr_data['RiskLevel'] = pd.cut(hr_data['RiskScore'], 
                                             bins=[0, 2, 4, 6, 10],
                                             labels=['Low', 'Medium', 'High', 'Critical'])
            
            # Calculate Cost Estimates
            if 'SalaryKES' in hr_data.columns:
                # Cost of replacement = 1.5x annual salary (industry standard)
                hr_data['ReplacementCost'] = hr_data['SalaryKES'] * 1.5
                
                # Total potential cost
                at_risk_data = hr_data[hr_data['RiskScore'] > 3] if 'RiskScore' in hr_data.columns else hr_data
                total_potential_cost = at_risk_data['ReplacementCost'].sum() if 'ReplacementCost' in at_risk_data.columns else 0
            
            # Display Key Metrics
            st.subheader("Attrition Risk Overview")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # Total employees
            col1.metric("Total Employees", len(hr_data))
            
            # At-risk employees
            if 'RiskScore' in hr_data.columns:
                at_risk_count = len(hr_data[hr_data['RiskScore'] > 3])
                col2.metric("At Risk Employees", f"{at_risk_count}", 
                           f"{(at_risk_count/len(hr_data)*100):.1f}%")
            else:
                col2.metric("At Risk Employees", "N/A")
            
            # Attrition rate
            if 'Attrition' in hr_data.columns:
                attrition_rate = hr_data['Attrition'].mean() * 100
                col3.metric("Current Attrition", f"{attrition_rate:.1f}%")
            else:
                col3.metric("Current Attrition", "N/A")
            
            # Potential cost
            if 'ReplacementCost' in hr_data.columns and 'RiskScore' in hr_data.columns:
                col4.metric("Potential Cost", f"KES {total_potential_cost:,.0f}")
            else:
                col4.metric("Potential Cost", "N/A")
            
            # Visualizations
            if 'RiskScore' in hr_data.columns:
                # Risk Distribution Chart
                st.subheader("Risk Score Distribution")
                fig1 = px.histogram(hr_data, x='RiskScore', nbins=20,
                                   title='Distribution of Employee Risk Scores')
                st.plotly_chart(fig1)
            
            # Risk by Department
            if 'Department' in hr_data.columns and 'RiskScore' in hr_data.columns:
                st.subheader("Risk by Department")
                dept_risk = hr_data.groupby('Department')['RiskScore'].mean().reset_index()
                fig2 = px.bar(dept_risk, x='Department', y='RiskScore',
                             title='Average Risk Score by Department')
                st.plotly_chart(fig2)
            
            # Engagement vs Performance Scatter Plot
            if all(col in hr_data.columns for col in ['EngagementScore', 'PerformanceRating']):
                st.subheader("Engagement vs Performance Risk Analysis")
                fig3 = px.scatter(hr_data, x='EngagementScore', y='PerformanceRating',
                                 color='RiskLevel' if 'RiskLevel' in hr_data.columns else None,
                                 hover_data=['Name'] if 'Name' in hr_data.columns else None,
                                 title='Engagement vs Performance (Color = Risk Level)')
                st.plotly_chart(fig3)
            
            # High-Risk Employees Table
            if 'RiskScore' in hr_data.columns:
                st.subheader("High-Risk Employees (Risk Score > 4)")
                high_risk = hr_data[hr_data['RiskScore'] > 4]
                
                if not high_risk.empty:
                    display_cols = ['Name', 'Department', 'RiskScore', 'RiskLevel', 
                                   'EngagementScore', 'PerformanceRating', 'TenureYears']
                    display_cols = [col for col in display_cols if col in high_risk.columns]
                    
                    st.dataframe(high_risk[display_cols].sort_values('RiskScore', ascending=False))
                    
                    # Download high-risk list
                    csv = high_risk[display_cols].to_csv(index=False)
                    st.download_button(
                        label="Download High-Risk List",
                        data=csv,
                        file_name="high_risk_employees.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No high-risk employees found (Risk Score > 4)")
            
            # Cost Analysis Section
            if 'ReplacementCost' in hr_data.columns and 'RiskScore' in hr_data.columns:
                st.subheader("Cost Impact Analysis")
                
                cost_by_risk = hr_data.groupby('RiskLevel')['ReplacementCost'].sum().reset_index()
                fig4 = px.pie(cost_by_risk, values='ReplacementCost', names='RiskLevel',
                             title='Potential Replacement Cost by Risk Level')
                st.plotly_chart(fig4)
                
                # Cost by Department
                if 'Department' in hr_data.columns:
                    cost_by_dept = hr_data.groupby('Department')['ReplacementCost'].sum().reset_index()
                    fig5 = px.bar(cost_by_dept, x='Department', y='ReplacementCost',
                                 title='Total Potential Replacement Cost by Department')
                    st.plotly_chart(fig5)
            
            # Data Preview
            st.subheader("Data Preview")
            preview_cols = [col for col in hr_data.columns if col not in ['RiskScore', 'RiskLevel', 'ReplacementCost']]
            st.dataframe(hr_data[preview_cols].head())
            
        except Exception as e:
            st.error(f"Error loading HR data: {str(e)}")
    else:
        # Use sample data if no file uploaded
        hr_data = pd.DataFrame(SAMPLE_HR_DATA)
        st.info("Using sample data. Upload a CSV file to analyze your own HR data.")
        st.dataframe(hr_data)
    
    # Additional Information
    st.markdown("---")
    st.subheader("Risk Scoring Methodology")
    st.markdown("""
    **Risk Score Calculation:**
    - **Engagement (40%)**: Lower scores = higher risk (10-point scale)
    - **Performance (30%)**: Lower ratings = higher risk (5-point scale)  
    - **Tenure (30%)**: Employees with <2 years tenure = higher risk
    
    **Risk Levels:**
    - **Low (0-2)**: Low attrition risk
    - **Medium (2-4)**: Moderate risk, monitor closely
    - **High (4-6)**: High risk, intervention recommended
    - **Critical (6-10)**: Very high risk, immediate action needed
    
    **Cost Assumptions:**
    - Replacement cost = 1.5x annual salary (includes recruitment, training, lost productivity)
    """)

# --- TRAINING ROI ---
elif module == "Training ROI":
    st.header("📊 Training ROI & Effectiveness Analysis")
    
    uploaded_file = st.file_uploader("Upload Training Data (CSV)", type="csv")
    
    if uploaded_file:
        training_data = pd.read_csv(uploaded_file)
    else:
        training_data = pd.DataFrame(SAMPLE_HR_DATA)
        st.info("Using sample data. Upload a CSV file to analyze your own training data.")
    
    # Data preprocessing
    if 'TrainingsCompleted' in training_data.columns and 'AvgSkillGain' in training_data.columns:
        # Calculate additional metrics
        training_data['ROI_per_training'] = training_data['AvgSkillGain'] / training_data['TrainingsCompleted'].replace(0, 1)
        training_data['SkillGain_per_Training'] = training_data['AvgSkillGain'] / training_data['TrainingsCompleted'].replace(0, 1)
        
        # Enhanced Metrics
        metrics = {
            "Total Trainings": f"{training_data['TrainingsCompleted'].sum():,}",
            "Avg Trainings/Employee": f"{training_data['TrainingsCompleted'].mean():.1f}",
            "Avg Skill Gain": f"{training_data['AvgSkillGain'].mean():.1f} pts",
            "ROI per Training": f"{training_data['ROI_per_training'].mean():.1f}x",
            "Skill Retention Rate": f"{(training_data['AppliedOnJobRatio'].mean() * 100):.1f}%" if 'AppliedOnJobRatio' in training_data.columns else "N/A",
            "High Performers Training Rate": f"{(training_data[training_data['PerformanceRating'] >= 4]['TrainingsCompleted'].mean()):.1f}" if 'PerformanceRating' in training_data.columns else "N/A",
            "Training Completion Rate": f"{(training_data['TrainingsCompleted'].sum() / (len(training_data) * 8) * 100):.1f}%"  # Assuming 8 possible trainings per employee
        }
        
        # Display metrics in two rows
        cols1 = st.columns(4)
        cols2 = st.columns(3)
        
        for i, (name, value) in enumerate(list(metrics.items())[:4]):
            cols1[i].metric(name, value)
        
        for i, (name, value) in enumerate(list(metrics.items())[4:]):
            cols2[i].metric(name, value)
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Department-wise analysis
            if 'Department' in training_data.columns:
                dept_stats = training_data.groupby('Department').agg({
                    'TrainingsCompleted': 'mean',
                    'AvgSkillGain': 'mean',
                    'ROI_per_training': 'mean'
                }).reset_index()
                
                fig1 = px.bar(
                    dept_stats, x='Department', y=['TrainingsCompleted', 'AvgSkillGain'],
                    title="Training Metrics by Department",
                    barmode='group',
                    labels={'value': 'Average', 'variable': 'Metric'}
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            # ROI by Department
            if 'Department' in training_data.columns:
                fig2 = px.bar(
                    dept_stats, x='Department', y='ROI_per_training',
                    title="ROI per Training by Department",
                    color='ROI_per_training',
                    color_continuous_scale='Viridis'
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            # Correlation analysis
            if 'PerformanceRating' in training_data.columns:
                fig3 = px.scatter(
                    training_data, x='TrainingsCompleted', y='PerformanceRating',
                    color='Department' if 'Department' in training_data.columns else None,
                    size='AvgSkillGain',
                    title="Training vs Performance Correlation",
                    hover_data=['Name'] if 'Name' in training_data.columns else None
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            # Training effectiveness by tenure
            if 'TenureYears' in training_data.columns:
                training_data['TenureGroup'] = pd.cut(training_data['TenureYears'], 
                                                     bins=[0, 2, 5, 10, 100], 
                                                     labels=['0-2 yrs', '2-5 yrs', '5-10 yrs', '10+ yrs'])
                
                tenure_stats = training_data.groupby('TenureGroup').agg({
                    'TrainingsCompleted': 'mean',
                    'AvgSkillGain': 'mean'
                }).reset_index()
                
                fig4 = px.line(
                    tenure_stats, x='TenureGroup', y=['TrainingsCompleted', 'AvgSkillGain'],
                    title="Training Effectiveness by Tenure",
                    markers=True
                )
                st.plotly_chart(fig4, use_container_width=True)
        
        # Advanced Analysis Section
        st.subheader("📈 Advanced Training Analytics")
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Training ROI by Position Level
            if 'PositionLevel' in training_data.columns:
                level_stats = training_data.groupby('PositionLevel').agg({
                    'TrainingsCompleted': 'mean',
                    'AvgSkillGain': 'mean',
                    'ROI_per_training': 'mean'
                }).reset_index()
                
                fig5 = px.bar(
                    level_stats, x='PositionLevel', y='ROI_per_training',
                    title="ROI by Position Level",
                    color='ROI_per_training',
                    color_continuous_scale='Plasma'
                )
                st.plotly_chart(fig5, use_container_width=True)
        
        with col4:
            # Training Impact on Attrition
            if 'Attrition' in training_data.columns:
                attrition_stats = training_data.groupby('Attrition').agg({
                    'TrainingsCompleted': 'mean',
                    'AvgSkillGain': 'mean'
                }).reset_index()
                
                fig6 = px.bar(
                    attrition_stats, x='Attrition', y=['TrainingsCompleted', 'AvgSkillGain'],
                    title="Training Impact on Attrition",
                    barmode='group'
                )
                st.plotly_chart(fig6, use_container_width=True)
        
        # Training Recommendations
        st.subheader("💡 Training Recommendations")
        
        # Identify departments with low ROI
        if 'Department' in training_data.columns:
            dept_stats = training_data.groupby('Department').agg({
                'ROI_per_training': 'mean'
            }).reset_index()
            
            low_roi_depts = dept_stats[dept_stats['ROI_per_training'] < dept_stats['ROI_per_training'].mean()]
            
            if not low_roi_depts.empty:
                st.warning("**Areas for Improvement:**")
                for _, row in low_roi_depts.iterrows():
                    st.write(f"- {row['Department']} shows below-average ROI ({row['ROI_per_training']:.1f}x). Consider reviewing training content and delivery methods.")
            
            # Identify high-performing departments
            high_roi_depts = dept_stats[dept_stats['ROI_per_training'] > dept_stats['ROI_per_training'].mean() * 1.2]
            if not high_roi_depts.empty:
                st.success("**Best Practices:**")
                for _, row in high_roi_depts.iterrows():
                    st.write(f"- {row['Department']} shows excellent ROI ({row['ROI_per_training']:.1f}x). Consider replicating their training approaches.")
        
        # Download enhanced report
        report = generate_training_report(training_data, "Training ROI Report", metrics)
        st.download_button(
            label="📥 Download Comprehensive Training Report",
            data=report,
            file_name="training_roi_analysis.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    else:
        st.error("Required columns (TrainingsCompleted, AvgSkillGain) not found in the uploaded data.")

# --- TEXT EXTRACTION FUNCTIONS ---
def extract_text_from_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def extract_text_from_docx(file):
    try:
        doc = docx.Document(file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading DOCX: {str(e)}")
        return ""

# --- COMPLIANCE CHECKING FUNCTIONS ---
def check_compliance_patterns(text, policy_type):
    issues = []
    
    # Define compliance patterns for different policy types
    patterns = {
        "general": [
            (r"(discriminat(e|ion|ory))", "Potential discrimination language"),
            (r"(harassment|bullying)", "Harassment policy reference"),
            (r"(confidentiality|nda|non.?disclosure)", "Confidentiality clause"),
            (r"(termination|firing|dismissal)", "Termination policy"),
            (r"(leave|vacation|sick|maternity|paternity)", "Leave policy"),
            (r"(code of conduct|ethics)", "Code of conduct"),
        ],
        "remote_work": [
            (r"(remote|work from home|wfh|telecommut)", "Remote work policy"),
            (r"(vpn|security|cyber)", "Remote security measures"),
            (r"(equipment|hardware|software)", "Equipment provision"),
            (r"(hours|availability|response time)", "Availability expectations"),
        ],
        "data_security": [
            (r"(data (protection|security|privacy))", "Data protection policy"),
            (r"(gdpr|ccpa|compliance)", "Regulatory compliance"),
            (r"(breach|incident response)", "Breach response plan"),
            (r"(encryption|access control)", "Security measures"),
        ]
    }
    
    # Check all relevant patterns
    for pattern_set in [patterns["general"], patterns.get(policy_type, [])]:
        for pattern, description in pattern_set:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].replace('\n', ' ')
                
                issues.append({
                    "type": description,
                    "context": context,
                    "policy_type": policy_type
                })
    
    return issues

# --- POLICY COMPLIANCE AUDITOR ENHANCED ---
def policy_compliance_auditor():
    st.header("📋 Policy Compliance Auditor")
    
    # Introduction
    st.markdown("""
    Upload your policy documents and employee handbooks to analyze compliance gaps, 
    identify missing sections, and ensure regulatory compliance.
    """)
    
    # File upload section
    uploaded_files = st.file_uploader(
        "Upload Policy Documents (PDF, DOCX)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        help="Upload your policy documents for compliance analysis"
    )
    
    if uploaded_files:
        st.success(f"{len(uploaded_files)} files uploaded successfully!")
        
        # Policy type selection
        policy_type = st.selectbox(
            "Select Policy Focus Area",
            ["General Compliance", "Remote Work", "Data Security", "All Policies"]
        )
        
        # Convert to simpler format for processing
        focus_area = policy_type.lower().replace(" ", "_")
        if focus_area == "all_policies":
            focus_area = "general"
        
        if st.button("🔍 Analyze Compliance", type="primary"):
            # Initialize results
            all_issues = []
            document_analysis = []
            
            # Process each file
            for file in uploaded_files:
                with st.spinner(f"Analyzing {file.name}..."):
                    # Extract text based on file type
                    if file.type == "application/pdf":
                        text = extract_text_from_pdf(file)
                    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                        text = extract_text_from_docx(file)
                    else:
                        text = ""
                    
                    if text:
                        # Analyze the text
                        issues = check_compliance_patterns(text, focus_area)
                        all_issues.extend(issues)
                        
                        # Document summary
                        doc_stats = {
                            "filename": file.name,
                            "word_count": len(text.split()),
                            "issues_found": len(issues),
                            "compliance_score": max(0, 100 - len(issues)*5)  # Simple scoring
                        }
                        document_analysis.append(doc_stats)
            
            if document_analysis:
                # Display overall results
                st.subheader("📊 Compliance Analysis Results")
                
                # Create metrics
                total_issues = len(all_issues)
                avg_score = sum(d['compliance_score'] for d in document_analysis) / len(document_analysis)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Documents Analyzed", len(uploaded_files))
                col2.metric("Total Issues Found", total_issues)
                col3.metric("Average Compliance Score", f"{avg_score:.1f}%")
                
                # Display document-level results
                st.subheader("Document-Level Analysis")
                doc_df = pd.DataFrame(document_analysis)
                st.dataframe(doc_df.style.highlight_max(subset=['compliance_score'], color='#90EE90')
                                          .highlight_min(subset=['compliance_score'], color='#FFCCCB'))
                
                # Display issues found
                if all_issues:
                    st.subheader("🔎 Identified Compliance Issues")
                    
                    # Group issues by type
                    issue_types = {}
                    for issue in all_issues:
                        issue_type = issue["type"]
                        if issue_type not in issue_types:
                            issue_types[issue_type] = []
                        issue_types[issue_type].append(issue)
                    
                    # Create expanders for each issue type
                    for issue_type, issues in issue_types.items():
                        with st.expander(f"{issue_type} ({len(issues)} found)"):
                            for i, issue in enumerate(issues, 1):
                                st.markdown(f"**Issue {i}**: {issue['context']}")
                    
                    # Visualizations
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # Issue type distribution
                        issue_counts = pd.DataFrame({
                            'Issue Type': list(issue_types.keys()),
                            'Count': [len(issues) for issues in issue_types.values()]
                        })
                        fig = px.pie(issue_counts, values='Count', names='Issue Type', 
                                    title='Distribution of Issue Types')
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # Compliance scores by document
                        fig2 = px.bar(doc_df, x='filename', y='compliance_score',
                                     title='Compliance Score by Document',
                                     labels={'compliance_score': 'Compliance Score (%)', 'filename': 'Document'})
                        fig2.update_layout(yaxis_range=[0, 100])
                        st.plotly_chart(fig2, use_container_width=True)
                    
                    # Recommendations
                    st.subheader("💡 Recommendations")
                    
                    if any("discrimination" in issue["type"].lower() for issue in all_issues):
                        st.warning("**Anti-Discrimination Policy**: Consider adding explicit non-discrimination clauses covering all protected characteristics.")
                    
                    if any("harassment" in issue["type"].lower() for issue in all_issues):
                        st.warning("**Anti-Harassment Policy**: Ensure you have clear reporting procedures and consequences for harassment.")
                    
                    if focus_area == "remote_work" and not any("security" in issue["type"].lower() for issue in all_issues):
                        st.info("**Remote Work Security**: Consider adding specific guidelines for data security in remote work arrangements.")
                    
                    st.info("""
                    **General Recommendations**:
                    - Review policies annually for regulatory updates
                    - Ensure all policies are easily accessible to employees
                    - Provide training on key policy areas
                    - Document employee acknowledgments of policy reviews
                    """)
                    
                else:
                    st.success("🎉 No compliance issues found! Your documents appear to be in good shape.")
                
                # Generate report
                if st.button("📄 Generate Compliance Report"):
                    # Create a simple report
                    report_data = {
                        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
                        "documents_analyzed": [d['filename'] for d in document_analysis],
                        "total_issues_found": total_issues,
                        "compliance_score": avg_score,
                        "issue_breakdown": issue_types,
                        "recommendations": "See above for specific recommendations"
                    }
                    
                    # Download button
                    st.download_button(
                        label="Download Compliance Report (JSON)",
                        data=json.dumps(report_data, indent=2),
                        file_name="compliance_analysis_report.json",
                        mime="application/json"
                    )
            else:
                st.warning("No text could be extracted from the uploaded documents.")
    else:
        # Show sample analysis when no files are uploaded
        st.info("💡 **How it works**: Upload policy documents to analyze them for compliance gaps, missing sections, and regulatory requirements.")
        
        with st.expander("📋 Example Compliance Analysis"):
            st.markdown("""
            | Document | Issues Found | Compliance Score |
            |----------|-------------|------------------|
            | Employee_Handbook.pdf | 3 | 85% |
            | Data_Security_Policy.docx | 1 | 95% |
            | Remote_Work_Policy.pdf | 5 | 75% |
            
            **Common issues found**:
            - Missing explicit non-discrimination clauses
            - Incomplete remote work security guidelines
            - Lack of clear reporting procedures for harassment
            """)
        
        st.warning("No policy documents uploaded. Please upload files to begin analysis.")

# This should be part of your main module selection logic
# Assuming you have a variable called 'module' that determines which section to show

# --- POLICY COMPLIANCE AUDITOR ---
if module == "Policy Compliance Auditor":
    policy_compliance_auditor()

# --- HR POLICY GENERATOR PRO ---
elif module == "HR Policy Generator Pro":
    st.header("📄 HR Policy Generator Pro")

    with st.sidebar:
        st.subheader("⚙️ Configuration")
        policy_template = st.selectbox(
            "Policy Template",
            ["Comprehensive HR Policy", "Remote Work Policy", "Code of Conduct", 
             "Anti-Discrimination Policy", "Data Security Policy", "Custom"]
        )
    
    with st.form("policy_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company = st.text_input("Company Name", "Acme Inc")
            industry = st.selectbox("Industry", [
                "Technology", "Finance", "Healthcare", "Manufacturing", 
                "Retail", "Education", "Non-Profit", "Other"
            ])
            employee_count = st.number_input("Number of Employees", min_value=1, max_value=100000, value=100)
            
        with col2:
            effective_date = st.date_input("Effective Date", datetime.now())
            review_freq = st.selectbox("Review Frequency", ["Annual", "Biannual", "Quarterly", "Monthly"])
            country = st.selectbox("Country", ["Kenya", "USA", "UK", "Canada", "Germany", "Other"])
        
        # Additional options
        st.subheader("Additional Options")
        col3, col4 = st.columns(2)
        
        with col3:
            include_remote_work = st.checkbox("Include Remote Work Policy", True)
            include_code_of_conduct = st.checkbox("Include Code of Conduct", True)
            include_data_security = st.checkbox("Include Data Security", True)
        
        with col4:
            include_anti_discrimination = st.checkbox("Include Anti-Discrimination", True)
            include_social_media = st.checkbox("Include Social Media Policy", False)
            include_whistleblower = st.checkbox("Include Whistleblower Protection", False)
        
        submitted = st.form_submit_button("✨ Generate Policy Document")
    
    if submitted:
        try:
            # Create PDF with enhanced formatting
            pdf = FPDF()
            pdf.add_page()
            
            # Header
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"{company.upper()} HUMAN RESOURCES POLICY HANDBOOK", ln=1, align='C')
            pdf.ln(5)
            
            # Metadata
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 8, f"Industry: {industry} | Employees: {employee_count} | Country: {country}", ln=1, align='C')
            pdf.cell(0, 8, f"Effective Date: {effective_date.strftime('%B %d, %Y')} | Review Frequency: {review_freq}", ln=1, align='C')
            pdf.ln(15)
            
            # Table of Contents
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "TABLE OF CONTENTS", ln=1)
            pdf.set_font("Arial", '', 10)
            
            sections = ["1. Purpose and Scope", "2. Employment Policies", "3. Code of Conduct", 
                       "4. Compensation & Benefits", "5. Leave Policies", "6. Health & Safety",
                       "7. Data Protection", "8. Policy Administration"]
            
            for i, section in enumerate(sections, 1):
                pdf.cell(0, 8, f"{section} ................................................. {i}", ln=1)
            
            pdf.ln(20)
            
            # Main Policy Content
            policy_sections = [
                ("1. PURPOSE AND SCOPE", 
                 f"This policy handbook establishes the framework for human resources management at {company}. "
                 f"It applies to all {employee_count} employees, contractors, and third-party representatives "
                 f"across our operations in {country}. The policies herein are designed to comply with {country} "
                 f"labor laws and industry best practices for the {industry} sector."),
                
                ("2. EMPLOYMENT POLICIES",
                 "Covers recruitment, selection, onboarding, probation periods, performance management, "
                 "and termination procedures. All employment decisions are based on merit, qualifications, "
                 "and business needs without discrimination."),
                
                ("3. CODE OF CONDUCT", 
                 "Employees must maintain high ethical standards, avoid conflicts of interest, protect "
                 "company assets, and maintain confidentiality. Professional behavior is expected at all times."),
                
                ("4. COMPENSATION & BENEFITS",
                 "Competitive compensation structure reviewed annually. Benefits package includes healthcare, "
                 "retirement plans, and professional development opportunities. Pay equity is regularly audited."),
                
                ("5. LEAVE POLICIES",
                 "Comprehensive leave policies including annual leave, sick leave, parental leave, and "
                 "bereavement leave. All leave requests must follow established approval procedures."),
                
                ("6. HEALTH & SAFETY",
                 "Commitment to providing a safe work environment. Regular safety training, emergency procedures, "
                 "and compliance with all occupational health and safety regulations."),
                
                ("7. DATA PROTECTION",
                 "Strict data protection protocols in accordance with relevant privacy laws. Employee data is "
                 "handled confidentially and used only for legitimate business purposes."),
                
                ("8. POLICY ADMINISTRATION",
                 f"This policy is effective {effective_date.strftime('%B %d, %Y')} and will be reviewed {review_freq.lower()} "
                 "by the HR department and legal counsel. Amendments require executive approval.")
            ]
            
            for title, content in policy_sections:
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, title, ln=1)
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 6, content)
                pdf.ln(8)
            
            # Optional Sections
            if include_remote_work:
                pdf.add_page()
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, "9. REMOTE WORK POLICY", ln=1)
                pdf.set_font("Arial", '', 10)
                pdf.multi_cell(0, 6, 
                    "Remote work arrangements require formal approval. Employees must maintain dedicated workspace, "
                    "follow security protocols, and maintain regular communication. Equipment and expense reimbursement "
                    "policies apply as per company guidelines."
                )
            
            # Approval Section
            pdf.add_page()
            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, "APPROVAL AND ACKNOWLEDGEMENT", ln=1)
            pdf.set_font("Arial", '', 10)
            pdf.multi_cell(0, 6, 
                f"This {company} HR Policy Handbook has been approved by the following authorized representatives "
                f"and is effective as of {effective_date.strftime('%B %d, %Y')}."
            )
            pdf.ln(15)
            
            signatures = [
                ("Chief Executive Officer", "_________________________", "Date: _________________________"),
                ("Chief HR Officer", "_________________________", "Date: _________________________"),
                ("Legal Counsel", "_________________________", "Date: _________________________")
            ]
            
            for title, sig, date in signatures:
                pdf.cell(95, 8, title, 0)
                pdf.cell(40, 8, sig, 0)
                pdf.cell(0, 8, date, 1)
                pdf.ln(10)
            
            # Save PDF to bytes buffer
            pdf_buffer = BytesIO()
            pdf.output(pdf_buffer)
            pdf_buffer.seek(0)
            
            # Download button
            st.success("Policy document generated successfully!")
            st.download_button(
                "📥 Download HR Policy Handbook (PDF)",
                data=pdf_buffer,
                file_name=f"{company.replace(' ', '_')}_HR_Policy_Handbook.pdf",
                mime="application/pdf"
            )
            
        except Exception as e:
            st.error(f"Error generating policy document: {str(e)}")