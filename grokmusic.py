
# TODO: Read iTunes XML file

import os

import pyechonest.config as config
import pyechonest.song as song

config.CODEGEN_BINARY_OVERRIDE = os.path.abspath("echoprint-codegen/echoprint-codegen")

# Put your API key in a shell variable ECHO_NEST_API_KEY, or put it here
# config.ECHO_NEST_API_KEY='KEY HERE'

#def echoprint_bulk(files):

def echoprint_lookup(file):
    # Note that song.identify reads just the first 30 seconds of the file
    fp = song.util.codegen(file)
    if len(fp) and "code" in fp[0]:
        # The version parameter to song/identify indicates the use of echoprint
        result = song.identify(query_obj=fp, version="4.11")
        pprint.pprint(result)
#        print "Got result:", result
#        if len(result):
#            print "Artist: %s (%s)" % (result[0].artist_name, result[0].artist_id)
#            print "Song: %s (%s)" % (result[0].title, result[0].id)
#        else:
#            print "No match. This track may not be in the database yet."
#    else:
#        print "Couldn't decode", file


# Identify the machine

# Identify the hash of each file
