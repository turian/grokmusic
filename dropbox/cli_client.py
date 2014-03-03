#!/usr/bin/env python

import sys
import simplejson
import pprint

from dropbox import client, rest, session

from locals import DROPBOX_APP_KEY, DROPBOX_APP_SECRET

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
        self.all_files_recurse("/")

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


def main():
    if DROPBOX_APP_KEY == '' or DROPBOX_APP_SECRET == '':
        exit("You need to set your DROPBOX_APP_KEY and DROPBOX_APP_SECRET!")
    dbclient = Dropbox(DROPBOX_APP_KEY, DROPBOX_APP_SECRET)
    dbclient.all_files()

if __name__ == '__main__':
    main()
