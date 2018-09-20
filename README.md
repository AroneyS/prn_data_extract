# Instructions
Extract from raw exports (via Coleman's workflow extractor) to separate flat .csv files with point selections converted to longitude/latitude from subject metadata (via Brooke's conversion function)

1. Extract data as per https://aggregation-caesar.zooniverse.org/Scripts.html#extracting-data
2. Run `python3 cleanup_workflow_output.py point_extractor_by_frame_example.csv question_extractor_example.csv subjects_metadata_file.csv test`
- Where 'point_extractor_by_frame_example.csv' and 'question_extractor_example.csv' are outputs from 1
- And 'subjects_metadata_file.csv' is the metadata of the subjects (images), containing edge longitude and lattitude and image size
- And 'test' is the desired file suffix

# Output (with 'test' as suffix)
- 'data_points_test.csv': Marks data output
    1. 'tool' -- 0, 1, 2, 3, corresponding to 'label'
    2. 'label' -- 'blockages', 'floods', 'shelters', 'damage' indicating mark type
    3. 'how_damaged' -- 'Minor', 'Moderate', 'Catastrophic' indicating damage amount
    4. 'frame' -- Image on which the point was placed (0: before, 1: after)
    5. 'x' -- x-coordinate of mark in image
    6. 'y' -- y-coordinate of mark in image
    7. 'lon_mark' -- longitude of mark
    8. 'lat_mark' -- latitude of mark

- 'data_questions_test.csv': Structure question output
    1. 't2_approximately_ho__s_your_estimate' -- contains answer to number of structures (None, <10, 10-30, >30) as strings

- 'data_shortcuts_test.csv': Shortcuts output
    1. 'label' --  contains 'Unclassifiable Image' if image declared unclassifiable or 'Ocean Only (no land)' if image declared to contain no land

- 'data_blanks_test.csv': contains the metadata of skipped classfications

- All outputs end with the following subject infomation: 
    1. 'lon_min' -- longitude at edge of image
    2. 'lon_max' -- longitude at other edge of image
    3. 'lat_min' -- latitude at edge of image
    4. 'lat_max' -- latitude at other edge of image
    5. 'imsize_x_pix' -- width of image (pixel)
    6. 'imsize_y_pix' -- height of image (pixel)