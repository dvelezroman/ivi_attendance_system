# * --------------------- IMPORTS --------------- *
# All the imports that we will need in our API
from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO, send, emit
from flask_cors import CORS, cross_origin
import os
import psycopg2
import cv2
import numpy as np
import re
import pickle
import threading

# we define the path of the current file, we will use it for later
FILE_PATH = os.path.dirname(os.path.realpath(__file__))

frames = []

# * ------------------------ CREATE APP ------------------------------- *
# Init the app
app = Flask(__name__)
# To avoid CORS errors
CORS(app, support_credentials=True)

socketio = SocketIO(app, cors_allowed_origins='*')
output_frame = None
lock = threading.Lock()


def generate():
    global output_frame, lock
    while True:
        with lock:
            if output_frame is None:
                continue

            # encode frame in JPEG format
            flag, encoded_image = cv2.imencode('.jpg', output_frame)
            if not flag:
                continue

        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encoded_image) + b'\r\n')


@socketio.on('message')
def handle_message(message):
    emit('response', f'I got your message {message}')


@socketio.on('get_frame')
def handle_get_frame(frame):
    global output_frame, lock
    print('I received a frame')
    # receive the frame and put it in outputFrame
    received_frame = pickle.loads(frame)
    # acquire the lock, set the output frame, and release the lock
    with lock:
        output_frame = received_frame.copy()


# * ---------- DATABASE CONFIG --------- *
DATABASE_USER = 'postgres'
DATABASE_PASSWORD = 'postgres2019'
DATABASE_HOST = '127.0.0.1'
DATABASE_PORT = '5432'
DATABASE_NAME = 'attendance'


def database_connection():
    return psycopg2.connect(user=DATABASE_USER,
                            password=DATABASE_PASSWORD,
                            host=DATABASE_HOST,
                            port=DATABASE_PORT,
                            database=DATABASE_NAME)


# * --------------------------- ROUTES ---------------------------------- *
# --------------------- Send frames to browsers -------------------------- *
@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media type (mime type)
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


# --------------------- Get data from the face recognition ------------- *
@app.route('/receive_data', methods=['POST'])
def get_receive_data():
    if request.method == 'POST':
        # Get the data
        json_data = request.get_json()
        print(json_data)
        try:
            # Connect to the DB
            connection = database_connection()
            # Open a cursor
            cursor = connection.cursor()

            # Query to check if the user has been saw by the camera today
            is_user_here_today = \
                f"SELECT * FROM users WHERE date = '{json_data['date']}' AND name = '{json_data['name']}'"
            cursor.execute(is_user_here_today)
            # Store the result
            result = cursor.fetchall()
            # Send the request
            connection.commit()

            # if user is already in the DB for today:
            if result:
                # Update user in the  DB
                update_user_query = f"UPDATE users SET departure_time = '{json_data['hour']}', " \
                                    f"departure_picture = '{json_data['picture_path']}' " \
                                    f"WHERE name = '{json_data['name']}' AND date = '{json_data['date']}'"
                cursor.execute(update_user_query)

            else:
                # Create a new row for the user today
                insert_user_query = f"INSERT INTO users (name, date, arrival_time, arrival_picture) " \
                                    f"VALUES ('{json_data['name']}', '{json_data['date']}', '{json_data['hour']}', " \
                                    f"'{json_data['picture_path']}')"
                cursor.execute(insert_user_query)

        except (Exception, psycopg2.DatabaseError) as error:
            print("ERROR DB: ", error)

        finally:
            # Execute the query
            connection.commit()

            # closing database connection
            if connection:
                cursor.close()
                connection.close()
                print("PostgresSQL connection is closed")

        # Return user's data to the front
        return jsonify(json_data)


