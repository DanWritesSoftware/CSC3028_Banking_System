from flask import Flask, render_template, request, redirect
from TempAccountHolder import *
app = Flask(__name__)

holder = AccountHolder() # global account holder for testing

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html',accountList=holder.contents)

@app.route('/new', methods = ['POST', 'GET'])
def new():
    if request.method == 'GET':
        return render_template('newAccount.html')
    if request.method == 'POST':
        accountName = request.form['accountName']
        accountValue = request.form['value']
        holder.addAccount(accountName,accountValue)
        return redirect('/home')

if __name__ == "__main__":
    app.run()