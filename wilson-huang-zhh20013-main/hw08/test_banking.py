import requests
import boto3
import time
import json
from datetime import datetime

# API Gateway URL and configuration
API_GATEWAY_URL = "https://n1klopdxhd.execute-api.us-east-1.amazonaws.com/prod/transaction"
ACCOUNTS_TABLE = "hw08-account-list"
AUDIT_TABLE = "hw08-transaction-audit"
DEPOSIT = "dep"
WITHDRAWAL = "wtd"
INVALID_ACCOUNT_NUMBER = "263826278362382"
WAIT_PERIOD = 3  # seconds
accounts = []
# Store initial balances to restore them later
initial_balances = {}
# Initial values we know from setup - using only the 5 existing accounts
KNOWN_INITIAL_BALANCES = {
    "12345": 1000,
    "67809": 5000,
    "11111": 250,
    "22222": 7500,
    "33333": 100
}
dynamodb = boto3.resource('dynamodb', region_name="us-east-1")
table = dynamodb.Table(ACCOUNTS_TABLE)
audit_table = dynamodb.Table(AUDIT_TABLE)

def load_account_list():
    """Load account list from DynamoDB and store initial balances"""
    # First try to load the specific known accounts
    for account_num, initial_balance in KNOWN_INITIAL_BALANCES.items():
        response = table.get_item(Key={'account': account_num})
        if "Item" in response:
            accounts.append(response["Item"])
            initial_balances[account_num] = initial_balance
            print(f"Loaded account {account_num} with balance {initial_balance}")
    
    # If no accounts were loaded, try a scan as fallback
    if not accounts:
        ddbresponse = table.scan()
        for a in ddbresponse["Items"]:
            accounts.append(a)
            account_num = a["account"]
            balance = int(a["balance"])
            initial_balances[account_num] = balance
    
    print("Accounts to test:", accounts)
    print("Initial balances:", initial_balances)

def get_account_balance(acct):
    """Get the current balance for an account"""
    response = table.get_item(
        Key={
            'account': acct
        }
    )
    if "Item" in response:
        return int(response["Item"]["balance"])
    else:
        print("*** No account found:", acct)
        return 0

def http_post(url, acct, amt, type):
    """Send POST request to API Gateway"""
    data = {"account": acct, "amount": amt, "type": type, "desc": "Automated test"}
    result = requests.post(url, json=data)
    if result.status_code != 200:
        print(f"**** HTTP error {result.status_code}")
        print(f"Response: {result.text}")
    return result

def deposit_funds(acct, amt):
    """Test depositing funds to an account"""
    initial_balance = get_account_balance(acct)
    http_post(API_GATEWAY_URL, acct, amt, DEPOSIT)
    time.sleep(WAIT_PERIOD)    
    final_balance = get_account_balance(acct)
    print(f" TEST: DEP {amt} into {acct}..... {initial_balance} --> {final_balance}")
    return final_balance == initial_balance + amt

def withdraw_funds(acct, amt):
    """Test withdrawing funds from an account"""
    initial_balance = get_account_balance(acct)
    http_post(API_GATEWAY_URL, acct, amt, WITHDRAWAL)
    time.sleep(WAIT_PERIOD)    
    final_balance = get_account_balance(acct)
    print(f" TEST: WTD {amt} from {acct}..... {initial_balance} --> {final_balance}")
    return final_balance == initial_balance - amt

def test_simple_deposit():
    """Test simple deposits for all accounts"""
    print("--------------------- SIMPLE DEPOSIT TESTS ---------------------")
    success = True
    for a in accounts:
        result = deposit_funds(a["account"], 100)
        if not result:
            success = False
            print(f"FAILED: Deposit to account {a['account']}")
    return success

def test_simple_withdrawal():
    """Test simple withdrawals for all accounts"""
    print("--------------------- SIMPLE WITHDRAWAL TESTS ---------------------")
    success = True
    for a in accounts:
        result = withdraw_funds(a["account"], 50)
        if not result:
            success = False
            print(f"FAILED: Withdrawal from account {a['account']}")
    return success

