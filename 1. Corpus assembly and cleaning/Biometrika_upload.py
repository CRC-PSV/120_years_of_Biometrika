# -*- coding: utf-8 -*-
"""
Created on Fri Mar 11 14:30:48 2022

@author: nicol
"""

#-----------------------------------------------------------------------------#
# Import text and xml files for Biometrika articles (1901-2013).
#-----------------------------------------------------------------------------#


import os

folder_metadata = ___
folder_ngram1 = ___
folder_ngram2 = ___
folder_ngram3 = ___
folder_ocr = ___

file_metadata = os.listdir(folder_metadata)
file_ngram1 = os.listdir(folder_ngram1)
file_ngram2 = os.listdir(folder_ngram2)
file_ngram3 = os.listdir(folder_ngram3)
file_ocr = os.listdir(folder_ocr)


#-----------------------------------------------------------------------------#
# Convert files to Tree objects in python. A file is converted into a tree-like 
# structure whose nodes are the various text blocks. 
# See https://docs.python.org/3/library/xml.etree.elementtree.html
#-----------------------------------------------------------------------------#


import xml.etree.ElementTree as ET

import re


archive = []


for file in file_metadata:

    tree = ET.parse(folder_metadata + "\\" + file)
     
    root = tree.getroot()
    
    archive.append(root)
    

archive_text = []

file_names = []

reg = re.compile(r'\-')


for file in file_ocr:
    
    file_name = reg.split(file)[2].replace(".txt", "")
    
    file_names.append(file_name)
     
    tree = ET.parse(folder_ocr + "\\" + file)
    
    root = tree.getroot()
    
    archive_text.append(root)
    
       
#-----------------------------------------------------------------------------#
# Initialize the dataframe with columns "id_document", "author", "year", "title", 
#                         "journal title", "volume", "issue", "page_init",
#                        "page_last", "date", "doi", "uri_pdf", "bibliography", 
#                        "article_type_1", "language", "texte_v1", "citation"
#-----------------------------------------------------------------------------#


import pandas as pd


df_Biometrika_columns = ["id_document", "author", "year", "title", 
                         "journal title", "volume", "issue", "page_init",
                         "page_last", "date", "doi", "uri_pdf", "abstract", 
                         "keywords", "bibliography", "article_type_1", 
                         "language", "texte_v1", "citation", 
                         "number of characters"] 

    
rows = []


#-----------------------------------------------------------------------------#
# Use for loops to extract blocks from a file (article) as string or numerical
# objects. 
#-----------------------------------------------------------------------------#


