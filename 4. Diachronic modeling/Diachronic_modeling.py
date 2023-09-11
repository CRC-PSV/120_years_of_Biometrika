# -*- coding: utf-8 -*-
"""
Spyder Editor
Created on Sun Aug  1 13:24:15 2021
@author: Francis
This is Projectjstor.
Biometrika Diachronic modeling
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
# ############################################################# Topic by period
#==============================================================================

# Topic - Period Matrix
DF_PT=pd.DataFrame(lda_output,
                   columns=topicnames,
                   index=docnames)

DF_PT['Period']=DF.Period
DF_PT = DF_PT.groupby(['Period']).sum()
DF_TP = DF_PT.transpose()
DF_TP = DF_TP/DF_TP.sum()
DF_TP_Overall = DF_PT.transpose()
DF_TP_Overall['Raw'] = DF_PT.sum()
DF_TP_Overall['Overall'] = DF_PT.sum() / sum(DF_PT.sum())


# Periods - Topics top_10 articles Matrix (sorted by year)
DF_PT_T10A=pd.DataFrame(data='', index=DF_TP.columns,columns=DF_TP.index)
for period in DF_TP.columns:
    for topic in DF_TP.index:
        for idx in DF_topic[DF_topic.Period==period].nlargest(
                10,topic).sort_values('Year',ascending=False).index:
            DF_PT_T10A[topic][period]=DF_PT_T10A[topic][period]+DF_topic.Citation[idx]+'\n'
            
# Topics top_20 articles Matrix by Periods - (sorted by weight)
DF_PT_T20A=pd.DataFrame(data='', index=DF_TP.columns,columns=DF_TP.index)
for period in DF_TP.columns:
    for topic in DF_TP.index:
        for idx in DF_topic.nlargest(20,topic).index:
            if DF_topic.Period[idx]==period:
                DF_PT_T20A[topic][period]=DF_PT_T20A[topic][period]+DF_topic.Citation[idx]+'\n'

#==============================================================================
# ################################################################ Save results
#==============================================================================
        
# Save lda results to excel
writer = pd.ExcelWriter(os.path.join(main_path,
                                     "4. Diachronic modeling",
                                     "Biometrika_Results_Diachronic_modeling.xlsx"))
df_param.T.to_excel(writer,'Para Score',encoding='utf8')        
pd.DataFrame([vocab,[x[0] for x in dtm.T.sum(axis=1).tolist()]]).T.to_excel(writer,'Vocab',encoding='utf8')
DF_TP.to_excel(writer,'Topics vs Periods',encoding='utf8')
DF_TP_Overall.to_excel(writer,'Overall Topics vs Periods',encoding='utf8')
DF_PT_T10A.to_excel(writer,'Top 10 articles',encoding='utf8')
DF_PT_T20A.to_excel(writer,'Top 20 articles',encoding='utf8')
writer.save()
writer.close()
    