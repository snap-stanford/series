# given a snapshots filename, plots the route on google map of the snapshots
# gradient colormaps represents time
# red -> blue -> green -> red -> ...
import sys, os

def generate_html(snapshots):
    latlngs = get_latlngs(snapshots)
    with open('template_routes.html', 'r') as template:
        lines = template.readlines()
    with open(snapshots[:-4] + '.html', 'w') as html:
        for line in lines[:34]:
            html.write(line)
        for i in range(len(latlngs[0])):
            html.write(' '*6 + 'new GLatLng(%s, %s),\n' %(latlngs[0][i], latlngs[1][i]))
        for line in lines[34:]:
            html.write(line)


def get_latlngs(snapshots):
    latlngs = [[], []]
    dir = '/dfs/scratch0/silei/vw_project/snapshots/'
    fil = os.path.join(dir, snapshots)
    with open(fil, 'r') as f:
        f.readline()
        c = f.readline().strip().split('\t')
        prev_lat = float(c[4])
        prev_lng = float(c[5])
        latlngs[0].append(prev_lat)
        latlngs[1].append(prev_lng)
        for line in f:
            c = line.strip().split('\t')
            lat = float(c[4])
            lng = float(c[5])
            if abs(prev_lat - lat) + abs(prev_lng - lng) > 0.005:
                latlngs[0].append(lat)
                latlngs[1].append(lng)
                prev_lat = lat
                prev_lng = lng
    return latlngs

if __name__ == '__main__':
    # input: snapshots file name
    snapshots = sys.argv[1]
    generate_html(snapshots)


    


