import numpy as np
import serial
import time
import sys
from datetime import datetime

sensor = sys.argv[1]
directory = sys.argv[2]
debug = int(sys.argv[3])

if sensor == 'mic':
	ser = serial.Serial('/dev/cu.usbserial-D308FHDS', 115200)
else:
	ser = serial.Serial('/dev/cu.usbserial-DN06A9ZF', 115200)

line = None

#Ignore boot sequence
while(line != 'Begin:\r\n'):
	line = ser.readline().decode('ascii')

print('Preparing to start collection...')
for i in range(5):
	ser.reset_input_buffer()
	time.sleep(1)
ser.reset_input_buffer()
print("Starting collection")
filenum = 0

while(1):
	vals = []
	b = ser.read()
	if debug:
		print(b[0])
	if(b == b'\x00'):
		print('Event detected')
		t = datetime.now()
		while(1):
			b = ser.read()
			if debug:
				print(b[0])
			if b == b'\xAA':
				b = ser.read()
				if debug:
					print(b[0])
				vals.append(b[0])
			elif b == b'\xFF':
				vals = np.array(vals)
				np.save('{}/{}/event{}.npy'.format(sensor, directory, filenum), vals)
				f = open('{}/{}/log.txt'.format(sensor, directory), 'a')
				f.write('Event ' + str(filenum) + ': ' + str(t) + '\n')
				f.close()
				print('Event ' + str(filenum) + ' saved with ' + str(vals.shape[0]) + ' data points')
				filenum += 1
				break
			else:
				print('Error: unexpected byte')
				exit()
	else:
		print("Unexpected data - flushing buffer and trying again...")
		ser.reset_input_buffer()
		time.sleep(1)
		
