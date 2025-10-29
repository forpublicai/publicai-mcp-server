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

@mcp.tool()
def get_bbc_news(
    lang: str = "english",
    max_articles: Optional[int] = 10
) -> Dict[str, any]:
    """Get latest news articles from BBC News in various languages.

    Args:
        lang: Language code (e.g., "english", "bengali", "hindi", "arabic", "spanish")
        max_articles: Maximum number of articles to return (default: 10)

    Returns:
        Dictionary with latest BBC news articles including titles, summaries, images, and links
    """
    try:
        url = f"https://bbc-news-api.vercel.app/news?lang={urllib.parse.quote(lang)}"

        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode())

        if data.get('status') == 200:
            # Collect all articles from all sections
            all_articles = []

            for key, value in data.items():
                if key not in ['status', 'elapsed time', 'timestamp'] and isinstance(value, list):
                    for article in value:
                        # Skip articles with null titles and summaries
                        if article.get('title') or article.get('summary'):
                            all_articles.append({
                                'title': article.get('title', 'No title'),
                                'summary': article.get('summary', 'No summary'),
                                'image_url': article.get('image_link', ''),
                                'article_url': article.get('news_link', ''),
                                'section': key,
                                'source': 'BBC News'
                            })

            # Limit articles
            all_articles = all_articles[:max_articles]

            return {
                'status': 'success',
                'language': lang,
                'articles_count': len(all_articles),
                'articles': all_articles,
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'api_elapsed_time': data.get('elapsed time', 'N/A')
            }
        else:
            return {
                'status': 'error',
                'error': f"API returned status {data.get('status')}",
                'language': lang
            }
    except urllib.error.HTTPError as e:
        return {
            'status': 'error',
            'error': f"HTTP Error {e.code}: {e.reason}",
            'suggestion': 'Check if the language code is valid. Use get_bbc_languages() to see available languages.'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Failed to fetch BBC news: {str(e)}"
        }

@mcp.tool()
def get_bbc_latest_by_section(
    lang: str = "english"
) -> Dict[str, any]:
    """Get the most recent BBC News organized by sections/categories.

    Args:
        lang: Language code (e.g., "english", "bengali", "hindi", "arabic")

    Returns:
        Dictionary with news organized by sections (e.g., Top Stories, World, Business, etc.)
    """
    try:
        url = f"https://bbc-news-api.vercel.app/latest?lang={urllib.parse.quote(lang)}"

        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode())

        if data.get('status') == 200:
            sections = {}
            total_articles = 0

            # Extract all sections (everything except status, elapsed time, timestamp)
            for key, value in data.items():
                if key not in ['status', 'elapsed time', 'timestamp'] and isinstance(value, list):
                    sections[key] = [
                        {
                            'title': article.get('title', ''),
                            'summary': article.get('summary', ''),
                            'image_url': article.get('image_link', ''),
                            'article_url': article.get('news_link', ''),
                            'section': key
                        }
                        for article in value
                    ]
                    total_articles += len(sections[key])

            return {
                'status': 'success',
                'language': lang,
                'total_sections': len(sections),
                'total_articles': total_articles,
                'sections': sections,
                'section_names': list(sections.keys()),
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'api_elapsed_time': data.get('elapsed time', 'N/A'),
                'source': 'BBC News'
            }
        else:
            return {
                'status': 'error',
                'error': f"API returned status {data.get('status')}",
                'language': lang
            }
    except urllib.error.HTTPError as e:
        return {
            'status': 'error',
            'error': f"HTTP Error {e.code}: {e.reason}",
            'suggestion': 'Check if the language code is valid. Use get_bbc_languages() to see available languages.'
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Failed to fetch BBC latest news: {str(e)}"
        }

