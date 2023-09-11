# -*- coding: utf-8 -*-
"""
Spyder Editor
Created on Sun Aug  1 13:24:15 2021
@author: Francis
This is Projectjstor.
Biometrika LDA
"""

#==============================================================================
# ############################################################## Import library
#==============================================================================

import os
import pickle
import pandas as pd
import bz2
import lda

#==============================================================================
# #################################################### Initialize project paths
#==============================================================================

main_path = os.path.join("your_path")
os.chdir(main_path)

#==============================================================================
# ################################################################# Import data
#==============================================================================
    
dtm = pd.read_pickle(bz2.BZ2File(
        os.path.join(main_path,
                     "0. Data",
                     "Biometrika_dtm_sklearn.pbz2"), 'rb'))

with open(os.path.join(main_path,
                       "0. Data",
                       "Biometrika_vocab_sklearn.pkl"), 'rb') as f:
    vocab = pickle.load(f) 

#==============================================================================
# ######################################### Temporary short cut for k23 and k75
#==============================================================================

ldamodel = lda.LDA(n_topics=23,
                   n_iter=1000,
                   alpha=0.1, 
                   eta=0.01, 
                   random_state=1234)

ldamodel.fit(dtm.toarray().astype(int))

#==============================================================================
# ################################################################ Save results
#==============================================================================
        
with open(os.path.join(main_path,
                       "0. Data",
                       "Biometrika_lda_model.pkl"), "wb") as f:
    pickle.dump(ldamodel, f, pickle.HIGHEST_PROTOCOL)
    