# * ---------- Get all the data of an employee ---------- *
@app.route('/get_employee/<string:name>', methods=['GET'])
def get_employee(name):
    answer_to_send = {}
    # Check if the user is already in the DB
    try:
        # Connect to DB
        connection = database_connection()

        cursor = connection.cursor()
        # Query the DB to get all the data of a user:
        user_information = f"SELECT * FROM users WHERE name = '{name}'"

        cursor.execute(user_information)
        result = cursor.fetchall()
        connection.commit()

        # if the user exist in the db:
        if result:
            print('RESULT: ',result)
            # Structure the data and put the dates in string for the front
            for k,v in enumerate(result):
                answer_to_send[k] = {}
                for ko,vo in enumerate(result[k]):
                    answer_to_send[k][ko] = str(vo)
            print('answer_to_send: ', answer_to_send)
        else:
            answer_to_send = {'error': 'User not found...'}

    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        # closing database connection:
        if connection:
            cursor.close()
            connection.close()

    # Return the user's data to the front
    return jsonify(answer_to_send)


# * --------- Get the 5 last users seen by the camera --------- *
@app.route('/get_5_last_entries', methods=['GET'])
def get_5_last_entries():
    # Create a dict thet will contain the answer to give to the front
    answer_to_send = {}
    # Check if the user is already in the DB
    try:
        # Connect to DB
        connection = database_connection()

        cursor = connection.cursor()
        # Query the DB to get the 5 last entries ordered by ID:
        lasts_entries = f"SELECT * FROM users ORDER BY id DESC LIMIT 5;"
        cursor.execute(lasts_entries)
        # Store the result
        result = cursor.fetchall()
        # Send the request
        connection.commit()

        # if DB is not empty:
        if result:
            # Structure the data and put the dates in dict for the front
            for k, v in enumerate(result):
                answer_to_send[k] = {}
                for ko, vo in enumerate(result[k]):
                    answer_to_send[k][ko] = str(vo)
        else:
            answer_to_send = {'error': 'DB is not connected or empty'}

    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        # closing database connection:
        if connection:
            cursor.close()
            connection.close()

    # Return the user's data to the front as a json
    return jsonify(answer_to_send)


# * ---------- Add new employee ---------- *
@app.route('/add_employee', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_employee():
    try:
        # Get the picture from the request
        image_file = request.files['image']

        # Store it in the folder of the know faces:
        file_path = os.path.join(f"middleware/assets/img/users/{request.form['nameOfEmployee']}.jpg")
        image_file.save(file_path)
        answer = 'new employee succesfully added'

    except:
        answer = 'Error while adding new employee. Please try later...'

    return jsonify(answer)


# * ---------- Get employee list ---------- *
@app.route('/get_employee_list', methods=['GET'])
def get_employee_list():
    # Create a dict that will store the list of employee's name
    employee_list = {}

    # Walk in the user's folder to get the user list
    walk_count = 0
    pathname = os.getcwd()
    for file_name in os.listdir(f"{pathname}/middleware/assets/img/users/"):
        # Capture the employee's name with the file's name
        name = re.findall("(.*)\.jpg", file_name)
        if name:
            employee_list[walk_count] = name[0]
        walk_count += 1

    return jsonify(employee_list)


# * ---------- Delete employee ---------- *
@app.route('/delete_employee/<string:name>', methods=['GET'])
def delete_employee(name):
    try:
        # Select the path
        pathname = os.getcwd()
        file_path = os.path.join(f"{pathname}/middleware/assets/img/users/{name}.jpg")
        # Remove the picture of the employee from the user's folder:
        os.remove(file_path)
        answer = 'Employee succesfully removed'

    except:
        answer = 'Error while deleting new employee. Please try later'

    return jsonify(answer)


# * ------------------------ Run Server -------------------------------- *
if __name__ == '__main__':
    # * ---- DEBUG MODE: ----- *
    app.run(host='127.0.0.1', port=5000, debug=True)
    socketio.run(app)

    #  * --- DOCKER PRODUCTION MODE: --- *
    # app.run(host='0.0.0.0', port=os.environ['PORT']) -> DOCKER


