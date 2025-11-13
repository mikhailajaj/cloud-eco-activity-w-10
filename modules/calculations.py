import pandas as pd

def calculate_finops_metrics(df):
    """
    Calculates key FinOps metrics from a dataframe.
    - Total resources, total cost.
    - Tagging compliance percentage and cost.
    - Tag completeness score and average.
    """
    if df is None or df.empty:
        return {}, pd.DataFrame()

    metrics = {}
    
    metrics['total_resources'] = len(df)
    metrics['total_cost'] = df['MonthlyCostUSD'].sum()

    # Tagging compliance
    if 'Tagged' in df.columns:
        tagged_counts = df['Tagged'].value_counts()
        metrics['tagged_count'] = tagged_counts.get('Yes', 0)
        metrics['untagged_count'] = tagged_counts.get('No', 0)
        
        metrics['tagging_compliance_pct'] = (
            metrics['tagged_count'] / metrics['total_resources'] * 100
            if metrics['total_resources'] > 0 else 0
        )
        
        cost_by_tag = df.groupby('Tagged')['MonthlyCostUSD'].sum()
        metrics['tagged_cost'] = cost_by_tag.get('Yes', 0)
        metrics['untagged_cost'] = cost_by_tag.get('No', 0)
        
        metrics['untagged_cost_pct'] = (
            metrics['untagged_cost'] / metrics['total_cost'] * 100
            if metrics['total_cost'] > 0 else 0
        )
    else:
        # Default metrics if 'Tagged' column is missing
        metrics['tagged_count'] = 0
        metrics['untagged_count'] = metrics['total_resources']
        metrics['tagging_compliance_pct'] = 0
        metrics['tagged_cost'] = 0
        metrics['untagged_cost'] = metrics['total_cost']
        metrics['untagged_cost_pct'] = 100

    # Tag Completeness Score
    tag_fields = ['Department', 'Project', 'Environment', 'Owner', 'CostCenter', 'CreatedBy']
    available_tags = [tag for tag in tag_fields if tag in df.columns]
    
    df_with_scores = df.copy()
    if available_tags:
        # Use .notna() and .ne('Unknown') to be more robust
        df_with_scores['tag_completeness_score'] = df_with_scores[available_tags].notna().sum(axis=1)
        df_with_scores['tag_completeness_pct'] = (
            df_with_scores['tag_completeness_score'] / len(available_tags) * 100
        )
        metrics['avg_completeness_pct'] = df_with_scores['tag_completeness_pct'].mean()
    else:
        df_with_scores['tag_completeness_score'] = 0
        df_with_scores['tag_completeness_pct'] = 0
        metrics['avg_completeness_pct'] = 0
        
    return metrics, df_with_scores

def calculate_historical_trends(historical_df):
    """
    Calculates monthly trends for cost and tagging compliance.
    """
    if historical_df is None or 'Date' not in historical_df.columns:
        return None

    historical_df['Date'] = pd.to_datetime(historical_df['Date'])
    monthly_summary = historical_df.groupby(historical_df['Date'].dt.to_period('M')).agg(
        TotalCost=('MonthlyCostUSD', 'sum'),
        TotalResources=('ResourceID', 'count')
    ).reset_index()

    # Calculate tagging compliance per month
    tagged_counts = historical_df[historical_df['Tagged'] == 'Yes'].groupby(historical_df['Date'].dt.to_period('M')).size()
    monthly_summary = monthly_summary.set_index('Date')
    monthly_summary['TaggedCount'] = tagged_counts
    monthly_summary = monthly_summary.reset_index()
    monthly_summary['TaggedCount'] = monthly_summary['TaggedCount'].fillna(0)
    
    monthly_summary['TaggingCompliance'] = (
        monthly_summary['TaggedCount'] / monthly_summary['TotalResources'] * 100
    )
    
    monthly_summary['Date'] = monthly_summary['Date'].dt.strftime('%Y-%m')
    
    return monthly_summary

