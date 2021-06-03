import pandas as pd
import numpy as np
import sklearn
from sklearn.model_selection import GroupKFold
import matplotlib.pyplot as plt
from tqdm.notebook import tqdm

# import tensorflow_hub as hub
import tensorflow as tf
# import bert_tokenization as tokenization
import tensorflow.keras.backend as K
from tensorflow import keras 

import os
from scipy.stats import spearmanr
from math import floor, ceil
#!pip3 install sentencepiece
from transformers import *

import seaborn as sns
import string
import re    #for regex

np.set_printoptions(suppress=True)
print(tf.__version__)

training_sample_count = 160000 # 4000
training_epochs = 3 # 3
test_count = 40000

if True:
    training_sample_count = 500 # 4000
    training_epochs = 1 # 3
    test_count = 300
running_folds = 1 # 2

MAX_SENTENCE_LENGTH = 20
MAX_SENTENCES = 5
MAX_LENGTH = 100

df = pd.read_csv('dataset.csv')
#df = df[['text', 'humor']]

df_train = pd.read_csv('train.csv')
#df_train = df_train[['text', 'humor']]

df_train = df_train[:training_sample_count*running_folds]

df_test = pd.read_csv('dev.csv')
#df_test = df_test[['text', 'humor']]

df_test = df_test[:test_count]

test_df_y = df_test.copy()
del df_test['humor']

df_sub = test_df_y.copy()

print(len(df),len(df_train),len(df_test))

output_categories = list(df_train.columns[[1]])
input_categories = list(df_train.columns[[0]])

TARGET_COUNT = len(output_categories)

print('\ninput categories:\n\t', input_categories)
print('\noutput TARGET_COUNT:\n\t', TARGET_COUNT)
print('\noutput categories:\n\t', output_categories)

from transformers import BertTokenizer

MODEL_TYPE = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(MODEL_TYPE)

import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def return_id(str1, str2, truncation_strategy, length):

    inputs = tokenizer.encode_plus(str1, str2,
        add_special_tokens=True,
        max_length=length,
        truncation_strategy=truncation_strategy)

    input_ids =  inputs["input_ids"]
    input_masks = [1] * len(input_ids)
    input_segments = inputs["token_type_ids"]
    padding_length = length - len(input_ids)
    padding_id = tokenizer.pad_token_id
    input_ids = input_ids + ([padding_id] * padding_length)
    input_masks = input_masks + ([0] * padding_length)
    input_segments = input_segments + ([0] * padding_length)

    return [input_ids, input_masks, input_segments]


def compute_input_arrays(df, columns, tokenizer):
    model_input = []
    for xx in range((MAX_SENTENCES*3)+3):
        model_input.append([])
    
    for _, row in tqdm(df[columns].iterrows()):
        i = 0
        
        # sent
        sentences = sent_tokenize(row.text)
        for xx in range(MAX_SENTENCES):
            s = sentences[xx] if xx<len(sentences) else ''
            ids_q, masks_q, segments_q = return_id(s, None, 'longest_first', MAX_SENTENCE_LENGTH)
            model_input[i].append(ids_q)
            i+=1
            model_input[i].append(masks_q)
            i+=1
            model_input[i].append(segments_q)
            i+=1
        
        # full row
        ids_q, masks_q, segments_q = return_id(row.text, None, 'longest_first', MAX_LENGTH)
        model_input[i].append(ids_q)
        i+=1
        model_input[i].append(masks_q)
        i+=1
        model_input[i].append(segments_q)
        
    for xx in range((MAX_SENTENCES*3)+3):
        model_input[xx] = np.asarray(model_input[xx], dtype=np.int32)
        
    print(model_input[0].shape)
    return model_input

inputs = compute_input_arrays(df_train, input_categories, tokenizer)
test_inputs = compute_input_arrays(df_test, input_categories, tokenizer)

print(len(inputs), len(inputs[0]), len(inputs[0][0]))

# check out input for 7th row
xx = 7
print(df_train.iloc[xx,0])
print(sent_tokenize(df_train.iloc[xx,0]))
inputs[0][xx], inputs[3][xx], inputs[6][xx], inputs[15][xx]

def compute_output_arrays(df, columns):
    return np.asarray(df[columns])

outputs = compute_output_arrays(df_train, output_categories)

config = BertConfig() # print(config) to see settings
config.output_hidden_states = False # Set to True to obtain hidden states
bert_model = TFBertModel.from_pretrained('bert-base-uncased', config=config)
config


