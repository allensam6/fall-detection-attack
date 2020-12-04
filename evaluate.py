from sklearn import svm, metrics, model_selection
import sys
import time
import h5py
import numpy as np
import matplotlib.pyplot as plt

filename = sys.argv[1]
sensor = sys.argv[2]
grid_search = int(sys.argv[3])

with h5py.File(sys.argv[1], 'r') as datafile:
	datafile = h5py.File(sys.argv[1], 'r')
	keys = datafile.keys()
	event_points = 5824
	data = []
	target = []
	for key in keys:
		if sensor == 'both':
			mic_event = datafile[key]['mic'][:]
			mic_timestamp = datafile[key]['mic'].attrs['start_time']
			mic_offset = int(round(mic_timestamp*5824))
			pir_event = datafile[key]['pir'][:]
			pir_timestamp = datafile[key]['pir'].attrs['start_time']
			pir_offset = int(round(pir_timestamp*5824))
			mic_event_aligned = np.zeros(8736)
			pir_event_aligned = np.zeros(8736)
			mic_event_aligned[mic_offset:(mic_offset + len(mic_event))] = mic_event[:]
			pir_event_aligned[pir_offset:(pir_offset + len(pir_event))] = pir_event[:]
			mic_spec, freq, t, im = plt.specgram(mic_event_aligned, Fs=datafile[key]['mic'].attrs['mic_sample_rate'])
			pir_spec, freq, t, im = plt.specgram(pir_event_aligned, Fs=datafile[key]['pir'].attrs['pir_sample_rate'])
			event = np.concatenate((mic_spec.flatten(), pir_spec.flatten()))
		else:
			event = datafile[key][sensor][:]
			event.resize(event_points)
			spec, freq, t, im = plt.specgram(event, Fs=datafile[key][sensor].attrs[f'{sensor}_sample_rate'])
			event = spec.flatten()
		data.append(event)
		target.append(datafile[key].attrs['label'])
data = np.array(data)
target = np.array(target)
X_train, X_test, y_train, y_test = model_selection.train_test_split(data, target, test_size=.3)

begin = time.time()
print('Training...')
spectrogram = int(sys.argv[3])
if grid_search:
	param_grid = {'C': [.1, 1, 10, 100], 'gamma': [1, .1, .01, .0001]}
	grid = model_selection.GridSearchCV(svm.SVC(), param_grid, refit=True, cv=5, iid=False)
	grid.fit(X_train, y_train)
	print(grid.best_estimator_)
else:
	clf = svm.SVC(kernel='linear')
	clf.fit(X_train, y_train)
end = time.time()
print('Training completed in {}'.format(end - begin))

if grid_search:
	y_pred = grid.predict(X_test)
else:
	y_pred = clf.predict(X_test)

print(metrics.classification_report(y_test, y_pred))
