# -*- coding: utf-8 -*-
import pandas as pd
from weibo_pre_process import remove_mess, cut_the_word

# the function to get word sequence
# Read from "datasheet.csv",then assign each a number
def generator(x):
    store = list(map(lambda s: cut_the_word(s), x[0]))
    content = []
    for i in store:
        content += i
    tmp = pd.Series(content).value_counts()
    tmp.to_csv("data_sheet_weibo.csv", encoding='utf-8')
    print("New datasheet was generated!")

def get_datasheet3(file_1,file_2,file_3):
    # import the training data
    objection = pd.read_excel(file_1, header=None)
    support = pd.read_excel(file_2, header=None)
    not_sure = pd.read_excel(file_3, header=None)
    # gather the data
    all_text = objection.append(support, ignore_index=True)
    all_text = all_text.append(not_sure, ignore_index=True)
    # get the pure word
    all_text[0] = list(map(lambda s: remove_mess(s), all_text[0]))

    generator(all_text)

def get_datasheet(file_1):
    # import the training data
    data = pd.read_csv(file_1, header=None)
    # get the pure word
    data[0] = list(map(lambda s: remove_mess(s), data[0]))

    generator(data)

#get_datasheet("1.xlsx", "-1.xlsx", "0.xlsx")
get_datasheet("txt.csv")
print("Done.")