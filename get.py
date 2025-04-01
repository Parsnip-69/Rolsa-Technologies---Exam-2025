import sqlite3
from datetime import datetime
from flask import render_template, request, session, redirect

def RetrieveInfo(account):

    AccountInfomation ={}
    BookingsInformation = {}
    counter = 0

    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()

    cursor.execute("SELECT AccountID, Type FROM Account JOIN AccountType ON Account.AccountTypeID = AccountType.AccountTypeID WHERE Email = ?", (account,))
    AccountInfo = cursor.fetchone()

    if AccountInfo[1] == "Business":
        cursor.execute("SELECT * FROM Business WHERE AccountID = ?", (AccountInfo[0],))

    elif AccountInfo[1] == "Personal":
        cursor.execute("SELECT * FROM Personal WHERE AccountID = ?", (AccountInfo[0],))

    AdditionalInfo = cursor.fetchone()

    AccountInfomation = {
        "FullName": AdditionalInfo[1],
        "Email": account,
        "Type": AccountInfo[1],
        "DateofBirth": AdditionalInfo[2],
        "Address": AdditionalInfo[3],
        "Postcode": AdditionalInfo[4],
    }
    
    cursor.execute("SELECT ForDateTime, Title FROM Booking JOIN BookingType ON Booking.BookingTypeID = BookingType.BookingTypeID WHERE AccountID = ? AND ForDateTime >= ?", (AccountInfo[0], datetime.now()))
    FutureBookings = cursor.fetchall()
    con.close()
    
    for booking in FutureBookings:
        Date = booking[0].split(" ")[0]
        Time = booking[0].split(" ")[1]

        BookingsInformation[counter] = {
            "Date": Date,
            "Time": Time,
            "Type": booking[1]
        }

        counter += 1
        
    return AccountInfomation, BookingsInformation


def RetrieveOffice():
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT OfficeID, OfficeName FROM Office")
    Offices = cursor.fetchall()
    con.close()

    return Offices

def RetrieveAdmins(account):
    AccountInfomation = {}
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT FullName, Email, Role, PhoneExt, OfficeName FROM Account JOIN Staff ON Account.AccountID = Staff.AccountID JOIN Office ON Staff.OfficeID = Office.OfficeID WHERE Email = ?", (account,))
    Admin = cursor.fetchone()
    con.close()

    AccountInfomation = {
        'Name': Admin[0],
        'Email': Admin[1],
        'Role': Admin[2],
        'PhoneExt': Admin[3],
        'Office': Admin[4]
    }
    return AccountInfomation

def UpcomingJobs(account):
    UpcomingWork = {}
    counter = 0
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (account,))
    AccountID = cursor.fetchone()
    cursor.execute("SELECT StaffID FROM Staff WHERE AccountID = ?", (AccountID[0],))
    StaffID = cursor.fetchone()
    cursor.execute("SELECT B.BookingID, FullName, ForDateTime, Address, Title FROM StaffSchedule SS JOIN Booking B ON SS.BookingID = B.BookingID JOIN BookingType BT ON B.BookingTypeID = BT.BookingTypeID JOIN Account A ON A.AccountID = B.AccountID JOIN Personal P ON A.AccountID = P.AccountID JOIN BookingReport BR ON B.BookingID = BR.ConsultationID WHERE StaffID = ? AND BR.ReportID IS NULL", (StaffID[0],))
    Upcoming = cursor.fetchall()
    con.close()
    for work in Upcoming:
        Date = work[2].split(" ")[0]
        Time = work[2].split(" ")[1]

        UpcomingWork[counter] = {
            "BookingID": work[0],
            "Name": work[1],
            "Date": Date,
            "Time": Time,
            "Address": work[3],
            "Type": work[4]
        }

        counter += 1

    return UpcomingWork

def UnassignedJobs():
    UnassignedWork = {}
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT SS.BookingID FROM StaffSchedule SS JOIN Booking B ON SS.BookingID = B.BookingID WHERE StaffID IS NULL AND B.BookingTypeID = 1 AND ForDateTime >= ?", (datetime.now(),))
    Unassigned= cursor.fetchall()
    for job in Unassigned:
        cursor.execute("SELECT BookingID, FullName, ForDateTime FROM Booking JOIN Account A ON Booking.AccountID = A.AccountID JOIN Personal P ON A.AccountID = P.AccountID WHERE BookingID = ?", (job[0],))
        JobInfo = cursor.fetchone()

        Date = JobInfo[2].split(" ")[0]
        Time = JobInfo[2].split(" ")[1]

        UnassignedWork[job] = {
            "BookingID": JobInfo[0],
            "Name": JobInfo[1],
            "Date": Date,
            "Time": Time
        }

    con.close()
    return UnassignedWork

