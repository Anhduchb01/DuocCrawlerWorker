import re
from datetime import datetime
import dateutil.parser
month_translation_dict = {
    "tháng một": "january",
    "tháng hai": "february",
    "tháng ba": "march",
    "tháng bốn": "april",
    "tháng năm": "may",
    "tháng sáu": "june",
    "tháng bảy": "july",
    "tháng tám": "august",
    "tháng chín": "september",
    "tháng mười một": "november",
    "tháng mười hai": "december",
    "tháng mười": "october",
    "tháng 11": "november",
    "tháng 10": "october",
    "tháng 12": "december",
    "tháng 1": "january",
    "tháng 2": "february",
    "tháng 3": "march",
    "tháng 4": "april",
    "tháng 5": "may",
    "tháng 6": "june",
    "tháng 7": "july",
    "tháng 8": "august",
    "tháng 9": "september"
    
}
acronym_month_dict = {
    "jan": "january",
    "feb": "february",
    "mar": "march",
    "apr": "april",
    "may": "may",
    "jun": "june",
    "jul": "july",
    "aug": "august",
    "sep": "september",
    "oct": "october",
    "nov": "november",
    "dec": "december"
}


def convert_to_custom_format(input_string):
    for vietnamese_month, english_month in month_translation_dict.items():
        input_string = input_string.lower()
        input_string = input_string.strip()
        input_string = input_string.replace('/',' ')
        input_string = input_string.replace('-',' ')
        input_string = input_string.replace(',',' ')
        input_string = input_string.replace(')',' ')
        input_string = input_string.replace('(',' ')
        input_string = input_string.replace('.',' ')
        input_string = input_string.replace(';',' ')
        input_string = input_string.replace('|',' ')
        input_string = input_string.replace(vietnamese_month, english_month)
    check_full_num = True
    input_words = [word for word in input_string.split() if word ]
    result = []
    for word in input_words:
        if not word.isnumeric():
            check_full_num = False
        if word in month_translation_dict.values() or word.isnumeric() or word in acronym_month_dict.keys():
            for acronym_month, english_month in acronym_month_dict.items():
                if word == acronym_month:
                    word = english_month
            result.append(word)
    cleaned_datestring = " ".join(result)
    new_date = dateutil.parser.parse(cleaned_datestring)
    new_date_parse = dateutil.parser.parse(cleaned_datestring)
    new_date_final = new_date.strftime("%Y/%m/%d")
    print(new_date_final)
    if check_full_num :
        year, month, day = map(int, new_date_final.split('/'))
        if day <= 12:
            new_date_final = new_date.strftime("%Y/%d/%m")
    return new_date_final

def update_date_time():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.duoc1
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
def convert_to_custom_format1(datestring):
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

    

    try:
        yourdate = dateutil.parser.parse(datestring)
        formatted_date = yourdate.strftime("%Y/%m/%d")
        if yourdate > datetime.now():
            # Swap month and day parts
            formatted_date = yourdate.strftime("%Y/%d/%m")

        return formatted_date

    except ValueError:
        
        for format_string in formats_to_check:
            try:
                datetime_object = datetime.strptime(datestring, format_string)
                formatted_date = datetime_object.strftime('%Y/%m/%d')
                if yourdate > datetime.now():
                    # Swap month and day parts
                    formatted_date = yourdate.strftime("%Y/%d/%m")
                return formatted_date
            except ValueError:
                cleaned_datestring = re.sub(r'[^0-9/:\-]', ' ', datestring)
                cleaned_datestring = re.sub(r'\s+', ' ', cleaned_datestring).strip()
                datetime_object = datetime.strptime(datestring, format_string)
                formatted_date = datetime_object.strftime('%Y/%m/%d')
                if yourdate > datetime.now():
                    # Swap month and day parts
                    formatted_date = yourdate.strftime("%Y/%d/%m")
                return formatted_date
        
        return ''  # If no valid format is found
from pymongo import MongoClient

from tqdm import tqdm
if __name__ == '__main__':  
    client = MongoClient('mongodb://localhost:27017/')
    db = client.duoc1
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

