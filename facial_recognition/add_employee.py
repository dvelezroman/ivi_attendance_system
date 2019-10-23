# Import the library
import face_recognition
import numpy as np
import os
import re

# Declare all the list
known_face_encodings = []
known_face_names = []
known_faces_filenames = []

# Walk in the folder to add every file name to known_faces_filenames
for (dirpath, dirnames, filenames) in os.walk('assets/img/users'):
    known_faces_filenames.extend(filenames)
    break

# Walk in the folder
for filename in known_faces_filenames:
    # Load each file
    face = face_recognition.load_image_file('assets/img/users/' + filename)
    # Extract the name of each employee and add it to known_face_names
    known_face_names.append(re.sub("[0-9]", '', filename[:-4]))
    # Encode the face of every employee
    known_face_encodings.append(face_recognition.face_encodings(face)[0])

# * ----------------------- Encode the nameless picture -----------------------
# Load Picture
face_picture = face_recognition.load_image_file("assets/img/user-one.jpg")
# Detect faces
face_locations = face_recognition.face_locations(face_picture)
# Encode faces
face_encodings = face_recognition.face_encodings(face_picture, face_locations)

# Loop in all detected faces
for face_encoding in face_encodings:
    # See if the face is a match for the know face (that we saved in the precedent step)
    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
    # name that we will give if the employee is not in the system
    name = "Unknown"
    # check the known face with the smallest distance to the new face
    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
    # Take the best one
    best_match_index = np.argmin(face_distances)
    # if we have a match:
    if matches[best_match_index]:
        # Give the detected face the name of the employee that match
        name = known_face_names[best_match_index]
