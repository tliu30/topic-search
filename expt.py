# import BOSS, requests
# from gensim import corpora, models

### First, use BOSS to generate queries ###

from requests_oauthlib import OAuth1Session

request_token_url = 'https://api.login.yahoo.com/oauth/v2/get_request_token'

oauth = OAuth1Session(client_key, client_secret = client_secret)
fetch_response = oauth.fetch_request_token(request_token_url)
resource_owner_key = fetch_response.get('oauth_token')
resource_owner_secret = fetch_response.get('oauth_token_secret')


### Second, for each hit, do this bigggg loop
### where the pages are pulled from the web
### and their contents are extracted from HTML
###
### (maybe also run a spellcheck)

import requests
from bs4 import BeautifulSoup
def extract(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content)
    return soup.get_text()
    ### Maybe do some cleaning?

docs = [extract(hit) for hit in results]

### Third, tokenize each doc

import re, string
def tokenize(text, stop_list):
    a = text.lower().translate(string.maketrans("",""), string.punctuation + string.digits)
    b = re.replace(r'(\s+)', ' ', a)
    c = b.split(' ')
    ### This might be too simple (simply deletes punctuation, then elims
    ### double spaces)

    ### Maybe eliminate some words here?
    ### It seems like code blocks get grabbed sometimes, so elim those
    ### To keep or not to keep numbers?
    return c

stop_list = []
tokenized = [tokenize(doc, stop_list) for doc in docs]

### Create bag-of-words corpus
dic = corpora.Dictionary(tokenized)
corpus = [dic.doc2bow(text) for text in tokenized]

##### Alternative that saves space
docs = [clean(extract(hit)) for hit in results]
open('mycorpus.txt', 'w').write('\n'.join(docs))

dic = corpora.Dictionary(docs)

class MyCorpus(object):
    def __iter__(self):
        for line in open('mycorpus.txt'):
            yield dic.doc2bow(line)

##### Similarly
# collect statistics about all tokens
dictionary = corpora.Dictionary(line.lower().split() for line in open('mycorpus.txt'))
# remove stop words and words that appear only once
stop_ids = [dictionary.token2id[stopword] for stopword in stoplist
            if stopword in dictionary.token2id]
once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
dictionary.filter_tokens(stop_ids + once_ids) # remove stop words and words that appear only once
dictionary.compactify() # remove gaps in id sequence after words that were removed
print(dictionary)

#### in any case, once corpus constructed as bow, can serialize corpus:
corpora.MmCorpus.serialize(corpus)
corpus = corpora.MmCorpus('/tmp/corpus.mm')

### Then, convert bow to tfidf
tfidf = models.TfidfModel(corpus) # object converting bow to tfidf
tfidf.save('./tmp/model.tfidf')
tfidf = models.TfidfModel.load('./tmp/mode.tfidf')
corpora.MmCorpus.serialize(tfidf[corpus])
tfidf = corpora.MmCorpus('/tmp/tfidf.mm')

### Topic models
model = lsimodel.LsiModel(tfidf_corpus, id2word=dictionary, num_topics)
model = rpmodel.Rpmodel(tfidf_corpus, num_topics = 500)
model = ldamodel.LdaModel(bow_corpus, id2word = dictionary, num_topics)
model = hdpmodel.HdpModel(bow_corpus, id2word = dictionary)

model.print_topics
