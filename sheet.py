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

    response_data = request.args
    sheet_id = get_sheets_id(response_data.get("link"))


    #sheet_id ="1kAJU_RGLNfEAkM1E1Zw909iBDDfKJYblH9o2aWpM9lo" # UNCOMMENT THIS IF YOU WANT TO TEST ON OUR TESTING SPREADSHEET
    range_name = 'Sheet1!A:D'
    response = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()


    #get sheet values
    values = response.get('values', []) #values is a list of all the rows [values in row1, values in row2, values in row3, etc...]
    #values[0] is the FIRST ROW
    #values[0][0] is the NAME of the FIRST ROW
    #values[i][0]  all the names
    # [amanda, an, derrick]
    total_agreement = 0

    setthing = set() #all the file names
    filedictionary = {}

    for i in values:
        setthing.add(i[1]) #--> all names

    total_images = len(setthing)
    images_with_total_agreement = []
    #setthing becomes set of all file names

    for i in setthing:
        filedictionary[i] = []
       
    for row in values:
        filedictionary[row[1]].append(row[2])

    for key, value in filedictionary.items():
        if len(set(value)) == 1:
            total_agreement+=1
            images_with_total_agreement.append(key)


    jsonreturn = {
        "agreement_percentage" : (total_agreement/total_images)*100 ,
        "total_agreement_images": images_with_total_agreement

    }



    
  #  [name, file_name, tags_array,file_num]
    #total_annotator_agreement --> what % of people agree on tags 
    #total agreement (amount of images ALL annotators got right) / all images
    #anarray = [] --> all my annotations
    #amandaarray = [] all annotations
    #derrickarray = [] all anotations



    #most_disagreed_upon_image
    #images with 0 agreements

    #most_agreed_upon_image
    #


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