from flask import Flask, render_template, request, redirect
import mysql.connector
import time

app = Flask(__name__)

def get_db():
    while True:
        try:
            db = mysql.connector.connect(
                host="db",
                user="root",
                password="root123",
                database="spendsmart"
            )
            return db
        except:
            print("Waiting for MySQL...")
            time.sleep(3)

@app.route('/', methods=['GET', 'POST'])
def home():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        amount = request.form.get('amount')
        category = request.form.get('category')
        cursor.execute("INSERT INTO expenses (amount, category) VALUES (%s, %s)", (amount, category))
        db.commit()
        db.close()
        return redirect('/')
    cursor.execute("SELECT id, amount, category, date FROM expenses ORDER BY date DESC")
    expenses = cursor.fetchall()
    cursor.execute("SELECT category, SUM(amount) as total FROM expenses GROUP BY category")
    rows = cursor.fetchall()
    category_total = {row['category']: float(row['total']) for row in rows}
    total = sum(category_total.values())
    db.close()
    return render_template('index.html', expenses=expenses, category_total=category_total, total=total)

@app.route('/delete/<int:id>')
def delete(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM expenses WHERE id=%s", (id,))
    db.commit()
    db.close()
    return redirect('/')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        amount = request.form.get('amount')
        category = request.form.get('category')
        cursor.execute("UPDATE expenses SET amount=%s, category=%s WHERE id=%s", (amount, category, id))
        db.commit()
        db.close()
        return redirect('/')
    cursor.execute("SELECT * FROM expenses WHERE id=%s", (id,))
    expense = cursor.fetchone()
    db.close()
    return render_template('edit.html', expense=expense)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
