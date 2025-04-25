from flask import Flask, render_template, session, redirect, request
import get as Get
import post as Post

app = Flask(__name__)
app.secret_key = "secret_secret_key" 

items = []  
times = 0 
total = 0

#Routing to all the pages
@app.context_processor
def inject_global_data():
    return {
        "account": session.get('account', None), #email address is considered as account
        "type": session.get('type', None) #type is considered as account type (Personal, Business, Admin)
    }

# Page 404 Handler

@app.errorhandler(404)
def not_found(e):
    return render_template("error.html"), 404

#Page Routing
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/charger_map")
def charger():
    return render_template("chargermap.html")

@app.route("/t&c")
def terms():
    return render_template("terms.html")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


@app.route("/commercial")
def commercial():
    ThreeProducts = Get.RetrieveProducts()
    return render_template("commercial.html", ThreeProducts = ThreeProducts)

@app.route("/residential")
def residential():
    ThreeProducts = Get.RetrieveProducts()
    return render_template("residential.html", ThreeProducts = ThreeProducts)

@app.route("/product_<productID>")
def product(productID):
    ProductInfo = Get.RetrieveProductInfo(productID)
    return render_template("product.html", ProductInfo = ProductInfo)

@app.route("/carbon", methods=["GET", "POST"])
def carbon():
    if request.method == "POST" and request.form.get("miles") and request.form.get("energy"):
        miles = request.form.get("miles")
        energy = request.form.get("energy")
        Car = Get.RetrieveVehicleEmissions(miles)
        Electrity = Get.RetrieveElectrityEmissions(energy)
        if Car is not None or Electrity is not None:
            
            if Electrity == "API request limit reached. Please try again later." or Car == "API request limit reached. Please try again later.":
                return render_template("carbon.html", Emission = "API request limit reached. Please try again later.")
            else:
                Emission = Car + Electrity
                return render_template("carbon.html", Car=round(Car, 2), Electrity=round(Electrity, 2), Emission=round(Emission, 2))
        else:
            return render_template("carbon.html")
            
    return render_template("carbon.html")

@app.route("/energy")
def energy():
    account = session.get('account', None) 
    Carbon = Get.RetrieveElectrityEmissions(total)
    
    if account != None:
        SavedEnergy = Get.SavedEnergy(account)
        return render_template("energy.html", items = items, total = round(total,3), Carbon = Carbon, SavedEnergy = SavedEnergy)
    else:
        return render_template("energy.html", items = items, total = round(total, 3), Carbon = Carbon)
    

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
    
@app.route("/view_saved_energy<EnergyID>")
def ViewSavedEnergy(EnergyID):
    if session.get('account', None) == None:
        return redirect("/login")
    account = session.get('account', None)
    EnergyInfo, EnergyItems = Get.RetrieveEnergyInfo(account, EnergyID)
    if EnergyInfo == None and EnergyItems == None:
        return redirect("/error")

    return render_template("viewenergy.html", EnergyInfo = EnergyInfo, EnergyItems = EnergyItems)

@app.route("/delete_saved_energy<EnergyID>")
def DeleteSavedEnergy(EnergyID):
    if session.get('account', None) == None:
        return redirect("/login")
    
    account = session.get('account', None)
    if session.get('type', None) in [1, 2]:
        Post.DeleteSavedEnergy(account, EnergyID)
        return redirect("/energy")
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

@app.route("/AddItem", methods=["GET","POST"])
def AddItem():
    try:
        global items, times, total
        items, times, total = Post.AddItemEnergy(items, times, total)
    except Exception as e:
        return redirect("/error")
    return redirect("/energy")

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
    
@app.route("/SaveEnergy")
def SaveEnergy():
    if session.get('account', None) == None:
        return redirect("/login")
    
    if session.get('type', None) in [1, 2]:
        return Post.SaveEnergy(items, total)
    else:
        return redirect("/account")

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

@app.route('/reset')
def reset():
    global items, total
    items = []
    total = 0
    return redirect ('/energy')

if __name__ == "__main__":
    app.run(debug=True)