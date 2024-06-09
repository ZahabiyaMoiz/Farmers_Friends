import requests, json
from flask import render_template, redirect, url_for, request, session, jsonify
from config import app, mysql, mail, Message
from datetime import datetime
import random
from helpers import coordinates, getweather, getaqi,getWeatherDayWise, encode_string, decode_string

######### VIEW FUNCTIONS ##########

to_reload = False


@app.route("/test_email", methods=['GET', 'POST'])
def test_email():
    msg = Message("Hello", sender="miss.zahabiya@gmail.com", recipients=["miss.zahabiya@gmail.com"])
    msg.body = "Hello Flask message sent from Flask-Mail 2 mail testing"
    mail.send(msg)
    return "Sent"


def send_email(subject, body, recipients):
    try:
        msg = Message(subject, sender="miss.zahabiya@gmail.com", recipients=recipients)
        msg.body = body
        mail.send(msg)
    except Exception as e:
        print(e)
        return "Failed"
    return "Sent"


@app.route('/',methods=['GET','POST'])
def index():
    # if "farmer_id" in session.keys():
    farmer_id = session.get("farmer_id")
    # if "buyer_id" in session.keys():
    buyer_id = session.get("buyer_id")
    if not farmer_id and not buyer_id:
        return render_template('index.html')
    print(farmer_id, session.get("is_premium"))
    if not buyer_id:
        cur = mysql.connection.cursor()
        cur.execute("""SELECT c.`id`, ua.`username` 'name', p.`Name` 'product_name', p.`id` 'product_id', c.`sender_id` 'buyer_id', c.`receiver_id` 'farmer_id'
                        FROM chat_notification c
                        JOIN user_account ua ON c.`sender_id` = ua.`id` AND ua.`role` = 'customer'
                        JOIN chat ch ON c.`chat_id` = ch.`id`
                        JOIN product p ON ch.`product_id` = p.`id`
                        WHERE c.`receiver_id` = %s AND c.`seen` = %s
                        GROUP BY p.`id`, c.`sender_id`
                    """, (farmer_id, 0))
        chat_notification = cur.fetchall()
        notification_data = []
        for i in chat_notification:
            notification_data.append({
                'notification_id': i[0],
                'name': i[1],
                'product_name': i[2],
                'product_id': i[3],
                'buyer_id': i[4],
                'farmer_id': i[5]
            })
        print(chat_notification)
        print(notification_data)
        return render_template('index.html', farmer_id=farmer_id, notification_data = notification_data, is_premium=session.get("is_premium", ''))
    chat_notification = 0
    cur = mysql.connection.cursor()
    cur.execute("""SELECT c.`id`, ua.`username` 'name', p.`Name` 'product_name', p.`id` 'product_id', c.`sender_id` 'farmer_id', c.`receiver_id` 'buyer_id'
                    FROM chat_notification c
                    JOIN user_account ua ON c.`sender_id` = ua.`id` AND ua.`role` = 'farmer'
                    JOIN chat ch ON c.`chat_id` = ch.`id`
                    JOIN product p ON ch.`product_id` = p.`id`
                    WHERE c.`receiver_id` = %s AND c.`seen` = %s
                    GROUP BY p.`id`, c.`sender_id`
                """, (buyer_id, 0))
    chat_notification = cur.fetchall()
    notification_data = []
    for i in chat_notification:
        notification_data.append({
            'notification_id': i[0],
            'farmer_name': i[1],
            'product_name': i[2],
            'product_id': i[3],
            'farmer_id': i[4],
            'buyer_id': i[5]
        })
    print(chat_notification)
    print(notification_data)
    is_premium = "True" if session.get("is_premium") else ""
    return render_template('index.html', buyer_id=buyer_id, notification_data = notification_data, is_premium=is_premium)


@app.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')
    data = request.get_json()['data']
    user_data = {}
    for i in data:
        user_data[i['name']] = str(i['value'])
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user_account WHERE username = %s AND password = %s AND role = %s", (user_data['username'], user_data['password'], user_data['user_type']))
    user = cur.fetchone()
    if not user:
        return jsonify({"success":False, "message":"Invalid username or password or role"})
    session['is_premium'] = False
    if user[4] == 1:
        session['is_premium'] = True
    if user_data['user_type'] == 'farmer':
        session['farmer_id'] = user[0]
    elif user_data['user_type'] == 'customer':
        session['buyer_id'] = user[0]
    return jsonify({"success":True, "message":"Login successful", "category":user[3]})