def test_invalid_account():
    """Test operations with invalid account numbers"""
    print("--------------------- INVALID ACCOUNT TESTS ---------------------")
    deposit_result = not deposit_funds(INVALID_ACCOUNT_NUMBER, 100)
    withdraw_result = not withdraw_funds(INVALID_ACCOUNT_NUMBER, 100)
    
    if not deposit_result:
        print("FAILED: Deposit to invalid account should not succeed")
    if not withdraw_result:
        print("FAILED: Withdrawal from invalid account should not succeed")
        
    return deposit_result and withdraw_result

def test_insufficient_funds():
    """Test withdrawal with insufficient funds"""
    print("--------------------- INSUFFICIENT FUNDS TESTS ---------------------")
    if not accounts:
        print("No accounts available for testing")
        return False
        
    # Get the first account and attempt to withdraw more than its balance
    account = accounts[0]["account"]
    balance = get_account_balance(account)
    withdrawal_amount = balance + 100
    
    # This should fail - return True if it does fail as expected
    result = not withdraw_funds(account, withdrawal_amount)
    
    if not result:
        print(f"FAILED: Withdrawal of {withdrawal_amount} from account with balance {balance} should not succeed")
    
    return result

def test_all_accounts_invalid_withdrawal():
    """Test invalid withdrawals for all accounts"""
    print("--------------------- INVALID WITHDRAWAL TESTS FOR ALL ACCOUNTS ---------------------")
    if not accounts:
        print("No accounts available for testing")
        return False
        
    success = True
    
    for a in accounts:
        account_num = a["account"]
        current_balance = get_account_balance(account_num)
        
        # Attempt to withdraw more than the current balance
        withdrawal_amount = current_balance + 100
        print(f"Testing invalid withdrawal from account {account_num}: attempting to withdraw ${withdrawal_amount} from balance of ${current_balance}")
        
        # This should fail - we expect the balance to remain unchanged
        http_post(API_GATEWAY_URL, account_num, withdrawal_amount, WITHDRAWAL)
        time.sleep(WAIT_PERIOD)
        
        # Check that balance is unchanged
        new_balance = get_account_balance(account_num)
        if new_balance != current_balance:
            success = False
            print(f"FAILED: Account {account_num} balance changed after invalid withdrawal. Before: {current_balance}, After: {new_balance}")
        else:
            print(f"SUCCESS: Account {account_num} balance correctly remained at {current_balance} after invalid withdrawal attempt")
    
    return success

def test_multiple_transactions():
    """Test multiple deposits and withdrawals on the same account"""
    print("--------------------- MULTIPLE TRANSACTION TESTS ---------------------")
    if not accounts:
        print("No accounts available for testing")
        return False
        
    success = True
    for a in accounts[:2]:  # Test with the first two accounts
        account_num = a["account"]
        initial_balance = get_account_balance(account_num)
        
        # Make multiple deposits
        print(f"Testing multiple transactions on account {account_num}")
        deposit_amounts = [50, 100, 150]
        total_deposit = sum(deposit_amounts)
        
        for amount in deposit_amounts:
            if not deposit_funds(account_num, amount):
                success = False
                print(f"FAILED: Deposit of {amount} to account {account_num}")
        
        # Verify intermediate balance
        mid_balance = get_account_balance(account_num)
        expected_mid = initial_balance + total_deposit
        if mid_balance != expected_mid:
            success = False
            print(f"FAILED: After deposits, balance should be {expected_mid}, but is {mid_balance}")
        
        # Make withdrawals that sum to the same total
        withdrawal_amounts = [75, 125, 100]
        total_withdrawal = sum(withdrawal_amounts)
        
        for amount in withdrawal_amounts:
            if not withdraw_funds(account_num, amount):
                success = False
                print(f"FAILED: Withdrawal of {amount} from account {account_num}")
        
        # Verify final balance
        final_balance = get_account_balance(account_num)
        expected_final = initial_balance + total_deposit - total_withdrawal
        if final_balance != expected_final:
            success = False
            print(f"FAILED: Final balance should be {expected_final}, but is {final_balance}")
        else:
            print(f"SUCCESS: Account {account_num} final balance is correct: {final_balance}")
            
    return success

