from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
DB_NAME = 'loans.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                income INTEGER NOT NULL,
                credit_score INTEGER NOT NULL,
                loan_amount INTEGER NOT NULL, 
                status TEXT NOT NULL,
                reason TEXT NOT NULL
            )
        ''')
    print("Database initialized.")

def evaluate_application(age, income, credit_score, loan_amount): 

    if credit_score >= 660 and age >= 20 and income >= 30000 and loan_amount <= 5 * income:
        return "Approved", "Meets all criteria"
    else:
        reasons = []
        if age < 20:
            reasons.append("Applicant is underage")
        if credit_score < 660:
            reasons.append("Low credit score")
        if income < 30000:
            reasons.append("Insufficient income")
        if loan_amount > 5 * income:
            reasons.append("Loan amount too high")
        return "Rejected", "; ".join(reasons)


@app.route('/')
def home():
    return redirect(url_for('list_applications'))


@app.route('/add', methods=['GET', 'POST'])
def add_application():

    if request.method == 'POST':
        name = request.form['name']
        age = int(request.form['age'])
        income = int(request.form['income'])
        credit_score = int(request.form['credit_score'])
        loan_amount = int(request.form['loan_amount'])

        status, reason = evaluate_application(age, income, credit_score, loan_amount)

        with sqlite3.connect(DB_NAME) as conn:
            conn.execute('''
                INSERT INTO applications (name,age, income, credit_score, loan_amount, status, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, age, income, credit_score, loan_amount, status, reason))

        return redirect(url_for('list_applications'))

    return render_template('add.html')


@app.route('/applications')
def list_applications():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute('SELECT * FROM applications')
        apps = cursor.fetchall()
    return render_template('list.html', apps=apps)


@app.route('/edit/<int:app_id>', methods=['GET', 'POST'])
def edit_application(app_id):
    with sqlite3.connect(DB_NAME) as conn:
        if request.method == 'POST':
            name = request.form['name']
            age = int(request.form['age'])
            income = int(request.form['income'])
            credit_score = int(request.form['credit_score'])
            loan_amount = int(request.form['loan_amount'])

            status, reason = evaluate_application(age, income, credit_score, loan_amount)

            conn.execute('''
                UPDATE applications SET name=?, age=?, income=?, credit_score=?, loan_amount=?, status=?, reason=?
                WHERE id=?
            ''', (name, age, income, credit_score, loan_amount, status, reason, app_id))

            return redirect(url_for('list_applications'))
        
        cursor=conn.execute('SELECT * FROM applications WHERE id=?', (app_id,))
        app_data = cursor.fetchone()

    return render_template('edit.html', app=app_data)


@app.route('/delete/<int:app_id>')
def delete_application(app_id):
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('DELETE FROM applications WHERE id=?', (app_id,))
    return redirect(url_for('list_applications'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)