# Instructions
Extract from raw exports (via Coleman's workflow extractor) to separate flat .csv files with point selections converted to longitude/latitude from subject metadata (via Brooke's conversion function)

1. Extract data as per https://aggregation-caesar.zooniverse.org/Scripts.html#extracting-data
2. Run python3 point_to_lonlat.py point_extractor_by_frame_example.csv question_extractor_example.csv subjects_metadata_file.csv test
Where 'point_extractor_by_frame_example.csv' and 'question_extractor_example.csv' are outputs from 1
And 'subjects_metadata_file.csv' is the metadata of the subjects (images), containing corner longitude and lattitude
And 'test' is the desired file suffix

# Output
'data_points_test.csv': 'blockages', 'floods', 'shelters' contain lon/lat for each point. 'damage' contains lon/lat/details for each point. Both as python list of tuples. 

'data_questions_test.csv': 'structures' contains answer to number of structures (None, <10, 10-30, >30) as strings

'data_shortcuts_test.csv': 'unclassifiable' contains 1 if image declared unclassifiable. 'only ocean' contains 1 if image declared to contain no land

'data_blanks_test.csv': contains metadata of skipped classfications