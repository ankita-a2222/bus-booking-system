// Initialize the database with sample data
async function initializeDatabase() {
    try {
        const response = await fetch('/api/init-db', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            console.log('Database initialized successfully');
        } else {
            console.error('Failed to initialize database');
        }
    } catch (error) {
        console.error('Error initializing database:', error);
    }
}

// Call initializeDatabase on appropriate pages
document.addEventListener('DOMContentLoaded', function() {
    // Run initialization only on the homepage
    if (window.location.pathname === '/' || window.location.pathname === '/index') {
        initializeDatabase();
    }
    
    // Handle search form
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            const from = document.getElementById('from').value;
            const to = document.getElementById('to').value;
            const date = document.getElementById('date').value;
            
            // Store search details
            sessionStorage.setItem('from', from);
            sessionStorage.setItem('to', to);
            sessionStorage.setItem('date', date);
            
            // Redirect to search results
            window.location.href = '/search';
        });
    }
    
    // Handle search results page
    if (window.location.pathname === '/search') {
        displaySearchResults();
    }
    
    // Handle seats page
    if (window.location.pathname === '/seats') {
        loadSeats();
    }
    
    // Handle booking page
    if (window.location.pathname === '/booking') {
        displayBookingInfo();
    }
    
    // Handle payment page
    if (window.location.pathname === '/payment') {
        displayPaymentInfo();
    }
    
    // Handle confirmation page
    if (window.location.pathname === '/confirmation') {
        displayConfirmationInfo();
    }
});

// Functions for search results page
async function displaySearchResults() {
    const from = sessionStorage.getItem('from');
    const to = sessionStorage.getItem('to');
    const date = sessionStorage.getItem('date');
    
    // Display the route info
    const routeInfoElement = document.getElementById('route');
    if (routeInfoElement) {
        routeInfoElement.innerText = `Showing buses from ${from} to ${to} on ${date}`;
    }
    
    try {
        // Show loading indicator
        const busListDiv = document.getElementById('busList');
        if (busListDiv) {
            busListDiv.innerHTML = '<div class="loader"></div>';
        }
        
        // Fetch available buses
        const response = await fetch(`/api/buses/search?from=${from}&to=${to}&date=${date}`);
        const data = await response.json();
        
        if (busListDiv) {
            // Clear loading indicator
            busListDiv.innerHTML = '';
            
            if (data.buses && data.buses.length > 0) {
                // Display bus details
                data.buses.forEach(bus => {
                    const busItem = document.createElement('div');
                    busItem.classList.add('bus-item');
                    busItem.innerHTML = `
                        <h3>${bus.name}</h3>
                        <p>Time: ${bus.time}</p>
                        <p>Price: ₹${bus.price}</p>
                        <button onclick="selectBus(${bus.id}, '${bus.name}', ${bus.price})">Select Seats</button>
                    `;
                    busListDiv.appendChild(busItem);
                });
            } else {
                // No buses found
                busListDiv.innerHTML = '<p>No buses found for this route and date.</p>';
            }
        }
    } catch (error) {
        console.error('Error fetching buses:', error);
        // Display error message
        if (busListDiv) {
            busListDiv.innerHTML = '<p class="error-message">Failed to load buses. Please try again.</p>';
        }
    }
}

// Function to handle bus selection
function selectBus(id, name, price) {
    // Store selected bus details
    sessionStorage.setItem('selectedBus', JSON.stringify({ id, name, price }));
    // Redirect to seats page
    window.location.href = '/seats';
}

// Functions for seat selection page
async function loadSeats() {
    const selectedBus = JSON.parse(sessionStorage.getItem('selectedBus'));
    const busInfoElement = document.getElementById('busInfo');
    const seatsContainer = document.getElementById('seatsContainer');
    
    if (busInfoElement && selectedBus) {
        busInfoElement.innerText = `Bus: ${selectedBus.name} | Price per seat: ₹${selectedBus.price}`;
    }
    
    if (seatsContainer) {
        // Show loading indicator
        seatsContainer.innerHTML = '<div class="loader"></div>';
        
        try {
            // Fetch seats for the selected route
            const response = await fetch(`/api/seats/${selectedBus.id}`);
            const data = await response.json();
            
            // Clear loading indicator
            seatsContainer.innerHTML = '';
            
            // Create seats dynamically
            data.seats.forEach(seat => {
                const seatElement = document.createElement('div');
                seatElement.classList.add('seat');
                if (!seat.is_available) {
                    seatElement.classList.add('booked');
                }
                seatElement.innerText = seat.seat_number;
                seatElement.setAttribute('data-seat-id', seat.id);
                seatElement.setAttribute('data-seat-number', seat.seat_number);
                
                // Add click handler for available seats
                if (seat.is_available) {
                    seatElement.onclick = function() { toggleSeat(seat.id, seat.seat_number, seatElement); };
                }
                
                seatsContainer.appendChild(seatElement);
            });
            
            // Update the price based on the API data
            sessionStorage.setItem('seatPrice', data.price);
        } catch (error) {
            console.error('Error loading seats:', error);
            seatsContainer.innerHTML = '<p class="error-message">Failed to load seats. Please try again.</p>';
        }
    }
}

