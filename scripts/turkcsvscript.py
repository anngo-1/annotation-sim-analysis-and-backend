# ==========Libraries==========
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

# ==========Authentication==========
user_credentials = service_account.Credentials.from_service_account_file('credentials.json')
spreadsheet_service = build('sheets', 'v4', credentials=user_credentials)

# ==========Pathing==========
target_folder = r'C:\Users\{Username}\Downloads\FairfaceCSV\TrainData'.format(Username=os.getlogin())
reference_folder = r'C:\Users\{Username}\Downloads\FairfaceCSV\reference'.format(Username=os.getlogin())
sheet_id = '1HOn9Nekv9IQuIG-T0WqzCMQLPNIQeH0Db9zqcmCsL-g' # Google Sheet ID To Write To

# ==========Data==========
range_name = 'A2:XFD1048576'

reference_prefix = 'https://tag-based-avatar-images.s3.us-west-1.amazonaws.com/cleanFairFace/'
image_prefix = 'https://tag-based-avatar-images.s3.us-west-1.amazonaws.com/train/'

reference_data = {
# All of these files are found in the reference folder

#'bridge_region_url' : 'nose_bridge_proj_reference.png', ###
'flat_bridge_projection_url' : 'projection1.jpg.png',
'medium_bridge_projection_url' : 'projection2.jpg.png',
'tall_bridge_projection_url' : 'projection3.jpg.png',

#'tip_region_url' : 'tip_projection_ref.png', ###
'flat_tip_projection_url' : 'flattip.png',
'medium_tip_projection_url' : 'mediumtip.png',
'tall_tip_projection_url' : 'talltip.png',

#'bridge_style_url' : 'bridge_style.png', ###
'bridge_style_upturned_url' : 'BRIDGE_STYLE_UPTURNED_REF.png',
'bridge_style_straight_url' : 'BRIDGE_STYLE_STRAIGHT_REF.png',
'bridge_style_downturned_url' : 'BRIDGE_STYLE_DOWNTURN_REF.png',

#'tip_style_url' : 'tip_style_reference.png',
'tip_style_upturned_url' : '17603.jpg', ###
'tip_style_straight_url' : '10214.jpg',
'tip_style_downturned_url' : '5036.jpg',

#'width_region_url' : 'real_width_reference.png', ###
'width_narrow_url' : 'NARROW_WIDTH.jpg',
'width_medium_url' : 'MEDIUM_WIDTH.jpg',
'width_wide_url' : 'WIDTH_WIDTH.jpg',

'nasal_hump_url' : 'nasalhumpyes.jpg', ###
'no_nasal_hump_url' : '10214.jpg',


}

sheet_data = [] # Used to hold all the data

# Go through each value
max = 5
counter = 0
for file_name in os.listdir(target_folder):
    
    # if counter == max:
    #     break
    
    # Create a column to hold the values
    sheet_row = []
    
    # Add the file as the first item to the column
    sheet_row.append(image_prefix + file_name)
    
    # Go through the reference sheet to add in all the references (dictionaries should be ordered above versions 3.1)
    for ref_image in reference_data.values():
        sheet_row.append(reference_prefix + ref_image)
    
    # Add the row into the column
    sheet_data.append(sheet_row)
    
    # counter += 1

# Submit the data to the spreadsheet
request_body = {
    'values' : sheet_data
}

submitted_response = spreadsheet_service.spreadsheets().values().append(
    spreadsheetId=sheet_id,
    range=range_name,
    valueInputOption='USER_ENTERED',
    body=request_body
).execute()

# Print to indicate
print('Sent to spreadsheet...')
