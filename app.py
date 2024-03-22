# from calendar import week
# from inspect import classify_class_attrs
# from re import L
# from time import strftime, time

# gspread is the google spreadsheet api
import gspread
# This authenticates the credentials
from google.oauth2.service_account import Credentials
# To work with time
from datetime import datetime

# link to the google spreadsheet api
scopes = ["https://www.googleapis.com/auth/spreadsheets"]

# The Following process 'can' be done by gspread on its own. However, that only
# works as long as the credentials file is kept in a specific folder somewhere
# in the computer. This method makes the file easier to manage (in the same dir)

#~ load the credentials
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
#~ validate it
client = gspread.authorize(creds)

# Ways the timetable is different from the subject sheet
# ~~ The timetable contains information on when each block takes palce, whereas,
# ~~ the subject sheet maps the blocks to the subjects.

# connection to the timetable
timetable_sheet_id = "1qC2PACU-I9L-ew-RmVL_1bBTymFdt6875Uq7Sql0aQc"
timetable = client.open_by_key(timetable_sheet_id)

# connection to the sheet that maps blocks to subjects + other useful subjet info
subject_sheet_id = "1xbsXA9W_ccPxllc-jCuxZtF--DRrO5mFUMjyaUvHODA"
subjects_sheet = client.open_by_key(subject_sheet_id)

# For the subjects
subject_worksheets = [x.title for x in subjects_sheet.worksheets()]
# print(subject_worksheets)
subs_fy = subjects_sheet.get_worksheet(subject_worksheets.index("FY Classes"))
fy_subs_all_values = subs_fy.get_all_values()
subs_sy = subjects_sheet.get_worksheet(subject_worksheets.index("SY Classes"))
# sy_subs_all_values = subs_sy.get_all_values()

reference_date = datetime(2024, 2, 12, 00, 00, 00)
reference_week = 1
# SET THE CUSTOM TIME HERE, YYYY, MM, DD, HH, and so on...
lookup_date = datetime(2024, 2, 18, 23, 59, 59)
# lookup_date = datetime.now()

# Find out what week it is -> Relative to a specific
# reference week whose week is provided.
# There are two types of weeks. A or B. These are represented by 0 or a 1 here.
def get_week(lookup_date) -> int:
    current_date = lookup_date
    print(current_date, "current_date", reference_date, "reference_date")
    difference = current_date - reference_date
    print(difference)
    print(-(-(difference.days+1)//7))
    week_difference = -(-(difference.days+1)//7)
    print(week_difference)
    return 0 + week_difference%2
print(get_week(lookup_date))

# Find out which Block is going on
def get_block(week:int, time_now=False, lookup_date=None):
    """
    :param week: value could be 0 or 1 corresponding to 'A' or 'B'
    """
    days = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 4: "Friday", 5: "Saturday",\
        6: "Sunday"}
    day = days[lookup_date.weekday()]
    print(day)
    # day = days[0]
    
    # Get the current time and then find out which block is it
    if time_now:
        now = datetime.now()
        current_time = datetime.strptime(now.strftime("%H:%M:%S"), "%H:%M:%S")
    else:
        current_time = datetime.strptime(lookup_date.strftime("%H:%M:%S"), "%H:%M:%S")
    # Value below is for debugging purposes only.
    # current_time = datetime.strptime("11:30:10",'%H:%M:%S')
    # print(current_time)

    timetable_worksheets = [x.title for x in timetable.worksheets()]  # all sheets
    blocks_sheet = timetable.get_worksheet(week+1) # sheet
    block_timings = blocks_sheet.col_values(1)  # block/event timings
    
    # Iterate over all the blocks and find out which block is it~
    time_index = None
    for i, j in enumerate(block_timings):
        start_end = j.split()
        if len(start_end) < 1:
            continue
        if datetime.strptime(start_end[0],'%H:%M') <= current_time <= datetime.strptime(start_end[2],'%H:%M'):
            time_index = i
            # print(time_index)
            break
    if time_index is None:
        return None
    # print(time_index)
    
    day_index = blocks_sheet.row_values(1).index(day.upper())
    # print(day_index)

    block = blocks_sheet.cell(time_index+1, day_index+1).value
    # print("Current Activity/Block", block)
    return block

def isBlock(block):
    # print("Block in isBlock", block, block.split()[0])
    try:
        print("came inside try")
        if block.upper() in "ABCDEFG":
            return True, True
        elif block.split()[0] in "ABCDEG":
            return True, False
        else:
            return False, False
    except AttributeError as e:
        print(str(e))
        return False, False

def get_classes(block):
    # For first years:
    print(isBlock(block))
    block_clarif = isBlock(block)
    if not block_clarif[0]:
        if block is None:
            return "No Event Scheduled"
        return block
    elif not block_clarif[1]:
        block = block.split()[0]
    column_index = fy_subs_all_values[0].index(block)
    fy_classes = subs_fy.col_values(column_index+1)
    sy_classes = subs_sy.col_values(column_index+1)
    print(fy_classes)
    # Now, with the classes, get the subject for each class
    class_subject_dict = {}
    for i, j in enumerate(fy_classes):
        # print("enumerating...", i, j)
        if j:
            print(fy_subs_all_values[i][0])
            class_subject_dict[j] = fy_subs_all_values[i][0]
    for i, k in enumerate(sy_classes):
        # print("enumerating...", i, k)
        if k:
            print(fy_subs_all_values[i][0])
            class_subject_dict[k] = fy_subs_all_values[i][0]
    return class_subject_dict

print(get_week(lookup_date))
