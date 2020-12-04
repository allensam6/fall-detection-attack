import datetime
import sys
import numpy as np
import h5py

event_list = open(sys.argv[1], 'r')
mic_root = sys.argv[2]
pir_root = sys.argv[3]

datafile = h5py.File('dataset.h5', 'w')

new_event_num = 0

while(1):
	heading = event_list.readline()
	if heading == '':
		break
	heading = heading.split()

	mic_directory = '{}/{}'.format(mic_root, heading[4])
	pir_directory = '{}/{}'.format(pir_root, heading[5])

	while(1):
		pair = event_list.readline()
		if pair == '\n':
			break
		pair = pair.split()
		mic_event_num = int(pair[0])
		pir_event_num = int(pair[1])

		mic_logfile = open('{}/log.txt'.format(mic_directory), 'r')
		while(1):
			line = mic_logfile.readline()
			if(line == ''):
				break
			line = line.split(': ')
			if(line[0] == 'Event {}'.format(mic_event_num)):
				mic_timestamp = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f\n')
	
		#print('Mic:', mic_timestamp.time())
		mic_logfile.close()
	
		pir_logfile = open('{}/log.txt'.format(pir_directory), 'r')
		while(1):
		        line = pir_logfile.readline()
		        if(line == ''):
		                break
		        line = line.split(': ')
		        if(line[0] == 'Event {}'.format(pir_event_num)):
		                pir_timestamp = datetime.datetime.strptime(line[1], '%Y-%m-%d %H:%M:%S.%f\n')
	
		#print('Pir:', pir_timestamp.time())
		pir_logfile.close()
		
		group = datafile.create_group('event{}'.format(new_event_num))
		new_event_num += 1
		group.attrs['subject'] = int(heading[0])
		group.attrs['activity'] = heading[1]
		group.attrs['location'] = heading[2]
		group.attrs['label'] = int(heading[3])

		mic_data = np.load('{}/event{}.npy'.format(mic_directory, mic_event_num))
		mic_dataset = group.create_dataset('mic', data=mic_data)
		mic_dataset.attrs['mic_sample_rate'] = 5824

		pir_data = np.load('{}/event{}.npy'.format(pir_directory, pir_event_num))
		pir_dataset = group.create_dataset('pir', data=pir_data)
		pir_dataset.attrs['pir_sample_rate'] = 5824
			
		if mic_timestamp < pir_timestamp:
			diff = pir_timestamp - mic_timestamp
			mic_dataset.attrs['start_time'] = 0.0
			pir_dataset.attrs['start_time'] = diff.total_seconds()
		else:
			diff = mic_timestamp - pir_timestamp
			mic_dataset.attrs['start_time'] = diff.total_seconds()
			pir_dataset.attrs['start_time'] = 0.0
	
		#print("Diff:", diff.total_seconds())
		threshold = datetime.timedelta(seconds=.5)
		if(diff < threshold):
			#print("Pass!")
			pass
		else:
			print("Fail!")
			print(heading)
			print(mic_event_num, pir_event_num)
			print(mic_timestamp, pir_timestamp)	

event_list.close()
datafile.close()
	
