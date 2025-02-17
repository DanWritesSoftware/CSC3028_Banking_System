The only current dependency is Flask

Accounts can be added to a temporary global object through the '/new' page

Accounts are displayed on the '/home' page


### InputValidator Class
The InputValidator class validates user inputs to ensure data integrity. It includes methods for validating:
- Account numbers (10 digits).
- Currency amounts (positive, up to 2 decimal places).
- Transaction limits (positive, ≤ 10000).
- Passwords (8+ characters, with uppercase, lowercase, digits, and special characters).
- Usernames (alphanumeric, 5-20 characters).
- Emails (standard format).
- Roles (Admin, Teller, Customer).

#### Usage
python
from InputValidator import InputValidator

# Example: Validate an account number
if InputValidator.validate_account_number("1234567890"):
    print("Valid account number")