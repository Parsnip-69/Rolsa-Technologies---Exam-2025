import sqlite3
from datetime import datetime
from flask import render_template, request, session, redirect
import math
import random
import requests
import json

def RetrieveInfo(account, FromWho):

    AccountInformation ={}
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

    AccountInformation = {
        "FullName": AdditionalInfo[1],
        "Email": account,
        "Type": AccountInfo[1],
        "Address": AdditionalInfo[3],
        "Postcode": AdditionalInfo[4],
    }

    if AccountInfo[1] == "Business":
        AccountInformation["PhoneNumber"] = AdditionalInfo[2]
    elif AccountInfo[1] == "Personal":
        AccountInformation["DateofBirth"] = AdditionalInfo[2]
    
    cursor.execute("SELECT ForDateTime, Title, BookingID FROM Booking JOIN BookingReport ON Booking.BookingID = BookingReport.ConsultationID JOIN BookingType ON Booking.BookingTypeID = BookingType.BookingTypeID WHERE ReportID IS NULL AND AccountID = ? AND ForDateTime >= ? AND Title != 'Not Continuing'", (AccountInfo[0], datetime.now()))
    FutureConsultation = cursor.fetchall()

    cursor.execute("SELECT ForDateTime, Title, BookingID FROM Booking JOIN BookingReport ON Booking.BookingID = BookingReport.FollowUpID JOIN BookingType ON Booking.BookingTypeID = BookingType.BookingTypeID WHERE AccountID = ? AND ForDateTime >= ? AND Title != 'Not Continuing'", (AccountInfo[0], datetime.now()))
    FutureFollowUp = cursor.fetchall()
    con.close()
    
    for booking in FutureConsultation + FutureFollowUp:
        Date = booking[0].split(" ")[0]
        Time = booking[0].split(" ")[1]

        BookingsInformation[counter] = {
            "BookingID": booking[2],
            "Date": Date,
            "Time": Time,
            "Type": booking[1]
        }

        counter += 1

    
    if FromWho == "Account":
        return AccountInformation, BookingsInformation
    elif FromWho == "Change":
        return AccountInformation    


def RetrieveOffice():
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT OfficeID, OfficeName FROM Office")
    Offices = cursor.fetchall()
    con.close()

    return Offices

def RetrieveAdmins(account):
    AccountInformation = {}
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT FullName, Email, Role, PhoneExt, OfficeName FROM Account JOIN Staff ON Account.AccountID = Staff.AccountID JOIN Office ON Staff.OfficeID = Office.OfficeID WHERE Email = ?", (account,))
    Admin = cursor.fetchone()
    con.close()

    AccountInformation = {
        'Name': Admin[0],
        'Email': Admin[1],
        'Role': Admin[2],
        'PhoneExt': Admin[3],
        'Office': Admin[4]
    }
    return AccountInformation

def UpcomingJobs(account):
    UpcomingWork = {}
    counter = 0
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()

    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (account,))
    AccountID = cursor.fetchone()

    cursor.execute("SELECT StaffID FROM Staff WHERE AccountID = ?", (AccountID[0],))
    StaffID = cursor.fetchone()

    cursor.execute("SELECT B.BookingID, A.AccountID, Type, ForDateTime, Title FROM StaffSchedule SS JOIN Booking B ON SS.BookingID = B.BookingID JOIN BookingType BT ON B.BookingTypeID = BT.BookingTypeID JOIN Account A ON A.AccountID = B.AccountID JOIN AccountType AT ON A.AccountTypeID = AT.AccountTypeID JOIN BookingReport BR ON B.BookingID = BR.ConsultationID WHERE StaffID = ? AND BR.ReportID IS NULL", (StaffID[0],))
    UpcomingConsultation = cursor.fetchall()

    cursor.execute("SELECT B.BookingID, A.AccountID, Type, ForDateTime, Title FROM StaffSchedule SS JOIN Booking B ON SS.BookingID = B.BookingID JOIN BookingType BT ON B.BookingTypeID = BT.BookingTypeID JOIN Account A ON A.AccountID = B.AccountID JOIN AccountType AT ON A.AccountTypeID = AT.AccountTypeID JOIN BookingReport BR ON B.BookingID = BR.FollowUpID WHERE StaffID = ? AND BR.FollowUpID IS NOT NULL", (StaffID[0],))
    UpcomingJobs = cursor.fetchall()

    for work in UpcomingConsultation + UpcomingJobs:
        if work[2] == "Business":
            cursor.execute("SELECT BusinessName, Address, Postcode FROM Business WHERE AccountID = ?", (work[1],))

        elif work[2] == "Personal":
            cursor.execute("SELECT FullName, Address FROM Personal WHERE AccountID = ?", (work[1],))

        AccountInfo = cursor.fetchone()
        
        Date = work[3].split(" ")[0]
        Time = work[3].split(" ")[1]

        UpcomingWork[counter] = {
            "BookingID": work[0],
            "Name": AccountInfo[0],
            "Date": Date,
            "Time": Time,
            "Address": AccountInfo[1],
            "Type": work[4]
        }

        counter += 1

    con.close()
    return UpcomingWork