for article, article_text in zip(archive, archive_text):
    
    bibliography = []
      
    article_type_1 = article.get("article-type")
            
    for first_node in article:
        
        for ref_list in first_node.iter("ref-list"): 
            
            for reference in ref_list.findall("./ref/mixed-citation"): 
                
                reference = reference.text
                
                reference = reference.replace("\n"," ")
                
                bibliography.append(reference)
                        
        for journal_meta in first_node.iter("journal-meta"):
            
            for journal_title in journal_meta.findall("./journal-title-group/journal-title"):
                
                journal_title = journal_title.text
                
        for article_meta in first_node.iter("article-meta"):
            
            for volume in article_meta.findall("./volume"):
                
                volume = volume.text
            
            for issue in article_meta.findall("./issue"):
                
                issue = issue.text
            
            for doi in article_meta.findall("./article-id"):
                
                doi = doi.text
            
            for article_title in article_meta.findall("./title-group/article-title"):
                
                if article_title.text is None: 
                    
                    for subject in article_meta.findall("./article-categories/subj-group/subject"): 
                        
                        title = subject.text
                        
                        title = title.strip(" \n")
                        
                        title = title.replace("\n", "")
                                
                else:
                    
                    sub_title = article_title.text
                    
                    sub_title = sub_title.strip(" \n")
                            
                    sub_title = sub_title.replace("\n", "")
                    
                    for child in article_title:
                        
                        if child.tail is not None:
                            
                            sub_title = sub_title + child.text + child.tail
                            
                            sub_title = re.sub(' +', ' ', sub_title)
                            
                            sub_title = sub_title.strip(" \n")
                            
                            sub_title = sub_title.replace("\n", "")
                            
                    title = sub_title
                    
                title = title.strip(" \$")
                
                title = title.replace("$", "")
                    
            for pub_year in article_meta.findall("./pub-date/year"):
                
                year = pub_year.text
                
            for pub_day in article_meta.findall("./pub-date/day"):
                
                day = pub_day.text
                
            for pub_month in article_meta.findall("./pub-date/month"):
                
                month = pub_month.text
                
            date = month + "/" + day + "/" + year
            
            page_init = "No page_init"
            
            for p_init in article_meta.findall("./fpage"):
                
                if p_init.text != None:
                    
                    page_init = p_init.text
                
                else:
                    
                    page_init = "No page_init"
            
            page_last = "No page_last"
            
            for p_last in article_meta.findall("./lpage"):
                
                if p_last.text != None:
                    
                    page_last = p_last.text
                
                else:
                    
                    page_last = "No page_last"
                    
            for uri in article_meta.findall("./self-uri"):
                
                uri_pdf = uri.get('{http://www.w3.org/1999/xlink}href')
            
            abstract = ""
            
            for abstr in article_meta.findall("./abstract/p"):
                
                if abstr.text is not None:
                    
                    sub_abstract = abstr.text
                    
                    sub_abstract = sub_abstract.strip(" \n")
                            
                    sub_abstract = sub_abstract.replace("\n", "")
                    
                    for child in abstr:
                        
                        if child.text is not None and child.tail is not None:
                            
                            sub_abstract = sub_abstract + child.text + child.tail
                            
                            sub_abstract = re.sub(' +', ' ', sub_abstract)
                            
                            sub_abstract = sub_abstract.strip(" \n")
                            
                            sub_abstract = sub_abstract.replace("\n", "")
                            
                    abstract = sub_abstract
                    
                abstract = abstract.strip(" \$")
                
                abstract = abstract.replace("$", "")
                
            keywords = []
            
            for key in article_meta.findall("./kwd-group/kwd"):
                
                keyword = key.text
                
                keywords.append(keyword)
                
            for lang in article_meta.findall("./custom-meta-group/custom-meta/meta-value"):
                
                language = lang.text
            
            name_list = []
                    
            for name in article_meta.findall("./contrib-group/contrib/string-name/given-names"): 
                
                if name.text != None:
                    
                    name = name.text
                    
                    lowercase_name_1 = name[0] + re.sub(r"[\u00C0-\u017Fa-zA-Z]", 
                          
                                           lambda x :  x.group(0).lower()
                                
                                                       if x.group(0).isupper()
                                
                                                       else x.group(0),
                    
                                          name[1:])
                    
                    lowercase_name_2 = lowercase_name_1[0] + re.sub(r"(?<=.\s)\w", 
                          
                                           lambda x :  x.group(0).upper()
                                
                                                       if x.group(0).islower()
                                
                                                       else x.group(0),
                    
                                          lowercase_name_1[1:])
                    
                    lowercase_name_3 = lowercase_name_2[0] + re.sub(r"(?<=-)\w", 
                          
                                           lambda x :  x.group(0).upper()
                                
                                                       if x.group(0).islower()
                                
                                                       else x.group(0),
                    
                                          lowercase_name_2[1:])
                    
                    name_list.append(lowercase_name_3)
                
                else:
                    
                    name_list.append("No name")
                
            surname_list = []
            
            for surname in article_meta.findall("./contrib-group/contrib/string-name/surname"):
                
                if surname.text != None:
                    
                    surname = surname.text
                    
                    lowercase_surname_1 = surname[0] + re.sub(r"[\u00C0-\u017Fa-zA-Z]", 
                          
                                           lambda x :  x.group(0).lower()
                                
                                                       if x.group(0).isupper()
                                
                                                       else x.group(0),
                    
                                          surname[1:])
                    
                    lowercase_surname_2 = lowercase_surname_1[0] + re.sub(r"(?<=-)\w", 
                          
                                           lambda x :  x.group(0).upper()
                                
                                                       if x.group(0).islower()
                                
                                                       else x.group(0),
                    
                                          lowercase_surname_1[1:])
                    
                    surname_list.append(lowercase_surname_2)
                    
                else:
                    
                    surname_list.append("No surname")                
            
            author = " "
            
            author_name = []
                    
            for surname, name in zip(surname_list, name_list):
                
                    
                if surname == "No surname":
                    
                    author_name.append(name)
                    
                elif name == "No name":
                    
                    author_name.append(surname)
                
                else:
                    
                    author_name.append(surname + "," + " " + name)
                        
            if len(author_name) > 1: 
                
                author = "; ".join(author_name)    
                
            else:
                
                author = author.join(author_name) 
            
            if author == "": 
                
                for string_name in article_meta.findall("./contrib-group/contrib/string-name"): 
                    
                    if string_name.text != None: 
                        
                        author = string_name.text
                        
            author = author.strip(" \n")
    
    texte_v1 = "Init:"
    
    for text in article_text:
        
        texte_v1 = texte_v1 + " " + str(text.text)
        
    texte_v1 = texte_v1.split(' ', 1)[1]
    
    texte_v1 = texte_v1.replace("\n"," ")
    
    num_char = len(texte_v1)
    
    citation = author + " (" + year + ")" + ". " + str(title) + ", " + journal_title
    
    citation = citation + " " + volume + "(" + issue + "): " + page_init
    
    citation = citation + "-" + page_last + "."
    
    
