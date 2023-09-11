import re
from datetime import datetime
import dateutil.parser

def convert_to_custom_format(datestring):
    # Define a list of formats to check
    formats_to_check = [
        "%d-%m-%Y - %H:%M %p",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y/%m/%d %I:%M %p",
        "%d/%m/%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%d/%m/%Y %I:%M %p",
    ]

    cleaned_datestring = re.sub(r'[^0-9/:\-]', ' ', datestring)
    cleaned_datestring = re.sub(r'\s+', ' ', cleaned_datestring).strip()

    try:
        yourdate = dateutil.parser.parse(cleaned_datestring)
        formatted_date = yourdate.strftime("%Y/%m/%d")
        return formatted_date
    except ValueError:
        for format_string in formats_to_check:
            try:
                datetime_object = datetime.strptime(datestring, format_string)
                formatted_date = datetime_object.strftime('%Y/%m/%d')
                return formatted_date
            except ValueError:
                pass
        
        return None  # If no valid format is found
from pymongo import MongoClient

from tqdm import tqdm
if __name__ == '__main__':  
    client = MongoClient('mongodb://localhost:27017/')
    db = client.Duoc
    posts_collection = db.posts
    query = {
    "timeCreatePostOrigin": {
        "$nin": [None, "None"]
        }
    }
    total_count = posts_collection.count_documents(query)
    with tqdm(total=total_count) as pbar:
        for post in posts_collection.find(query):
            old_date = post["timeCreatePostOrigin"]
            new_date = convert_to_custom_format(old_date)
            if new_date is not None:
                # Update the document with the new date
                posts_collection.update_one(
                    {"_id": post["_id"]},
                    {"$set": {"timeCreatePostOrigin": new_date}}
                )
            pbar.update(1)
    # Close the MongoDB connection
    client.close()

