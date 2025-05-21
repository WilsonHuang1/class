'''Pytests for convert.py'''
import pytest # pylint: disable=unused-import
import convert

def test_weight_conversion():
    '''Test the convert_weight function'''
    # Test pounds to kilograms
    assert convert.convert_weight(1, 'lbs') == "0.454 kg"
    assert convert.convert_weight(0, 'lbs') == "0.000 kg"
    assert convert.convert_weight(-1, 'lbs') == "-0.454 kg"
    assert convert.convert_weight(1000, 'lbs') == "453.592 kg"
    assert convert.convert_weight(-1000, 'lbs') == "-453.592 kg"

    # Test kilograms to pounds
    assert convert.convert_weight(1, 'kg') == "2.205 lbs"
    assert convert.convert_weight(0, 'kg') == "0.000 lbs"
    assert convert.convert_weight(-1, 'kg') == "-2.205 lbs"
    assert convert.convert_weight(1000, 'kg') == "2204.623 lbs"
    assert convert.convert_weight(-1000, 'kg') == "-2204.623 lbs"

    # Test invalid inputs
    assert convert.convert_weight(None, 'kg') is None
    assert convert.convert_weight('abc', 'lbs') is None
    assert convert.convert_weight(1, 'invalid') is None

def test_temperature_conversion():
    '''Test the convert_temperature function'''
    # Test Fahrenheit to Celsius
    assert convert.convert_temperature(32, 'F') == "0.0 C"
    assert convert.convert_temperature(0, 'F') == "-17.8 C"
    assert convert.convert_temperature(-1, 'F') == "-18.3 C"
    assert convert.convert_temperature(212, 'F') == "100.0 C"
    assert convert.convert_temperature(1000, 'F') == "537.8 C"
    assert convert.convert_temperature(-1000, 'F') == "-573.3 C"

    # Test Celsius to Fahrenheit
    assert convert.convert_temperature(0, 'C') == "32.0 F"
    assert convert.convert_temperature(100, 'C') == "212.0 F"
    assert convert.convert_temperature(-40, 'C') == "-40.0 F"
    assert convert.convert_temperature(1000, 'C') == "1832.0 F"
    assert convert.convert_temperature(-1000, 'C') == "-1768.0 F"

    # Test invalid inputs
    assert convert.convert_temperature(None, 'F') is None
    assert convert.convert_temperature('abc', 'C') is None
    assert convert.convert_temperature(1, 'invalid') is None

def test_distance_conversion():
    '''Test the convert_distance function'''
    # Test feet to meters
    assert convert.convert_distance(1, 'f') == "0.305 m"
    assert convert.convert_distance(0, 'f') == "0.000 m"
    assert convert.convert_distance(-1, 'f') == "-0.305 m"
    assert convert.convert_distance(1000, 'f') == "304.800 m"
    assert convert.convert_distance(-1000, 'f') == "-304.800 m"

    # Test meters to feet
    assert convert.convert_distance(1, 'm') == "3.281 f"
    assert convert.convert_distance(0, 'm') == "0.000 f"
    assert convert.convert_distance(-1, 'm') == "-3.281 f"
    assert convert.convert_distance(1000, 'm') == "3280.840 f"
    assert convert.convert_distance(-1000, 'm') == "-3280.840 f"

    # Test invalid inputs
    assert convert.convert_distance(None, 'm') is None
    assert convert.convert_distance('abc', 'f') is None
    assert convert.convert_distance(1, 'invalid') is None

def test_area_conversion():
    '''Test the convert_area function'''
    # Test acres to square feet
    assert convert.convert_area(1, 'ac') == "43560.00 sqf"
    assert convert.convert_area(0, 'ac') == "0.00 sqf"
    assert convert.convert_area(-1, 'ac') == "-43560.00 sqf"
    assert convert.convert_area(1000, 'ac') == "43560000.00 sqf"
    assert convert.convert_area(-1000, 'ac') == "-43560000.00 sqf"

    # Test square feet to acres
    assert convert.convert_area(43560, 'sqf') == "1.0000 ac"
    assert convert.convert_area(0, 'sqf') == "0.0000 ac"
    assert convert.convert_area(-43560, 'sqf') == "-1.0000 ac"
    assert convert.convert_area(1000000, 'sqf') == "22.9568 ac"
    assert convert.convert_area(-1000000, 'sqf') == "-22.9568 ac"

    # Test invalid inputs
    assert convert.convert_area(None, 'ac') is None
    assert convert.convert_area('abc', 'sqf') is None
    assert convert.convert_area(1, 'invalid') is None

def test_parse_input():
    '''Test the parse_input function'''
    assert convert.parse_input("1 lbs") == (1, "lbs")
    assert convert.parse_input("0 F") == (0, "F")
    assert convert.parse_input("-1 m") == (-1, "m")
    assert convert.parse_input("1000 ac") == (1000, "ac")
    assert convert.parse_input("-1000 sqf") == (-1000, "sqf")

    # Test invalid inputs
    assert convert.parse_input("") == (None, None)
    assert convert.parse_input("abc") == (None, None)
    assert convert.parse_input("1.2.3 kg") == (None, None)
    assert convert.parse_input("kg 100") == (None, None)
    assert convert.parse_input("1 2 3") == (None, None)

def test_convert_units():
    '''Test the convert_units function'''
    # Test valid conversions
    assert convert.convert_units(1, 'lbs') == "0.454 kg"
    assert convert.convert_units(32, 'F') == "0.0 C"
    assert convert.convert_units(1, 'm') == "3.281 f"
    assert convert.convert_units(1, 'ac') == "43560.00 sqf"

    # Test invalid units
    result = convert.convert_units(1, 'invalid')
    assert "Invalid unit" in result
    assert "lbs/kg" in result
    assert "F/C" in result
    assert "f/m" in result
    assert "ac/sqf" in result