@mcp.tool()
def get_bbc_languages() -> Dict[str, any]:
    """Get a list of all supported languages for BBC News.

    Returns:
        Dictionary with all available BBC News language services, their codes, URLs, and descriptions
    """
    try:
        url = "https://bbc-news-api.vercel.app/languages"

        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode())

        if data.get('status') == 200:
            languages = data.get('languages', [])

            return {
                'status': 'success',
                'total_languages': len(languages),
                'languages': [
                    {
                        'code': lang.get('code', ''),
                        'name': lang.get('name', ''),
                        'url': lang.get('url', ''),
                        'description': lang.get('description', '')
                    }
                    for lang in languages
                ],
                'language_codes': [lang.get('code', '') for lang in languages],
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'usage_note': 'Use the language codes with get_bbc_news() or get_bbc_latest_by_section()'
            }
        else:
            return {
                'status': 'error',
                'error': f"API returned status {data.get('status')}"
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Failed to fetch BBC languages: {str(e)}"
        }

@mcp.tool()
def search_bbc_news_by_topic(
    topic: str,
    lang: str = "english",
    max_results: int = 5
) -> Dict[str, any]:
    """Search BBC News articles for a specific topic or keyword.

    Args:
        topic: Topic or keyword to search for (e.g., "climate", "economy", "technology")
        lang: Language code (default: "english")
        max_results: Maximum number of matching articles to return (default: 5)

    Returns:
        Dictionary with BBC news articles matching the topic
    """
    try:
        # Fetch latest news
        url = f"https://bbc-news-api.vercel.app/news?lang={urllib.parse.quote(lang)}"

        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode())

        if data.get('status') == 200:
            # Collect all articles from all sections
            all_articles = []

            for key, value in data.items():
                if key not in ['status', 'elapsed time', 'timestamp'] and isinstance(value, list):
                    for article in value:
                        if article.get('title') or article.get('summary'):
                            all_articles.append({
                                'title': article.get('title', ''),
                                'summary': article.get('summary', ''),
                                'image_link': article.get('image_link', ''),
                                'news_link': article.get('news_link', ''),
                                'section': key
                            })

            # Filter articles by topic (case-insensitive search in title and summary)
            topic_lower = topic.lower()
            matching_articles = []

            for article in all_articles:
                title = article.get('title', '').lower()
                summary = article.get('summary', '').lower()

                if topic_lower in title or topic_lower in summary:
                    matching_articles.append({
                        'title': article.get('title', ''),
                        'summary': article.get('summary', ''),
                        'image_url': article.get('image_link', ''),
                        'article_url': article.get('news_link', ''),
                        'section': article.get('section', ''),
                        'relevance': 'title match' if topic_lower in title else 'summary match'
                    })

                if len(matching_articles) >= max_results:
                    break

            return {
                'status': 'success',
                'search_topic': topic,
                'language': lang,
                'matches_found': len(matching_articles),
                'articles': matching_articles,
                'searched_articles': len(all_articles),
                'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'note': 'Search performed on latest BBC News articles. For comprehensive search, use BBC website directly.'
            }
        else:
            return {
                'status': 'error',
                'error': f"API returned status {data.get('status')}",
                'language': lang
            }
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Failed to search BBC news: {str(e)}"
        }