@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method != 'POST':
        return render_template('signup.html')

@app.route('/profile',methods=['GET','POST'])
def profile():
    # user_id = session.get('user_id')
    if 'farmer_id' not in session.keys() and 'buyer_id' not in session.keys():
        return redirect(url_for('login'))
    
    farmer_id = session.get('farmer_id')
    buyer_id = session.get('buyer_id')
    
    cur = mysql.connection.cursor()
    profile_type = ""
    products = []
    if farmer_id:
        cur.execute("SELECT * FROM farmer WHERE UserAccountID = %s", (farmer_id,))
        user = cur.fetchone()
        user = {
            'name': user[1],
            'location': user[2],
            'phone': user[3],
            'email': user[4],
            'farm_size': user[5],
            'farming_experience': user[6]
        }
        profile_type = "Farmer"
        cur.execute("SELECT * FROM product WHERE FarmerID = %s", (farmer_id,))
        product_data = cur.fetchall()
        for i in product_data:
            products.append({
                'id': i[0],
                'name': i[1],
                'image_url': i[2],
                'description': i[3],
                'category': i[4],
                'price': i[5],
                'quantity': i[6],
                'farmer_id': i[7]
            })
    elif buyer_id:
        cur.execute("SELECT * FROM buyer WHERE UserAccountID = %s", (buyer_id,))
        user = cur.fetchone()
        user = {
            'name': user[1],
            'location': user[2],
            'phone': user[3],
            'email': user[4],
        }
        profile_type = "Buyer"

    return render_template('profile.html', user=user, farmer_id=farmer_id, buyer_id=buyer_id, profile_type=profile_type, products=products)

