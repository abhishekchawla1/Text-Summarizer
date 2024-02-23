# -*- coding: utf-8 -*-
"""Text Summarization

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Bo16NR6TyGUEpwoZ4JJKb8W7kHSifWLj
"""

!pip install opendatasets

import opendatasets as od

data='https://www.kaggle.com/datasets/gowrishankarp/newspaper-text-summarization-cnn-dailymail/code'

od.download(data)

import os

data_dir='./newspaper-text-summarization-cnn-dailymail'

os.listdir(data_dir)

import pandas as pd
import numpy as np
df_train=pd.read_csv(r'/content/newspaper-text-summarization-cnn-dailymail/cnn_dailymail/train.csv')

df_train.shape

df_train.head()

df_validation=pd.read_csv(r'/content/newspaper-text-summarization-cnn-dailymail/cnn_dailymail/validation.csv')

df_validation.shape

df_test=pd.read_csv(r'/content/newspaper-text-summarization-cnn-dailymail/cnn_dailymail/test.csv')

df_test.shape

df_train.info()

df_train.columns

df_train.isnull().sum()

df_train.duplicated().any()

training=df_train['article'][:500].replace("'","")
testing=df_train['highlights'][:500].replace("'","")

import tensorflow as tf
tokenizer=tf.keras.preprocessing.text.Tokenizer()

def token_news(sent):
  tokenizer.fit_on_texts([sent])
  seq=tokenizer.texts_to_sequences([sent])
  seq_len=50
  pad_seq=tf.keras.preprocessing.sequence.pad_sequences(seq,maxlen=seq_len)
  return pad_seq

import pandas as pd
import numpy as np

training=training.apply(token_news,tokenizer)

training

testing=testing.apply(token_news,tokenizer)

testing

from tensorflow.keras.models import Model

vocab_size=10000
embedding_dim=200
seq_len=50
input=tf.keras.Input(shape=seq_len)
ehs=[]
e_layer=tf.keras.layers.Embedding(input_dim=vocab_size,output_dim=embedding_dim)(input)
e_lstm=tf.keras.layers.Bidirectional(tf.keras.layers.LSTM(1600,return_sequences=True))(e_layer)
encoded=tf.keras.layers.Concatenate()([e_lstm[:,-1,:],e_lstm[:,0,:]])
model=tf.keras.Model(inputs=input,outputs=encoded)

def encoder(a,ta,model):
  o=tf.keras.optimizers.Adam(learning_rate=0.01)
  for i in range(len(a)):
    with tf.GradientTape() as tape:
      result=model(a[i],training=True)
      test_result=model(ta[i],training=True)
      loss=tf.keras.losses.mean_squared_error(result,test_result)

      ehs.append(result)
      g=tape.gradient(loss,model.trainable_variables)
      o.apply_gradients(zip(g,model.trainable_variables))
      return ehs

