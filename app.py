from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "loansphere_secret"

loans = []


# -------- DATABASE SETUP -------- #

def create_table():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()

create_table()


# -------- LOGIN -------- #

@app.route('/', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
        user = cursor.fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "Invalid username or password"

    return render_template("login.html")


# -------- SIGNUP -------- #

@app.route('/signup', methods=['GET','POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "User already exists"

        cursor.execute("INSERT INTO users VALUES (?,?)",(username,password))

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("signup.html")


# -------- DASHBOARD -------- #

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    user_loans = [l for l in loans if l["user"] == session.get("user")]

    total_loans = len(user_loans)
    low_risk = len([l for l in user_loans if l["risk"] == "Low Risk"])
    medium_risk = len([l for l in user_loans if l["risk"] == "Medium Risk"])
    high_risk = len([l for l in user_loans if l["risk"] == "High Risk"])

    return render_template(
        "dashboard.html",
        loans=user_loans,
        total_loans=total_loans,
        low_risk=low_risk,
        medium_risk=medium_risk,
        high_risk=high_risk
    )


# -------- LOAN EVALUATION -------- #

@app.route('/loan', methods=['GET','POST'])
def loan():

    if 'user' not in session:
        return redirect('/')

    if request.method == 'POST':

        name = request.form['name']
        loan_type = request.form['loan_type']
        credit_score = int(request.form['credit_score'])
        income = float(request.form['income'])
        loan_amount = float(request.form['loan_amount'])
        tenure = int(request.form['tenure'])

        if loan_type == "Housing Loan":
            rate = 0.08/12
        else:
            rate = 0.12/12

        emi = (loan_amount * rate * (1+rate)**tenure)/((1+rate)**tenure-1)

        if credit_score >= 750:
            risk = "Low Risk"
            decision = "Approved"
        elif credit_score >= 650:
            risk = "Medium Risk"
            decision = "Review"
        else:
            risk = "High Risk"
            decision = "Rejected"

        loans.append({
            "user": session.get("user"),
            "name": name,
            "credit_score": credit_score,
            "risk": risk,
            "emi": round(emi,2),
            "decision": decision
        })

        return render_template(
            "result.html",
            name=name,
            risk=risk,
            decision=decision,
            emi=round(emi,2),
            credit_score=credit_score
        )

    return render_template("loan_form.html")


# -------- LOGOUT -------- #

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)