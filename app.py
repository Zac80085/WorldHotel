#Name:Hein Zarni Naing
#StudentID:23005535
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from decimal import Decimal
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import random
import mysql.connector
import os
import dbfunc
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)   
app.secret_key ="HeinZarniNaing"
scheduler = BackgroundScheduler()


@app.route('/')
@app.route('/index')      
def index():
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT DISTINCT City FROM Hotel ORDER BY City')
    cities = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", cities = cities)


@app.route('/ForgetPassword')
def ForgetPassword():
     return render_template("ForgetPassword.html")


@app.route('/LogIn', methods=['GET', 'POST'])
def LogIn():
    if request.method == 'POST':
        Email = request.form['email']
        Password = request.form['psw']
        try:
            conn = dbfunc.getConnection()
            if conn is not None and conn.is_connected():
                dbcursor = conn.cursor(dictionary=True)
                dbcursor.execute('SELECT * FROM User WHERE Email = %s', (Email,))
                user_record = dbcursor.fetchone()
                dbcursor.close()
                conn.close()

            if user_record:
                hashed_password = user_record['Password']

                if check_password_hash(hashed_password, Password):
                    print("Password Matches")
                    session['user_email'] = user_record['Email']
                    session['isAdmin'] = user_record['isAdmin'] == "Yes"
                    session['user_id'] = user_record['UserID']  
                    return redirect(url_for('admin'))
                else:
                    flash('Invalid email or password', 'error')
                    return render_template("LogIn.html")

        except Exception as e:
            print(f"An error occurred during login: {e}")
            print(f"Username: {Email}, Password: {Password}")

        flash('Invalid email or password', 'error')
        return render_template("LogIn.html")

    else:
        return render_template("LogIn.html")


@app.route('/LogOut')
def LogOut():
    session.pop('user_email', None)  
    session.pop('isAdmin', None)      
    return redirect(url_for('index'))
          
@app.route('/admin')
def admin():
    if 'isAdmin' in session and session['isAdmin']:
        return render_template('admin.html')
    else:
        flash('You do not have access to the admin page.', 'error')
        return redirect(url_for('index'))

@app.route('/registerForm', methods = ['GET', 'POST'])
def registerForm():
     if request.method == 'GET':
          return render_template("registerForm.html")
     else:
          FirstName = request.form.get('firstname')
          LastName = request.form.get('lname')
          Email = request.form.get('email')
          Password = request.form.get('psw')
          hashed_password = generate_password_hash(Password, method='pbkdf2:sha256')
          conn = dbfunc.getConnection() 
          if conn is not None and conn.is_connected():
               dbcursor = conn.cursor()
               DB_NAME = 'HotelBooking' 
               TABLE_NAME = 'User'
               dbcursor.execute(f'USE {DB_NAME};')
               INSERT_statement = (
                    f'INSERT INTO {TABLE_NAME} '
                    '(FirstName, LastName, Email, Password) '
                    'VALUES (%s, %s, %s, %s);'
                    )
               dataset = (FirstName, LastName, Email, hashed_password)
               print(dataset)
               dbcursor.execute(INSERT_statement, dataset)
               conn.commit()
               print('INSERT query executed successfully.')
               dbcursor.close()
               conn.close()
          return redirect(url_for("LogIn"))



@app.route('/Contact', methods = ['GET', 'POST'])        
def Contact():
    if request.method == 'GET':
        return render_template("Contact.html")
    else:
        FirstName = request.form['firstname']
        LastName = request.form['lastname']
        Email = request.form['email']
        Subject = request.form['subject']
        Location = request.form['Location']

        conn = dbfunc.getConnection()

        if conn is not None and conn.is_connected():
            dbcursor = conn.cursor()
            DB_NAME = 'HotelBooking'
            TABLE_NAME = 'Contact'

            dbcursor.execute(f'USE {DB_NAME};')
            INSERT_statement = (
                f'INSERT INTO {TABLE_NAME} '
                '(FirstName, LastName, Email, Subject, Location) '
                'VALUES (%s, %s, %s, %s, %s);'
            )
            dataset = (FirstName, LastName, Email, Subject, Location)
            print(dataset)
            dbcursor.execute(INSERT_statement, dataset)
            conn.commit()
            print('INSERT query executed successfully.')
            dbcursor.close()
            conn.close()

        return redirect(url_for("index"))
   
