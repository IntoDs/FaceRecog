# import cv2 
# import face_recognition
# import dlib
# from imutils import paths
# import imutils
# import os
# import argparse
# import pickle

def getImages():
    import cv2 
    import face_recognition
    import dlib
    from imutils import paths
    import imutils
    import os
    import argparse
    import pickle
    from mainface import imagePath
    
    # ap = argparse.ArgumentParser()
    # ap.add_argument("-i", "--dataset", required=False,
    #     help="path to input directory of faces + images")
    # ap.add_argument("-e", "--encodings", required=False,
    #     help="path to serialized db of facial encodings")
    # ap.add_argument("-d", "--detection-method", type=str, default="cnn",
    #     help="face detection model to use: either `hog` or `cnn`")
    # args = vars(ap.parse_args())


    print("[INFO] quantifying faces...")
    imagePaths =  imagePath #list(paths.list_images(args["dataset"]))
    # initialize the list of known encodings and known names
    knownEncodings = []
    knownNames = []

    print(imagePaths)

    for (i, imagePath) in enumerate(imagePaths):
        # extract the person name from the image path
        print("[INFO] processing image {}/{}".format(i + 1,
            len(imagePaths)))
        name = imagePath.split(os.path.sep)[-2]

        
        image = cv2.imread(imagePath)
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb, model='hog')
        # compute the facial embedding for the face
        encodings = face_recognition.face_encodings(rgb, boxes)

        # loop over the encodings
        for encoding in encodings:
            # add each encoding + name to our set of known names and
            # encodings
            knownNames.append(name)
            knownEncodings.append(encoding)

    print("[INFO] serializing encodings...")
    data = {"encodings": knownEncodings, "names": knownNames}
    f = open("encodings", "wb")
    f.write(pickle.dumps(data))
    f.close()
    print("[INFO] done.")
    
if __name__ =='__main__':
    getImages()