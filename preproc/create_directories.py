import os
from datetime import datetime
from datetime import timedelta

start_time = datetime.strptime('2014-03-03 07:10:57.492788',"%Y-%m-%d %H:%M:%S.%f")
end_time = datetime.strptime('2014-05-19 11:28:55.227533', "%Y-%m-%d %H:%M:%S.%f")

current_time = start_time

location = '/lfs/local/0/abhisg/vw/hour_data_2/'
while current_time <= end_time:
    current_folder_name = datetime.strftime(current_time,"%Y%m%d_%H")
    print current_folder_name
    os.mkdir(location+current_folder_name)
    current_time += timedelta(hours=1)



