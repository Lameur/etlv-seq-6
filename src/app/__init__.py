"""
Main application package.

Exports the main `run_analysis` function.
"""

import os
import pandas as pd

# Import core components
from .data.constants import ROUTES, CARBON_EMISSIONS, ACCOMMODATION, SCENARIOS
from .calculations.analysis import calculate_route_metrics, analyze_scenarios, generate_key_findings
from .visualization.plotting import setup_visualization_directory, plot_carbon_footprint_comparison, plot_carbon_per_vacation_day, plot_time_distribution, plot_cost_comparison, plot_carbon_breakdown, create_dashboard
from .presentation.generate_pptx import generate_presentation # <-- Import the new function

# Define the output directory for results
RESULTS_DIR = "results"
RESULTS_FILENAME = "travel_analysis_results.csv"
FINDINGS_FILENAME = "key_findings.txt"


def main():
    """Runs the complete travel analysis workflow."""
    print("Starting Eco-Friendly Travel Analysis...")

    # 1. Setup output directories
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    setup_visualization_directory() # Sets up results/visualizations

    # 2. Calculate route metrics (carbon, distance)
    routes_with_metrics = calculate_route_metrics(ROUTES, CARBON_EMISSIONS)

    # 3. Analyze scenarios (feasibility, cost, time, carbon per day)
    df_results = analyze_scenarios(routes_with_metrics, ACCOMMODATION, SCENARIOS)

    # 4. Save detailed results to CSV
    results_path = os.path.join(RESULTS_DIR, RESULTS_FILENAME)
    df_results.to_csv(results_path, index=False)
    print(f"\nDetailed analysis results saved to: {results_path}")

    # 5. Generate Key Findings
    key_findings = generate_key_findings(df_results)
    print("\n--- Key Findings ---")
    for finding in key_findings:
        print(finding)
    # Save findings to a text file
    findings_path = os.path.join(RESULTS_DIR, FINDINGS_FILENAME)
    with open(findings_path, 'w') as f:
        f.write("Key Findings from Eco-Travel Analysis (Grenoble to Abuja):\n")
        f.write("===========================================================\n\n")
        for finding in key_findings:
            f.write(f"- {finding}\n")
    print(f"\nKey findings saved to: {findings_path}")


    # 6. Generate Visualizations
    print("\nGenerating visualizations...")
    plot_carbon_footprint_comparison(df_results)
    plot_carbon_per_vacation_day(df_results)
    plot_time_distribution(df_results)
    plot_cost_comparison(df_results, accommodation_type='Hostel') # Example for Hostel
    plot_cost_comparison(df_results, accommodation_type='Airbnb') # Example for Airbnb
    plot_carbon_breakdown(routes_with_metrics)
    # create_dashboard(df_results, routes_with_metrics) # Optional: Dashboard generation

    # 7. Generate PowerPoint Presentation
    print("\nGenerating PowerPoint presentation...")
    generate_presentation(df_results, key_findings, routes_with_metrics)

    print("\nAnalysis complete.")

# Make the main function available for import
__all__ = ['main']