@app.route('/TandC')
def TandC():
     return render_template("TandC.html")

    
@app.route('/DeleteUser/<int:user_id>', methods=['POST'])
def DeleteUser(user_id):
    if 'user_email' not in session or not session.get('isAdmin'):
        flash('You must be an admin to delete users.', 'error')
        return redirect(url_for('LogIn'))

    try:
        conn = dbfunc.getConnection()
        if conn and conn.is_connected():
            cursor = conn.cursor()
            cursor.execute('DELETE FROM User WHERE UserID = %s', (user_id,))
            conn.commit()
            flash('User deleted successfully.', 'success')
        else:
            flash('Connection to the database failed.', 'error')
    except Exception as e:
        flash(f'An error occurred while deleting the user: {e}', 'error')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

    return redirect(url_for('UserData'))

@app.route('/RoomData')
def RoomData():
    conn = dbfunc.getConnection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT RoomID, RoomType, RoomNumber, AvailabilityStatus, PeakSeasonPrice, OffPeakSeasonPrice, HotelID FROM Room')  
        Room = cursor.fetchall()
        conn.close()
        return render_template('RoomData.html', Rooms=Room)
    else:
        return "Failed to connect to the database."

def get_room_type_ids():
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT * FROM RoomType")
        room_types = cursor.fetchall()
        
        room_type_ids = {room_type['RoomTypeName']: room_type['RoomTypeID'] for room_type in room_types}
        return room_type_ids
        
    finally:
        cursor.close()
        conn.close()


def get_hotel_id_by_city(city):
    conn = dbfunc.getConnection() 
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT HotelID FROM Hotel WHERE City = %s", (city,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result:
        return result['HotelID']
    else:
        return None

def get_room_rates(hotel_id, room_type_id, is_peak):
    conn = dbfunc.getConnection()  
    cursor = conn.cursor(dictionary=True)
    if is_peak:
        cursor.execute("SELECT PeakSeasonPrice FROM Hotel_RoomType WHERE HotelID = %s AND RoomTypeID = %s", (hotel_id, room_type_id))
    else:
        cursor.execute("SELECT OffPeakSeasonPrice FROM Hotel_RoomType WHERE HotelID = %s AND RoomTypeID = %s", (hotel_id, room_type_id))
    rate = cursor.fetchone()
    cursor.close()
    conn.close()
    if rate:
        return rate['PeakSeasonPrice'] if is_peak else rate['OffPeakSeasonPrice']
    else:
        return None


def calculate_discount(check_in_date):
    today = datetime.now().date()
    check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
    days_in_advance = (check_in - today).days

    if 80 <= days_in_advance <= 90:
        return 0.30  
    elif 60 <= days_in_advance <= 79:
        return 0.20 
    elif 45 <= days_in_advance <= 59:
        return 0.10  
    else:
        return 0  

def calculate_room_price(check_in_date, days_stay, hotel_id, room_type_id, guest_count):
    check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
    peak_months = {4, 5, 6, 7, 8, 11, 12}
    is_peak = check_in.month in peak_months

    standard_rate = Decimal(get_room_rates(hotel_id, 1, is_peak))  
    days_stay = Decimal(days_stay)
    guest_count = Decimal(guest_count)
    room_rate_multiplier = Decimal('1.0')
    extra_guest_multiplier = Decimal('0.0')

    if room_type_id == 1:
        room_rate_multiplier = Decimal('1')
        extra_guest_multiplier = 0 
    elif room_type_id == 2:
        room_rate_multiplier = Decimal('1.2')
        extra_guest_multiplier = Decimal('0.1') if guest_count > Decimal('2') else 0  
    elif room_type_id == 3:
        room_rate_multiplier = Decimal('1.5')
        extra_guest_multiplier = Decimal('0.1') * (guest_count - Decimal('4')) if guest_count > Decimal('2') else 0  

    total_rate = (standard_rate * room_rate_multiplier) + (standard_rate * extra_guest_multiplier)

    total_cost = total_rate * days_stay

    discount_value = calculate_discount(check_in_date)

    discounted_total_cost = total_cost * (1 - Decimal(discount_value))

    return total_cost, discount_value, discounted_total_cost


