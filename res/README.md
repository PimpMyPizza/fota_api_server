# Firmware Upload Script for FOTA

The script `add_firmware_version.py` allows you to register a new firmware version in a MongoDB database. The firmware consists of multiple `.hex` chunks, and this script records the firmware version, its storage path, and the number of chunks in the **firmware** collection. This information will be used in the API for **Firmware Over-The-Air (FOTA) updates**.

## 🛠️ Prerequisites

Before using the script, ensure you have:

- Python 3 installed
- MongoDB running and accessible
- The required Python package `pymongo` installed:

```sh
pip install pymongo
```

## 🚀 Usage

Run the script with the following command:

```sh
python add_firmware_version.py -u <mongo_url> -n <db_name> -v <firmware_version> -p <firmware_path>
```

## 📌 Example Usage:

````sh
python add_firmware_version.py -u "mongodb://localhost:27017" -n "fota_server" -v "1.0.5" -p "./firmware/1.0.5/"
````

## How It Works:

1. The script connects to MongoDB.
2. It counts the number of `.hex` files in the specified directory.
3. It inserts a document into the `firmwares` collection with:
```json
{
  "version": "1.0.5",
  "path": "/path/to/firmware/directory/containing/firmware/chunks/",
  "number_of_chunks": 3,
  "number": 1
}
```
Note that `number` represents the unique id of the firmware. The firmware with the greatest `number` is defined as `latest`.
4. The API can then use this data for FOTA updates.

## 🔍 Verifying the Data

After running the script, you can check the stored data in MongoDB by using:

```
mongo
use firmware_db
db.firmware.find().pretty()
```

## ⚠️ Notes:

- Ensure that the firmware directory contains only the necessary .hex files.
- If the specified path is incorrect or inaccessible, the script will return an error.