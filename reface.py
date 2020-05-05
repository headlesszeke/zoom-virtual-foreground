import numpy as np
import cv2
import pyfakewebcam
import sys

if len(sys.argv) != 2:
    print("Usage: %s /path/to/fakewebcam")
    sys.exit(1)
    
# initialize real capture device
cap = cv2.VideoCapture("/dev/video0")
width, height = 640, 480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cap.set(cv2.CAP_PROP_FPS, 60)

# initialize fake cam
fake = pyfakewebcam.FakeWebcam(sys.argv[1], width, height)

# laziness...read all frames of laughing man animation into array
new_faces = []
for x in range(0,48):
    img = cv2.imread("%s%s.png" % ("laughing_man/",x),-1)
    new_faces.append(img)

# this one worked best for me even with glare on glasses, but ymmv
facecasc = cv2.CascadeClassifier("./haarcascade_frontalface_alt.xml")

# array of found faces
faces = []

# index of laughing man animation array
idx = 0

while True:
    try:
        # get a frame
        _, img = cap.read()

        # convert to grayscale for better detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # find faces
        found_faces = facecasc.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

        # only update if you find new faces (use prev faces if detection didn't work for this frame)
        if len(found_faces) > 0:
            faces = found_faces

        # iterate through each face
        for (x, y, w, h) in faces:

            # hax...make new face cover more than area of old face
            nw = int(w * 1.5)
            nh = int(h * 1.5)
            ny = max(0, y - int(nh * 0.2))
            nx = max(0, x - int(nw * 0.1))
            new_face = cv2.resize(new_faces[idx],(nw,nh))

            # replace the old with the new in the original image 
            for c in range(0,3):
                img[ny:ny + nh,nx:nx + nw,c] = new_face[:,:,c] * (new_face[:,:,3]/255.0) + img[ny:ny + nh,nx:nx + nw,c] * (1.0 - new_face[:,:,3]/255.0)

        # move to next laughing man animation frame
        if idx < len(new_faces) - 1:
            idx += 1
        else:
            idx = 0

        # opencv is BGR, but web cam is RGB, so convert it           
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # write modified frame out to fake web cam
        fake.schedule_frame(frame)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    except:
        pass
