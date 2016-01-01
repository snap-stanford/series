# plot lat lng pairs on google map
import sys

def generate_html(output, latlngs):
    with open('template_latlngs.html', 'r') as template:
        lines = template.readlines()
    with open(output, 'w') as html:
        for line in lines[:34]:
            html.write(line)
        for i in range(len(latlngs[0])):
            html.write(' '*6 + 'new GLatLng(%s, %s),\n' %(latlngs[0][i], latlngs[1][i]))
        for line in lines[34:]:
            html.write(line)


if __name__ == '__main__':
    # input: filename, lat, lng, lat, lng, ...
    output = sys.argv[1]
    if len(sys.argv) < 4 or len(sys.argv) % 2 != 0:
        print 'wrong input'
        exit()
    latlngs = [[], []]
    for i in range(2, len(sys.argv)):
        latlngs[i%2].append(sys.argv[i])
    print output, latlngs
    generate_html(output, latlngs)


    


