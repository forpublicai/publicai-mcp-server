from fastmcp import FastMCP
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import math

mcp = FastMCP("Public AI MCP Server")

@mcp.tool()
def greet(name: str) -> str:
    """Greet a person by name.

    Args:
        name: The name of the person to greet
    """
    return f"Hello, {name}!"

@mcp.tool()
def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12
) -> Dict[str, float]:
    """Calculate compound interest with detailed breakdown.

    Args:
        principal: Initial investment amount
        annual_rate: Annual interest rate as percentage (e.g., 5.5 for 5.5%)
        years: Number of years to compound
        compounds_per_year: Compounding frequency per year (default: 12 for monthly)

    Returns:
        Dictionary with total amount, interest earned, and effective rate
    """
    rate = annual_rate / 100
    amount = principal * math.pow(1 + rate/compounds_per_year, compounds_per_year * years)
    interest = amount - principal
    effective_rate = (amount / principal - 1) * 100

    return {
        "principal": round(principal, 2),
        "total_amount": round(amount, 2),
        "interest_earned": round(interest, 2),
        "effective_rate_percent": round(effective_rate, 2),
        "years": years
    }

@mcp.tool()
def analyze_text_sentiment(text: str) -> Dict[str, any]:
    """Analyze text for basic sentiment indicators and metrics.

    Args:
        text: The text to analyze

    Returns:
        Dictionary with word count, sentence count, and sentiment indicators
    """
    # Simple sentiment word lists
    positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
                     'love', 'best', 'perfect', 'happy', 'joy', 'awesome', 'brilliant'}
    negative_words = {'bad', 'terrible', 'awful', 'hate', 'worst', 'horrible',
                     'poor', 'disappointing', 'sad', 'angry', 'frustrating', 'useless'}

    words = text.lower().split()
    sentences = text.count('.') + text.count('!') + text.count('?')
    sentences = max(1, sentences)  # At least 1 sentence

    positive_count = sum(1 for word in words if any(pos in word for pos in positive_words))
    negative_count = sum(1 for word in words if any(neg in word for neg in negative_words))

    sentiment_score = positive_count - negative_count
    if sentiment_score > 0:
        sentiment = "positive"
    elif sentiment_score < 0:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "word_count": len(words),
        "sentence_count": sentences,
        "avg_words_per_sentence": round(len(words) / sentences, 1),
        "positive_indicators": positive_count,
        "negative_indicators": negative_count,
        "sentiment": sentiment,
        "sentiment_score": sentiment_score
    }

@mcp.tool()
def generate_meeting_times(
    start_date: str,
    num_weeks: int = 4,
    day_of_week: str = "Monday",
    time: str = "10:00"
) -> List[str]:
    """Generate recurring meeting times for scheduling.

    Args:
        start_date: Starting date in YYYY-MM-DD format
        num_weeks: Number of weeks to generate (default: 4)
        day_of_week: Day of week for meetings (Monday-Sunday)
        time: Time in HH:MM format (default: 10:00)

    Returns:
        List of formatted meeting date-times
    """
    days = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
        "friday": 4, "saturday": 5, "sunday": 6
    }

    target_day = days.get(day_of_week.lower())
    if target_day is None:
        return [f"Error: Invalid day of week '{day_of_week}'"]

    try:
        current_date = datetime.strptime(start_date, "%Y-%m-%d")
    except ValueError:
        return [f"Error: Invalid date format '{start_date}'. Use YYYY-MM-DD"]

    # Find the first occurrence of target day
    days_ahead = target_day - current_date.weekday()
    if days_ahead < 0:
        days_ahead += 7
    first_meeting = current_date + timedelta(days=days_ahead)

    meetings = []
    for week in range(num_weeks):
        meeting_date = first_meeting + timedelta(weeks=week)
        meetings.append(f"{meeting_date.strftime('%Y-%m-%d (%A)')} at {time}")

    return meetings

@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> Dict[str, any]:
    """Convert between common units of measurement.

    Args:
        value: The numeric value to convert
        from_unit: Source unit (kg, lb, km, mi, c, f, m, ft, etc.)
        to_unit: Target unit

    Returns:
        Dictionary with original value, converted value, and units
    """
    # Conversion factors to base units
    conversions = {
        # Weight (to kg)
        'kg': 1.0, 'lb': 0.453592, 'oz': 0.0283495, 'g': 0.001,
        # Distance (to meters)
        'm': 1.0, 'km': 1000, 'mi': 1609.34, 'ft': 0.3048, 'in': 0.0254, 'cm': 0.01,
        # Temperature (special case)
        'c': 'celsius', 'f': 'fahrenheit', 'k': 'kelvin'
    }

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    # Handle temperature separately
    if from_unit in ['c', 'f', 'k'] or to_unit in ['c', 'f', 'k']:
        # Convert to Celsius first
        if from_unit == 'f':
            celsius = (value - 32) * 5/9
        elif from_unit == 'k':
            celsius = value - 273.15
        else:
            celsius = value

        # Convert from Celsius to target
        if to_unit == 'f':
            result = celsius * 9/5 + 32
        elif to_unit == 'k':
            result = celsius + 273.15
        else:
            result = celsius

        return {
            "original_value": value,
            "original_unit": from_unit.upper(),
            "converted_value": round(result, 2),
            "converted_unit": to_unit.upper()
        }

    # Handle other units
    if from_unit not in conversions or to_unit not in conversions:
        return {"error": f"Unsupported unit conversion: {from_unit} to {to_unit}"}

    # Check if units are compatible (same base unit type)
    base_from = conversions[from_unit]
    base_to = conversions[to_unit]

    # Convert to base unit, then to target unit
    base_value = value * base_from
    result = base_value / base_to

    return {
        "original_value": value,
        "original_unit": from_unit,
        "converted_value": round(result, 4),
        "converted_unit": to_unit
    }

if __name__ == "__main__":
     mcp.run(transport="http", host="127.0.0.1", port=8000)