"""
FinOps Data Validation and Deduplication Module
Addresses REQ-016 through REQ-019: Data quality and validation requirements
"""
import pandas as pd
import streamlit as st
from typing import Tuple, Dict

@st.cache_data
def validate_and_deduplicate_data(df: pd.DataFrame, remove_duplicates: bool = True) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Core data validation and optional deduplication for CloudMart dataset.
    
    Args:
        df: Input DataFrame to validate
        remove_duplicates: Whether to remove duplicate records (default: True)
    
    Returns:
        - Cleaned dataframe (with or without duplicates based on preference)
        - Validation metrics dictionary
    """
    if df is None or df.empty:
        return None, {"error": "Empty dataset"}
    
    # Store original metrics
    original_count = len(df)
    
    # Identify duplicates by ResourceID (primary business key)
    duplicate_mask = df.duplicated(subset=['ResourceID'], keep='first')
    duplicate_count = duplicate_mask.sum()
    
    if remove_duplicates:
        # Remove duplicates, keeping first occurrence
        df_clean = df[~duplicate_mask].copy()
        processing_note = f"Removed {duplicate_count} duplicate records"
    else:
        # Keep all records including duplicates
        df_clean = df.copy()
        processing_note = f"Kept all records including {duplicate_count} duplicates"
    
    # Calculate compliance rate (tagged resources)
    tagged_resources = len(df_clean[df_clean['Tagged'] == 'Yes'])
    compliance_rate = (tagged_resources / len(df_clean) * 100) if len(df_clean) > 0 else 0
    
    # Calculate total monthly cost
    total_cost = df_clean['MonthlyCostUSD'].sum()
    
    # Validation metrics
    metrics = {
        "original_records": original_count,
        "duplicate_records": duplicate_count,
        "unique_resources": len(df_clean),
        "duplication_rate": (duplicate_count / original_count * 100) if original_count > 0 else 0,
        "compliance_rate": round(compliance_rate, 1),
        "total_monthly_cost": round(total_cost, 2),
        "duplicates_removed": remove_duplicates,
        "processing_note": processing_note
    }
    
    return df_clean, metrics

def validate_required_fields(df: pd.DataFrame) -> Dict[str, float]:
    """Validate completeness of required tagging fields"""
    required_fields = ['Department', 'Project', 'Environment', 'Owner']
    completeness = {}
    
    for field in required_fields:
        if field in df.columns:
            non_null = df[field].notna().sum()
            completeness[field] = (non_null / len(df) * 100) if len(df) > 0 else 0
            
    return completeness

def validate_cloudmart_data(df: pd.DataFrame, remove_duplicates: bool = True) -> Tuple[pd.DataFrame, Dict[str, any]]:
    """
    Main CloudMart data validation function for CHUNK 1 integration.
    Returns validated data and comprehensive metrics for dashboard use.
    
    Args:
        df: Input DataFrame to validate
        remove_duplicates: Whether to remove duplicate records (default: True)
    """
    if df is None or df.empty:
        return None, {"error": "No data provided"}
    
    # Apply core validation and optional deduplication
    clean_df, metrics = validate_and_deduplicate_data(df, remove_duplicates=remove_duplicates)
    
    if clean_df is None:
        return None, metrics
    
    # Add field completeness analysis
    field_completeness = validate_required_fields(clean_df)
    metrics["field_completeness"] = field_completeness
    
    # Add summary stats for dashboard
    metrics["total_resources"] = len(clean_df)
    metrics["untagged_resources"] = len(clean_df[clean_df['Tagged'] == 'No'])
    
    # Adjust data quality score calculation based on duplicate handling
    if remove_duplicates:
        metrics["data_quality_score"] = round((100 - metrics["duplication_rate"]) * 0.7 + metrics["compliance_rate"] * 0.3, 1)
    else:
        # When keeping duplicates, focus more on compliance rate
        metrics["data_quality_score"] = round(metrics["compliance_rate"] * 0.8 + 20, 1)  # Base score for keeping intentional duplicates
    
    # For display purposes, fill NaN values in non-critical columns only
    # Keep NaN in tag fields for compliance analysis
    display_df = clean_df.copy()
    non_tag_cols = ['Service', 'Region', 'CostCenter']
    for col in non_tag_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].fillna('Unknown')
    
    return display_df, metrics