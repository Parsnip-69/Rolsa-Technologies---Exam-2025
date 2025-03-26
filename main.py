from flask import Flask, render_template, request, session, redirect
import sqlite3 
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
from datetime import datetime

import retrieve

app = Flask(__name__)
app.secret_key = "password"

#Page Routing
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    account = session.get('account', None)
    if account == None:
        return render_template("login.html")
    else:
        return redirect("/account")


@app.route("/register")
def register():
    account = session.get('account', None)
    if account == None:
        return render_template("register.html")
    else:
        return redirect("/account")

@app.route("/account")
def account():
    account = session.get('account', None)
    if account != None:
        AccountInfomation, BookingsInformation = retrieve.RetrieveInfo(account)
        print(AccountInfomation, BookingsInformation)
        return render_template("account.html", AccountInfomation = AccountInfomation, BookingsInformation = BookingsInformation)
    else:
        return redirect("/login")
    

@app.route("/bookConsult")
def consultation():
    if session.get('account', None) == None:
        return redirect("/login")
    
    return render_template("consultation.html")






@app.route("/AddAccount", methods=["GET","POST"])
def AddAccount():
    message = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        retype = request.form['retype']
        business = request.form['business']

        if password == retype:
            con = sqlite3.connect("RolsaDB.db")
            cursor = con.cursor()
            cursor.execute("SELECT * FROM Account WHERE Email = ?", (email,))
            account = cursor.fetchone()
            if account:
                message = "Email already exists"
                return render_template("register.html", message=message)
            if business == "No":
                cursor.execute("INSERT INTO Account (Email, Password, AccountTypeID) VALUES (?, ?, ?)", (email, generate_password_hash(password), 1))
                con.commit()
                cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (email,))
                accountID = cursor.fetchone()
                cursor.execute("INSERT INTO Personal(AccountID, FullName) VALUES (?, ?)", (accountID[0], name))
                con.commit()
                con.close()
                return redirect("/login")  
            elif business == "Yes":
                cursor.execute("INSERT INTO Account (email, password, AccountTypeID) VALUES (?, ?, ?)", (email, generate_password_hash(password), 2))
                con.commit()
                con.close()
                return redirect("/login")
        else:
            message = "Passwords do not match"
            return render_template("register.html", message=message)
        
    return render_template("register.html", message=message)

@app.route("/CheckAccount", methods=["GET","POST"])
def CheckAccount():
    message = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        con = sqlite3.connect("RolsaDB.db")
        cursor = con.cursor()
        cursor.execute("SELECT * FROM Account WHERE Email = ?", (email,))
        account = cursor.fetchone()
        con.close()

        if account:
            if check_password_hash(account[2], password):
                session['account'] = email
                return redirect("/account")
                
            else:
                message = "The email or password is not correct. Please try again."
                return render_template("login.html", message=message)
                
        else:
            message = "The email or password is not correct. Please try again."
            return render_template("login.html", message=message)
        
    return render_template("login.html", message=message)

@app.route("/ReserveConsultation", methods=["GET","POST"])
def ReserveConsultation():
    message = None
    now = datetime.now()
    if request.method == "POST":
        date = request.form['date']
        time = request.form['time']
        ForDateTime = date + " " + time
        con = sqlite3.connect("RolsaDB.db")
        cursor = con.cursor()
        cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (session.get('account', None),))
        AccountID = cursor.fetchone()
        cursor.execute("INSERT INTO Booking (BookingTypeID, MadeDateTime, ForDateTime, AccountID, PaymentStatusID, PaymentReference) VALUES (?, ?, ?, ?, ?, ?)", (1, now, ForDateTime, AccountID[0], 1, "None"))
        con.commit()
        con.close()
        return redirect("/account")
    return render_template("consultation.html", message=message)


#Other
@app.route("/logout")
def logout():
    session.pop('account', None)
    return redirect("/")

@app.context_processor
def inject_global_data():
    return {
        "account": session.get('account', None)
    }

if __name__ == "__main__":
    app.run(debug=True)