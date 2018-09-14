import sys, os
import numpy as np
import pandas as pd
import ujson
from scipy.interpolate import interp1d
import scipy.ndimage
from ast import literal_eval

try:
    infile = sys.argv[1]
except:
    infile = "point_extractor_by_frame_example.csv"

try:
    metafile = sys.argv[2]
except:
    metafile = "test_data/planetary-response-network-and-rescue-global-caribbean-storms-2017-subjects.csv"

# the order of tools is from the workflow information - as is the fact the
# marks are in task T2
tools = ['Road Blockage', 'Flood', 'Temporary Settlement', 'Structural Damage']

shortcuts = ['Unclassifiable Image', 'Ocean Only (no land)']

# for the structural damage subtask, if it exists
details = ['Minor', 'Moderate', 'Catastrophic']



def get_coords_mark(markinfo):

    mark_x = [float(i) for i in markinfo['x']]
    mark_y = [float(i) for i in markinfo['y']]

    the_x = np.array([markinfo['x_min'], markinfo['imsize_x_pix']], dtype=float)
    the_y = np.array([markinfo['y_min'], markinfo['imsize_y_pix']], dtype=float)
    the_lon = np.array([markinfo['lon_min'], markinfo['lon_max']], dtype=float)
    the_lat = np.array([markinfo['lat_min'], markinfo['lat_max']], dtype=float)

    # don't throw an error if the coords are out of bounds, but also don't extrapolate
    f_x_lon = interp1d(the_x, the_lon, bounds_error=False, fill_value=(None, None))
    f_y_lat = interp1d(the_y, the_lat, bounds_error=False, fill_value=(None, None))

    return f_x_lon(mark_x), f_y_lat(mark_y)


classifications_all = pd.read_csv(infile)
#print(classifications_all.head(2))
#print(classifications_all.columns)

# Make subject dictionary with id as key and metadata
subjects_all = pd.read_csv(metafile)
subjects_dict = {}
for index, row in subjects_all.iterrows():
    subjects_dict[row['subject_id']] = eval(row['metadata'])
print('Files loaded successfully')

#column_names = classifications_all.columns.values.tolist() + ''
outfile = classifications_all
# Iterate through classifications, adding lattitude equivalents
for i, row in classifications_all.iterrows():
    subject_id = row['subject_id']
    markinfo = subjects_dict[subject_id]
    markinfo['x_min'] = 1 #np.ones_like(markinfo['x'])
    markinfo['y_min'] = 1 #np.ones_like(markinfo['y'])

    for (tool, name) in [(0, 'blockages'), (1, 'floods'), (2, 'shelters'), (3, 'damage')]:
        for df in [0, 1]:
            #data.frame{1,0}.T0_tool{0,1,2,3}_{x,y}
            basename = 'data.frame' + str(df) + '.T0_tool' + str(tool) + '_'

            try:
                markinfo['x'] = eval(row[basename + 'x'])
                markinfo['y'] = eval(row[basename + 'y'])
            except:
                markinfo['x'] = None
                markinfo['y'] = None

            if markinfo['x'] != None and markinfo['y'] != None:
                (lon, lat) = get_coords_mark(markinfo)
                coords = []
                if tool == 3: #Tool 3 is Structural damage which can also include further details
                    detail_list = eval(row[basename + 'details'])
                    for j in range(len(lon)):
                        detail = list(detail_list[j][0])[0]
                        if detail != 'None':
                            detail = int(detail)
                            coords.append(( lon[j], lat[j], details[detail] ))
                else:
                    for j in range(len(lon)):
                        coords.append(( lon[j], lat[j] ))

                outfile.at[i, name] = str(coords)

    print('Done: ' + str(i) + '/282,783')
    if i > 100:
        break

outfile.to_csv('output_test.csv')


