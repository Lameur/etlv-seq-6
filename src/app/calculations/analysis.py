"""
Performs the core calculations for the travel analysis, including
carbon footprint, cost estimation, and feasibility checks.
"""

import numpy as np
import pandas as pd
from math import radians, cos, sin, asin, sqrt
from ..data.constants import CARBON_EMISSIONS, ROUTES, ACCOMMODATION, SCENARIOS

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees).

    Args:
        lat1 (float): Latitude of point 1.
        lon1 (float): Longitude of point 1.
        lat2 (float): Latitude of point 2.
        lon2 (float): Longitude of point 2.

    Returns:
        float: Distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def calculate_route_metrics(routes, carbon_emissions):
    """Calculates total distance and carbon footprint for each route.

    Args:
        routes (dict): Dictionary containing route data.
        carbon_emissions (dict): Dictionary of carbon emissions per mode.

    Returns:
        dict: Updated routes dictionary with calculated metrics.
    """
    print("\nCalculating route metrics...")
    for route_name, route_data in routes.items():
        total_carbon = 0
        total_distance = 0

        for segment in route_data['segments']:
            mode = segment['mode']
            distance = segment['distance']
            total_distance += distance
            # Calculate carbon in kg CO2e
            carbon = (distance * carbon_emissions[mode]) / 1000
            segment['carbon'] = carbon
            total_carbon += carbon

        route_data['total_carbon_one_way'] = total_carbon
        route_data['total_carbon_round_trip'] = total_carbon * 2
        route_data['total_distance'] = total_distance

        print(f"  {route_name}: Distance={total_distance} km, Carbon (one-way)={total_carbon:.1f} kg CO2e")
    return routes

def analyze_scenarios(routes, accommodation, scenarios):
    """Analyzes travel scenarios based on routes, accommodation, and duration.

    Args:
        routes (dict): Dictionary containing route data with calculated metrics.
        accommodation (dict): Dictionary of accommodation costs.
        scenarios (dict): Dictionary defining travel scenarios (duration).

    Returns:
        pd.DataFrame: DataFrame containing the results of the scenario analysis.
    """
    print("\nAnalyzing scenarios...")
    results = []
    for scenario_name, scenario_data in scenarios.items():
        total_days = scenario_data['days']
        print(f"  Scenario: {scenario_name} ({total_days} days)")

        for route_name, route_data in routes.items():
            # Calculate travel time in days (rounding up)
            travel_days_one_way = np.ceil(route_data['travel_time_hours'] / 24)
            travel_days_round = travel_days_one_way * 2
            days_at_destination = total_days - travel_days_round

            # Determine feasibility and carbon efficiency
            if days_at_destination <= 0:
                feasibility = "Not feasible"
                carbon_per_vacation_day = None
                days_at_destination_calc = 0 # Use 0 for calculations if not feasible
            else:
                feasibility = "Feasible"
                carbon_per_vacation_day = route_data['total_carbon_round_trip'] / days_at_destination
                days_at_destination_calc = days_at_destination

            # Calculate costs for each accommodation type
            for accom_name, accom_cost in accommodation.items():
                if feasibility == "Feasible":
                    total_cost = route_data['cost_eur'] + (days_at_destination_calc * accom_cost)
                else:
                    total_cost = None # No cost if the trip isn't feasible

                results.append({
                    'Scenario': scenario_name,
                    'Route': route_name,
                    'Accommodation': accom_name,
                    'Travel Days (Round Trip)': travel_days_round if feasibility == "Feasible" else None,
                    'Days at Destination': days_at_destination_calc,
                    'Carbon Footprint (kg CO2e)': route_data['total_carbon_round_trip'],
                    'Carbon per Vacation Day': carbon_per_vacation_day,
                    'Total Cost (EUR)': total_cost,
                    'Feasibility': feasibility
                })

    df_results = pd.DataFrame(results)
    print("Scenario analysis complete.")
    return df_results

