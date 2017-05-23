# -*- coding: utf-8 -*-
import pandas as pd
import re
import jieba
import jieba.analyse
import numpy as np
from keras.models import Sequential
from keras.layers import Dense,Dropout,Activation,Embedding
from keras.layers import Conv1D,GlobalMaxPooling1D
from keras.utils import np_utils
from keras.preprocessing import sequence

#the function to get the pure word
def remove_mess(str):
    p = re.compile('[a-zA-Z\"\'’\/\(\),:;\（\）\|\-\*@#$%^&\[\]{}<>+`\s\n\r]')
    return re.sub(p,'',str)

##########################   Pre-processing period    ############################

#import the training data
fake = pd.read_excel("fake.xls", header=None)
truth = pd.read_excel("truth.xls", header=None)
not_sure = pd.read_excel("not_sure.xls", header=None)
#giving the label
fake['label'] = -1
truth['label'] = 1
not_sure['label'] = 0
#gather the data
all = fake.append(truth, ignore_index=True)
all = all.append(not_sure,ignore_index=True)
#get the pure word
all[0] = list(map(lambda s: remove_mess(s),all[0]))
#get the maxlen
all['len'] = list(map(lambda s:len(s),all[0]))
maxlen = max(list(all[0]))*0.4


content = [x for i in all['word'] for x in i]
abc = pd.Series(content).value_counts()
abc[:] = range(1,1+len(abc))
abc[''] = 0


def doc2num(s,maxlen):
    s=jieba.cut(s,cut_all=False)
    s=[i for i in s if i in abc]
    s+=max((maxlen-len(s)), 0)*['']
    return list(abc[s])

all['doc2num'] = list(map(lambda s :doc2num(s,maxlen),all[0]))
tmp['doc2num'] = list(map(lambda s:doc2num(s,maxlen),tmp[0]))
idx = list(range(len(all)))
np.random.shuffle(idx)
all = all.loc[idx]
x_train = np.array(list(all['doc2num']))
y_train = np.array(list(all['label']))
y_train = y_train.reshape((-1,1))
x_test = np.array(list(tmp['doc2num']))

