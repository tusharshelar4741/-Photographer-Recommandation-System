# Shotgear version 8
import pickle
import secrets

import pandas as pd
import pymysql
from flask import Flask, render_template, request, session
from flask import jsonify
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
from sqlalchemy import ForeignKey

pymysql.install_as_MySQLdb()

app = Flask(__name__)

secret_key = secrets.token_hex(16)  # Generates a 32-character hexadecimal string (16 bytes)

# Set the secret key in your Flask application
app.secret_key = secret_key

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# model = joblib.load('photographer_recommendation_model.pkl')
with open('photographer_recommendation_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Load dataset
data = pd.read_csv('photography.csv')

# Preprocess data
label_encoder = LabelEncoder()
data['Event Name'] = label_encoder.fit_transform(data['Event Name'])
data['Location'] = label_encoder.fit_transform(data['Location'])

# Fit Nearest Neighbors model
X = data[['Event Name', 'Location']]
y = data['Photographer Name']
knn = NearestNeighbors(n_neighbors=5, algorithm='auto')
knn.fit(X)

photographer_data = pd.read_csv('photography.csv')

# Define the categories
event_photography = [
    'Wedding event',
    'Naming Ceremony',
    'Engagement party',
    'Birthday party',
    'Festival Photography',
    'Anniversary celebration',
    'Educational ceremony',
    'Music and Dance photography',
    'Family and Social event'
]

nature_and_art_photography = [
    'Nature Photography',
    'Flower Photography',
    'Fashion Show Photography',
    'Portrait Photography',
    'Sports event Photography'
]

commercial_photography = [
    'Corporate Photography',
    'Private events photography'
]


# cur = mysql.connection.cursor(pymysql.cursors.DictCursor)
#         cur.execute(
#             "SELECT retailer_first_name, retailer_last_name, retailer_email, retailer_phone_no, retailer_city FROM retailer_table WHERE retailer_email = %s",
#             (session['userid'],))
#         retailer_data = cur.fetchall()
#         cur.close()


class photographer(db.Model):
    __tablename__ = 'photographer'
    photographer_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone_no = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    longitude = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Text, nullable=False)
    profile_picture = db.Column(db.Text, nullable=True)


class bookings(db.Model):
    __tablename__ = 'bookings'
    booking_id = db.Column(db.Integer, primary_key=True)
    photographer_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.user_id'))
    name = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    date = db.Column(db.Text, nullable=False)
    photographer_name = db.Column(db.Text, nullable=False)
    photographer_price = db.Column(db.Text, nullable=False)
    status = db.Column(db.Text, nullable=False)


class users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)

    email = db.Column(db.Text, nullable=False)
    phone_no = db.Column(db.Text, nullable=False)


class bookings_list(db.Model):
    __tablename__ = 'bookings_list'
    booking_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('users.user_id'))
    name = db.Column(db.Text, nullable=False)
    phone = db.Column(db.Text, nullable=False)
    location = db.Column(db.Text, nullable=False)
    date = db.Column(db.Text, nullable=False)
    photographer_name = db.Column(db.Text, nullable=False)
    photographer_price = db.Column(db.Text, nullable=False)


class feedback(db.Model):
    __tablename__ = 'feedback'
    feedback_id = db.Column(db.Integer, primary_key=True)
    photographer_id = db.Column(db.Integer, ForeignKey('photographer.photographer_id'))
    photographer_name = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text, nullable=False)


@app.route('/')
def landing():
    return render_template('landing_page.html')


@app.route('/index')
def index():
    categories = ['Wedding', 'Nature', 'Birthday ', 'Social Event', 'Wildlife',
                  'Potrait', 'Private events', 'Fashion show', 'Corporate',
                  'Festival']
    current_user = session.get('email')
    return render_template('index.html', current_user=current_user, categories=categories)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


@app.route('/portfolio_details')
def portfolio_details():
    return render_template('portfolio_details.html')


@app.route('/blog')
def blog():
    return render_template('blog.html')


@app.route('/single_blog')
def single_blog():
    return render_template('single-blog.html')


@app.route('/pages')
def pages():
    return render_template('pages.html')


@app.route('/elements')
def elements():
    return render_template('elements.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login_page')
def login_page():
    return render_template('login_user.html')


@app.route('/register_page')
def register_page():
    return render_template('register_user.html')


@app.route('/photographer_reg')
def photographer_reg():
    return render_template('photographer_registration.html')


@app.route('/photographer_log')
def photographer_log():
    return render_template('photographer_login.html')


