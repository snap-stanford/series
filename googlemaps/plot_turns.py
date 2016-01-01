# given the driver key (0~63), generate the google map which plots all the turns
# of the driver
# turns with signal: yellow -> red
# turns without signal: green -> blue
import sys, os
import pandas as pd

def generate_html(dkey):
    latlngs, colors = get_latlngs(dkey)
    with open('template_turns.html', 'r') as template:
        lines = template.readlines()
    with open(str(dkey) + '.html', 'w') as html:
        for line in lines[:34]:
            html.write(line)
        for i in range(len(latlngs[0])):
            html.write(' '*6 + 'new GLatLng(%s, %s),\n' %(latlngs[0][i], latlngs[1][i]))
        
        for line in lines[35:37]:
            html.write(line)
        html.write(colors)
        for line in lines[38:]:
            html.write(line)


def get_latlngs(dkey):
    latlngs = [[], []]
    colors = ''
    dir = '/dfs/scratch0/silei/vw_project/turns/'
    for filename in os.listdir(dir):
        if filename.startswith(str(dkey)):
            latlngs[0].append(filename.split('_')[2])
            latlngs[1].append(filename.split('_')[3])
            signal = False
            fil = os.path.join(dir, filename)
            df = pd.read_csv(fil, header = None, delim_whitespace = True)
            df.columns = ['Day', 'Time', 'Steer_Angle', 'Velocity', 'Heading', \
                'Latitude', 'Longitude', 'Brightness', 'Road_Type', \
                'Num_Oncoming_Lanes', 'Curr_Seg_ID', 'Seg_Dist_Left', \
                'Next_Seg_ID', 'Steer_Velocity', 'Brake', 'Pedal', 'Fuel', \
                'X_Accel', 'Y_Accel', 'Mileage', 'RPM', 'Wiper_Speed', \
                'Time2Coll', 'Deacc_Request', 'L_Sig', 'R_Sig']
            for i in range(len(df)):
                if df['L_Sig'][i] == 't' or df['R_Sig'][i] == 't':
                    signal = True
            if signal == True:
                colors = colors + '"FFFF00", "FF0000", '
            else:
                colors = colors + '"00FF00", "0000FF", '
    return latlngs, colors

if __name__ == '__main__':
    # input: driver_key
    dkey = sys.argv[1]
    generate_html(dkey)


    


