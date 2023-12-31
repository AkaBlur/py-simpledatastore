import pathlib
import pytest

from simpledatastore import _id_file, _filehelper



@pytest.fixture
def TestPath() -> pathlib.Path:
    testPath = pathlib.Path("dir-for-testing")
    _filehelper.mkdir(testPath)
    
    return testPath


@pytest.fixture
def TestIDFile(TestPath: pathlib.Path) -> _id_file.IDFile:
    testIDFile = _id_file.IDFile(TestPath)

    return testIDFile


@pytest.fixture
def TestIDs() -> list[int]:
    testIDs = [
        12, 42, 17, 69, 1337
    ]

    return testIDs


# test creation of ID file in given path
def test_create_IDFile(TestPath: pathlib.Path):
    testIDFile = _id_file.IDFile(TestPath)
    testIDFilepath = TestPath / pathlib.Path("_ID.dat")

    assert (testIDFilepath.exists() and testIDFilepath.is_file())

    _filehelper.del_path(TestPath)


# test the reading of IDs from an ID file
def test_read_IDs(TestPath: pathlib.Path,
                  TestIDFile: _id_file.IDFile,
                  TestIDs: list[int]):
    idFilename = pathlib.Path("_ID.dat")

    _filehelper.write_file(
        TestPath / idFilename,
        [str(el) for el in TestIDs])
    
    readIDs = TestIDFile.read_IDs()

    assert readIDs
    assert (set(TestIDs) == set(readIDs))

    _filehelper.del_path(TestPath)


# test the writing of IDs to the id file
def test_write_IDs(TestPath: pathlib.Path,
                   TestIDFile: _id_file.IDFile,
                   TestIDs: list[int]):
    idFilename = pathlib.Path("_ID.dat")

    for id in TestIDs:
        TestIDFile.add_ID(id)

    readIDs = _filehelper.read_file_lines(TestPath / idFilename)
    
    assert readIDs

    readIDs = [int(el) for el in readIDs]

    assert (set(readIDs) == set(TestIDs))

    # also try writing an ID that already exist
    with pytest.raises(KeyError):
        TestIDFile.add_ID(TestIDs[0])

    _filehelper.del_path(TestPath)


# test removing of IDs from file
def test_remove_ID(TestPath: pathlib.Path,
                   TestIDFile: _id_file.IDFile,
                   TestIDs: list[int]):
    for id in TestIDs:
        TestIDFile.add_ID(id)

    removedIDs = TestIDs[0:2]
    remainingIDs = TestIDs[2:]

    for id in removedIDs:
        TestIDFile.remove_ID(id)

    readIDs = TestIDFile.read_IDs()

    assert (len(readIDs) == len(remainingIDs))
    assert (set(readIDs) == set(remainingIDs))

    # try removing an ID that's already removed

    with pytest.raises(KeyError):
        TestIDFile.remove_ID(removedIDs[0])

    _filehelper.del_path(TestPath)


# test purging of IDs
def test_purge_ids(TestPath: pathlib.Path,
                   TestIDFile: _id_file.IDFile,
                   TestIDs: list[int]):
    for id in TestIDs:
        TestIDFile.add_ID(id)

    TestIDFile.purge_IDs()

    readIDs = TestIDFile.read_IDs()

    assert (len(readIDs) == 0)

    _filehelper.del_path(TestPath)


# test the integrity check of the ID file
def test_check_integrity(TestPath: pathlib.Path,
                         TestIDFile: _id_file.IDFile,
                         TestIDs: list[int]):
    for id in TestIDs:
        TestIDFile.add_ID(id)

    # add additional IDs that should not be addable
    testIDFile = TestPath / pathlib.Path("_ID.dat")
    additionalIDs = TestIDs[:2]
    remainingIDs = TestIDs[2:]

    # double IDs
    _filehelper.append_file_lines(testIDFile, [str(id) for id in additionalIDs])
    # triple IDs
    _filehelper.append_file_lines(testIDFile, [str(id) for id in additionalIDs[:1]])

    TestIDFile.check_integrity()
    readIDs = TestIDFile.read_IDs()

    # integrity check removes double IDs completely from the list
    # so only non-double IDs are kept

    assert (len(remainingIDs) == len(readIDs))
    assert (set(remainingIDs) == set(remainingIDs))

    _filehelper.del_path(TestPath)