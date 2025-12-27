"""Test Form 4 XML parsing logic"""
import xml.etree.ElementTree as ET
from datetime import datetime

# Load sample XML
with open('docs/sample_form4.xml', 'r') as f:
    xml_content = f.read()

print("Testing Form 4 XML Parser")
print("=" * 60)

# Parse XML
root = ET.fromstring(xml_content)

# Extract transactions
transactions_found = 0
for transaction in root.findall('.//nonDerivativeTransaction'):
    # Extract transaction date
    trans_date_elem = transaction.find('.//transactionDate/value')
    if trans_date_elem is None or not trans_date_elem.text:
        continue
    
    transaction_date = datetime.strptime(trans_date_elem.text, '%Y-%m-%d').date()
    
    # Extract shares
    shares_elem = transaction.find('.//transactionShares/value')
    if shares_elem is None or not shares_elem.text:
        continue
    
    shares_traded = abs(int(float(shares_elem.text)))
    
    if shares_traded == 0:
        continue
    
    # Extract transaction code
    code_elem = transaction.find('.//transactionCode')
    transaction_code = code_elem.text if code_elem is not None and code_elem.text else 'P'
    
    # Extract acquired/disposed code
    acquired_disposed_elem = transaction.find('.//transactionAcquiredDisposedCode/value')
    acquired_disposed = acquired_disposed_elem.text if acquired_disposed_elem is not None and acquired_disposed_elem.text else 'A'
    
    # Determine buy/sell
    if transaction_code in ['P', 'A', 'M']:
        transaction_type = 'buy'
    elif transaction_code in ['S', 'D', 'F', 'G']:
        transaction_type = 'sell'
    else:
        transaction_type = 'buy' if acquired_disposed == 'A' else 'sell'
    
    print(f"\nTransaction #{transactions_found + 1}:")
    print(f"  Date: {transaction_date}")
    print(f"  Shares: {shares_traded:,}")
    print(f"  Code: {transaction_code}")
    print(f"  Acquired/Disposed: {acquired_disposed}")
    print(f"  Type: {transaction_type}")
    
    transactions_found += 1

print(f"\n{'=' * 60}")
print(f"✅ Total transactions found: {transactions_found}")
print(f"✅ Parser test PASSED!" if transactions_found > 0 else "❌ Parser test FAILED!")
