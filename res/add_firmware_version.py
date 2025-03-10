import argparse
import pymongo
import os


def count_hex_files(directory):
    """Counts the number of .hex files in the given directory."""
    try:
        return len([f for f in os.listdir(directory) if f.endswith(".hex")])
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 0


def add_firmware(mongo_url, db_name, firmware_version, firmware_path):
    """Connects to MongoDB and adds a firmware version, path, number of chunks, and collection count to 'firmwares'."""
    try:
        client = pymongo.MongoClient(mongo_url)
        db = client[db_name]
        collection = db["firmwares"]

        num_chunks = count_hex_files(firmware_path)
        num_existing_firmwares = collection.count_documents({})  # Get current number of elements

        firmware_data = {
            "version": firmware_version,
            "path": firmware_path,
            "number_of_chunks": num_chunks,
            "number": num_existing_firmwares
        }

        result = collection.insert_one(firmware_data)
        print(f"Firmware added successfully with ID: {result.inserted_id}")
        print(f"Total firmware entries in 'firmwares' collection: {num_existing_firmwares + 1}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        client.close()  # noqa


def main():
    parser = argparse.ArgumentParser(
        description="Add a firmware version, path, number of chunks, and total count to MongoDB.")

    parser.add_argument("-u", "--mongo_url", type=str, required=True,
                        help="MongoDB connection URL (e.g., 'mongodb://localhost:27017')")
    parser.add_argument("-n", "--db_name", type=str, required=True, help="MongoDB database name")
    parser.add_argument("-v", "--firmware_version", type=str, required=True, help="Firmware version")
    parser.add_argument("-p", "--firmware_path", type=str, required=True, help="Path to the firmware directory")

    args = parser.parse_args()

    add_firmware(args.mongo_url, args.db_name, args.firmware_version, args.firmware_path)


if __name__ == "__main__":
    main()
