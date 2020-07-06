from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot
from gui2 import Ui_MainWindow
import sys
from main_model import Model
import imutils
from imutils import paths
import cv2 
import face_recognition
import dlib
import os
import argparse
import pickle
from facecog2 import runProg
import time
import pkg_resources.py2_warn
# import six

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
        self.debugPrint( "Completed!" )
    
    # slot
    def browseSlot( self ):
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
            global folderPath
            folderPath = fileName
            self.refreshAll()
            print(folderPath)
            print(fileName)

    def runSlot(self):
        self.debugPrint('[INFO] loading...')
        time.sleep(1)
        self.debugPrint('[INFO] starting video stream...')

        runProg()

        self.debugPrint('DONE!')


    def getImages(self):
        self.debugPrint('Loading...')
        

        self.debugPrint("[INFO] quantifying faces...")
        imagePaths = list(paths.list_images(folderPath))
        # initialize the list of known encodings and known names
        knownEncodings = []
        knownNames = []

        print(imagePaths)

        for (i, imagePath) in enumerate(imagePaths):
            # extract the person name from the image path
            self.debugPrint("[INFO] processing image {}/{}".format(i + 1,
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

        self.debugPrint("[INFO] serializing encodings...")
        data = {"encodings": knownEncodings, "names": knownNames}
        f = open("encodings", "wb")
        f.write(pickle.dumps(data))
        f.close()
        self.debugPrint("[INFO] done.")

        
def main():
    """
    This is the MAIN ENTRY POINT of our application.  The code at the end
    of the mainwindow.py script will not be executed, since this script is now
    our main program.   We have simply copied the code from mainwindow.py here
    since it was automatically generated by '''pyuic5'''.

    """
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = MainWindowUIClass()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
if __name__ == '__main__':
    main()