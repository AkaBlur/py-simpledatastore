# Py-SimpleDataStore
A simple data storage solution to store small amounts of data in a file-based database. <br><br>


## Concepts
The storage consists of one single folder for all data files, e.g. something like: <br>
`~/my-storage`

Inside the storage all data is stored in seperate files. <br>
`~/my-storage/1234-4163f83b7ab34f965ae128219c2fc692.dat`

Each storage object has an unique ID to be referred to. <br>
**1234**`-4163f83b7ab34f965ae128219c2fc692.dat`

Verification of the storage content is done via simple MD5 hashes. <br>
`1234-`**4163f83b7ab34f965ae128219c2fc692**`.dat`

### ID
- IDs are not generated by the storage <br>
  :point_right: They need to be managed from the outside
- IDs have to be unique `int`
- IDs are stored locally for storage verification inside the store folder as `_ID.dat`

### Content
- Currently only `string` is supported
- One `ID` can only have one specific `string`-list as content <br>
  :point_right: No Duplicates with the same `ID` are allowed!

### Storage Integrity
Integrity of the storage is validated through several steps:
1. No duplicates inside `ID` file
2. No duplicate `ID`s inside the storage itself (files with the same ID)
   
3. Every `ID` inside the `ID` file has to have a file in storage
4. Every `ID` inside the storage has to have an entry inside the `ID` file
   
5. Each stored file has to have a hash that is valid for its stored content

## Usage
### Storage Creation
```python
# storage path as pathlib.Path
storePath = pathlib.Path("mystore")
dataStore = SimpleDataStore(storePath)
```

### Storage Deletion
Deletes the whole store including the files stored on disk.
```python
SimpleDataStore.delete_store()
```
---
### Helper functions
**List IDs**
```python
idList: list[int]
idList = SimpleDataStore.list_IDs()
```

**Check Integrity** <br>
Checks integrity of the store according to the set integrity rules for the storage. <br>
Automatically corrects for errors.
```python
SimpleDataStore.check_integrity()
```

**Hashing function** <br>
Hashing function for the storage files.
```python
SimpleDataStore.calc_hash(content: list[str]) -> str
```

---
### Storage access
**Adding data**
```python
SimpleDataStore.add_storage_file(id: int, content: list[str])
```
**Deleting data**
```python
SimpleDataStore.delete_storage_file(id: int)
```
**Reading data**
```python
SimpleDataStore.read_storage_data(id: int) -> list[str]
```
**Writing data** <br>
Writes data to a storage file.
```python
SimpleDataStore.write_storage_data(id: int, content: list[str])
```
**Appending data** <br>
Appends data to already existing data into a storage file.
```python
SimpleDataStore.append_storage_data(id: int, content: list[str])
```
