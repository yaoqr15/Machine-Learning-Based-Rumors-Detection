# -*- coding: utf-8 -*-
import pandas as pd
from pre_process import remove_mess, cut_the_word

# the function to get word sequence
# Read from "datasheet.csv",then assign each a number
def generator(x):
    store = list(map(lambda s: cut_the_word(s), x[0]))
    content = []
    for i in store:
        content += i
    tmp = pd.Series(content).value_counts()
    tmp.to_csv("data_sheet.csv", encoding='utf-8')
    print("New datasheet was generated!")

def get_datasheet(file_1,file_2,file_3):
    # import the training data
    fake = pd.read_excel(file_1, header=None)
    truth = pd.read_excel(file_2, header=None)
    not_sure = pd.read_excel(file_3, header=None)
    # gather the data
    all_text = fake.append(truth, ignore_index=True)
    all_text = all_text.append(not_sure, ignore_index=True)
    # get the pure word
    all_text[0] = list(map(lambda s: remove_mess(s), all_text[0]))
    generator(all_text)

get_datasheet("fake.xls", "truth.xls", "not_sure.xls")

get = pd.read_csv("data_sheet.csv", header=None)

print(get)