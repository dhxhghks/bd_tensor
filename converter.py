import tensorflow as tf
import h5py
from dlgo import kerasutil

f = h5py.File("betago.hdf5", "r")
model = kerasutil.load_model_from_hdf5_group(f['model'])
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

with open("betago.tflite", "wb") as f:
    f.write(tflite_model)