@app.route('/signup_farmer',methods=["GET","POST"])
def signup_farmer():
    
    if request.method != 'POST':
        return ''
    
    data = request.get_json()['data']
    user_data = {}
    
    for i in data:
        user_data[i['name']] = str(i['value'])

    if user_data['password'] != user_data['reenter-password']:
        return jsonify({"success":False, "message":"Passwords do not match"})
    
    cur = mysql.connection.cursor()

    cur.execute("SELECT * from user_account where username = %s and password = %s", (user_data['username'], user_data['password']))
    user = cur.fetchone()
    if user:
        return jsonify({"success":False, "message":"User already exists"})


    cur.execute("INSERT INTO user_account (username, password, role, is_premium) values (%s, %s, %s, %s)", (user_data['username'], user_data['password'], user_data['category'], user_data['is_premium']))
    mysql.connection.commit()
    user_id = cur.lastrowid

    # session['user_id'] = user_id

    if user_data['category'] == 'farmer':
        cur.execute("INSERT INTO farmer (Name, Location, ContactPhone, ContactEmail, FarmSize, FarmingExperience, zipcode, UserAccountID) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (user_data['username'], '', user_data['phone'], user_data['email'], 0, 0, user_data['zipcode'],user_id))
    elif user_data['category'] == 'customer':
        cur.execute("INSERT INTO buyer (Name, Location, ContactPhone, ContactEmail, UserAccountID) VALUES (%s, %s, %s, %s, %s)", (user_data['username'], '', user_data['phone'], user_data['email'], user_id))
    mysql.connection.commit()

    return jsonify({"success":True, 'message':'User created successfully', "category":user_data['category']})


@app.route("/products", methods=['GET', 'POST'])
def products():
    farmer_id = session.get('farmer_id')
    buyer_id = session.get('buyer_id')
    cur = mysql.connection.cursor()
    
    notification_id = request.args.get('notification_id')
    
    open_chat = False
    product_id = None
    prod_farmer_id = None
    if notification_id:
        print("open chat")
        print(notification_id)
        cur.execute("UPDATE chat_notification SET seen = %s WHERE id = %s", (1, notification_id))
        mysql.connection.commit()
        cur.execute("""SELECT ch.`product_id`, c.`sender_id` FROM chat_notification c
                    JOIN chat ch ON c.`chat_id` = ch.`id`
                    WHERE c.`id` = %s""", (notification_id,))
        chat_data = cur.fetchone()
        product_id = chat_data[0]
        prod_farmer_id = chat_data[1]
        open_chat = True
    
    cur.execute("SELECT * FROM product")
    products = cur.fetchall()
    product_data = []
    for i in products:
        product_data.append({
            'id': i[0],
            'name': i[1],
            'image_url': i[2],
            'description': i[3],
            'category': i[4],
            'price': i[5],
            'quantity': i[6],
            'farmer_id': i[7]
        })


    cur = mysql.connection.cursor()
    cur.execute("""SELECT c.`id`, ua.`username` 'name', p.`Name` 'product_name', p.`id` 'product_id', c.`sender_id` 'farmer_id', c.`receiver_id` 'buyer_id'
                    FROM chat_notification c
                    JOIN user_account ua ON c.`sender_id` = ua.`id` AND ua.`role` = 'farmer'
                    JOIN chat ch ON c.`chat_id` = ch.`id`
                    JOIN product p ON ch.`product_id` = p.`id`
                    WHERE c.`receiver_id` = %s AND c.`seen` = %s
                    GROUP BY p.`id`, c.`sender_id`
                """, (buyer_id, 0))
    chat_notification = cur.fetchall()
    notification_data = []
    for i in chat_notification:
        notification_data.append({
            'notification_id': i[0],
            'farmer_name': i[1],
            'product_name': i[2],
            'product_id': i[3],
            'farmer_id': i[4],
            'buyer_id': i[5]
        })
    return render_template('product.html', is_premium=session.get("is_premium", ''), products=product_data, farmer_id=farmer_id, buyer_id=buyer_id, open_chat=open_chat, product_id=product_id, prod_farmer_id=prod_farmer_id, notification_data = notification_data)


@app.route("/chat", methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        data = request.get_json()['data']
        print(data)
        message = encode_string(data['message'])
        try:        
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO chat (product_id, sender_id, receiver_id, message, sent_at, sender_type) VALUES (%s, %s, %s, %s, %s, %s)", (data['product_id'], data['sender_id'], data['receiver_id'], message, datetime.now(), data['sender_type']))            
            mysql.connection.commit()
            chat_id = cur.lastrowid
            cur.execute("INSERT INTO chat_notification (sender_id, receiver_id, chat_id, seen, created_at) VALUES (%s, %s, %s, %s, %s)", (data['sender_id'], data['receiver_id'], chat_id, 0, datetime.now()))
            mysql.connection.commit()
        except Exception as e:
            print(e)
            return jsonify({"success":False, "message":"Message not sent"})
        return jsonify({"success":True, "message":"Message sent successfully"})
    
    product_id = request.args.get('product_id')
    buyer_id = request.args.get('buyer_id')
    cur = mysql.connection.cursor()
    
    
    # cur.execute("SELECT * FROM chat WHERE product_id = %s", (product_id,))
    # chats = cur.fetchall()
    query = f"""
        SELECT c.product_id,p.name,c.`sender_type`,c.`sender_id`,c.`receiver_id`,ua.username AS sender_name,
        uc.username AS reciever_name, c.`message`
        FROM chat c
        JOIN user_account ua
        ON ua.id=c.sender_id
        JOIN product p
        ON c.product_id=p.`id`
        JOIN user_account uc
        ON uc.id=c.`receiver_id`
        WHERE (c.`receiver_id` = {buyer_id} OR c.`sender_id` = {buyer_id} ) AND p.id = {product_id};
    """
    cur.execute(query)
    chats = cur.fetchall()

    chat_data = []
    for i in chats:
        chat_data.append({
            'product_id': i[0],
            'product_name': i[1],
            'sender_type': i[2],
            'sender_id': i[3],
            'receiver_id': i[4],
            'sender_name': i[5],
            'receiver_name': i[6],
            'message': decode_string(i[7])
        })
    return jsonify(chat_data)

@app.route("/farmer", methods=['GET', 'POST'])
def farmer():
    return render_template('farmer/farmer.html')

@app.route("/buyer", methods=['GET', 'POST'])
def buyer():
    if 'buyer_id' not in session.keys():
        return redirect(url_for('login'))
    buyer_id = session.get('buyer_id')
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM buyer WHERE UserAccountID = %s", (buyer_id,))
    user = cur.fetchone()
    user = {
        'name': user[1],
        'location': user[2],
        'phone': user[3],
        'email': user[4],
    } 
    return render_template('customer/buyer.html', user=user)

@app.route("/buyer/update", methods=['GET', 'POST'])
def buyer_update():
    if 'buyer_id' not in session.keys():
        return redirect(url_for('login'))
    if request.method != 'POST':
        return redirect(url_for('index'))
    buyer_id = session.get('buyer_id')
    data = request.get_json()['data']
    user_data = {}
    for i in data:
        user_data[i['name']] = str(i['value'])
    cur = mysql.connection.cursor()
    cur.execute("UPDATE buyer SET NAME = %s, Location = %s, ContactPhone = %s, ContactEmail = %s WHERE UserAccountID = %s", (user_data['name'], user_data['address'], user_data['phone_number'], user_data['email'], buyer_id))
    mysql.connection.commit()
    return jsonify({"success":True, "message":"Profile updated successfully"})
    # return render_template('buyer_update.html', user=user)

@app.route("/file_upload", methods=['GET', 'POST'])
def file_upload():
    print("here")
    attachment_file = request.files.get("file")
    filename = attachment_file.filename
    file_url = "static/uploads/"+filename
    attachment_file.save("static/uploads/"+filename)
    return jsonify({"success":True, "message":"File uploaded successfully", "file_url":file_url})

@app.route("/product_delete", methods=['POST'])
def product_delete():
    if 'farmer_id' not in session.keys():
        return redirect(url_for('login'))
    product_id = request.args.get('product_id')
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM product WHERE id = %s", (product_id,))
    mysql.connection.commit()
    return jsonify({"success":True, "message":"Product deleted successfully"})

@app.route("/product_update", methods=['GET', 'POST'])
def product_update():
    print(session.keys())
    if 'farmer_id' not in session.keys():
        return redirect(url_for('login'))
    if request.method != 'POST':
        product_id = request.args.get('product_id')
        print(product_id)
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM product WHERE id = %s", (product_id,))
        product = cur.fetchone()
        products = {
            'id': product[0],
            'name': product[1],
            'image_url': product[2],
            'description': product[3],
            'category': product[4],
            'price': product[5],
            'quantity': product[6],
            'farmer_id': product[7]
        }
        return render_template('farmer/product_update.html', products=products, farmer_id=product[7])
    
    data = request.get_json()['data']
    user_data = {}
    for i in data:
        user_data[i['name']] = str(i['value'])
    farmer_id = session.get('farmer_id')
    print(user_data)
        
    cur = mysql.connection.cursor()
    cur.execute("UPDATE product SET Name = %s, image_url = %s, Description = %s, Category = %s, Price = %s, QuantityAvailable = %s WHERE FarmerID = %s and id = %s", (user_data['product_name'], user_data['product_image_url'], user_data['product_description'], '', int(user_data['product_price']), int(user_data['product_quantity']), int(farmer_id), int(user_data['product_id'])))
    mysql.connection.commit()
    return jsonify({"success":True, "message":"Product updated successfully"})
    # return render_template('farmer/product_update.html')

@app.route("/product_add", methods=['GET', 'POST'])
def product_add():
    if request.method == 'POST':
        data = request.get_json()['data']
        user_data = {}
        for i in data:
            user_data[i['name']] = str(i['value'])
        farmer_id = session.get('farmer_id')
        print(user_data)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO product (Name, image_url, Description, Category, Price, QuantityAvailable, FarmerID) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_data['product_name'], user_data['product_image_url'], user_data['product_description'], '', int(user_data['product_price']), int(user_data['product_quantity']), int(farmer_id)))
        mysql.connection.commit()
        return jsonify({"success":True, "message":"Product added successfully"})

    if 'farmer_id' not in session.keys():
        return redirect(url_for('login'))
    farmer_id = session.get('farmer_id')
    return render_template('farmer/product_add.html', farmer_id=farmer_id)

