import sys, os
import numpy as np
import pandas as pd
import ujson
from scipy.interpolate import interp1d
import scipy.ndimage
from ast import literal_eval

try:
    pointfile = sys.argv[1]
except:
    pointfile = "point_extractor_by_frame_example.csv"

try:
    questionfile = sys.argv[2]
except:
    questionfile = "question_extractor_example.csv"

try:
    metafile = sys.argv[3]
except:
    metafile = "test_data/planetary-response-network-and-rescue-global-caribbean-storms-2017-subjects.csv"

try:
    suffix = sys.argv[4]
except:
    suffix = 'test'


# the order of tools is from the workflow information
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


## Classify point questions

classifications_points = pd.read_csv(pointfile)
column_names = classifications_points.columns.values.tolist()
# classification_id,user_name,user_id,workflow_id,task,created_at,subject_id,extractor,data.aggregation_version,
# data.frame{1/0}.T0_tool{3/2/1/0}_{x/y/details} (x18)
base_columns = ['classification_id', 'user_name', 'user_id', 'workflow_id', 'task', 'created_at',
                'subject_id', 'extractor','data.aggregation_version']


# Make subject dictionary with id as key and metadata
subjects_all = pd.read_csv(metafile)
subjects_dict = {}
for index, row in subjects_all.iterrows():
    subjects_dict[row['subject_id']] = eval(row['metadata'])
print('Files loaded successfully')

column_points_extras = ['tool', 'label', 'how_damaged', 'frame', 'x', 'y', 'lon_mark', 'lat_mark',
 'lon_min', 'lon_max', 'lat_min', 'lat_max', 'imsize_x_pix', 'imsize_y_pix']
column_points = column_names + column_points_extras
points_included_cols = base_columns + column_points_extras
points_temp = []

# Iterate through point classifications, finding longitude/lattitude equivalents
for i, row in classifications_points.iterrows():
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
                
                for j in range(len(lon)):
                    data_temp = []
                    if tool == 3: #Tool 3 is Structural damage which can also include further details
                        detail_list = eval(row[basename + 'details'])
                        for j in range(len(lon)):
                            detail = list(detail_list[j][0])[0]
                            if detail == 'None':
                                detail = 'Unspecified'
                            else:
                                detail = details[int(detail)]
                    else:
                        detail = ''
                    # Append order: 'tool', 'label', 'how_damaged', 'frame', 'x', 'y',
                    #               'lon_mark', 'lat_mark', 'lon_min', 'lon_max', 'lat_min',
                    #               'lat_max', 'imsize_x_pix', 'imsize_y_pix'
                    add_temp = [
                                tool, 
                                name, 
                                detail, 
                                df, 
                                markinfo['x'][j], 
                                markinfo['y'][j],
                                lon[j],
                                lat[j], 
                                markinfo['lon_min'], 
                                markinfo['lon_max'], 
                                markinfo['lat_min'], 
                                markinfo['lat_max'], 
                                markinfo['imsize_x_pix'], 
                                markinfo['imsize_y_pix']
                    ]
                    temp = temp + add_temp

                    temp = row.tolist()
                    temp = temp + data_temp
                    points_temp.append(temp)

    if i % 100 == 0:
        print('Done: ' + str(i))
    if i > 1000:
        break


points_outfile = pd.DataFrame(points_temp, columns=column_points)
filename = 'data_points_' + str(suffix) + '.csv'
points_outfile[points_included_cols].to_csv(filename, index=False)


## Classify questions, shortcuts and non-answers

classifications_questions = pd.read_csv(questionfile)
column_names = classifications_questions.columns.values.tolist()
# classification_id,user_name,user_id,workflow_id,task,created_at,subject_id,extractor,data.10-to-30,data.None,data.aggregation_version,data.more-than-30,data.none,data.ocean-only-no-land,data.unclassifiable-image,data.up-to-10
base_columns = ['classification_id', 'user_name', 'user_id', 'workflow_id', 'task',
                'created_at', 'subject_id', 'extractor','data.aggregation_version']

column_questions_extras = ['question', 'label']
column_questions = column_names + column_questions_extras
questions_included_cols = base_columns + column_questions_extras
questions_temp = []

column_shortcuts_extras = ['label']
column_shortcuts = column_names + column_shortcuts_extras
shortcuts_included_cols = base_columns + column_shortcuts_extras
shortcuts_temp = []

column_blanks = column_names
blanks_included_cols = base_columns
blanks_temp = []

# Iterate through question classifications, consolidating data
for i, row in classifications_questions.iterrows():
    # Number of structures visible
    if row['data.None'] == 1.00:
        temp = row.tolist()
        temp.append('t2_approximately_ho__s_your_estimate')
        temp.append('None')
        questions_temp.append(temp)
    elif row['data.up-to-10'] == 1.00:
        temp = row.tolist()
        temp.append('t2_approximately_ho__s_your_estimate')
        temp.append('<10')
        questions_temp.append(temp)
    elif row['data.10-to-30'] == 1.00:
        temp = row.tolist()
        temp.append('t2_approximately_ho__s_your_estimate')
        temp.append('10-30')
        questions_temp.append(temp)
    elif row['data.more-than-30'] == 1.00:
        temp = row.tolist()
        temp.append('t2_approximately_ho__s_your_estimate')
        temp.append('>30')
        questions_temp.append(temp)
    
    # Shortcuts (no answer to any questions)
    elif row['data.unclassifiable-image'] == 1.00:
        temp = row.tolist()
        temp.append('Unclassifiable Image')
        shortcuts_temp.append(temp)
    elif row['data.ocean-only-no-land'] == 1.00:
        temp = row.tolist()
        temp.append('Ocean Only (no land)')
        shortcuts_temp.append(temp)

    # No answer given
    elif row['data.none'] == 1.00:
        temp = row.tolist()
        blanks_temp.append

    if i % 100 == 0:
        print('Done: ' + str(i))
    if i > 1000:
        break
    

questions_outfile = pd.DataFrame(questions_temp, columns=column_questions)
filename = 'data_questions_' + str(suffix) + '.csv'
questions_outfile[questions_included_cols].to_csv(filename, index=False)

shortcuts_outfile = pd.DataFrame(shortcuts_temp, columns=column_shortcuts)
filename = 'data_shortcuts_' + str(suffix) + '.csv'
shortcuts_outfile[shortcuts_included_cols].to_csv(filename, index=False)

blanks_outfile = pd.DataFrame(blanks_temp, columns=column_blanks)
filename = 'data_blanks_' + str(suffix) + '.csv'
questions_outfile[blanks_included_cols].to_csv(filename, index=False)