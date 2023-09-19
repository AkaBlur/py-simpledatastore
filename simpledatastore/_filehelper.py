from dataclasses import dataclass
import os
import pathlib
import re
import shutil



##################################################################
######################## FILE DESCRIPTORS ########################
##################################################################
"""
Class for storing all parameters a file needs for identification

    Members:
        filepath (pathlib.Path): Path to the file
        ID (int): unique ID for the storage object
        contentHash (str): MD5 hash of the content for validation
"""
@dataclass
class FilenameDescriptor:
    filepath: pathlib.Path
    ID: int
    contentHash: str


"""
Decodes a filename and generates the FilenameDescriptor object

    Parameters:
        filepath (pathlib.Path): complete path to the file

    Returns:
        FilenameDescriptor: descriptor object for the file
"""
def decode_filename(filepath: pathlib.Path) -> FilenameDescriptor:
    fileDescriptor = FilenameDescriptor

    if not filepath.exists() or not filepath.is_file():
        raise ValueError("Given file does not exist or is not a file!", str(filepath))

    fileDescriptor.filepath = filepath

    fName = filepath.stem

    fileDescriptor.ID = int(fName.split("_")[0])
    fileDescriptor.contentHash = fName.split("_")[1]

    return fileDescriptor


"""
Encodes necessary information to generate a new file as store object

    Parameters:
        storePath (pathlib.Path): path where the file will be stored
        ID (int): unique ID for the storage object
        contentHash (str): MD5 hash of the content for validation

    Returns:
        FilenameDescriptor: descriptor object for the file
"""
def encode_filename(storePath: pathlib.Path, id: int, contentHash: str) -> FilenameDescriptor:
    fName = str(id) + "_" + contentHash + ".dat"
    fDescriptor = FilenameDescriptor(
        (storePath / pathlib.Path(fName)),
        ID = id,
        contentHash = contentHash
    )

    return fDescriptor


##################################################################
################### FILE CREATION AND DELETION ###################
##################################################################
"""
Creates a directory if not already present

    Parameters:
        path (pathlib.Path): path to create
"""
def mkdir(path: pathlib.Path):
    if not path.exists():
        os.mkdir(path)


"""
Creates a file, if it does not exist yet

    Parameters:
        storePath (pathlib.Path): path where the file will be created
        fname (pathlib.Path): name of the file to be created
"""
def create_file(storePath: pathlib.Path, fname: pathlib.Path):
    fPath = storePath / fname

    # NOTE: if a directory exists a file with the same name can't be created
    if storePath.exists() and not fPath.exists():
        file = open(fPath, "w")
        file.close()


"""
Deletes a single file

    Parameters:
        path (pathlib.Path): file to be removed
"""
def del_file(path: pathlib.Path):
    if path.exists() and path.is_file():
        os.remove(path = path)


"""
Deletes a directory and its contents

    Parameters:
        path (pathlib.Path): path to be deleted
"""
def del_path(path: pathlib.Path):
    if path.exists() and path.is_dir():
        shutil.rmtree(path)


"""
Renames an existing file

    Parameters:
        oldName (pathlib.Path): old filename (file has to exist)
        newName (pathlib.Path): new filename
            ! files have to be in same directory !
"""
def rename_file(oldName: pathlib.Path, newName: pathlib.Path):
    if oldName.exists() and oldName.is_file():
        os.rename(oldName, newName)


##################################################################
#################### FILE AND DIRECTORY STAT #####################
##################################################################
"""
List all files inside a directory

    Parameters:
        path (pathlib.Path): path that should be searched

    Returns:
        list[str]: list of all files found inside given directory
"""
def list_dir_files(path: pathlib.Path) -> list[pathlib.Path]:
    pathFiles = []

    if path.exists() and path.is_dir():
        with os.scandir(path) as pathIt:
            for pathObj in pathIt:
                if pathObj.is_file():
                    pathFiles.append(pathlib.Path(pathObj))

    return pathFiles


"""
Finds a file for a given regex string
Only returns the first occurence

    Parameters:
        path (pathlib.Path): path where to search
        regString (str): regex string for matching <r"put-string-here">

    Returns:
        pathlib.Path: Path object for the found file
"""
def find_file(path: pathlib.Path, regString: str) -> pathlib.Path:
    pathFiles = list_dir_files(path)
    reString = re.compile(regString)

    for file in pathFiles:
        m = reString.match(file.name)

        if m:
            return file
        
    return


##################################################################
######################## FILE READ / WRITE #######################
##################################################################
"""
Writes data to an existing file.
Overwrites every content in the file!

    Parameters:
        filePath (pathlib.Path): full path to the file
        contentLines (list[str]): list of lines to be written to the file
            ! lines will be appended with a newline char !
"""
def write_file(filePath: pathlib.Path, contentLines: list[str]):
    if filePath.exists() and filePath.is_file():
        with open(filePath, "w") as file:
            file.writelines((line + "\n") for line in contentLines)


"""
Append lines to an existing file

    Parameters:
        filePath (pathlib.Path): full path to the file
        contentLines (list[str]): list of lines to be written to the file
            ! lines will be appended with a newline char !
"""
def append_file_lines(filePath: pathlib.Path, contentLines: list[str]):
    if filePath.exists() and filePath.is_file():
        with open(filePath, "a") as file:
            file.writelines((line + "\n") for line in contentLines)


"""
Reads all lines from a file

    Parameters:
        filePath (pathlib.Path): complete path to file

    Returns:
        list[str]: list of all lines, newlines are removed
"""
def read_file_lines(filePath: pathlib.Path) -> list[str]:
    lines = []

    if filePath.exists() and filePath.is_file():
        with open(filePath, "r") as file:
            line = file.readline()

            while line:
                lines.append(line.rstrip("\n")) 

                line = file.readline()

    return lines



