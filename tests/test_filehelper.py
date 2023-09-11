import hashlib
import os
import pytest
import pathlib

from simpledatastore import _filehelper


@pytest.fixture
def EmptyDirectory() -> pathlib.Path:
    dir = pathlib.Path("")
    return dir


@pytest.fixture
def NewDirectory() -> pathlib.Path:
    dir = pathlib.Path("dir-for-testing")
    return dir


# create directory
def test_mkdir():
    testDir = pathlib.Path("testing")

    _filehelper.mkdir(testDir)

    assert (testDir.exists() and testDir.is_dir())

    os.removedirs(testDir)


# create new file
def test_create_new_file(EmptyDirectory: pathlib.Path):
    testFile = pathlib.Path("testing-new-file.dat")

    _filehelper.create_file(EmptyDirectory, testFile)

    assert (testFile.exists() and testFile.is_file())
    assert (os.path.getsize(testFile) == 0)

    os.remove(testFile)


# don't create file if one already exists
def test_create_existing_file(EmptyDirectory: pathlib.Path):
    testFile = pathlib.Path("testing-new-file.dat")
    testSecondFile = pathlib.Path("testing-new-file.dat")

    _filehelper.create_file(EmptyDirectory, testFile)
    with open(testFile, "w") as file:
        file.write("Testing")

    _filehelper.create_file(EmptyDirectory, testSecondFile)

    assert (testFile.exists() and testFile.is_file())
    assert (not os.path.getsize(testFile) == 0)

    os.remove(testFile)


# can't create file if directory with the same name exists
def test_create_directory_file(EmptyDirectory: pathlib.Path):
    testFile = pathlib.Path("testing-new-file.dat")
    testDir = pathlib.Path("testing-new-file.dat")

    _filehelper.mkdir(testDir)
    _filehelper.create_file(EmptyDirectory, testFile)

    assert (testDir.exists() and testDir.is_dir())
    assert (testFile.exists() and not testFile.is_file())

    os.removedirs(testDir)


# write to file
def test_write_file(EmptyDirectory: pathlib.Path):
    testFile = pathlib.Path("testing.dat")
    testLines = [
        "This",
        "is",
        "a",
        "test",
        "\t42"
    ]

    _filehelper.create_file(EmptyDirectory, testFile)
    _filehelper.write_file(EmptyDirectory / testFile, testLines)

    readLines = []

    with open(testFile, "r") as file:
        line = file.readline().strip("\n")

        while line:
            readLines.append(line)

            line = file.readline().strip("\n")

    os.remove(testFile)

    assert (readLines == testLines)


# append to file
def test_append_file(EmptyDirectory: pathlib.Path):
    testFile = pathlib.Path("testing.dat")
    testLines = [
        "This",
        "is",
        "a",
        "test",
        "\t42"
    ]

    _filehelper.create_file(EmptyDirectory, testFile)
    _filehelper.write_file(EmptyDirectory / testFile, testLines)

    anotherLine = "Appendix"
    
    _filehelper.append_file_lines(EmptyDirectory / testFile, [anotherLine])

    readLines = []

    with open(testFile, "r") as file:
        line = file.readline().strip("\n")

        while line:
            readLines.append(line)

            line = file.readline().strip("\n")

    os.remove(testFile)

    assert (readLines == (testLines + [anotherLine]))


# read from file
def test_read_file(EmptyDirectory: pathlib.Path):
    testFile = pathlib.Path("testing.dat")
    testLines = [
        "This",
        "is",
        "a",
        "test",
        "\t42"
    ]

    _filehelper.create_file(EmptyDirectory, testFile)
    _filehelper.write_file(EmptyDirectory / testFile, testLines)

    readLines = _filehelper.read_file_lines(EmptyDirectory / testFile)

    os.remove(testFile)

    assert (readLines == testLines)


# remove path and its contents
def test_remove_path(NewDirectory: pathlib.Path):
    testFirstFile = pathlib.Path("testing-new-file.dat")
    testSecondFile = pathlib.Path("testing-second-file.dat")

    _filehelper.mkdir(NewDirectory)
    _filehelper.create_file(NewDirectory, testFirstFile)
    _filehelper.create_file(NewDirectory, testSecondFile)

    _filehelper.del_path(NewDirectory)

    assert (not NewDirectory.exists())
    assert (not testFirstFile.exists() and not testSecondFile.exists())


# list path files
def test_list_path_items(NewDirectory: pathlib.Path):
    testFileList = [
        pathlib.Path("testing-first-file.dat"),
        pathlib.Path("testing-second-file.dat"),
        pathlib.Path("testing-third-file.dat"),
        pathlib.Path("testing-fourth-file.dat"),
        pathlib.Path("testing-fifth-file.dat")]
    
    _filehelper.mkdir(NewDirectory)
    
    for file in testFileList:
        _filehelper.create_file(NewDirectory, file)

    readFileList = _filehelper.list_dir_files(NewDirectory)

    # both lists should be sorted, input list may be not
    testFileList = sorted(testFileList)
    readFileList = sorted(readFileList)

    assert (len(readFileList) == len(testFileList))

    for i, testFile in enumerate(testFileList):
        readFile = pathlib.Path(readFileList[i])

        assert (readFile == testFile)

    _filehelper.del_path(NewDirectory)


# check encoding and decoding of filename structure
def test_encode_decode_filename(NewDirectory: pathlib.Path):
    testID = 12
    testContent = [
        "Hello\n",
        "This is a \t test\n"]
    
    contentStr = ("").join(testContent)
    contentStr = contentStr.encode("utf-8")

    testHash = hashlib.md5(contentStr, usedforsecurity = False).hexdigest()

    testFileName = str(testID) + "_" + testHash + ".dat"

    # encoding for generating a new file
    TestDescriptor = _filehelper.encode_filename(
        NewDirectory,
        id = testID,
        contentHash = testHash)
    
    assert (TestDescriptor.filepath == (NewDirectory / pathlib.Path(testFileName)))
    assert (TestDescriptor.ID == testID)
    assert (TestDescriptor.contentHash == testHash)

    # decoding for reading from disk files
    testFile = pathlib.Path(testFileName)
    _filehelper.mkdir(NewDirectory)
    _filehelper.create_file(NewDirectory, testFile)

    ReadDescriptor = _filehelper.decode_filename(NewDirectory / testFile)

    assert (ReadDescriptor.filepath == TestDescriptor.filepath)
    assert (ReadDescriptor.ID == TestDescriptor.ID)
    assert (ReadDescriptor.contentHash == TestDescriptor.contentHash)

    _filehelper.del_path(NewDirectory)