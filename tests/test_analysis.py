"""
Tests for the analysis calculations.
"""

import pytest
import sys
import os
import numpy as np
import pandas as pd # Added for DataFrame comparison

# Add project root to sys.path to allow imports from 'src'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import functions to test and constants for haversine
from src.app.calculations.analysis import (
    haversine,
    calculate_route_metrics,
    analyze_scenarios,
    generate_key_findings
)
from src.app.data.constants import GRENOBLE_COORDS, ABUJA_COORDS

# --- Mock Data for Testing ---

MOCK_CARBON_EMISSIONS = {
    'Plane': 250, # gCO2e/pkm
    'Train': 35,
    'Bus': 25,
    'Ship': 18
}

MOCK_ROUTES = {
    'FastAir': {
        'segments': [
            {'mode': 'Plane', 'distance': 4000}
        ],
        'travel_time_hours': 10,
        'cost_eur': 800
    },
    'SlowLand': {
        'segments': [
            {'mode': 'Train', 'distance': 1000},
            {'mode': 'Bus', 'distance': 3000}
        ],
        'travel_time_hours': 150, # ~6.25 days
        'cost_eur': 600
    }
}

MOCK_ACCOMMODATION = {
    'Hostel': 30, # EUR per day
    'Hotel': 90
}

MOCK_SCENARIOS = {
    '1-week': {'days': 7},
    '1-month': {'days': 30}
}

# --- Haversine Tests (Existing) ---

def test_haversine_grenoble_abuja():
    """Tests the haversine distance calculation between Grenoble and Abuja."""
    expected_distance_km = 4019
    tolerance_km = 50
    calculated_distance = haversine(GRENOBLE_COORDS[0], GRENOBLE_COORDS[1],
                                    ABUJA_COORDS[0], ABUJA_COORDS[1])
    assert abs(calculated_distance - expected_distance_km) < tolerance_km, \
           f"Haversine distance mismatch: Expected ~{expected_distance_km} km, got {calculated_distance:.1f} km"

def test_haversine_same_point():
    """Tests the haversine distance calculation for the same point (should be 0)."""
    distance = haversine(GRENOBLE_COORDS[0], GRENOBLE_COORDS[1],
                         GRENOBLE_COORDS[0], GRENOBLE_COORDS[1])
    assert distance == pytest.approx(0.0), "Distance between the same point should be zero."

# --- New Tests for Core Analysis Functions ---

def test_calculate_route_metrics():
    """Tests the calculation of distance and carbon footprint for routes."""
    routes_copy = {k: v.copy() for k, v in MOCK_ROUTES.items()} # Work on a copy
    routes_copy['FastAir']['segments'] = [s.copy() for s in routes_copy['FastAir']['segments']]
    routes_copy['SlowLand']['segments'] = [s.copy() for s in routes_copy['SlowLand']['segments']]

    calculated_routes = calculate_route_metrics(routes_copy, MOCK_CARBON_EMISSIONS)

    # FastAir assertions
    assert calculated_routes['FastAir']['total_distance'] == 4000
    assert calculated_routes['FastAir']['segments'][0]['carbon'] == pytest.approx((4000 * 250) / 1000)
    assert calculated_routes['FastAir']['total_carbon_one_way'] == pytest.approx(1000.0)
    assert calculated_routes['FastAir']['total_carbon_round_trip'] == pytest.approx(2000.0)

    # SlowLand assertions
    assert calculated_routes['SlowLand']['total_distance'] == 4000
    train_carbon = (1000 * 35) / 1000
    bus_carbon = (3000 * 25) / 1000
    assert calculated_routes['SlowLand']['segments'][0]['carbon'] == pytest.approx(train_carbon)
    assert calculated_routes['SlowLand']['segments'][1]['carbon'] == pytest.approx(bus_carbon)
    assert calculated_routes['SlowLand']['total_carbon_one_way'] == pytest.approx(train_carbon + bus_carbon)
    assert calculated_routes['SlowLand']['total_carbon_round_trip'] == pytest.approx((train_carbon + bus_carbon) * 2)

