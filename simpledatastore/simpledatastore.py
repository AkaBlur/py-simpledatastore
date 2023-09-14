import hashlib
import pathlib

import _filehelper
import _id_file



"""
Simple data storage that works on small files stored inside a local directory
Identification for each stored object is via IDs
IDs are NOT generated
    -> tracking of which ID can be used should be done manually
Data validation is done via simple MD5 hashes

    Parameters:
        path (pathlib.Path): storage path for the data store
"""
class SimpleDataStore:
    __storePath: pathlib.Path


    #####################################################################
    ###################### GENERAL STORAGE OPTIONS ######################
    #####################################################################
    def __init__(self, path: pathlib.Path):
        self.__storePath = path

        _filehelper.mkdir(path)
        self.__IDFile = _id_file.IDFile(self.__storePath)


    """
    Deletes the store completely (ID file and data files)
    """
    def delete_store(self):
        _filehelper.del_path(self.__storePath)


    """
    Lists alls IDs that are currently inside the store

        Returns:
            list[int]: list of currently stored IDs
    """
    def list_IDs(self) -> list[int]:
        idFileIDs = self.__IDFile.read_IDs()

        storeFiles = _filehelper.list_dir_files(self.__storePath)
        storeFileIDs = []

        for fPath in storeFiles:
            curDescriptor = _filehelper.decode_filename(fPath)
            storeFileIDs.append(curDescriptor.ID)

        if set(storeFileIDs) == set(idFileIDs):
            return idFileIDs
        
        else:
            # TODO: what if store directory contents and ID-file contents don't match
            return
        
    
    """
    Checks the integrity of the store
    IDs listed inside the ID file are checked against the available files
    Also within the files all hashes are checked if correct
    """
    def check_integrity(self):
        # integrity check of ID file
        self.__IDFile.check_integrity()
        idFileIDs = self.__IDFile.read_IDs()

        # IDs of all store files
        storeFileIDs = []

        for fPath in _filehelper.list_dir_files(self.__storePath):
            curDescriptor = _filehelper.decode_filename(fPath)
            storeFileIDs.append(curDescriptor.ID)


        ################################################################
        # ERROR: multiple IDs in file storage
        # -> all occurences get deleted
        doubles = []
        for id in set(storeFileIDs):
            if storeFileIDs.count(id) > 1:
                doubles.append(id)

        if len(doubles) > 0:
            # remove doubles
            self.__remove_file_by_id(doubles)

            # remove from original ID list
            storeFileIDs = list(set(storeFileIDs))
            for el in doubles:
                storeFileIDs.remove(el)


        ################################################################
        # ERROR: ID mismatch between ID file and store files
        if not len(storeFileIDs) == len(idFileIDs) or set(storeFileIDs) == set(idFileIDs):
            # ID file has always priority
            idToDelete = [id for id in storeFileIDs if not id in idFileIDs]

            self.__remove_file_by_id(idToDelete)


        ################################################################
        # ERROR: hash value of content is mismatched with filename
        # -> file gets removed from store
        storeFiles = _filehelper.list_dir_files(self.__storePath)
        for file in storeFiles:
            content = _filehelper.read_file_lines(file)
            curDescriptor = _filehelper.decode_filename(file)

            hash = self.calc_hash(content = content)

            if not hash == curDescriptor.contentHash:
                _filehelper.del_file(file)


        # update ID file
        storeFiles = _filehelper.list_dir_files(self.__storePath)
        newIDs = []
        for file in storeFiles:
            curDescriptor = _filehelper.decode_filename(file)
            newIDs.append(curDescriptor.ID)

        self.__IDFile.purge_IDs()
        for id in newIDs:
            self.__IDFile.add_ID(id)


    #####################################################################
    ################## STORAGE DATA (FILES) OPERATIONS ##################
    #####################################################################
    """
    Adds a storage object (file)

        Parameters:
            id (int): unique identifier used for the store object
            content (list[str]): list of strings stored as content inside the data store
    """
    def add_storage_file(self, id: int, content: list[str]):
        ids = self.list_IDs()

        if id in ids:
            raise ValueError("ID already used in store!")
        
        # write ID to ID-file
        self.__IDFile.add_ID(id)
        # generate new hash
        contentHash = self.calc_hash(content)

        fDescriptor = _filehelper.encode_filename(
            self.__storePath,
            id = id,
            contentHash = contentHash
        )

        _filehelper.create_file(self.__storePath, fDescriptor.filepath.stem())
        _filehelper.write_file(fDescriptor.filepath, content)


    def delete_storage_file(self, id: int):
        ...

    
    def read_storage_data(self, id: int) -> list[str]:
        ...


    def write_storage_data(self, id: int, content: list[str]):
        ...


    def append_storage_data(self, id: int, content: list[str]):
        ...


    """
    Hashing function for each storage file object
    
        Parameters:
            content (list[str]): list of lines of content inside the storage file

        Returns:
            str: hash value for the given content as string
    """
    def calc_hash(self, content: list[str]) -> str:
        # for encoding all content is bundled to single string and UTF-8 encoded
        contentStr = ("").join(content).encode("utf-8")
        hash = hashlib.md5(contentStr, usedforsecurity = False).hexdigest()

        return hash
    

    """
    Removes files by their respecting IDs
    
        Parameters:
            id (int): IDs to remove from the store
    """
    def __remove_file_by_id(self, idList: list[int]):
        for fPath in _filehelper.list_dir_files(self.__storePath):
            curDesc = _filehelper.decode_filename(fPath)

            if curDesc.ID in idList:
                _filehelper.del_file(fPath)