import sqlite3
from datetime import datetime
from flask import render_template, request, session, redirect

def RetrieveInfo(account):

    AccountInfomation ={}
    BookingsInformation = {}
    times = 0

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

        BookingsInformation[times] = {
            "Date": Date,
            "Time": Time,
            "Type": booking[1]
        }

        times += 1
        
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
    times = 0
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (account,))
    AccountID = cursor.fetchone()
    cursor.execute("SELECT StaffID FROM Staff WHERE AccountID = ?", (AccountID[0],))
    StaffID = cursor.fetchone()
    cursor.execute("SELECT B.BookingID, FullName, ForDateTime, Address, Title FROM StaffSchedule SS JOIN Booking B ON SS.BookingID = B.BookingID JOIN BookingType BT ON B.BookingTypeID = BT.BookingTypeID JOIN Account A ON A.AccountID = B.AccountID JOIN Personal P ON A.AccountID = P.AccountID WHERE StaffID = ?", (StaffID[0],))
    Upcoming = cursor.fetchall()
    con.close()
    for work in Upcoming:
        Date = work[2].split(" ")[0]
        Time = work[2].split(" ")[1]

        UpcomingWork[times] = {
            "BookingID": work[0],
            "Name": work[1],
            "Date": Date,
            "Time": Time,
            "Address": work[3],
            "Type": work[4]
        }

        times += 1

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