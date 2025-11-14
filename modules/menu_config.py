"""
Menu Configuration Module for FinOps Dashboard
Centralized menu and navigation configuration for better maintainability
"""

# Dashboard Navigation Menu
DASHBOARD_SECTIONS = [
    "📊 Overview",
    "💰 Cost Analysis", 
    "🛡️ Compliance",
    "🔧 Remediation",
    "🔍 Missing Data Analytics",
    "📋 Reports"
]

# Filter Configuration
FILTER_GROUPS = {
    "core_governance": {
        "title": "**Core Governance Filters:**",
        "filters": [
            {
                "key": "department",
                "label": "🏢 Department",
                "help": "Filter by business unit (Marketing, Sales, Analytics, etc.)",
                "column": "Department"
            },
            {
                "key": "project", 
                "label": "📋 Project",
                "help": "Filter by application or project name",
                "column": "Project"
            },
            {
                "key": "environment",
                "label": "🌍 Environment", 
                "help": "Filter by environment type (Prod, Dev, Test)",
                "column": "Environment"
            },
            {
                "key": "service",
                "label": "☁️ Cloud Service",
                "help": "Filter by AWS service type (EC2, S3, RDS, etc.)",
                "column": "Service"
            },
            {
                "key": "region",
                "label": "🌐 Region",
                "help": "Filter by AWS region", 
                "column": "Region"
            }
        ]
    },
    "operational": {
        "title": "**Operational Filters:**",
        "filters": [
            {
                "key": "created_by",
                "label": "⚙️ Created By",
                "help": "Filter by creation method (Terraform, Jenkins, Manual, etc.)",
                "column": "CreatedBy"
            },
            {
                "key": "tagging_status",
                "label": "🏷️ Tagging Status",
                "help": "Filter by tagging compliance status",
                "type": "selectbox",
                "options": ['All', 'Tagged Only', 'Untagged Only']
            }
        ]
    },
    "financial": {
        "title": "**Financial Filters:**",
        "filters": [
            {
                "key": "cost_range",
                "label": "💰 Cost Range (USD/month)",
                "help": "Filter by monthly cost range (includes 20% buffer above max)",
                "type": "slider",
                "column": "MonthlyCostUSD",
                "step": 5.0
            },
            {
                "key": "owner",
                "label": "👤 Resource Owner",
                "help": "Filter by resource owner",
                "column": "Owner",
                "limit": 20
            },
            {
                "key": "cost_center",
                "label": "💼 Cost Center", 
                "help": "Filter by accounting cost center",
                "column": "CostCenter"
            }
        ]
    }
}

# Quick Filter Presets
QUICK_PRESETS = [
    {
        "label": "🚨 Critical Issues",
        "help": "Show untagged production resources",
        "filters": {
            "environment": ["Prod"],
            "tagging_status": "Untagged Only"
        }
    },
    {
        "label": "🏭 Production Only", 
        "help": "Show all production resources",
        "filters": {
            "environment": ["Prod"]
        }
    },
    {
        "label": "🔧 Manual Resources",
        "help": "Show manually created resources", 
        "filters": {
            "created_by": ["Manual"]
        }
    },
    {
        "label": "💸 High Cost",
        "help": "Show resources costing >$100/month",
        "filters": {
            "cost_min": 100.0
        }
    }
]

# Export Configuration
EXPORT_CONFIG = {
    "filename_prefix": "cloudmart_filtered_data",
    "timestamp_format": "%Y%m%d_%H%M%S",
    "file_extension": "csv"
}

# UI Configuration
UI_CONFIG = {
    "sidebar_title": "🧭 Navigation",
    "data_processing_title": "⚙️ Data Processing", 
    "advanced_filters_title": "🎯 Advanced Filters",
    "data_export_title": "📁 Data Export",
    "cost_range_defaults": {
        "min": 0.0,
        "max": 301.0,  # Based on current data max ($300) + 1
        "buffer_type": "plus_one"  # Changed from multiplier to +1
    }
}

def get_dashboard_sections():
    """Get the list of dashboard sections"""
    return DASHBOARD_SECTIONS

def get_filter_groups():
    """Get the filter group configuration"""
    return FILTER_GROUPS

def get_quick_presets():
    """Get the quick filter presets"""
    return QUICK_PRESETS

def get_export_config():
    """Get the export configuration"""
    return EXPORT_CONFIG

def get_ui_config():
    """Get the UI configuration"""
    return UI_CONFIG