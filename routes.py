import json
import logging
from datetime import datetime
from flask import jsonify, request, render_template, redirect, url_for, flash
from sqlalchemy.exc import SQLAlchemyError
from app import app, db
from models import Bus, Route, Seat, Booking, Passenger

# Home route
@app.route('/')
def home():
    return render_template('homepage.html')

# Render templates routes
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/search')
def search_page():
    return render_template('search.html')

@app.route('/seats')
def seats_page():
    return render_template('seats.html')

@app.route('/booking')
def booking_page():
    return render_template('booking.html')

@app.route('/payment')
def payment_page():
    return render_template('payment.html')

@app.route('/confirmation')
def confirmation_page():
    return render_template('confirmation.html')

# Initialize database with sample data
@app.route('/api/init-db', methods=['POST'])
def init_db():
    try:
        # Clear existing data
        Booking.query.delete()
        Passenger.query.delete()
        Seat.query.delete()
        Route.query.delete()
        Bus.query.delete()
        db.session.commit()  # Commit the deletions
        
        # Create buses
        bus1 = Bus(name="Orange Travels", capacity=40)
        bus2 = Bus(name="Red Bus Express", capacity=40)
        bus3 = Bus(name="Green Line", capacity=40)
        
        db.session.add_all([bus1, bus2, bus3])
        db.session.commit()  # Commit to get bus IDs
        
        # Fetch the created buses to get their IDs
        buses = Bus.query.all()
        bus_id_1 = buses[0].id
        bus_id_2 = buses[1].id
        bus_id_3 = buses[2].id
        
        # Create routes for today and next few days
        today = datetime.now().date()
        
        # Sample routes with different cities using actual bus IDs
        routes_data = [
            # Delhi to Mumbai
            {"from_location": "Delhi", "to_location": "Mumbai", "departure_time": "08:00", "price": 500, "bus_id": bus_id_1},
            {"from_location": "Delhi", "to_location": "Mumbai", "departure_time": "10:00", "price": 650, "bus_id": bus_id_2},
            {"from_location": "Delhi", "to_location": "Mumbai", "departure_time": "14:00", "price": 700, "bus_id": bus_id_3},
            
            # Mumbai to Bangalore
            {"from_location": "Mumbai", "to_location": "Bangalore", "departure_time": "09:00", "price": 600, "bus_id": bus_id_1},
            {"from_location": "Mumbai", "to_location": "Bangalore", "departure_time": "11:00", "price": 750, "bus_id": bus_id_2},
            
            # Bangalore to Chennai
            {"from_location": "Bangalore", "to_location": "Chennai", "departure_time": "08:30", "price": 450, "bus_id": bus_id_3},
            {"from_location": "Bangalore", "to_location": "Chennai", "departure_time": "12:30", "price": 550, "bus_id": bus_id_1},
            
            # Chennai to Hyderabad
            {"from_location": "Chennai", "to_location": "Hyderabad", "departure_time": "07:00", "price": 550, "bus_id": bus_id_2},
            {"from_location": "Chennai", "to_location": "Hyderabad", "departure_time": "15:00", "price": 650, "bus_id": bus_id_3},
            
            # Hyderabad to Delhi
            {"from_location": "Hyderabad", "to_location": "Delhi", "departure_time": "19:00", "price": 800, "bus_id": bus_id_1},
            {"from_location": "Hyderabad", "to_location": "Delhi", "departure_time": "21:00", "price": 950, "bus_id": bus_id_2}
        ]
        
        routes = []
        for i in range(7):  # Create routes for the next 7 days
            for route_data in routes_data:
                # Calculate the date by adding days to today's date
                day_to_add = i
                route_date = today
                try:
                    route_date = today.replace(day=today.day + day_to_add)
                except ValueError:
                    # Handle month overflow (e.g., April 30 + 1 day)
                    if today.month == 12:
                        route_date = today.replace(year=today.year + 1, month=1, day=day_to_add)
                    else:
                        route_date = today.replace(month=today.month + 1, day=day_to_add)
                
                route = Route(
                    from_location=route_data["from_location"],
                    to_location=route_data["to_location"],
                    departure_time=route_data["departure_time"],
                    price=route_data["price"],
                    date=route_date,
                    bus_id=route_data["bus_id"]
                )
                routes.append(route)
        
        db.session.add_all(routes)
        db.session.commit()
        
        # Create seats for each bus
        for bus in Bus.query.all():
            seats = []
            for i in range(1, bus.capacity + 1):
                seat = Seat(seat_number=i, bus_id=bus.id, is_available=True)
                seats.append(seat)
            db.session.add_all(seats)
        
        db.session.commit()
        
        return jsonify({"message": "Database initialized successfully"}), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database initialization error: {str(e)}")
        return jsonify({"error": "Database initialization failed", "details": str(e)}), 500

