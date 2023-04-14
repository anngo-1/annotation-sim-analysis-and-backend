from google.oauth2 import service_account
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from googleapiclient.discovery import build
import json
import re

#authentification shizzle
creds = service_account.Credentials.from_service_account_file('credentials.json')
service = build('sheets', 'v4', credentials=creds)


app = Flask(__name__)

CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/updatesheet', methods=['POST'])
@cross_origin()
def update():
    response_data = request.get_json()
    sheet_id = get_sheets_id(response_data["link"])
    
    range_name = 'Sheet1!A:B'


    #get current data
    response = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()

    #get values
    values = response.get('values', [])

    #find the last row that contains data
    last_row = len(values)


    #list non hashable so turn into string
    for i in response_data["data"]:
        i["tags_labeled"] = json.dumps(i["tags_labeled"])

    
    userdata = json.loads(json.dumps(response_data["data"]))
    values = [[row['annotator'], row['file_name'], row['tags_labeled'], row["file_num"]] for row in userdata]


    request_body = {
        'values': values
    }
    range_name = f'Sheet1!A{last_row+1}:B{last_row+1}'
    response = service.spreadsheets().values().append(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='USER_ENTERED',
        insertDataOption='INSERT_ROWS',
        body=request_body
    ).execute()

    #print response for error check
    return response





#ANALYZE SPREADSHEET DATA!!!!!
@app.route('/sheetstats', methods=['GET'])
@cross_origin()
def getsheet():
    sheet_id ="1kAJU_RGLNfEAkM1E1Zw909iBDDfKJYblH9o2aWpM9lo" #--> use this specific sheet for now, later will have link parameter
    range_name = 'Sheet1!A:D'
    response = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()

    #get sheet values
    values = response.get('values', []) #values is a list of all the rows [values in row1, values in row2, values in row3, etc...]

    '''
    Here is the general format on how the data is sorted. They are all dictionaries.
    FILES = {
        [image_name] = {
            [attribute_name] = number_of_selection (The amount of people who chose this tag)
        }
        
        ...
    }
    '''
    
    people = set()
    all_attribute = set()
    files = dict()
    
    for i in values:
        # Define the items present in each value in the data.
        person = i[0]
        file_name = i[1]
        tag_array = i[2]
        
        # Add person to the set
        people.add(person)
        
        # Create empty dictionary to hold future tag attributes if the attribute hasn't been marked yet.
        if not file_name in files:
            files[file_name] = dict()
        
        # Go through each attribute
        file_attributes = files[file_name]
        
        # Convert the JSON tag string into an array. (Using regex to seperate the quotation marks "".)
        tag_list = re.findall(r'"(.*?)"', tag_array)
        
        # Go through the attribute in each of the converted taglist and add an attribute if it doesn't already exist.
        # Add the count
        for attribute in tag_list:
            if not attribute in file_attributes:
                file_attributes[attribute] = 0
            
            all_attribute.add(attribute)
            file_attributes[attribute] += 1
            
            
    # DATA ANALYSIS TIME
    '''
    The Data Needed Are As Follows
    Annotator Agreement For Each Attribute
    '''
    json_data = dict()
    total_percentage = 0 # Keep track of the total percentage
    for img_name, attribute_dict in files.items():
         # Go through each attribute to receive the percentage by dividing the number of selections over the total number of people.
         for attribute_name, total_count in attribute_dict.items():
             percent_selected = str((total_count / len(people)) * 100)
             json_data[img_name] = percent_selected
             
             # Add to the total percentage
             total_percentage += percent_selected
                
    
    # Calculate the average
    json_data['average_agreement'] = str(total_percentage / 100)
    print(files)
    print(all_attribute)
    return json_data




#HELPER FUNCTION
def get_sheets_id(url):
    # Extract the sheets ID from the URL
    pattern = r'/spreadsheets/d/([a-zA-Z0-9-_]+)'
    match = re.search(pattern, url)
    
    if match:
        # Return the matched ID
        return match.group(1)
    else:
        # If no match found, return None
        return None


app.run(port=5002)
