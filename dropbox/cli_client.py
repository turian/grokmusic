#!/usr/bin/env python

import sys
import simplejson
import pprint
import os.path

import requests

from dropbox import client, rest, session

import pyechonest.config as config
import pyechonest.song as song
import pyechonest.track as track

from locals import *
config.ECHO_NEST_API_KEY=ECHO_NEST_API_KEY

class Dropbox:
    TOKEN_FILE = "token_store.txt"

    def __init__(self, app_key, app_secret):
        self.app_key = app_key
        self.app_secret = app_secret
        self.current_path = ''
        self.prompt = "Dropbox> "

        self.api_client = None
        self.login()

    def login(self):
        serialized_token = open(self.TOKEN_FILE).read()
        if serialized_token.startswith('oauth1:'):
            access_key, access_secret = serialized_token[len('oauth1:'):].split(':', 1)
            sess = session.DropboxSession(self.app_key, self.app_secret)
            sess.set_token(access_key, access_secret)
            self.api_client = client.DropboxClient(sess)
            print "[loaded OAuth 1 access token]"
        elif serialized_token.startswith('oauth2:'):
            access_token = serialized_token[len('oauth2:'):]
            self.api_client = client.DropboxClient(access_token)
            print "[loaded OAuth 2 access token]"
        else:
            raise("Malformed access token in %r." % (self.TOKEN_FILE,))

    def all_files(self):
        return self.all_files_recurse("/Music")
#        return self.all_files_recurse("/Music/best")
#        return self.all_files_recurse("/")

    def all_files_recurse(self, path):
        print "all_files_recurse(%s)..." % path
        metadata = self.api_client.metadata(path)

        # TODO: Save hash for directory

        dirs = []
        files = []
        for c in metadata["contents"]:
            if c["is_dir"]:
                files += self.all_files_recurse(c["path"])
            else:
                files.append(c)

        print "...all_files_recurse(%s): %d" % (path, len(files))
        return files

"""
mkdir -p
Code from: http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python/600612#600612
"""
import os, errno
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

DEFAULT = "json"
def main():
    if DROPBOX_APP_KEY == '' or DROPBOX_APP_SECRET == '':
        exit("You need to set your DROPBOX_APP_KEY and DROPBOX_APP_SECRET!")
    dbclient = Dropbox(DROPBOX_APP_KEY, DROPBOX_APP_SECRET)
    all_files = dbclient.all_files()
    import random
    random.shuffle(all_files)
    for f in all_files:
        fnew = DEFAULT + f["path"] + ".json"
        if os.path.exists(fnew): continue       # Skip things we've analyzed

        try:
            print >> sys.stderr, "%s" % f["path"]
            fmedia = dbclient.api_client.media(f["path"])
            t = track.track_from_url(fmedia["url"])
    #        print t.__dict__

            r = requests.get(t.analysis_url)
            if r.status_code == 200 and r.headers['content-type'] == "application/json":
                d = os.path.split(fnew)
                mkdir_p(d[0])
                open(fnew, "wt").write(r.text)
    #            dbclient.api_client.put_file(fnew, r.text)
                print >> sys.stderr, "... %s" % fnew
    #            print f["path"] + ".json"
    #            print r.json()
            else:
                print >> sys.stderr, "Error on %s, %s, %s" % (f["path"], r.status_code, r.headers['content-type'])
    #        break
        except Exception, e:
            print >> sys.stderr, type(e), e, f["path"]


if __name__ == '__main__':
    main()
