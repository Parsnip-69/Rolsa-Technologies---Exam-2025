from flask import Flask, render_template, session, redirect
import get as Get
import post as Post

app = Flask(__name__)
app.secret_key = "secret_secret_key" 

#Page Routing
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/charger_map")
def charger():
    return render_template("chargermap.html")

@app.route("/commercial")
def commercial():
    ThreeProducts = Get.RetrieveProducts()
    return render_template("commercial.html", ThreeProducts = ThreeProducts)

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
    accountType = session.get('type', None)
    account = session.get('account', None)
    if account != None and accountType == 1 or accountType == 2:
        AccountInformation, BookingsInformation = Get.RetrieveInfo(account, "Account")
        ReportViewing = Get.ReportsToCheck(account)
        if AccountInformation['Address'] is None:
            return redirect("/change_account_details")
        return render_template("account.html", AccountInformation = AccountInformation, BookingsInformation = BookingsInformation, ReportViewing = ReportViewing)
    elif account != None and accountType == 3:
        return redirect("/admin")
    else:
        return redirect("/login")
    
@app.route("/admin")
def admin():
    staff = session.get('type', None)
    account = session.get('account', None)
    if staff == 3:
        AccountInformation = Get.RetrieveAdmins(account)
        UnassignedWork = Get.UnassignedJobs()
        UpcomingWork = Get.UpcomingJobs(account)
        return render_template("admin.html", AccountInformation = AccountInformation, UnassignedWork = UnassignedWork, UpcomingWork = UpcomingWork)
    else:
        return redirect("/account")

    

@app.route("/book_consult")
def consultation():
    if session.get('account', None) == None:
        return redirect("/login")
    
    return render_template("consultation.html")


@app.route("/create_admin")
def CreateAdmin():
    if session.get('type', None) == 3:
        Offices = Get.RetrieveOffice()
        return render_template("addadmin.html", Offices = Offices)
    else:
        return redirect("/account")
    
@app.route("/write_report<BookingID>")
def WriteReport(BookingID):
    if session.get('type', None) == 3:
        Products = Get.AllProducts()
        ReportClientInfo = Get.ReportClientInfo(BookingID)
        return render_template("writereport.html", Products = Products, ReportClientInfo = ReportClientInfo, BookingID = BookingID)
    else:
        return redirect("/account")
    
@app.route("/From_Booking<BookingID>")
def FromBooking(BookingID):
    account = session.get('account', None)
    if session.get('account', None) == None:
        return redirect("/login")
    if session.get('type', None) in [1, 2]:
        ReportID = Get.RetrieveReportID(account, BookingID)
        return redirect("/view_report" + str(ReportID))


@app.route("/view_report<ReportID>")
def ViewReport(ReportID):
    if session.get('type', None) == 1:
        account = session.get('account', None)
        ConsultationInfo, ReportDetails, ProductInfo, Invoice = Get.RetrievingReportInfo(ReportID, account, "View")
        return render_template("viewreport.html", ConsultationInfo = ConsultationInfo, ReportDetails = ReportDetails, ProductInfo = ProductInfo, Invoice = Invoice)
    else:
        return redirect("/account")
    

@app.route("/book_report<ReportID>")
def BookReport(ReportID):
    account = session.get('account', None)
    if session.get('account', None) == None:
        return redirect("/login")
    
    if session.get('type', None) in [1, 2]:
        BookingInfo = Get.RetrievingReportInfo(ReportID, account, "Book")
        return render_template("bookreport.html", ReportID = ReportID, BookingInfo = BookingInfo)
        
    else:
        return redirect("/account")
    
@app.route("/change_account_details")
def ChangeAccountDetails():
    account = session.get('account', None)
    if session.get('account', None) == None:
        return redirect("/login")
    
    AccountInformation = Get.RetrieveInfo(account, "Change")
    
    return render_template("change.html", AccountInformation = AccountInformation)

#Post Routing
#General Post Routing
@app.route("/AddAccount", methods=["GET","POST"])
def AddAccount():
    return Post.AddAccount()

@app.route("/CheckAccount", methods=["GET","POST"])
def CheckAccount():
    return Post.CheckAccount()

#Personal/Business Post Routing
@app.route("/ReserveConsultation", methods=["GET","POST"])
def ReserveConsultation():
    if session.get('account', None) == None:
        return redirect("/login")
    
    return Post.ReserveConsultation()

@app.route("/BookReportSlot<ReportID>", methods=["GET","POST"])
def BookReportSlot(ReportID):
    if session.get('account', None) == None:
        return redirect("/login")
    
    if session.get('type', None) in [1, 2]:
        return Post.BookReportSlot(ReportID)
    else:
        return redirect("/account")

@app.route("/DoNotContinue<ReportID>", methods=["GET","POST"])
def DoNotContinue(ReportID):
    if session.get('type', None) in [1, 2]:
        return Post.DoNotContinue(ReportID)
    else:
        return redirect("/account")
    
@app.route("/CancelBooking<BookingID>", methods=["GET","POST"])
def CancelBooking(BookingID):
    if session.get('type', None) in [1, 2]:
        return Post.CancelBooking(BookingID)
    else:
        return redirect("/account")
    
@app.route("/ChangeAccountInfo", methods=["GET","POST"])
def ChangeAccountInfo():
    if session.get('account', None) == None:
        return redirect("/login")
    
    if session.get('type', None) in [1, 2]:
        return Post.ChangeAccountInfo()

#Admin Only Post Routing
@app.route("/AddAdmin", methods=["GET","POST"])
def AddAdmin():
    if session.get('type', None) == 3:
        return Post.AddAdmin()
    else:
        return redirect("/account")

@app.route("/AssigningConsultation", methods=["GET","POST"])
def AssigningConsultation():
    if session.get('type', None) == 3:
        return Post.AssigningConsultation()
    else:
        return redirect("/account")

@app.route("/UnassignConsultation<BookingID>", methods=["GET","POST"])
def UnassignConsultation(BookingID):
    if session.get('type', None) == 3:
        return Post.UnassignConsultation(BookingID)
    else:
        return redirect("/account")
    
@app.route("/SaveReport<BookingID>", methods=["GET","POST"])
def SaveReport(BookingID):
    if session.get('type', None) == 3:  
        return Post.SaveReport(BookingID)
    else:
        return redirect("/account")

#Other
@app.route("/logout")
def logout():
    session.pop('account', None)
    session.pop('type', None)
    return redirect("/")

@app.route("/error")
def error():
    return render_template("error.html")

@app.context_processor
def inject_global_data():
    return {
        "account": session.get('account', None), #email address is considered as account
        "type": session.get('type', None) #type is considered as account type (Personal, Business, Admin)
    }

if __name__ == "__main__":
    app.run(debug=True)