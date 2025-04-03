from database_handler import Database

# Initialize database handler
db = Database("BankingDatabase.db")

# Define test data
acc_id = "9999999999"           # 10-digit unique ID
usr_id = "1234567890"           # Make sure this user ID exists in your User table
acc_name = "Test Account"
acc_balance = 100.50

# Call the create_account method
try:
    success = db.create_account(acc_id, usr_id, acc_name, acc_balance)
    if success:
        print("✅ Account created successfully!")
    else:
        print(" Account creation failed.")
except Exception as e:
    print(" Error:", e)