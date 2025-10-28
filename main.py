from fastmcp import FastMCP
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math
import urllib.request
import urllib.parse

mcp = FastMCP("Public AI MCP Server")

# @mcp.tool()
# def search_swiss_stations(query: str, limit: int = 10) -> List[Dict[str, any]]:
#     """Search for Swiss public transport stations (train, bus, tram).

#     Args:
#         query: Station name to search for (e.g., "Zürich", "Bern")
#         limit: Maximum number of results to return (default: 10)

#     Returns:
#         List of stations with id, name, and coordinates
#     """
#     try:
#         url = f"http://transport.opendata.ch/v1/locations?query={urllib.parse.quote(query)}"
#         with urllib.request.urlopen(url, timeout=10) as response:
#             data = json.loads(response.read().decode())

#         stations = data.get('stations', [])[:limit]
#         return [
#             {
#                 'id': s['id'],
#                 'name': s['name'],
#                 'coordinates': {
#                     'lat': s['coordinate']['x'],
#                     'lon': s['coordinate']['y']
#                 },
#                 'type': s.get('icon', 'unknown')
#             }
#             for s in stations
#         ]
#     except Exception as e:
#         return [{"error": f"Failed to search stations: {str(e)}"}]

# @mcp.tool()
# def get_swiss_departures(station: str, limit: int = 10) -> Dict[str, any]:
#     """Get real-time departures from a Swiss public transport station.

#     Args:
#         station: Station name or ID (e.g., "Zürich HB", "Bern")
#         limit: Number of departures to return (default: 10, max: 40)

#     Returns:
#         Dictionary with station info and list of upcoming departures with delays
#     """
#     try:
#         url = f"http://transport.opendata.ch/v1/stationboard?station={urllib.parse.quote(station)}&limit={min(limit, 40)}"
#         with urllib.request.urlopen(url, timeout=10) as response:
#             data = json.loads(response.read().decode())

#         station_info = data.get('station', {})
#         stationboard = data.get('stationboard', [])

#         departures = []
#         for item in stationboard:
#             stop = item.get('stop', {})
#             prognosis = stop.get('prognosis', {})

#             scheduled_time = stop.get('departure', '')
#             actual_time = prognosis.get('departure', scheduled_time)
#             delay = stop.get('delay', 0)

#             departures.append({
#                 'time': scheduled_time,
#                 'actual_time': actual_time,
#                 'delay_minutes': delay,
#                 'platform': stop.get('platform', 'N/A'),
#                 'type': item.get('category', ''),
#                 'number': item.get('number', ''),
#                 'to': item.get('to', ''),
#                 'operator': item.get('operator', '')
#             })

#         return {
#             'station': station_info.get('name', station),
#             'station_id': station_info.get('id', ''),
#             'departures': departures
#         }
#     except Exception as e:
#         return {"error": f"Failed to get departures: {str(e)}"}

# @mcp.tool()
# def plan_swiss_journey(
#     from_station: str,
#     to_station: str,
#     via_station: Optional[str] = None,
#     limit: int = 4
# ) -> List[Dict[str, any]]:
#     """Plan a journey on Swiss public transport with real-time connections.

#     Args:
#         from_station: Departure station name (e.g., "Zürich HB")
#         to_station: Arrival station name (e.g., "Bern")
#         via_station: Optional intermediate station (e.g., "Olten")
#         limit: Number of connection options to return (default: 4, max: 6)

#     Returns:
#         List of journey options with times, platforms, transfers, and products
#     """
#     try:
#         url = f"http://transport.opendata.ch/v1/connections?from={urllib.parse.quote(from_station)}&to={urllib.parse.quote(to_station)}&limit={min(limit, 6)}"
#         if via_station:
#             url += f"&via[]={urllib.parse.quote(via_station)}"

#         with urllib.request.urlopen(url, timeout=10) as response:
#             data = json.loads(response.read().decode())

#         connections = data.get('connections', [])

