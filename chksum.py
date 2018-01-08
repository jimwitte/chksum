#!/usr/bin/env python

import sys
from requests import HTTPError
from riotwatcher import RiotWatcher
import datetime
import calendar
from tabulate import tabulate
from operator import itemgetter
import csv
import argparse

# function to add months to a date
def add_months(sourcedate,months):
    if months < 6:
      months = 6
    elif months > 30:
        months = 30
    month = sourcedate.month - 1 + months
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)

# function to convert millisecond timestamp to local date
def timestamp_to_date(timestamp):
  timestampseconds = int(timestamp/1000) # convert to seconds
  timestampdate = datetime.datetime.fromtimestamp(timestampseconds) # convert to date object
  return timestampdate

# process command line argument
parser = argparse.ArgumentParser(description='check summoner names. API key is required. Specify either input file or name.')
parser.add_argument("-i","--input", help="input text file with names, one name per line.",metavar='PATH')
parser.add_argument("-o","--output",help="name of output csv file",metavar='PATH')
parser.add_argument("-r","--region",help="region (default na1)",default="na1")
parser.add_argument("-k","--key",help="file with API key (default apikey.txt)",default="apikey.txt",metavar='PATH')
parser.add_argument("-n","--name",help="check a single name")
args = parser.parse_args()

# read username and password from apikey file
try:
  f = open(args.key,"r")
except IOError:
  print("Error. Key file not found.")
  quit()
apikey = f.readline().strip()
f.close()

# create new api connection
watcher = RiotWatcher(apikey)

# specify region
my_region = args.region

# create empty lists
results = []
notfound = []
matchlist = []

# get names, either from file or from command line
if args.name:
  names=[args.name]
elif args.input:
  try:
    f = open(args.input,"r")
  except IOError:
    print("Error. Input file not found.")
    quit()
  with f as namelist:
    names = namelist.read().splitlines()
  f.close()
  names = filter(None, names) # remove empty lines
else:
  print("Must specify either --name NAME or --input PATH")
  quit()

# loop through the list of names
for name in names:

  # show progress while running
  sys.stdout.write("\rchecking %s...         " % name)
  sys.stdout.flush()

# try to get data from API
  try:
    me = watcher.summoner.by_name(my_region, name)
  except HTTPError as err:
    if err.response.status_code == 429:
      print('We should retry in {} seconds.'.format(e.headers['Retry-After']))
      print('this retry-after is handled by default by the RiotWatcher library')
      print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
      notfound.append([name])  # add to list of names not found
      continue  # continue to next item in loop
    elif err.response.status_code == 403:
      print("Authorization error. New API key required?")
      quit()
    else:
      raise  # if some other error, show error.

# format and convert last revision date
  revdate = timestamp_to_date(me['revisionDate'])
  revdatestr = revdate.strftime('%Y-%m-%d %H:%M:%S')
  expiredate = add_months(revdate,me['summonerLevel']) # calculate expire date
  expiredatestr = "%s %s" %(expiredate.strftime('%Y-%m-%d'),revdate.strftime('%H:%M:%S'))

# get recent matches
  try:
    matchlist = watcher.match.matchlist_by_account(my_region,me['accountId'])
  except HTTPError as err:
    if err.response.status_code == 429:
      print('We should retry in {} seconds.'.format(e.headers['Retry-After']))
      print('this retry-after is handled by default by the RiotWatcher library')
      print('future requests wait until the retry-after time passes')
    elif err.response.status_code == 404:
      matchlist = []
    else:
      raise  # if some other error, show error.
  
# format last match date
  if matchlist:
    recentmatch = matchlist['matches'][0] # assumes first match in list is most recent
    recentmatchdate = timestamp_to_date(recentmatch['timestamp'])
    recentmatchdatestr = recentmatchdate.strftime('%Y-%m-%d %H:%M:%S')
    recentmatchdateexpirestr = add_months(recentmatchdate,me['summonerLevel']).strftime('%Y-%m-%d')
    try:
      matchdetails = watcher.match.by_id(my_region,recentmatch['gameId'])
    except HTTPError as err:
      if err.response.status_code == 404:
        matchdetails = []
    if matchdetails:
      matchduration = int(matchdetails['gameDuration']/60)
    else:
      matchduration = 0
  else:
    recentmatchdatestr = 0
    recentmatchdateexpirestr = 0
    matchduration = 0

# append data to results (list of found names)
  results.append([
    me['name'],
    me['summonerLevel'],
    revdatestr,
    expiredatestr,
    recentmatchdatestr,
    matchduration,
    recentmatchdateexpirestr
  ])

# sort found names by date
sorted_results = sorted(results,key=itemgetter(6)) # sort by last column

# table headers
tableheaders = ['Name','Lvl','Revision Date','Revision Expire','Last Match Date','Last Match Min','Last Match Expire']

# print header
sys.stdout.write("\r                        ")
print("\n")  # print a blank line
now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M") # get current date and time
print("Date/Time: %s" % now)
print("Region: %s" % my_region)
print("API Key: %s" %apikey)
if args.input:
  print("input file: %s" % args.input)
if args.output:
  print("output file: %s" % args.output)
print("\n")

# print table of sorted found names
print tabulate(sorted_results, headers=tableheaders, tablefmt='orgtbl')
print("\n")

if args.name and matchlist:
  for match in matchlist['matches']:
    match.update((k, timestamp_to_date(match['timestamp']).strftime('%Y-%m-%d %H:%M:%S')) for k,v in match.iteritems() if k == "timestamp")
  print tabulate(matchlist['matches'], headers='keys', tablefmt='orgtbl')

# print list of names not found.
if not notfound:
  print("\n")
  print("All names found.\n")
else:
  print tabulate(notfound, headers=['Names not found'], tablefmt='orgtbl')
  print("\n")  # print another blank line at the end.

# create csv output file if needed
if args.output:
  with open(args.output, "wb") as f:
      writer = csv.writer(f)
      writer.writerows([tableheaders])
      writer.writerows(results)
      writer.writerows(notfound)
