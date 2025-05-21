"""Unit conversion module that provides functions to convert between different units of measurement.
Supports conversions for weight, temperature, distance, and area."""

def convert_weight(value, unit):
    """Convert between pounds and kilograms"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    if unit.lower() == 'lbs':
        return f"{value * 0.45359237:.3f} kg"
    if unit.lower() == 'kg':
        return f"{value * 2.20462262:.3f} lbs"
    return None

def convert_temperature(value, unit):
    """Convert between Fahrenheit and Celsius"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    if unit.upper() == 'F':
        celsius = (value - 32) * 5/9
        return f"{celsius:.1f} C"
    if unit.upper() == 'C':
        fahrenheit = (value * 9/5) + 32
        return f"{fahrenheit:.1f} F"
    return None

def convert_distance(value, unit):
    """Convert between feet and meters"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    if unit.lower() == 'f':
        return f"{value * 0.3048:.3f} m"
    if unit.lower() == 'm':
        return f"{value * 3.28084:.3f} f"
    return None

def convert_area(value, unit):
    """Convert between acres and square feet"""
    try:
        value = float(value)
    except (TypeError, ValueError):
        return None
    if unit.lower() == 'ac':
        sqft = value * 43560
        return f"{sqft:.2f} sqf"
    if unit.lower() == 'sqf':
        acres = value / 43560
        return f"{acres:.4f} ac"
    return None

def parse_input(user_input):
    """Parse user input into value and unit"""
    try:
        parts = user_input.strip().split()
        if len(parts) != 2:
            return None, None
        value = float(parts[0])
        unit = parts[1]
        return value, unit
    except (ValueError, IndexError):
        return None, None

def convert_units(value, unit):
    """Main conversion function that routes to specific conversion functions"""
    conversions = [
        convert_weight,
        convert_temperature,
        convert_distance,
        convert_area
    ]
    for conversion in conversions:
        result = conversion(value, unit)
        if result:
            return result
    return "Invalid unit. Please use: lbs/kg, F/C, f/m, ac/sqf"
