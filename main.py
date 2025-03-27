from flask import Flask, render_template, session, redirect



import get
import post as Post

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
    accountType = session.get('type', None)
    account = session.get('account', None)
    if account != None and accountType == 1 or accountType == 2:
        AccountInfomation, BookingsInformation = get.RetrieveInfo(account)
        return render_template("account.html", AccountInfomation = AccountInfomation, BookingsInformation = BookingsInformation)
    elif account != None and accountType == 3:
        return redirect("/admin")
    else:
        return redirect("/login")
    
@app.route("/admin")
def admin():
    staff = session.get('type', None)
    account = session.get('account', None)
    if staff == 3:
        AccountInfomation = get.RetrieveAdmins(account)
        return render_template("admin.html", AccountInfomation = AccountInfomation)
    else:
        return redirect("/account")

    

@app.route("/bookConsult")
def consultation():
    if session.get('account', None) == None:
        return redirect("/login")
    
    return render_template("consultation.html")


@app.route("/CreateAdmin")
def CreateAdmin():
    if session.get('type', None) == 3:
        Offices = get.RetrieveOffice()
        return render_template("addadmin.html", Offices = Offices)
    else:
        return redirect("/account")


#Post Routing
@app.route("/AddAccount", methods=["GET","POST"])
def AddAccount():
    return Post.AddAccount()

@app.route("/CheckAccount", methods=["GET","POST"])
def CheckAccount():
    return Post.CheckAccount()

@app.route("/ReserveConsultation", methods=["GET","POST"])
def ReserveConsultation():
    return Post.ReserveConsultation()

@app.route("/AddAdmin", methods=["GET","POST"])
def AddAdmin():
    return Post.AddAdmin()



#Other
@app.route("/logout")
def logout():
    session.pop('account', None)
    session.pop('type', None)
    return redirect("/")

@app.context_processor
def inject_global_data():
    return {
        "account": session.get('account', None), #email address is considered as account
        "type": session.get('type', None) #staff is considered as staff
    }

if __name__ == "__main__":
    app.run(debug=True)