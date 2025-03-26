from flask import Flask, render_template, request, session, redirect
import sqlite3 
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "password"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/AddAccount", methods=["GET","POST"])
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

@app.route("/CheckAccount", methods=["GET","POST"])
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
                session['account'] = account
                return redirect("/")
                
            else:
                message = "The email or password is not correct. Please try again."
                return render_template("login.html", message=message)
                
        else:
            message = "The email or password is not correct. Please try again."
            return render_template("login.html", message=message)
        
    return render_template("login.html", message=message)




if __name__ == "__main__":
    app.run(debug=True)