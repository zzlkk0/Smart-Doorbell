import cv2
import numpy as np

# Load the face cascade
faceCascade = cv2.CascadeClassifier('/home/link/facedetect/haarcascade_frontalface_default.xml')


# Initialize video capture
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set width
cap.set(4, 480)  # Set height

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
        scaleFactor=1.25,
        minNeighbors=3,
        minSize=(105, 105)
    )

    # Draw rectangles around faces and count them
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        # Optionally, save each detected face
        roi_color = img[y:y + h, x:x + w]
        face_filename = f"face_{x}_{y}.jpg"
        cv2.imwrite(face_filename, roi_color)
        # Save detected face as an image file

    # Display the number of faces detected
    cv2.putText(img, f'Faces: {len(faces)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show the video with face rectangles and face count
    cv2.imshow('video', img)

    # Break on 'Esc' key
    k = cv2.waitKey(30) & 0xff
    if k == 27:  # Esc to quit
        break

cap.release()
cv2.destroyAllWindows()
