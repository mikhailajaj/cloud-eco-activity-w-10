"""
FinOps Report Generation Module
Generates comprehensive reports for CloudMart tagging compliance and cost analysis
"""
import pandas as pd
import streamlit as st
from datetime import datetime
from typing import Dict, Any
import io

def calculate_avg_field_completeness(df: pd.DataFrame) -> float:
    """Calculate average field completeness across required tag fields"""
    tag_fields = ['Department', 'Project', 'Environment', 'Owner', 'CostCenter', 'CreatedBy']
    available_tags = [tag for tag in tag_fields if tag in df.columns]
    
    if not available_tags:
        return 0.0
    
    completeness_scores = df[available_tags].notna().sum(axis=1) / len(available_tags) * 100
    return completeness_scores.mean()

def generate_executive_summary(metrics: Dict[str, Any], df: pd.DataFrame) -> str:
    """Generate executive summary section of the report"""
    
    # Calculate key insights directly from the DataFrame for accuracy
    total_resources = len(df)
    untagged_count = len(df[df['Tagged'] == 'No'])
    untagged_pct = (untagged_count / total_resources * 100) if total_resources > 0 else 0
    
    total_cost = df['MonthlyCostUSD'].sum()
    untagged_cost = df[df['Tagged'] == 'No']['MonthlyCostUSD'].sum()
    untagged_cost_pct = (untagged_cost / total_cost * 100) if total_cost > 0 else 0
    
    # Most problematic department
    if 'Department' in df.columns and 'Tagged' in df.columns:
        dept_untagged = df[df['Tagged'] == 'No'].groupby('Department')['MonthlyCostUSD'].sum().sort_values(ascending=False)
        worst_dept = dept_untagged.index[0] if len(dept_untagged) > 0 else "N/A"
        worst_dept_cost = dept_untagged.iloc[0] if len(dept_untagged) > 0 else 0
    else:
        worst_dept = "N/A"
        worst_dept_cost = 0
    
    summary = f"""
## 📋 Executive Summary

**Date Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}

### 🚨 Critical Findings

- **{untagged_pct:.1f}%** of cloud resources are untagged ({untagged_count:,} out of {total_resources:,} resources)
- **${untagged_cost:,.2f}** in monthly costs cannot be properly allocated ({untagged_cost_pct:.1f}% of total costs)
- **{worst_dept}** department has the highest untagged cost burden (${worst_dept_cost:,.2f}/month)

### 💰 Financial Impact

| Metric | Value | Impact |
|--------|--------|--------|
| Total Monthly Cost | ${total_cost:,.2f} | Base cloud spend |
| Untagged Cost | ${untagged_cost:,.2f} | Hidden/unallocatable costs |
| Cost Visibility Gap | {untagged_cost_pct:.1f}% | Percentage of spend without accountability |
| Estimated Annual Impact | ${untagged_cost * 12:,.2f} | Projected yearly unallocated spend |

### 🎯 Governance Status

- **Compliance Rate:** {(total_resources - untagged_count) / total_resources * 100 if total_resources > 0 else 0:.1f}%
- **Data Quality Score:** {metrics.get('data_quality_score', 85):.1f}%
- **Field Completeness:** {calculate_avg_field_completeness(df):.1f}% average across required tags
"""
    return summary

