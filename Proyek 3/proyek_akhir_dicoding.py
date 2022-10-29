# -*- coding: utf-8 -*-
"""Proyek_Akhir_Dicoding

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1gsLQLZMlCb4MUxEotRg-2xqAHFNNWfMh

# Library
"""

!pip install opendatasets
import os
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
import json
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.layers import Dense, Conv2D, MaxPooling2D, Flatten, Dropout
import matplotlib.pyplot as plt
import opendatasets as od

"""# Kaggle Dataset:
https://www.kaggle.com/datasets/shrutipandit707/flowerrecognitiondataset
"""

od.download(
    "https://www.kaggle.com/datasets/shrutipandit707/flowerrecognitiondataset")
!rm -r flowerrecognitiondataset/flowers/dandelion/
!rm -r flowerrecognitiondataset/flowers/tulip/

BASE_DIR = 'flowerrecognitiondataset/flowers'

print("Jumlah Daisy: "+str(len(os.listdir('flowerrecognitiondataset/flowers/daisy'))))
print("Jumlah Rose: "+str(len(os.listdir('flowerrecognitiondataset/flowers/rose'))))
print("Jumlah Sunflower: "+str(len(os.listdir('flowerrecognitiondataset/flowers/sunflower'))))

"""# Augmentasi Gambar"""

train_datagen = ImageDataGenerator(rescale=1./255,
                                   rotation_range=30,
                                   horizontal_flip=True,
                                   shear_range=0.2,
                                   fill_mode='nearest',
                                   validation_split=0.2)
valid_datagen = ImageDataGenerator(rescale=1./255,
                                   validation_split=0.2)

train_generator = train_datagen.flow_from_directory(
    BASE_DIR,
    target_size=(100,100),
    batch_size=12,
    class_mode='categorical',
    subset='training'
)

valid_generator = valid_datagen.flow_from_directory(
    BASE_DIR,
    target_size=(100,100),
    batch_size=12,
    class_mode='categorical',
    subset='validation'
)

"""# Asristektur CNN"""

model = Sequential()
model.add(Conv2D(32, (3,3), activation='relu', strides=(1,1), padding='same', input_shape=(100,100,3)))
model.add(MaxPooling2D(2,2))
model.add(Conv2D(64, (3,3), activation='relu'))
model.add(MaxPooling2D(2,2)),
model.add(Conv2D(128, (3,3), activation='relu'))
model.add(MaxPooling2D(2,2))
model.add(Conv2D(256, (3,3), activation='relu'))
model.add(MaxPooling2D(2,2))
model.add(Flatten())
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(3, activation='softmax'))
model.summary()

"""# CUSTOM CALLBACK"""

class stopTraining(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if (logs.get('Accuracy')>=0.87 and logs.get('val_Accuracy')>=0.87):
      print("Stop Training, Accuracy has already reach 85%")
      self.model.stop_training=True

customCallback = stopTraining()

"""# COMPILING AND FITTING MODEL"""

model.compile(loss='categorical_crossentropy',
              optimizer=tf.optimizers.Adam(learning_rate=0.0001),
              metrics=['Accuracy'])

records = model.fit(train_generator,
                    steps_per_epoch=100, 
                    epochs=100,
                    validation_data=valid_generator, 
                    validation_steps=10, 
                    verbose=2,
                    callbacks=[[customCallback]])

"""# PLOT ACCURACY and LOSS"""

f = plt.figure(figsize=(12,6))
plt.subplot(1, 2, 1)
plt.plot(records.history['Accuracy'])
plt.plot(records.history['val_Accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')

plt.subplot(1, 2, 2)
plt.plot(records.history['loss'])
plt.plot(records.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')

plt.show()

"""# Saving Model to TF_LITE FORMAT"""

save_path = 'mymodel/'
tf.saved_model.save(model, save_path)

converter = tf.lite.TFLiteConverter.from_saved_model(save_path)
tflite_model = converter.convert()
     
with tf.io.gfile.GFile('model_image_classification.tflite', 'wb') as f:
  f.write(tflite_model)