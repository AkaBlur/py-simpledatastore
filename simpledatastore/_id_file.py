import pathlib

import _filehelper



"""
ID File class
Holds all currently stored IDs of all stored file objects

    Parameters:
        storePath (pathlib.Path): path where the ID file should be stored
            ! needs to exist !
"""
class IDFile:
    __storePath: pathlib.Path
    __IDFile: pathlib.Path

    def __init__(self, storePath: pathlib.Path):
        self.__storePath = storePath
        self.__IDFile = self.__storePath / pathlib.Path("_ID.dat")

        _filehelper.create_file(
            storePath = self.__storePath,
            fname = self.__IDFile.name)
        

    """
    Reads all IDs that are currently stored
    
        Returns:
            list[int]: list of all IDs included in the ID file
    """
    def read_IDs(self) -> list[int]:
        ids = []

        lines = _filehelper.read_file_lines(self.__IDFile)

        for line in lines:
            ids.append(int(line))

        return ids


    """
    Writes an ID to the ID file if it's not already present

        Parameters:
            id (int): unique identifier that should be written to the ID file
    """
    def write_ID(self, id: int):
        ids = self.read_IDs()

        if ids and id in ids:
            raise KeyError("ID already present in ID-File!")

        _filehelper.append_file_lines(self.__IDFile, [str(id)])

        
    """
    Removes an ID from the ID file

        Parameters:
            id (int): ID that should be removed from the ID file (needs to exist)
    """
    def remove_ID(self, id: int):
        ids = self.read_IDs()

        if not id in ids:
            raise KeyError("ID not found in ID-File!")
        
        else:
            ids.remove(id)
        
        _filehelper.write_file(self.__IDFile, [str(el) for el in ids])
