from google.oauth2 import service_account
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from googleapiclient.discovery import build
import json
import re
import numpy as np
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





#ANALYZE SPREADSHEET DATA!!!!!
@app.route('/sheetstats', methods=['GET'])
@cross_origin()
def getsheet():

    response_data = request.args
    # sheet_id = get_sheets_id(response_data.get("link"))
    tags_used = response_data.get("tags_used")


    sheet_id ="1-eveLZg1SCz2aMkvtxKCTyq1UdAfPglQ0foM1XL9o60" # UNCOMMENT THIS IF YOU WANT TO TEST ON OUR TESTING SPREADSHEET
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

    # total_agreement = 0
    # values_transpose = np.array(values).T.tolist()
    values_df = pd.DataFrame(values, columns = ["Annotator", "File Name", "Tags", "File Num"])
    image_names = sorted(set(values_df["File Name"]))
    values_df.sort_values(by="File Name", inplace = True)
    # print(values_df)
    # print(images)

    total_images = len(image_names)
    # print(values_df["Tags"])

    df_created = False
    for tag in values_df["Tags"]:
        user_image_tags = re.findall(r'"(.*?)"', tag)
        if df_created == False:
            num_tags = range(len(user_image_tags))
            tag_df = pd.DataFrame(columns = ["Tag {}".format(i) for i in num_tags])
            df_created = True
        tag_df.loc[len(tag_df)] = user_image_tags
        # print(user_image_tags)
    # print(tag_df)

    values_df = pd.concat([values_df, tag_df], axis = 1)
    print(values_df)

    image_files = list()
    for image in image_names:
        image_df = values_df.loc[values_df["File Name"] == image, ["Tag {}".format(i) for i in num_tags]]
        image_files.append(ImageFile(image, image_df))
        # print(image_df)
        
    for im in image_files:
        # print(im)
        for column in im.df:
            print(im.df)
            # print(im.df[column])
            agreement = im.df[column].mode()

            occurences = im.df[column].value_counts()[agreement[0]]
            percentage = occurences / len(im.df) if occurences > 1 else 0
            
            # im.per_tag_agreement = agreement
        # print(im)
        


    # # put the lists of tags into a list of nested lists
    # tag_arrays = [[] for _ in range(total_images)]
    # for i in range(len(values_transpose[2])):
    #     index = images.index(values_transpose[1][i])
    #     user_image_tags = re.findall(r'"(.*?)"', values_transpose[2][i])
    #     tag_arrays[index].append(user_image_tags)
    # print(tag_arrays)



    # # analyze the data by getting most common tag for each attribute for each image
    # results = [[] for _ in range(total_images)]
    # tags = [[] for _ in range(total_images)]
    # i = 0
    # for arr in tag_arrays:
    #     arr_transpose = np.array(arr).T.tolist()
    #     file_df = pd.DataFrame(arr_transpose)
    #     print(file_df)
    #     print(arr_transpose)
    #     results[i].append(images[i])
    #     for lis in arr_transpose:
    #         most_freq_tag = statistics.mode(lis)
    #         percent = (lis.count(most_freq_tag)/len(lis)) * 100
    #         results[i].append(str(percent))
    #     # print(s)
    #     # results.append(s)
    #     i += 1

            
    # images_with_total_agreement = []
    
    # for i in setthing:
    #     filedictionary[i] = []
       
    # for row in values:
    #     filedictionary[row[1]].append(row[2])

    # for key, value in filedictionary.items():
    #     if len(set(value)) == 1:
    #         total_agreement+=1
    #         images_with_total_agreement.append(key)
    results = 0


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