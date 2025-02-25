from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

connect = sqlite3.connect('ims.db')

cursor = connect.cursor()
cursor.execute("PRAGMA foreign_keys = ON")
cursor.execute(
    'CREATE TABLE IF NOT EXISTS inv (item_id INTEGER PRIMARY KEY AUTOINCREMENT, \
    item_name VARCHAR(50), item_descr VARCHAR(255), location_id VARCHAR(20), division VARCHAR(20), \
    min_qty NUMBER, max_qty NUMBER, contract VARCHAR(1), recurring VARCHAR(1))')
cursor.execute(
    'CREATE TABLE IF NOT EXISTS inv_counts (count_id INTEGER PRIMARY KEY AUTOINCREMENT, \
    timestamp DATE, user NUMBER, item_id INTEGER,  \
    stock_lvl NUMBER)'
)
cursor.execute(
    'CREATE TABLE IF NOT EXISTS locations (location_id INTEGER PRIMARY KEY AUTOINCREMENT, \
    facility VARCHAR(14), primary_loc VARCHAR(25), secondary_loc VARCHAR(10), division VARCHAR(20))'
)

@app.route('/additem', methods=['GET', 'POST'])
def additem():
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_descr = request.form['item_descr']
        location_id = request.form['location_id']
        division = request.form['division']
        min_qty = request.form['min_qty']
        max_qty = request.form['max_qty']
        contract = request.form['contract']
        recurring = request.form['recurring']

        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('INSERT INTO inv \
                           (item_name, item_descr, location_id, division, min_qty, max_qty, contract, recurring) \
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                           (item_name, item_descr, location_id, division, min_qty, max_qty, contract, recurring))
            users.commit()
        return render_template('index.html')
    else:
        return render_template('inventory/additem.html')
    
@app.route('/addlocation', methods=['GET', 'POST'])
def addlocation():
    if request.method == 'POST':
        facility = request.form['facility']
        primary_loc = request.form['primary_loc']
        secondary_loc = request.form['secondary_loc']
        division = request.form['division']

        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('INSERT INTO locations \
                           (facility, primary_loc, secondary_loc, division) \
                           VALUES (?, ?, ?, ?)',
                           (facility, primary_loc, secondary_loc, division))
            users.commit()
        return render_template('index.html')
    else:
        return render_template('inventory/addlocation.html')
    
@app.route('/viewinventory', methods=['GET'])
def viewinventory():
    if request.method == 'GET':
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT * FROM inv ORDER BY division')
            inv_data = cursor.fetchall()
            cursor.execute('SELECT locations.location_id, locations.facility, locations.primary_loc, locations.secondary_loc, inv.location_id \
                           FROM locations JOIN inv \
                           ON locations.location_id = inv.location_id \
                           ')
            loc_data = cursor.fetchall()
        return render_template('inventory/viewinventory.html', data = zip(inv_data, loc_data))
    
@app.route('/invcounts', methods=['GET', 'POST'])
def invcounts():
    if request.method == 'POST':
        item_id = request.form['item_id']
        item_name = request.form['item_name']
        location_id = request.form['location_id']
        stock_lvl = request.form['stock_lvl']
        user = request.form['user']
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('INSERT INTO inv_counts  \
                           (item_id, item_name, location_id, stock_lvl, \
                           user) \
                           VALUES (?, ?, ?, ?, ?)', 
                           (item_id, item_name, location_id, stock_lvl, user))
            users.commit()
            cursor.execute('SELECT inv.item_id, inv.item_name, inv.item_descr, inv.location_id, inv_counts.stock_lvl \
                            FROM inv JOIN inv_counts \
                            ON inv.item_id = inv_counts.item_id')
            count_data = cursor.fetchall()    
        return render_template('inventory/invcounts.html', count_data=count_data)
    else:
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT inv.item_id, inv.item_name, inv.item_descr, inv.location_id, inv_counts.stock_lvl \
                            FROM inv JOIN inv_counts \
                            ON inv.item_id = inv_counts.item_id')
            count_data = cursor.fetchall() 
        return render_template('inventory/invcounts.html', count_data=count_data)
    
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

@app.route('/updateitem', methods=['GET', 'POST'])
def updateitem():
    if request.method == 'POST':
        item_name = request.form['item_name']
        item_descr = request.form['item_descr']
        location_id = request.form['location_id']
        division = request.form['division']
        min_qty = request.form['min_qty']
        max_qty = request.form['max_qty']
        contract = request.form['contract']
        recurring = request.form['recurring']
        item_id = request.form['item_id']
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute("UPDATE inv SET \
                           item_name = ?, item_descr = ?, location_id = ?, division = ?, \
                           min_qty = ?, max_qty = ?, contract = ?, recurring = ? \
                           WHERE item_id = ?", 
                            (item_name, item_descr, location_id, division, min_qty, max_qty,
                             contract, recurring, item_id))

            users.commit()
            cursor.execute('SELECT * FROM inv ORDER BY DIVISION ASC')

            upd_data = cursor.fetchall()    
            
        return render_template('inventory/updateitem.html', upd_data=upd_data)
    else:
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT * FROM inv')

            upd_data = cursor.fetchall() 
        return render_template('inventory/updateitem.html', upd_data=upd_data)

@app.route('/deleteitem', methods=['GET', 'POST'])
def deleteitem():
    if request.method == 'POST':
        item_id = request.form['item_id']
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('DELETE FROM inv WHERE item_id = ?', (item_id,))
            users.commit()
            cursor.execute('SELECT * FROM inv ORDER BY DIVISION')
            data = cursor.fetchall() 
        return render_template('inventory/deleteitem.html', data = data)
    else:
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('SELECT inv.item_id, inv.item_name, inv.item_descr, inv.division, \
                           locations.facility, locations.primary_loc, locations.secondary_loc \
                           FROM inv JOIN locations \
                           ON inv.location_id = locations.location_id')
            data = cursor.fetchall() 
        return render_template('inventory/deleteitem.html', data = data)

if __name__ == '__main__':
    app.run(debug=False)
