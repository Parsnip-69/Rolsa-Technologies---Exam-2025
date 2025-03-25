from flask import Flask, render_template
import sqlite3 

app = Flask(__name__)
app.secret_key = "password"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login")
def login():
    return render_template("login.html")



if __name__ == "__main__":
    app.run(debug=True)