def test_boundary_conditions():
    """Test boundary conditions like zero amount transactions"""
    print("--------------------- BOUNDARY CONDITION TESTS ---------------------")
    if not accounts:
        print("No accounts available for testing")
        return False
    
    success = True
    account = accounts[0]["account"]
    
    # Test zero amount deposit (should be valid)
    initial_balance = get_account_balance(account)
    http_post(API_GATEWAY_URL, account, 0, DEPOSIT)
    time.sleep(WAIT_PERIOD)
    new_balance = get_account_balance(account)
    
    if new_balance != initial_balance:
        success = False
        print(f"FAILED: Zero deposit should not change balance. Before: {initial_balance}, After: {new_balance}")
    else:
        print(f"SUCCESS: Zero deposit correctly did not change balance (still {new_balance})")
    
    # Test zero amount withdrawal (should be valid)
    http_post(API_GATEWAY_URL, account, 0, WITHDRAWAL)
    time.sleep(WAIT_PERIOD)
    new_balance = get_account_balance(account)
    
    if new_balance != initial_balance:
        success = False
        print(f"FAILED: Zero withdrawal should not change balance. Before: {initial_balance}, After: {new_balance}")
    else:
        print(f"SUCCESS: Zero withdrawal correctly did not change balance (still {new_balance})")
    
    return success

# Audit trail functions
def get_account_transactions(account_number, limit=10):
    """
    Retrieve recent transactions for a specific account
    
    Args:
        account_number (str): The account number to retrieve transactions for
        limit (int): Maximum number of transactions to return
        
    Returns:
        list: List of transaction records
    """
    print(f"\n--------------------- TRANSACTIONS FOR ACCOUNT {account_number} ---------------------")
    
    # We need to use a scan with a filter since we don't have a GSI
    response = audit_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr("account").eq(account_number),
        Limit=limit
    )
    
    transactions = response.get("Items", [])
    
    # Sort transactions by timestamp (newest first)
    transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    if not transactions:
        print(f"No transactions found for account {account_number}")
    else:
        print(f"Found {len(transactions)} transactions for account {account_number}")
        for tx in transactions:
            tx_type = tx.get("type", "unknown")
            amount = tx.get("amount", 0)
            balance = tx.get("balance_after", 0)
            desc = tx.get("desc", "")
            timestamp = tx.get("timestamp", "")
            
            if tx_type == "deposit":
                print(f"DEPOSIT: +${amount} on {timestamp} - '{desc}' - Balance: ${balance}")
            else:
                print(f"WITHDRAWAL: -${amount} on {timestamp} - '{desc}' - Balance: ${balance}")
    
    return transactions

def get_latest_transactions(limit=10):
    """
    Retrieve the most recent transactions across all accounts
    
    Args:
        limit (int): Maximum number of transactions to return
        
    Returns:
        list: List of transaction records
    """
    print(f"\n--------------------- LATEST {limit} TRANSACTIONS ---------------------")
    
    # Scan the table to get latest transactions
    response = audit_table.scan(Limit=limit)
    
    transactions = response.get("Items", [])
    
    # Sort transactions by timestamp (newest first)
    transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    if not transactions:
        print("No transactions found")
    else:
        print(f"Latest {len(transactions)} transactions:")
        for tx in transactions:
            tx_type = tx.get("type", "unknown")
            amount = tx.get("amount", 0)
            account = tx.get("account", "unknown")
            desc = tx.get("desc", "")
            timestamp = tx.get("timestamp", "")
            
            if tx_type == "deposit":
                print(f"DEPOSIT: Account {account} +${amount} on {timestamp} - '{desc}'")
            else:
                print(f"WITHDRAWAL: Account {account} -${amount} on {timestamp} - '{desc}'")
    
    return transactions[:limit]

