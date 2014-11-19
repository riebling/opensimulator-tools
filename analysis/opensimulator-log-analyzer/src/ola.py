#!/usr/bin/python

import datetime
import re
import sys 

tsFormat = "%Y-%m-%d %H:%M:%S"

# Need to exclude milliseconds since this will only appear if explicitly configured in OpenSim.exe.config, etc.
tsRe = re.compile("^([\d-]+ [\d:]+)")
loginRe = re.compile("\[LLOGIN SERVICE]: Login request for (\w+) (\S+) at ")
# 2014-01-16 00:28:54,961 INFO  - OpenSim.Services.LLLoginService.LLLoginService [LLOGIN SERVICE]: Login request for Joe Danger at last using viewer Singularity 1.8.2.4929, channel Singularity, IP 192.168.1.2, Mac f6504c2415f0282a3e4bd2cbef1ddf08, Id0 cf7b76bf4f26fd0700c483692312f14b
diagProcessMemoryRe = re.compile("Process memory.*:")

def getFormattedTs(ts):
    return ts.strftime("%Y-%m-%d %H:%M:%S")

"""
See if can match login information to the given line.
If so, return the name.
If not, return None.
"""
def matchLogin(logline, ts):
    match = loginRe.search(logline)
  
    if match != None:
        # print "Found match for %s" % (logline)
        firstName = match.group(1)
        lastName = match.group(2)
        #print "%s Login request %s %s" % (getFormattedTs(ts), firstName, lastName)
        return "%s %s" % (firstName, lastName)
    else:
        return None;

def matchDiag(logline, ts):
    match = diagProcessMemoryRe.search(logline)

    if match != None:
        print "%s %s" % (getFormattedTs(ts), logline),
        
"""Return timestamp matching a logline.  If there was no match, then None is returned"""
def matchTs(logline):
    match = tsRe.search(logline)

    # We'll just discard ValueError parse failures
    try:
        if match != None:
            ts = datetime.datetime.strptime(match.group(1), tsFormat)
      
            # If timestamp somehow has a year before 1900, put in 1900 to signal the problem so that we don't fail later on with strftime
            if ts.year < 1900:
                ts.year = 1900

            return ts
    except ValueError:
        pass

    return None

############
### MAIN ###
############

# Usage
if len(sys.argv) == 1:
    print "Usage: %s <path>+" % sys.argv[0]
    sys.exit(-1)
  
filenames = sys.argv[1:]

loginsByUser = {}

for filename in filenames:
    print "Analyzing %s" % (filename)
    
    loglines = file(filename).readlines();

    loglinesIter = iter(loglines)

    # We must have some timestamp here in case we meet a file which manages to match an RE but with no stamp
    # But must be >= 1900 to stop issues with strftime()
    lastTs = datetime.datetime(1900, 1, 1)

    try:
        while True:
            logline = loglinesIter.next()
      
            ts = matchTs(logline)
            if ts != None:
                lastTs = ts

            loginName = matchLogin(logline, lastTs)
            if loginName != None:
                if loginName in loginsByUser:
                    loginsByUser[loginName] += 1
                else:
                    loginsByUser[loginName] = 1
                                 
            matchDiag(logline, lastTs)
            
    except StopIteration:
        pass

print "Summary"
print "Login information"

for loginName, count in loginsByUser.iteritems():
    print "%s: %s" % (loginName, count)
    
print "Total unique user logins recorded: %s" % (len(loginsByUser))
print "Fin"