@app.route("/checkout", methods=['GET', 'POST'])
def checkout():
    if request.method != 'POST':
        return redirect(url_for('index'))
    
    if 'buyer_id' not in session.keys():
        return redirect(url_for('login'))
    
    data = request.get_json()['data']
    print(data)
    return render_template('customer/checkout.html', data=data)

@app.route("/invoice", methods=['GET', 'POST'])
def invoice():

    if 'buyer_id' not in session.keys():
        return redirect(url_for('login'))
    
    data = session.get("checkout_data")
    date = datetime.now().strftime("%d/%m/%Y")
    data['date'] = date
    data['invoice_number'] = "INV-"+ str(random.randint(10000, 99999))
    cur = mysql.connection.cursor()
    for i in data['products']:
        cur.execute("""
            SELECT f.`NAME` FROM product p 
            JOIN farmer f ON f.`UserAccountID` = p.`FarmerID`
            WHERE p.`id`=%s
        """, (i['product_id'],))
        i['farmer_name'] = cur.fetchone()[0]
        i['product_price'], i['product_quantity'] = int(i['product_price']), int(i['product_quantity'])
    cur.execute("SELECT NAME, ContactEmail FROM buyer WHERE UserAccountID = %s", (session['buyer_id'],))
    buyer_name, buyer_email = cur.fetchone()
    print(buyer_name, buyer_email)
    
    subject = "Invoice and Order Confirmation for your purchase"
    body = f"Hello {buyer_name},\n\nThank you for your purchase. Your order has been confirmed.\n\n"
    body += "Here is the invoice for your purchase:\n\n"
    body += f"Date: {date}\n"
    body += f"Invoice Number: {data['invoice_number']}\n\n"
    body += "Products:\n"
    total_amount = 0
    for i in data['products']:
        body += f"Product Name: {i['product_name']}\n"
        body += f"Farmer Name: {i['farmer_name']}\n"
        body += f"Price: {i['product_price']} Rs\n"
        body += f"Quantity: {i['product_quantity']}\n"
        body += f"Total: {i['product_price']*i['product_quantity']} Rs\n\n"
        total_amount += i['product_price']*i['product_quantity']

        print((session['buyer_id'], int(i['product_id']), i['product_quantity'], date, i['product_price']*i['product_quantity']))
        t_price = i['product_price']*i['product_quantity']
        cur.execute("INSERT INTO orders (CustomerID, ProductID, QuantityOrdered, OrderDate, Amount) VALUES (%s, %s, %s, %s, %s)", (session['buyer_id'], int(i['product_id']), i['product_quantity'], date, t_price))
        mysql.connection.commit()
    cur.close()    
    body += f"Total Amount: {total_amount} Rs\n\n"
    body += "Thank you for shopping with us. We hope to see you again soon.\n\n"
    body += "Regards,\nFarmer Friend"
    send_email(subject, body, [buyer_email])
    
    return render_template('customer/invoice.html', data=data)