def Decoder(eh,target_tokens,model):
  loss=0
  seq_len=50
  hidden_size=128
  emb_dim=128
  vocab_size=10000
  c_vector=tf.zeros((128,50))
  d_state=tf.zeros((128,50))
  learning_rate=0.01
  o=tf.keras.optimizers.Adam(learning_rate=0.01)
  v = tf.random.normal(shape=(hidden_size,50))
  Wh = tf.random.normal(shape=(hidden_size, 50))
  Ws = tf.random.normal(shape=(hidden_size, 50))
  battn = tf.random.normal(shape=(hidden_size,50))
  weights= tf.random.normal(shape=(100, 1))
  bias=tf.random.uniform([])

  for t in range(len(target_tokens)):
    input=tf.keras.Input(shape=(seq_len))
    e_layer=tf.keras.layers.Embedding(input_dim=vocab_size,output_dim=emb_dim)(input)
    model=tf.keras.Model(inputs=input,outputs=e_layer)
    o_e=model.predict(target_tokens[t])
    attention_score=[]
    for i in range(len(ehs)):
      ehs[i]=tf.reshape(ehs[i],(128,50))
      eti=v*tf.nn.tanh(Wh*ehs[i]+Ws*d_state+battn)
      attention_score.append(eti)

    ad=tf.nn.softmax(attention_score)
    for i in range(len(ehs)):
      c_vector+=ad[i]*ehs[i]

    o_e=tf.reshape(o_e,((128,50,1)))
    o_e=tf.squeeze(o_e,axis=-1)
    c_i=tf.expand_dims(tf.concat([c_vector,o_e],axis=-1),axis=0)
    oe1=tf.matmul(c_i,weights)+bias
    vocab_dist=tf.nn.softmax(oe1,axis=1)
    hpi=np.argmax(vocab_dist)
    twp=vocab_dist[0,hpi,0]
    timeless_loss=-tf.math.log(twp)
    d_state=(d_state+c_vector)/2
    d_state=tf.reshape(d_state,(128,50))

    loss+=timeless_loss
    m_loss=loss/(t+1)

    v+=learning_rate*m_loss*tf.nn.tanh(Wh*ehs[i]+Ws*d_state+battn)
    Ws+=learning_rate*m_loss*d_state
    Wh=Wh+learning_rate*m_loss*ehs[i]
    battn+=learning_rate*m_loss
    bias+=learning_rate*m_loss
    weights+=learning_rate*m_loss*weights
    d_state=(d_state+c_vector)/2
    d_state = tf.reshape(d_state, (128, 50))


  return [v,Ws,Wh,battn,weights,bias]

eh=encoder(training,testing,model)

is1=tf.keras.Input(shape=(128,100))
l2=tf.keras.layers.Dense(1)(is1)
model=tf.keras.Model(inputs=is1,outputs=l2)

testing

eh

model

type(testing)

type(eh)

v, Ws, Wh, battn, weights, bias = decoder(eh,testing,model)

def tests(para,v,ws,wh,battn,weights,model,bias,tokenizer,l=50):
  tokenizer.fit_on_texts([para])
  seq=tokenizer.texts_to_sequences([para])
  seq_len=50
  pad_seq=tf.keras.preprocessing.sequence.pad_sequences(seq,maxlen=seq_len)
  t_para=token_news(para)
  ehs=[model.predict(t_para)]
  summary=[]
  hs=128
  ed=50
  c_vector=tf.zeros((128,50))
  d_state=tf.zeros((128,50))
  ct=np.zeros((128))
  for j in range(l):
    i=tf.keras.Input(shape=(seq_len))
    el=tf.keras.layers.Embedding(input_dim=vocab_size,output_dim=ed)(i)
    model=tf.keras.Model(inputs=i,outputs=el)
    oe=model.predict(ct,verbose=0)

    attention_score=[]
    for i in range(len(ehs)):
      ehs[i]=tf.reshape(ehs[i],(128,50))
      eti=v*tf.nn.tanh(wh*ehs[i]+ws*d_state+battn)
      attention_score.append(eti)

    ad=tf.nn.softmax(attention_score)
    for i in range(len(ehs)):
      c_vector+=ad[i]*ehs[i]

    oe=tf.reshape(oe,(128,50,1))
    oe=tf.squeeze(oe,axis=-1)
    ci=tf.expand_dims(tf.concat([c_vector,oe]),axis=0)
    oe1=tf.matmul(ci,weights)+bias
    vd=tf.nn.softmax(oe1,axis=1)
    hpi=np.argmax(vd)
    ct[j]=hpi
    d_state=(d_state+c_vector)/2
    d_state=tf.reshape(d_state,(128,50))
    summary.append(ct)

  ttw={tokenizer.word_index[i]:i for i in tokenizer.word_index.keys()}
  ttw.update({0.0:'',127.0:''})
  return (' '.join([ttw[i] for i in ct]))

df_test

test=df_test['article'][1:3].replace("'","")

for i in test:
  print(i+'\n')
  print(tests(i,v,Ws,Wh,battn,weights,model,bias,tokenizer,l=50))