import sys
sys.stdout = open('latlngs', 'w')

def get_latlngs(filename):
    #format = '{lat: %f, lng: %f},'
    format = 'new GLatLng(%f, %f),'
    with open(filename, 'r') as f:
        f.readline()
        c = f.readline().strip().split('\t')
        prev_lat = float(c[4])
        prev_lng = float(c[5])
        print format %(prev_lat, prev_lng)
        for line in f:
            c = line.strip().split('\t')
            lat = float(c[4])
            lng = float(c[5])
            if abs(prev_lat - lat) + abs(prev_lng - lng) > 0.005:
                print format %(lat, lng)
                prev_lat = lat
                prev_lng = lng

if __name__ == '__main__':
    filename = sys.argv[1]
    get_latlngs(filename)
