# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from os.path import splitext
from pre_process import remove_mess, cut_the_word, word_seq
from keras.models import load_model
from keras.utils.np_utils import to_categorical

maxlen = 2300
len_of_count = 10500
short_text = 600

##########################   Pre-processing period    ############################
##################################################################################

def deal_with_data3(file_1, file_2, file_3):
    # import the training data
    fake = pd.read_excel(file_2, header=None)
    truth = pd.read_excel(file_1, header=None)
    not_sure = pd.read_excel(file_3, header=None)
    # giving the label
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

    all_text['label'] = all_text[1]
    # get the pure word
    all_text['passage'] = list(map(lambda s: remove_mess(s), all_text[1]))
    # get the len
    all_text['len'] = list(map(lambda s: len(s), all_text['passage']))
    # get the word sequence
    all_text['seq'] = word_seq(all_text, maxlen)
    return all_text

def convert(num, w):
    if w == 'in':
        if num == 2:
            return -1
        else:
            return num
    else:
        if num == -1:
            return 2
        else:
            return num

# figure out the result
def rumor_or_not(all_text):
    guokr_w = 0.8
    sina_w = 0.2
    guokr = all_text[all_text[0] == '果壳']
    sina = all_text[all_text[0] == '新浪']
    guokr = guokr['predict'].value_counts().index[0]
    sina = sina['predict'].value_counts().index[0]
    sina = convert(sina, 'in')
    guokr = convert(guokr, 'in')
    return convert(round(guokr_w*guokr+sina_w*sina), 'out')

##################################################################################

print("Reading data from file...")
temp = pd.read_csv("temp.csv", header=None)
all_text = deal_with_data("txt.csv")
x_cal = np.array(list(all_text['seq']))

# load the model and predict the classes
print("Loading model...")
saved_model = "0.9983_2017-05-27.h5"
model = load_model(saved_model)
print("Predicting...")
predict = model.predict_classes(x_cal)
all_text['predict'] = list(predict)
print(all_text)
# 0 = not_sure   1 = truth  2 = rumor
# ->   0              1          -1
print("Judging...")
result = rumor_or_not(all_text)
passage = all_text[(all_text[0] == '果壳') & (all_text['predict'] == result)][1]
passage = passage[0]
if result == 2:
    temp['result'] = '谣言'
elif result == 1:
    temp['result'] = '事实'
else:
    temp['result'] = '不确定'
temp['passage'] = passage

temp.to_csv("temp.csv", encoding="utf-8", header=False, index=False)
print("Done!")

'''
x_train = np.array(list(all_text['seq']))
y_train = np.array(list(all_text['label']))
y_train = to_categorical(y_train, num_classes=3)

score = model.evaluate(x_train, y_train, verbose=0)
print('train score:', score[0])
print('train accuracy:', score[1])

with open("test.txt", 'w') as fp:
    for i in range(0, len(x_train)):
        fp.write(str(y_train[i]))
        fp.write(str(predict[i]))
        fp.write('\n')
'''