import urllib2
import time
import re
import oauth2 as oauth
import requests
import string
import os
import codecs

from gensim import models, corpora
from bs4 import BeautifulSoup

def search(query, start = 0):
    """
    Query Yahoo's search engine via BOSS API.
    Returns 50 urls.  Max result is 1000th.
    -------------------------------
    query - string
    start - index of first query (results are 0 indexed)
    """

    def oauth_request(url, params, method="GET"):
        params['oauth_version'] = "1.0"
        params['oauth_nonce'] = oauth.generate_nonce()
        params['oauth_timestamp'] = int(time.time())

        consumer = oauth.Consumer(key=OAUTH_CONSUMER_KEY,
                                  secret=OAUTH_CONSUMER_SECRET)

        params['oauth_consumer_key'] = consumer.key
        req = oauth.Request(method=method, url=url, parameters=params)
        req.sign_request(oauth.SignatureMethod_HMAC_SHA1(), consumer, None)

        return req

    url = "http://yboss.yahooapis.com/ysearch/web"

    req = oauth_request(url, params={"q": query, "start": start})
    req['q'] = req['q'].encode('utf8')
    req_url = req.to_url().replace('+', '%20')
    result = urllib2.urlopen(req_url).read()
    urls   = re.findall(r'"url":"(.+?)"', result)
    edited = [url.replace('\\','') for url in urls]
    return edited

def search1000(query):
    results = []
    for i in range(20):
        results += search(query, i * 50)

    return results

#####################################################
# Some utility functions for extracting / tokenizing
#####################################################

def extract(url):
    """
    Pulls all text from url.
    In future, may be benefecial to do some cleaning
    """
    try:
        page = requests.get(url)
    except: return None 
    soup = BeautifulSoup(page.content)
    return soup.get_text()

def tokenize(text):
    """
    Seperates text into individual word 'tokens.'
    Currently, all 'tokens' are accepted; may want
    to do some more filtering in future.
    """
    with_punc = text.lower()
    for punc in string.punctuation: # rid of punctuation
        with_punc.replace(punc, ' ')
    for digit in string.digits:
        with_punc.replace(digit, ' ')
    without_punc = with_punc
    tokens = re.sub(r'(\s+)', ' ', without_punc).split(' ') # rid of double spaces
    return tokens

def gen_corpus(query, name = None):
    if not name: name = './%s/'%(query)

    if not os.path.exists(name):
        os.mkdir(name)
        if name[-1] != '/': name += '/'

    hits   = search1000(query)
#    store  = open(name + 'corp', 'w')
    store = codecs.open(name + 'corp', encoding='utf-8', mode='w')
    tokens = []

    for hit in hits:
        text = extract(hit)

        if not text: continue

        # Save a version of the text
        store.write( text.replace('\n', '') + '\n' )

        # Generate / save tokens
        tokens.append( tokenize(text) )

    # Close doc store
    store.close()

    # Create dictionary
    dic = corpora.Dictionary(tokens)
    dic.save(name + 'dic')

    # Do bag of words & tfidf
    bow_corp   = [dic.doc2bow(doc) for doc in tokens]
    tfidf_mdl  = models.TfidfModel(bow_corp)
    tfidf_corp = tfidf_mdl[bow_corp]

    corpora.MmCorpus.serialize(name + 'corp.bow', bow_corp)
    corpora.MmCorpus.serialize(name + 'corp.tfidf', tfidf_corp)
    tfidf_mdl.save(name + 'mdl.tfidf')

    return None

if __name__ == '__main__':
    gen_corpus('australia gold')
