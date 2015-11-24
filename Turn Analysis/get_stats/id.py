FILE_DRIVER_ID = '../stats/driver_id'
FILE_CAR_ID = '../stats/car_id'

def _extract_ids():
    car_ids = dict()
    driver_ids = dict()
    with open('../stats/sessions.tsv', 'r') as f:
        for line in f:
            contents = line.split('\t')
            car_id = contents[0].rstrip()
            driver_id = contents[-1].rstrip()
            if not driver_id in driver_ids:
                if driver_id != '__EMPTY__':
                    index = len(driver_ids)
                    driver_ids[driver_id] = index
            if not car_id in car_ids:
                index = len(car_ids)
                car_ids[car_id] = index

    driver_ids = dict((y, x) for x, y in driver_ids.iteritems())
    car_ids = dict((y, x) for x, y in car_ids.iteritems())
    return car_ids, driver_ids
    #return sorted(driver_ids, key=driver_ids.get)

def _print_driver_ids(driver_ids):
    _print_dict(FILE_DRIVER_ID, driver_ids)

def _print_car_ids(car_ids):
    _print_dict(FILE_CAR_ID, car_ids)

def _print_dict(file, d):
    with open(file, 'w') as f:
        for key in sorted(d):
            f.write(str(key) + '\t' + str(d[key]) + '\n')

# extract sessions for each driver
# sessions are represented by a dict where key is driver key and 
# value is (car_key, #session)
def extract_driver_sessions():
    driver_keys = get_driver_keys()
    car_keys = get_car_keys()
    sessions = dict()
    with open('../stats/sessions.tsv', 'r') as f:
        for line in f:
            contents = line.split('\t')
            driver_id = contents[-1].rstrip()
            if driver_id != '__EMPTY__':
                driver_key = driver_keys[driver_id]
                car_key = car_keys[contents[0]]
                num_session = contents[-2]
                if driver_key in sessions:
                    sessions[driver_key].append([car_key, num_session])
                else:
                    sessions[driver_key] = [[car_key, num_session]]
    return sessions

# print driver sessions 
def _print_driver_sessions(sessions):
    driver_ids = get_driver_ids()
    with open('../stats/driver_sessions', 'w') as f:
        for driver_key in sorted(sessions):
            f.write(str(driver_key) + '\t')
            f.write(driver_ids[driver_key] + '\t')
            for session in sessions[driver_key]:
                f.write(session[0] + ' ' + session[1] + '\t')
            f.write('\n')

def _get_id(key, file):
    key = str(key)
    with open(file, 'r') as f:
        for line in f:
            k, value = line.split('\t')
            if key == k:
                return value.rstrip()

def _get_key(id, file):
    with open(file, 'r') as f:
        for line in f:
            key, value = line.split('\t')
            if value.rstrip() == id:
                return key

def _get_dict(file):
    d = dict()
    with open(file, 'r') as f:
        for line in f:
            key, value = line.split('\t')
            d[key] = value.rstrip()
    return d

def _get_dict_reverse(file):
    d = dict()
    with open(file, 'r') as f:
        for line in f:
            value, key = line.split('\t')
            d[key.strip()] = value
    return d

def _keys_to_ids(file, list):
    d = _get_dict(file)
    new_list = []
    for key in list:
        new_list.append(d[key])
    return new_list

def _ids_to_keys(file, list):
    d = _get_dict_reverse(file)
    new_list = []
    for id in list:
        new_list.append(d[id])
    return new_list

# get driver id 
def get_driver_id(key):
    return _get_id(key, FILE_DRIVER_ID)

# get car id 
def get_car_id(key):
    return _get_id(key, FILE_CAR_ID)

# get driver key
def get_driver_key(id):
    return _get_key(id, FILE_DRIVER_ID)

# get car id 
def get_car_key(id):
    return _get_key(id, FILE_CAR_ID)

# driver key -> id dict
def get_driver_ids():
    return _get_dict(FILE_DRIVER_ID)

# car key -> id dict
def get_car_ids():
    return _get_dict(FILE_CAR_ID)

# driver id -> key dict
def get_driver_keys():
    return _get_dict_reverse(FILE_DRIVER_ID)

# car id -> key dict
def get_car_keys():
    return _get_dict_reverse(FILE_CAR_ID)

# transfer a list of driver keys to driver ids
def driver_keys_to_ids(list):
    return _keys_to_ids(FILE_DRIVER_ID, list)

# transfer a list of car keys to car ids
def car_keys_to_ids(list):
    return _keys_to_ids(FILE_CAR_ID, list)

# transfer a list of driver ids to driver keys
def driver_ids_to_keys(list):
    return _ids_to_keys(FILE_DRIVER_ID, list)

# transfer a list of car ids to car keys
def car_ids_to_keys(list):
    return _ids_to_keys(FILE_CAR_ID, list)

if __name__ == '__main__': 
    #car_ids, driver_ids = _extract_ids()
    #_print_car_ids(car_ids)
    #_print_driver_ids(driver_ids)

    _print_driver_sessions(extract_driver_sessions())

