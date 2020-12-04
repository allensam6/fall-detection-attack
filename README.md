# fall-detection-attack

**dataset.h5**
hdf5 file containing mic and PIR sensor data corresponding to 200 fall and non-fall events.

***

**event_list.txt**
List of valid events used by extract.py

***

**extract.py**
Script which loads the data for events listed in event_list.txt, verifies that the mic and PIR data were collected simultaneously, and combines all events to produce dataset.h5

***

**collect.py**
Script used to receive event data from sensor nodes during experiment

***

**evaluate.py**
Script used to train and evaluate SVM 

***

**mic/**
Directory containing microphone data (NOTE: many of the events are invalid and are not included in the final dataset)

***

**pir/**
Directory containing PIR data (NOTE: many of the events are invalid and are not included in the final dataset)

***

**sensor_node/**
esp-idf project containing code for sensor_nodes