#-----------------------------------------------------------------------------#
# Assign objects to the relevant columns. 
#-----------------------------------------------------------------------------#
    
    
    rows.append({"author": author, "year": year, 
                 "title": title, 
                 "journal title": journal_title, "volume": volume, 
                 "issue": issue, "page_init": page_init, 
                 "page_last": page_last, "date": date, "doi": doi, 
                 "uri_pdf": uri_pdf, "abstract": abstract, 
                 "keywords": keywords, "bibliography": bibliography, 
                 "article_type_1": article_type_1, "language": language, 
                 "texte_v1": texte_v1, "citation": citation, 
                 "number of characters": num_char}) 
   
   
#-----------------------------------------------------------------------------#
# Create df_Biometrika dataframe from the objects extracted above. 
#-----------------------------------------------------------------------------#                


df_Biometrika = pd.DataFrame(rows, columns = df_Biometrika_columns)

df_Biometrika["id_document"] = file_names

df_Biometrika = df_Biometrika.sort_values(by="year", ascending = True)


#-----------------------------------------------------------------------------#
# Load correction file (.xlsx) as a pandas dataframe. 
#-----------------------------------------------------------------------------#


df_corrections = pd.read_excel (___)


#-----------------------------------------------------------------------------#
# Clean the dataframe using information from the correction file.
#-----------------------------------------------------------------------------#


df_Biometrika_clean = df_Biometrika


for i in range(0, df_corrections.shape[0]):
    
    for j in range(0, df_Biometrika_clean.shape[0]):
        
        if df_Biometrika_clean ["id_document"][j] == df_corrections["id_document"][i]:
            
            df_Biometrika_clean ["author"][j] = df_corrections["author"][i]
            
            df_Biometrika_clean ["article_type_1"][j] = df_corrections["article_type_1"][i]
            
            df_Biometrika_clean ["language"][j] = df_corrections["language"][i]
            
        if df_Biometrika_clean["id_document"][j] == "10.2307_2331887":
            
            df_Biometrika_clean["page_init"][j] = "1"
            
            df_Biometrika_clean["page_last"][j] = "60"
    
    
#-----------------------------------------------------------------------------#
# Create a pandas dataframe for the translated texts (articles in other 
# languages than English).
#-----------------------------------------------------------------------------#


folder_translations = ___

file_translations = os.listdir(folder_translations)

archive_translations = []

translations_names = []

reg = re.compile(r'\-')


for translation in file_translations:

    translation_name = reg.split(translation)[2].replace(".txt", "")
    
    translations_names.append(translation_name)
    

df_Translations_columns = ["id_document", "texte_v1"]

rows_Translations = []

for translation in file_translations:
    
    with open(folder_translations + "\\" + translation, 'r') as file:
    
        texte_v1 = file.read().replace('\n', '')
        
        texte_v1 = re.sub('<.*?>', '', texte_v1)

    rows_Translations.append({"texte_v1": texte_v1})


df_Translations = pd.DataFrame(rows_Translations, columns = df_Translations_columns)

df_Translations["id_document"] = translations_names             


#-----------------------------------------------------------------------------#
# Load translations into the "clean" Biometrika dataframe. 
#-----------------------------------------------------------------------------#


