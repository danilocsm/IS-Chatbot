import heapq
from numpy import argmax, array
from random import choice
import tensorflow as tf 
from tensorflow.keras.layers import Dense, Embedding, Dropout, GlobalAveragePooling1D, Flatten
import os
import utils
import re

PATH_TO_MODEL = re.sub(r'\\src', r'\\model\\model.h5', os.getcwd())
informational_intent = ['time', 'date']

class Engine():

    def __init__(self):

        self.configs = utils.load_configs()
        self.answers = utils.load_answers()
        self.model =  self.train_engine()


    def make_model(self) :

        model = tf.keras.Sequential()
        model.add(Embedding(len(self.configs['word_to_id']), 32, input_length=self.configs['sequence_len']))
        model.add(Flatten())
        model.add(Dense(16, activation='relu'))
        model.add(Dense(16, activation='relu'))
        model.add(Dense(self.configs['output_len'],activation='softmax'))
        model.compile(optimizer=tf.keras.optimizers.RMSprop(0.001),
                            loss='binary_crossentropy',
                            metrics=['accuracy'])
        return model


    def train_engine(self, retrain=False):
        
        if os.path.isfile(PATH_TO_MODEL) and not retrain:
            model = tf.keras.models.load_model(PATH_TO_MODEL)
            
        else:
            model = self.make_model()
            doc_x, doc_y = array(self.configs['doc_x']), array(self.configs['doc_y'])
            model.fit(doc_x, doc_y, epochs=10, batch_size=32, verbose=0)
            model.evaluate(doc_x, doc_y)
            model.save(PATH_TO_MODEL)
        
        return model 

    
    def engine_predict(self, _input):
        word_to_id = self.configs['word_to_id']
        words = self.configs['words']
        encoded_input = array([array(utils.pad_sequence(word_to_id, utils.encode_input(word_to_id, words, _input), self.configs['sequence_len']))])
        predicted = argmax(self.model.predict(encoded_input))
        # predict_best_3 = heapq.nlargest(3, range(len(predicted)), predicted.take)
        predicted_intent = self.configs['index_intents'][str(predicted)]
        information = ""
        if predicted_intent in informational_intent:
            information = utils.get_information(predicted_intent)
        # print(predicted_intent)
        return (choice(self.answers[predicted_intent]) + information), predicted_intent 

        