def generate_key_findings(df_results):
    """Generates a summary of key findings from the analysis results.

    Args:
        df_results (pd.DataFrame): DataFrame with analysis results.

    Returns:
        list: A list of strings summarizing the key findings.
    """
    findings = []
    feasible_results = df_results[df_results['Feasibility'] == 'Feasible'] # Filter for feasible options first

    if feasible_results.empty:
        findings.append("No feasible travel options found for the given scenarios.")
        return findings

    # 1. Comparing carbon emissions
    avg_carbon = feasible_results.groupby('Route')['Carbon Footprint (kg CO2e)'].mean()
    if not avg_carbon.empty:
        best_carbon_route = avg_carbon.idxmin()
        worst_carbon_route = avg_carbon.idxmax()
        min_carbon = avg_carbon.min()
        max_carbon = avg_carbon.max()

        findings.append(f"1. Carbon Footprint: '{best_carbon_route}' has the lowest average carbon footprint ({min_carbon:.1f} kg CO2e round trip).")
        if best_carbon_route != worst_carbon_route and 'Air Travel' in avg_carbon.index:
            air_carbon = avg_carbon.get('Air Travel', np.nan)
            if not np.isnan(air_carbon) and air_carbon > 0:
                 carbon_reduction = (1 - (min_carbon / air_carbon)) * 100
                 findings.append(f"   - This is {carbon_reduction:.1f}% less than 'Air Travel' ({air_carbon:.1f} kg CO2e)." )

    # 2. Feasibility for 1-week
    feasible_week = feasible_results[feasible_results['Scenario'] == '1-week']['Route'].unique()
    if feasible_week.size > 0:
        findings.append(f"2. 1-Week Feasibility: Only these routes are feasible for a 1-week trip: {', '.join(feasible_week)}.")
    else:
        findings.append("2. 1-Week Feasibility: No routes are feasible for a 1-week trip.")

    # 3. Carbon efficiency for 1-month
    month_results = feasible_results[(feasible_results['Scenario'] == '1-month') & (feasible_results['Carbon per Vacation Day'].notna())]
    if not month_results.empty:
        avg_carbon_per_day = month_results.groupby('Route')['Carbon per Vacation Day'].mean()
        if not avg_carbon_per_day.empty:
            best_carbon_per_day_route = avg_carbon_per_day.idxmin()
            findings.append(f"3. 1-Month Carbon Efficiency: '{best_carbon_per_day_route}' has the lowest carbon footprint per day at the destination ({avg_carbon_per_day.min():.1f} kg CO2e/day)." )
    else:
         findings.append("3. 1-Month Carbon Efficiency: No feasible routes found for 1-month trip to calculate efficiency.")

    # 4. Cost comparison (using Hostel for consistency)
    hostel_costs = feasible_results[feasible_results['Accommodation'] == 'Hostel']
    if not hostel_costs.empty:
        cheapest_options = hostel_costs.loc[hostel_costs.groupby(['Scenario'])['Total Cost (EUR)'].idxmin()]
        findings.append("4. Cheapest Options (Hostel Accommodation):")
        for _, row in cheapest_options.iterrows():
            findings.append(f"   - {row['Scenario']}: '{row['Route']}' at approximately €{row['Total Cost (EUR)']:.0f}.")
    else:
        findings.append("4. Cheapest Options: Could not determine cheapest options (no feasible hostel data).")

    # 5. Recommendations
    findings.append("5. Environmental Recommendation Summary:")
    if feasible_week.size > 0:
        # Recommend the lowest carbon option among the feasible ones for 1 week
        week_carbon = avg_carbon[avg_carbon.index.isin(feasible_week)]
        if not week_carbon.empty:
            best_week_route = week_carbon.idxmin()
            findings.append(f"   - 1-week vacation: '{best_week_route}' (lowest carbon among feasible options)." )
        else:
             findings.append("   - 1-week vacation: No recommendation possible (no feasible carbon data).")
    else:
        findings.append("   - 1-week vacation: No feasible options.")

    month_carbon = avg_carbon[avg_carbon.index.isin(feasible_results[feasible_results['Scenario'] == '1-month']['Route'].unique())]
    if not month_carbon.empty:
        best_month_route = month_carbon.idxmin()
        findings.append(f"   - 1-month vacation: '{best_month_route}' (lowest overall carbon footprint among feasible options)." )
    else:
        findings.append("   - 1-month vacation: No feasible options.")

    return findings