#         journeys = []
#         for conn in connections:
#             from_info = conn.get('from', {})
#             to_info = conn.get('to', {})

#             journey = {
#                 'departure': {
#                     'station': from_info.get('station', {}).get('name', ''),
#                     'time': from_info.get('departure', ''),
#                     'platform': from_info.get('platform', 'N/A'),
#                     'delay_minutes': from_info.get('delay', 0)
#                 },
#                 'arrival': {
#                     'station': to_info.get('station', {}).get('name', ''),
#                     'time': to_info.get('arrival', ''),
#                     'platform': to_info.get('platform', 'N/A'),
#                     'delay_minutes': to_info.get('delay', 0) if to_info.get('delay') else None
#                 },
#                 'duration': conn.get('duration', ''),
#                 'transfers': conn.get('transfers', 0),
#                 'products': conn.get('products', [])
#             }

#             journeys.append(journey)

#         return journeys
#     except Exception as e:
#         return [{"error": f"Failed to plan journey: {str(e)}"}]


@mcp.tool()
def lookup_uk_postcode(postcode: str) -> Dict[str, any]:
    """Look up detailed information about a UK postcode using real data.

    Args:
        postcode: UK postcode (e.g., "SW1A 1AA", "M1 1AE")

    Returns:
        Dictionary with postcode info, coordinates, region, parliamentary constituency, etc.
    """
    try:
        # Clean postcode
        clean_postcode = postcode.replace(' ', '')
        url = f"https://api.postcodes.io/postcodes/{urllib.parse.quote(clean_postcode)}"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        if data.get('status') == 200:
            result = data.get('result', {})
            return {
                'postcode': result.get('postcode', ''),
                'coordinates': {
                    'lat': result.get('latitude'),
                    'lon': result.get('longitude')
                },
                'region': result.get('region', ''),
                'country': result.get('country', ''),
                'parliamentary_constituency': result.get('parliamentary_constituency', ''),
                'admin_district': result.get('admin_district', ''),
                'parish': result.get('parish', ''),
                'nhs_ha': result.get('nhs_ha', ''),
                'ccg': result.get('ccg', '')
            }
        else:
            return {"error": "Postcode not found"}
    except Exception as e:
        return {"error": f"Failed to lookup postcode: {str(e)}"}

@mcp.tool()
def get_uk_bank_holidays(division: str = "england-and-wales") -> List[Dict[str, any]]:
    """Get UK bank holidays using real government data.

    Args:
        division: UK division (england-and-wales, scotland, northern-ireland)

    Returns:
        List of upcoming bank holidays with dates and titles
    """
    try:
        url = "https://www.gov.uk/bank-holidays.json"
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        division_key = division.lower()
        holidays = data.get(division_key, {}).get('events', [])

        # Filter to upcoming holidays only
        today = datetime.now().date()
        upcoming = []
        for holiday in holidays:
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
            if holiday_date >= today:
                upcoming.append({
                    'title': holiday['title'],
                    'date': holiday['date'],
                    'notes': holiday.get('notes', '')
                })

        return upcoming[:10]  # Return next 10
    except Exception as e:
        return [{"error": f"Failed to get bank holidays: {str(e)}"}]

