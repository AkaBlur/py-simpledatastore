from dataclasses import dataclass
import hashlib
import json
import pathlib
import pytest

import simpledatastore
from simpledatastore import _filehelper



# internal representation of a store file object (for easier handling)
@dataclass
class TestDataFile:
    __test__ = False
    id: int
    content: list[str]


# testing directory
@pytest.fixture
def TestPath() -> pathlib.Path:
    testDir = pathlib.Path("dir-for-testing")
    _filehelper.mkdir(testDir)

    return testDir


# testing data store object
@pytest.fixture
def TestDataStore(TestPath: pathlib.Path) -> simpledatastore.SimpleDataStore:
    testStore = simpledatastore.SimpleDataStore(TestPath)

    return testStore


# random ID values
@pytest.fixture
def TestRandomIDs() -> list[int]:
    return [9958,7644,7300,2513,385]


# one testing store file (contains JSON data)
@pytest.fixture
def TestStoreFile(TestRandomIDs: list[int]) -> TestDataFile:
    jsonContent = dict()
    testFile = pathlib.Path("tests/json-testfiles/json-test0.json")

    with open(testFile, "r") as file:
        jsonContent = json.load(file)

    oneFile = TestDataFile(
        id = TestRandomIDs[0],
        content = [str(jsonContent)]
    )

    return oneFile


# multiple files for testing (containing JSON data)
@pytest.fixture
def TestStoreFiles(TestRandomIDs: list[int]) -> list[TestDataFile]:
    testFiles = []

    for i, id in enumerate(TestRandomIDs):
        jsonContent = dict()
        testFile = pathlib.Path(f"tests/json-testfiles/json-test{i}.json")

        with open(testFile, "r") as file:
            jsonContent = json.load(file)

        oneFile = TestDataFile(
            id = id,
            content = [str(jsonContent)]
        )

        testFiles.append(oneFile)

    return testFiles


# tests creation of store
def test_create_store(TestPath: pathlib.Path,
                      TestDataStore: simpledatastore.SimpleDataStore):
    
    storeIDFile = TestPath / pathlib.Path("_ID.dat")

    assert (storeIDFile.exists() and storeIDFile.is_file())

    _filehelper.del_path(TestPath)


# test loading a store that is already stored on disk
def test_create_existing_store(TestPath: pathlib.Path,
                               TestDataStore: simpledatastore.SimpleDataStore,
                               TestStoreFiles: list[TestDataFile]):
    testIDs = [file.id for file in TestStoreFiles]
    
    # store is created when passing the fixture
    for file in TestStoreFiles:
        TestDataStore.add_storage_file(file.id,
                                       file.content)
        
    # simulating a new storage
    newStore = simpledatastore.SimpleDataStore(TestPath)

    # check existing ID file
    idFile = TestPath / pathlib.Path("_ID.dat")
    assert (idFile and idFile.exists() and idFile.is_file())

    # check IDs inside ID file
    idFileEntries = [
        int(id) for id in _filehelper.read_file_lines(idFile)
    ]

    assert (len(testIDs) == len(idFileEntries))
    assert (set(testIDs) == set(idFileEntries))

    # check file IDs and hashes
    storeFiles = [
        path for path in _filehelper.list_dir_files(TestPath)
        if not path.name[0] == "_"
    ]

    for file in storeFiles:
        curDescriptor = _filehelper.decode_filename(file)

        # find the matching ID in testing set
        testEntry = [
            test for test in TestStoreFiles
            if curDescriptor.ID == test.id
        ]
        assert (len(testEntry) == 1)

        testEntry = testEntry[0]
        
        # calculate hash from test data
        testHash = newStore.calc_hash(testEntry.content)

        # check ID and hash against test data
        assert (curDescriptor.ID == testEntry.id)
        assert (curDescriptor.contentHash == testHash)

    _filehelper.del_path(TestPath)