def generate_detailed_analysis(df: pd.DataFrame, metrics: Dict[str, Any]) -> str:
    """Generate detailed analysis section"""
    
    analysis = """
## 🔍 Detailed Analysis

### Department Breakdown
"""
    
    if 'Department' in df.columns and 'Tagged' in df.columns:
        # Department analysis
        dept_analysis = df.groupby(['Department', 'Tagged']).agg({
            'ResourceID': 'count',
            'MonthlyCostUSD': 'sum'
        }).unstack(fill_value=0)
        
        analysis += """
| Department | Tagged Resources | Untagged Resources | Tagged Cost | Untagged Cost | Risk Level |
|------------|------------------|-------------------|-------------|---------------|------------|
"""
        
        for dept in dept_analysis.index:
            tagged_res = dept_analysis.loc[dept, ('ResourceID', 'Yes')] if ('ResourceID', 'Yes') in dept_analysis.columns else 0
            untagged_res = dept_analysis.loc[dept, ('ResourceID', 'No')] if ('ResourceID', 'No') in dept_analysis.columns else 0
            tagged_cost = dept_analysis.loc[dept, ('MonthlyCostUSD', 'Yes')] if ('MonthlyCostUSD', 'Yes') in dept_analysis.columns else 0
            untagged_cost = dept_analysis.loc[dept, ('MonthlyCostUSD', 'No')] if ('MonthlyCostUSD', 'No') in dept_analysis.columns else 0
            
            total_cost = tagged_cost + untagged_cost
            risk_pct = (untagged_cost / total_cost * 100) if total_cost > 0 else 0
            
            if risk_pct > 50:
                risk_level = "🔴 HIGH"
            elif risk_pct > 25:
                risk_level = "🟡 MEDIUM"
            else:
                risk_level = "🟢 LOW"
                
            analysis += f"| {dept} | {tagged_res} | {untagged_res} | ${tagged_cost:,.2f} | ${untagged_cost:,.2f} | {risk_level} |\n"
    
    # Service analysis
    if 'Service' in df.columns:
        analysis += """

### Top Cost Services
"""
        service_costs = df.groupby('Service')['MonthlyCostUSD'].sum().sort_values(ascending=False).head(10)
        
        analysis += """
| Service | Monthly Cost | Percentage of Total |
|---------|--------------|-------------------|
"""
        total_cost = df['MonthlyCostUSD'].sum()
        for service, cost in service_costs.items():
            pct = (cost / total_cost * 100) if total_cost > 0 else 0
            analysis += f"| {service} | ${cost:,.2f} | {pct:.1f}% |\n"
    
    # Environment analysis
    if 'Environment' in df.columns:
        analysis += """

### Environment Distribution
"""
        env_analysis = df.groupby(['Environment', 'Tagged']).agg({
            'ResourceID': 'count',
            'MonthlyCostUSD': 'sum'
        }).unstack(fill_value=0)
        
        analysis += """
| Environment | Total Resources | Tagged % | Monthly Cost | Compliance Level |
|-------------|----------------|----------|--------------|------------------|
"""
        
        for env in env_analysis.index:
            tagged_res = env_analysis.loc[env, ('ResourceID', 'Yes')] if ('ResourceID', 'Yes') in env_analysis.columns else 0
            total_res = env_analysis.loc[env, 'ResourceID'].sum()
            tagged_pct = (tagged_res / total_res * 100) if total_res > 0 else 0
            total_cost = env_analysis.loc[env, 'MonthlyCostUSD'].sum()
            
            if tagged_pct >= 80:
                compliance_level = "✅ Excellent"
            elif tagged_pct >= 60:
                compliance_level = "⚠️ Good"
            elif tagged_pct >= 40:
                compliance_level = "🔶 Fair"
            else:
                compliance_level = "❌ Poor"
                
            analysis += f"| {env} | {total_res} | {tagged_pct:.1f}% | ${total_cost:,.2f} | {compliance_level} |\n"
    
    return analysis

def generate_recommendations(df: pd.DataFrame, metrics: Dict[str, Any]) -> str:
    """Generate actionable recommendations based on analysis"""
    
    recommendations = """
## 🚀 Recommendations for Governance Improvement

### Immediate Actions (0-30 days)

1. **🛑 Implement "Tag or Terminate" Policy**
   - Enforce mandatory tagging for new resources
   - Set up automated alerts for untagged resources
   - Establish 48-hour grace period before enforcement

2. **📊 Deploy Cost Allocation Dashboard**
   - Use this dashboard for monthly department reviews
   - Share untagged cost reports with department heads
   - Track improvement metrics weekly

### Short-term Actions (1-3 months)

3. **🔧 Infrastructure as Code (IaC) Integration**
   - Mandate Terraform/CloudFormation for all deployments
   - Add tag validation to CI/CD pipelines
   - Block deployments missing required tags

4. **👥 Department-specific Remediation**"""
    
    # Add department-specific recommendations
    if 'Department' in df.columns and 'Tagged' in df.columns:
        dept_untagged = df[df['Tagged'] == 'No'].groupby('Department')['MonthlyCostUSD'].sum().sort_values(ascending=False)
        
        for i, (dept, cost) in enumerate(dept_untagged.head(3).items()):
            priority = ["HIGH", "MEDIUM", "LOW"][i]
            recommendations += f"""
   - **{dept}** ({priority} Priority): Address ${cost:,.2f}/month in untagged costs"""
    
    recommendations += """

### Long-term Strategy (3-12 months)

5. **💡 Automation & Governance**
   - Implement auto-tagging based on resource patterns
   - Set up cost anomaly detection
   - Create automated compliance scoring

6. **🎯 Cultural Change**
   - Gamify tagging compliance across departments
   - Include tagging metrics in team KPIs
   - Provide regular training on cost optimization

7. **📈 Advanced Analytics**
   - Implement predictive cost forecasting
   - Set up automated showback/chargeback
   - Create department-specific cost optimization recommendations

### Success Metrics

Target the following improvements within 6 months:
- **Tagging Compliance:** Increase from {:.1f}% to 95%+
- **Cost Visibility:** Reduce untagged costs from ${:,.2f} to <$500/month
- **Field Completeness:** Achieve 90%+ completion for all required tags
""".format(
        (len(df) - len(df[df['Tagged'] == 'No'])) / len(df) * 100 if len(df) > 0 else 0,
        df[df['Tagged'] == 'No']['MonthlyCostUSD'].sum()
    )
    
    return recommendations