@mcp.tool()
def search_nhs_gp_appointments(
    postcode: str,
    appointment_type: str = "general",
    preferred_date: Optional[str] = None
) -> Dict[str, any]:
    """Search for available NHS GP appointments near a postcode.

    Args:
        postcode: Your postcode to find nearby GP practices
        appointment_type: Type of appointment (general, urgent, nurse, phone)
        preferred_date: Preferred date in YYYY-MM-DD format (optional)

    Returns:
        Dictionary with available appointments at nearby GP practices
    """
    # This is simulated data for demonstration purposes
    practices = [
        {
            'name': 'Central Medical Practice',
            'address': f'123 High Street, near {postcode}',
            'distance_miles': 0.3,
            'rating': 4.5,
            'available_slots': [
                {
                    'date': (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'),
                    'time': '09:30',
                    'doctor': 'Dr. Sarah Johnson',
                    'appointment_type': appointment_type
                },
                {
                    'date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                    'time': '14:15',
                    'doctor': 'Dr. James Smith',
                    'appointment_type': appointment_type
                }
            ]
        },
        {
            'name': 'Park View Surgery',
            'address': f'45 Park Road, near {postcode}',
            'distance_miles': 0.7,
            'rating': 4.2,
            'available_slots': [
                {
                    'date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
                    'time': '11:00',
                    'doctor': 'Dr. Emma Williams',
                    'appointment_type': appointment_type
                },
                {
                    'date': (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d'),
                    'time': '16:30',
                    'doctor': 'Dr. Michael Brown',
                    'appointment_type': appointment_type
                }
            ]
        }
    ]

    return {
        'search_postcode': postcode,
        'appointment_type': appointment_type,
        'practices_found': len(practices),
        'practices': practices,
        'note': 'DEMO DATA - This demonstrates NHS booking integration potential'
    }

@mcp.tool()
def book_nhs_gp_appointment(
    practice_name: str,
    appointment_date: str,
    appointment_time: str,
    patient_nhs_number: str,
    reason: str
) -> Dict[str, any]:
    """Book an NHS GP appointment.

    Args:
        practice_name: Name of the GP practice
        appointment_date: Date in YYYY-MM-DD format
        appointment_time: Time in HH:MM format
        patient_nhs_number: Patient's NHS number
        reason: Brief reason for appointment

    Returns:
        Confirmation of booking with reference number
    """
    # Simulated booking confirmation
    import random
    reference = f"NHS-{random.randint(100000, 999999)}"

    return {
        'status': 'confirmed',
        'reference_number': reference,
        'practice': practice_name,
        'appointment_date': appointment_date,
        'appointment_time': appointment_time,
        'patient_nhs_number': patient_nhs_number[:3] + '****' + patient_nhs_number[-2:],
        'what_to_bring': ['NHS card or number', 'Photo ID', 'List of current medications'],
        'cancellation_policy': 'Please give 24 hours notice to cancel',
        'note': 'DEMO BOOKING - This demonstrates NHS booking integration potential'
    }

@mcp.tool()
def check_dvla_license_status(license_number: str, postcode: str) -> Dict[str, any]:
    """Check DVLA driving license status and renewal eligibility.

    Args:
        license_number: UK driving license number
        postcode: Postcode on license

    Returns:
        License status, expiry date, and renewal information
    """
    # Simulated license data
    import random

    expiry_days = random.randint(30, 365)
    expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime('%Y-%m-%d')

    needs_renewal = expiry_days < 180

    return {
        'license_number': license_number[:5] + '******' + license_number[-2:],
        'status': 'valid',
        'expiry_date': expiry_date,
        'days_until_expiry': expiry_days,
        'needs_renewal': needs_renewal,
        'license_type': 'Full UK Driving License',
        'categories': ['B - Car', 'AM - Moped'],
        'penalty_points': random.choice([0, 0, 0, 3]),
        'renewal_eligible': expiry_days < 180,
        'renewal_fee': '£14.00 online or £17.00 postal',
        'note': 'DEMO DATA - This demonstrates DVLA integration potential'
    }

@mcp.tool()
def renew_dvla_license(
    license_number: str,
    postcode: str,
    payment_method: str = "card"
) -> Dict[str, any]:
    """Renew a UK driving license online.

    Args:
        license_number: UK driving license number
        postcode: Postcode on license
        payment_method: Payment method (card, or postal)

    Returns:
        Renewal confirmation and expected delivery date
    """
    # Simulated renewal
    import random
    application_ref = f"DVLA{random.randint(1000000, 9999999)}"
    delivery_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    fee = 14.00 if payment_method == "card" else 17.00

    return {
        'status': 'renewal_submitted',
        'application_reference': application_ref,
        'license_number': license_number[:5] + '******' + license_number[-2:],
        'fee_paid': f'£{fee:.2f}',
        'expected_delivery': delivery_date,
        'delivery_address_postcode': postcode,
        'what_happens_next': [
            'Your application is being processed',
            'You can continue to drive while waiting',
            'New photocard will arrive by post',
            'Check status at gov.uk/view-driving-licence'
        ],
        'note': 'DEMO RENEWAL - This demonstrates DVLA integration potential'
    }

@mcp.tool()
def check_tv_license(postcode: str) -> Dict[str, any]:
    """Check TV License status for an address.

    Args:
        postcode: Postcode of the property

    Returns:
        TV License status and renewal information
    """
    # Simulated license check
    import random

    has_license = random.choice([True, True, False])

    if has_license:
        expiry_days = random.randint(10, 365)
        expiry_date = (datetime.now() + timedelta(days=expiry_days)).strftime('%Y-%m-%d')

        return {
            'postcode': postcode,
            'license_status': 'active',
            'expiry_date': expiry_date,
            'days_until_expiry': expiry_days,
            'needs_renewal': expiry_days < 30,
            'license_type': 'Standard Color TV License',
            'annual_fee': '£169.50',
            'payment_plan_available': True,
            'auto_renewal_enabled': random.choice([True, False]),
            'note': 'DEMO DATA - This demonstrates TV Licensing integration potential'
        }
    else:
        return {
            'postcode': postcode,
            'license_status': 'none_found',
            'message': 'No TV License found for this address',
            'required_if': 'You watch or record live TV or use BBC iPlayer',
            'annual_fee': '£169.50',
            'purchase_url': 'tvlicensing.co.uk',
            'note': 'DEMO DATA - This demonstrates TV Licensing integration potential'
        }

@mcp.tool()
def get_bbc_iplayer_recommendations(
    genre: Optional[str] = None,
    duration_minutes: Optional[int] = None
) -> List[Dict[str, any]]:
    """Get BBC iPlayer content recommendations.

    Args:
        genre: Filter by genre (drama, documentary, comedy, news, sport, entertainment)
        duration_minutes: Maximum duration in minutes

    Returns:
        List of recommended BBC iPlayer programmes
    """
    # Simulated iPlayer content
    all_content = [
        {
            'title': 'The Traitors',
            'genre': 'entertainment',
            'duration_minutes': 60,
            'series': 2,
            'episode': 8,
            'description': 'Psychological reality series where contestants compete in challenges',
            'available_until': (datetime.now() + timedelta(days=180)).strftime('%Y-%m-%d'),
            'rating': '15'
        },
        {
            'title': 'Planet Earth III',
            'genre': 'documentary',
            'duration_minutes': 55,
            'series': 3,
            'episode': 5,
            'description': 'David Attenborough explores extreme habitats',
            'available_until': (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'),
            'rating': 'U'
        },
        {
            'title': 'Happy Valley',
            'genre': 'drama',
            'duration_minutes': 58,
            'series': 3,
            'episode': 6,
            'description': 'Crime drama set in West Yorkshire',
            'available_until': (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d'),
            'rating': '15'
        },
        {
            'title': 'BBC News at Ten',
            'genre': 'news',
            'duration_minutes': 30,
            'description': 'Latest national and international news',
            'available_until': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'rating': 'U'
        },
        {
            'title': 'Match of the Day',
            'genre': 'sport',
            'duration_minutes': 90,
            'description': 'Premier League highlights and analysis',
            'available_until': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'rating': 'U'
        }
    ]

    # Filter by genre
    if genre:
        all_content = [c for c in all_content if c['genre'].lower() == genre.lower()]

    # Filter by duration
    if duration_minutes:
        all_content = [c for c in all_content if c['duration_minutes'] <= duration_minutes]

    return all_content

# --- Register Swiss voting tools ---
import sys
sys.path.append("servers/swiss-voting")  # Ensure path works even if run from project root
import swiss_voting_tools  # noqa: F401 (registers tools on import)

if __name__ == "__main__":
     mcp.run(transport="http", host="127.0.0.1", port=8000)