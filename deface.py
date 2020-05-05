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

# this one worked best for me even with glare on glasses, but ymmv
facecasc = cv2.CascadeClassifier("./haarcascade_frontalface_alt.xml")

# array of found faces
faces = []

# number of pixel blocks
blocks = 9

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

            # divide x and y into blocks number of equal chunks
            xsteps = np.linspace(x, x + w, blocks + 1, dtype="int")
            ysteps = np.linspace(y, y + h, blocks + 1, dtype="int")

            # iterate through x and y blocks
            for i in range(1, len(ysteps)):
                for j in range(1, len(xsteps)):

                    # dimensions of current block
                    startx = xsteps[j - 1]
                    starty = ysteps[i - 1]
                    endx = xsteps[j]
                    endy = ysteps[i]
                    roi = img[starty:endy, startx:endx]

                    # average the colors together 
                    (B, G, R) = [int(k) for k in cv2.mean(roi)[:3]]

                    # draw a block of the averaged colors over that part of the frame
                    cv2.rectangle(img, (startx, starty), (endx, endy), (B, G, R), -1)

        # opencv is BGR, but web cam is RGB, so convert it           
        frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # write modified frame out to fake web cam
        fake.schedule_frame(frame)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
    except:
        pass
