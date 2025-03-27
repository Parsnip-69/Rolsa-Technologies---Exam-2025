from flask import render_template, request, session, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime



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
                session['type'] = account[3]
                return redirect("/account")
                
            else:
                message = "The email or password is not correct. Please try again."
                return render_template("login.html", message=message)
                
        else:
            message = "The email or password is not correct. Please try again."
            return render_template("login.html", message=message)
        
    return render_template("login.html", message=message)


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

def AddAdmin():
    message = None
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        retype = request.form['retype']
        role = request.form['role']
        ext = request.form['ext']
        office = request.form['office']
        if password == retype:
            con = sqlite3.connect("RolsaDB.db")
            cursor = con.cursor()
            cursor.execute("SELECT * FROM Account WHERE Email = ?", (email,))
            account = cursor.fetchone()
            if account:
                message = "Email already exists"
                return render_template("addadmin.html", message=message)
            cursor.execute("INSERT INTO Account (Email, Password, AccountTypeID) VALUES (?, ?, ?)", (email, generate_password_hash(password), 3))
            con.commit()
            cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (email,))
            accountID = cursor.fetchone()
            cursor.execute("INSERT INTO Staff (AccountID, FullName, Role, OfficeID, PhoneExt) VALUES (?, ?, ?, ?, ?)", (accountID[0], name, role, office, ext))
            con.commit()
            con.close()
            return redirect("/admin")
        else:
            message = "Passwords do not match"
            return render_template("addadmin.html", message=message)