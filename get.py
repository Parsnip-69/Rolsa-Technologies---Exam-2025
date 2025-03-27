import sqlite3
from datetime import datetime

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

