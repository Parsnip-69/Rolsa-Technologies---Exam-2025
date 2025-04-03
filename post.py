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
                cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (email,))
                accountID = cursor.fetchone()
                cursor.execute("INSERT INTO Business(AccountID, BusinessName) VALUES (?, ?)", (accountID[0], name))
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
        selected_date = datetime.strptime(date, '%Y-%m-%d')
        if selected_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            message = "Please select a weekday (Monday to Friday)"
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

def SaveReport(BookingID):
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

        cursor.execute("SELECT ReportID FROM Report WHERE StaffID = ? AND Description = ? AND LabourHours = ? AND BookingTypeID = ?", (StaffID[0], description, estimatedhours, TypeID[0]))
        ReportID = cursor.fetchone()


        cursor.execute("UPDATE BookingReport SET ReportID = ? WHERE ConsultationID = ?", (ReportID[0], BookingID))
        con.commit()


        for counter, quantity in enumerate(quantities):
            if quantity and quantity.strip().isdigit():
                quantity = int(quantity)
                if quantity > 0:
                    cursor.execute("INSERT INTO ReportProducts (ProductID, ReportID, Quantity) VALUES (?, ?, ?)", (AllProducts[counter][0],ReportID[0] ,quantity))
                    con.commit()

            
                
    con.close()
    return redirect("/admin")


def BookReportSlot(ReportID):
    if session.get('account', None) == None:
            return redirect("/login")
    
    if request.method == "POST":
        start = request.form['start']
        end = request.form['end']
        if start < datetime.now().strftime('%Y-%m-%d'):
            return render_template("bookreport.html", message="Please select a date in the future")
        selected_date = datetime.strptime(start, '%Y-%m-%d')
        if selected_date.weekday() >= 5:
            return render_template("consultation.html", message="Please select a weekday (Monday to Friday)")
        
        start = start + " " + "09:00" 

        CurrentDateTime = datetime.now()
        
        con = sqlite3.connect("RolsaDB.db")
        cursor = con.cursor()
        
        cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (session['account'],))
        AccountID = cursor.fetchone()
       
        cursor.execute("SELECT BookingTypeID FROM Report WHERE ReportID = ?", (ReportID,))
        TypeID = cursor.fetchone()
        
        cursor.execute("INSERT INTO Booking(BookingTypeID, MadeDateTime, ForDateTime, AccountID, EndDate) VALUES (?, ?, ?, ?, ?)", (TypeID[0], CurrentDateTime , start, AccountID[0], end))
        con.commit()
        
        cursor.execute("SELECT BookingID FROM Booking WHERE AccountID = ? AND ForDateTime = ? AND EndDate = ?", (AccountID[0], start, end))
        BookingID = cursor.fetchone()

        cursor.execute("SELECT StaffID From Report WHERE ReportID = ?", (ReportID[0],))
        StaffID = cursor.fetchone()
        
        cursor.execute("UPDATE BookingReport SET FollowUpID = ? WHERE ReportID = ?", (BookingID[0], ReportID))
        con.commit()
        
        cursor.execute("INSERT INTO StaffSchedule(BookingID, StaffID) VALUES (?, ?)", (BookingID[0], StaffID[0]))
        con.commit()
        
        con.close()
        return redirect("/account")

def DoNotContinue(ReportID): 
    CurrentDateTime = datetime.now()

    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()

    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (session['account'],))
    AccountID = cursor.fetchone()

    cursor.execute("SELECT Booking.BookingID FROM BookingReport JOIN Booking ON BookingReport.ConsultationID = Booking.BookingID WHERE ReportID = ? AND AccountID = ?", (ReportID, AccountID[0]))
    CheckValidAccount = cursor.fetchone()

    if CheckValidAccount == None:
        return redirect("/account")
    
    cursor.execute("SELECT BookingTypeID FROM BookingType WHERE Title = 'Not Continuing'")
    TypeID = cursor.fetchone()

    cursor.execute("INSERT INTO Booking(BookingTypeID, MadeDateTime, ForDateTime, AccountID) VALUES (?, ?, ?, ?)", (TypeID[0], CurrentDateTime , CurrentDateTime, AccountID[0]))
    con.commit()

    cursor.execute("SELECT BookingID FROM Booking WHERE AccountID = ? AND ForDateTime = ?", (AccountID[0], CurrentDateTime))
    BookingID = cursor.fetchone()


    cursor.execute("UPDATE BookingReport SET FollowUpID = ? WHERE ReportID = ?", (BookingID[0], ReportID))
    con.commit()
    con.close()

    return redirect("/account")


def ChangeAccountInfo():
    message = None
    email = session['account'] 
    if request.method == 'POST':
        type = request.form['type']
        address = request.form['address']
        postcode = request.form['postcode']
        if type == "Business":
            phone = request.form['phone']
        elif type == "Personal":
            date = request.form['date']

        con = sqlite3.connect("RolsaDB.db")
        cursor = con.cursor()
        cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (email,))
        AccountID = cursor.fetchone()
        if type == "Business":
            cursor.execute("UPDATE Business SET Address = ?, Postcode = ?, PhoneNumber = ? WHERE AccountID = ?", (address, postcode, phone, AccountID[0]))
            con.commit()
        elif type == "Personal":
            cursor.execute("UPDATE Personal SET Address = ?, Postcode = ?, DateOfBirth = ? WHERE AccountID = ?", (address, postcode, date, AccountID[0]))
            con.commit()
        con.close()
        return redirect("/account")
    return render_template("change.html", message=message)


def CancelBooking(BookingID):
    account = session['account']
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()

    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (account,))
    AccountID = cursor.fetchone()
    
    cursor.execute("SELECT BookingID FROM Booking WHERE BookingID = ? AND AccountID = ?", (BookingID, AccountID[0]))
    CheckValidAccount = cursor.fetchone()

    if CheckValidAccount == None:
        return redirect("/account")

    cursor.execute("SELECT BookingTypeID FROM BookingType WHERE Title = 'Not Continuing'")
    TypeID = cursor.fetchone()
    cursor.execute("UPDATE Booking SET BookingTypeID = ? WHERE BookingID = ?", (TypeID[0], BookingID))
    con.commit()
    con.close()
    return redirect("/account")