def AllProducts():
    Products = {}
    counter = 0
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT ProductID, Title FROM Products")
    AllProducts = cursor.fetchall()
    con.close()

    for product in AllProducts:
        Products[counter] = {
            "ProductID": product[0],
            "Name": product[1],
        }

        counter += 1

    return Products

def OutstandingReport(account):
    Reports = {}
    counter = 0
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (account,))
    AccountID = cursor.fetchone()
    cursor.execute("SELECT StaffID FROM Staff WHERE AccountID = ?", (AccountID[0],))
    StaffID = cursor.fetchone() 
    cursor.execute("SELECT B.BookingID FROM StaffSchedule SS JOIN Booking B ON SS.BookingID = B.BookingID JOIN BookingReport BR ON B.BookingID = BR.ConsultationID WHERE SS.StaffID = ?", (StaffID[0],))
    
    OnTheScheduleOutstanding = cursor.fetchall()


def ReportClientInfo(BookingID):
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT FullName, Address, Postcode, ForDateTime FROM Booking JOIN Account A ON Booking.AccountID = A.AccountID JOIN Personal P ON A.AccountID = P.AccountID WHERE BookingID = ?", (BookingID,))
    ReportClientInfo = cursor.fetchone()
    con.close()
    return ReportClientInfo


def RetrievingReportInfo(ReportID, account):
    ConsultationInfo = {}
    ProductInfo = {}
    TotalProductPrice = 0

    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (account,))
    AccountID = cursor.fetchone()

    cursor.execute("SELECT FullName, ForDateTime FROM Report JOIN Staff S ON Report.StaffID = S.StaffID JOIN BookingReport BR ON Report.ReportID = BR.ReportID JOIN Booking B ON BR.ConsultationID = B.BookingID  WHERE Report.ReportID = ? AND B.AccountID = ?", (ReportID, AccountID[0]))
    ReportInfo = cursor.fetchone()

    if ReportInfo == None:
        return redirect("/account")

    Date = ReportInfo[1].split(" ")[0]
    Time = ReportInfo[1].split(" ")[1]
    
    ConsultationInfo = {
        "Staff": ReportInfo[0],
        "Date": Date,
        "Time": Time
    }

    cursor.execute("SELECT Description, LabourHours, Title FROM Report JOIN BookingType BT ON Report.BookingTypeID = BT.BookingTypeID WHERE ReportID = ?", (ReportID,))
    ReportDetails = cursor.fetchone()

    cursor.execute("SELECT Title, Description, Price, Quantity FROM ReportProducts JOIN Products ON ReportProducts.ProductID = Products.ProductID WHERE ReportID = ?", (ReportID,))
    Products = cursor.fetchall()
    
    counter = 0
    for product in Products:
        ProductInfo[counter] = {
            "Name": product[0],
            "Description": product[1],
            "Price": product[2],
            "Quantity": product[3]
        }

        counter += 1

    for product in Products:
        TotalProductPrice += product[2] * product[3]
    TotalLabourPrice = ReportDetails[1] * 50
    SubTotal = TotalLabourPrice + TotalProductPrice
    VAT = SubTotal * 0.2
    Total = SubTotal + VAT
    Invoice = {
        "Labour": '%.2f' % TotalLabourPrice,
        "Product": '%.2f' % TotalProductPrice,
        "SubTotal": '%.2f' % SubTotal,
        "VAT": '%.2f' % VAT,
        "Total": '%.2f' % Total
    }

    return ConsultationInfo, ReportDetails, ProductInfo, Invoice


    









def ReportsToCheck(account):
    ReportViewing = {}
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT BR.ReportID, ForDateTime, S.FullName FROM BookingReport BR JOIN Report R ON BR.ReportID = R.ReportID JOIN Staff S ON R.StaffID = S.StaffID JOIN Booking B ON BR.ConsultationID = B.BookingID WHERE B.AccountID = (SELECT AccountID FROM Account WHERE Email = ?)", (account,))
    Reports = cursor.fetchall()
    con.close()
    for report in Reports:
        Date = report[1].split(" ")[0]

        ReportViewing[report] = {
            "ReportID": report[0],
            "Date": Date,
            "Staff": report[2]
        }
    
    return ReportViewing



