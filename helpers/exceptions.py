class DatasetExceptionBase(Exception):
    ''' The base class for all dataset exceptions'''
    pass

class DatasetNotFound(DatasetExceptionBase, FileNotFoundError):
    ''' The file was not found. '''
    pass

class DatasetFileExists(DatasetExceptionBase, FileExistsError):
    ''' The file you want to save already exists. '''
    pass

class DatasetMissingFrame(DatasetExceptionBase):
    ''' The dataset has not frame. '''
    pass