def UnassignedJobs():
    UnassignedWork = {}
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("SELECT SS.BookingID FROM StaffSchedule SS JOIN Booking B ON SS.BookingID = B.BookingID WHERE StaffID IS NULL AND B.BookingTypeID = 1 AND ForDateTime >= ?", (current_time,))
    Unassigned = cursor.fetchall()
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

def ReportClientInfo(BookingID):
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT FullName, Address, Postcode, ForDateTime FROM Booking JOIN Account A ON Booking.AccountID = A.AccountID JOIN Personal P ON A.AccountID = P.AccountID WHERE BookingID = ?", (BookingID,))
    ReportClientInfo = cursor.fetchone()
    con.close()
    return ReportClientInfo


def RetrievingReportInfo(ReportID, account, Type):
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

    cursor.execute("SELECT Report.ReportID, Description, LabourHours, Title, FollowUpID FROM Report JOIN BookingReport ON Report.ReportID = BookingReport.ReportID JOIN BookingType BT ON Report.BookingTypeID = BT.BookingTypeID WHERE Report.ReportID = ?", (ReportID,))
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
    TotalLabourPrice = ReportDetails[2] * 50
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

    con.close()
    
    DaysRequired = math.ceil(ReportDetails[2]/8)

    BookingInfo = {
        "Description": ReportDetails[1],
        "Type": ReportDetails[3],
        "LabourHours": ReportDetails[2],
        "NumberofDays": DaysRequired,
        "Staff": ConsultationInfo['Staff'],
        "Total": Invoice['Total']
    }


    if Type == "View":
        return ConsultationInfo, ReportDetails, ProductInfo, Invoice
    elif Type == "Book":
        return BookingInfo

def ReportsToCheck(account):
    ReportViewing = {}
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT BR.ReportID, ForDateTime, S.FullName FROM BookingReport BR JOIN Report R ON BR.ReportID = R.ReportID JOIN Staff S ON R.StaffID = S.StaffID JOIN Booking B ON BR.ConsultationID = B.BookingID WHERE FollowUpID IS NULL AND B.AccountID = (SELECT AccountID FROM Account WHERE Email = ?)", (account,))
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


def RetrieveReportID(account, BookingID):
    ReportID = {}
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (account,))
    AccountID = cursor.fetchone()
    cursor.execute("SELECT ReportID FROM BookingReport JOIN Booking ON BookingReport.FollowUpID = Booking.BookingID WHERE FollowUPID = ? AND AccountID = ?", (BookingID, AccountID[0]))
    ReportID = cursor.fetchone()
    con.close()
    if ReportID == None:
        return None
    else:
        return ReportID[0]
    