@app.route('/register_user', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        # Extract data from the form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone_no = request.form['contact']

        existing_user = users.query.filter_by(email=email).first()
        if existing_user:
            return "Email already exists"

        # Create a new instance of the users model with the form data
        new_user = users(username=username, password=password, email=email, phone_no=phone_no)

        # Add the new user to the database session and commit the transaction
        db.session.add(new_user)
        db.session.commit()
        session['email'] = email
        db.session.close()
        return redirect(url_for('login_page'))  # Redirect to the login page after successful registration


@app.route('/login_user', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.query.filter_by(username=username, password=password).first()

        if user:
            session['user_id'] = user.user_id
            return redirect(url_for('index'))
        else:
            return render_template('login_user.html', error='Invalid credentials')


@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to the login page or any other desired page
    return redirect(url_for('landing'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return render_template('login_user.html')  # Render a template indicating login is required

    # Retrieve the user's profile information from the database
    user_id = session['user_id']
    user = users.query.filter_by(user_id=user_id).first()

    # Query the bookings associated with the current user
    user_bookings = bookings_list.query.filter_by(user_id=user_id).all()
    bookingss = bookings.query.filter_by(user_id=user_id).all()

    return render_template('profile.html', user=user, bookings=user_bookings, bookingss=bookingss)


@app.route('/recommend_photographers', methods=['GET', 'POST'])
def recommend_photographers():
    if request.method == 'POST':
        category = request.form['category']
        app.logger.info(category)

        # Filter the dataset for the selected category
        selected_photographers = photographer_data[photographer_data['Event Name'] == category]

        # Get the top 5 photographers based on the lowest price
        top_photographers = selected_photographers.nsmallest(5, 'Price')

        # Shuffle the top 5 photographers
        top_photographers_shuffled = top_photographers.sample(frac=1)

        # Convert the result to a JSON response
        result = top_photographers_shuffled.to_dict(orient='records')
        categories = [
            'Wedding event', 'Naming Ceremony', 'Engagement party', 'Birthday party', 'Nature Photography',
            'Fashion Show Photography', 'Portrait Photography', 'Flower Photography', 'Corporate Photography',
            'Festival Photography', 'Sports event Photography', 'Private events photography', 'Educational ceremony',
            'Music and Dance photography', 'Anniversary celebration', 'Family and Social event']
        current_user = session.get('email')
        app.logger.info(result)
        return render_template('index.html', current_user=current_user, categories=categories, result=result)
    else:
        categories = [
            'Wedding event', 'Naming Ceremony', 'Engagement party', 'Birthday party', 'Nature Photography',
            'Fashion Show Photography', 'Portrait Photography', 'Flower Photography', 'Corporate Photography',
            'Festival Photography', 'Sports event Photography', 'Private events photography', 'Educational ceremony',
            'Music and Dance photography', 'Anniversary celebration', 'Family and Social event']
        current_user = session.get('email')
        return render_template('index.html', current_user=current_user, categories=categories)


# def recommend_photographers(event_name, location):
#     event_name_encoded = label_encoder.transform([event_name])[0]
#     location_encoded = label_encoder.transform([location])[0]
#     user_input = [[event_name_encoded, location_encoded]]
#     _, indices = knn.kneighbors(user_input)
#     recommended_photographers = data.iloc[indices[0]]['Photographer Name'].tolist()
#     return recommended_photographers
#
#
# @app.route('/recommend_photographer', methods=['POST'])
# def recommend_photographer():
#     # app.logger.info('button clicked')
#     if request.method == 'POST':
#         #     # Get event name and location from the request
#         #     event_name = request.form['event_name']
#         #     location = request.form['location']
#         #     app.logger.info(event_name + ' ' + location)
#         #
#         #     # Prepare input data for prediction
#         #     input_data = pd.DataFrame({'Event Name': [event_name], 'Location': [location]})
#         #     app.logger.info(input_data)
#         #
#         #     # Predict probabilities for all photographers
#         #     probabilities = model.predict_proba(input_data)
#         #
#         #     # Get the list of all photographer names
#         #     photographer_names = model.classes_
#         #
#         #     # Combine photographer names with their probabilities
#         #     recommendations = list(zip(photographer_names, probabilities[0]))
#         #
#         #     # Sort recommendations based on probabilities (descending order)
#         #     recommendations.sort(key=lambda x: x[1], reverse=True)
#         #
#         #     # Get top 5 recommendations
#         #     top_n_recommendations = recommendations[:5]
#         #     app.logger.info(top_n_recommendations)
#         #
#         #     # Prepare response data
#         #     recommended_photographers = [{'photographer': photographer, 'probability': probability} for
#         #                                  photographer, probability in top_n_recommendations]
#         #
#         #     app.logger.info(recommended_photographers)
#         #     return jsonify(recommended_photographers)
#
#         app.logger.info("Data")
#         event_name = request.form['event_name']
#         location = request.form['location']
#         # event_name = data['event_name']
#         # location = data['location']
#         recommendations = recommend_photographers(event_name, location)
#         app.logger.info("Data" + recommendations)
#         categories = [
#         'Wedding event', 'Naming Ceremony', 'Engagement party', 'Birthday party', 'Nature Photography',
#         'Fashion Show Photography', 'Portrait Photography', 'Flower Photography', 'Corporate Photography',
#         'Festival Photography', 'Sports event Photography', 'Private events photography', 'Educational ceremony',
#         'Music and Dance photography', 'Anniversary celebration', 'Family and Social event']
#         current_user = session.get('email')
#         return render_template('index.html', current_user=current_user, categories=categories, recommendations=recommendations)
#     return redirect('/')


@app.route('/photographer_register', methods=['POST'])
def photographer_register():
    global file_path
    if request.method == 'POST':
        # Extract form data from the request
        name = request.form['name']
        email = request.form['email']
        phone_no = request.form['phone_no']
        address = request.form['address']
        username = request.form['username']
        password = request.form['pswd']
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        profile_picture = request.files['image']

        if profile_picture:
            file_extension = profile_picture.filename.rsplit('.', 1)[1].lower()
            file_path = os.path.join('static', 'photographer_profile_photos', f'{username}_profile.{file_extension}')
            profile_picture.save(file_path)

            # Create a directory under photographer_sample_photos with the username
            directory_path = os.path.join('static', 'photographer_sample_photos', username)
            os.makedirs(directory_path, exist_ok=True)

        # Create a new instance of the photographer model
        new_photographer = photographer(
            name=name,
            address=address,
            email=email,
            phone_no=phone_no,
            username=username,
            password=password,
            latitude=latitude,
            longitude=longitude,
            profile_picture=file_path,
        )

        # Add the new photographer to the database session and commit changes
        db.session.add(new_photographer)
        db.session.commit()

        # Create a session with the photographer id
        session['photographer_id'] = new_photographer.photographer_id

        # Optionally, you can redirect the user to a success page or perform any other actions
        return redirect(url_for('photographer_log'))


@app.route('/photographer_login', methods=['POST'])
def photographer_login():
    if request.method == 'POST':
        # Extract username and password from the login form
        username = request.form['username']
        password = request.form['passwd']

        # Check if the username and password are valid
        user = photographer.query.filter_by(username=username, password=password).first()

        if user:
            # If user is found in the database, create a session and store the user's id
            session['photographer_id'] = user.photographer_id
            return redirect(url_for('dashboard'))
        else:
            # If username or password is incorrect, redirect back to login page with a message
            return redirect(url_for('login_page'))


@app.route('/dashboard')
def dashboard():
    # Check if photographer is logged in
    if 'photographer_id' not in session:
        return redirect(url_for('photographer_login'))  # Redirect to login page if not logged in

    # Retrieve photographer ID from session
    photographer_id = session['photographer_id']

    # Query the photographer table to get data of the logged-in photographer
    photographer_dataa = photographer.query.filter_by(photographer_id=photographer_id).first()

    # Query the bookings table to get all bookings associated with the photographer
    bookings_data = bookings.query.filter_by(photographer_id=photographer_id).all()

    feedback_data = feedback.query.filter_by(photographer_id=photographer_id).all()
    # Pass the photographer data and bookings data to the template for rendering
    return render_template('dashboard.html', photographer_dataa=photographer_dataa, bookings=bookings_data, feedback_data=feedback_data)


@app.route('/upload_image', methods=['POST'])
def upload_image():
    # Retrieve username from session or wherever it is stored
    username = request.args.get('username')
    directory_path = os.path.join('static', 'photographer_sample_photos', username)

    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    # Save the uploaded image to the directory
    if 'image' in request.files:
        image_file = request.files['image']
        if image_file.filename != '':
            image_file.save(os.path.join(directory_path, image_file.filename))

    # Redirect to the new endpoint
    return redirect(url_for('your_work'))


import os


@app.route('/view_photographer_portfolio', methods=['GET', 'POST'])
def view_photographer_portfolio():
    # Retrieve photographer ID from session
    photographer_id = request.args.get('photographer_id')
    price = request.args.get('price')

    # Query the photographer table to get data of the logged-in photographer
    photographer_data = photographer.query.filter_by(photographer_id=photographer_id).first()

    # Fetch all images from the directory static/photographer_sample_photos/
    username = photographer_data.username
    directory_path = os.path.join('static', 'photographer_sample_photos', username)
    directory_path = directory_path.replace("\\", "/")  # Replace backslashes with forward slashes
    image_files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    # Create a single variable containing paths of all the images with forward slashes
    image_paths = [os.path.join('photographer_sample_photos', username, f).replace("\\", "/") for f in image_files]

    # Query the feedback table to get feedback data for the photographer
    feedback_data = feedback.query.filter_by(photographer_id=photographer_id).all()

    # Pass the photographer data, bookings data, image paths, and feedback data to the template for rendering
    return render_template('photographer_portfolio.html', photographer_dataa=photographer_data, image_paths=image_paths,
                           price=price, feedback_data=feedback_data)



@app.route('/your_work', methods=['GET', 'POST'])
def your_work():
    # Retrieve photographer ID from session
    photographer_id = session.get('photographer_id')

    # Query the photographer table to get data of the logged-in photographer
    photographer_data = photographer.query.filter_by(photographer_id=photographer_id).first()

    # Fetch all images from the directory static/photographer_sample_photos/
    username = photographer_data.username
    directory_path = os.path.join('static', 'photographer_sample_photos', username)
    directory_path = directory_path.replace("\\", "/")  # Replace backslashes with forward slashes
    image_files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]

    # Create a single variable containing paths of all the images with forward slashes
    image_paths = [os.path.join('photographer_sample_photos', username, f).replace("\\", "/") for f in image_files]

    # Pass the photographer data, bookings data, and image paths to the template for rendering
    return render_template('photographer_your_work.html', photographer_dataa=photographer_data, image_paths=image_paths)


@app.route('/confirm_photographer_booking', methods=['POST', 'GET'])
def confirm_photographer_booking():
    booking_id = request.args.get('booking_id')
    booking = bookings.query.filter_by(booking_id=booking_id).first()
    if booking:
        # Update the status field to 'booked'
        booking.status = 'booked'

        # Commit the changes to the database
        db.session.commit()
        return redirect('/dashboard')
    else:
        return redirect('/dashboard')


@app.route('/decline_photographer_booking', methods=['POST', 'GET'])
def decline_photographer_booking():
    booking_id = request.args.get('booking_id')
    booking = bookings.query.filter_by(booking_id=booking_id).first()
    if booking:
        # Update the status to "declined"
        booking.status = "declined"

        # Commit the changes to the database
        db.session.commit()
        return redirect('/dashboard')
    else:
        return redirect('/dashboard')



def generate_unique_id():
    pass


@app.route('/booking_form')
def booking_form():
    return render_template('booking_form.html')


@app.route('/photographer_booking')
def photographer_booking():
    return render_template('photographer_booking.html')


@app.route('/Mymap')
def Mymap():
    return render_template('map.html')


@app.route('/bookingss')
def bookingss():
    latest_booking = bookings_list.query.order_by(bookings_list.booking_id.desc()).first()

    # Extract the required attributes from the latest booking
    booking_data = {
        'photographer_name': latest_booking.photographer_name,
        'photographer_price': latest_booking.photographer_price,
        'name': latest_booking.name,
        'phone': latest_booking.phone,
        'location': latest_booking.location,
        'date': latest_booking.date
    }

    # Render the bookings.html template and pass the latest booking data
    return render_template('bookings.html', booking_data=booking_data)


@app.route('/bookingsss')
def bookingsss():
    latest_booking = bookings.query.order_by(bookings.booking_id.desc()).first()

    # Extract the required attributes from the latest booking
    booking_data = {
        'photographer_name': latest_booking.photographer_name,
        'photographer_price': latest_booking.photographer_price,
        'name': latest_booking.name,
        'phone': latest_booking.phone,
        'location': latest_booking.location,
        'date': latest_booking.date
    }

    # Render the bookings.html template and pass the latest booking data
    return render_template('photo_booking.html', booking_data=booking_data)


@app.route('/submit_booking', methods=['POST'])
def submit_booking():
    if request.method == 'POST':
        # Extract form data from the request
        # Check if user is logged in
        if 'user_id' not in session:
            # Redirect to the login page if user is not logged in
            return redirect(url_for('login'))

        name = request.form['name']
        phone = request.form['contact']
        location = request.form['location']
        date = request.form['date']
        photographer_name = request.form['photographer']
        photographer_price = request.form['price']

        # Create a new instance of the bookings_list model
        new_booking = bookings_list(name=name, phone=phone, location=location, date=date,
                                    photographer_name=photographer_name, photographer_price=photographer_price,
                                    user_id=session['user_id'])

        # Add the new booking to the database session and commit changes
        db.session.add(new_booking)
        db.session.commit()
        db.session.close()
        # Optionally, you can redirect the user to a success page or perform any other actions
        return redirect(url_for('bookingss'))

    # Handle other HTTP methods if needed
    return "Invalid request method"


@app.route('/submit_photographer_booking', methods=['POST'])
def submit_photographer_booking():
    if request.method == 'POST':
        # Extract form data from the request
        # Check if user is logged in
        if 'user_id' not in session:
            # Redirect to the login page if user is not logged in
            return redirect(url_for('login'))

        name = request.form['name']
        phone = request.form['contact']
        location = request.form['location']
        date = request.form['date']
        photographer_name = request.form['photographer']
        photographer_price = request.form['price']

        photographer_data = photographer.query.filter_by(name=photographer_name).first()
        if photographer_data:
            photographer_id = photographer_data.photographer_id
        else:
            # Handle the case where photographer name doesn't exist
            # Redirect or show an error message
            return redirect(url_for('error_page'))
        # Create a new instance of the bookings_list model
        new_booking = bookings(photographer_id=photographer_id, user_id=session['user_id'], name=name, phone=phone,
                               location=location, date=date,
                               photographer_name=photographer_name, photographer_price=photographer_price,
                               status='requested')

        # Add the new booking to the database session and commit changes
        db.session.add(new_booking)
        db.session.commit()
        db.session.close()
        # Optionally, you can redirect the user to a success page or perform any other actions
        return redirect(url_for('bookingsss'))

    # Handle other HTTP methods if needed
    return "Invalid request method"


def haversine(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, sqrt, atan2

    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = 6371 * c  # Radius of the Earth in kilometers

    return distance


@app.route('/find_nearest_photographers', methods=['POST'])
def find_nearest_photographers():
    # Get user's current latitude and longitude from the form
    user_latitude = request.form.get('latitude')
    user_longitude = request.form.get('longitude')

    # Query all photographers from the database
    all_photographers = photographer.query.all()

    # Calculate distance between user and each photographer
    for p in all_photographers:
        distance = haversine(user_latitude, user_longitude, p.latitude, p.longitude)
        p.distance = distance  # Add distance to photographer object

        # Format the profile_picture path
    if p.profile_picture:
        p.profile_picture = p.profile_picture.replace('static\\', '').replace('\\', '/')

    # Sort photographers by distance (ascending order)
    nearest_photographers = sorted(all_photographers, key=lambda x: x.distance)

    # Render template with nearest photographers
    return render_template('map.html', photographers=nearest_photographers)


@app.route('/logout_photographer', methods=['GET'])
def logout_photographer():
    session.clear()
    return redirect(url_for('landing'))


@app.route('/provide_feedback', methods=['POST'])
def provide_feedback():
    if request.method == 'POST':
        # Get data from the form
        booking_id = request.args.get('booking_id')
        rating = int(request.form.get('rating'))  # Assuming rating is provided as an integer
        feedback_text = request.form.get('feedbackText')

        # Assuming you have user_id stored in session
        user_id = session.get('user_id')
        user = users.query.filter_by(user_id=user_id).first()
        username = user.username
        # Check if all necessary data is available
        if not (booking_id and rating and feedback_text and user_id):
            return jsonify({'error': 'Missing data'})

        # Fetch photographer_id using booking_id
        booking = bookings.query.filter_by(booking_id=booking_id).first()
        if not booking:
            return jsonify({'error': 'Booking not found'})

        photographer_id = booking.photographer_id
        # Assuming you have username stored in session
        photographer_name = booking.photographer_name
        # Create a new Feedback instance
        new_feedback = feedback(
            photographer_id=photographer_id,
            photographer_name=photographer_name,
            user_id=user_id,
            username=username,
            rating=rating,
            review=feedback_text
        )

        # Add the new feedback to the database session
        db.session.add(new_feedback)
        # Commit the session to save the changes to the database
        db.session.commit()

        return redirect('/profile')

    return jsonify({'error': 'Method not allowed'})


if __name__ == '__main__':
    app.run(debug=True)
