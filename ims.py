from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

connect = sqlite3.connect('ims.db')
connect.execute(
    'CREATE TABLE IF NOT EXISTS ACSINV (name TEXT, \
        division TEXT, stock_lvl NUMBER, minQty NUMBER, maxQty NUMBER, contract TEXT, \
        recurring TEXT)')

@app.route('/additem', methods=['GET', 'POST'])
def additem():
    if request.method == 'POST':
        name = request.form['name']
        division = request.form['division']
        stock_lvl = request.form['stock_lvl']
        minQty = request.form['minQty']
        maxQty = request.form['maxQty']
        contract = request.form['contract']
        recurring = request.form['recurring']

        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('INSERT INTO ACSINV \
                           (name, division, stock_lvl, minQty, maxQty, contract, recurring) VALUES (?,?,?,?,?,?,?)',
                           (name, division, stock_lvl, minQty, maxQty, contract, recurring))
            users.commit()
        return render_template('index.html')
    else:
        return render_template('additem.html')
    
@app.route('/viewinventory')
def viewinventory():
    connect = sqlite3.connect('ims.db')
    cursor = connect.cursor()
    cursor.execute('SELECT * FROM ACSINV ORDER BY DIVISION ASC')

    data = cursor.fetchall()
    return render_template('viewinventory.html', data = data)

# TODO: make @app.route and function to delete items
@app.route('/deleteitem', methods=['GET', 'DELETE'])
def deleteitem():
    if request.method == 'DELETE':
        with sqlite3.connect('ims.db') as users:
            cursor = users.cursor()
            cursor.execute('DELETE FROM ACSINV WHERE rowid = ?, (rowid)')
            users.commit()
        return render_template('index.html')
    else:
        return render_template('viewinventory.html')

# TODO: make @app.route, function, and HTML page to update inventory filtered by division

# TODO: need to add physical LOCATION column (especially true for new S/N clinics)

if __name__ == '__main__':
    app.run(debug=False)