@app.route('/display_booking', methods=['POST'])
def display_booking():
    session['check_in_date'] = request.form['check_in_date']
    session['check_out_date'] = request.form['check_out_date']
    session['num_days'] = request.form['num_days'] 
    session['location'] = request.form['location']
    session['guest_count'] = int(request.form['guest_count'])
    session['standard_room_count'] = int(request.form['standard_room_count'])
    session['double_room_count'] = int(request.form['double_room_count'])
    session['family_room_count'] = int(request.form['family_room_count'])
    
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    rooms_to_book = []
    room_ids = {}
    room_counts = {
        'Standard': int(session.get('standard_room_count', '0')),
        'Double': int(session.get('double_room_count', '0')),
        'Family': int(session.get('family_room_count', '0'))
    }

    for room_type, count in room_counts.items():
        if count > 0:  
            cursor.execute("""
            SELECT Room.RoomID, Room.RoomNumber, RoomType.RoomTypeName, RoomType.RoomTypeFeature, Hotel.City
            FROM Room
            INNER JOIN RoomType ON Room.RoomTypeID = RoomType.RoomTypeID
            INNER JOIN Hotel ON Room.HotelID = Hotel.HotelID
            WHERE Hotel.City = %s AND RoomType.RoomTypeName = %s
            AND Room.AvailabilityStatus = 'No' LIMIT %s
            """, (session['location'], room_type, count))
            rooms = cursor.fetchall()
            rooms_to_book.extend(rooms)
            room_ids[room_type] = [room['RoomID'] for room in rooms]

    cursor.close()
    conn.close()

    session['available_rooms'] = rooms_to_book
    session['room_ids'] = room_ids

    days_stay = session['num_days']
    location = session['location']
    hotel_id = get_hotel_id_by_city(location) 
    if not hotel_id:
        return jsonify({'error': 'Hotel not found for the selected city.'}), 400

    room_type_ids = get_room_type_ids()  

    room_prices = {} 
    room_discounts = {}  
    total_price_before_discount = Decimal('0.0')  
    room_features = {}
    for room in rooms_to_book:
        room_features[room['RoomID']] = room['RoomTypeFeature']
    session['room_features'] = room_features

    for room_type, count in room_counts.items():
        if count > 0:
            room_type_id = room_type_ids.get(room_type)
            price_per_room, discount_percentage, discounted_price = calculate_room_price(
                session['check_in_date'],
                days_stay,
                hotel_id,
                room_type_id,
                session['guest_count']
            )
            room_prices[room_type] = price_per_room * count 
            room_discounts[room_type] = discounted_price * count  
            total_price_before_discount += room_prices[room_type] 
    session['room_prices'] = room_prices
    total_price_after_discount = sum(room_discounts.values())
    session['total_price_after_discount'] = float(total_price_after_discount)

    total_discount_percentage = (1 - (total_price_after_discount / total_price_before_discount)) * 100 if total_price_before_discount else Decimal('0.0')
    session['total_discount_percentage'] = float(total_discount_percentage)


    return render_template('display_booking.html',
                           room_prices=room_prices,
                           room_discounts=room_discounts,
                           total_price=total_price_after_discount,
                           total_discount_percentage = total_discount_percentage,
                           check_in_date=session['check_in_date'],
                           check_out_date=session['check_out_date'],
                           num_days=session['num_days'],
                           location=session['location'],
                           guest_count=session['guest_count'],
                           standard_room_count=session['standard_room_count'],
                           double_room_count=session['double_room_count'],
                           family_room_count=session['family_room_count'],
                           available_rooms=session.get('available_rooms'),
                           room_ids=session.get('room_ids'),
                           room_features=session.get('room_features')
                           )