def RetrieveProducts():
    with sqlite3.connect('RolsaDB.db') as con:
        cur = con.cursor()
        cur.execute('SELECT MAX(ProductID) FROM Products')
        max_product_id = cur.fetchone()[0]

        ThreeProducts = {}
        for i in range(3):
            RandomNumber = random.randrange(1, max_product_id + 1)
            while any(item.get('ProductID') == RandomNumber for item in ThreeProducts.values()):
                RandomNumber = random.randrange(1, max_product_id + 1)

            cur.execute('SELECT Title, Description, Price FROM Products WHERE ProductID = ?', (RandomNumber,))
            product_info = cur.fetchone()
            if product_info:
                ThreeProducts[i] = {
                    'ProductID': RandomNumber,
                    'Title': product_info[0],
                    'Description': product_info[1],
                    'Price': product_info[2]
                }

    return ThreeProducts

def RetrieveProductInfo(productID):
    ProductInfo = {}
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT Title, Description, Price FROM Products WHERE ProductID = ?", (productID,))
    ProductInfo = cursor.fetchone()
    con.close()

    ProductInfo = {
        "ProductID": productID,
        "Title": ProductInfo[0],
        "Description": ProductInfo[1],
        "Price": ProductInfo[2]
    }

    return ProductInfo



def RetrieveElectrityEmissions(total):

    api_key = 'p9uyFp7qj9XKLtsAJtJK7Q'

    url = 'https://www.carboninterface.com/api/v1/estimates'

    data = {
        "type": "electricity",
        "electricity_unit": "kwh",
        "electricity_value": total,
        "country": "gb",
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        Carbon = response_data['data']['attributes']['carbon_kg']
    except (KeyError, ValueError, TypeError) as e:
        Carbon = None

    return Carbon


def RetrieveVehicleEmissions(mileage):

    api_key = 'p9uyFp7qj9XKLtsAJtJK7Q'

    url = 'https://www.carboninterface.com/api/v1/estimates'

    data = {
        "type": "vehicle",
        "distance_unit": "mi",
        "distance_value": mileage,
        "vehicle_model_id": "7268a9b7-17e8-4c8d-acca-57059252afe9"
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

  
    response = requests.post(url, headers=headers, json=data)
 
    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        Carbon = response_data['data']['attributes']['carbon_kg']
    except (KeyError, ValueError, TypeError) as e:
        Carbon = None

    return Carbon
 
def SavedEnergy(account):
    SavedEnergy = {}
    counter = 0


    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (account,))
    AccountID = cursor.fetchone()

    cursor.execute("SELECT * FROM EnergyUsage WHERE AccountID = ?", (AccountID[0],))
    EnergyUsage = cursor.fetchall()
    con.close()

    for energy in EnergyUsage:
        Date = energy[3].split(" ")[0]
        Time = energy[3].split(" ")[1]

        DateTime = Date + " @ " + Time

        SavedEnergy[counter] = {
            "EnergyID": energy[0],
            "Date":  DateTime,
            "Total": energy[1],
        }

        counter += 1
    
    return SavedEnergy

def RetrieveEnergyInfo(account, EnergyID):
    EnergyItems = {}
    counter = 0
    con = sqlite3.connect("RolsaDB.db")
    cursor = con.cursor()
    cursor.execute("SELECT AccountID FROM Account WHERE Email = ?", (account,))
    AccountID = cursor.fetchone()
    
    cursor.execute("SELECT * FROM EnergyUsage WHERE AccountID = ? AND EnergyUsageID = ?", (AccountID[0], EnergyID))
    EnergyInfo = cursor.fetchone()

    if EnergyInfo == None:
        return None, None

    cursor.execute("SELECT * FROM EnergyItem WHERE EnergyUsageID = ?", (EnergyInfo[0],))
    EnergyItems = cursor.fetchall()
    
    for item in EnergyItems:
        RoundedTotal = item[3] * item[4]
        RoundedTotal = round(RoundedTotal, 5)
        EnergyItems[counter] = {
            "Name": item[2],
            "Time": item[3],
            "kWh": item[4],
            "Total": RoundedTotal,
        }
        counter += 1

    con.close()

    return EnergyInfo, EnergyItems






