from google.oauth2 import service_account
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from googleapiclient.discovery import build
import json
import re
import numpy as np
import statistics

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
    tags_used = response_data.get("tags_used")


    # sheet_id ="1-eveLZg1SCz2aMkvtxKCTyq1UdAfPglQ0foM1XL9o60" # UNCOMMENT THIS IF YOU WANT TO TEST ON OUR TESTING SPREADSHEET
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
    values_transpose = np.array(values).T.tolist()
    images = sorted(set(values_transpose[1]))

    total_images = len(images)

    # put the lists of tags into a list of nested lists
    tag_arrays = [[] for _ in range(total_images)]
    for i in range(len(values_transpose[2])):
        index = images.index(values_transpose[1][i])
        user_image_tags = re.findall(r'"(.*?)"', values_transpose[2][i])
        tag_arrays[index].append(user_image_tags)
    # print(tag_array)

    # analyze the data by getting most common tag for each attribute for each image
    results = []
    i = 0
    for arr in tag_arrays:
        arr_transpose = np.array(arr).T.tolist()
        print(arr_transpose)
        s = images[i] + "\n"
        for lis in arr_transpose:
            most_freq_tag = statistics.mode(lis)
            percent = (lis.count(most_freq_tag)/len(lis)) * 100
            s += most_freq_tag + ": " + str(percent) + "%\n"
        print(s)
        results.append(s)
        i += 1
    
    print(results)

            
    # images_with_total_agreement = []
    
    # for i in setthing:
    #     filedictionary[i] = []
       
    # for row in values:
    #     filedictionary[row[1]].append(row[2])

    # for key, value in filedictionary.items():
    #     if len(set(value)) == 1:
    #         total_agreement+=1
    #         images_with_total_agreement.append(key)


    jsonreturn = {
        "tags_used" :tags_used,
        "agreement_by_image" : results,
        # "total_agreement_images": images_with_total_agreement

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




@app.route('/bitmojiequivalent', methods=['GET'])
@cross_origin()
def bitmojiequivalent():
    response_data = request.args
    tags_used = response_data.get("tags_used") #tags_used = [1,2,3,4]



    tagsandimages = {}







    jsonreturn = {
        "tagsandbitmojis":tagsandimages #an array of images that best match the tag array that was just sent

    }





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