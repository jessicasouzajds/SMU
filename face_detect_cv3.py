import cv2
import sys
import numpy as np

# Get user supplied values
# imagePath = sys.argv[1]
cascPath = "haarcascade_frontalface_default.xml"

# Create the haar cascade
faceCascade = cv2.CascadeClassifier(cascPath)

# Read the image
#image = cv2.imread(imagePath)

# capture video
cap = cv2.VideoCapture(0)
while(True):
    ret, image = cap.read()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
        #flags = cv2.CV_HAAR_SCALE_IMAGE
    )

    print("Found {0} faces!".format(len(faces)))

    width, height, _ = image.shape

    x = np.arange(height*width)
    x = x.reshape((width,height))
    mask = np.ones_like(x)



    # Desired "pixelated" size
    wi, he = (4, 4)
    # Draw a rectangle around the faces
    for (x, y, w, h) in faces:
        #cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        crop_img = gray[y:y+h,x:x+w]
        cv2.imshow("croped", crop_img)
        # Resize input to "pixelated" size
        temp = cv2.resize(crop_img, (wi, he), interpolation=cv2.INTER_LINEAR)

        # Initialize output image
        output = cv2.resize(temp, (w, h),      interpolation=cv2.INTER_NEAREST)
        cv2.imshow("aaaa", output)
        image[y:y+h,x:x+w,0] = output
        image[y:y+h,x:x+w,1] = output
        image[y:y+h,x:x+w,2] = output
        print(len(image))

    cv2.imshow("Faces found", image)
    cv2.waitKey(1)