#a="流言揭秘：牙齿的颜色，越白越健康？20170210093100摘要你被骗了！在镜头里的那些唇红齿白、巧笑嫣然的美白效果其实都是后期通过电脑修图软件处理生成，并非牙膏的实际使用效果！要知道牙齿并不是越白越健康！根据科学研究表明，最坚固的牙齿是自然健康略带黄色的摘要你被骗了！在镜头里的那些唇红齿白、巧笑嫣然的美白效果其实都是后期通过电脑修图软件处理生成，并非牙膏的实际使用效果！要知道牙齿并不是越白越健康！根据科学研究表明，最坚固的牙齿是自然健康略带黄色的你被骗了！在镜头里的那些唇红齿白、巧笑嫣然的美白效果其实都是后期通过电脑修图软件处理生成，并非牙膏的实际使用效果！要知道牙齿并不是越白越健康！根据科学研究表明，最坚固的牙齿是自然健康略带黄色的牙齿，看上去并不会呢么显白，更不会像纸张或者钢琴键一样白的颜色，而是应该再暗两个色调。当然如果你长期吸烟，那你的牙齿颜色会再深一点。这是因为牙齿外层是牙釉质，具有半透明特性，釉质内层的牙本质颜色并不是白色的，而是偏黄色，它的颜色会部分透过牙釉质，从而使牙齿颜色有一定的黄色。越健康的牙釉质钙化程度越高，其硬度也越高，这样的牙釉质更透明，其深部的牙本质的黄色也更容易透过而呈淡黄色。相反，如果牙釉质发育得不好，钙化程度不高，透明度就会变弱，牙本质颜色不能透过，牙齿就会呈现出一种不正常的白色或乳白色，比如患者患有初期龋齿时，牙面上会因脱矿而形成白垩色斑块。随着年龄的增长，牙釉质在此过程中被磨耗，牙齿会看上去比之前更黄，但这并不影响到牙齿的健康，所以，如果当你的牙齿就连洁牙之后都是黄色，说明这黄色不是来自牙面而是来自釉质本身，换个方向想这也说明你的釉质发育的比别人好，比别人坚固，是健康的证明通常情况下，因为色素沉淀的关系亚洲人的牙齿普遍比西方人更黄，vitapanclassical比色板。东方人种恒牙一般白的话在A2到A3差不多，西方人种会更白。牙齿美白剂最早出现，是为了改善美国人自身牙齿增龄性变化的。白种人随着年龄的增长，到达一定年龄时牙齿就会产生变化，比如过了30岁牙齿就不如从前白了。而这种增龄性在黄种人身上表现得并不那么明显。但并没有研究数据表明深色皮肤的人种拥有更白的牙齿颜色，他们的牙齿看上去更白更亮其实是因为与肤色的对比度比较高而已。所以，牙齿并不是越白越好，看起来自然，与自身肤色、性格协调的牙齿颜色才是最好的选择。在正常颜色范围内的牙齿，并非都需要做美白。如果因为牙齿颜色过深而影响美观者，就需要通过一定的治疗方法加以改善了。另外，除了随着年龄的牙齿变黄，饮食也会导致牙齿泛黄，小编列举了其中八种会导致黄牙的食物与饮料，它们不仅会黏附在牙釉质表面，导致牙齿染色，还会磨损牙釉质，让牙齿收到双重打击。使牙齿提供泛黄双重打击：红茶中富含可以使牙齿染色丹宁酸，因此它被认为是世界上导致牙齿着色问题最棘手的饮料之一。如果你在喝红茶的同时还享用了其他易使牙齿染色的食物和饮料，那伤害会大大增加。与此相反，绿茶被认为影响牙齿着色的因素就小的多，因此用绿茶代替红茶会使你的牙齿更健康。可乐，苏打水和运动饮料中的柠檬酸与磷酸会消磨牙釉质，之前流传过牙齿放在可乐中一夜就完全溶解”已经被证实为谣言，但是据实验证实：牙齿在可乐中浸泡一夜确实会引起严重着色，浸泡一周牙齿会变黑。即使无色的碳酸饮料不会导致牙齿着色，但其中的酸性还是会腐蚀牙釉质，研究表明，许多所谓的运动饮料比可乐具有更强的破坏性。众所周知，由于其深色的多酚和单宁酸，红葡萄酒是牙齿染色的罪魁祸首之一，但你不要以为喝白葡萄酒就能避免这个的问题，因为它一样糟糕，甚至更糟。虽然果汁并不能与可乐和颜色怪异的运动饮料相提并论，但非鲜榨果汁的酸性确实比大多数人所意识到的高。新鲜的果汁并没有经过处理，所以没有太大的问题，但是也同样不要让它们在你的牙齿上停留太久。当你知道你心爱的食物和饮料有可能导致牙齿着色后，第一反应肯定认为是吃完立马刷牙就没事了，但这个想法是错误的。在食用过酸性饮料或食物后，牙釉质会在接下来的一个小时中变得没有呢么坚硬，如果你在这个时间段内刷牙，其实就是在磨损你的牙釉质。你可以选择在牙釉质再次变硬后用软毛牙刷刷牙。当然，更好的选择是在你食用了易使牙齿着色的食物后，做这样两个小步骤：1、在结束后含一大口水在口中并漱口，用来清除酸和染色物质，你可以感受一下喝完可乐后的口腔与喝完可乐再漱口后的口腔，其实是有很大区别的。2、让你的口腔分泌更多的唾液，唾液具有清洁和保护作用，可以冲洗掉口中和牙齿间的食物残渣，抵抗口腔微生物，起到抗菌和杀菌的作用，避免口腔感染，是一道天然屏障。同时，唾液中所含的大量微量元素，可以促进被损伤的牙釉质的再矿化，从而预防蛀牙的进一步发展。所以，小编说了这么多，其实并不是让你完全不去碰你心爱的食物哦，比起牙齿来说，戒掉汽水更有助于缩减你的腰围（笑小编只是为了让你知道随着时间的推移，是什么原因导致牙齿变黄，并提供一个简单的小仪式，让你能够在吃喝之后好好保护你的牙齿哟微科普流言揭秘：牙齿的颜色，越白越健康？"
#a = ''.join(a[:100]+a[-100:])
#b = jieba.analyse.extract_tags(a)
#a = list(jieba.cut(a,cut_all=False))

embedding_vector_length = 32
min_count = 5
batch_size = 32
nb_epoch = 10
nb_filter = 128
filter_length = 3

model = Sequential()
model.add(Embedding(len(abc),
                    embedding_vector_length,
                    input_length=maxlen))
model.add(Conv1D(activation="relu",
                 filters=128,
                 kernel_size=3,
                 padding="valid"))
model.add(GlobalMaxPooling1D())

model.add(Dense(128))
model.add(Dropout(0.2))
model.add(Activation('relu'))

model.add(Dense(1))
model.add(Activation('sigmoid'))
model.compile(loss='binary_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])
model.fit(x_train,y_train,
          batch_size==batch_size,
          epochs=nb_epoch)

pre = model.predict_classes(x_test)

print(pre)