# tests deletion of the store
def test_del_store(TestPath: pathlib.Path,
                   TestDataStore: simpledatastore.SimpleDataStore):
    storeIDFile = TestPath / pathlib.Path("_ID.file")
    TestDataStore.delete_store()

    assert (not storeIDFile.exists())

    _filehelper.del_path(TestPath)


# test for adding a data file
def test_add_storage_file(TestPath: pathlib.Path,
                          TestDataStore: simpledatastore.SimpleDataStore,
                          TestStoreFile: TestDataFile):
    TestDataStore.add_storage_file(TestStoreFile.id,
                                   TestStoreFile.content)
    
    # store should create an entry inside ID file
    storeIDFile = TestPath / pathlib.Path("_ID.dat")
    readID = _filehelper.read_file_lines(storeIDFile)

    assert (readID and int(readID[0]) == TestStoreFile.id)

    # store should create a file for the store object
    # filename has to follow with ID and hash value
    listStoreFile = [
        path for path in _filehelper.list_dir_files(TestPath)
        if not path.name[0] == "_"]
    assert (listStoreFile and len(listStoreFile) == 1)
    assert (listStoreFile[0].exists() and listStoreFile[0].is_file())

    # ID in filename
    testDescriptor = _filehelper.decode_filename(listStoreFile[0])
    assert (testDescriptor.ID == TestStoreFile.id)

    # hash in filename
    checkHash = TestDataStore.calc_hash(TestStoreFile.content)
    assert (testDescriptor.contentHash == checkHash)

    # file content
    readFilelines = _filehelper.read_file_lines(listStoreFile[0])
    assert (len(readFilelines) == len(TestStoreFile.content))
    assert (set(readFilelines) == set(TestStoreFile.content))

    # store should not add a file if the ID is already used
    with pytest.raises(ValueError):
        TestDataStore.add_storage_file(TestStoreFile.id,
                                       TestStoreFile.content)

    _filehelper.del_path(TestPath)


# test for deleting a store file
def test_delete_storage_file(TestPath: pathlib.Path,
                             TestDataStore: simpledatastore.SimpleDataStore,
                             TestStoreFile: TestDataFile):
    TestDataStore.add_storage_file(TestStoreFile.id,
                                 TestStoreFile.content)
    TestDataStore.delete_storage_file(TestStoreFile.id)

    # store should delete ID entry in ID file
    storeIDFile = TestPath / pathlib.Path("_ID.dat")
    readID = _filehelper.read_file_lines(storeIDFile)
    readID = [int(id) for id in readID]

    assert (TestStoreFile.id not in readID)

    # store should delete storage file
    listStoreFile = [
        path for path in _filehelper.list_dir_files(TestPath)
        if not path.name[0] == "_"
    ]
    
    assert (len(listStoreFile) == 0)

    # error should be raised on deleting an already deleted file
    with pytest.raises(ValueError):
        TestDataStore.delete_storage_file(TestStoreFile.id)

    _filehelper.del_path(TestPath)


# test for listing all IDs from stored objects
def test_list_ID(TestPath: pathlib.Path,
                 TestDataStore: simpledatastore.SimpleDataStore,
                 TestStoreFiles: list[TestDataFile]):
    for testFile in TestStoreFiles:
        TestDataStore.add_storage_file(testFile.id,
                                       testFile.content)
        
    testIDs = [file.id for file in TestStoreFiles]
    readIDs = TestDataStore.list_IDs()

    assert (len(testIDs) == len(readIDs))
    assert (set(testIDs) == set(readIDs))

    _filehelper.del_path(TestPath)


# test for reading the content of a file
def test_read_storage_data(TestPath: pathlib.Path,
                           TestDataStore: simpledatastore.SimpleDataStore,
                           TestStoreFile: TestDataFile):
    TestDataStore.add_storage_file(TestStoreFile.id,
                                    TestStoreFile.content)
    
    testContent = TestStoreFile.content
    readContent = TestDataStore.read_storage_data(TestStoreFile.id)

    assert (len(testContent) == len(readContent))
    assert (set(testContent) == set(readContent))

    _filehelper.del_path(TestPath)


