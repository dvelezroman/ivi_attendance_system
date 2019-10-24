# Import the library
import face_recognition
import cv2
import numpy as np
import multiprocessing
import os
from time import sleep
import re

# Declare all the list
known_face_encodings = []
known_face_names = []
known_faces_file_names = []


# Walk in the folder to add every file name to known_faces_file_names
def get_known_faces_file_names(path="assets/img/users"):
    for (dir_path, dir_names, file_names) in os.walk(path):
        known_faces_file_names.extend(file_names)
        break


def load_picture(file_name):
    # Load the file
    loaded_picture = face_recognition.load_image_file(file_name)
    return loaded_picture


# Walk in the folder
def encode_known_faces(path="assets/img/users"):
    for filename in known_faces_file_names:
        # load the picture
        picture = load_picture(path + filename)
        # Encode the face
        encoded_face = encode_one_face_picture(picture)
        # append the encoded picture to the know faces array
        known_face_encodings.append(encoded_face)
        # Extract the name of each employee and add it to known_face_names
        known_face_names.append(re.sub("[0-9]", '', filename[:-4]))


# encode a face in a picture
def encode_one_face_picture(picture):
    encoded_face = face_recognition.face_encodings(picture)[0]
    return encoded_face


# encode faces in a picture
def encode_faces_picture(picture):
    faces_in_picture = get_face_locations(picture)
    encoded_faces = face_recognition.face_encodings(picture, faces_in_picture)
    return encoded_faces


# get face locations in a picture
def get_face_locations(frames_to_get_locations_queue, locations_queue):
    while True:
        if frames_to_get_locations_queue.qsize() > 0:
            picture = frames_to_get_locations_queue.get()
            locations = face_recognition.face_locations(picture)
            locations_queue.put(locations)


# get best match of a face
def compare_face_against_known_faces(encoding):
    matches = face_recognition.compare_faces(known_face_encodings, encoding)
    name = "Unknown"
    face_distances = face_recognition.face_distance(known_face_encodings, encoding)
    best_match_index = np.argmin(face_distances)
    if matches[best_match_index]:
        name = known_face_names[best_match_index]

    return name


# gets the video source
def get_video_stream(source=0):
    pointer = cv2.VideoCapture(source)
    sleep(2)
    return pointer


# gets the frame rate
def get_frame_rate(stream):
    rate = stream.get(cv2.CAP_PROP_FPS)
    return rate


# gets the frames
def put_frames_to_queue(stream, frames_queue, frames_to_get_locations_queue):
    while True:
        flag, frame = stream.read()
        if flag is not None:
            frames_queue.put(frame)
            frames_to_get_locations_queue.put(frame)


# * ----------------------- Encode the nameless picture -----------------------
# Load Picture
# face_picture = load_picture("assets/img/user-one.jpg")
# Detect and Encode faces
# face_encodings = encode_faces_picture(face_picture)


# * ----------------------- Loop in all detected faces -----------------------
# Loop in all detected faces
# for face_encoding in face_encodings:
    # See if the face is a match for the know face (that we saved in the precedent step)
    # name_of_face = compare_face_against_known_faces(face_encoding)

# * ------------------------ Select the web cam of the computer -----------------------
if __name__ == '__main__':
    video_stream = get_video_stream()
    frames = 0
    fps = get_frame_rate(video_stream)
    monitoring = True

    frames_queue = multiprocessing.Queue()
    locations_queue = multiprocessing.Queue()
    frames_to_get_locations_queue = multiprocessing.Queue()

    put_frames_to_queue_process = multiprocessing.Process(
        target=put_frames_to_queue, args=(video_stream, frames_queue, frames_to_get_locations_queue, ))
    put_frames_to_queue_process.start()

    get_face_locations_process = multiprocessing.Process(
        target=get_face_locations, args=(frames_queue, locations_queue, ))
    get_face_locations_process.start()

    faces = []

    while True:
        frames += 1
        frm = frames_queue.get()

        if locations_queue.qsize() > 0:
            faces = locations_queue.get()

        text = "{} faces".format(len(faces))
        cv2.putText(frm, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))

        # Showing the frame with all the applied modifications
        cv2.imshow("Stream", frm)

        key_pressed = cv2.waitKey(1) & 0xFF
        if key_pressed == ord("q"):
            locations_queue.close()
            frames_queue.close()
            frames_to_get_locations_queue.close()
            put_frames_to_queue_process.terminate()
            get_face_locations_process.terminate()
            break

    cv2.destroyAllWindows()
    video_stream.release()
