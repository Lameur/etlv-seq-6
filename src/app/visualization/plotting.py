"""
Generates visualizations for the travel analysis results.
"""

import os
import shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker

# Define the output directory for plots
VIZ_DIR = "results/visualizations"

def setup_visualization_directory():
    """Creates or clears the visualization output directory."""
    if os.path.exists(VIZ_DIR):
        # Clear existing contents
        for filename in os.listdir(VIZ_DIR):
            file_path = os.path.join(VIZ_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')
    else:
        # Create the directory if it doesn't exist
        os.makedirs(VIZ_DIR)
    print(f"Visualization directory '{VIZ_DIR}' is ready.")

def format_thousands(x, pos):
    """Format tick labels with thousands separator."""
    return f'{int(x):,}'

def plot_carbon_footprint_comparison(df_results):
    """Plots the comparison of carbon footprints by route and scenario."""
    plt.figure(figsize=(12, 8))
    carbon_data = df_results[df_results['Feasibility'] == 'Feasible'].drop_duplicates(subset=['Route', 'Scenario'])
    if carbon_data.empty:
        print("Skipping carbon footprint plot: No feasible data.")
        plt.close()
        return

    sns.barplot(x='Route', y='Carbon Footprint (kg CO2e)',
                hue='Scenario', data=carbon_data,
                palette=['#ff7675', '#74b9ff'])
    plt.title('Carbon Footprint by Route and Scenario', fontsize=16)
    plt.ylabel('Carbon Footprint (kg CO2e)', fontsize=14)
    plt.xlabel('Route', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Scenario')
    plt.xticks(rotation=0)
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))
    plt.tight_layout()
    save_path = os.path.join(VIZ_DIR, 'carbon_footprint_comparison.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved: {save_path}")
    plt.close()

def plot_carbon_per_vacation_day(df_results):
    """Plots the carbon footprint per vacation day."""
    plt.figure(figsize=(12, 8))
    carbon_per_day_data = df_results[(df_results['Feasibility'] == 'Feasible') &
                                     (df_results['Carbon per Vacation Day'].notna())].drop_duplicates(subset=['Route', 'Scenario'])
    if carbon_per_day_data.empty:
        print("Skipping carbon per day plot: No feasible data.")
        plt.close()
        return

    sns.barplot(x='Route', y='Carbon per Vacation Day',
                hue='Scenario', data=carbon_per_day_data,
                palette=['#ff7675', '#74b9ff'])
    plt.title('Carbon Footprint per Vacation Day', fontsize=16)
    plt.ylabel('kg CO2e per Day at Destination', fontsize=14)
    plt.xlabel('Route', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Scenario')
    plt.xticks(rotation=0)
    plt.tight_layout()
    save_path = os.path.join(VIZ_DIR, 'carbon_per_vacation_day.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved: {save_path}")
    plt.close()

def plot_time_distribution(df_results):
    """Plots the distribution of travel days vs. days at destination."""
    time_data = df_results[df_results['Feasibility'] == 'Feasible'].drop_duplicates(subset=['Route', 'Scenario'])
    if time_data.empty:
        print("Skipping time distribution plot: No feasible data.")
        return

    x = np.arange(len(time_data))
    width = 0.35

    fig, ax = plt.subplots(figsize=(12, 8))
    ax.bar(x - width/2, time_data['Travel Days (Round Trip)'], width, label='Travel Days', color='#e17055')
    ax.bar(x + width/2, time_data['Days at Destination'], width, label='Days at Destination', color='#00b894')

    ax.set_title('Time Distribution: Travel vs. Destination', fontsize=16)
    ax.set_ylabel('Days', fontsize=14)
    ax.set_xticks(x)
    # Ensure labels are strings
    ax.set_xticklabels([f"{row['Route']} ({row['Scenario']})" for _, row in time_data.iterrows()], rotation=45, ha='right')
    ax.legend()
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    save_path = os.path.join(VIZ_DIR, 'time_distribution.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved: {save_path}")
    plt.close(fig)

def plot_cost_comparison(df_results, accommodation_type='Hostel'):
    """Plots the total cost comparison for a specific accommodation type."""
    plt.figure(figsize=(12, 8))
    cost_data = df_results[(df_results['Feasibility'] == 'Feasible') &
                          (df_results['Accommodation'] == accommodation_type)]
    if cost_data.empty:
        print(f"Skipping cost comparison plot ({accommodation_type}): No feasible data.")
        plt.close()
        return

    sns.barplot(x='Route', y='Total Cost (EUR)',
                hue='Scenario', data=cost_data,
                palette=['#ff7675', '#74b9ff'])
    plt.title(f'Total Cost Comparison (with {accommodation_type} Accommodation)', fontsize=16)
    plt.ylabel('Total Cost (EUR)', fontsize=14)
    plt.xlabel('Route', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(title='Scenario')
    plt.xticks(rotation=0)
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))
    plt.tight_layout()
    save_path = os.path.join(VIZ_DIR, f'cost_comparison_{accommodation_type.lower()}.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved: {save_path}")
    plt.close()

def plot_carbon_breakdown(routes):
    """Plots the carbon footprint breakdown by transport mode."""
    plt.figure(figsize=(14, 10))
    carbon_breakdown = []
    for route_name, route_data in routes.items():
        # Check if segments exist and have carbon data
        if 'segments' in route_data and all('carbon' in seg for seg in route_data['segments']):
            for segment in route_data['segments']:
                carbon_breakdown.append({
                    'Route': route_name,
                    'Mode': segment['mode'],
                    'Carbon (kg CO2e)': segment['carbon'] # One-way carbon
                })
        else:
            print(f"Warning: Missing segment or carbon data for route '{route_name}'. Skipping breakdown.")

    if not carbon_breakdown:
        print("Skipping carbon breakdown plot: No data available.")
        plt.close()
        return

    df_breakdown = pd.DataFrame(carbon_breakdown)

    # Pivot for stacked bars
    pivot_df = df_breakdown.pivot_table(index='Route', columns='Mode', values='Carbon (kg CO2e)', aggfunc='sum')
    pivot_df.fillna(0, inplace=True)

    if pivot_df.empty:
        print("Skipping carbon breakdown plot: Pivot table is empty.")
        plt.close()
        return

    # Plot stacked bar chart
    ax = pivot_df.plot(kind='bar', stacked=True, figsize=(14, 10),
                      color=['#fdcb6e', '#0984e3', '#00b894', '#6c5ce7', '#e17055', '#fab1a0']) # Added more colors
    plt.title('Carbon Footprint Breakdown by Transport Mode (One-Way)', fontsize=16)
    plt.ylabel('Carbon Footprint (kg CO2e)', fontsize=14)
    plt.xlabel('Route', fontsize=14)
    plt.legend(title='Transport Mode')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=0)
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))
    plt.tight_layout()
    save_path = os.path.join(VIZ_DIR, 'carbon_breakdown.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved: {save_path}")
    plt.close()

def create_dashboard(df_results, routes):
    """Creates a summary dashboard with multiple plots."""
    fig = plt.figure(figsize=(20, 24))
    gs = fig.add_gridspec(3, 2, hspace=0.5, wspace=0.3)

    # Data subsets
    feasible_results = df_results[df_results['Feasibility'] == 'Feasible']
    if feasible_results.empty:
        print("Skipping dashboard creation: No feasible data.")
        plt.close(fig)
        return

    carbon_data = feasible_results.drop_duplicates(subset=['Route', 'Scenario'])
    carbon_per_day_data = feasible_results[feasible_results['Carbon per Vacation Day'].notna()].drop_duplicates(subset=['Route', 'Scenario'])
    time_data = feasible_results.drop_duplicates(subset=['Route', 'Scenario'])
    cost_data_hostel = feasible_results[feasible_results['Accommodation'] == 'Hostel']

    # --- Plot 1: Carbon footprint comparison ---
    ax1 = fig.add_subplot(gs[0, 0])
    if not carbon_data.empty:
        sns.barplot(x='Route', y='Carbon Footprint (kg CO2e)',
                   hue='Scenario', data=carbon_data,
                   palette=['#ff7675', '#74b9ff'], ax=ax1)
        ax1.set_title('Carbon Footprint by Route and Scenario', fontsize=16)
        ax1.set_ylabel('Carbon Footprint (kg CO2e)', fontsize=14)
        ax1.set_xlabel('') # Remove x-label for cleaner look
        ax1.grid(axis='y', linestyle='--', alpha=0.7)
        ax1.legend(title='Scenario')
        ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))
        ax1.tick_params(axis='x', rotation=10)
    else:
        ax1.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)
        ax1.set_title('Carbon Footprint by Route and Scenario', fontsize=16)

    # --- Plot 2: Carbon per vacation day ---
    ax2 = fig.add_subplot(gs[0, 1])
    if not carbon_per_day_data.empty:
        sns.barplot(x='Route', y='Carbon per Vacation Day',
                   hue='Scenario', data=carbon_per_day_data,
                   palette=['#ff7675', '#74b9ff'], ax=ax2)
        ax2.set_title('Carbon Footprint per Vacation Day', fontsize=16)
        ax2.set_ylabel('kg CO2e per Day at Destination', fontsize=14)
        ax2.set_xlabel('') # Remove x-label
        ax2.grid(axis='y', linestyle='--', alpha=0.7)
        ax2.legend(title='Scenario')
        ax2.tick_params(axis='x', rotation=10)
    else:
        ax2.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)
        ax2.set_title('Carbon Footprint per Vacation Day', fontsize=16)

    # --- Plot 3: Travel days vs days at destination ---
    ax3 = fig.add_subplot(gs[1, 0])
    if not time_data.empty:
        time_indices = range(len(time_data))
        width = 0.35
        ax3.bar([i - width/2 for i in time_indices], time_data['Travel Days (Round Trip)'],
               width, label='Travel Days', color='#e17055')
        ax3.bar([i + width/2 for i in time_indices], time_data['Days at Destination'],
               width, label='Days at Destination', color='#00b894')
        ax3.set_title('Time Distribution: Travel vs. Destination', fontsize=16)
        ax3.set_ylabel('Days', fontsize=14)
        ax3.set_xticks(time_indices)
        ax3.set_xticklabels([f"{row['Route']}\n({row['Scenario']})" for _, row in time_data.iterrows()], rotation=45, ha='right')
        ax3.legend()
        ax3.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        ax3.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)
        ax3.set_title('Time Distribution: Travel vs. Destination', fontsize=16)

    # --- Plot 4: Cost comparison (Hostel) ---
    ax4 = fig.add_subplot(gs[1, 1])
    if not cost_data_hostel.empty:
        sns.barplot(x='Route', y='Total Cost (EUR)',
                   hue='Scenario', data=cost_data_hostel,
                   palette=['#ff7675', '#74b9ff'], ax=ax4)
        ax4.set_title('Total Cost Comparison (Hostel)', fontsize=16)
        ax4.set_ylabel('Total Cost (EUR)', fontsize=14)
        ax4.set_xlabel('') # Remove x-label
        ax4.grid(axis='y', linestyle='--', alpha=0.7)
        ax4.legend(title='Scenario')
        ax4.yaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))
        ax4.tick_params(axis='x', rotation=10)
    else:
        ax4.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)
        ax4.set_title('Total Cost Comparison (Hostel)', fontsize=16)

    # --- Plot 5: Carbon breakdown ---
    ax5 = fig.add_subplot(gs[2, :])
    carbon_breakdown = []
    for route_name, route_data in routes.items():
        if 'segments' in route_data and all('carbon' in seg for seg in route_data['segments']):
            for segment in route_data['segments']:
                carbon_breakdown.append({
                    'Route': route_name,
                    'Mode': segment['mode'],
                    'Carbon (kg CO2e)': segment['carbon']
                })

    if carbon_breakdown:
        df_breakdown = pd.DataFrame(carbon_breakdown)
        pivot_df = df_breakdown.pivot_table(index='Route', columns='Mode', values='Carbon (kg CO2e)', aggfunc='sum')
        pivot_df.fillna(0, inplace=True)
        if not pivot_df.empty:
            pivot_df.plot(kind='bar', stacked=True, ax=ax5, figsize=(14, 8),
                         color=['#fdcb6e', '#0984e3', '#00b894', '#6c5ce7', '#e17055', '#fab1a0'])
            ax5.set_title('Carbon Footprint Breakdown by Transport Mode (One-Way)', fontsize=16)
            ax5.set_ylabel('Carbon Footprint (kg CO2e)', fontsize=14)
            ax5.set_xlabel('Route', fontsize=14)
            ax5.legend(title='Transport Mode')
            ax5.grid(axis='y', linestyle='--', alpha=0.7)
            ax5.yaxis.set_major_formatter(ticker.FuncFormatter(format_thousands))
            ax5.tick_params(axis='x', rotation=0)
        else:
             ax5.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)
             ax5.set_title('Carbon Footprint Breakdown by Transport Mode (One-Way)', fontsize=16)
    else:
        ax5.text(0.5, 0.5, 'No Data', ha='center', va='center', fontsize=14)
        ax5.set_title('Carbon Footprint Breakdown by Transport Mode (One-Way)', fontsize=16)

    plt.suptitle('Eco-Friendly Travel Analysis: Grenoble to Abuja', fontsize=24, y=1.02)
    plt.tight_layout(rect=[0, 0, 1, 0.99]) # Adjust rect to prevent suptitle overlap
    save_path = os.path.join(VIZ_DIR, 'eco_travel_dashboard.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Dashboard saved: {save_path}")
    plt.close(fig)

def generate_all_visualizations(df_results, routes):
    """Generates all standard visualizations."""
    setup_visualization_directory() # Ensure the output directory is ready
    print("\nGenerating visualizations...")
    setup_visualization_directory() # Ensure directory is clean

    # Set global plot styles
    sns.set_style("whitegrid")
    plt.rcParams['font.family'] = 'DejaVu Sans'
    plt.rcParams['font.size'] = 12

    # Generate individual plots
    plot_carbon_footprint_comparison(df_results)
    plot_carbon_per_vacation_day(df_results)
    plot_time_distribution(df_results)
    plot_cost_comparison(df_results, accommodation_type='Hostel') # Example with Hostel
    plot_cost_comparison(df_results, accommodation_type='Hotel')  # Example with Hotel
    plot_cost_comparison(df_results, accommodation_type='Airbnb') # Example with Airbnb
    plot_carbon_breakdown(routes)

    # Generate dashboard
    create_dashboard(df_results, routes)

    print("Visualization generation complete.")