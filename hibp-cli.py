'''
Pulls pastes and domains from a list of emails/usernames or single search term
Uses the Adobe password dump (not included) and searches haveibeenpwned.com
from results with the same base 64 password as the input

https://github.com/bradvo
'''
import os
import re
import sys
import json
import time
import argparse
import requests
import subprocess

aparser = argparse.ArgumentParser()
aparser.add_argument('-s', '--string', nargs='+', required=False, action='store',
                    dest="search_str", help="hibp.py -s example@email.com")
aparser.add_argument('-f', '--file', nargs='+', required=False, action='store',
                    dest="file", help="hibp.py -f /path/to/file")
aparser.add_argument('-a', '--adobe', action='store_true',
                    help="hibp.py -a (-s example@email.com or -f /path/to/file)")
aparser.add_argument('-d', '--hints', action='store_true',
                    help="hibp.py -a -d (-s example@email.com or -f /path/to/file)")
args = aparser.parse_args()

# Change adobedump to path of your cred file
adobedump = 'C:/path/to/cred/file'
breachurl = 'https://haveibeenpwned.com/api/v2/breachedAccount/'
pasteurl = 'https://haveibeenpwned.com/api/v2/pasteaccount/'

# used grep since python's re module would use too much resources compared to grep.
# might not be the most efficient but gets the job done.
# if any one knows a better way please let me know :)
def grep_file(search):
    fetch = []
    # cygwin paramters, will take a few minutes to parse
    try:
        proc = subprocess.Popen(('grep "%s" %s' % (search, adobedump)),
                                  stdout = subprocess.PIPE)
        # speed up grep with linux paramters
        #proc = subprocess.Popen(('LC_ALL=C fgrep "%s" %s' % (search, adobedump)), stdout = subprocess.PIPE)
        output = proc.communicate()[0]
        if len(output) >= 1:
            for line in output.splitlines():
                fetch.append(line)
            return fetch
        else:
            return None
    except KeyboardInterrupt:
        sys.exit()


# open file and return list
def open_file():
    for i in args.file:
        with open(i, 'r') as efile:
            lines = efile.read().splitlines()
    return lines


# get pass64 from email
def get_pass64(email):
    for e in email:
        e = e.split('-|-')
        if e[3] != '':
            return e[3]
        else:
            return None


# build dictionary of results based on password from email search string
def build_dict(pass64):
    matchdict = {}
    for match in grep_file(pass64):
        match = match.split('-|-')
        del match[0:2]
        match[2] = match[2][:-3]
        matchdict[match[0]] = (match[1], match[2])
    return matchdict


# Get json and parse
# TODO add retry if no 200 on first connect
def get_breach_domain(email, s):
    url = breachurl + email
    time.sleep(1)
    r = s.get(url, verify=True)
    if r.status_code == 200:
        for eljson in r.json():
            # if -a is used, since searching the adobe dump
            if args.adobe:
                if eljson['Domain'] != 'adobe.com':
                    print email + ':' + eljson['Domain']
            else:
                print email + ':' + eljson['Domain']


def get_breach_paste(email, s):
    url = pasteurl + email
    time.sleep(1)
    r = s.get(url, verify=True)
    if r.status_code == 200:
        for eljson in r.json():
            print email + ':' + eljson['Source'].lower() + '.com/' + eljson['Id']


def hibp_search_results(emails):
    sesh = requests.Session()
    #TODO grab hints
    if args.hints:
        for email in emails:
            '''
            if dict[email][1]:
                print email + ':' + dict[email][1]
            '''
            get_breach_domain(email, sesh)
            get_breach_paste(email, sesh)   
    else:
        for email in emails:
            get_breach_domain(email, sesh)
            get_breach_paste(email, sesh)
    sesh.close()


def hibpsearch():
    if args.search_str:
        hsearch = hibp_search_results(args.search_str)
    elif args.file:
        hsearch = hibp_search_results(open_file())
    else:
        print 'Could not search HIBP. Need to add search string (-s) or file (-f)'


def adobesearch():
    if args.search_str:
        for i in args.search_str:
            print i
            print '-' * 25
            grepsearch = grep_file(i)
            if grepsearch is not None:
                passwd = get_pass64(grepsearch)
                if passwd is not None:
                    hibp_search_results(build_dict(passwd))
                else:
                    print 'Could not find password\n\n'
            else:
                print "Could not find email\n\n"
    elif args.file:
        for i in open_file():
            print i
            print '-' * 25
            grepsearch = grep_file(i)
            if grepsearch is not None:
                passwd = get_pass64(grepsearch)
                if passwd is not None:
                    hibp_search_results(build_dict(passwd))
                else:
                    print 'Could not find password\n\n'
            else:
                print 'Could not find email\n\n'
    else:
        print 'Could not search adobe. Need to add search string (-s) or file (-f)'


def main():
    if args.adobe:
        adobesearch()
    elif args.search_str or args.file:
        hibpsearch()
    else:
        print "hibp.py -h"


if __name__ == "__main__":
    main()