@app.route("/pinvoice", methods=['GET', 'POST'])
def pinvoice():
    if request.method != 'POST':
        return redirect(url_for('index'))
    if 'buyer_id' not in session.keys() and 'farmer_id' not in session.keys():
        return redirect(url_for('login'))
    data = request.get_json()['data']
    session["checkout_data"] = data
    return {
        "success":True
    }

@app.route("/farmer_chat", methods=['GET', 'POST'])
def farmer_chat(): 
    farmer_id = session.get('farmer_id')
    print(session.get('is_premium'), session.get('farmer_id'))
    if not farmer_id:
        return redirect(url_for('login'))
    if session.get('is_premium') == False:
        return redirect(url_for('index'))
    notification_id = request.args.get('notification_id')
    open_chat = False
    n_product_id = None
    prod_farmer_id = None
    if notification_id:
        print("open chat")
        print(notification_id)
        cur = mysql.connection.cursor()
        cur.execute("UPDATE chat_notification SET seen = %s WHERE id = %s", (1, notification_id))
        mysql.connection.commit()
        cur.execute("""SELECT ch.`product_id`, c.`sender_id` FROM chat_notification c
                    JOIN chat ch ON c.`chat_id` = ch.`id`
                    WHERE c.`id` = %s""", (notification_id,))
        chat_data = cur.fetchone()
        n_product_id = chat_data[0]
        prod_farmer_id = chat_data[1]
        open_chat = True

    query = f"""
        SELECT c.product_id,p.name,c.`sender_type`,c.`sender_id`,c.`receiver_id`,ua.username AS sender_name,
        uc.username AS reciever_name, c.`message`
        FROM chat c
        JOIN user_account ua
        ON ua.id=c.sender_id
        JOIN product p
        ON c.product_id=p.`id`
        JOIN user_account uc
        ON uc.id=c.`receiver_id`
        WHERE c.`receiver_id` = {farmer_id} OR c.`sender_id` = {farmer_id}
    """

    cur = mysql.connection.cursor()
    cur.execute(query)
    chats = cur.fetchall()
    chat_data = {}
    for product_id, product_name, sender_type, sender_id, receiver_id, sender_name, receiver_name, message in chats:
        if product_id not in chat_data:
            chat_data[product_id] = {
                "product_name": product_name,
                "customer_chats": {}
            }

        customer_id = receiver_id if sender_type == "farmer" else sender_id
        customer_name = receiver_name if sender_type == "farmer" else sender_name

        if customer_id not in chat_data[product_id]["customer_chats"]:
            chat_data[product_id]["customer_chats"][customer_id] = {
                "customer_name": customer_name,
                "messages": [],
            }

        chat_data[product_id]["customer_chats"][customer_id]["messages"].append({
            "message": decode_string(message),
            "sender": sender_name,
            "receiver": receiver_name,
            "sender_type": sender_type
        })
    # make a list of chats based on product and customers
    print(json.dumps(chat_data, indent=4))

    print(chats)
    
    return render_template('chat.html', chats=chat_data, range=range, len=len, farmer_id=farmer_id, open_chat=open_chat, product_id=n_product_id, prod_farmer_id=prod_farmer_id, is_premium=session.get("is_premium", ''))


