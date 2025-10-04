#!/usr/bin/env python3
"""
Script to create sample tasks.xlsx file for the MCP server demo.
"""

import pandas as pd
from datetime import datetime, timedelta

def create_sample_tasks():
    """Create sample tasks data and save to Excel file."""
    
    # Create sample tasks data
    tasks_data = {
        'id': [1, 2, 3, 4, 5, 6, 7, 8],
        'title': [
            'Complete project documentation',
            'Review code changes',
            'Update database schema',
            'Fix authentication bug',
            'Deploy to production',
            'Setup monitoring dashboard',
            'Optimize database queries',
            'Write unit tests'
        ],
        'description': [
            'Write comprehensive documentation for the new API endpoints',
            'Review pull request #123 for security vulnerabilities',
            'Add new user fields to the database',
            'Fix login issue reported by users',
            'Deploy version 2.1.0 to production servers',
            'Configure Grafana dashboard for system metrics',
            'Optimize slow queries identified in performance testing',
            'Add test coverage for authentication module'
        ],
        'status': ['pending', 'done', 'pending', 'in_progress', 'pending', 'done', 'pending', 'in_progress'],
        'priority': ['high', 'medium', 'low', 'high', 'medium', 'low', 'high', 'medium'],
        'assigned_to': ['John Doe', 'Jane Smith', 'Bob Wilson', 'Alice Brown', 'Charlie Davis', 'David Lee', 'Emma Taylor', 'Frank Miller'],
        'created_date': [
            '2024-01-15', '2024-01-14', '2024-01-16', '2024-01-13', 
            '2024-01-17', '2024-01-12', '2024-01-18', '2024-01-16'
        ],
        'due_date': [
            '2024-01-20', '2024-01-15', '2024-01-25', '2024-01-18', 
            '2024-01-22', '2024-01-14', '2024-01-24', '2024-01-19'
        ]
    }
    
    # Create DataFrame and save to Excel
    df = pd.DataFrame(tasks_data)
    df.to_excel('tasks.xlsx', index=False)
    print("✅ Sample tasks.xlsx file created successfully!")
    print(f"📊 Created {len(df)} sample tasks with various statuses")
    return df

if __name__ == "__main__":
    create_sample_tasks()