@mcp.tool()
def get_bbc_multilingual_headlines(
    languages: Optional[List[str]] = None,
    headlines_per_language: int = 3
) -> Dict[str, any]:
    """Get top headlines from BBC News in multiple languages simultaneously.

    Args:
        languages: List of language codes (e.g., ["english", "hindi", "arabic"]). If None, uses ["english", "spanish", "arabic"]
        headlines_per_language: Number of headlines per language (default: 3)

    Returns:
        Dictionary with top headlines organized by language
    """
    if languages is None:
        languages = ["english", "spanish", "arabic"]

    results = {
        'status': 'success',
        'languages_requested': languages,
        'headlines_by_language': {},
        'total_headlines': 0,
        'fetched_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    for lang in languages:
        try:
            url = f"https://bbc-news-api.vercel.app/news?lang={urllib.parse.quote(lang)}"

            with urllib.request.urlopen(url, timeout=15) as response:
                data = json.loads(response.read().decode())

            if data.get('status') == 200:
                # Collect all articles from all sections
                all_articles = []

                for key, value in data.items():
                    if key not in ['status', 'elapsed time', 'timestamp'] and isinstance(value, list):
                        for article in value:
                            if article.get('title') or article.get('summary'):
                                all_articles.append({
                                    'title': article.get('title', 'No title'),
                                    'summary': article.get('summary', 'No summary'),
                                    'news_link': article.get('news_link', ''),
                                    'section': key
                                })

                # Limit to requested number
                all_articles = all_articles[:headlines_per_language]

                results['headlines_by_language'][lang] = {
                    'language_name': lang.capitalize(),
                    'headlines': [
                        {
                            'title': article.get('title', ''),
                            'summary': article.get('summary', '')[:150] + '...' if len(article.get('summary', '')) > 150 else article.get('summary', ''),
                            'url': article.get('news_link', ''),
                            'section': article.get('section', '')
                        }
                        for article in all_articles
                    ],
                    'count': len(all_articles)
                }
                results['total_headlines'] += len(all_articles)
            else:
                results['headlines_by_language'][lang] = {
                    'language_name': lang.capitalize(),
                    'error': f"Failed to fetch (status {data.get('status')})",
                    'count': 0
                }
        except Exception as e:
            results['headlines_by_language'][lang] = {
                'language_name': lang.capitalize(),
                'error': str(e),
                'count': 0
            }

    return results

@mcp.tool()
def fact_check_claim(
    claim: str,
    source: Optional[str] = None,
    date_published: Optional[str] = None
) -> Dict[str, any]:
    """Oh Really? - Fact-checking service that provides references for claims made in the news.

    This tool helps verify claims by providing context, related facts, and authoritative sources.
    Particularly useful for BBC and UK news content verification.

    Args:
        claim: The claim or statement to fact-check (e.g., "The UK has the oldest broadcasting service in the world")
        source: Optional source where the claim was made (e.g., "BBC News", "The Guardian")
        date_published: Optional date when claim was published (YYYY-MM-DD format)

    Returns:
        Dictionary with fact-check results, verification status, references, and context
    """
    import random

    # This is a demonstration tool that shows the structure of fact-checking responses
    # In production, this would integrate with real fact-checking databases and APIs

    # Generate a fact-check reference ID
    check_id = f"BBC-FC-{random.randint(100000, 999999)}"

    # Simulate fact-checking logic
    claim_lower = claim.lower()

    # Example fact-checking responses based on common UK/BBC related claims
    fact_checks = {
        'bbc': {
            'verification': 'verified',
            'context': 'The BBC (British Broadcasting Corporation) is indeed one of the oldest and largest broadcasting organizations.',
            'key_facts': [
                'BBC founded in 1922 as British Broadcasting Company',
                'Became British Broadcasting Corporation in 1927',
                'BBC Archives contain material dating back to 1890',
                'Over 15 million items in BBC Archives'
            ],
            'sources': [
                {'title': 'BBC History', 'url': 'https://www.bbc.co.uk/historyofthebbc', 'type': 'official'},
                {'title': 'BBC Written Archives Centre', 'url': 'https://www.bbc.co.uk/archive', 'type': 'official'},
                {'title': 'BBC Royal Charter', 'url': 'https://www.bbc.com/aboutthebbc/governance', 'type': 'official'}
            ]
        },
        'archive': {
            'verification': 'verified',
            'context': 'The BBC Archives are one of the largest broadcast archives in the world.',
            'key_facts': [
                'Over 15 million items on 60 miles of shelving',
                'Approximately 1 million hours of playable media',
                'Television Archive: 1.5M+ tape items, 600K+ film cans',
                'Sound Archive: 700K vinyl records, 180K 78rpm records',
                'Photographic Library: 7 million images dating to 1922'
            ],
            'sources': [
                {'title': 'BBC Archives Wikipedia', 'url': 'https://en.wikipedia.org/wiki/BBC_Archives', 'type': 'reference'},
                {'title': 'BBC Archive Centre', 'url': 'https://www.bbc.co.uk/archive', 'type': 'official'}
            ]
        },
        'television': {
            'verification': 'partially-verified',
            'context': 'BBC Television Service began regular broadcasts in 1936.',
            'key_facts': [
                'BBC Television Service launched November 2, 1936',
                'World\'s first regular high-definition television service',
                'Suspended during WWII (1939-1946)',
                'Earliest archived BBC TV footage dates to 1936'
            ],
            'sources': [
                {'title': 'BBC History of Television', 'url': 'https://www.bbc.co.uk/historyofthebbc/timelines/television', 'type': 'official'},
                {'title': 'British Film Institute', 'url': 'https://www.bfi.org.uk/', 'type': 'archive'}
            ]
        },
        'nhs': {
            'verification': 'verified',
            'context': 'The National Health Service (NHS) provides healthcare to UK residents.',
            'key_facts': [
                'NHS founded on July 5, 1948',
                'Provides healthcare free at point of use',
                'Funded through taxation',
                'One of the largest employers in the world'
            ],
            'sources': [
                {'title': 'NHS Official Website', 'url': 'https://www.nhs.uk/about-us', 'type': 'official'},
                {'title': 'UK Government - NHS', 'url': 'https://www.gov.uk/government/organisations/nhs', 'type': 'government'}
            ]
        },
        'uk government': {
            'verification': 'context-needed',
            'context': 'UK Government claims require specific context and date verification.',
            'key_facts': [
                'UK is a constitutional monarchy with parliamentary democracy',
                'Government data available at gov.uk',
                'Parliamentary records available at parliament.uk',
                'Official statistics from Office for National Statistics (ONS)'
            ],
            'sources': [
                {'title': 'UK Government', 'url': 'https://www.gov.uk', 'type': 'government'},
                {'title': 'UK Parliament', 'url': 'https://www.parliament.uk', 'type': 'government'},
                {'title': 'Office for National Statistics', 'url': 'https://www.ons.gov.uk', 'type': 'statistics'}
            ]
        }
    }

    # Determine which fact-check template to use
    selected_check = None
    for key in fact_checks:
        if key in claim_lower:
            selected_check = fact_checks[key]
            break

    # Default response if no specific match
    if not selected_check:
        selected_check = {
            'verification': 'requires-investigation',
            'context': 'This claim requires further investigation with authoritative sources.',
            'key_facts': [
                'Always verify claims with multiple authoritative sources',
                'Check publication dates and context',
                'Look for primary sources when possible',
                'Consider potential bias in sources'
            ],
            'sources': [
                {'title': 'BBC Reality Check', 'url': 'https://www.bbc.co.uk/news/reality_check', 'type': 'fact-checking'},
                {'title': 'Full Fact UK', 'url': 'https://fullfact.org', 'type': 'fact-checking'},
                {'title': 'UK Government Statistics', 'url': 'https://www.gov.uk/search/research-and-statistics', 'type': 'statistics'}
            ]
        }

    # Build response
    response = {
        'fact_check_id': check_id,
        'claim': claim,
        'verification_status': selected_check['verification'],
        'status_explanation': {
            'verified': 'Claim is supported by authoritative sources',
            'partially-verified': 'Claim is partially accurate but needs context',
            'context-needed': 'Claim requires additional context to verify',
            'requires-investigation': 'Claim needs further investigation',
            'disputed': 'Claim is disputed by authoritative sources',
            'false': 'Claim is contradicted by authoritative sources'
        }.get(selected_check['verification'], 'Status unknown'),
        'context': selected_check['context'],
        'key_facts': selected_check['key_facts'],
        'authoritative_sources': selected_check['sources'],
        'verification_date': datetime.now().strftime('%Y-%m-%d'),
        'source_metadata': {
            'claim_source': source if source else 'Not specified',
            'date_published': date_published if date_published else 'Not specified'
        },
        'bbc_credit': 'Fact-checking powered by BBC-style verification standards',
        'methodology': [
            '1. Identify claim and extract key assertions',
            '2. Search authoritative sources (government, academic, official records)',
            '3. Cross-reference multiple sources',
            '4. Provide context and nuance',
            '5. Cite primary sources where possible'
        ],
        'recommended_actions': {
            'verified': 'Claim appears accurate based on available sources',
            'partially-verified': 'Review additional context before sharing',
            'context-needed': 'Seek more information about specific circumstances',
            'requires-investigation': 'Verify with multiple authoritative sources before accepting',
            'disputed': 'Be aware of conflicting information from reliable sources',
            'false': 'Do not share; claim contradicted by evidence'
        }.get(selected_check['verification'], 'Investigate further'),
        'additional_resources': {
            'uk_fact_checking': [
                'BBC Reality Check',
                'Full Fact',
                'Channel 4 FactCheck'
            ],
            'uk_government_data': [
                'gov.uk/search/research-and-statistics',
                'Office for National Statistics (ONS)',
                'UK Parliament Hansard'
            ],
            'archives': [
                'BBC Archives',
                'British Library',
                'The National Archives'
            ]
        },
        'note': 'DEMO FACT-CHECK - This demonstrates BBC-quality fact-checking methodology. In production, would integrate with real-time fact-checking databases and AI-powered verification.'
    }

    return response

@mcp.tool()
def generate_uk_archive_alt_text(
    image_description: str,
    archive_context: Optional[str] = None,
    date_circa: Optional[str] = None,
    format_type: Optional[str] = None
) -> Dict[str, any]:
    """Generate descriptive alt text for UK archive images (BBC Archives, British Film Institute, National Archives, etc.).

    This tool helps make historical archive materials more accessible by generating comprehensive,
    descriptive alt text that follows archival and accessibility best practices.

    Args:
        image_description: Basic description of what's visible in the image (e.g., "black and white photo of broadcasting equipment")
        archive_context: Optional context about the source (e.g., "BBC Television Archive", "British Film Institute collection")
        date_circa: Optional approximate date or era (e.g., "1936", "1960s", "mid-1950s")
        format_type: Optional original format (e.g., "film still", "publicity photograph", "telerecording", "wax cylinder label")

    Returns:
        Dictionary with generated alt text in various lengths and accessibility compliance information
    """
    # Build comprehensive alt text
    alt_text_parts = []

    # Add format context if provided
    if format_type:
        alt_text_parts.append(format_type.capitalize())

    # Add date context
    if date_circa:
        alt_text_parts.append(f"circa {date_circa}")

    # Add main description
    alt_text_parts.append(image_description)

    # Add archive context
    if archive_context:
        alt_text_parts.append(f"From {archive_context}")

    # Generate different length versions
    full_alt_text = ". ".join(alt_text_parts)

    # Short version (<=125 characters) - WCAG recommended
    short_version = image_description[:120] + "..." if len(image_description) > 125 else image_description

    # Medium version (descriptive but concise)
    medium_parts = [image_description]
    if date_circa:
        medium_parts.append(f"circa {date_circa}")
    medium_version = ". ".join(medium_parts)

    # Generate structured metadata
    metadata = {
        'description': image_description,
        'temporal_context': date_circa if date_circa else 'unknown',
        'format': format_type if format_type else 'photograph',
        'archive_source': archive_context if archive_context else 'UK archives'
    }

    # Accessibility tips based on content
    accessibility_tips = [
        "Alt text should describe the image content, not interpret it",
        "For historical images, include temporal context when known",
        "Avoid starting with 'Image of' or 'Picture of'"
    ]

    if format_type and 'film' in format_type.lower():
        accessibility_tips.append("For film stills, mention if it's a scene or behind-the-scenes")

    return {
        'alt_text_short': short_version,
        'alt_text_medium': medium_version,
        'alt_text_full': full_alt_text,
        'character_count': {
            'short': len(short_version),
            'medium': len(medium_version),
            'full': len(full_alt_text)
        },
        'metadata': metadata,
        'wcag_compliant': len(short_version) <= 125,
        'accessibility_tips': accessibility_tips,
        'example_usage': {
            'html': f'<img src="archive-image.jpg" alt="{medium_version}">',
            'markdown': f'![{medium_version}](archive-image.jpg)',
            'aria_label': medium_version
        },
        'archive_context': {
            'bbc_archives': 'Over 15 million items spanning 1890-present',
            'collections': [
                'BBC Television Archive (1.5M+ tape items)',
                'BBC Sound Archive (700K vinyl, 180K 78rpm records)',
                'BBC Written Archives (1922-present)',
                'BBC Photographic Library (7M images)',
                'Heritage Collection (broadcast technology, props)'
            ],
            'access_note': 'Material being digitized from analogue formats for preservation'
        }
    }

if __name__ == "__main__":
     mcp.run(transport="http", host="127.0.0.1", port=8000)