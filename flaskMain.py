from flask import Flask, render_template, request, redirect, flash
from DatabaseHandler import Database
from input_validator import InputValidator
from UserManagement import UserManager
import random # for account number generation
app = Flask(__name__)

app.config['SECRET_KEY'] = 'idkwhatthisishaha' # TODO: figure out what this is

db = Database('BankingDatabase.db') # Database Object
um = UserManager()
valid = InputValidator()

@app.route('/')
def default():
    return redirect('/home') # TODO: replace with login when user session management is complete

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    # Fetch user accounts (#TODO replace 1 with dynamic user ID)
    accountArray = db.getUserAccounts(1)

    # Initialize a list for error messages
    validationErrors = []

    # Iterate through each account and validate
    for account in accountArray:

        if not valid.validate_account_number(account.accountNumber):
            # Account Error
            validationErrors.append(f"ERROR READING DATA - Account number {account.accountNumber} is invalid.")

        if valid.validate_currency_amount(account.balance) == False:
            # Balance Error
            validationErrors.append(f"ERROR READING DATA - Balance for account {account.accountNumber} is invalid.")

    if validationErrors:
        # Show errors to user
        for error in validationErrors:
            flash(error, 'error')
            print(error)
        # redirect to error page where flashed messages are displayed.
        return render_template('error.html')

    return render_template('home.html',accountList=accountArray) # TODO: Replace with dynamic user ID whith mulit-user implementation

@app.route('/new', methods = ['POST', 'GET'])
def new():
    if request.method == 'GET':
        # Load form
        return render_template('newAccount.html')
    if request.method == 'POST':
        # Get the account name and value from the form
        accountName = request.form['accountName']
        accountValue = request.form['value']

        # Validate Input

        # Initialize a list for error messages
        validationErrors = []

        if not valid.validate_username(accountName):
            # Account name issue
            validationErrors.append(f"ERROR Account Name {accountName} is invalid. Please keep names between 5 and 20 Characters.")

        try:
            if not valid.validate_currency_amount(float(accountValue)):
                # Currency issue
                validationErrors.append(f"ERROR Currency Value {accountValue} is invalid. Please include the decimals after the whole number.")
        except ValueError:
            # Not a number
            validationErrors.append(f"ERROR Please Input Digits.")

        if validationErrors:
            # Flash errors
            for error in validationErrors:
                flash(error, 'error')
                print(error)
            # reload page to reset form and diaplay flashed errors.
            return redirect('/new')

        # Generate a new account number
        randomAccount = random.randint(1000000000, 9999999999)
        # Regenerate if in use
        while db.accountIdInUse(randomAccount):
            randomAccount = random.randint(1000000000, 999999999)

        # Create account in database
        db.createAccount(randomAccount,1,accountName,accountValue) # TODO: Replace with dynamic user ID whith mulit-user implementation
        return redirect('/home')

@app.route('/register', methods = ['POST', 'GET'])
def newUser():
    if request.method == 'GET':
        #Load Form
        return render_template('register.html')
    if request.method == 'POST':
        userName = request.form['userName']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        # Generate Unique User ID
        randomAccount = random.randint(1000000000, 9999999999)
        # Regenerate if in use
        while db.userIdInUse(randomAccount):
            randomAccount = random.randint(1000000000, 999999999)

    message = um.signUp(userName, email, password, confirmPassword, randomAccount)
    flash(message)
    return redirect('/home')
        
@app.route('/transfer', methods = ['POST','GET'])
def transfer():
    if request.method == 'GET':
        return render_template('transfer.html')
    

if __name__ == "__main__":
    app.run()