@app.route("/farmer/get_full_weather", methods=["GET", "POST"])
def full_weather():

    farmer_id = session.get('farmer_id')
    if not farmer_id:
        return redirect(url_for('login'))    

    if request.method != 'POST':
        return render_template("farmer/get_weather.html", farmer_id=farmer_id)

    res_date = request.args.get("date")
    print(res_date)
    cur = mysql.connection.cursor()
    cur.execute("SELECT zipcode FROM farmer WHERE UserAccountID = %s", (farmer_id,))
    zipcode = cur.fetchone()[0]

    zipcode = int(zipcode)
    units = request.form.get("units")

    # Get latitude and longitude for zipcode
    latlong = coordinates(zipcode)
    lat = latlong["lat"]
    lon = latlong["lon"]

    # Get weather by latitude and longitude
    # weather = getweather(lat, lon, units)
    weather = getWeatherDayWise(lat, lon, units, date=res_date)
    aqi = getaqi(lat, lon)
    print(weather)
    # print(aqi)
    return render_template("full_weather.html", weather=weather, aqi=aqi, units=units)
    

@app.route("/order", methods=['GET', 'POST'])
def order():
    buyer_id = session.get("buyer_id")
    if not buyer_id:
        return redirect(url_for('login'))
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM orders WHERE CustomerID = %s", (buyer_id,))
    orders = cur.fetchall()
    order_data = []
    for i in orders:
        cur.execute("SELECT Name FROM product WHERE id = %s", (i[2],))
        product_name = cur.fetchone()[0]
        order_data.append({
            'order_id': i[0],
            'product_id': i[2],
            'product_name': product_name,
            'quantity': i[3],
            'order_date': i[4],
            'amount': i[5]
        })
    print(order_data)
    cur.close()
    return render_template('order.html', buyer_id=buyer_id, order_data=order_data)

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    return render_template('admin.html')

if __name__ == '__main__':
    app.run(debug=True, port=5002)