def test_analyze_scenarios():
    """Tests the scenario analysis for feasibility, cost, and time."""
    # First, calculate metrics needed by analyze_scenarios
    routes_copy = {k: v.copy() for k, v in MOCK_ROUTES.items()}
    routes_copy['FastAir']['segments'] = [s.copy() for s in routes_copy['FastAir']['segments']]
    routes_copy['SlowLand']['segments'] = [s.copy() for s in routes_copy['SlowLand']['segments']]
    routes_with_metrics = calculate_route_metrics(routes_copy, MOCK_CARBON_EMISSIONS)

    df_results = analyze_scenarios(routes_with_metrics, MOCK_ACCOMMODATION, MOCK_SCENARIOS)

    assert isinstance(df_results, pd.DataFrame)
    assert len(df_results) == 8 # 2 scenarios * 2 routes * 2 accommodations

    # Check 1-week scenario
    week_air_hostel = df_results[(df_results['Scenario'] == '1-week') & (df_results['Route'] == 'FastAir') & (df_results['Accommodation'] == 'Hostel')].iloc[0]
    week_land_hostel = df_results[(df_results['Scenario'] == '1-week') & (df_results['Route'] == 'SlowLand') & (df_results['Accommodation'] == 'Hostel')].iloc[0]

    assert week_air_hostel['Feasibility'] == 'Feasible'
    assert week_air_hostel['Travel Days (Round Trip)'] == np.ceil(10/24) * 2 # 2 days
    assert week_air_hostel['Days at Destination'] == 7 - 2 # 5 days
    assert week_air_hostel['Total Cost (EUR)'] == pytest.approx(800 + 5 * 30)
    assert week_air_hostel['Carbon per Vacation Day'] == pytest.approx(2000.0 / 5)

    assert week_land_hostel['Feasibility'] == 'Not feasible'
    assert pd.isna(week_land_hostel['Travel Days (Round Trip)'])
    assert week_land_hostel['Days at Destination'] == 0
    assert pd.isna(week_land_hostel['Total Cost (EUR)'])
    assert pd.isna(week_land_hostel['Carbon per Vacation Day'])

    # Check 1-month scenario
    month_air_hotel = df_results[(df_results['Scenario'] == '1-month') & (df_results['Route'] == 'FastAir') & (df_results['Accommodation'] == 'Hotel')].iloc[0]
    month_land_hotel = df_results[(df_results['Scenario'] == '1-month') & (df_results['Route'] == 'SlowLand') & (df_results['Accommodation'] == 'Hotel')].iloc[0]

    assert month_air_hotel['Feasibility'] == 'Feasible'
    assert month_air_hotel['Days at Destination'] == 30 - 2 # 28 days
    assert month_air_hotel['Total Cost (EUR)'] == pytest.approx(800 + 28 * 90)
    assert month_air_hotel['Carbon per Vacation Day'] == pytest.approx(2000.0 / 28)

    assert month_land_hotel['Feasibility'] == 'Feasible'
    travel_days_land = np.ceil(150/24) * 2 # 7*2 = 14 days
    days_dest_land = 30 - travel_days_land # 16 days
    assert month_land_hotel['Travel Days (Round Trip)'] == travel_days_land
    assert month_land_hotel['Days at Destination'] == days_dest_land
    assert month_land_hotel['Total Cost (EUR)'] == pytest.approx(600 + days_dest_land * 90)
    assert month_land_hotel['Carbon per Vacation Day'] == pytest.approx(routes_with_metrics['SlowLand']['total_carbon_round_trip'] / days_dest_land)

def test_generate_key_findings_no_feasible():
    """Tests key findings generation when no options are feasible."""
    df_empty = pd.DataFrame(columns=['Scenario', 'Route', 'Accommodation', 'Feasibility'])
    df_not_feasible = pd.DataFrame([{'Scenario': '1-week', 'Route': 'Any', 'Accommodation': 'Any', 'Feasibility': 'Not feasible'}])

    findings_empty = generate_key_findings(df_empty)
    findings_not_feasible = generate_key_findings(df_not_feasible)

    assert findings_empty == ["No feasible travel options found for the given scenarios."]
    assert findings_not_feasible == ["No feasible travel options found for the given scenarios."]

def test_generate_key_findings_with_data():
    """Tests key findings generation with the mock data results."""
    # Generate results from mock data first
    routes_copy = {k: v.copy() for k, v in MOCK_ROUTES.items()}
    routes_copy['FastAir']['segments'] = [s.copy() for s in routes_copy['FastAir']['segments']]
    routes_copy['SlowLand']['segments'] = [s.copy() for s in routes_copy['SlowLand']['segments']]
    routes_with_metrics = calculate_route_metrics(routes_copy, MOCK_CARBON_EMISSIONS)
    df_results = analyze_scenarios(routes_with_metrics, MOCK_ACCOMMODATION, MOCK_SCENARIOS)

    findings = generate_key_findings(df_results)

    assert isinstance(findings, list)
    assert len(findings) > 5 # Expect multiple findings

    # Check specific findings based on mock data
    # SlowLand has lower carbon (110*2=220) vs FastAir (1000*2=2000)
    assert any("'SlowLand' has the lowest average carbon footprint" in f for f in findings)
    # Only FastAir is feasible for 1 week
    assert any("Only these routes are feasible for a 1-week trip: FastAir" in f for f in findings)
    # SlowLand is more carbon efficient per day for 1 month
    assert any("'SlowLand' has the lowest carbon footprint per day" in f for f in findings)
    # Check cheapest (Hostel)
    # 1-week: FastAir = 800 + 5*30 = 950
    # 1-month: FastAir = 800 + 28*30 = 1640; SlowLand = 600 + 16*30 = 1080
    assert any("1-week: 'FastAir' at approximately €950" in f for f in findings)
    assert any("1-month: 'SlowLand' at approximately €1080" in f for f in findings)
    # Check recommendations
    assert any("1-week vacation: 'FastAir'" in f for f in findings)
    assert any("1-month vacation: 'SlowLand'" in f for f in findings)