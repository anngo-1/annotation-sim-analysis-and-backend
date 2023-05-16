from google.oauth2 import service_account
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from googleapiclient.discovery import build
import json
import re
# import numpy as np
# import statistics
import pandas as pd
from imagefile import ImageFile
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


#pandas settings
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', None)
#ANALYZE SPREADSHEET DATA!!!!!
@app.route('/sheetstats', methods=['GET'])
@cross_origin()
def getsheet():

    response_data = request.args
    sheet_id = get_sheets_id(response_data.get("link"))
    tags_used = response_data.get("tags_used")


    # sheet_id ="1vJwuC8jh6kq9Zrcqm_VzhXGJMvvrkx1OBPD_L-Oo6hw" # UNCOMMENT THIS IF YOU WANT TO TEST ON OUR TESTING SPREADSHEET
    # sheet_id = "1gAZCF9RJ_IJxS8NBxZFDMGJ3PeHxqCCUHtAHe8bXviY"
    range_name = 'Sheet1!A:D'
    response = service.spreadsheets().values().get(
        spreadsheetId=sheet_id,
        range=range_name
    ).execute()


    #get sheet values
    values = response.get('values', []) #values is a list of all the rows [values in row1, values in row2, values in row3, etc...]

    values_df = pd.DataFrame(values, columns = ["Annotator", "File Name", "Tags", "File Num"])
    image_names = sorted(set(values_df["File Name"]))
    values_df.sort_values(by="File Name", inplace = True, ignore_index=True)
    # print(values_df)
    # print(images)

    tag_list = []
    for tag in values_df["Tags"]:
        user_image_tags = re.findall(r'"(.*?)"', tag)
        tag_list.append(user_image_tags)
        # print(user_image_tags)
    # print(tag_df)

    num_tags = len(user_image_tags)
    tag_df = pd.DataFrame(tag_list, columns = ["Tag {}".format(i) for i in range(num_tags)])
    print(tag_df)

    values_df = pd.concat([values_df, tag_df], axis = 1, join='inner')
    print(values_df)

    image_files = list()
    for image in image_names:
        image_df = values_df.loc[values_df["File Name"] == image, ["Tag {}".format(i) for i in range(num_tags)]]
        image_files.append(ImageFile(image, image_df))
        # print(image_df)
        
    for im in image_files:
        # print(im)
        agreement_list = []
        for column in im.all_tags_df:
            # print(im.all_tags_df)
            # print(im.all_tags_df[column])
            agreed_tags = im.all_tags_df[column].mode().tolist()

            occurences = im.all_tags_df[column].value_counts()[agreed_tags[0]]
            percentage = (occurences / len(im.all_tags_df)) * 100 if occurences > 1 else 0

            agreement_list.append(tuple((agreed_tags, percentage)))
            # print(agreed_tags)
            # print(percentage)
            # im.per_tag_agreement = agreement
        agreement_df = pd.DataFrame(agreement_list, columns = ["Agreed Tags", "Percentage"])
        im.agreement_df = agreement_df
        im.total_agreement = agreement_df["Percentage"].sum() / len(agreement_df)
        print(im.agreement_df)
        print(im.total_agreement)
        # print(im)
        
    total_agreement = 0
   
    results = []
    for im in image_files:
        results.append(im.print_agreement())
        total_agreement += im.total_agreement
    
    overall_agreement = total_agreement/len(image_files)

    
    jsonreturn = {
        "tags_used" :tags_used,
        "agreement/image" : results,
        "agreement_percentage": overall_agreement

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