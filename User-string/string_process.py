# -*- coding: utf-8 -*-
'''
0用户输入字符串    1关键词    2是否谣言    3证明的文章   4出处网址    5微博发布者   6发布时间  7微博内容   
'''
import sys
import jieba.analyse
import pandas as pd

# the function to extract the keyword and build the temp.csv
def process(sentence):
    print("Build temp.csv ")
    temp = []
    temp.append(sentence)
    keyword = list(jieba.analyse.extract_tags(sentence, 5))
    tmp = '，'
    keyword = tmp.join(keyword)
    temp.append(keyword)
    output = pd.DataFrame(temp).T
    output.to_csv("temp.csv", encoding="utf-8", header=False, index=False)
    print("Done\n")
# get the str from outside ,and begin the process
sys.argv.append("Null")
sentence = sys.argv[1]
process(sentence)





