# -*- coding: utf-8 -*-
import pandas as pd
import re
import jieba
import numpy as np
import copy

# ######################   initial the parameter   ####################### #
short_text = 600
useless_word = ['，','：','‘','’','','。','—','——',
                '你','我','他','它','咱们','大家','自己',
                '这','那','这儿','那边','各','每','的','了',
                '谁','什么','哪','怎么','哪里','几','地']
##########################################################################

# the function to get the pure word   ; Using the Regular Expression
def remove_mess(str):
    p = re.compile('[a-zA-Z\"\'’\/\(\),:;~‘\（\）\|\-\*@#$%^&\[\]{}<>+`\s\n\r\\\\]')
    return re.sub(p,'',str)

# the function to cut the word      ;  Using the "jieba" module
def cut_the_word(str_in):
    length = len(str_in)
    if length <= short_text:
        tmp = list(jieba.cut(str_in, cut_all=False))
        word = [x for x in tmp if x not in useless_word]
        return word
    else:
        cut = int(0.2*length)
        tmp = str_in[:cut]+str_in[-cut:]
        word = list(jieba.cut(tmp, cut_all=False))
        word = [x for x in word if x not in useless_word]
        return word


# the function to get word sequence
# Read from "datasheet.csv",then assign each a number
def word_seq(x, maxlength):
    store = list(map(lambda s: cut_the_word(s), x[0]))
    tmp = pd.read_csv('datasheet.csv', header=None, index_col=0)
    select = tmp[tmp[1] > 1]
    count = copy.deepcopy(select[1])
    count[:] = range(1, 1 + len(count))

    def doc2num(a, maxlength):
        a = [i for i in a if i in count]
        a = list(count[a])
        a += max(maxlength-len(a), 0)*[0]
        return a

    x['seq'] = list(map(lambda s: doc2num(s, maxlength), store))
    return list(x['seq'])