# test for writing content to an existing file
def test_write_storage_data(TestPath: pathlib.Path,
                            TestDataStore: simpledatastore.SimpleDataStore,
                            TestStoreFiles: list[TestDataFile]):
    TestFile = TestStoreFiles[0]

    TestDataStore.add_storage_file(TestFile.id,
                                    TestFile.content)
    
    anotherContent = TestStoreFiles[1].content

    TestDataStore.write_storage_data(TestFile.id,
                                     anotherContent)
    NewFDescriptor = _filehelper.encode_filename(
        TestPath,
        TestFile.id,
        TestDataStore.calc_hash(anotherContent)
    )

    readFile = _filehelper.find_file(TestPath, NewFDescriptor.filepath.name)

    assert (readFile.exists() and readFile.is_file())

    readContent = TestDataStore.read_storage_data(TestFile.id)

    assert (len(anotherContent) == len(readContent))
    assert (set(anotherContent) == set(readContent))

    _filehelper.del_path(TestPath)


# test for appending content to an existing file
def test_append_storage_data(TestPath: pathlib.Path,
                             TestDataStore: simpledatastore.SimpleDataStore,
                             TestStoreFiles: list[TestDataFile]):
    TestFile = TestStoreFiles[0]
    TestDataStore.add_storage_file(TestFile.id,
                                    TestFile.content)
    
    anotherContent = TestStoreFiles[1].content
    testContent = TestFile.content + anotherContent

    TestDataStore.append_storage_data(TestFile.id,
                                      anotherContent)
    NewFDescriptor = _filehelper.encode_filename(
        TestPath,
        TestFile.id,
        TestDataStore.calc_hash(testContent)
    )

    readFile = _filehelper.find_file(TestPath, NewFDescriptor.filepath.name)

    assert (readFile.exists() and readFile.is_file())

    readContent = TestDataStore.read_storage_data(TestFile.id)

    assert (len(testContent) == len(readContent))
    assert (set(testContent) == set(readContent))

    _filehelper.del_path(TestPath)


# test hash calculation
def test_calc_hash(TestPath: pathlib.Path,
                   TestDataStore: simpledatastore.SimpleDataStore,
                   TestStoreFile: TestDataFile):
    contentStr = ("").join(TestStoreFile.content).encode("utf-8")
    testHash = hashlib.md5(contentStr, usedforsecurity = False).hexdigest()

    readHash = TestDataStore.calc_hash(TestStoreFile.content)

    assert (readHash == testHash)

    _filehelper.del_path(TestPath)


##################################################################
################## INTEGRITY CHECKING FUNCTIONS ##################
##################################################################

# mulitple IDs inside store directory
def test_integrity_multiID(TestPath: pathlib.Path,
                           TestDataStore: simpledatastore.SimpleDataStore,
                           TestStoreFiles: list[TestDataFile]):
    # regular files added to store
    for storeFile in TestStoreFiles:
        TestDataStore.add_storage_file(storeFile.id,
                                      storeFile.content)
    
    # generate some fake files and add them to the store
    singleFiles = TestStoreFiles[2:]
    doubleFiles = TestStoreFiles[:2]

    # content needs to be switched to ensure a different hash
    doubleFiles[0].content = TestStoreFiles[2].content
    doubleFiles[1].content = TestStoreFiles[3].content

    for file in doubleFiles:
        dID = file.id
        dHash = TestDataStore.calc_hash(file.content)

        doubleFilename = str(dID) + "_" + dHash + ".dat"

        _filehelper.create_file(
            TestPath,
            pathlib.Path(doubleFilename))
        
    TestDataStore.check_integrity()

    readFiles = [
        path for path in _filehelper.list_dir_files(TestPath)
        if not path.name[0] == "_"
    ]
    readIDs = []

    for file in readFiles:
        curDescriptor = _filehelper.decode_filename(file)
        readIDs.append(curDescriptor.ID)

    # after integrity check only files with single occurence remain
    singleIDs = [fileData.id for fileData in singleFiles]
    
    assert (len(singleIDs) == len(readIDs))
    assert (set(singleIDs) == set(readIDs))

    # cross checking with IDs in ID file
    idFileIDs = _filehelper.read_file_lines(
        TestPath / pathlib.Path("_ID.dat"))
    
    idFileIDs = [int(id) for id in idFileIDs]

    assert (len(singleIDs) == len(idFileIDs))
    assert (set(singleIDs) == set(idFileIDs))

    _filehelper.del_path(TestPath)