for i in range(0, df_Translations.shape[0]):
    
    for j in range(0, df_Biometrika_clean.shape[0]):
        
        if df_Biometrika_NB["id_document"].iloc[j] == str(df_Translations_1["id_document"].iloc[i]):
            
            df_Biometrika_clean ["texte_v1"][j] = df_Translations["texte_v1"][i]


#-----------------------------------------------------------------------------#
# Clean the authors' names in the Biometrika dataframe. 
#-----------------------------------------------------------------------------#


df_author_corrections = pd.read_excel (___)


for i in range(0, df_author_corrections.shape[0]):
    
    for j in range(0, df_Biometrika_clean.shape[0]):
        
        if df_Biometrika_clean ["id_document"][j] == str(df_author_corrections["id_document"][i]):
            
            df_Biometrika_clean ["author"][j] = df_author_corrections["author"][i]

             
#-----------------------------------------------------------------------------#
# Convert the main dataframe and the clean dataframe to a csv files. 
#-----------------------------------------------------------------------------#


df_Biometrika.to_csv(___, index = False, header=True)

df_Biometrika_clean.to_csv(___, index = False, header=True)


#-----------------------------------------------------------------------------#
# Import html and xml files for Biometrika articles (2013-2020).
#-----------------------------------------------------------------------------#


import os

import re

from bs4 import BeautifulSoup

folder_Biometrika_new = ___

file_Biometrika_new = os.listdir(folder_Biometrika_new)

archive_text = []

file_names = []

reg = re.compile(r'\-')

html =[]


#-----------------------------------------------------------------------------#
# Pull data from HTML files using the "Beautiful soup" package
# See https://beautiful-soup-4.readthedocs.io/en/latest/
#-----------------------------------------------------------------------------#


for file in file_Biometrika_new:
    
    file_name = reg.split(file)[0].replace(".html", "")
    
    file_names.append(file_name)
    
    with open(folder_Biometrika_new + "\\" + file, encoding = 'utf8') as fp: 
        
        soup = BeautifulSoup(fp, features="lxml")
        
        archive_text.append(soup)
        
        html_raw = str(soup)
        
        html_clean = html_raw.replace('\n', '')
        
        html.append(html_clean)
        
        
folder_Biometrika_new_txt = ___

file_Biometrika_new_txt = os.listdir(folder_Biometrika_new_txt)

archive_text_txt = []

for file in file_Biometrika_new_txt:
    
    with open(folder_Biometrika_new_txt + "\\" + file, encoding='utf-16') as f:
        
        content = f.read()
        
        f.close()
 
        content = content.replace("\n", " ")
        
        content = content.replace("\t", " ")
    
        archive_text_txt.append(content)


#-----------------------------------------------------------------------------#
# Initialize the dataframe with columns "id_document", "author", "year", "title", 
#                         "journal title", "volume", "issue", "page_init",
#                         "page_last", "date", "doi", "uri_pdf", "abstract", 
#                         "keywords", "bibliography", "article_type_1", 
#                         "language", "texte_v1", "metadata_xml",  "ocr", 
#                         "html", "citation", 
#                         "number of characters", "nb_pages"
#-----------------------------------------------------------------------------#


import pandas as pd


df_Biometrika_new_columns = ["id_document", "author", "year", "title", 
                         "journal title", "volume", "issue", "page_init",
                         "page_last", "date", "doi", "uri_pdf", "abstract", 
                         "keywords", "bibliography", "article_type_1", 
                         "language", "texte_v1", "metadata_xml",  "ocr", 
                         "html", "citation", 
                         "number of characters", "nb_pages"] 

    
rows = []


#-----------------------------------------------------------------------------#
# Use for loops to extract data from a file (article) as string or numerical 
# objects. 
#-----------------------------------------------------------------------------#


