# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from os.path import splitext
from weibo_pre_process import remove_mess, cut_the_word, word_seq
from keras.models import load_model
from keras.utils.np_utils import to_categorical

maxlen = 200
len_of_count = 4800
short_text = 150

##########################   Pre-processing period    ############################
##################################################################################

def deal_with_data3(file_1, file_2, file_3):
    # import the training data
    objection = pd.read_excel(file_2, header=None)
    support = pd.read_excel(file_1, header=None)
    not_sure = pd.read_excel(file_3, header=None)
    # giving the label
    objection['label'] = -1
    support['label'] = 1
    not_sure['label'] = 0
    # gather the data
    all_text = objection.append(support, ignore_index=True)
    all_text = all_text.append(not_sure, ignore_index=True)
    # get the pure word
    all_text[0] = list(map(lambda s: remove_mess(s), all_text[0]))
    # get the len
    all_text['len'] = list(map(lambda s: len(s), all_text[0]))
    # get the word sequence
    all_text['seq'] = word_seq(all_text, maxlen)
    return all_text

def deal_with_data(file_1):
    # import the training data
    extension_name = splitext(file_1)[1]
    if extension_name == '.csv':
        all_text = pd.read_csv(file_1, header=None)
    elif extension_name == '.xls' or extension_name == '.xlsx':
        all_text = pd.read_excel(file_1, header=None)
    else:
        print("File name error,please check it out!\n")
        return 1

    # get the pure word
    all_text['passage'] = list(map(lambda s: remove_mess(s), all_text[1]))
    # get the word sequence
    all_text['seq'] = word_seq(all_text, maxlen)
    return all_text


##################################################################################


all_text = deal_with_data("weibo.csv")
x_data = np.array(list(all_text['seq']))

saved_model = "0.827_2017-05-28.h5"
model = load_model(saved_model)
predict = model.predict_classes(x_data)
all_text['label'] = predict
select = all_text[[0, 1, 2]][all_text.label == 1]
select.to_csv('weibo.csv',encoding='utf-8', header=False, index=False)
print('Done')

'''
score = model.evaluate(x_test, y_test, verbose=0)
print('\nTesting set:\ntrain score:', score[0])
print('train accuracy:', score[1])

with open("test.txt2", 'w') as fp:
    for i in range(0, len(x_test)):
        fp.write(str(y_test[i]))
        fp.write(str(predict[i]))
        fp.write('\n')
'''