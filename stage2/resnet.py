from keras.models import Model
from keras.layers import Activation, BatchNormalization, Dense, Flatten, Input, Reshape
from keras.layers.convolutional import Conv2D
from keras.layers.merge import add

class ResNet(object):
    def __init__(self, input_N=256, filter_N=256, n_stages=5,
                 kernel_width=3, kernel_height=3,
                 inpkern_width=3, inpkern_height=3):
        self.input_N = input_N
        self.filter_N = filter_N
        self.n_stages = n_stages
        self.kernel_width = kernel_width
        self.kernel_height = kernel_height
        self.inpkern_width = inpkern_width
        self.inpkern_height = inpkern_height

    def create(self, input_width=15, input_height=5):
        bn_axis = 3
        inp = Input(shape=(input_height, input_width))

        x = Reshape((input_width, input_height, 1))(inp)
        x = Conv2D(self.input_N, (self.inpkern_width, self.inpkern_height), padding='same', name='conv1')(x)
        x = BatchNormalization(axis=bn_axis, name='bn_conv1')(x)
        x = Activation('relu')(x)

        for i in range(self.n_stages):
            x = self.res_block(x, [self.filter_N, self.filter_N], stage=i + 1, block='a')

        self.model = Model(inp, x)
        return self.model

    def res_block(self, input_tensor, filters, stage, block):
        nb_filter1, nb_filter2 = filters
        bn_axis = 3
        conv_name_base = 'res' + str(stage) + block + '_branch'
        bn_name_base = 'bn' + str(stage) + block + '_branch'

        x = Conv2D(nb_filter1, (self.kernel_height,self.kernel_width), padding='same', name=conv_name_base+'_a')(input_tensor)
        x = BatchNormalization(axis=bn_axis, name=bn_name_base+'_a')(x)
        x = Activation('relu')(x)
        x = Conv2D(nb_filter2, (self.kernel_height, self.kernel_width), padding='same', name=conv_name_base+'_b')(x)
        x = add([x, input_tensor])
        x = BatchNormalization(axis=bn_name_base, name=bn_name_base+'_b')(x)
        x = Activation('relu')(x)

        return x



