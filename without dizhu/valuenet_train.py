from resnet import *
import pickle

import tensorflow as tf
import keras.backend.tensorflow_backend as KTF

config = tf.ConfigProto()
config.gpu_options.allow_growth = True   #不全部占满显存, 按需分配
session = tf.Session(config=config)

# 设置session
KTF.set_session(session)

resnet = ResNet()
resnet.create()
x = pickle.load(open('./data/stage2/x.pkl','rb'))
y = pickle.load(open('./data/stage2/y.pkl','rb'))
resnet.model.fit(x, y, batch_size=1024, epochs=100, validation_split=0.1)
resnet.model.save('./value_net/value_2.h5')