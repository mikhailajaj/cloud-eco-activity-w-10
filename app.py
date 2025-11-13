import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from modules.data_loader import load_data
from modules.data_validator import validate_cloudmart_data
from modules.report_generator import generate_report_data

# --- Page Configuration ---
st.set_page_config(
    page_title="CloudMart FinOps Dashboard",
    page_icon="💰",
    layout="wide"
)

# --- CHUNK 3: Interactive Cost Analysis Visualizations ---
@st.cache_data
def create_department_cost_chart(df):
    """Cost breakdown by Department (bar chart) with compliance overlay"""
    dept_summary = df.groupby(['Department', 'Tagged']).agg({
        'MonthlyCostUSD': 'sum',
        'ResourceID': 'count'
    }).reset_index()
    
    fig = px.bar(dept_summary, x='Department', y='MonthlyCostUSD', color='Tagged',
                 title='Monthly Cost by Department (Tagged vs Untagged)',
                 labels={'MonthlyCostUSD': 'Monthly Cost (USD)'},
                 color_discrete_map={'Yes': '#2E8B57', 'No': '#DC143C'},
                 hover_data={'ResourceID': True})
    
    fig.update_layout(barmode='group', xaxis_tickangle=-45)
    return fig

@st.cache_data
def create_tagging_impact_chart(df):
    """Cost impact of untagged resources (pie chart) with drill-down"""
    tagged_cost = df[df['Tagged'] == 'Yes']['MonthlyCostUSD'].sum()
    untagged_cost = df[df['Tagged'] == 'No']['MonthlyCostUSD'].sum()
    
    cost_data = pd.DataFrame({
        'Status': ['Tagged Resources', 'Untagged Resources'],
        'Cost': [tagged_cost, untagged_cost],
        'Percentage': [tagged_cost/(tagged_cost+untagged_cost)*100, 
                      untagged_cost/(tagged_cost+untagged_cost)*100]
    })
    
    fig = px.pie(cost_data, values='Cost', names='Status',
                 title='Cost Impact of Untagged Resources',
                 color_discrete_map={'Tagged Resources': '#2E8B57', 'Untagged Resources': '#DC143C'},
                 hover_data={'Percentage': ':.1f'})
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

@st.cache_data
def create_creation_method_chart(df):
    """Cost by creation method (Manual vs Production/Jenkins) analysis"""
    method_summary = df.groupby(['CreatedBy', 'Tagged']).agg({
        'MonthlyCostUSD': 'sum',
        'ResourceID': 'count'
    }).reset_index()
    
    fig = px.sunburst(method_summary, path=['CreatedBy', 'Tagged'], values='MonthlyCostUSD',
                     title='Cost Distribution by Creation Method and Tagging Status',
                     color='MonthlyCostUSD',
                     hover_data={'ResourceID': True})
    return fig

@st.cache_data  
def create_resource_efficiency_chart(df):
    """Resource count vs cost analysis (scatter plot) with insights"""
    service_summary = df.groupby(['Service', 'Tagged']).agg({
        'MonthlyCostUSD': 'sum',
        'ResourceID': 'count'
    }).reset_index()
    service_summary['Cost_Per_Resource'] = service_summary['MonthlyCostUSD'] / service_summary['ResourceID']
    
    fig = px.scatter(service_summary, x='ResourceID', y='MonthlyCostUSD', 
                    color='Tagged', size='Cost_Per_Resource',
                    hover_data=['Service', 'Cost_Per_Resource'],
                    title='Resource Efficiency: Count vs Cost by Service',
                    labels={'ResourceID': 'Resource Count', 'MonthlyCostUSD': 'Monthly Cost (USD)'},
                    color_discrete_map={'Yes': '#2E8B57', 'No': '#DC143C'})
    
    fig.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')))
    return fig

