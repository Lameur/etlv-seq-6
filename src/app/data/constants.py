"""
Stores constant data used in the travel analysis, such as
carbon emission factors, route details, and accommodation costs.
"""

# Updated carbon emissions per transport mode (gCO2e per passenger-km)
# Sources:
# - ADEME Carbon Database 2023 (France): Provides comprehensive factors for various modes.
#   Link: https://bilans-ges.ademe.fr/fr/basecarbone/donnees-consulter/liste-des-elements
#   Justification: Official French agency data, relevant for European segments.
# - UK Government GHG Conversion Factors 2023: Widely used standard, good for international comparisons.
#   Link: https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2023
#   Justification: Provides robust factors, especially for aviation.
# - International Transport Forum (ITF) Transport Outlook: Offers global perspectives.
#   Link: https://www.itf-oecd.org/transport-outlook-2023
#   Justification: Useful for cross-checking and understanding global trends.
# Note: Values are approximate averages and can vary significantly based on specific vehicle/aircraft,
# occupancy, fuel type, and operational efficiency. Ferry emissions are particularly variable.
CARBON_EMISSIONS = {
    'Plane': 250,  # Average for long-haul flight (>3700km), economy class. Includes RFI (Radiative Forcing Index) multiplier implicitly or explicitly depending on source methodology.
    'Train': 35,   # European average for electric high-speed/intercity trains. Lower in France due to nuclear power (~6 gCO2e/pkm), higher elsewhere.
    'Bus': 25,     # Modern coach bus, average occupancy.
    'Car': 165,    # Average medium-sized gasoline car, assuming single occupant for comparison baseline.
    'CarPool': 42, # Same car as above, but with 4 occupants (165 / 4 ~ 41.25).
    'Ship': 18     # Passenger ferry (Ro-Pax). Highly variable; this is a lower-end estimate based on some sources. Can be much higher.
}

# Realistic route options with estimated distances, times, and costs.
# Distances: Calculated using mapping tools (e.g., Google Maps, Rome2rio) for driving/train/bus segments, great-circle for flights.
# Travel Time: Includes estimated transfer times, check-in, border crossings where applicable. Highly approximate for long overland routes.
# Cost: Rough estimates for round trips based on searches in mid-2024. Highly variable based on booking time, season, and provider.
ROUTES = {
    'Air Travel': {
        'segments': [
            {'mode': 'Train', 'description': 'Grenoble to Lyon St Exupéry Airport (LYS)', 'distance': 110},
            {'mode': 'Plane', 'description': 'Lyon (LYS) to Paris (CDG)', 'distance': 400}, # Flight distance
            {'mode': 'Plane', 'description': 'Paris (CDG) to Abuja (ABV)', 'distance': 4200}, # Flight distance
        ],
        'travel_time_hours': 10,  # One-way: ~1.5h train + 2h airport wait + 1h flight + 2h layover + 6h flight + 1h arrival = ~13.5h. Rounded down slightly for simplicity, could be longer.
        'cost_eur': 820,  # Round trip estimate (can vary wildly: €600-€1200+).
    },
    'Mixed Transport': { # Train -> Ferry -> Bus through West Africa
        'segments': [
            {'mode': 'Train', 'description': 'Grenoble to Marseille', 'distance': 300},
            {'mode': 'Ship', 'description': 'Marseille to Tangier (Morocco)', 'distance': 1800}, # Sea distance
            {'mode': 'Bus', 'description': 'Tangier to Dakar (Senegal)', 'distance': 3500}, # Overland via Mauritania
            {'mode': 'Bus', 'description': 'Dakar to Abuja (Nigeria)', 'distance': 3200}, # Overland via Mali, Burkina Faso, Niger/Benin
        ],
        'travel_time_hours': 175, # One-way: ~3h train + 10h wait/transfer + ~40h ferry + ~72h bus (Tangier-Dakar) + ~48h bus (Dakar-Abuja) + buffer = ~7.3 days.
        'cost_eur': 1200, # Round trip estimate: Train ~€100, Ferry ~€300-400, Buses ~€300-400 each way. Very rough.
    },
    'Land & Sea': { # Train -> Ferry -> Bus through West Africa (alternative)
        'segments': [
            {'mode': 'Train', 'description': 'Grenoble to Barcelona', 'distance': 650},
            {'mode': 'Ship', 'description': 'Barcelona to Tangier (Morocco)', 'distance': 1500}, # Sea distance
            {'mode': 'Bus', 'description': 'Tangier across Morocco/Western Sahara', 'distance': 1200},
            {'mode': 'Bus', 'description': 'Western Sahara border to Senegal border', 'distance': 1500}, # Through Mauritania
            {'mode': 'Bus', 'description': 'Senegal border to Abuja', 'distance': 2400}, # Via Mali, Burkina Faso, Niger/Benin
        ],
        'travel_time_hours': 165, # One-way: ~7h train + 10h wait/transfer + ~30h ferry + ~30h bus + ~36h bus + ~48h bus + buffer = ~6.9 days.
        'cost_eur': 1150, # Round trip estimate: Similar logic to Mixed Transport, slightly different ferry/train costs.
    }
}

# Updated accommodation costs (EUR per day) in Abuja.
# Sources: Booking.com, Hostelworld, Airbnb searches for Abuja (mid-2024).
# Justification: Based on current listings, representing typical budget to mid-range options.
ACCOMMODATION = {
    'Hotel': 90,    # Mid-range hotel (3-star equivalent).
    'Hostel': 30,   # Dorm bed in a reputable hostel.
    'Airbnb': 50    # Private room in a shared apartment or basic studio.
}

# Define departure and arrival coordinates
GRENOBLE_COORDS = (45.1885, 5.7245)
ABUJA_COORDS = (9.0765, 7.3986)

# Define scenarios
SCENARIOS = {
    '1-week': {'days': 7},
    '1-month': {'days': 30}
}