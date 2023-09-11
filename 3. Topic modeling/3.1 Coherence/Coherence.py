# -*- coding: utf-8 -*-
"""
Spyder Editor
Created on Sun Aug  1 13:24:15 2021
@author: Francis
This is Projectjstor.
Biometrika Coherence
"""

#==============================================================================
# ############################################################## Import library
#==============================================================================

import os
import sys
import datetime
import pandas as pd
import numpy as np
import pickle
import bz2
import lda
import tmtoolkit

#==============================================================================
# #################################################### Initialize project paths
#==============================================================================

main_path = os.path.join("D:\projetjstor\Biometrika")
os.chdir(main_path)

#==============================================================================
# ################################################################# Import data
#==============================================================================
    
DF = pd.read_pickle(os.path.join(main_path,
                                 "0. Data",
                                 "Private",
                                 "Biometrika_dataframe_final.pkl"))

dtm = pd.read_pickle(bz2.BZ2File(
        os.path.join(main_path,
                     "0. Data",
                     "Biometrika_dtm_sklearn.pbz2"), 'rb'))

with open(os.path.join(main_path,
                       "0. Data",
                       "Biometrika_vocab_sklearn.pkl"), 'rb') as f:
    vocab = pickle.load(f) 

#==============================================================================
# ############################################ Coherence analysis of multiple k
#==============================================================================

k_topics = 25 #range of topics to test coherence
num_topics = list(range(k_topics+1)[1:]) 
num_topics = num_topics + [(x+2)*25 for x in range(5)]

LDA_models = {}
time_start = datetime.datetime.now()
for i in num_topics:
    ldamodel = lda.LDA(n_topics=i,
                       n_iter=1000, #default 2000                       
                       alpha=5/i, #default 0,1, 5/i in Mallet, 50/i in Griffiths TL, Steyvers M (2004). “Finding Scientific Topics.” Proceedings of the National Academy of Sciences of the United States of America, 101, 5228–5235.
                       eta=0.01, #default 0,01, 1/i in gensim, some suggest 200/words in dict.
                       random_state=1234,) 
    LDA_models[i] = ldamodel.fit(dtm.toarray().astype(int))
    sys.stdout.write("\rModeling till "+str(i)+" topics took %s"%(str(datetime.datetime.now() - time_start)))
    sys.stdout.flush() # 11h
    
roder_2015 = [tmtoolkit.topicmod.evaluate.metric_coherence_gensim(
        measure='c_v', # C_v measure is based on a sliding window, one-set segmentation of the top words and an indirect confirmation measure that uses normalized pointwise mutual information (NPMI) and the cosine similarity
        topic_word_distrib=LDA_models[i].components_,
        vocab=np.array(vocab),
        dtm=dtm, 
        top_n=50,
        texts=DF.Lemma,
        return_mean=True) for i in num_topics] 
    
DF_k_coherence = pd.DataFrame([num_topics,[LDA_models[i].alpha for i in num_topics],[LDA_models[i].eta for i in num_topics],roder_2015]).T
DF_k_coherence.columns=['K_topics','Alpha','Eta','Coherence']

#==============================================================================
# ######################################## Coherence analysis of multiple alpha
#==============================================================================

k_topics = 23
num_alpha = [0.01,0.05,0.1,0.2,0.25,0.3,0.4,0.5,LDA_models[k_topics].alpha] #range of alphas to test coherence

LDA_models_a = {}
time_start = datetime.datetime.now()
for i in num_alpha:
    ldamodel = lda.LDA(n_topics=k_topics,
                       n_iter=1000, #default 2000                       
                       alpha=i, #default 0,1, 50/i in Griffiths TL, Steyvers M (2004). “Finding Scientific Topics.” Proceedings of the National Academy of Sciences of the United States of America, 101, 5228–5235.
                       eta=0.01, #default 0,01, 1/i in gensim, some suggest 200/words in dict.
                       random_state=1234,) 
    LDA_models_a[i] = ldamodel.fit(dtm.toarray().astype(int))
    sys.stdout.write("\rModeling till alpha "+str(i)+" took %s"%(str(datetime.datetime.now() - time_start)))
    sys.stdout.flush() # 11h

    
roder_2015_a = [tmtoolkit.topicmod.evaluate.metric_coherence_gensim(
        measure='c_v', # C_v measure is based on a sliding window, one-set segmentation of the top words and an indirect confirmation measure that uses normalized pointwise mutual information (NPMI) and the cosine similarity
        topic_word_distrib=LDA_models_a[i].components_,
        vocab=np.array(vocab),
        dtm=dtm, 
        top_n=50,
        texts=DF.Lemma,
        return_mean=True) for i in num_alpha] 
        
DF_a_coherence = pd.DataFrame([[k_topics for i in num_alpha],[LDA_models_a[i].alpha for i in num_alpha],[LDA_models_a[i].eta for i in num_alpha],roder_2015_a]).T
DF_a_coherence.columns=['K_topics','Alpha','Eta','Coherence']
    