def generate_technical_appendix(df: pd.DataFrame, metrics: Dict[str, Any]) -> str:
    """Generate technical details and data quality information"""
    
    appendix = f"""
## 📋 Technical Appendix

### Data Quality Assessment

- **Total Records Processed:** {len(df):,}
- **Unique Resources:** {metrics.get('unique_resources', 'N/A')}
- **Duplicate Records:** {metrics.get('duplicate_records', 'N/A')}
- **Data Quality Score:** {metrics.get('data_quality_score', 'N/A')}%

### Tag Field Completeness

"""
    
    # Field completeness details
    if 'field_completeness' in metrics:
        appendix += """| Tag Field | Completeness | Status |
|-----------|--------------|--------|
"""
        for field, completeness in metrics['field_completeness'].items():
            if completeness >= 80:
                status = "✅ Good"
            elif completeness >= 50:
                status = "⚠️ Needs Improvement"
            else:
                status = "❌ Critical"
            appendix += f"| {field} | {completeness:.1f}% | {status} |\n"
    
    appendix += f"""

### Processing Details

- **Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Analysis Period:** Current month snapshot
- **Currency:** USD
- **Methodology:** CloudMart FinOps Framework v2.0

### Data Sources

- Primary: `cloudmart_multi_account_cleaned.csv`
- Validation: Automated data quality checks
- Processing: Streamlit dashboard with caching enabled
"""
    
    return appendix

def generate_full_report(df: pd.DataFrame, metrics: Dict[str, Any]) -> str:
    """Generate complete FinOps governance report"""
    
    report_title = """
# 📊 CloudMart FinOps Governance Report
## Cloud Resource Tagging Compliance & Cost Analysis

---
"""
    
    # Combine all sections
    full_report = (
        report_title +
        generate_executive_summary(metrics, df) +
        generate_detailed_analysis(df, metrics) +
        generate_recommendations(df, metrics) +
        generate_technical_appendix(df, metrics)
    )
    
    return full_report

def create_csv_export(df: pd.DataFrame, report_type: str = "untagged") -> io.StringIO:
    """Create CSV export for specific report types"""
    
    output = io.StringIO()
    
    if report_type == "untagged":
        untagged_df = df[df['Tagged'] == 'No'].copy()
        # Add calculated fields for the export
        untagged_df['RecommendedAction'] = 'Add required tags'
        untagged_df['Priority'] = untagged_df['MonthlyCostUSD'].apply(
            lambda x: 'High' if x > 100 else 'Medium' if x > 50 else 'Low'
        )
        untagged_df.to_csv(output, index=False)
    
    elif report_type == "compliance_summary":
        # Create department compliance summary
        compliance_summary = df.groupby('Department').agg({
            'ResourceID': 'count',
            'Tagged': lambda x: (x == 'Yes').sum(),
            'MonthlyCostUSD': 'sum'
        }).reset_index()
        
        compliance_summary['ComplianceRate'] = (
            compliance_summary['Tagged'] / compliance_summary['ResourceID'] * 100
        ).round(1)
        
        # Calculate untagged costs per department, handling departments with no untagged resources
        untagged_by_dept = df[df['Tagged'] == 'No'].groupby('Department')['MonthlyCostUSD'].sum()
        compliance_summary['UntaggedCost'] = compliance_summary['Department'].map(untagged_by_dept).fillna(0)
        
        compliance_summary.to_csv(output, index=False)
    
    elif report_type == "full_analysis":
        # Enhanced dataset with calculated fields
        enhanced_df = df.copy()
        
        # Add tag completeness score
        tag_fields = ['Department', 'Project', 'Environment', 'Owner', 'CostCenter', 'CreatedBy']
        available_tags = [tag for tag in tag_fields if tag in enhanced_df.columns]
        enhanced_df['TagCompletenessScore'] = enhanced_df[available_tags].notna().sum(axis=1)
        enhanced_df['TagCompletenessPct'] = (enhanced_df['TagCompletenessScore'] / len(available_tags) * 100).round(1)
        
        # Add risk category
        enhanced_df['RiskCategory'] = enhanced_df['MonthlyCostUSD'].apply(
            lambda x: 'High Risk' if x > 150 else 'Medium Risk' if x > 75 else 'Low Risk'
        )
        
        enhanced_df.to_csv(output, index=False)
    
    output.seek(0)
    return output

@st.cache_data
def generate_report_data(df: pd.DataFrame, metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Generate all report data and exports"""
    
    report_data = {
        'markdown_report': generate_full_report(df, metrics),
        'untagged_csv': create_csv_export(df, 'untagged').getvalue(),
        'compliance_csv': create_csv_export(df, 'compliance_summary').getvalue(),
        'full_analysis_csv': create_csv_export(df, 'full_analysis').getvalue(),
        'generation_timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
    }
    
    return report_data