from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot
from imutils.video import VideoStream
from gui3 import Ui_MainWindow
import pkg_resources.py2_warn
from main_model import Model
from imutils import paths
import face_recognition
import argparse
import imutils
import pickle
import time
import dlib
import cv2 
import sys
import os

class MainWindowUIClass( Ui_MainWindow ):

    def __init__( self ):
        '''Initialize the super class
        '''
        super().__init__()
        self.model = Model()
        
        
    def setupUi( self, MW ):
        ''' Setup the UI of the super class, and add here code
        that relates to the way we want our UI to operate.
        '''
        super().setupUi( MW )

        # close the lower part of the splitter to hide the 
        # debug window under normal operations
        #self.splitter.setSizes([300, 0])
        self.debugPrint("Welcome! Click 'LOAD' to begin..." )

    def debugPrint( self, msg ):
        '''Print the message in the text edit at the bottom of the
        horizontal splitter.
        '''
        self.debugText.append( msg )

    def refreshAll( self ):
        '''
        Updates the widgets whenever an interaction happens.
        Typically some interaction takes place, the UI responds,
        and informs the model of the change.  Then this method
        is called, pulling from the model information that is
        updated in the GUI.
        '''
        self.lineEdit.setText( self.model.getFileName() )
        # self.textEdit.setText( self.model.getFileContents() )
    
    # slot
    def returnPressedSlot( self ):
        ''' Called when the user enters a string in the line edit and
        presses the ENTER key.
        '''
        fileName =  self.lineEdit.text()
        if self.model.isValid( fileName ):
            self.model.setFileName( self.lineEdit.text() )
            self.refreshAll()
        else:
            m = QtWidgets.QMessageBox()
            m.setText("Invalid file name!\n" + fileName )
            m.setIcon(QtWidgets.QMessageBox.Warning)
            m.setStandardButtons(QtWidgets.QMessageBox.Ok
                                 | QtWidgets.QMessageBox.Cancel)
            m.setDefaultButton(QtWidgets.QMessageBox.Cancel)
            ret = m.exec_()
            self.lineEdit.setText( "" )
            self.refreshAll()
            self.debugPrint( "Invalid file specified: " + fileName  )


    # slot
    def loadSlot( self ):
        ''' Called when the user presses the Load button.
        '''
        self.getImages()
    
    # slot
    def browseSlot( self ):
        global fileName
        ''' 
        Called when the user presses the Browse button
        '''
        #self.debugPrint( "Browse button pressed" )
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        # dialog = QtWidgets.QFileDialog()
        fileName = QtWidgets.QFileDialog.getExistingDirectory(None, "Select Folder",
                        options=options)
        if fileName:
            self.debugPrint( "setting file name: " + fileName )
            self.model.setFileName( fileName )
            # global folderPath
            # folderPath = fileName
            self.refreshAll()
            # print(folderPath)
            print(fileName)

    def runSlot(self):
        self.debugPrint('[INFO] Loading...')
        self.runProg()

    def progress(self, progressBar):
        return

    def getImages(self):
        # global folderPath
        global imagePaths

        self.debugPrint("[INFO] quantifying faces...")
        imagePaths = list(paths.list_images(fileName))
        # initialize the list of known encodings and known names
        knownEncodings = []
        knownNames = []
        time.sleep(1)

        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            self.debugPrint("[INFO] processing image {}/{}".format(i + 1,
                len(imagePaths)))
            name = imagePath.split(os.path.sep)[-2]
            self.progressBar.setMaximum(len(imagePaths))
            self.progressBar.setValue(i+1)
            app.processEvents()
            time.sleep(0.5)

            
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

        self.debugPrint("[INFO] serializing encodings...")
        app.processEvents()
        time.sleep(0.5)
        data = {"encodings": knownEncodings, "names": knownNames}
        f = open("encodings", "wb")
        f.write(pickle.dumps(data))
        f.close()
        self.debugPrint("[INFO] done.")

    def runProg(self):

        self.debugPrint('[INFO] starting video stream...')
        self.debugPrint('[INFO] press "q" to close video stream')
        data = pickle.loads(open("encodings", "rb").read())
        # initialize the video stream and pointer to output video file, then
        # allow the camera sensor to warm up
        vs = VideoStream(src=0).start()
        writer = None
        time.sleep(2.0)

        while True:
            # grab the frame from the threaded video stream
            frame = vs.read()
            
            # convert the input frame from BGR to RGB then resize it to have
            # a width of 750px (to speedup processing)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb = imutils.resize(frame, width=500)
            r = frame.shape[1] / float(rgb.shape[1])
            # detect the (x, y)-coordinates of the bounding boxes
            # corresponding to each face in the input frame, then compute
            # the facial embeddings for each face
            boxes = face_recognition.face_locations(rgb, model='hog')
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []


            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(data["encodings"],
                    encoding)
                name = "Unknown"
                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}
                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1
                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)
                
                # update the list of names
                names.append(name)

            # loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
                # rescale the face coordinates
                top = int(top * r)
                right = int(right * r)
                bottom = int(bottom * r)
                left = int(left * r)
                # draw the predicted face name on the image
                cv2.rectangle(frame, (left, top), (right, bottom),
                    (150, 255, 100), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.75, (150, 255, 100), 2)

            # check to see if we are supposed to display the output frame to
            # the screen
            if 1 > 0:
                cv2.imshow('video', frame)
                key = cv2.waitKey(1) & 0xFF
                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                    self.debugPrint('[INFO] Closing...')
                    break

        cv2.destroyAllWindows()
        vs.stop()
        # check to see if the video writer point needs to be released
        if writer is not None:
            writer.release()

        
def main():
    """
    This is the MAIN ENTRY POINT of our application.  The code at the end
    of the mainwindow.py script will not be executed, since this script is now
    our main program.   We have simply copied the code from mainwindow.py here
    since it was automatically generated by '''pyuic5'''.

    """
    import sys
    global app
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainWindowUIClass()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()