#==============================================================================
# ################################################################ Save results
#==============================================================================
        
writer = pd.ExcelWriter(os.path.join(main_path,
                                     "3. Topic modeling",
                                     "3.1 Coherence",
                                     "Biometrika_Results_from_coherence_analyses.xlsx"))
DF_k_coherence.to_excel(writer,'K_coherence',encoding='utf8')  
DF_a_coherence.to_excel(writer,'A_coherence',encoding='utf8')      
writer.save()
writer.close()


#final model (+23 texts)
with open(os.path.join(main_path,
                       "LDA",
                       "Biometrika_lda_model_T23.pkl"), 'rb') as f:
    ldamodel = pickle.load(f) 


from gensim.corpora.dictionary import Dictionary
from gensim.models import CoherenceModel
dct = Dictionary(DF.Lemma)
vocab = {x:1 for i,x in enumerate(vocab)}

topn=10
CoherenceModel(
            coherence='c_v',  #C_v measure is based on a sliding window, one-set segmentation of the top words and an indirect confirmation measure that uses normalized pointwise mutual information (NPMI) and the cosine similarity
            topics=[np.array([x for x in pd.Series(data = vocab.keys(), index = vocab.values()).sort_index()])[np.argsort(topic_dist)][:-(topn+1):-1] for i, topic_dist in enumerate(np.array(ldamodel.components_).astype("float"))], 
            texts=DF.Lemma, 
            dictionary=dct, 
            window_size=110, #The correlation of CV and NPMI remains on a high level, when the window size is larger than 50. Default = 110.       
            topn=topn).get_coherence()

#cv=0.36486111323077886 @ k=23 & topn=10
#cv=0.3467748883801981 @ k=75 & topn=10

#cv=0.35673711640425276 @ k=23 & topn=20
#cv=0.34812226327563794 @ k=75 & topn=20

num_topics = [20,21,22,23,24,25,50,75,100,125,150]
num_topics = [15,16,17,18,19]
num_topics = [15,16,17,18,19,20,21,22,23,24,25,50,75,100,125,150]
dcv = {}
topn=20
for i in num_topics:
    c_v = CoherenceModel(
            coherence='c_v',  #C_v measure is based on a sliding window, one-set segmentation of the top words and an indirect confirmation measure that uses normalized pointwise mutual information (NPMI) and the cosine similarity
            topics=[np.array([x for x in pd.Series(data = vocab.keys(), index = vocab.values()).sort_index()])[np.argsort(topic_dist)][:-(topn+1):-1] for i, topic_dist in enumerate(np.array(LDA_models[i].components_).astype("float"))], 
            texts=DF.Lemma, 
            dictionary=dct, 
            window_size=110, #The correlation of CV and NPMI remains on a high level, when the window size is larger than 50. Default = 110.       
            topn=topn).get_coherence()
    dcv[i]=c_v
    print(i, c_v)
    
with open(os.path.join(main_path,
                       "LDA",
                       "test",
                       "Biometrika_lda_models_k.pkl"), 'wb') as f:
    pickle.dump(LDA_models, f, pickle.HIGHEST_PROTOCOL)

    
###original model

with open(os.path.join(main_path,
                       "LDA",
                       "backup2_missing23articles",
                       "Biometrika_lda_models_k.pkl"), 'rb') as f:
    LDA_models = pickle.load(f) 

DF2 = pd.read_pickle(os.path.join(main_path,
                                 "LDA",
                                 "backup2_missing23articles",
                                 "Biometrika_dataframe.pkl"))
dct2 = Dictionary(DF2.Lemma)

with open(os.path.join(main_path,
                       "LDA",
                       "backup2_missing23articles",
                       "Biometrika_vocab_sklearn.pkl"), 'rb') as f:
    vocab2 = pickle.load(f) 
vocab2 = {x:1 for i,x in enumerate(vocab2)}
i=23
topn=50
CoherenceModel(
            coherence='c_v',  #C_v measure is based on a sliding window, one-set segmentation of the top words and an indirect confirmation measure that uses normalized pointwise mutual information (NPMI) and the cosine similarity
            topics=[np.array([x for x in pd.Series(data = vocab2.keys(), index = vocab2.values()).sort_index()])[np.argsort(topic_dist)][:-(topn+1):-1] for i, topic_dist in enumerate(np.array(LDA_models[i].components_).astype("float"))], 
            texts=DF2.Lemma, 
            dictionary=dct2, 
            window_size=110, #The correlation of CV and NPMI remains on a high level, when the window size is larger than 50. Default = 110.       
            topn=topn).get_coherence()

#cv=0.5593146668592925 @ k=23 & topn=10
#cv=0.580949787135544 @ k=75 & topn=10

#cv=0.5083028163702465 @ k=23 & topn=20
#cv=0.5320845849349446 @ k=75 & topn=20

#cv=0.4548590362239996 @ k=23 & topn=50
#cv=0.46798213765856095 @ k=75 & topn=50
