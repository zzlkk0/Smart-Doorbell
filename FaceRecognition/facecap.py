import cv2
import numpy as np

# Load the face cascade
faceCascade = cv2.CascadeClassifier('/home/link/facedetect/haarcascade_frontalface_default.xml')

# Initialize video capture
cap = cv2.VideoCapture('rtmp://0.0.0.0:8888/live1/stream')
cap.set(3, 320)  # Set width
cap.set(4, 240)  # Set height

if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Check if face cascade is loaded correctly
if faceCascade.empty():
    print("Error: Could not load face cascade.")
    exit()

while True:
    ret, img = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    img = cv2.flip(img, 1)  # Flip the image horizontally
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.15,
        minNeighbors=3,
        minSize=(105, 105)
    )

    # Draw rectangles around faces
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Display the number of faces detected
    cv2.putText(img, f'Faces: {len(faces)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the video with face rectangles and face count
    cv2.imshow('video', img)

    # Check for 'k' key press to capture face
    k = cv2.waitKey(30) & 0xff
    if k == ord('k'):
        for (x, y, w, h) in faces:
            roi_color = img[y:y + h, x:x + w]
            face_filename = f"face_{x}_{y}.jpg"
            cv2.imwrite(face_filename, roi_color)
        print(f"Captured {len(faces)} face(s)")

    # Break on 'Esc' key
    if k == 27:  # Esc to quit
        break

cap.release()
cv2.destroyAllWindows()
