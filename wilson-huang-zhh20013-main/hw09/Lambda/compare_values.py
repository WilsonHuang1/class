def lambda_handler(event, context):
    """
    Lambda function to compare two numeric values.
    
    Parameters:
    - event: Dict containing:
        - value1: First numeric value (string)
        - value2: Second numeric value (string)
        - operation: String indicating the operation to perform
          ("equal", "notEqual", "greaterThan", "greaterThanOrEqual", 
           "lessThan", "lessThanOrEqual")
           
    Returns:
    - Dict with 'result' key containing a boolean value
    """
    # Extract values from the event
    value1 = float(event.get('value1', 0))
    value2 = float(event.get('value2', 0))
    operation = event.get('operation', 'equal')
    
    # Perform the requested comparison
    result = False
    
    if operation == 'equal':
        result = value1 == value2
    elif operation == 'notEqual':
        result = value1 != value2
    elif operation == 'greaterThan':
        result = value1 > value2
    elif operation == 'greaterThanOrEqual':
        result = value1 >= value2
    elif operation == 'lessThan':
        result = value1 < value2
    elif operation == 'lessThanOrEqual':
        result = value1 <= value2
    
    return {
        'result': result,
        'value1': value1,
        'value2': value2,
        'operation': operation
    }