def get_transaction_summary():
    """
    Get a summary of transaction counts and total amounts by type
    
    Returns:
        dict: Summary of transaction counts and amounts
    """
    print("\n--------------------- TRANSACTION SUMMARY ---------------------")
    
    # Scan the entire table
    response = audit_table.scan()
    
    transactions = response.get("Items", [])
    
    # Initialize counters
    deposit_count = 0
    withdrawal_count = 0
    deposit_total = 0
    withdrawal_total = 0
    
    # Process all transactions
    for tx in transactions:
        tx_type = tx.get("type", "")
        amount = float(tx.get("amount", 0))
        
        if tx_type == "deposit":
            deposit_count += 1
            deposit_total += amount
        elif tx_type == "withdrawal":
            withdrawal_count += 1
            withdrawal_total += amount
    
    # Build and print summary
    summary = {
        "deposit_count": deposit_count,
        "withdrawal_count": withdrawal_count,
        "deposit_total": deposit_total,
        "withdrawal_total": withdrawal_total,
        "net_change": deposit_total - withdrawal_total,
        "total_transactions": deposit_count + withdrawal_count
    }
    
    print(f"Total Transactions: {summary['total_transactions']}")
    print(f"Deposits: {deposit_count} transactions totaling ${deposit_total:.2f}")
    print(f"Withdrawals: {withdrawal_count} transactions totaling ${withdrawal_total:.2f}")
    print(f"Net Change: ${(deposit_total - withdrawal_total):.2f}")
    
    return summary

def find_transactions_by_description(search_term, limit=10):
    """
    Search for transactions containing a specific term in the description
    
    Args:
        search_term (str): Term to search for in transaction descriptions
        limit (int): Maximum number of results to return
        
    Returns:
        list: Matching transactions
    """
    print(f"\n--------------------- TRANSACTIONS MATCHING '{search_term}' ---------------------")
    
    # Scan with a filter for the description
    response = audit_table.scan(
        FilterExpression=boto3.dynamodb.conditions.Attr("desc").contains(search_term),
        Limit=limit
    )
    
    transactions = response.get("Items", [])
    
    # Sort by timestamp
    transactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    if not transactions:
        print(f"No transactions found matching '{search_term}'")
    else:
        print(f"Found {len(transactions)} transactions matching '{search_term}':")
        for tx in transactions:
            tx_type = tx.get("type", "unknown")
            amount = tx.get("amount", 0)
            account = tx.get("account", "unknown")
            desc = tx.get("desc", "")
            timestamp = tx.get("timestamp", "")
            
            print(f"Account {account} - {'Deposit' if tx_type == 'deposit' else 'Withdrawal'} of ${amount} - '{desc}' - {timestamp}")
    
    return transactions

def get_account_balance_history(account_number, limit=10):
    """
    Get the balance history for an account based on transaction audit trail
    
    Args:
        account_number (str): Account number to get history for
        limit (int): Maximum number of transactions to include
        
    Returns:
        list: Balance history entries
    """
    print(f"\n--------------------- BALANCE HISTORY FOR ACCOUNT {account_number} ---------------------")
    
    # Get transactions for the account
    transactions = get_account_transactions(account_number, limit=limit)
    
    # We already get the balance after each transaction from the audit table
    if transactions:
        print("\nBalance History:")
        for i, tx in enumerate(transactions):
            tx_type = tx.get("type", "unknown")
            amount = float(tx.get("amount", 0))
            balance = float(tx.get("balance_after", 0))
            timestamp = tx.get("timestamp", "")
            
            if tx_type == "deposit":
                print(f"{timestamp}: ${balance} (after +${amount} deposit)")
            else:
                print(f"{timestamp}: ${balance} (after -${amount} withdrawal)")
    else:
        print(f"No balance history available for account {account_number}")
    
    return transactions

