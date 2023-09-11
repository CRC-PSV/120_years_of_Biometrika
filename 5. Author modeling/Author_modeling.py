# -*- coding: utf-8 -*-
"""
Spyder Editor
Created on Sun Aug  1 13:24:15 2021
@author: Francis
This is Projectjstor.
Biometrika Author modeling
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

main_path = os.path.join("D:\projetjstor\Biometrika")
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

DF_topic=pd.concat([DF,df_document_topic],
                   axis=1,
                   join='inner')

#==============================================================================
# ############################################################# Topic by author
#==============================================================================       
                        
# Author - Topic Matrix
authors = set()
authors_list = list()
for group_author in DF.Authors:
    for author in group_author:
        authors.add(author)
        authors_list.append(author)
authors = sorted(authors)
        
DF_AT = pd.DataFrame(data='', index=range(len(authors)),columns=topicnames+['Author','Pub_sum','Pub_weighted'])
DF_AT_norm = pd.DataFrame(data='', index=range(len(authors)),columns=topicnames)
for idx,author in enumerate(authors):
    list_bool = DF.Authors.apply(lambda x: True if author in x else False)
    #author_topic=sum(lda_output[list_bool])/len(lda_output[list_bool])
    author_topic=sum(lda_output[list_bool]/np.transpose(np.repeat(np.expand_dims(DF.nb_authors[list_bool],axis=0), repeats=len(ldamodel.components_), axis=0)))
    author_topic_norm=author_topic/sum(author_topic)
    DF_AT.loc[idx]=list(author_topic)+[author,
             authors_list.count(author),
             sum(1/DF.nb_authors[list_bool])]
    DF_AT_norm.loc[idx]=list(author_topic_norm)

#==============================================================================
# ################################################### Topic by period + author
#==============================================================================

# Topic - Journal + Period Matrix (12hre)
DF_PAT = pd.DataFrame([[item for sublist in [sorted(set(DF_topic.Period))]*len(authors) for item in sublist],
                         [item for sublist in [[x]*len(set(DF_topic.Period)) for x in authors] for item in sublist]
                         ], index=['Period','Authors']).transpose()
DF_PAT=DF_PAT.reindex(columns =['Period','Authors']+topicnames)
for idx,row in DF_PAT.iterrows():    
    sys.stdout.write("\r"+str(idx)+"/"+str(len(DF_PAT))) # \r prints a carriage return, then we print on top of the previous line.
    list_bool_1 = DF_topic.Authors.apply(lambda x: True if row.Authors in x else False)
    list_bool_2 = DF_topic.Period.apply(lambda x: True if row.Period in x else False)
    if sum(list_bool_1 & list_bool_2):
        author_period_topic = sum(lda_output[list_bool_1 & list_bool_2]/np.transpose(np.repeat(np.expand_dims(DF.nb_authors[list_bool_1 & list_bool_2],axis=0), repeats=len(ldamodel.components_), axis=0)))
        DF_PAT.loc[idx]=[row[0],row[1]]+list(author_period_topic)
              
#==============================================================================
# ########################################################## Author correlation
#==============================================================================

# Author Pearson Correlation
DF_AfromT = DF_AT_norm.astype('float64').T.corr(method='pearson')

#==============================================================================
# ####################################################### Some corpus statistic
#==============================================================================

DF_stat = pd.DataFrame(data = [[group[0], len(group[1])] for group in DF.groupby(['Period'])], columns= ['Period','Total_article'])

#nb moyen de mots par article par période
DF_stat['Total_word'] = [dtm[group[1].index].sum() for group in DF.groupby(['Period'])]
DF_stat['Mean_word'] = DF_stat['Total_word']/DF_stat['Total_article']

#nb moyen d’auteurs par période (la somme par période du nb de noms distincts dans tous les articles de la période)
DF_stat['Total_author'] = [group[1].nb_authors.sum() for group in DF.groupby(['Period'])]
DF_stat['Mean_author'] = DF_stat['Total_author']/DF_stat['Total_article']

#==============================================================================
# ################################################################ Save results
#==============================================================================
        
# Save lda results to excel
writer = pd.ExcelWriter(os.path.join(main_path,
                                     "5. Author modeling",
                                     "Biometrika_Results_Author_modeling.xlsx"))
df_param.T.to_excel(writer,'Para Score',encoding='utf8')        
pd.DataFrame([vocab,[x[0] for x in dtm.T.sum(axis=1).tolist()]]).T.to_excel(writer,'Vocab',encoding='utf8')
DF_stat.to_excel(writer,'Statistics',encoding='utf8')
DF_AT.to_excel(writer,'Authors vs Topics',encoding='utf8')
DF_PAT.to_excel(writer,'Authors+P vs Topics',encoding='utf8')
DF_AfromT.to_excel(writer,'Author Cor.',encoding='utf8')
writer.save()
writer.close()
    