let selectedSeats = [];
let totalPrice = 0;

function toggleSeat(seatId, seatNumber, seatElement) {
    // Find if we already have this seat
    const seatIndex = selectedSeats.findIndex(seat => seat.id === seatId);
    
    if (seatIndex !== -1) {
        // Seat is already selected, deselect it
        selectedSeats.splice(seatIndex, 1);
        seatElement.classList.remove('selected');
    } else {
        // Select the seat
        selectedSeats.push({ id: seatId, number: seatNumber });
        seatElement.classList.add('selected');
    }
    
    // Update seat info and total price
    const seatPrice = parseFloat(sessionStorage.getItem('seatPrice') || '0');
    totalPrice = selectedSeats.length * seatPrice;
    
    // Update the UI
    const selectedSeatsElement = document.getElementById('selectedSeats');
    const totalPriceElement = document.getElementById('totalPrice');
    const proceedButton = document.getElementById('proceedButton');
    
    if (selectedSeatsElement) {
        selectedSeatsElement.innerText = selectedSeats.length ? selectedSeats.map(seat => seat.number).join(', ') : 'None';
    }
    
    if (totalPriceElement) {
        totalPriceElement.innerText = totalPrice;
    }
    
    if (proceedButton) {
        proceedButton.disabled = selectedSeats.length === 0;
    }
    
    // Store the selected seats and total price
    sessionStorage.setItem('selectedSeats', JSON.stringify(selectedSeats));
    sessionStorage.setItem('totalPrice', totalPrice);
}

// Add event listener for the proceed button
document.addEventListener('DOMContentLoaded', function() {
    const proceedButton = document.getElementById('proceedButton');
    if (proceedButton) {
        proceedButton.addEventListener('click', function() {
            // Redirect to booking page
            window.location.href = '/booking';
        });
    }
});

// Functions for booking page
function displayBookingInfo() {
    const selectedSeats = JSON.parse(sessionStorage.getItem('selectedSeats') || '[]');
    const totalPrice = sessionStorage.getItem('totalPrice');
    const selectedBus = JSON.parse(sessionStorage.getItem('selectedBus'));
    
    // Display booking info
    const bookingInfoElement = document.getElementById('bookingInfo');
    if (bookingInfoElement && selectedSeats.length > 0) {
        const seatNumbers = selectedSeats.map(seat => seat.number).join(', ');
        bookingInfoElement.innerText = `Seats: ${seatNumbers} | Total Price: ₹${totalPrice}`;
    }
    
    // Handle passenger form submission
    const passengerForm = document.getElementById('passengerForm');
    if (passengerForm) {
        passengerForm.addEventListener('submit', async function(event) {
            event.preventDefault();
            
            // Get passenger details
            const name = document.getElementById('name').value;
            const age = document.getElementById('age').value;
            const email = document.getElementById('email').value;
            const phone = document.getElementById('phone').value;
            
            // Create booking data
            const bookingData = {
                route_id: selectedBus.id,
                seat_numbers: selectedSeats.map(seat => seat.number),
                passenger: {
                    name: name,
                    age: parseInt(age),
                    email: email,
                    phone: phone
                }
            };
            
            try {
                // Show loading state
                const submitButton = passengerForm.querySelector('button[type="submit"]');
                submitButton.disabled = true;
                submitButton.innerText = 'Processing...';
                
                // Send booking request
                const response = await fetch('/api/bookings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(bookingData)
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    // Store booking details
                    sessionStorage.setItem('bookingIds', JSON.stringify(data.booking_ids));
                    sessionStorage.setItem('passengerId', data.passenger_id);
                    
                    // Store passenger details for the payment page
                    sessionStorage.setItem('passengerDetails', JSON.stringify({
                        name: name,
                        age: age,
                        email: email,
                        phone: phone
                    }));
                    
                    // Redirect to payment page
                    window.location.href = '/payment';
                } else {
                    // Show error message
                    alert(`Booking failed: ${data.error}`);
                }
            } catch (error) {
                console.error('Error creating booking:', error);
                alert('Failed to create booking. Please try again.');
            } finally {
                // Reset button state
                submitButton.disabled = false;
                submitButton.innerText = 'Proceed to Payment';
            }
        });
    }
}

