from datetime import datetime

# string to seconds
def str_to_sec(time):
    format = '%Y-%m-%d %H:%M:%S.%f'
    time = datetime.strptime(time, format)
    sec = float(time.strftime('%s.%f'))
    return sec

# second to string
def sec_to_str(time):
    time = datetime.fromtimestamp(time)
    format = '%Y-%m-%d %H:%M:%S.%f'
    string = time.strftime(format)
    return string

