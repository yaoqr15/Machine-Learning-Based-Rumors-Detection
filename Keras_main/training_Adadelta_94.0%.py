# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import datetime
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Embedding
from keras.layers import Conv1D, GlobalMaxPooling1D
from keras.utils.np_utils import to_categorical
from keras.callbacks import EarlyStopping, CSVLogger
from pre_process import remove_mess, cut_the_word, word_seq

maxlen = 2300
len_of_count = 10500
short_text = 600

##########################   Pre-processing period    ############################
##################################################################################

# import the training data
print("Import from xls document...")

fake = pd.read_excel("fake.xls", header=None)
truth = pd.read_excel("truth.xls", header=None)
not_sure = pd.read_excel("not_sure.xls", header=None)

print('Done.')

# giving the label
print("Processing the data...")
fake['label'] = -1
truth['label'] = 1
not_sure['label'] = 0
# gather the data
all_text = fake.append(truth, ignore_index=True)
all_text = all_text.append(not_sure, ignore_index=True)
# get the pure word
all_text['passage'] = list(map(lambda s: remove_mess(s), all_text[0]))
# get the len
all_text['len'] = list(map(lambda s: len(s), all_text['passage']))
# get the word sequence
print("Get the word sequence...")
all_text['seq'] = word_seq(all_text, maxlen)

print("Done.")
##################################################################################


##############################   Training period   ###############################
##################################################################################

# shuffle the order
print("Shuffle the data...")
idx = list(range(len(all_text)))
np.random.shuffle(idx)
all_text = all_text.loc[idx]
# initialize the training data
print("Wrap the training data...")
x_train = np.array(list(all_text['seq']))
y_train = np.array(list(all_text['label']))
y_train = to_categorical(y_train, num_classes=3)
print("Done.")
# setup the parameter of the layers
embedding_vector_length = 32
batch_size = 32
nb_epoch = 35
nb_filter = 128
filter_length = 3

# ###############     define the model  ################ #

model = Sequential()
# Embedding layer
model.add(Embedding(len_of_count,
                    embedding_vector_length,
                    input_length=maxlen))
# Convolution-1D layer
model.add(Conv1D(activation="relu",
                 filters=256,
                 kernel_size=3,
                 padding="valid"))
# Pooling layer
model.add(GlobalMaxPooling1D())
# Dense layer ,Dropout layer & Activation layer
model.add(Dense(512))
model.add(Dropout(0.2))
model.add(Activation('relu'))
# Output layer
model.add(Dense(3))
model.add(Activation('softmax'))
# compile the model
model.compile(loss='categorical_crossentropy',
              optimizer='Adadelta',
              metrics=['accuracy'])
# Fit the model
print('Train...')
csv_logger = CSVLogger('training.log')
model.fit(x_train, y_train,
          batch_size=batch_size,
          epochs=nb_epoch,
          callbacks=[csv_logger])

score = model.evaluate(x_train, y_train, verbose=0)
print('train score:', score[0])
print('train accuracy:', score[1])

# Save the trained model
time = str(datetime.datetime.now())[:10]
model.save(str(score[1])[:6]+'_'+time+'.h5')