for article, article_txt in zip(archive_text, archive_text_txt): 
    
    title = article.find("meta", {"name":"citation_title"})['content']
    
    title = title.replace('\n', '')
    
    author_name = article.find_all("meta", {"name":"citation_author"})
    
    authors = []
    
    if len(author_name) > 1: 
        
        for i in range(len(author_name)): 
            
            authors.append(author_name[i]['content'])
        
        author = "; ".join(authors)
        
    elif len(author_name) == 1: 
        
        author = author_name[0]['content']
        
    else:
        
        author = 'no_author'
        
    date = article.find("meta", {"name":"citation_publication_date"})['content']
    
    year = date[:4]
    
    journal_title = article.find("meta", {"name":"citation_journal_title"})['content']
    
    volume = article.find("meta", {"name":"citation_volume"})['content']
    
    issue = article.find("meta", {"name":"citation_issue"})['content']
    
    page_init = article.find("meta", {"name":"citation_firstpage"})['content']
    
    page_last = article.find("meta", {"name":"citation_lastpage"})['content']
    
    doi = article.find("meta", {"name":"citation_doi"})['content']
    
    uri_pdf = article.find("meta", {"name":"citation_pdf_url"})['content'] 
        
    if article.find("section", {"class":"abstract"}) is None:
        
        abstract = 'no abstract'
        
    else: 
        
        abstract = article.find("section", {"class":"abstract"}).text
        
        abstract = abstract.replace('\n', '')
        
        abstract = abstract.replace('\r', '')
        
        abstract = abstract.replace('\t', '')
    
    keys = article.find_all("script", {"type":"application/ld+json"})[0]
    
    if re.search('"keywords"(.*?),"inLanguage"', keys.string) is None:
        
        keywords = "no_keywords"
        
    else: 
        
        keywords = re.search('"keywords"(.*?),"inLanguage"', keys.string).group(1)[3 :-1]
        
        keywords = keywords.replace('\n', '')
        
        keywords = keywords.replace('\r', '')
        
        keywords = keywords.replace('\t', '')
        
    
    if article.find_all("meta", {"name":"citation_reference"}) is not None:
        
        words_elimination = ['citation_title=', 'citation_author=', 
                             'citation_journal_title=', 'citation_year=', 
                             ' citation_volume=', 'citation_pages=', 
                             'citation_publisher=']
        
        citations = article.find_all("meta", {"name":"citation_reference"})
    
        citations_list = []
        
        for i in range(len(citations)): 
            
            citations_list.append(citations[i]['content'][:-2])
        
        bibliography = ". ".join(citations_list)
        
        for word in  words_elimination: 
            
            bibliography = bibliography.replace(word, '')
            
        bibliography = bibliography.replace(';', ',')
        
        bibliography = bibliography.replace('\n', '')
        
        bibliography = bibliography.replace('\r', '')
        
        bibliography = bibliography.replace('\t', '')
            
    else: 
        
        bibliography = 'no_bibliography'
         
    
    if re.search('"@type":"(.*?)",', keys.string) is None:
        
        article_type_1 = 'no_article_type'
    
    else: 
        
        article_type_1 = re.search('"@type":"(.*?)",', keys.string).group(1)
    
    language = "eng"
    
    if len(article.find_all("h2", {"class": "section-title js-splitscreen-section-title"})) != 0:
        
        text = []
        
        for element in article.find_all("h2", 
                                        {"class": "section-title js-splitscreen-section-title"}):
            
            title_paragraph = element.text + '.'
            
            text.append(title_paragraph) 
        
        for element in article.find_all("p", {"class": "chapter-para"}): 
            
            text.append(element.text) 
             
            texte_v1 = " ".join(text)
            
            texte_v1 = texte_v1.replace('\n', '')
            
            texte_v1 = texte_v1.replace('\r', '')
            
            texte_v1 = texte_v1.replace('\t', '')
      
    elif re.search("INTRODUCTION (.*?) REFERENCES", article_txt) is not None: 
        
        texte_v1 = re.search("INTRODUCTION (.*?) REFERENCES", article_txt).group(1)
        
        texte_v1 = texte_v1.replace('\n', '')
        
        texte_v1 = texte_v1.replace('\r', '')
        
        texte_v1 = texte_v1.replace('\t', '')
        
    elif re.search("Some key words: (.*?) REFERENCES", article_txt) is not None: 
        
        texte_v1 = re.search("Some key words: (.*?) REFERENCES", article_txt).group(1)
        
        texte_v1 = texte_v1.replace('\n', '')
        
        texte_v1 = texte_v1.replace('\r', '')
        
        texte_v1 = texte_v1.replace('\t', '')
    
    else:
        
        texte_v1 = 'no_text' 
        
    num_char = len(texte_v1)
    
    citation = author + " (" + year + ")" + ". " + str(title) + ", " + journal_title
    
    citation = citation + " " + volume + "(" + issue + "): " + page_init
    
    citation = citation + "-" + page_last + "."
    
    try: 
        
        nb_pages = int(page_last) - int(page_init) + 1
            
    except ValueError: 
        
        nb_pages = "No nb_pages"
    