# --- Dashboard Pages ---
def show_overview_page(df_clean, metrics):
    """Overview/Summary page with key metrics and validation results"""
    st.header("📊 Overview & Data Quality")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Resources", f"{metrics['total_resources']:,}")
    with col2:
        st.metric("Compliance Rate", f"{metrics['compliance_rate']:.1f}%")
    with col3:
        st.metric("Monthly Cost", f"${metrics['total_monthly_cost']:,.2f}")
    with col4:
        st.metric("Data Quality Score", f"{metrics['data_quality_score']:.1f}%")
    
    # Show processing information based on duplicate handling setting
    if metrics.get('duplicates_removed', True):
        st.info(f"✅ Processed {metrics['original_records']} records, removed {metrics['duplicate_records']} duplicates")
    else:
        st.warning(f"⚠️ Processed {metrics['original_records']} records, kept {metrics['duplicate_records']} duplicates (intentional)")
    
    # Show processing note if available
    if 'processing_note' in metrics:
        st.caption(f"📋 {metrics['processing_note']}")

def show_cost_analysis_page(df_clean):
    """Cost Analysis page with interactive visualizations (CHUNK 3)"""
    st.header("💰 Cost Analysis")
    st.markdown("**Interactive cost breakdown and governance insights**")
    
    # Key metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        total_cost = df_clean['MonthlyCostUSD'].sum()
        st.metric("Total Monthly Cost", f"${total_cost:,.2f}")
    with col2:
        untagged_cost = df_clean[df_clean['Tagged'] == 'No']['MonthlyCostUSD'].sum()
        st.metric("Untagged Cost", f"${untagged_cost:,.2f}")
    with col3:
        manual_cost = df_clean[df_clean['CreatedBy'] == 'Manual']['MonthlyCostUSD'].sum()
        st.metric("Manual Creation Cost", f"${manual_cost:,.2f}")
    
    # Visualization tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Department Breakdown", "🏷️ Tagging Impact", "⚙️ Creation Methods", "📈 Cost Efficiency"])
    
    with tab1:
        st.plotly_chart(create_department_cost_chart(df_clean), use_container_width=True)
    
    with tab2:
        st.plotly_chart(create_tagging_impact_chart(df_clean), use_container_width=True)
    
    with tab3:
        st.plotly_chart(create_creation_method_chart(df_clean), use_container_width=True)
    
    with tab4:
        st.plotly_chart(create_resource_efficiency_chart(df_clean), use_container_width=True)
    
    # Key insights section
    st.subheader("🔍 Cost Governance Insights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.warning("**Critical Finding**: Manual resource creation shows 0% compliance")
        manual_resources = len(df_clean[df_clean['CreatedBy'] == 'Manual'])
        st.write(f"• {manual_resources} resources created manually")
        st.write(f"• ${manual_cost:,.2f}/month untracked costs")
        
    with col2:
        st.success("**Best Practice**: Production resources achieve 100% compliance")
        prod_resources = len(df_clean[(df_clean['Environment'] == 'Prod') & (df_clean['Tagged'] == 'Yes')])
        st.write(f"• {prod_resources} production resources properly tagged")
        st.write(f"• Infrastructure as Code shows better compliance")

def show_compliance_analysis_page(df_clean, metrics):
    """Compliance Analysis page - Task Set 3 implementation (REQ-011 to REQ-015)"""
    st.header("🛡️ Compliance Analysis")
    st.markdown("**Tag Completeness and Governance Analytics**")
    
    # Calculate tag completeness scores for all resources
    tag_fields = ['Department', 'Project', 'Environment', 'Owner', 'CostCenter', 'CreatedBy']
    available_tags = [tag for tag in tag_fields if tag in df_clean.columns]
    
    # REQ-011: Create Tag Completeness Score per resource
    df_with_scores = df_clean.copy()
    df_with_scores['tag_completeness_score'] = df_with_scores[available_tags].notna().sum(axis=1)
    df_with_scores['tag_completeness_pct'] = (df_with_scores['tag_completeness_score'] / len(available_tags) * 100)
    
    # Key compliance metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        avg_completeness = df_with_scores['tag_completeness_pct'].mean()
        st.metric("Avg Tag Completeness", f"{avg_completeness:.1f}%")
    with col2:
        perfect_tagged = len(df_with_scores[df_with_scores['tag_completeness_score'] == len(available_tags)])
        st.metric("Fully Tagged Resources", f"{perfect_tagged:,}")
    with col3:
        untagged_resources = len(df_clean[df_clean['Tagged'] == 'No'])
        st.metric("Untagged Resources", f"{untagged_resources:,}")
    with col4:
        critical_resources = len(df_with_scores[df_with_scores['tag_completeness_score'] <= 2])
        st.metric("Critical Gap Resources", f"{critical_resources:,}")
    
    # REQ-013: Identify most frequently missing tag fields
    st.subheader("📊 Missing Tag Field Analysis")
    missing_analysis = pd.DataFrame({
        'Tag Field': available_tags,
        'Missing Count': [df_clean[tag].isna().sum() for tag in available_tags],
        'Missing Percentage': [df_clean[tag].isna().sum() / len(df_clean) * 100 for tag in available_tags]
    }).sort_values('Missing Count', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_missing = px.bar(missing_analysis, x='Tag Field', y='Missing Count',
                           title='Missing Tag Fields Analysis',
                           color='Missing Percentage',
                           color_continuous_scale='Reds')
        st.plotly_chart(fig_missing, use_container_width=True)
    
    with col2:
        st.dataframe(missing_analysis, hide_index=True)
    
    # REQ-012: Find top 5 resources with lowest completeness
    st.subheader("🚨 Resources with Lowest Tag Completeness")
    lowest_completeness = df_with_scores.nsmallest(5, 'tag_completeness_score')[
        ['ResourceID', 'Service', 'MonthlyCostUSD', 'tag_completeness_score', 'tag_completeness_pct']
    ]
    st.dataframe(lowest_completeness, hide_index=True)
    
    # REQ-014: List all untagged resources with costs
    st.subheader("💸 Untagged Resources Impact")
    untagged_df = df_clean[df_clean['Tagged'] == 'No'][
        ['ResourceID', 'Service', 'Region', 'Department', 'MonthlyCostUSD']
    ].sort_values('MonthlyCostUSD', ascending=False)
    
    if len(untagged_df) > 0:
        st.write(f"**{len(untagged_df)} untagged resources** costing **${untagged_df['MonthlyCostUSD'].sum():,.2f}/month**")
        st.dataframe(untagged_df.head(10), hide_index=True)
        
        # REQ-015: Export untagged resources to CSV
        csv_data = untagged_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Untagged Resources CSV",
            data=csv_data,
            file_name="untagged_resources.csv",
            mime="text/csv",
            help="Download complete list of untagged resources for remediation"
        )
    else:
        st.success("✅ No untagged resources found!")
    
    # Compliance heatmap by service and department
    st.subheader("🔥 Compliance Heatmap")
    
    # Debug: Show raw compliance data
    st.write("**Debug: Raw Compliance Data**")
    heatmap_data = df_clean.groupby(['Service', 'Department']).agg({
        'Tagged': lambda x: (x == 'Yes').sum() / len(x) * 100,
        'ResourceID': 'count'
    }).reset_index()
    st.dataframe(heatmap_data.head(10))
    
    # Use a lower threshold for filtering (only exclude single-resource groups)
    heatmap_data = heatmap_data[heatmap_data['ResourceID'] >= 1]  # Keep all groups
    
    if len(heatmap_data) > 0:
        heatmap_pivot = heatmap_data.pivot(index='Service', columns='Department', values='Tagged')
        
        # Calculate actual min and max values for proper scaling
        min_compliance = heatmap_pivot.min().min()
        max_compliance = heatmap_pivot.max().max()
        
        # Create heatmap with proper scaling
        fig_heatmap = px.imshow(heatmap_pivot, 
                              title=f'Tag Compliance by Service & Department (%) - Range: {min_compliance:.1f}% to {max_compliance:.1f}%',
                              color_continuous_scale='RdYlGn',
                              aspect='auto',
                              zmin=min_compliance,
                              zmax=max_compliance,
                              labels={'color': 'Compliance %'})
        
        # Add text annotations showing the actual values
        fig_heatmap.update_traces(
            text=heatmap_pivot.round(1).astype(str) + '%',
            texttemplate='%{text}',
            textfont={"size": 10},
            showscale=True
        )
        
        # Improve layout
        fig_heatmap.update_layout(
            title_x=0.5,
            xaxis_title="Department",
            yaxis_title="Service",
            coloraxis_colorbar=dict(
                title="Compliance Rate (%)",
                title_side="right"
            )
        )
        
        st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Add summary statistics below the heatmap
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Minimum Compliance", f"{min_compliance:.1f}%")
        with col2:
            st.metric("Maximum Compliance", f"{max_compliance:.1f}%")
        with col3:
            avg_compliance = heatmap_pivot.mean().mean()
            st.metric("Average Compliance", f"{avg_compliance:.1f}%")
        with col4:
            compliance_range = max_compliance - min_compliance
            st.metric("Compliance Range", f"{compliance_range:.1f}%")

def show_remediation_workflow_page(df_clean):
    """Remediation Workflow page - Task Set 5 implementation (REQ-021 to REQ-025)"""
    st.header("🔧 Remediation Workflow")
    st.markdown("**Interactive Tag Remediation and Impact Analysis**")
    
    # Initialize session state for remediation tracking with unique session key
    session_key = f"remediation_session_{id(df_clean)}"
    
    if 'remediation_initialized' not in st.session_state:
        st.session_state.remediated_df = df_clean.copy()
        st.session_state.remediation_history = []
        st.session_state.original_df = df_clean.copy()  # Keep original for comparison
        st.session_state.remediation_initialized = True
    
    # Use the original df for baseline comparison, not the current df_clean
    original_untagged = len(st.session_state.original_df[st.session_state.original_df['Tagged'] == 'No'])
    current_untagged = len(st.session_state.remediated_df[st.session_state.remediated_df['Tagged'] == 'No'])
    remediated_count = original_untagged - current_untagged
    
    # REQ-024: Compare cost visibility before/after remediation
    st.subheader("📊 Remediation Impact Dashboard")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Original Untagged", f"{original_untagged:,}")
    with col2:
        st.metric("Currently Untagged", f"{current_untagged:,}", f"-{remediated_count}")
    with col3:
        original_untagged_cost = st.session_state.original_df[st.session_state.original_df['Tagged'] == 'No']['MonthlyCostUSD'].sum()
        current_untagged_cost = st.session_state.remediated_df[st.session_state.remediated_df['Tagged'] == 'No']['MonthlyCostUSD'].sum()
        cost_recovered = original_untagged_cost - current_untagged_cost
        st.metric("Cost Visibility Recovered", f"${cost_recovered:,.2f}")
    with col4:
        progress_pct = (remediated_count / original_untagged * 100) if original_untagged > 0 else 0
        st.metric("Remediation Progress", f"{progress_pct:.1f}%")
    
    # Progress visualization
    if remediated_count > 0:
        progress_data = pd.DataFrame({
            'Status': ['Remediated', 'Still Untagged'],
            'Count': [remediated_count, current_untagged],
            'Cost': [cost_recovered, current_untagged_cost]
        })
        
        col1, col2 = st.columns(2)
        with col1:
            fig_progress = px.pie(progress_data, values='Count', names='Status',
                                title='Remediation Progress by Resource Count',
                                color_discrete_map={'Remediated': '#2E8B57', 'Still Untagged': '#DC143C'})
            st.plotly_chart(fig_progress, use_container_width=True)
        
        with col2:
            fig_cost = px.pie(progress_data, values='Cost', names='Status',
                            title='Cost Visibility Recovery',
                            color_discrete_map={'Remediated': '#2E8B57', 'Still Untagged': '#DC143C'})
            st.plotly_chart(fig_cost, use_container_width=True)
    
    # REQ-021: Create editable table for untagged resources
    st.subheader("✏️ Interactive Tag Editor")
    
    # Filter untagged resources for editing
    untagged_resources = st.session_state.remediated_df[st.session_state.remediated_df['Tagged'] == 'No'].copy()
    
    if len(untagged_resources) > 0:
        st.write(f"**{len(untagged_resources)} resources** need tag remediation:")
        
        # Select resources to remediate
        st.write("**Step 1**: Select resources to remediate")
        resource_options = untagged_resources['ResourceID'].tolist()
        selected_resources = st.multiselect(
            "Choose resources to edit:",
            resource_options,
            help="Select one or more resources to add tags"
        )
        
        if selected_resources:
            st.write("**Step 2**: Fill in missing tags")
            selected_df = untagged_resources[untagged_resources['ResourceID'].isin(selected_resources)]
            
            # REQ-022: Fill missing tags manually - Department, Project, Owner fields editable
            editable_columns = ['Department', 'Project', 'Environment', 'Owner', 'CostCenter', 'CreatedBy']
            display_columns = ['ResourceID', 'Service', 'Region', 'MonthlyCostUSD'] + editable_columns
            
            # Create editable dataframe
            edited_df = st.data_editor(
                selected_df[display_columns],
                key="resource_editor",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ResourceID": st.column_config.TextColumn("Resource ID", disabled=True),
                    "Service": st.column_config.TextColumn("Service", disabled=True),
                    "Region": st.column_config.TextColumn("Region", disabled=True),
                    "MonthlyCostUSD": st.column_config.NumberColumn("Monthly Cost ($)", disabled=True, format="$%.2f"),
                    "Department": st.column_config.SelectboxColumn("Department", 
                        options=["Marketing", "Sales", "Analytics", "Finance", "Engineering", "Operations"]),
                    "Project": st.column_config.TextColumn("Project"),
                    "Environment": st.column_config.SelectboxColumn("Environment", 
                        options=["Prod", "Dev", "Test", "Staging"]),
                    "Owner": st.column_config.TextColumn("Owner (email)"),
                    "CostCenter": st.column_config.TextColumn("Cost Center"),
                    "CreatedBy": st.column_config.SelectboxColumn("Created By", 
                        options=["Terraform", "Jenkins", "CloudFormation", "Manual", "Ansible"])
                }
            )
            
            # Apply remediation button
            col1, col2 = st.columns([1, 3])
            with col1:
                if st.button("✅ Apply Tag Updates", type="primary"):
                    # Update the main dataframe
                    for _, row in edited_df.iterrows():
                        resource_id = row['ResourceID']
                        mask = st.session_state.remediated_df['ResourceID'] == resource_id
                        
                        # Update all editable fields
                        for col in editable_columns:
                            if pd.notna(row[col]) and str(row[col]).strip():
                                st.session_state.remediated_df.loc[mask, col] = row[col]
                        
                        # Check if resource is now fully tagged
                        resource_row = st.session_state.remediated_df.loc[mask]
                        tag_completeness = resource_row[editable_columns].notna().sum().iloc[0]
                        
                        if tag_completeness >= 4:  # At least 4 out of 6 tags filled
                            st.session_state.remediated_df.loc[mask, 'Tagged'] = 'Yes'
                            
                        # Add to remediation history
                        st.session_state.remediation_history.append({
                            'ResourceID': resource_id,
                            'Timestamp': pd.Timestamp.now(),
                            'Tags_Added': [col for col in editable_columns if pd.notna(row[col]) and str(row[col]).strip()]
                        })
                    
                    st.success(f"✅ Updated {len(edited_df)} resources!")
                    st.rerun()
            
            with col2:
                st.info("💡 **Tip**: Fill at least Department, Project, Environment, and Owner to mark a resource as 'Tagged'")
    else:
        st.success("🎉 **All resources are properly tagged!** No remediation needed.")
    
    # REQ-023: Download updated dataset
    st.subheader("📥 Export Remediated Data")
    
    col1, col2 = st.columns(2)
    with col1:
        # Download remediated dataset
        remediated_csv = st.session_state.remediated_df.to_csv(index=False)
        st.download_button(
            label="📁 Download Remediated Dataset",
            data=remediated_csv,
            file_name="remediated_cloudmart_dataset.csv",
            mime="text/csv",
            help="Download the updated dataset with your tag remediation changes"
        )
    
    with col2:
        # Download remediation history
        if st.session_state.remediation_history:
            history_df = pd.DataFrame(st.session_state.remediation_history)
            history_csv = history_df.to_csv(index=False)
            st.download_button(
                label="📋 Download Remediation Log",
                data=history_csv,
                file_name="remediation_history.csv",
                mime="text/csv",
                help="Download log of all remediation actions taken"
            )
    
    # REQ-025: Document impact of improved tagging
    st.subheader("📄 Governance Impact Report")
    
    if remediated_count > 0:
        st.markdown(f"""
        ### **Tagging Remediation Impact Analysis**
        
        **Resource Accountability Improvements:**
        - ✅ **{remediated_count}** resources now have proper ownership tracking
        - 💰 **${cost_recovered:,.2f}** monthly cost now visible in department budgets
        - 📊 **{progress_pct:.1f}%** improvement in overall compliance
        
        **Financial Governance Benefits:**
        - 🎯 **Enhanced Cost Allocation**: Departments can now track their actual cloud spend
        - 🔍 **Improved Budget Planning**: Historical costs can be properly attributed
        - ⚠️ **Risk Reduction**: Eliminated orphaned resources with unclear ownership
        
        **Operational Excellence Gains:**
        - 🏷️ **Standardized Tagging**: Consistent tag schema applied across resources
        - 🔄 **Process Improvement**: Remediation workflow establishes best practices
        - 📈 **Measurable Progress**: Clear metrics for ongoing compliance monitoring
        
        **Recommendations for Sustained Governance:**
        1. **Automate Tag Validation**: Implement tag policies in infrastructure-as-code
        2. **Monthly Compliance Reviews**: Schedule regular audits of new resources
        3. **Department Accountability**: Assign tag compliance KPIs to resource owners
        4. **Cost Allocation Rules**: Use tags for automated chargeback systems
        """)
    else:
        st.info("📝 Complete some tag remediation to see governance impact analysis.")
    
    # Reset remediation button (for testing/demo purposes)
    if st.button("🔄 Reset to Original State", help="Reset all remediation changes for testing"):
        st.session_state.remediated_df = st.session_state.original_df.copy()
        st.session_state.remediation_history = []
        st.success("🔄 Reset complete! All changes reverted.")
        st.rerun()