# API Routes
@app.route('/api/buses/search', methods=['GET'])
def search_buses():
    try:
        from_location = request.args.get('from')
        to_location = request.args.get('to')
        date_str = request.args.get('date')
        
        if not all([from_location, to_location, date_str]):
            return jsonify({"error": "Missing required parameters"}), 400
        
        try:
            search_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Get all routes between the specified locations, ignoring date
        routes = Route.query.filter_by(
            from_location=from_location,
            to_location=to_location
        ).all()
        
        # If no routes found, return empty result
        if not routes:
            return jsonify({"message": "No buses found for this route", "buses": []}), 200
        
        # Get unique bus/departure_time combinations
        unique_routes = {}
        for route in routes:
            # Use a combination of bus_id and departure_time as a unique key
            key = f"{route.bus_id}_{route.departure_time}"
            # Keep only one route per unique key
            if key not in unique_routes:
                unique_routes[key] = route
        
        # Create the output list using the unique routes
        buses = []
        for route in unique_routes.values():
            bus = Bus.query.get(route.bus_id)
            buses.append({
                "id": route.id,  # Using route ID as the unique identifier
                "name": bus.name,
                "price": route.price,
                "time": route.departure_time,
                "from": route.from_location,
                "to": route.to_location,
                "date": search_date.strftime('%Y-%m-%d')  # Use the searched date
            })
        
        return jsonify({"buses": buses}), 200
    
    except SQLAlchemyError as e:
        logging.error(f"Database error in search_buses: {str(e)}")
        return jsonify({"error": "Failed to search buses", "details": str(e)}), 500
    except Exception as e:
        logging.error(f"Unexpected error in search_buses: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@app.route('/api/seats/<int:route_id>', methods=['GET'])
def get_seats(route_id):
    try:
        route = Route.query.get_or_404(route_id)
        bus = Bus.query.get_or_404(route.bus_id)
        
        # Get all seats for this bus
        seats = Seat.query.filter_by(bus_id=bus.id).all()
        
        # Check which seats are already booked for this route
        booked_seats = []
        for seat in seats:
            # Check if this seat is booked for this route
            booking = Booking.query.filter_by(route_id=route_id, seat_id=seat.id).first()
            if booking:
                booked_seats.append(seat.seat_number)
        
        seat_info = []
        for seat in seats:
            seat_info.append({
                "id": seat.id,
                "seat_number": seat.seat_number,
                "is_available": seat.seat_number not in booked_seats
            })
        
        return jsonify({
            "route_id": route_id,
            "bus_name": bus.name,
            "price": route.price,
            "seats": seat_info
        }), 200
    
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_seats: {str(e)}")
        return jsonify({"error": "Failed to get seats", "details": str(e)}), 500

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    try:
        data = request.json
        
        # Validate input data
        if not all([
            data.get('route_id'), 
            data.get('seat_numbers'), 
            data.get('passenger')
        ]):
            return jsonify({"error": "Missing required data"}), 400
        
        route_id = data['route_id']
        seat_numbers = data['seat_numbers']
        passenger_data = data['passenger']
        
        # Validate passenger data
        if not all([
            passenger_data.get('name'),
            passenger_data.get('age'),
            passenger_data.get('email'),
            passenger_data.get('phone')
        ]):
            return jsonify({"error": "Incomplete passenger details"}), 400
        
        # Get route and validate
        route = Route.query.get_or_404(route_id)
        
        # Check if required seats are available
        bus = Bus.query.get(route.bus_id)
        seats = []
        unavailable_seats = []
        
        for seat_number in seat_numbers:
            seat = Seat.query.filter_by(bus_id=bus.id, seat_number=seat_number).first()
            if not seat:
                return jsonify({"error": f"Seat {seat_number} not found"}), 404
            
            # Check if seat is already booked for this route
            booking = Booking.query.filter_by(route_id=route_id, seat_id=seat.id).first()
            if booking:
                unavailable_seats.append(seat_number)
            else:
                seats.append(seat)
        
        if unavailable_seats:
            return jsonify({
                "error": "Some seats are not available",
                "unavailable_seats": unavailable_seats
            }), 409
        
        # Create passenger
        passenger = Passenger(
            name=passenger_data['name'],
            age=passenger_data['age'],
            email=passenger_data['email'],
            phone=passenger_data['phone']
        )
        db.session.add(passenger)
        db.session.flush()  # Get the passenger ID
        
        # Calculate total price
        total_price = route.price * len(seats)
        
        # Create bookings for each seat
        bookings = []
        for seat in seats:
            booking = Booking(
                passenger_id=passenger.id,
                route_id=route_id,
                seat_id=seat.id,
                total_price=route.price,  # Price per seat
                payment_status="Pending"
            )
            bookings.append(booking)
        
        db.session.add_all(bookings)
        db.session.commit()
        
        booking_ids = [booking.id for booking in bookings]
        
        return jsonify({
            "message": "Booking created successfully",
            "booking_ids": booking_ids,
            "passenger_id": passenger.id,
            "total_price": total_price
        }), 201
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error in create_booking: {str(e)}")
        return jsonify({"error": "Failed to create booking", "details": str(e)}), 500

@app.route('/api/payment', methods=['POST'])
def process_payment():
    try:
        data = request.json
        
        # Validate input
        if not all([data.get('booking_ids'), data.get('payment_method')]):
            return jsonify({"error": "Missing booking IDs or payment method"}), 400
        
        booking_ids = data['booking_ids']
        payment_method = data['payment_method']
        
        # Update booking status
        for booking_id in booking_ids:
            booking = Booking.query.get_or_404(booking_id)
            booking.payment_status = "Paid"
        
        db.session.commit()
        
        # Get first booking to get passenger and route details
        first_booking = Booking.query.get(booking_ids[0])
        passenger = Passenger.query.get(first_booking.passenger_id)
        route = Route.query.get(first_booking.route_id)
        
        # Get all seats for this booking
        seat_numbers = []
        total_price = 0
        for booking_id in booking_ids:
            booking = Booking.query.get(booking_id)
            seat = Seat.query.get(booking.seat_id)
            seat_numbers.append(seat.seat_number)
            total_price += booking.total_price
        
        # Create confirmation data
        confirmation = {
            "booking_ids": booking_ids,
            "passenger": passenger.to_dict(),
            "route": route.to_dict(),
            "seat_numbers": seat_numbers,
            "total_price": total_price,
            "payment_method": payment_method,
            "payment_status": "Paid",
            "booking_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify({
            "message": "Payment processed successfully",
            "confirmation": confirmation
        }), 200
    
    except SQLAlchemyError as e:
        db.session.rollback()
        logging.error(f"Database error in process_payment: {str(e)}")
        return jsonify({"error": "Failed to process payment", "details": str(e)}), 500

@app.route('/api/booking/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    try:
        booking = Booking.query.get_or_404(booking_id)
        
        return jsonify({
            "booking": booking.to_dict()
        }), 200
    
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_booking: {str(e)}")
        return jsonify({"error": "Failed to get booking", "details": str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Server error"}), 500
