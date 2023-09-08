# 120 years of Biometrika
## Abstract
Founded by Karl Pearson in 1901, Biometrika has played a key role in the development of statistics throughout the 20th and the beginning of the 21st century. While the early history of the journal is well-known, at least in broad strokes, the later — and longer — episodes of its intellectual development remain understudied. The objective of this study is to provide an all-encompassing view of 120 years of Biometrika. To this end, computational text-mining approaches are implemented to analyze the full-text content of all published research articles in the journal between 1901 and 2020 (N = 5596). These approaches include synchronic and diachronic modeling, as well as author network analysis. The results show the detailed content of 23 major topics that span over more than a century of publishing history. Striking changes in the thematic content of the journal are also documented, from the decline of Pearsonian biometry research in the 1930s to the rise of modern statistics and probability theory in the 1970s and subsequently. Author network shows the existence of several sub-communities of researchers, well-aligned with topic clusters and their evolution through time, while highlighting the role of specific key figures in the 120 year long history of Biometrika.
## Requirements
This code was tested on Python 3.7.3. Other requirements are as follows (see requirements.txt):
- lda
- numpy
- pandas
- sklearn
- tmtoolkit
- treetaggerwrapper
## Quick Start
- Install libraries: pip install -r requirements.txt
- Install TreeTagger
### 1. Corpus assembly and cleaning\*
- Execute to replicate research : Corpus_assembly_and_cleaning.py
### 2. Preprocessing\*
- Execute to replicate research : Preprocessing.py
### 3. Topic modeling
#### 3.1 Coherence\*
- Execute to replicate research : Coherence.py
#### 3.2 LDA
- Execute to replicate research : LDA.py
#### 3.3 Topic interpretation and correlation
- Execute to replicate research : Topic_interpretation_and_correlation.py
### 4. Diachronic modeling
- Execute to replicate research : Diachronic_modeling.py
### 5. Author modeling
- Execute to replicate research : Author_modeling.py

\*Note that for legal issues, the complete full-text of journal articles could not be included with the dataset (but can be retrieved by asking the respective publishers).
## Citation
Please cite: Bertoldi N., Lareau F., Pence C.H., Malaterre C. (2023) A quantitative window on the history of statistics: Topic-modelling 120 years of 
Biometrika. Digital Scholarship in the Humanities.

## Authors
### Nicola Bertoldi
- Email: nicola.bertoldi87@gmail.com
### Francis Lareau
- Email: francislareau@hotmail.com
### Charles H. Pence
- Email: charles.pence@uclouvain.be
### Christophe Malaterre
- Email: malaterre.christophe@uqam.ca

## Acknowledgments
The authors are grateful to JSTOR and Oxford University Press for providing access to Biometrika articles for text-mining purposes. The authors thank the audiences of a 2021 TEC seminar at UQAM, and of the 2021 SPS congress for comments on an earlier version of the manuscript. N.B was supported by fellowships from the Canada Research Chair in Philosophy of the Life Sciences at UQAM and the CIRST. F.L. acknowledges funding from the Fonds de recherche du Québec - Société et culture (FRQSC-276470) and the Canada Research Chair in Philosophy of the Life Sciences at UQAM. C.H.P. and C.M. acknowledge funding from the XIe Commission mixte permanente Québec–Wallonie-Bruxelles (Grant 11.805). C.M. acknowledges funding from Canada Foundation for Innovation (Grant 34555) and Canada Research Chairs (CRC-950-230795).
