import urllib2
import oauth2 as oauth
import time
import re

def search(query, start = 0):

 def oauth_request(url, params, method="GET"):
     # Removed trailing commas here - they make a difference.
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
 result = urllib2.urlopen(req_url)
 return [url.replace('\\','') for url in re.findall( r'"clickurl":"(.+?)"', result.read())]

if __name__ == '__main__':
    print search('Stephen Bates')