#-----------------------------------------------------------------------------#
# Assign objects to the relevant columns. 
#-----------------------------------------------------------------------------#

    
    rows.append({"author": author, "year": year, 
                 "title": title, 
                 "journal title": journal_title, "volume": volume, 
                 "issue": issue, "page_init": page_init, 
                 "page_last": page_last, "date": date, "doi": doi,
                 "uri_pdf": uri_pdf, "abstract": abstract, 
                 "keywords": keywords, "bibliography": bibliography, 
                 "article_type_1": article_type_1, "language": language, 
                 "texte_v1": texte_v1, "citation": citation, 
                 "number of characters": num_char, "nb_pages": nb_pages}) 
    

#-----------------------------------------------------------------------------#
# Create df_Biometrika_new dataframe from the objects extracted above. 
#-----------------------------------------------------------------------------#


df_Biometrika_new = pd.DataFrame(rows, columns = df_Biometrika_new_columns)

df_Biometrika_new["id_document"] = file_names

df_Biometrika_new["html"] = html

df_Biometrika_new = df_Biometrika_new.sort_values(by="year", ascending = True)

df_Biometrika_new.to_csv(___, index = False, header=True)


#-----------------------------------------------------------------------------#
# Load correction file (.xlsx) as a pandas dataframe. 
#-----------------------------------------------------------------------------#


df_corrections_new = pd.read_excel (r'C:\Users\nicol\OneDrive\Bureau\Biometrika\Textes\Corrections_Biometrika_new.xlsx')


#-----------------------------------------------------------------------------#
# Clean the dataframe using information from the correction file.
#-----------------------------------------------------------------------------#


df_Biometrika_new_clean = df_Biometrika_new


for i in range(0, df_corrections_new.shape[0]):
    
    for j in range(0, df_Biometrika_new_clean.shape[0]):
        
        if df_Biometrika_new_clean ["id_document"][j] == str(df_corrections_new["id_document"][i]):
            
            df_Biometrika_new_clean ["title"][j] = df_corrections_new["title"][i]
            
            df_Biometrika_new_clean ["article_type_1"][j] = df_corrections_new["article_type_1"][i]
            
        if df_Biometrika_new_clean ["article_type_1"][j] == "miscellanea":
            
            df_Biometrika_new_clean ["article_type_1"][j] = "misc"
            
            
df_author_corrections_new = pd.read_excel (r'C:\Users\nicol\OneDrive\Bureau\Biometrika\Textes\Biometrika_new_corrections_authors.xlsx')


for i in range(0, df_author_corrections_new.shape[0]):
    
    for j in range(0, df_Biometrika_new_clean.shape[0]):
        
        if df_Biometrika_new_clean ["id_document"][j] == str(df_author_corrections_new["id_document"][i]):
            
            df_Biometrika_new_clean ["author"][j] = df_author_corrections_new["author"][i]


#-----------------------------------------------------------------------------#
# Convert the clean dataframe to a csv files. 
#-----------------------------------------------------------------------------#            
           

df_Biometrika_new_clean.to_csv(___, index = False, header=True)


#-----------------------------------------------------------------------------#
# Merge the df_Biometrika_clean and the df_Biometrika_new_clean dataframe. 
#-----------------------------------------------------------------------------#                           


import pandas as pd

import data_frame_ultimate as df

import data_frame_new as df_new


frames = [df.df_Biometrika_clean, df_new.df_Biometrika_new_clean]

df_Biometrika_complete = pd.concat(frames, axis=0, join="outer", ignore_index=True,
    
                                   keys=None, levels=None, names=None, 
                                   
                                   verify_integrity=False, copy=True,)


#-----------------------------------------------------------------------------#
# Convert the complete dataframe to a csv file. 
#-----------------------------------------------------------------------------# 

f_Biometrika_complete.to_csv(___, index = False, header=True) 