@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        if 'user_email' not in session:
            flash('You must be logged in to complete the booking.', 'error')
            return redirect(url_for('LogIn'))

        payment_successful = True
        payment_date = datetime.now()
        card_number = request.form.get('cardnumber')
        if card_number:
            last_four_digits = card_number[-4:]
        else:
            flash('Credit card number is required.', 'error')
            return render_template('payment.html')

        if payment_successful:
            try:
                conn = dbfunc.getConnection()
                if conn and conn.is_connected():
                    dbcursor = conn.cursor()
                    hotel_id = get_hotel_id_by_city(session.get('location'))
                    total_discount_percentage = session.get('total_discount_percentage')
                    total_price_after_discount = session.get('total_price_after_discount')
                    if 'room_prices' not in session:
                        flash('There was an error with your booking. Please try again.', 'error')
                        return redirect(url_for('display_booking'))
                    
                    conn.start_transaction()

                    for room_type, room_ids in session.get('room_ids', {}).items():
                        room_price = session['room_prices'].get(room_type)
                        for room_id in room_ids:
                            booking_data = (
                                session.get('user_id'),
                                session.get('check_in_date'),
                                session.get('check_out_date'),
                                hotel_id,
                                session.get('guest_count'),
                                room_id,
                                total_price_after_discount,
                                total_discount_percentage,
                                'Completed',
                                payment_date,
                                last_four_digits,
                                room_price
                            )
                            insert_query = (
                                'INSERT INTO Booking (UserID, CheckInDate, CheckOutDate, HotelID, TotalPeople, RoomID, TotalPrice, Discount, PaymentStatus, PaymentDate, LastFourDigit, RoomPrice) '
                                'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
                            )
                            dbcursor.execute(insert_query, booking_data)
                            
                            update_query = (
                                'UPDATE Room SET AvailabilityStatus = %s WHERE RoomID = %s'
                            )
                            dbcursor.execute(update_query, ("Yes", room_id))

                    conn.commit()
                    flash('Booking and payment successful!', 'success')
                    return redirect(url_for('ConfirmPage'))
            except Exception as e:
                if conn:
                    conn.rollback()
                flash(f'An error occurred while processing the booking: {e}', 'error')
            finally:
                if conn and conn.is_connected():
                    dbcursor.close()
                    conn.close()
        else:
            flash('Payment failed. Please try again.', 'error')

        return redirect(url_for('ConfirmPage'))
    else:
        return render_template('payment.html')