def create_model():
    # model structure
    # takes q_ids [max=20*MAX_SENTENCES] and a_ids [max=200]
    import gc
    
    model_inputs = []
    f_inputs=[]
    for i in range(MAX_SENTENCES):
        # bert embeddings
        q_id = tf.keras.layers.Input((MAX_SENTENCE_LENGTH,), dtype=tf.int32)
        q_mask = tf.keras.layers.Input((MAX_SENTENCE_LENGTH,), dtype=tf.int32)
        q_atn = tf.keras.layers.Input((MAX_SENTENCE_LENGTH,), dtype=tf.int32)
        q_embedding = bert_model(q_id, attention_mask=q_mask, token_type_ids=q_atn)[0]
        q = tf.keras.layers.GlobalAveragePooling1D()(q_embedding)
        
        # internal model
        hidden1 = keras.layers.Dense(32, activation="relu")(q)
        hidden2 = keras.layers.Dropout(0.3)(hidden1)
        hidden3 = keras.layers.Dense(8, activation='relu')(hidden2)
        
        f_inputs.append(hidden3)
        model_inputs.extend([q_id, q_mask, q_atn])
        
    # whole sentence
    a_id = tf.keras.layers.Input((MAX_LENGTH,), dtype=tf.int32)
    a_mask = tf.keras.layers.Input((MAX_LENGTH,), dtype=tf.int32)
    a_atn = tf.keras.layers.Input((MAX_LENGTH,), dtype=tf.int32)
    a_embedding = bert_model(a_id, attention_mask=a_mask, token_type_ids=a_atn)[0]
    a = tf.keras.layers.GlobalAveragePooling1D()(a_embedding)
    print(a.shape)
    # internal model
    hidden1 = keras.layers.Dense(256, activation="relu")(a)
    hidden2 = keras.layers.Dropout(0.2)(hidden1)
    hidden3 = keras.layers.Dense(64, activation='relu')(hidden2)

    f_inputs.append(hidden3)
    model_inputs.extend([a_id, a_mask, a_atn])
    
    # final classifier
    concat_ = keras.layers.Concatenate()(f_inputs)
    hiddenf1 = keras.layers.Dense(512, activation='relu')(concat_)
    hiddenf2 = keras.layers.Dropout(0.2)(hiddenf1)
    hiddenf3 = keras.layers.Dense(256, activation='relu')(hiddenf2)
    
    output = keras.layers.Dense(TARGET_COUNT, activation='sigmoid')(hiddenf3) # softmax
    model = keras.Model(inputs=model_inputs, outputs=[output] )
    
    gc.collect()
    return model

model = create_model()


# Evaluation Metrics
import sklearn
def print_evaluation_metrics(y_true, y_pred, label='', is_regression=True, label2=''):
    print('==================', label2)
    ### For regression
    if is_regression:
        print('mean_absolute_error',label,':', sklearn.metrics.mean_absolute_error(y_true, y_pred))
        print('mean_squared_error',label,':', sklearn.metrics.mean_squared_error(y_true, y_pred))
        print('r2 score',label,':', sklearn.metrics.r2_score(y_true, y_pred))
        #     print('max_error',label,':', sklearn.metrics.max_error(y_true, y_pred))
        return sklearn.metrics.mean_squared_error(y_true, y_pred)
    else:
        ### FOR Classification
#         print('balanced_accuracy_score',label,':', sklearn.metrics.balanced_accuracy_score(y_true, y_pred))
#         print('average_precision_score',label,':', sklearn.metrics.average_precision_score(y_true, y_pred))
#         print('balanced_accuracy_score',label,':', sklearn.metrics.balanced_accuracy_score(y_true, y_pred))
#         print('accuracy_score',label,':', sklearn.metrics.accuracy_score(y_true, y_pred))
        print('f1_score',label,':', sklearn.metrics.f1_score(y_true, y_pred))
        
        matrix = sklearn.metrics.confusion_matrix(y_true, y_pred)
        print(matrix)
        TP,TN,FP,FN = matrix[1][1],matrix[0][0],matrix[0][1],matrix[1][0]
        Accuracy = (TP+TN)/(TP+FP+FN+TN)
        Precision = TP/(TP+FP)
        Recall = TP/(TP+FN)
        F1 = 2*(Recall * Precision) / (Recall + Precision)
        print('Acc', Accuracy, 'Prec', Precision, 'Rec', Recall, 'F1',F1)
        return sklearn.metrics.accuracy_score(y_true, y_pred)

print_evaluation_metrics([1,0], [0.9,0.1], '', True)
print_evaluation_metrics([1,0], [1,1], '', False)

min_acc = 100
min_test = []
valid_preds = []
test_preds = []
best_model = False
for BS in [6]:
    LR = 1e-5
    print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
    print('LR=', LR)
    gkf = GroupKFold(n_splits=2).split(X=df_train.text, groups=df_train.text)

    for fold, (train_idx, valid_idx) in enumerate(gkf):
        if fold not in range(running_folds):
            continue
        train_inputs = [(inputs[i][train_idx])[:training_sample_count] for i in range(len(inputs))]
        train_outputs = (outputs[train_idx])[:training_sample_count]

        valid_inputs = [inputs[i][valid_idx] for i in range(len(inputs))]
        valid_outputs = outputs[valid_idx]

        print(len(train_idx), len(train_outputs))
#         print(train_idx[:10], valid_idx[:10])

        model = create_model()
        K.clear_session()
        optimizer = tf.keras.optimizers.Adam(learning_rate=LR)
        model.compile(loss='binary_crossentropy', optimizer=optimizer)
        print('model compiled')
        
        model.fit(train_inputs, train_outputs, epochs=training_epochs, batch_size=BS,
                 validation_split=0.2, verbose=1
                 )
        print("model fit")
        # model.save_weights(f'bert-{fold}.h5')



best_model.save('colbert4')
