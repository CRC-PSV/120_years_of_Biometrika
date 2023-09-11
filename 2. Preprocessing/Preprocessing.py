# -*- coding: utf-8 -*-
"""
Spyder Editor
Created on Sun Aug  1 13:24:15 2021
@author: Francis
This is Projectjstor.
Biometrika preprocessing
"""

#==============================================================================
# ############################################################## Import library
#==============================================================================

import os
import sys
import pandas as pd
import numpy as np
import pickle
import re
import bz2
from sklearn.feature_extraction.text import CountVectorizer
import treetaggerwrapper #  TreeTagger must be install and path specified
treetagger_path = "C:\TreeTagger"

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
                                 "Private",
                                 "Biometrika_NB_clean.pkl"))

DF = DF[DF['final decision']=='YES']
DF.reset_index(inplace=True)

DF['Citation'] = DF.citation
DF['Authors'] = DF.author.apply(lambda x: [tuple(y.split(', ')) for y in x.split('; ')])
DF['Year'] = DF.year   
DF['nb_authors'] = DF.Authors.apply(lambda x: len(x))
DF['Period'] = DF.Period_05

DF_meta = DF[['index', 'id_document', 'title', 'journal title', 'volume', 
             'issue', 'page_init', 'page_last', 'date', 'doi', 'uri_pdf',
             'language', 'nb_pages', 'data_source', 'Citation', 'Authors', 
             'Year', 'nb_authors', 'Period']]

#==============================================================================
# ########################### Word tokenization, POS tagging, and lemmatization
#==============================================================================
   
tagger = treetaggerwrapper.TreeTagger(TAGLANG='en', TAGDIR=treetagger_path)

for i in range(len(DF)):
    if DF.texte_v3[i]!='':
        tokens = treetaggerwrapper.make_tags(tagger.tag_text(DF.texte_v3[i]))
        list_of_lemma=[]
        for token in tokens:
            if (isinstance(token,treetaggerwrapper.Tag)
            and bool(re.findall('FW|MD|VVPRHASAL|VV.?|JJ.?|NN.?|NP.?|RB.?',token[1]))        
            and len(token[2])>=3):            
                token = token[2].lower()
                token = re.sub('^[\.\-\s\']+|[\.\-\s\']+$|^[a-z][\-\'][a-z]$','',token)
                list_of_lemma.append(token)
        DF.Lemma[i]=list_of_lemma

#==============================================================================
# ############################# Min word lenght, max and min document frequency
#==============================================================================

min_word_len = 3
min_df = 20 #float in range [0.0, 1.0] or int
max_df = 1.0 #float in range [0.0, 1.0] or int

def bool_min_df(numeric,min_df,sum_words):
    ''' Return True when numeric is more than an integer or more than a float % of the sum of all words'''
    if isinstance(min_df,int):
        value = int(numeric) >= min_df
    elif isinstance(min_df,float):
        value = int(numeric) >= min_df*sum_words
    else:
        raise ValueError('min_df should be integer or float')
    return value

def bool_max_df(numeric,min_df,sum_words):
    ''' Return True when numeric is less than an integer or less than a float % of the sum of all words'''
    if isinstance(min_df,int):
        value = int(numeric) <= min_df
    elif isinstance(min_df,float):
        value = int(numeric) <= min_df*sum_words
    else:
        raise ValueError('min_df should be integer or float')
    return value

#==============================================================================
# ####################################################### Vectorization Sklearn
#==============================================================================

def identity_tokenizer(text):
    ''' Method to use with Countvectorizer '''
    return text

#building stopwords set
stopwords = {line.strip() for line in open(
        os.path.join(main_path,
                     "0. Data",
                     "stopwords_en.txt"),
                     encoding='utf-8')}
stopwords = stopwords.union({'','etc.','al','@card@','i.e','fig','figure','e.g','iii','case', 'give', 'make', 'note', 'page', 'paper', 'publish', 'say', 'see', 'show', 'table', 'take', 'use', 'volume', 'well', 'work', 'write'})

#setup
vectorizer_all = CountVectorizer(lowercase = False,
                             max_df = 1.0, #float in range [0.0, 1.0] or int, default=1.0
                             min_df = 1, #float in range [0.0, 1.0] or int, default=1
                             analyzer = 'word', 
                             tokenizer = identity_tokenizer,
                             preprocessor = identity_tokenizer,
                             stop_words = None, 
                             ngram_range = (1, 1))
#Create dtm
dtm_sklearn_all = vectorizer_all.fit_transform(DF.Lemma)
#stopwords add-on
stopwords = stopwords.union({x for x in vectorizer_all.get_feature_names() if (re.findall('[^a-z\-]',x) or (len(x) <min_word_len))})

#setup
vectorizer = CountVectorizer(lowercase = False,
                             max_df = max_df, #float in range [0.0, 1.0] or int, default=1.0
                             min_df = min_df, #float in range [0.0, 1.0] or int, default=1
                             analyzer = 'word', 
                             tokenizer = identity_tokenizer,
                             preprocessor = identity_tokenizer,
                             stop_words = stopwords, 
                             ngram_range = (1, 1))
#Create matrix and vocab
dtm_sklearn = vectorizer.fit_transform(DF.Lemma)
vocab_sklearn = np.array(vectorizer.get_feature_names())
DF.Lemma = vectorizer.inverse_transform(dtm_sklearn)

#==============================================================================
# ################################################################ Save results
#==============================================================================

pd.to_pickle(DF,os.path.join(main_path,
                             "0. Data",
                             "Private",
                             "Biometrika_dataframe_final.pkl"))
    
pd.to_pickle(DF_meta,os.path.join(main_path,
                                  "0. Data",
                                  "Biometrika_dataframe_meta.pkl"))

with bz2.BZ2File(os.path.join(main_path,
                              "0. Data",
                              "Biometrika_dtm_sklearn.pbz2"), "w") as f:
    pickle.dump(dtm_sklearn, f, pickle.HIGHEST_PROTOCOL)

with open(os.path.join(main_path,
                       "0. Data",
                       "Biometrika_vocab_sklearn.pkl"), "wb") as f:
    pickle.dump(vocab_sklearn, f, pickle.HIGHEST_PROTOCOL)
    
