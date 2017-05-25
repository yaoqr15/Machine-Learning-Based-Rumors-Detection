# -*- coding: utf-8 -*-
import pandas as pd
import re
import jieba
import jieba.analyse
import numpy as np
import copy
from keras.models import Sequential
from keras.layers import Dense,Dropout,Embedding,Flatten
from keras.layers import Conv1D,MaxPooling1D,Merge
from keras.utils.np_utils import to_categorical

global len_of_count
#len_of_count = 0
short_text = 600
useless_word = ['，','：','‘','’','','。','—','——',
                '你','我','他','它','咱们','大家','自己',
                '这','那','这儿','那边','各','每','的','了',
                '谁','什么','哪','怎么','哪里','几','地']

#the function to get the pure word
def remove_mess(str):
    p = re.compile('[a-zA-Z\"\'’\/\(\),:;~‘\（\）\|\-\*@#$%^&\[\]{}<>+`\s\n\r\\\\]')
    return re.sub(p,'',str)

#the function to cut the word
def cut_the_word(str_in):
    length = len(str_in)
    if length <= short_text:
        tmp = list(jieba.cut(str_in,cut_all=False))
        word = [x for x in tmp if x not in useless_word]
        return word
    else:
        cut = int(0.2*length)
        tmp = str_in[:cut]+str_in[-cut:]
        word = list(jieba.cut(tmp,cut_all=False))
        word = [x for x in word if x not in useless_word]
        return word


#the function to get word sequence
#gather the word and count,then assign each a number
def word_seq(x, maxlength):
    global len_of_count
    content = []
    store = list(map(lambda s: cut_the_word(s), x[0]))
    for i in store:
        content += i
    count = pd.Series(content).value_counts()
    tmp = pd.DataFrame(count)
    select = tmp[tmp[0] > 1]
    count = copy.deepcopy(select[0])
    count[:] = range(1, 1 + len(count))
    count[''] = 0
    len_of_count = len(count)

    def doc2num(a, maxlength):
        a = [i for i in a if i in count]
        a += max(maxlength-len(a),0)*['']
        return list(count[a])

    x['seq'] = list(map(lambda s: doc2num(s, maxlength), store))
    return list(x['seq'])

##########################   Pre-processing period    ############################
##################################################################################

#import the training data
fake = pd.read_excel("fake.xls", header=None)
truth = pd.read_excel("truth.xls", header=None)
not_sure = pd.read_excel("not_sure.xls", header=None)
#giving the label
fake['label'] = -1
truth['label'] = 1
not_sure['label'] = 0
#gather the data
all_text = fake.append(truth, ignore_index=True)
all_text = all_text.append(not_sure,ignore_index=True)
#get the pure word
all_text[0] = list(map(lambda s: remove_mess(s),all_text[0]))
#get the maxlen
all_text['len'] = list(map(lambda s:len(s),all_text[0]))
long_text = int(max(list(all_text['len']))*0.4*0.5)
maxlen = max(long_text,int(short_text*0.5))
#get the word sequence
all_text['seq'] = word_seq(all_text, maxlen)

##################################################################################


##############################   Training period   ###############################
##################################################################################

#shuffle the order
idx = list(range(len(all_text)))
np.random.shuffle(idx)
all_text = all_text.loc[idx]
print(all_text)
#initialize the training data
x_train = np.array(list(all_text['seq']))
y_train = np.array(list(all_text['label']))
y_train = to_categorical(y_train, num_classes=3)
print(y_train)
#print(len_of_count,maxlen)
#setup the parameter of the layers
embedding_vector_length = 50
batch_size = 32
nb_epoch = 10

################     define the model  ###############

#define the embedding_layer
embedding_layer = Embedding(len_of_count,
                            embedding_vector_length,
                            input_length=maxlen)
#Left model
model_left = Sequential()
#Embedding layer
model_left.add(embedding_layer)
#Convolution-1D layer & Pooling layer    1/3
model_left.add(Conv1D(128, 5, activation='relu'))
model_left.add(MaxPooling1D(5))
#Convolution-1D layer & Pooling layer    2/3
model_left.add(Conv1D(128, 5, activation='relu'))
model_left.add(MaxPooling1D(5))
#Convolution-1D layer & Pooling layer    3/3
model_left.add(Conv1D(128, 5, activation='relu'))
model_left.add(MaxPooling1D(35))
#Flatten layer
model_left.add(Flatten())

#Right model
model_right = Sequential()
#Embedding layer
model_right.add(embedding_layer)
#Convolution-1D layer & Pooling layer    1/3
model_right.add(Conv1D(128, 4, activation='relu'))
model_right.add(MaxPooling1D(4))
#Convolution-1D layer & Pooling layer    2/3
model_right.add(Conv1D(128, 4, activation='relu'))
model_right.add(MaxPooling1D(4))
#Convolution-1D layer & Pooling layer    3/3
model_right.add(Conv1D(128, 4, activation='relu'))
model_right.add(MaxPooling1D(28))
#Flatten layer
model_right.add(Flatten())

#Third model
model_3 = Sequential()
#Embedding lyaer
model_3.add(embedding_layer)
#Convolution-1D layer & Pooling layer    1/3
model_3.add(Conv1D(128, 6, activation='relu'))
model_3.add(MaxPooling1D(3))
#Convolution-1D layer & Pooling layer    2/3
model_3.add(Conv1D(128, 6, activation='relu'))
model_3.add(MaxPooling1D(3))
#Convolution-1D layer & Pooling layer    3/3
model_3.add(Conv1D(128, 6, activation='relu'))
model_3.add(MaxPooling1D(30))
#Flatten layer
model_3.add(Flatten())

#Combine 3 model together
merged = Merge([model_left, model_right, model_3],
               mode='concat')

#The final model
model = Sequential()
#add merge
model.add(merged)
#Dense layer ,Dropout layer & Activation layer
model.add(Dense(128,activation='relu'))
model.add(Dropout(0.2))
#Output layer
model.add(Dense(3, activation='softmax'))
#compile the model
model.compile(loss='categorical_crossentropy',
              optimizer='sgd',
              metrics=['accuracy'])
#Fit the model
print('Train...')
model.fit(x_train, y_train,
          epochs=nb_epoch)

score = model.evaluate(x_train, y_train, verbose=0)
print('train score:', score[0])
print('train accuracy:', score[1])

