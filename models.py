import datetime
from app import db

# Bus Model
class Bus(db.Model):
    __tablename__ = 'buses'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    routes = db.relationship('Route', backref='bus', lazy=True)
    seats = db.relationship('Seat', backref='bus', lazy=True)
    
    def __repr__(self):
        return f'<Bus {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'capacity': self.capacity
        }

# Route Model
class Route(db.Model):
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    from_location = db.Column(db.String(100), nullable=False)
    to_location = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Foreign Key
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='route', lazy=True)
    
    def __repr__(self):
        return f'<Route {self.from_location} to {self.to_location}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'from_location': self.from_location,
            'to_location': self.to_location,
            'departure_time': self.departure_time,
            'price': self.price,
            'date': self.date.strftime('%Y-%m-%d'),
            'bus_id': self.bus_id,
            'bus_name': self.bus.name if self.bus else None
        }

# Seat Model
class Seat(db.Model):
    __tablename__ = 'seats'
    
    id = db.Column(db.Integer, primary_key=True)
    seat_number = db.Column(db.Integer, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)
    
    # Foreign Keys
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='seat', lazy=True)
    
    def __repr__(self):
        return f'<Seat {self.seat_number} on Bus {self.bus_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'seat_number': self.seat_number,
            'is_available': self.is_available,
            'bus_id': self.bus_id
        }

# Passenger Model
class Passenger(db.Model):
    __tablename__ = 'passengers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='passenger', lazy=True)
    
    def __repr__(self):
        return f'<Passenger {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'email': self.email,
            'phone': self.phone
        }

# Booking Model
class Booking(db.Model):
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    total_price = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='Pending')
    
    # Foreign Keys
    passenger_id = db.Column(db.Integer, db.ForeignKey('passengers.id'), nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=False)
    
    def __repr__(self):
        return f'<Booking {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'booking_date': self.booking_date.strftime('%Y-%m-%d %H:%M:%S'),
            'total_price': self.total_price,
            'payment_status': self.payment_status,
            'passenger_id': self.passenger_id,
            'route_id': self.route_id,
            'seat_id': self.seat_id,
            'passenger': self.passenger.to_dict() if self.passenger else None,
            'route': self.route.to_dict() if self.route else None,
            'seat': self.seat.to_dict() if self.seat else None
        }
