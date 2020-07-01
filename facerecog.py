import cv2 
import face_recognition
import dlib

video_capture = cv2.VideoCapture(0, cv2.CAP_V4L2)

print(cv2.CAP_PROP_FPS)

image = face_recognition.load_image_file("jake.jpg")
abbie = face_recognition.load_image_file("abbie2.jpg")
jake_encoding = face_recognition.face_encodings(image)[0]
abbie_encoding = face_recognition.face_encodings(abbie)[0]

known_faces = [
jake_encoding,
abbie_encoding,
]

face_locations = []
face_encodings = []
face_names = []
frame_number = 0

while True:
    ret, frame = video_capture.read()

    rgb_frame = frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_frame, model="hog")
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, model="large")

    face_names = []
    for face_encoding in face_encodings:
        # See if the face is a match for the known face(s)
        match = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.6)

        name = None
        if match[0]:
            name = "Jake"
        elif match[1]:
            name = "Abbie"
        else:
            name = "Unknown"

        face_names.append(name)

    # Label the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        if not name:
            continue
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(frame, (left, bottom - 25), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)


    cv2.imshow('video', frame)

    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()