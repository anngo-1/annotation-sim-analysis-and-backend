from google.oauth2 import service_account
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from googleapiclient.discovery import build
import numpy as np
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

    
    people = set()
    all_attribute = set()
    files = dict()
    
    for i in values:
        # Define items
        person = i[0]
        file_name = i[1]
        tag_array = i[2]
        
        # Add person to the set
        people.add(person)
        
        if not file_name in files:
            files[file_name] = dict()
        
        # Go through each attribute
        file_attributes = files[file_name]
        
        tag_list = re.findall(r'"(.*?)"', tag_array)
            
        for attribute in tag_list:
            if not attribute in file_attributes:
                file_attributes[attribute] = 0
            
            all_attribute.add(attribute)
            file_attributes[attribute] += 1
            
            


    #output arrays/variables
    total_agreement_count = 0
    for key, value in files.items():
        if np.unique(list(value.values())).size == 1: #if there is TOTAL annotator agremeent
            total_agreement_count+=1
    

    jsonreturn = {
        "TOTAL_annotator_agreement": total_agreement_count/len(files)
    }
            
        
        
        
    
    print(files)
    print(all_attribute)
    print(total_agreement_count)
    print(len(files))
    return jsonreturn




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