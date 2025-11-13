import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

@st.cache_data
def load_data(file_path):
    """
    Loads the dataset from a CSV file with error handling and preprocessing.
    - Maps 'Tagged' column to consistent 'Yes'/'No' values.
    - Fills NaN in key categorical columns with 'Unknown'.
    """
    try:
        # Read CSV with proper handling for quoted data format
        # The CloudMart CSV has each row wrapped in quotes, so we need special handling
        df = pd.read_csv(file_path, quoting=1)  # QUOTE_ALL
        
        # Check if we have a single column (malformed CSV detection)
        if len(df.columns) == 1 and ',' in df.columns[0]:
            # The header row is quoted as a single string, need to split
            header_str = df.columns[0]
            columns = header_str.split(',')
            
            # Re-read with proper column names
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Parse each line manually to handle quoted format
            data_rows = []
            for i, line in enumerate(lines[1:]):  # Skip header
                # Remove outer quotes and split
                clean_line = line.strip().strip('"')
                values = clean_line.split(',')
                data_rows.append(values)
            
            df = pd.DataFrame(data_rows, columns=columns)
        
        # Clean up any whitespace issues
        df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
        
        # Handle empty string values properly (convert to NaN first, then handle)
        df = df.replace('', pd.NA)
        
        # Convert MonthlyCostUSD to numeric
        if 'MonthlyCostUSD' in df.columns:
            df['MonthlyCostUSD'] = pd.to_numeric(df['MonthlyCostUSD'], errors='coerce')
        
        # Ensure 'Tagged' column is consistent
        if 'Tagged' in df.columns:
            df['Tagged'] = df['Tagged'].map({1: 'Yes', 0: 'No', 'Yes': 'Yes', 'No': 'No'}).fillna('No')
        
        # For missing tag analysis, we need to preserve NaN values initially
        # Don't fill NaN in tag fields yet - this will be handled in compliance analysis
        
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure it is in the correct directory.")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred while loading the data: {e}")
        return None

def generate_historical_data(df):
    """
    Generates sample historical data for trend analysis by simulating
    the past 6 months of cost and tagging data.
    """
    if df is None:
        return None

    historical_dfs = []
    end_date = datetime.today()

    for i in range(6, 0, -1):
        # Create a dataframe for each month
        month_df = df.copy()
        
        # Simulate date for the month
        month_date = end_date - timedelta(days=i*30)
        month_df['Date'] = month_date.strftime('%Y-%m')
        
        # Simulate cost variations (+/- 10%)
        cost_variation = 1 + (np.random.rand(len(month_df)) - 0.5) * 0.2
        month_df['MonthlyCostUSD'] *= cost_variation
        
        # Simulate tagging improvement over time
        # The older the data, the worse the tagging compliance
        untagged_probability = i / 10.0 
        is_untagged = np.random.choice([True, False], size=len(month_df), p=[untagged_probability, 1 - untagged_probability])
        month_df.loc[is_untagged, 'Tagged'] = 'No'
        
        historical_dfs.append(month_df)

    # Combine with current data
    current_month_df = df.copy()
    current_month_df['Date'] = end_date.strftime('%Y-%m')
    historical_dfs.append(current_month_df)
    
    full_history_df = pd.concat(historical_dfs, ignore_index=True)
    
    return full_history_df

