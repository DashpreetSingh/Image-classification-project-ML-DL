# -*- coding: utf-8 -*-
"""deep learning project image classification

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1s7gegOWwkvmcemwD---wE-M5-8kauZwu
"""

#import libraries 
import tensorflow as tf
from tensorflow.keras import models, layers
import matplotlib.pyplot as plt

#set the image pixel and batch 

IMAGE_SIZE = 256   #have 256 pixel
BATCH_SIZE = 32    #we set data  in batch of 32 images 
CHANNEL = 3        #In a color image, we normally have 3 channels: red, green and blue;
EPOCHS = 5         #epochs is one complete pass of the training of the dataset throught the alogrithm

#using the image_dataset_from_directory

dataset  = tf.keras.preprocessing.image_dataset_from_directory(  #image_dataset_from_directory allow to load your data in tensorflow
    directory = "/content/drive/MyDrive/PlantVillage",
    shuffle = True,
    image_size = (IMAGE_SIZE,IMAGE_SIZE),
    batch_size = BATCH_SIZE
)

class_names = dataset.class_names
class_names

len(dataset) #every element in  the dataset have a batch of 32 images so 68*32 = 2176 but in last folder its not acurate so the total image are 2152

plt.figure(figsize= (10, 10))
for image_batch, label_batch in dataset.take(1):
  for i in range(12):
    ax = plt.subplot(3,4,i+1)
    plt.imshow(image_batch[i].numpy().astype("uint8")) #imshow() creates an image from a 2-dimensional numpy array & numpy uint8 will wrap the pixels
    plt.title(class_names[label_batch[i]]) #to find the leaf batch we use this & label batch in numpy so 1st folder is 0 2nd is 1 and 3rd is 2 so to indicate the folder we use label_batch function 
    plt.axis("off")

len(dataset)

#80% ==> training
#20% ==> 10% validation , 10% test

#for training the data
train_size = 0.8           #is a sklearn function use to split the dataset
len(dataset)*train_size

train_ds = dataset.take(54) #in this we are using 1st 54 batches [:54]
len(train_ds)

test_ds = dataset.skip(54)    #in this we are using after 54 batches like [54:]
len(test_ds)

#invalidation and test 
val_size = 0.1
len(dataset) * val_size

val_ds = test_ds.take(6)
len(val_ds)

test_ds = test_ds.skip(6)
len(test_ds)

def get_dataset_partitions_tf(ds,train_split = 0.8 , val_split = 0.1 , test_split = 0.1 , shuffle= True, shuffle_size = 10000):
   ds_size = len(ds)
   if shuffle:
     ds= ds.shuffle(shuffle_size, seed=12)

   train_size = int(train_split * ds_size)
   val_size = int(val_split *ds_size)

   train_ds = ds.take(train_size)
   val_ds = ds.skip(train_size).take(val_size)
   test_ds = ds.skip(train_size).skip(val_size)
   
   return train_ds , val_ds , test_ds

train_ds , val_ds , test_ds =  get_dataset_partitions_tf(dataset)

len(train_ds)

len(val_ds)

len(test_ds)

train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size = tf.data.AUTOTUNE)    #CACHE read the image and keep that image in memory #prefetch will load the next batch of the batch form the disk and improve the performance
val_ds = val_ds.cache().shuffle(1000).prefetch(buffer_size = tf.data.AUTOTUNE)    
test_ds = test_ds.cache().shuffle(1000).prefetch(buffer_size = tf.data.AUTOTUNE)

#preprocessing

resize_and_rescale = tf.keras.Sequential([
    layers.experimental.preprocessing.Resizing(IMAGE_SIZE, IMAGE_SIZE),
    layers.experimental.preprocessing.Rescaling(1.0/255) #its scaling the px 1 to 255
])

data_augmentation = tf.keras.Sequential([
    layers.experimental.preprocessing.RandomFlip("horizontal_and_vertical"),
    layers.experimental.preprocessing.RandomRotation(0.2),
])

#BUILDING MODEL 
input_shape = (BATCH_SIZE, IMAGE_SIZE,IMAGE_SIZE, CHANNEL)
n_classes = 3 

model = models.Sequential([
    resize_and_rescale,
    data_augmentation,
    layers.Conv2D(32,(3,3), activation= 'relu', input_shape = input_shape),
    layers.MaxPooling2D((2,2,)),
    layers.Conv2D(64, kernel_size= (3,3),activation = 'relu'),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64, kernel_size = (3,3) , activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64,(3,3),activation = 'relu'),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64,(3,3),activation = 'relu'),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(64,(3,3),activation = 'relu'),
    layers.MaxPooling2D((2,2)),
    layers.Flatten(),
    layers.Dense(64 , activation = 'relu'),
    layers.Dense(n_classes, activation='softmax'),
])
model.build(input_shape=input_shape )

model.summary()

#model optimization

model.compile(
    optimizer='adam',  # adam is optimizer  
    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),  #SparseCategoricalCrossentropy. All other loss functions need outputs and labels of the same shape, this specific loss function doesn't need.
    metrics=['accuracy']
)

history = model.fit(
    train_ds,
    epochs = EPOCHS,
    batch_size = BATCH_SIZE,
    verbose = 1,
    validation_data = val_ds
)

scores = model.evaluate(test_ds)

scores

history

history.params

history.history.keys()

history.history['accuracy']

acc=history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history ['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(8,8))
plt.subplot(1,2,1)
plt.plot(range(EPOCHS), acc , label ='Training Accuracy')
plt.plot(range(EPOCHS), val_acc , label = 'Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.figure(figsize=(8,8))
plt.subplot(1,2,1)
plt.plot(range(EPOCHS), loss , label ='Training loss')
plt.plot(range(EPOCHS), val_loss , label = 'Validation loss')
plt.legend(loc='lower right')
plt.title('Training and Validation loss') #loss is basically an ERROR

#we create th emodel and have to check the model is predicting correct ort not 

import numpy as np 
for image_batch , labels_batch in test_ds.take(1):

  first_image = image_batch[0].numpy().astype('uint8')
  first_label =labels_batch[0].numpy()

  print("first image to predict")
  plt.imshow(first_image)
  print("actual label :",class_names[first_label])

  batch_prediction = model.predict(image_batch)
  print("prediction label :",class_names[np.argmax(batch_prediction[0])])  #The numpy. argmax() function returns indices of the max element of the array in a particular axis

def predict(model,img):
  img_array = tf.keras.preprocessing.image.img_to_array(images[i].numpy()) #we created a image array 
  img_array = tf.expand_dims(img_array,0) #create new batch 

  predictions = model.predict(img_array)

  predicted_class = class_names[np.argmax(predictions[0])]
  confidence = round(100 * (np.max(predictions[0])), 2)
  return predicted_class, confidence

plt.figure(figsize=(15,15))
for images, labels in test_ds.take(1):
  for i in range (9):
    ax = plt.subplot(3,3,i+1)
    plt.imshow(images[i].numpy().astype("uint8"))

    predicted_class, confidence = predict(model, images[i].numpy())
    actual_class = class_names[labels[i]]

    plt.title(f"Actual :{actual_class},\n Predicted : {predicted_class}.\n Confidence : {confidence}%")

    plt.axis("off")

