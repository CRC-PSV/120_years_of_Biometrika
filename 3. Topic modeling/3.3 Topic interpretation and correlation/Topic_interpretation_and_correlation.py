# -*- coding: utf-8 -*-
"""
Spyder Editor
Created on Sun Aug  1 13:24:15 2021
@author: Francis
This is Projectjstor.
Biometrika Topic interpretation and correlation
"""

#==============================================================================
# ############################################################## Import library
#==============================================================================

import os
import sys
import pandas as pd
import numpy as np
import pickle
import bz2

#==============================================================================
# #################################################### Initialize project paths
#==============================================================================

main_path = os.path.join("your_path")
os.chdir(main_path)

#==============================================================================
# ################################################################# Import data
#==============================================================================

DF = pd.read_pickle(os.path.join(main_path,
                                 "0. Data",
                                 "Biometrika_dataframe_meta.pkl"))

dtm = pd.read_pickle(bz2.BZ2File(
        os.path.join(main_path,
                     "0. Data",
                     "Biometrika_dtm_sklearn.pbz2"), 'rb'))

with open(os.path.join(main_path,
                       "0. Data",
                       "Biometrika_vocab_sklearn.pkl"), 'rb') as f:
    vocab = pickle.load(f) 
    
with open(os.path.join(main_path,
                       "0. Data",
                       "Biometrika_lda_model.pkl"), "rb") as f:
    ldamodel = pickle.load(f)
    
#==============================================================================
# ##################### Data statistic, lda model score and lda hyperparameters
#==============================================================================
  
df_param=pd.DataFrame(index=['Value'])
df_param['Sparsity']=((dtm.todense() > 0).sum() / 
        dtm.todense().size*100) #sparsicity (% nonzero)
df_param['Log Likelyhood']=ldamodel.loglikelihood() #Log Likelyhood (higher better)
df_param['alpha']=ldamodel.alpha
df_param['eta']=ldamodel.eta
df_param['n_iter']=ldamodel.n_iter
df_param['n_components']=ldamodel.n_topics
df_param['random_state']=ldamodel.random_state
df_param['refresh']=ldamodel.refresh

#==============================================================================
# ########################################################### Topic by document
#==============================================================================

#Topic for each document
lda_output=ldamodel.doc_topic_
topicnames = ["Topic_" + str(i) for i in range(len(ldamodel.components_))]
docnames = [i for i in range(dtm.shape[0])]
df_document_topic = pd.DataFrame(lda_output, 
                                 columns=topicnames,
                                 index=docnames)
dominant_topic = np.argmax(df_document_topic.values, axis=1)

#add results to statistic general
DF['Dom_topic'] = dominant_topic
DF_topic=pd.concat([DF,df_document_topic],
                   axis=1,
                   join='inner')
    
#count document by topic
df_topic_distribution = DF['Dom_topic'].value_counts(
        ).reset_index(name="Num_Documents")
df_topic_distribution.columns = ['Topic_Num', 'Num_Doc']

# Topic - keyword Matrix
df_topic_keywords = pd.DataFrame(ldamodel.components_)#every row =1
df_topic_keywords.index = topicnames

#Transpose to topic - keyword matrix
df_keywords_topic = df_topic_keywords.transpose()
df_keywords_topic.index = vocab

# Topic - Top Keywords Dataframe
n_top_words = 50+1
DF_Topic_TKW = pd.DataFrame(columns=range(n_top_words-1),index=range(len(ldamodel.components_)))

topic_word = ldamodel.components_
for i, topic_dist in enumerate(topic_word):
    topic_words = np.array(vocab)[np.argsort(topic_dist)][:-n_top_words:-1]
    DF_Topic_TKW.loc[i]=topic_words

DF_Topic_TKW.columns = ['Word_'+str(i) for i in range(DF_Topic_TKW.shape[1])]
DF_Topic_TKW.index = ['Topic_'+str(i) for i in range(DF_Topic_TKW.shape[0])]
DF_Topic_TKW['Sum_Doc'] = np.array(DF['Dom_topic'].value_counts(
        ).sort_index())
DF_Topic_TKW['Top-10_Words'] = ''
for idx,row in DF_Topic_TKW.iterrows():
    DF_Topic_TKW['Top-10_Words'][idx]=(row['Word_0']+'; '+row['Word_1']+'; '+
                row['Word_2']+'; '+row['Word_3']+'; '+row['Word_4']+'; '+
                row['Word_5']+'; '+row['Word_6']+'; '+row['Word_7']+'; '+
                row['Word_8']+'; '+row['Word_9'])
    
#==============================================================================
# ####################################### Top words and tops articles by topics
#==============================================================================
    
# Periods - Topics top_20 articles Matrix (sorted by year)
DF_20WA=pd.DataFrame(data='', index=range(len(ldamodel.components_)),columns=['Top_20_words','Top_20_articles'])
for i in range(len(DF_20WA)):
    DF_20WA.Top_20_words[i] = '\n'.join(str(rank+1)+'. '+x for rank, x in enumerate(np.array(vocab)[np.argsort(ldamodel.components_[i])][:-21:-1]))
    pd.DataFrame(np.argsort(df_document_topic.values, axis=0)[:-21:-1])[1]
    DF_20WA.Top_20_articles[i] = '\n'.join([str(rank+1)+'. '+DF_topic.Citation[idx] for rank, idx in enumerate(np.argsort(df_document_topic.values, axis=0)[:-21:-1].T[i])])

#==============================================================================
# ########################################################### Topic correlation
#==============================================================================

# Topic Pearson Correlation
DF_TfromD = df_document_topic.corr(method='pearson')

DF_TfromW=df_topic_keywords.T.corr(method='pearson')

#==============================================================================
# ################################################################ Save results
#==============================================================================
        
# Save lda results to excel
writer = pd.ExcelWriter(os.path.join(main_path,
                                     "3. Topic modeling",
                                     "3.3 Topic interpretation and correlation",
                                     "Biometrika_Results_LDA.xlsx"))
df_param.T.to_excel(writer,'Para Score',encoding='utf8')        
pd.DataFrame([vocab,[x[0] for x in dtm.T.sum(axis=1).tolist()]]).T.to_excel(writer,'Vocab',encoding='utf8')
DF_topic.to_excel(writer,'Doc vs Topic',encoding='utf8')
DF_Topic_TKW.to_excel(writer,'Top 50 Topics Words',encoding='utf8')
df_keywords_topic.to_excel(writer,'Words vs Topics',encoding='utf8',
                           header=topicnames,
                           index=[vocab])
DF_20WA.to_excel(writer,'Top_20',encoding='utf8')
DF_TfromD.to_excel(writer,'Topic Cor. from Doc',encoding='utf8')
DF_TfromW.to_excel(writer,'Topic Cor. from Word',encoding='utf8')
writer.save()
writer.close()
    
