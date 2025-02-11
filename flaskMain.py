from flask import Flask, render_template, request, redirect
from TempAccountHolder import *
from DatabaseHandler import Database
app = Flask(__name__)

#holder = AccountHolder() # global account holder for testing
db = Database('BankingDatabase.db') # Database Object

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    accountArray = db.getUserAccounts(1)
    return render_template('home.html',accountList=accountArray) # TODO: Replace with dynamic user ID whith mulit-user implementation

@app.route('/new', methods = ['POST', 'GET'])
def new():
    if request.method == 'GET':
        return render_template('newAccount.html')
    if request.method == 'POST':
        accountName = request.form['accountName']
        accountValue = request.form['value']
        #holder.addAccount(accountName,accountValue)
        db.createAccount(1,accountName,accountValue) # TODO: Replace with dynamic user ID whith mulit-user implementation
        return redirect('/home')

if __name__ == "__main__":
    app.run()