@app.route('/ConfirmPage')
def ConfirmPage():
    if 'user_id' not in session:
        flash('You must be logged in to view confirmation.', 'error')
        return redirect(url_for('LogIn'))

    user_id = session['user_id']
    conn = None
    try:
        conn = dbfunc.getConnection()
        if conn and conn.is_connected():
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT b.BookingID, b.CheckInDate, b.CheckOutDate, b.TotalPrice, b.RoomPrice, 
                       r.RoomNumber, rt.RoomTypeName, h.City, b.BookingStatus
                FROM Booking b
                JOIN Room r ON b.RoomID = r.RoomID
                JOIN RoomType rt ON r.RoomTypeID = rt.RoomTypeID
                JOIN Hotel h ON r.HotelID = h.HotelID
                WHERE b.UserID = %s AND b.BookingStatus = 'Booked'
                ORDER BY b.BookingID DESC
            """, (user_id,))
            bookings = cursor.fetchall()
            cursor.close()

            if bookings:
                return render_template('ConfirmPage.html', bookings=bookings)
            else:
                flash('No current bookings found for the logged-in user.', 'info')
                return redirect(url_for('index'))
    except Exception as e:
        flash(f'An error occurred while retrieving booking information: {e}', 'error')
        return redirect(url_for('index'))
    finally:
        if conn:
            conn.close()

    return redirect(url_for('index')) 

    

  
@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    booking_id = request.form.get('booking_id', type=int)
    if not booking_id:
        flash('Booking ID not provided', 'error')
        return jsonify({'error': 'Booking ID not provided'}), 400

    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Booking WHERE BookingID = %s AND BookingStatus = 'Booked'", (booking_id,))
        booking = cursor.fetchone()
        if not booking:
            flash('No booking found with the provided ID', 'error')
            return jsonify({'error': 'No booking found with the provided ID'}), 404
        
        cursor.execute('SELECT CheckInDate, TotalPrice, RoomID FROM Booking WHERE BookingID = %s', (booking_id,))
        booking_details = cursor.fetchone()

        check_in_date = booking_details['CheckInDate']
        if isinstance(check_in_date, datetime):
            check_in_date = check_in_date.date()

        cancellation_date = datetime.now().date()
        total_price = booking_details['TotalPrice']
        days_until_booking = (check_in_date - cancellation_date).days

        refunded_fee = calculate_refunded_fee(total_price, days_until_booking)
        refund_percentage = calculate_percentage(days_until_booking)
        payment_status = 'NoRefund' if refund_percentage == 0 else 'Refunded'

        cursor.execute('UPDATE Booking SET BookingStatus = %s, PaymentStatus = %s WHERE BookingID = %s', 
                       ('Cancelled', payment_status, booking_id))

        cursor.execute('UPDATE Room SET AvailabilityStatus = %s WHERE RoomID = %s', 
                       ('No', booking_details['RoomID']))

        cursor.execute('INSERT INTO Cancellation (BookingID, Percentage, CancellationDate, RefundedFee) VALUES (%s, %s, %s, %s)', 
                       (booking_id, refund_percentage, cancellation_date, refunded_fee))

        conn.commit()
        flash('Booking cancelled successfully', 'success')
        return redirect(url_for('showCancelBooking', user_id=booking['UserID']))
    except Exception as e:
        conn.rollback()
        flash(str(e), 'error')
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()
  
      
        
def calculate_percentage(days_until_booking):
    if days_until_booking > 60:
        return 100
    elif days_until_booking > 30:
        return 50
    else:
        return 0

def calculate_refunded_fee(total_price, days_until_booking):
    percentage = calculate_percentage(days_until_booking)
    return (total_price * percentage) / 100

def update_room_availability():
    conn = dbfunc.getConnection()
    if conn is not None and conn.is_connected():
        cursor = conn.cursor()
        try:
            update_query = """
            UPDATE Room
            SET AvailabilityStatus = 'No'
            WHERE RoomID IN (
                SELECT RoomID FROM Booking
                WHERE CheckOutDate < CURDATE() AND AvailabilityStatus = 'Yes'
            )
            """
            cursor.execute(update_query)
            conn.commit()
            print("Updated room availability status.")
        except Exception as e:
            print(f"Failed to update room availability: {e}")
        finally:
            cursor.close()
            conn.close()
            

def update_booking_status():
    today = datetime.now().date()
    conn = dbfunc.getConnection()
    cursor = conn.cursor()
    try:
       
        cursor.execute("""
            UPDATE Booking
            SET BookingStatus = 'Due'
            WHERE CheckInDate < %s AND BookingStatus != 'Due'
        """, (today,))
        conn.commit()
        print(f"Updated bookings to 'Due' where check-in date has passed as of {today}.")
    except Exception as e:
        print(f"Failed to update booking statuses: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

#Hotel
@app.route('/addHotel', methods=['GET', 'POST'])
def addHotel():
    if request.method == 'POST':
        
        address = request.form['address']
        city = request.form['city']
        postcode = request.form['postcode']
        capacity = request.form['capacity']

        conn = dbfunc.getConnection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Hotel (Address, City, PostCode, Capacity) VALUES (%s, %s, %s, %s)",
                       (address, city, postcode, capacity))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Hotel added successfully!', 'success')
        return redirect(url_for('admin'))
    else:
        return render_template('addHotel.html')

@app.route('/updateHotel/<int:hotel_id>', methods=['GET', 'POST'])
def updateHotel(hotel_id):
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        address = request.form['address']
        city = request.form['city']
        postcode = request.form['postcode']
        capacity = request.form['capacity']

        cursor.execute("""
            UPDATE Hotel 
            SET Address = %s, City = %s, PostCode = %s, Capacity = %s 
            WHERE HotelID = %s
            """, (address, city, postcode, capacity, hotel_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Hotel updated successfully!', 'success')
        return redirect(url_for('admin'))
    else:
        cursor.execute("SELECT * FROM Hotel WHERE HotelID = %s", (hotel_id,))
        hotel = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('updateHotel.html', hotel=hotel)

@app.route('/deleteHotel/<int:hotel_id>', methods=['POST'])
def deleteHotel(hotel_id):
    if not session.get('isAdmin', False):
        flash('You do not have permission to delete rooms.', 'error')
        return redirect(url_for('listHotels')) 

    try:
        conn = dbfunc.getConnection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Hotel WHERE HotelID = %s", (hotel_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Hotel deleted successfully!', 'success')
    except Exception as e:
        flash(f'Failed to delete hotel: {e}', 'error')
    finally:
        return redirect(url_for('listHotels'))
    
#Room
@app.route('/addRoom', methods=['GET', 'POST'])
def addRoom():
    if request.method == 'POST':
        room_num = request.form['room_num']
        room_type = request.form['room_type'] 
        hotel_id = request.form['hotel_id']
        availability_status = request.form.get('availability_status', 'No')

        conn = dbfunc.getConnection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Room (RoomNumber , RoomTypeID , HotelID, AvailabilityStatus) VALUES (%s, %s, %s, %s)",
                       (room_num, room_type, hotel_id, availability_status))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Room added successfully!', 'success')
        return redirect(url_for('admin'))
    else:
        conn = dbfunc.getConnection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Hotel")
        hotels = cursor.fetchall()
        cursor.execute("SELECT * FROM RoomType")
        room_types = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('addRoom.html', hotels=hotels, room_types=room_types)

@app.route('/updateRoom/<int:room_id>', methods=['GET', 'POST'])
def updateRoom(room_id):
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        room_num = request.form['room_num']
        room_type_id = request.form['room_type']  
        hotel_id = request.form['hotel_id']
        availability_status = request.form['availability_status']

        cursor.execute("""
            UPDATE Room
            SET RoomNumber = %s, RoomTypeID = %s, HotelID = %s, AvailabilityStatus = %s
            WHERE RoomID = %s
        """, (room_num, room_type_id, hotel_id, availability_status, room_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Room updated successfully!', 'success')
        return redirect(url_for('admin'))
    else:
        cursor.execute("SELECT * FROM Room WHERE RoomID = %s", (room_id,))
        room = cursor.fetchone()

        cursor.execute("SELECT RoomTypeID, RoomTypeName FROM RoomType")
        room_types = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return render_template('updateRoom.html', room=room, room_types=room_types)
    

@app.route('/deleteRoom/<int:room_id>', methods=['POST'])
def deleteRoom(room_id):
    if not session.get('isAdmin', False):
        flash('You do not have permission to delete rooms.', 'error')
        return redirect(url_for('listRooms')) 
    try:
        conn = dbfunc.getConnection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Room WHERE RoomID = %s", (room_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Room deleted successfully!', 'success')
    except Exception as e:
        flash(f'Failed to delete room: {e}', 'error')
    return redirect(url_for('listRooms'))  


@app.route('/updateRoomPrice/<int:hotel_id>/<int:room_type_id>', methods=['GET', 'POST'])
def updateRoomPrice(hotel_id, room_type_id):
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        peak_season_price = request.form['peak_season_price']
        off_peak_season_price = request.form['off_peak_season_price']
        
        cursor.execute("""
            UPDATE Hotel_RoomType 
            SET PeakSeasonPrice = %s, OffPeakSeasonPrice = %s 
            WHERE HotelID = %s AND RoomTypeID = %s
            """, (peak_season_price, off_peak_season_price, hotel_id, room_type_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Room prices updated successfully!', 'success')
        return redirect(url_for('admin'))
    else:
        cursor.execute("SELECT * FROM Hotel_RoomType WHERE HotelID = %s AND RoomTypeID = %s", (hotel_id, room_type_id))
        room_price = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('updateRoomPrice.html', room_price=room_price, hotel_id=hotel_id, room_type_id=room_type_id)


@app.route('/listHotels')
def listHotels():
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Hotel")
    hotels = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('listHotels.html', hotels=hotels)

@app.route('/listRooms')
def listRooms():
    room_id_query = request.args.get('room_id')
    room_number_query = request.args.get('room_number')
    hotel_id_query = request.args.get('hotel_id')
    availability_query = request.args.get('availability')
    room_type_query = request.args.get('room_type')

    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)

    base_query = """
        SELECT Room.RoomID, Room.RoomNumber, RoomType.RoomTypeName, Hotel.HotelID, Room.AvailabilityStatus
        FROM Room
        INNER JOIN RoomType ON Room.RoomTypeID = RoomType.RoomTypeID
        INNER JOIN Hotel ON Room.HotelID = Hotel.HotelID
    """
    
    filters = []
    params = []
    
    if room_id_query:
        filters.append("Room.RoomID LIKE %s")
        params.append(f"%{room_id_query}%")
    if room_number_query:
        filters.append("Room.RoomNumber LIKE %s")
        params.append(f"%{room_number_query}%")
    if hotel_id_query:
        filters.append("Hotel.HotelID LIKE %s")
        params.append(f"%{hotel_id_query}%")
    if availability_query:
        filters.append("Room.AvailabilityStatus LIKE %s")
        params.append(f"%{availability_query}%")
    if room_type_query:
        filters.append("RoomType.RoomTypeName LIKE %s")
        params.append(f"%{room_type_query}%")

    if filters:
        base_query += " WHERE " + " AND ".join(filters)

    cursor.execute(base_query, tuple(params))
    rooms = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('listRooms.html', rooms=rooms)

@app.route('/listRoomPrices')
def listRoomPrices():
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT Hotel_RoomType.HotelID, Hotel_RoomType.RoomTypeID, Hotel_RoomType.PeakSeasonPrice, 
               Hotel_RoomType.OffPeakSeasonPrice, Hotel.Address, RoomType.RoomTypeName 
        FROM Hotel_RoomType
        JOIN Hotel ON Hotel_RoomType.HotelID = Hotel.HotelID
        JOIN RoomType ON Hotel_RoomType.RoomTypeID = RoomType.RoomTypeID
    """)
    room_prices = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('listRoomPrices.html', room_prices=room_prices)


