from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",   # change if your password is different
    database="spendsmart"
)

cursor = db.cursor(dictionary=True)

# HOME ROUTE
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        amount = request.form.get('amount')
        category = request.form.get('category')

        if amount and category:
            cursor.execute(
                "INSERT INTO expenses (amount, category) VALUES (%s, %s)",
                (amount, category)
            )
            db.commit()
            return redirect('/')

    # 👇 THIS IS WHERE YOU PASTE NEW CODE
    filter_category = request.args.get('filter')

    if filter_category:
        cursor.execute(
            "SELECT id, amount, category, date FROM expenses WHERE category LIKE %s ORDER BY date DESC",
            ('%' + filter_category + '%',)
        )
    else:
        cursor.execute(
            "SELECT id, amount, category, date FROM expenses ORDER BY date DESC"
        )

    expenses = cursor.fetchall()

    total = sum(int(exp['amount']) for exp in expenses)
    category_total = {}

    for exp in expenses:
        cat = exp['category']
        category_total[cat] = category_total.get(cat, 0) + int(exp['amount'])

    return render_template('index.html', expenses=expenses, total=total,category_total=category_total)


# DELETE
@app.route('/delete/<int:id>')
def delete(id):
    cursor.execute("DELETE FROM expenses WHERE id = %s", (id,))
    db.commit()
    return redirect('/')


# EDIT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if request.method == 'POST':
        amount = request.form.get('amount')
        category = request.form.get('category')

        cursor.execute(
            "UPDATE expenses SET amount=%s, category=%s WHERE id=%s",
            (amount, category, id)
        )
        db.commit()
        return redirect('/')

    cursor.execute("SELECT * FROM expenses WHERE id=%s", (id,))
    expense = cursor.fetchone()
    return render_template('edit.html', expense=expense)


if __name__ == '__main__':
    app.run(debug=True)