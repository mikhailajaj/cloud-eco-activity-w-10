import plotly.express as px
import plotly.graph_objects as go

# --- Standard Visualizations ---

def plot_tagging_status(df):
    """Creates a pie chart of tagged vs untagged resources."""
    if 'Tagged' not in df.columns or df.empty:
        return go.Figure().add_annotation(text="Not enough data for 'Tagging Status' chart.", showarrow=False)
    
    tagged_counts = df['Tagged'].value_counts().reset_index()
    tagged_counts.columns = ['Status', 'Count']
    
    fig = px.pie(
        tagged_counts,
        values='Count',
        names='Status',
        title="Resource Tagging Status",
        color='Status',
        color_discrete_map={'Yes': '#2ca02c', 'No': '#d62728'},
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(legend_title_text='Status')
    return fig

def plot_cost_by_department_tagging(df):
    """Plots a bar chart showing cost per department by tagging status."""
    if 'Department' not in df.columns or 'Tagged' not in df.columns or df.empty:
        return go.Figure().add_annotation(text="Not enough data for 'Cost by Department' chart.", showarrow=False)
    
    dept_cost = df.groupby(['Department', 'Tagged'])['MonthlyCostUSD'].sum().reset_index()
    
    fig = px.bar(
        dept_cost,
        x='Department',
        y='MonthlyCostUSD',
        color='Tagged',
        barmode='group',
        title="Cost by Department (Tagged vs Untagged)",
        labels={'MonthlyCostUSD': 'Monthly Cost (USD)'},
        color_discrete_map={'Yes': '#2ca02c', 'No': '#d62728'}
    )
    fig.update_layout(xaxis_title="Department", yaxis_title="Monthly Cost (USD)", legend_title_text='Status')
    return fig

def plot_cost_by_service(df):
    """Shows a horizontal bar chart of total cost per service."""
    if 'Service' not in df.columns or df.empty:
        return go.Figure().add_annotation(text="Not enough data for 'Cost by Service' chart.", showarrow=False)
    
    service_cost = df.groupby('Service')['MonthlyCostUSD'].sum().sort_values(ascending=True).reset_index()
    
    fig = px.bar(
        service_cost.tail(15), # Show top 15 services
        x='MonthlyCostUSD',
        y='Service',
        orientation='h',
        title="Top 15 Services by Cost",
        labels={'MonthlyCostUSD': 'Monthly Cost (USD)', 'Service': 'Service'}
    )
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    return fig

def plot_cost_by_environment(df):
    """Visualizes cost by environment (Prod, Dev, Test)."""
    if 'Environment' not in df.columns or df.empty:
        return go.Figure().add_annotation(text="Not enough data for 'Cost by Environment' chart.", showarrow=False)
    
    env_cost = df.groupby('Environment')['MonthlyCostUSD'].sum().reset_index()
    
    fig = px.pie(
        env_cost,
        values='MonthlyCostUSD',
        names='Environment',
        title="Cost Distribution by Environment",
        hole=0.3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

# --- New Historical Trend Visualizations ---

def plot_historical_cost_trend(monthly_summary):
    """
    Plots a line chart showing the total cloud cost over the past few months.
    """
    if monthly_summary is None or monthly_summary.empty:
        return go.Figure().add_annotation(text="Not enough data for 'Historical Cost Trend' chart.", showarrow=False)

    fig = px.line(
        monthly_summary,
        x='Date',
        y='TotalCost',
        title='Monthly Cloud Cost Trend',
        markers=True,
        labels={'TotalCost': 'Total Monthly Cost (USD)', 'Date': 'Month'}
    )
    fig.update_layout(xaxis_title="Month", yaxis_title="Total Cost (USD)")
    return fig

def plot_historical_compliance_trend(monthly_summary):
    """
    Plots a line chart showing the tagging compliance percentage over time.
    """
    if monthly_summary is None or monthly_summary.empty:
        return go.Figure().add_annotation(text="Not enough data for 'Historical Compliance Trend' chart.", showarrow=False)

    fig = px.line(
        monthly_summary,
        x='Date',
        y='TaggingCompliance',
        title='Monthly Tagging Compliance Trend',
        markers=True,
        labels={'TaggingCompliance': 'Compliance (%)', 'Date': 'Month'}
    )
    fig.update_layout(yaxis_range=[0, 100], xaxis_title="Month", yaxis_title="Tagging Compliance (%)")
    return fig