@app.route('/cancelledBookings')
def cancelledBookings():
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM Booking 
        INNER JOIN Cancellation ON Booking.BookingID = Cancellation.BookingID
        WHERE Booking.BookingStatus = 'Cancelled'
    """)
    cancelled_bookings = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('cancelledBookings.html', cancelled_bookings=cancelled_bookings)

#User
@app.route('/listUserDetails')
def listUserDetails():
    user_id = request.args.get('user_id')
    email = request.args.get('email')
    last_name = request.args.get('last_name')

    query = """
        SELECT User.UserID, User.FirstName, User.LastName, User.Email, GROUP_CONCAT(Booking.BookingID) AS BookingIDs
        FROM User
        LEFT JOIN Booking ON User.UserID = Booking.UserID
    """

    conditions = []
    params = []

    if user_id:
        conditions.append("User.UserID = %s")
        params.append(user_id)
    if email:
        conditions.append("User.Email = %s")
        params.append(email)
    if last_name:
        conditions.append("User.LastName = %s")
        params.append(last_name)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " GROUP BY User.UserID, User.FirstName, User.LastName, User.Email"

    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params)
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('listUserDetails.html', users=users)


@app.route('/updateUserDetails/<int:user_id>', methods=['GET', 'POST'])
def updateUserDetails(user_id):
    if 'isAdmin' in session and session['isAdmin']:
        conn = dbfunc.getConnection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')

            cursor.execute("""
                UPDATE User SET FirstName = %s, LastName = %s, Email = %s 
                WHERE UserID = %s
            """, (first_name, last_name, email, user_id))
            conn.commit()
            flash('User details updated successfully!', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('listUserDetails'))

        cursor.execute("SELECT UserID, FirstName, LastName, Email FROM User WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('updateUserDetails.html', user=user)
    else:
        flash('You must be an admin to access this page.', 'error')
        return redirect(url_for('index'))
    

@app.route('/updatePassword/<int:user_id>', methods=['GET', 'POST'])
def updatePassword(user_id):
    if 'isAdmin' in session and session['isAdmin']:
        conn = dbfunc.getConnection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            new_password = request.form.get('new_password')
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')

            cursor.execute('UPDATE User SET Password = %s WHERE UserID = %s', (hashed_password, user_id))
            if cursor.rowcount == 0:
                flash('No user found with the given information.', 'error')
            else:
                conn.commit()
                flash('Password updated successfully!', 'success')
            cursor.close()
            conn.close()
            return redirect(url_for('listUserDetails'))

        cursor.execute("SELECT UserID, FirstName, LastName, Email FROM User WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template('updatePassword.html', user = user)
    else:
        flash('You must be an admin to access this page.', 'error')
        return redirect(url_for('index'))


@app.route('/deleteUser/<int:user_id>', methods=['POST'])
def deleteUser(user_id):
    if not session.get('isAdmin', False):
            flash('You do not have permission to delete rooms.', 'error')
            return redirect(url_for('listUserDetails')) 

    try:
        conn = dbfunc.getConnection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM User WHERE UserID = %s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        flash(f'Failed to delete User: {e}', 'error')
    finally:
        return redirect(url_for('listUserDetails'))
    
@app.route('/showCancelBooking')
def showCancelBooking():
    user_id = request.args.get('user_id', type=int)
    booking_id = request.args.get('booking_id', type=int)
    
    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)
    
    if booking_id:
        cursor.execute("""
            SELECT Booking.BookingID, Booking.CheckInDate, Booking.CheckOutDate, Booking.TotalPrice, Booking.RoomPrice, Hotel.City AS Location, Room.RoomNumber
            FROM Booking
            INNER JOIN Hotel ON Booking.HotelID = Hotel.HotelID
            INNER JOIN Room ON Booking.RoomID = Room.RoomID
            WHERE Booking.BookingID = %s AND Booking.BookingStatus = 'Booked'
        """, (booking_id,))
        booking = cursor.fetchone()
        cursor.close()
        conn.close()
        if booking:
            return render_template('cancelBooking.html', booking=booking)
        else:
            flash("Booking not found or already processed.", "error")
    elif user_id:
        cursor.execute("""
            SELECT Booking.BookingID, Booking.CheckInDate, Booking.CheckOutDate, Booking.TotalPrice, Booking.RoomPrice, Hotel.City AS Location, Room.RoomNumber
            FROM Booking
            INNER JOIN Hotel ON Booking.HotelID = Hotel.HotelID
            INNER JOIN Room ON Booking.RoomID = Room.RoomID
            WHERE Booking.UserID = %s AND Booking.BookingStatus = 'Booked'
        """, (user_id,))
        bookings = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('cancelBookingsList.html', bookings=bookings, user_id=user_id)
    
    flash("No valid parameters provided.", "error")
    return redirect(url_for('Profile'))
    
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_room_availability, trigger='cron', hour=1, id='update_room_availability')
scheduler.add_job(func=update_booking_status, trigger='cron', hour=1, id='update_booking_status')

@app.route('/userUpdateDetails', methods=['GET', 'POST'])
def userUpdateDetails():
    user_id = session.get('user_id')  
    if not user_id:
        flash("You must be logged in to update your details.", "error")
        return redirect(url_for('LogIn'))

    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        try:
            cursor.execute("""
                UPDATE User SET FirstName = %s, LastName = %s
                WHERE UserID = %s
            """, (first_name, last_name, user_id))
            conn.commit()
            flash('Your details were successfully updated!', 'success')
        except Exception as e:
            conn.rollback()
            flash(f"Failed to update details: {str(e)}", "error")
        finally:
            cursor.close()
            conn.close()
            return redirect(url_for('Profile'))  

    cursor.execute("SELECT UserID, FirstName, LastName FROM User WHERE UserID = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('UserupdateUserDetails.html', user=user)

@app.route('/userUpdatePassword', methods=['GET', 'POST'])
def userUpdatePassword():
    user_id = session.get('user_id')
    if not user_id:
        flash("You must be logged in to update your password.", "error")
        return redirect(url_for('LogIn'))

    conn = dbfunc.getConnection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')

        cursor.execute("SELECT Password FROM User WHERE UserID = %s", (user_id,))
        user_data = cursor.fetchone()

        if user_data and check_password_hash(user_data['Password'], old_password):
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
            try:
                cursor.execute("UPDATE User SET Password = %s WHERE UserID = %s", (hashed_password, user_id))
                conn.commit()
                flash('Your password has been updated successfully!', 'success')
            except Exception as e:
                conn.rollback()
                flash(f"Failed to update password: {str(e)}", "error")
        else:
            flash("The old password you entered is incorrect.", "error")

        cursor.close()
        conn.close()
        return redirect(url_for('Profile')) 

    return render_template('UserupdateUserPassword.html', user_id=user_id)

@app.route('/Profile')
def Profile():
    user_id = session.get('user_id')  
    if not user_id:
        flash('You are not logged in.', 'error')
        return redirect(url_for('LogIn'))

    conn = dbfunc.getConnection()
    if conn is None or not conn.is_connected():
        flash('Failed to connect to the database.', 'error')
        return redirect(url_for('index'))

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT UserID, FirstName, LastName, Email FROM User WHERE UserID = %s", (user_id,))
        user = cursor.fetchone()
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('index'))

        cursor.execute("SELECT * FROM Booking WHERE UserID = %s AND BookingStatus = 'Booked'", (user_id,))
        bookings = cursor.fetchall()

        return render_template('Profile.html', user=user, bookings=bookings)
    except Exception as e:
        flash(f'An error occurred: {e}', 'error')
        return redirect(url_for('index'))
    finally:
        cursor.close()
        conn.close()
        
        
if __name__ == '__main__':
      app.run(debug=True)
      
