# CloudMart FinOps Dashboard 2.0

This project is an enhanced, interactive Streamlit dashboard for analyzing cloud resource tagging compliance and cost governance. It has been refactored for better maintainability and includes new features for deeper financial analysis.

## 🚀 Key Enhancements in Version 2.0

-   **Modular Architecture**: The original single-file application has been refactored into a clean, modular structure, separating data loading, calculations, and visualizations. This makes the codebase easier to manage and extend.
-   **📈 Historical Trend Analysis**: A new "Historical Trends" tab has been added to visualize simulated cost and tagging compliance data over the last six months. This helps in understanding the long-term effectiveness of governance policies.
-   **🎨 Improved UI/UX**: The dashboard layout has been redesigned for a more intuitive and professional user experience, with clearly organized tabs and better visual layouts.
-   **Robust Code**: The code now includes better error handling, caching, and is structured for scalability.

## Features

-   **Data Exploration**: Load and inspect the `cloudmart_multi_account_cleaned.csv` dataset.
-   **KPI Dashboard**: Displays total resources, tagging compliance percentage, total cost, and untagged cost.
-   **Interactive Filters**: Filter data by Service, Region, and Department across the relevant tabs.
-   **Historical Analysis**: View trends of monthly cost and tagging compliance.
-   **Cost Visibility**: Visualizes costs across departments, services, and environments.
-   **Compliance Deep Dive**:
    - Identifies resources with low "Tag Completeness Scores".
    - Lists untagged resources and highlights the most frequently missing tags.
    - Allows downloading lists of non-compliant resources.
-   **Interactive Tag Remediation**:
    - Provides an editable table to simulate filling in missing tag values.
    - Instantly recalculates and shows the "before and after" impact on compliance KPIs.
    - Allows downloading the remediated dataset.

## Summary of Findings

Based on an analysis of the `cloudmart_multi_account_cleaned.csv` dataset, here is a summary of the key findings:

*   **Percentage of Untagged Resources:** **52.8%**
    *   Out of 36 unique resources, 19 are untagged, indicating a systemic governance issue.
*   **Total Untagged Cost:** **$1,370.00 / month**
    *   This cost cannot be accurately allocated, representing a significant blind spot in financial accountability.
*   **Departments with Missing Tags:**
    *   Untagged resources were found across **all** departments: Marketing, Sales, Analytics, DevOps, Finance, and HR. This shows the problem is widespread and not isolated to a single business unit.

### Recommendations for Governance Improvement

1.  **Implement a "Tag or Terminate" Policy:** Enforce a strict, automated policy where newly provisioned resources without mandatory tags (`Department`, `Project`, `Owner`) are automatically flagged and, after a short grace period, terminated.
2.  **Leverage Infrastructure as Code (IaC):** Mandate the use of tools like Terraform or CloudFormation and integrate a "linter" to check for required tags before deployment.
3.  **Establish Clear Showback/Chargeback:** Circulate detailed cost reports to each department head, highlighting untraceable costs to create top-down pressure for remediation.
4.  **Gamify Compliance:** Use the dashboard to create and track a "Tagging Compliance Score" for each department to encourage ownership and friendly competition.

## Project Structure

```
activity6_improved/
├── app.py                 # Main Streamlit app entry point
├── data/
│   └── cloudmart_multi_account_cleaned.csv
├── modules/
│   ├── __init__.py
│   ├── data_loader.py     # Handles data loading and simulation
│   ├── calculations.py    # FinOps metrics and trend calculations
│   └── visualizations.py  # All Plotly visualization functions
├── requirements.txt
└── README.md
```

## Installation

1.  **Navigate to the `activity6_improved` directory**:
    ```bash
    cd /Users/mikha2il3ajaj/Development/cloud-eco/activity6_improved
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the Streamlit dashboard**:
    ```bash
    streamlit run app.py
    ```
2.  Open your web browser to the URL provided by Streamlit (usually `http://localhost:8501`).

## Agent-driven Improvements

This project was improved by simulating a team of specialized AI agents:

-   **`solution-architect`**: Designed the new modular project structure.
-   **`code-reviewer`**: Refactored the code for clarity, robustness, and adherence to best practices.
-   **`finops-analyst`**: Added the historical trend analysis feature and produced the summary of findings.
-   **`ux-designer` & `finops-dashboard-developer`**: Redesigned the UI for better usability and a more professional aesthetic.
-   **`project-organizer`**: Updated this README and ensured the project structure is logical and well-documented.