# mismatch between the ID file IDs and the actually store objects
def test_integrity_mismatchID(TestPath: pathlib.Path,
                              TestDataStore: simpledatastore.SimpleDataStore,
                              TestStoreFiles: list[TestDataFile]):
    # generate some fake files and add them to the store
    legitFiles = TestStoreFiles[2:]
    ghostFiles = TestStoreFiles[:2]

    # regular files added to store
    for storeFile in legitFiles:
        TestDataStore.add_storage_file(storeFile.id,
                                      storeFile.content)

    for file in ghostFiles:
        dID = file.id
        dHash = TestDataStore.calc_hash(file.content)

        doubleFilename = str(dID) + "_" + dHash + ".dat"

        _filehelper.create_file(
            TestPath,
            pathlib.Path(doubleFilename))
        
    TestDataStore.check_integrity()

    readFiles = [
        path for path in _filehelper.list_dir_files(TestPath)
        if not path.name[0] == "_"
    ]
    readIDs = []

    for file in readFiles:
        curDescriptor = _filehelper.decode_filename(file)
        readIDs.append(curDescriptor.ID)

    # after integrity check only files with IDs in the ID file remain
    legitIDs = [fileData.id for fileData in legitFiles]
    
    assert (len(legitIDs) == len(readIDs))
    assert (set(legitIDs) == set(readIDs))

    # cross checking with IDs in ID file
    idFileIDs = _filehelper.read_file_lines(
        TestPath / pathlib.Path("_ID.dat"))
    
    idFileIDs = [int(id) for id in idFileIDs]

    assert (len(legitIDs) == len(idFileIDs))
    assert (set(legitIDs) == set(idFileIDs))

    _filehelper.del_path(TestPath)


# hash error in the calculated hash (from file content)
# and the given hash from the filename
def test_integrity_hash_error(TestPath: pathlib.Path,
                              TestDataStore: simpledatastore.SimpleDataStore,
                              TestStoreFiles: list[TestDataFile]):
    # regular files added to store
    for storeFile in TestStoreFiles:
        TestDataStore.add_storage_file(storeFile.id,
                                      storeFile.content)
        
    # overwrite content of some of the files
    legitFiles = TestStoreFiles[3:]
    kaputFiles = TestStoreFiles[:3]

    for file in kaputFiles:
        id = file.id
        # for ease in testing only the ID is taken for content
        # hash remains the same in the name
        fakeContent = [str(id)]
        realHash = TestDataStore.calc_hash(file.content)

        filename = str(id) + "_" + realHash + ".dat"

        _filehelper.write_file(TestPath / pathlib.Path(filename),
                               fakeContent)
        
    TestDataStore.check_integrity()

    readFiles = [
        path for path in _filehelper.list_dir_files(TestPath)
        if not path.name[0] == "_"
    ]
    readIDs = []

    for file in readFiles:
        curDescriptor = _filehelper.decode_filename(file)
        readIDs.append(curDescriptor.ID)

    # after integrity check files with wrong hash get deleted
    # only valid ones remain
    legitIDs = [fileData.id for fileData in legitFiles]
    
    assert (len(legitIDs) == len(readIDs))
    assert (set(legitIDs) == set(readIDs))

    # cross checking with IDs in ID file
    idFileIDs = _filehelper.read_file_lines(
        TestPath / pathlib.Path("_ID.dat"))
    
    idFileIDs = [int(id) for id in idFileIDs]

    assert (len(legitIDs) == len(idFileIDs))
    assert (set(legitIDs) == set(idFileIDs))

    _filehelper.del_path(TestPath)