def show_reports_page(df_clean, metrics):
    """Reports page - Automated report generation and exports"""
    st.header("📋 Reports & Documentation")
    st.markdown("**Automated FinOps governance reports and data exports**")
    
    # Generate report data
    with st.spinner("Generating comprehensive reports..."):
        report_data = generate_report_data(df_clean, metrics)
    
    # Key report metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Report Sections", "4")
    with col2:
        untagged_count = len(df_clean[df_clean['Tagged'] == 'No'])
        st.metric("Untagged Resources", f"{untagged_count:,}")
    with col3:
        total_cost = df_clean['MonthlyCostUSD'].sum()
        st.metric("Total Monthly Cost", f"${total_cost:,.2f}")
    with col4:
        compliance_rate = metrics.get('compliance_rate', 0)
        st.metric("Compliance Rate", f"{compliance_rate:.1f}%")
    
    # Report tabs
    tab1, tab2, tab3 = st.tabs(["📊 Executive Report", "📥 Data Exports", "📈 Quick Insights"])
    
    with tab1:
        st.subheader("📋 Executive Summary Report")
        st.markdown("Complete FinOps governance analysis with recommendations")
        
        # Display the markdown report
        st.markdown(report_data['markdown_report'])
        
        # Download full report
        st.download_button(
            label="📄 Download Full Report (Markdown)",
            data=report_data['markdown_report'],
            file_name=f"cloudmart_finops_report_{report_data['generation_timestamp']}.md",
            mime="text/markdown",
            help="Download the complete FinOps governance report in Markdown format",
            type="primary"
        )
    
    with tab2:
        st.subheader("📥 Data Export Center")
        st.markdown("Download specific datasets for further analysis and remediation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🚨 Untagged Resources")
            untagged_count = len(df_clean[df_clean['Tagged'] == 'No'])
            st.write(f"Export {untagged_count} untagged resources for immediate remediation")
            
            st.download_button(
                label="📥 Download Untagged Resources",
                data=report_data['untagged_csv'],
                file_name=f"untagged_resources_{report_data['generation_timestamp']}.csv",
                mime="text/csv",
                help="Resources requiring immediate tag remediation"
            )
            
            st.markdown("### 📊 Compliance Summary")
            st.write("Department-level compliance metrics and costs")
            
            st.download_button(
                label="📥 Download Compliance Summary",
                data=report_data['compliance_csv'],
                file_name=f"compliance_summary_{report_data['generation_timestamp']}.csv",
                mime="text/csv",
                help="Department compliance rates and untagged costs"
            )
        
        with col2:
            st.markdown("### 🔍 Enhanced Dataset")
            st.write("Complete dataset with calculated compliance scores and risk categories")
            
            st.download_button(
                label="📥 Download Enhanced Analysis",
                data=report_data['full_analysis_csv'],
                file_name=f"enhanced_cloudmart_analysis_{report_data['generation_timestamp']}.csv",
                mime="text/csv",
                help="Full dataset with tag completeness scores and risk analysis"
            )
            
            st.markdown("### 📋 Report Package")
            st.write("All reports and data files in a single download")
            
            # Create a summary of all available downloads
            downloads_summary = f"""
# CloudMart FinOps Report Package
Generated: {report_data['generation_timestamp']}

## Included Files:
1. Executive Report (Markdown)
2. Untagged Resources (CSV)
3. Compliance Summary (CSV)  
4. Enhanced Analysis (CSV)

## Key Metrics:
- Total Resources: {len(df_clean):,}
- Untagged Resources: {untagged_count:,}
- Compliance Rate: {compliance_rate:.1f}%
- Total Monthly Cost: ${total_cost:,.2f}
"""
            
            st.download_button(
                label="📦 Download Report Summary",
                data=downloads_summary,
                file_name=f"report_package_summary_{report_data['generation_timestamp']}.txt",
                mime="text/plain",
                help="Summary of all available reports and exports"
            )
    
    with tab3:
        st.subheader("📈 Quick Insights Dashboard")
        st.markdown("Key findings and actionable recommendations")
        
        # Quick insights based on data analysis
        total_resources = len(df_clean)
        untagged_resources = len(df_clean[df_clean['Tagged'] == 'No'])
        untagged_cost = df_clean[df_clean['Tagged'] == 'No']['MonthlyCostUSD'].sum()
        total_cost = df_clean['MonthlyCostUSD'].sum()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🎯 Priority Actions")
            
            # Most expensive untagged resources
            if untagged_resources > 0:
                expensive_untagged = df_clean[df_clean['Tagged'] == 'No'].nlargest(5, 'MonthlyCostUSD')
                st.markdown("**🚨 Most Expensive Untagged Resources:**")
                for _, row in expensive_untagged.iterrows():
                    st.write(f"• {row['ResourceID']} ({row['Service']}) - ${row['MonthlyCostUSD']:,.2f}/month")
            
            # Worst performing departments
            if 'Department' in df_clean.columns:
                dept_untagged = df_clean[df_clean['Tagged'] == 'No'].groupby('Department')['MonthlyCostUSD'].sum().sort_values(ascending=False)
                if len(dept_untagged) > 0:
                    st.markdown("**🏢 Departments Needing Focus:**")
                    for dept, cost in dept_untagged.head(3).items():
                        st.write(f"• {dept}: ${cost:,.2f}/month untagged")
        
        with col2:
            st.markdown("#### 📊 Success Metrics")
            
            # Calculate compliance improvements needed
            target_compliance = 95
            current_compliance = (total_resources - untagged_resources) / total_resources * 100
            resources_to_tag = max(0, total_resources - int(total_resources * target_compliance / 100))
            
            st.metric("Current Compliance", f"{current_compliance:.1f}%")
            st.metric("Target Compliance", f"{target_compliance}%")
            st.metric("Resources to Tag", f"{resources_to_tag}")
            
            # ROI calculation
            annual_untagged = untagged_cost * 12
            st.markdown(f"**💰 Annual Cost Visibility Gap:** ${annual_untagged:,.2f}")
            
            if untagged_cost > 0:
                # Assume 15% cost optimization potential once tagged
                potential_savings = annual_untagged * 0.15
                st.markdown(f"**💡 Potential Annual Savings:** ${potential_savings:,.2f}")
        
        # Action recommendations based on data
        st.markdown("#### 🎯 Recommended Next Steps")
        
        recommendations = []
        
        if untagged_resources > total_resources * 0.5:
            recommendations.append("🚨 **Critical**: >50% resources untagged - Implement emergency tagging campaign")
        
        if 'CreatedBy' in df_clean.columns:
            manual_untagged = len(df_clean[(df_clean['CreatedBy'] == 'Manual') & (df_clean['Tagged'] == 'No')])
            if manual_untagged > 0:
                recommendations.append(f"⚙️ **Process**: {manual_untagged} manually-created resources are untagged - Implement IaC governance")
        
        if 'Environment' in df_clean.columns:
            prod_untagged = len(df_clean[(df_clean['Environment'] == 'Prod') & (df_clean['Tagged'] == 'No')])
            if prod_untagged > 0:
                recommendations.append(f"🔴 **Production Risk**: {prod_untagged} production resources untagged - High priority remediation needed")
        
        if untagged_cost > total_cost * 0.3:
            recommendations.append("💰 **Financial**: >30% of costs untrackable - Implement immediate chargeback policies")
        
        if len(recommendations) == 0:
            recommendations.append("✅ **Excellent**: Low risk detected - Focus on maintaining current compliance levels")
        
        for rec in recommendations:
            st.write(rec)

