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



def get_coords_mark(markinfo):

    mark_x = markinfo['x']
    mark_y = markinfo['y']

    the_x = np.array([markinfo['x_min'], markinfo['imsize_x_pix']])
    the_y = np.array([markinfo['y_min'], markinfo['imsize_y_pix']])
    the_lon = np.array([markinfo['lon_min'], markinfo['lon_max']])
    the_lat = np.array([markinfo['lat_min'], markinfo['lat_max']])

    # don't throw an error if the coords are out of bounds, but also don't extrapolate
    f_x_lon = interp1d(the_x, the_lon, bounds_error=False, fill_value=(None, None))
    f_y_lat = interp1d(the_y, the_lat, bounds_error=False, fill_value=(None, None))

    return f_x_lon(mark_x), f_y_lat(mark_y)

classifications_all = pd.read_csv(infile)

#Make subject dictionary with id as key and metadata
subjects_all = pd.read_csv(metafile)
subjects_dict = {}
for index, row in subjects_all.iterrows():
    subjects_dict[row['subject_id']] = eval(row['metadata'])



#print(classifications_all.columns)
#print(subjects_dict[13308116])
#print(meta["#scene_corner_UL_x"])

for row in classifications_all:
    subject_id = row['subject_id']

    compiled_data = subjects_dict[subject_id]
    
    compiled_data['x_min'] = np.ones_like(marks_subj.subject_id)
    compiled_data['y_min'] = np.ones_like(marks_subj.subject_id)

    for tool in [0, 1, 2, 3]:
        for df in [0, 1]:
            #data.frame{1,0}.T0_tool{0,1,2,3}_{x,y}
            basename = 'data.frame' + df + '.T0_tool' + tool + '_'

            compiled_data['x'] = eval(row[basename + 'x'])[0]
            compiled_data['y'] = eval(row[basename + 'y'])[0]

            if tool == 3:
                compiled_data['details'] = row[basename + 'details']

            if compiled_data['x'] != None & compiled_data['y'] != None:
                get_coords_mark(compiled_data)