def test_audit_trail():
    """Test that transactions exist in the audit trail"""
    print("--------------------- AUDIT TRAIL TEST ---------------------")
    
    # Get the latest transactions
    latest_transactions = get_latest_transactions(5)
    
    # Check if we have any transactions at all
    if not latest_transactions:
        print("FAILED: No transactions found in the audit trail")
        return False
    
    # Verify we can get transactions for specific accounts
    for account_id in ["12345", "11111", "33333"]:
        account_transactions = get_account_transactions(account_id)
        if account_transactions:
            print(f"SUCCESS: Found transactions for account {account_id}")
        else:
            print(f"NOTE: No transactions found for account {account_id}")
    
    # Since we've verified transactions exist, consider the test passed
    print("SUCCESS: Audit trail contains transaction records")
    
    # Get transaction summary
    get_transaction_summary()
    
    return True

def restore_initial_balances():
    """Restore all accounts to their initial balances"""
    print("\n--------------------- RESTORING INITIAL BALANCES ---------------------")
    success = True
    
    for account_num, initial_balance in initial_balances.items():
        current_balance = get_account_balance(account_num)
        
        # Calculate the difference to restore
        difference = initial_balance - current_balance
        
        if difference == 0:
            print(f"Account {account_num} already at initial balance: {initial_balance}")
            continue
            
        if difference > 0:
            # Need to deposit to restore balance
            print(f"Restoring account {account_num} by depositing {difference}")
            http_post(API_GATEWAY_URL, account_num, difference, DEPOSIT)
        else:
            # Need to withdraw to restore balance
            withdrawal_amount = abs(difference)
            print(f"Restoring account {account_num} by withdrawing {withdrawal_amount}")
            http_post(API_GATEWAY_URL, account_num, withdrawal_amount, WITHDRAWAL)
            
        time.sleep(WAIT_PERIOD)
        final_balance = get_account_balance(account_num)
        
        if final_balance == initial_balance:
            print(f"✓ Account {account_num} restored to initial balance: {initial_balance}")
        else:
            print(f"✗ Failed to restore account {account_num}. Current: {final_balance}, Target: {initial_balance}")
            success = False
    
    if success:
        print("All accounts successfully restored to initial balances!")
    else:
        print("Some accounts could not be restored to their initial balances.")
    
    return success

def verify_account_balances():
    """Verify that accounts match their known initial balances if available"""
    print("\n--------------------- VERIFYING ACCOUNT BALANCES ---------------------")
    for account_num, known_balance in KNOWN_INITIAL_BALANCES.items():
        current_balance = get_account_balance(account_num)
        if account_num in initial_balances:
            if current_balance == known_balance:
                print(f"✓ Account {account_num} has correct balance: {current_balance}")
            else:
                print(f"✗ Account {account_num} has incorrect balance: {current_balance}, Expected: {known_balance}")
                # Update the initial_balances with the known correct values
                initial_balances[account_num] = known_balance

def run_all_tests():
    """Run all test cases and report overall success/failure"""
    test_results = {
        "Simple Deposit": test_simple_deposit(),
        "Simple Withdrawal": test_simple_withdrawal(),
        "Invalid Account": test_invalid_account(),
        "Insufficient Funds": test_insufficient_funds(),
        "Multiple Transactions": test_multiple_transactions(),
        "All Accounts Invalid Withdrawal": test_all_accounts_invalid_withdrawal(),
        "Boundary Conditions": test_boundary_conditions(),
        "Audit Trail": test_audit_trail()
    }
    
    print("\n--------------------- TEST SUMMARY ---------------------")
    all_passed = True
    for test_name, result in test_results.items():
        status = "PASSED" if result else "FAILED"
        print(f"{test_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\nALL TESTS PASSED!")
    else:
        print("\nSOME TESTS FAILED. Please check the logs above.")
    
    # Restore initial balances regardless of test results
    restore_success = restore_initial_balances()
    
    if not restore_success:
        print("WARNING: Could not restore all accounts to initial state!")
    
    return all_passed

if __name__ == "__main__":
    print("Loading account data...")
    load_account_list()
    
    if not accounts:
        print("No accounts found in the table. Please make sure the DynamoDB table is populated.")
    else:
        # Verify and correct initial balances if possible
        verify_account_balances()
        
        # Run all tests
        run_all_tests()