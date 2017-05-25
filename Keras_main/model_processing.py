# -*- coding: utf-8 -*-
import pandas as pd
import os
import re
import jieba
import numpy as np
import copy
import datetime
from pre_process import remove_mess, cut_the_word, word_seq
from keras.models import load_model
from keras.utils.np_utils import to_categorical

maxlen = 2500
len_of_count = 11000
short_text = 600

##########################   Pre-processing period    ############################
##################################################################################

# import the training data
fake = pd.read_excel("fake.xls", header=None)
truth = pd.read_excel("truth.xls", header=None)
not_sure = pd.read_excel("not_sure.xls", header=None)
# giving the label
fake['label'] = -1
truth['label'] = 1
not_sure['label'] = 0
# gather the data
all_text = fake.append(truth, ignore_index=True)
all_text = all_text.append(not_sure,ignore_index=True)
# get the pure word
all_text[0] = list(map(lambda s: remove_mess(s),all_text[0]))
#get the len
all_text['len'] = list(map(lambda s:len(s),all_text[0]))
#get the word sequence
all_text['seq'] = word_seq(all_text, maxlen)

##################################################################################

x_train = np.array(list(all_text['seq']))
y_train = np.array(list(all_text['label']))
y_train = to_categorical(y_train, num_classes=3)

saved_model = "0.935_2017-05-26.h5"
model = load_model(saved_model)
predict = model.predict_classes(x_train)

score = model.evaluate(x_train, y_train, verbose=0)
print('train score:', score[0])
print('train accuracy:', score[1])

with open("test.txt", 'w') as fp:
    for i in range(0,len(x_train)):
        fp.write(str(y_train[i]))
        fp.write(str(predict[i]))
        fp.write('\n')