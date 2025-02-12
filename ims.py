from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

connect = sqlite3.connect('ims.db')

cur = connect.cursor()
cur.execute(
    'CREATE TABLE IF NOT EXISTS ACSINV (name NAME, \
    division NAME, location NAME, unit_price INTEGER, pref_vendor NAME, \
    stock_lvl INTEGER, minQty INTEGER, maxQty INTEGER, contract TEXT, \
    recurring TEXT, qty_need INTEGER, user INTEGER, timestamp DATE)')

@app.route('/additem', methods=['GET', 'POST'])
def additem():
    if request.method == 'POST':
        name = request.form['name']
        division = request.form['division']
        location = request.form['location']
        stock_lvl = request.form['stock_lvl']
        minQty = request.form['minQty']
        maxQty = request.form['maxQty']
        unit_price = request.form['unit_price']
        pref_vendor = request.form['pref_vendor']
        contract = request.form['contract']
        recurring = request.form['recurring']

        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('INSERT INTO ACSINV \
                           (name, division, location, unit_price, pref_vendor, stock_lvl, minQty, maxQty, \
                           contract, recurring) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                           (name, division, location, unit_price, pref_vendor, stock_lvl, minQty, maxQty, 
                            contract, recurring))
            users.commit()
        return render_template('index.html')
    else:
        return render_template('inventory/additem.html')
    
@app.route('/viewinventory', methods=['GET'])
def viewinventory():
    if request.method == 'GET':
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT * FROM ACSINV ORDER BY DIVISION ASC')
            data = cursor.fetchall()
        return render_template('inventory/viewinventory.html', data = data)
    
@app.route('/needtoorder', methods=['GET'])
def needtoorder():
    if request.method == 'GET':
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT name, division, location, minQty, stock_lvl, \
                           (minQty - stock_lvl) AS qty_need \
                           FROM acsinv \
                           WHERE (minQty - stock_lvl) > 0')
            data = cursor.fetchall()
        return render_template('orders/needtoorder.html', data = data)

@app.route('/updatestock', methods=['GET', 'POST'])
def updatestock():
    if request.method == 'POST':
        name = request.form['name']
        division = request.form['division']
        location = request.form['location']
        stock_lvl = request.form['stock_lvl']
        minQty = request.form['minQty']
        maxQty = request.form['maxQty']
        unit_price = request.form['unit_price']
        pref_vendor = request.form['pref_vendor']
        contract = request.form['contract']
        recurring = request.form['recurring']
        user = request.form['user']
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute("UPDATE acsinv SET \
                           division = ?, location = ?, stock_lvl = ?, minQty = ?, \
                           maxQty = ?, unit_price = ?, pref_vendor = ?, contract = ?, \
                           recurring = ?, user = ? WHERE name = ?", 
                            (division, location, stock_lvl, minQty, maxQty, unit_price,
                             pref_vendor, contract, recurring, user, name))

            users.commit()
            cursor.execute('SELECT * FROM ACSINV ORDER BY DIVISION ASC')

            data = cursor.fetchall()    
            
        return render_template('inventory/updatestock.html', data=data)
    else:
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT name, division, location, stock_lvl, minQty, \
                           maxQty, unit_price, pref_vendor, contract, recurring \
                           FROM ACSINV ORDER BY DIVISION ASC')

            data = cursor.fetchall() 
        return render_template('inventory/updatestock.html', data=data)

@app.route('/deleteitem', methods=['GET', 'POST'])
def deleteitem():
    if request.method == 'POST':
        name = request.form['name']
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('DELETE FROM ACSINV WHERE name = ?', (name,))
            users.commit()
            cursor.execute('SELECT * FROM ACSINV ORDER BY DIVISION ASC')

            data = cursor.fetchall() 
        return render_template('inventory/deleteitem.html', data = data)
    else:
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT name, division, stock_lvl FROM ACSINV ORDER BY DIVISION ASC')

            data = cursor.fetchall() 
        return render_template('inventory/deleteitem.html', data = data)

if __name__ == '__main__':
    app.run(debug=False)
