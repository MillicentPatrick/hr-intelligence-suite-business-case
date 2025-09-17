HR Intelligence Suite: Unified Analytics Dashboard
A comprehensive, data-driven dashboard that quantifies the impact of HR initiatives across Recruitment, Retention, Development, and Compliance.

🌟 Overview
The HR Intelligence Suite is an integrated analytics platform built in Streamlit. It transforms raw HR data into strategic insights, providing a single source of truth for HR leadership to make evidence-based decisions that reduce cost, mitigate risk, and improve organizational health.

🧩 Dashboard Modules
Navigate using the sidebar to access each module's dedicated report and interactive analytics.

| Module | Purpose | Key Features |
| :--- | :--- | :--- |
| **Recruitment Analytics** | Optimize talent acquisition efficiency and effectiveness. | Funnel analytics, source ROI, time-to-hire, cost-per-hire, departmental distribution, hires by source, offer acceptance metrics. |
| **Attrition Risk & Cost** | Proactively identify flight risk and quantify its financial impact. | Predictive risk scoring, employee heatmaps, cost impact analysis, high-risk employee lists, risk by department, engagement vs performance matrix. |
| **Training ROI Analyzer** | Measure the financial return and efficacy of learning & development programs. | Skill gain metrics, ROI calculation, retention impact analysis, departmental effectiveness, training vs performance correlation, completion rates. |
| **Policy Compliance Auditor** | Automate the review of policy documents for regulatory gaps and risks. | AI-powered gap detection, compliance scoring, actionable recommendations, issue type distribution, document-level analysis. |
| **HR Policy Generator Pro** | Rapidly generate customized, compliant HR policy handbooks. | Dynamic PDF generation, multi-country compliance, customizable sections, professional formatting, automatic TOC. |
🚀 Quick Start
Prerequisites
Python 3.8+

pip

Installation & Run
Clone and install:

bash
git clone <repository-url>
cd hr-intelligence-suite
pip install -r requirements.txt
Prepare your data: Place CSV files (employee_data.csv, recruitment_data.csv, training_data.csv) in the /data directory.

Launch the dashboard:

bash
streamlit run app.py
Open your browser to http://localhost:8501. Use the sidebar to navigate between modules.

📊 Module Specifications & Metrics
1. Recruitment Analytics
Funnel Overview: Total Hires, Hiring Rate, Average Time to Hire, Average Cost per Hire.

Distribution Analysis: Hiring distribution by department, Hires by recruitment sources.

Data Review: Interactive table of raw employee data for validation.

Next Steps:

Wire LLM for automated job description and policy rewrites.

Integrate with Greenhouse/Workday APIs for scheduled data syncs.

Add candidate pipeline stage tracking.

Integrate offer acceptance rate metrics.

2. Attrition Risk & Cost Analysis
Overview: Total Employees, At-Risk Employees, Current Attrition Rate, Potential Cost Exposure.

Risk Analysis: Risk score distribution, Risk by department, Engagement vs. Performance matrix.

High-Risk List: Actionable list of employees with high flight risk.

Cost Impact: Potential replacement cost by risk level, Total potential cost by department.

Methodology: Transparency into the risk scoring algorithm (e.g., based on tenure, performance, engagement, compensation).

3. Training ROI Analyzer
Overview: Total Trainings, Avg. Trainings/Employee, Avg. Skill Gain, Overall ROI.

Efficacy Metrics: Skill retention rate, Training completion rate, High performer retention rate.

Advanced Analytics: Training vs. performance correlation, ROI by department, Effectiveness by employee tenure.

Strategic Insights: ROI by position level, Training impact on attrition rates.

Recommendations: Data-driven suggestions for which programs to expand, improve, or sunset.

4. Policy Compliance Auditor
Compliance Report: Overall compliance score and high-level summary.

Document-Level Analysis: Compliance score, word count, and issues found per uploaded document.

Issue Breakdown: Distribution of issue types (e.g., Non-Discrimination, Data Security, Harassment).

Recommendations: Specific, actionable steps to remediate each identified compliance gap.

5. HR Policy Generator Pro
Dynamic Generation: Creates a customized employee handbook based on company size, industry, and location.

Configurable Sections: Select from Remote Work, Data Security, Code of Conduct, and more.

Professional Output: Generates a print-ready PDF with company branding, table of contents, and signature pages.

🔧 Configuration
Set company-specific constants (e.g., fully-burdened hourly cost, average replacement cost) in config.py.

Modify data schema mappings in utils/data_loader.py if your CSV column names differ.

Customize the risk scoring model in modules/attrition.py to align with your organization's drivers.

🚧 Roadmap & Contribution
We welcome contributions to our prioritized roadmap:

Authentication: Add LDAP/SSO for secure client deployment.

API Integration: Implement scheduled syncs with major ATS (e.g., Lever, Greenhouse) and HRIS (e.g., Workday, BambooHR) platforms.

LLM Integration: Wire OpenAI/Gemini for intelligent policy rewriting and summarization.

Advanced Forecasting: Build predictive models for attrition and recruitment needs.

To contribute, please fork the repository and submit a Pull Request against the development branch.

📄 License
This project is licensed under the MIT License. See the LICENSE file for details.

🛟 Support
For technical support or data integration questions, please file an issue on GitHub or contact: people-analytics@yourcompany.com