// Functions for payment page
function displayPaymentInfo() {
    const totalPrice = sessionStorage.getItem('totalPrice');
    const passengerDetails = JSON.parse(sessionStorage.getItem('passengerDetails'));
    
    // Display payment info
    const paymentInfoElement = document.getElementById('paymentInfo');
    if (paymentInfoElement && passengerDetails) {
        paymentInfoElement.innerText = `Passenger: ${passengerDetails.name} | Total Amount: ₹${totalPrice}`;
    }
    
    // Handle payment method change
    const paymentMethodSelect = document.getElementById('paymentMethod');
    if (paymentMethodSelect) {
        paymentMethodSelect.addEventListener('change', function() {
            const method = this.value;
            const cardDetails = document.getElementById('cardDetails');
            if (cardDetails) {
                cardDetails.style.display = (method === 'card') ? 'block' : 'none';
            }
        });
    }
    
    // Handle payment form submission
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', function(event) {
            event.preventDefault();
            
            // Create mock confirmation data since this is a demo
            const mockConfirmation = {
                booking_ids: JSON.parse(sessionStorage.getItem('bookingIds')),
                passenger: JSON.parse(sessionStorage.getItem('passengerDetails')),
                route: {
                    from_location: sessionStorage.getItem('from'),
                    to_location: sessionStorage.getItem('to'),
                    date: sessionStorage.getItem('date'),
                    departure_time: "08:00", // Mock time
                    bus_name: JSON.parse(sessionStorage.getItem('selectedBus')).name
                },
                seat_numbers: JSON.parse(sessionStorage.getItem('selectedSeats')).map(seat => seat.number),
                total_price: sessionStorage.getItem('totalPrice'),
                payment_method: document.getElementById('paymentMethod').value,
                payment_status: "Paid",
                booking_date: new Date().toISOString().slice(0, 19).replace('T', ' ')
            };
            
            // Store confirmation data
            sessionStorage.setItem('confirmation', JSON.stringify(mockConfirmation));
            
            // Redirect to confirmation page without alert
            window.location.href = '/confirmation';
        });
    }
}

// Functions for confirmation page
function displayConfirmationInfo() {
    const confirmation = JSON.parse(sessionStorage.getItem('confirmation'));
    
    // Display ticket details
    const ticketDetailsElement = document.getElementById('ticketDetails');
    if (ticketDetailsElement && confirmation) {
        ticketDetailsElement.innerHTML = `
            <p><strong>Name:</strong> ${confirmation.passenger.name}</p>
            <p><strong>Email:</strong> ${confirmation.passenger.email}</p>
            <p><strong>Phone:</strong> ${confirmation.passenger.phone}</p>
            <p><strong>Bus:</strong> ${confirmation.route.bus_name}</p>
            <p><strong>Route:</strong> ${confirmation.route.from_location} to ${confirmation.route.to_location}</p>
            <p><strong>Date:</strong> ${confirmation.route.date}</p>
            <p><strong>Time:</strong> ${confirmation.route.departure_time}</p>
            <p><strong>Seats:</strong> ${confirmation.seat_numbers.join(', ')}</p>
            <p><strong>Total Amount Paid:</strong> ₹${confirmation.total_price}</p>
            <p><strong>Payment Method:</strong> ${confirmation.payment_method}</p>
            <p><strong>Booking Date:</strong> ${confirmation.booking_date}</p>
        `;
    }
    
    // Handle download ticket button
    const downloadTicketButton = document.getElementById('downloadTicket');
    if (downloadTicketButton && ticketDetailsElement) {
        downloadTicketButton.addEventListener('click', function() {
            const ticketContent = ticketDetailsElement.innerText;
            const ticketBlob = new Blob([ticketContent], { type: 'text/plain' });
            const ticketURL = URL.createObjectURL(ticketBlob);
            const a = document.createElement('a');
            a.href = ticketURL;
            a.download = 'Bus_Ticket.txt';
            a.click();
        });
    }
}
