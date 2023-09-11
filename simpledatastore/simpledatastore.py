from dataclasses import dataclass
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
        idFileIDs = self.__idFile.read_IDs()
        idFileIDs = sorted(idFileIDs)

        storeFiles = _filehelper.list_dir_files(self.__storePath)

        storeFileIDs = []

        for fPath in storeFiles:
            curDescriptor = _filehelper.decode_filename(fPath)
            storeFileIDs.append(curDescriptor.ID)

        storeFileIDs = sorted(storeFileIDs)

        if storeFileIDs == idFileIDs:
            return idFileIDs
        
        else:
            # TODO: what if store directory contents and ID-file contents don't match
            return
        
    
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
        self.__idFile.write_ID(id)
        # generate new hash
        # for encoding all content is bundled to single string and UTF-8 encoded
        contentStr = ("").join(content).encode("utf-8")
        contentHash = hashlib.md5(
            contentStr,
            usedforsecurity = False).hexdigest()

        fDescriptor = _filehelper.encode_filename(
            self.__storePath,
            id = id,
            contentHash = contentHash
        )

        _filehelper.create_file(self.__storePath, fDescriptor.filepath.stem())
        _filehelper.write_file(fDescriptor.filepath, content)