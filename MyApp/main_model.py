class Model:
    def __init__( self ):
        '''
        Initializes the two members the class holds:
        the file name and its contents.
        '''
        self.fileName = None
        self.fileContent = ""

    def isValid( self, fileName ):
        '''
        returns True if the file exists and can be
        opened.  Returns False otherwise.
        '''
        try: 
            file = open( fileName, 'r' )
            file.close()
            return True
        except:
            return False

    def setFileName( self, fileName ):
        '''
        sets the member fileName to the value of the argument
        if the file exists.  Otherwise resets both the filename
        and file contents members.
        '''
        if self.isValid( fileName ):
            self.fileName = fileName
        else:
            self.fileName = ""
            
    def getFileName( self ):
        '''
        Returns the name of the file name member.
        '''
        return self.fileName

    # def getFileContents( self ):
    #     '''
    #     Returns the contents of the file if it exists, otherwise
    #     returns an empty string.
    #     '''
    #     return self.fileContents
    
    # # def folderPath(self):
    # #     global folder_path
    # #     folder_path = self.model.setFileName( folder_path )