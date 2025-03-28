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
    formatted_now = now.strftime('%Y-%m-%d')
    if request.method == "POST":
        date = request.form['date']
        if date < formatted_now:
            message = "Please select a date in the future"
            return render_template("consultation.html", message=message)
        time = request.form['time']
        ForDateTime = date + " " + time
        con = sqlite3.connect("RolsaDB.db")
        cursor = con.cursor()
        cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (session.get('account', None),))
        AccountID = cursor.fetchone()
        cursor.execute("INSERT INTO Booking (BookingTypeID, MadeDateTime, ForDateTime, AccountID, PaymentStatusID, PaymentReference) VALUES (?, ?, ?, ?, ?, ?)", (1, now, ForDateTime, AccountID[0], 1, "None"))
        con.commit()
        cursor.execute("SELECT BookingID FROM Booking WHERE AccountID = ? AND ForDateTime = ?", (AccountID[0], ForDateTime))
        BookingID = cursor.fetchone()
        cursor.execute("INSERT INTO StaffSchedule(BookingID, StaffID) VALUES (?, ?)", (BookingID[0], None))
        con.commit()
        cursor.execute("INSERT INTO BookingReport(ReportID, ConsultationID, FollowUpID) VALUES (?, ? ,?)", (None ,BookingID[0], None))
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
        

def AssigningConsultation():
    message = None
    email = session['account'] 
    if request.method == 'POST':
        BookingID = request.form['BookingID']
        con = sqlite3.connect("RolsaDB.db")
        cursor = con.cursor()
        cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (email,))
        AccountID = cursor.fetchone()
        cursor.execute("SELECT StaffID FROM Staff WHERE AccountID = ?", (AccountID[0],))
        StaffID = cursor.fetchone()
        cursor.execute("UPDATE StaffSchedule SET StaffID = ? WHERE BookingID = ?", (StaffID[0], BookingID))
        con.commit()
        con.close()
        return redirect("/admin")
    
def UnassignConsultation(BookingID):
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("UPDATE StaffSchedule SET StaffID = NULL WHERE BookingID = ?", (BookingID,))
    con.commit()
    con.close()
    return redirect("/admin")

def SaveReport(ReportID):
    message = None
    counter = 0  
    email = session['account'] 
    quantities = []
    counter=0
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT ProductID, Title FROM Products")
    AllProducts = cursor.fetchall()

    if request.method == "POST":
        description = request.form['description']
        type = request.form['type']
        estimatedhours = request.form['estimatedhours']
        for product in AllProducts:
            quantities.append(request.form[str(product[0])])
            counter+=1

        cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (email,))
        AccountID = cursor.fetchone()
  
        cursor.execute("SELECT StaffID FROM Staff WHERE AccountID = ?", (AccountID[0],))
        StaffID = cursor.fetchone()
   
        cursor.execute("SELECT BookingTypeID FROM BookingType WHERE Title = ?", (type,))
        TypeID = cursor.fetchone()
  
        cursor.execute("INSERT INTO Report(StaffID, Description, LabourHours, BookingTypeID ) VALUES (?, ?, ?, ?)", (StaffID[0], description, estimatedhours, TypeID[0]))
        con.commit()

        for counter, quantity in enumerate(quantities):
            quantity = int(quantity)
            if quantity != 0:
                cursor.execute("INSERT INTO ReportProducts (ProductID, ReportID, Quantity) VALUES (?, ?, ?)", (AllProducts[counter][0],ReportID ,quantity))
                con.commit()
                con.close()

    return redirect("/admin")