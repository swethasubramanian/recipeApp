import pandas as pd
import nltk, pickle, re, itertools
from collections import defaultdict

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

import nltk
from gensim import corpora, models, similarities

from sqlCalls import *

def lemmatizePhrase(phrase):
    """ 
    Lemmatize each word in a pharse
    """
    words = phrase.lower().split()
    return ' '.join(str(WordNetLemmatizer().lemmatize(word.encode('utf-8'))) for word in words)


def doNLPStuff(selDfx, keywords):
    keywordList = lemmatizePhrase(keywords)
    tDf = preprocess()
    dictionary = corpora.Dictionary.load('/tmp/descri.dict')
    #corpus_tfidf = corpora.MmCorpus('/tmp/corpus_tfidf.mm')
    index = similarities.MatrixSimilarity.load('/tmp/tfidf_lsi_similarities.index')
    lsi = models.LsiModel.load('/tmp/model.lsi')
    
    b=index[lsi[dictionary.doc2bow(keywordList.split())]]
    tDf['LSI_sim'] = b
    selDfx2 = pd.merge(selDfx, tDf[['id', 'LSI_sim']], on=['id'], how='inner')
    selDfx3 = selDfx2[selDfx2['LSI_sim']>0.1]
    return selDfx3.reset_index()

def removeShittyUnicodes(tDf):
    tDf['description'] = tDf['description_one']
    tDf['description'] = tDf['description'].str.replace('\xc2\x97', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\x97', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb3', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xa8', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xa9', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\x99', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb1', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\x89', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\x94', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\x94', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\x93', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\x92', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\xa6', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xaa', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\x9c', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\x93', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\x9d', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\xa2', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xa1', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xa2', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb9', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\xb7', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\xb4', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb4', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xa4', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xae', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\xa8', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb3', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xa0', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\xb0', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xaf', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xad', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\x96', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb8', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xa7', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\xa7', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\x95', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xbb', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xab', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb6', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb1', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x84\xa2', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xbc', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\xbf', ' ')
    tDf['description'] = tDf['description'].str.replace('\xe2\x80\x91', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\x81', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\x85', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc2\xa9', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb6', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xba', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xaa', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xb2', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\x87', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\xbe', ' ')
    tDf['description'] = tDf['description'].str.replace('\xc3\x89', 'e')
    tDf['description'] = tDf['description'].str.replace('\x89', ' ')
    tDf['description'] = tDf['description'].apply(lambda x: unicode(x, errors = 'ignore'))


    tokenizer = RegexpTokenizer(r'[a-z]\w+')
    tDf['description'] = tDf['description'].str.lower()
    tDf['tokens'] = tDf['description'].apply(lambda x:tokenizer.tokenize(x))

    ## Now remove stop words
    stop_words = set(stopwords.words('english'))
    tDf['tokens'] = tDf['tokens'].apply(lambda x: [word.lower() for word in x if not word.lower() in stop_words])

    ## Lemma or stem? Let me lemma for the sake of doing it properly
    ## lemma differentiates between make and making, it is irrelavant!
    ps = PorterStemmer()
    tDf['tokens'] = tDf['tokens'].apply(lambda x: [ps.stem(str(word)) for word in x])
    return tDf



def preprocess():
    tDf = getRecipeDescriptionAndTags();
    tDf['tags'] = tDf.tags.str.rsplit(",")
    tempTags = list(itertools.chain.from_iterable(list(tDf.tags)))
    tags = list(set(tempTags))
    return tDf


