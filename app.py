from flask import Flask, render_template, request, url_for, redirect, jsonify, flash, Response, render_template_string
from flask_mysqldb import MySQL
import cv2

import barcode
from barcode.writer import ImageWriter
import cv2
import numpy as np

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



app = Flask(__name__)
app.secret_key = '123'




app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'mydatabase'



mysql = MySQL(app)
@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/user')
def user_login():

    return render_template('user.html')


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == 'admin':

            return render_template('product.html', username=username)
        else:

            return render_template('index.html', error='Invalid credentials')


    return render_template('admin.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        shopname = request.form['shopname']
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM register WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            flash("Username already exists. Please choose a different username.", 'error')
            return redirect(url_for('register'))

        cur.execute("INSERT INTO register (shopname, name, username, password) VALUES (%s, %s, %s, %s)",
                    (shopname, name, username, password))
        mysql.connection.commit()
        cur.close()

        flash("Registration successful. You can now log in.", 'success')
        return redirect(url_for('user'))


    return render_template('register.html')


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cur = mysql.connection.cursor()

        cur.execute("SELECT * FROM register WHERE username=%s AND password=%s", (username, password))

        existing_user = cur.fetchone()

        if not existing_user:
            flash("Invalid username or password.", 'error')
            return redirect(url_for('user'))


    flash("Login successful.", 'success')
    return redirect(url_for('userproduct',id=existing_user[0]))


    return render_template('user.html')
@app.route('/userproduct')
def userproduct():

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM productorder ")
    count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM addproduct ")
    data = cur.fetchone()[0]
    cur.close()
    return render_template('userproduct.html',count1=count ,data1=data)


@app.route('/addorder', methods=['GET', 'POST'])
def addorder():

    if request.method == "POST":
        productname = request.form['productname']

        cur = mysql.connection.cursor()
        # cur.execute("SELECT * FROM addproduct WHERE id=%s AND productname = %s", (productname,))
        # existing_user = cur.fetchone()
        quantity = request.form['quantity']
        price = request.form['price']


        name = request.form['name']
        shopname = request.form['shopname']
        email = request.form['email']
        phoneno = request.form['phoneno']
        address = request.form['address']


        send_email(email, productname, price, quantity, name, shopname, phoneno, address)

        cur.execute(
            "INSERT INTO productorder (productname, price, quantity, name, shopname, email, phoneno, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (productname, price, quantity, name, shopname, email, phoneno, address))
        mysql.commit()
        cur.close()

        flash("Product order added successfully.")

        return redirect(url_for('order'))

    return render_template('addorder.html')

def send_email(email, productname, price, quantity, name, shopname, phoneno, address):

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'kdtakarul007@gmail.com'
    smtp_password = 'jjun wpij oiow braa'
    sender_email = 'kdtakarul007@gmail.com'


    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = 'Order Confirmation'

    body = f"Dear {name},\n\nThank you for your order!\n\nOrder Details:\nProduct: {productname}\nPrice: {price}\nQuantity: {quantity}\n\nShipping Details:\nName: {name}\nShop Name: {shopname}\nPhone Number: {phoneno}\nAddress: {address}\n\nBest regards,\nYour Shop Name"

    msg.attach(MIMEText(body, 'plain'))


    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(sender_email, email, text)
        alert_script = """
            <script>
                alert("Order confirmed! Check your email for details.");
                window.location.href = "{{ url_for('order') }}";
            </script>
            """

        return render_template_string(alert_script)


# @app.route('/addorder', methods=['GET', 'POST'])
# def addorder():
#
#
#     # pid = request.args.get('id')
#     # productname = request.args.get('productname')
#     #
#     # cur.execute("SELECT * FROM addproduct WHERE id=%s AND productname = %s", (pid, productname))
#     # existing_user = cur.fetchone()
#     #
#     if request.method == "POST":
#         # Handle the form submission for adding an order.
#         productname = request.form['productname']
#         price = request.form['price']
#         quantity = request.form['quantity']
#         name = request.form['name']
#         shopname = request.form['shopname']
#         email = request.form['email']
#         phoneno = request.form['phoneno']
#         address = request.form['address']
#
#         send_email(email, productname, price, quantity, name, shopname, phoneno, address)
#
#
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO productorder (productname, price, quantity, name, shopname, email, phoneno, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",(productname, price, quantity, name, shopname, email, phoneno, address))
#         mysql.connection.commit()
#         cur.close()
#         flash("Product order added successfully.", )
#         cur.execute()
#         return redirect(url_for('order'))
#
#                # pid=pid,existing_user=existing_user
#     return render_template('addorder.html' )



@app.route('/view')
def view():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM addproduct")
    existing_user = cur.fetchall()

    cur.close()
    flash("Product view successfully.", 'success')

    return render_template('view.html', data=existing_user)







@app.route('/product')
def product():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM productorder ")
    count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM addproduct ")
    data = cur.fetchone()[0]
    cur.close()

    return render_template('product.html' ,data1=data,count1=count)
@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':

        productname = request.form['productname']
        quantity = request.form['quantity']
        price = request.form['price']
        mafdate=request.form['mafdate']

        cur = mysql.connection.cursor()

        cur.execute("INSERT INTO addproduct (productname, quantity, price,mafdate) VALUES (%s, %s, %s,%s)",
                    (productname, quantity, price ,mafdate))


        mysql.connection.commit()

        cur.close()

        flash("Product added successfully.", 'success')
        return redirect(url_for('viewproduct'))


    return render_template('addproduct.html')
@app.route('/viewproduct', methods=['GET', 'POST'])
def viewproduct(existing_user=None):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM addproduct")
    existing_user = cur.fetchall()



    cur.close()
    flash("Product view successfully.", 'success')

    return render_template('viewproduct.html',data=existing_user)
@app.route('/order' ,methods=['GET','POST'])
def order():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productorder")
    existing_user = cur.fetchall()

    cur.close()
    flash("view successfully.", 'success')



    return render_template('order.html' ,data=existing_user)
@app.route('/adminorder' ,methods=['GET','POST'])
def adminorder():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM productorder")
    existing_user = cur.fetchall()

    cur.close()
    flash("view successfully.", 'success')



    return render_template('adminorder.html', data=existing_user)




@app.route('/barcode', methods=['POST'])
def barcode():
    uploaded_image = request.files['image']
    if uploaded_image:
        try:
            # Use a barcode scanning library to process the image and extract the barcode data
            barcode_data = barcode.scan(uploaded_image)
            return jsonify({"message": f"Scanned Barcode: {barcode_data}"})
        except Exception as e:
            return jsonify({"error": str(e)})
    else:
        return jsonify({"error": "No image uploaded"})



video_capture1 = cv2.VideoCapture(0)  # First camera
video_capture2 = cv2.VideoCapture(1)  # Second camera
video_capture1.set(3, 640)  # Width
video_capture1.set(4, 480)  # Height
video_capture1.set(5, 30)   # Frame rate
video_capture2.set(3, 640)  # Width
video_capture2.set(4, 480)  # Height
video_capture2.set(5, 30)   # Frame rate

def generate_frames(camera):
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/cam')
def cam():
    return render_template('cam.html')

@app.route('/video_feed1')
def video_feed1():
    return Response(generate_frames(video_capture1), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed2')
def video_feed2():
    return Response(generate_frames(video_capture2), mimetype='multipart/x-mixed-replace; boundary=frame')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080 ,debug=True)