# --- Main Application ---
def main():
    st.title("💰 CloudMart FinOps Dashboard")
    st.markdown("**Enterprise Cloud Cost & Compliance Governance Platform**")
    
    # --- Sidebar Navigation and Controls (REQ-020, REQ-021) ---
    st.sidebar.title("🧭 Navigation")
    
    # Data Processing Options
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ Data Processing")
    
    # Duplicate handling toggle
    remove_duplicates = st.sidebar.checkbox(
        "🔄 Remove Duplicate Records", 
        value=True,
        help="Uncheck to keep duplicate records (useful for intentional duplicates or testing)"
    )
    
    # Show processing status
    if remove_duplicates:
        st.sidebar.success("✅ Duplicates will be removed")
    else:
        st.sidebar.warning("⚠️ Keeping duplicate records")
    
    st.sidebar.markdown("---")
    
    page = st.sidebar.radio("Select Dashboard Section:", [
        "📊 Overview", "💰 Cost Analysis", "🛡️ Compliance", "🔧 Remediation", "📋 Reports"
    ])
    
    # --- Data Loading & Validation ---
    df_original = load_data("./data/cloudmart_multi_account_cleaned.csv")
    if df_original is None:
        st.error("❌ Could not load CloudMart dataset. Check file path.")
        st.stop()
    
    # Apply CHUNK 1 validation with duplicate handling preference
    df_clean, metrics = validate_cloudmart_data(df_original, remove_duplicates=remove_duplicates)
    if df_clean is None:
        st.error("❌ Data validation failed. Check data quality.")
        st.stop()
    
    # --- Page Routing ---
    if page == "📊 Overview":
        show_overview_page(df_clean, metrics)
    elif page == "💰 Cost Analysis":
        show_cost_analysis_page(df_clean)
    elif page == "🛡️ Compliance":
        show_compliance_analysis_page(df_clean, metrics)
    elif page == "🔧 Remediation":
        show_remediation_workflow_page(df_clean)
    elif page == "📋 Reports":
        show_reports_page(df_clean, metrics)

if __name__ == "__main__":
    main()