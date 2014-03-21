'''
Created on 2013-7-15

@author: zhangshijie
'''

#coding=utf-8 
import logging 
import os
from optparse import OptionParser
#!/usr/bin/env python
from Convert import Convert
def convert(source,descFilePath,err):
    try:  
            convert = Convert("C:\\wamp\\www\\1207DQGZYWMFJZHQ102010.mp4","C:\\wamp\\www\\")
    except Exception, e:
        err = e
        return -1     
    return 0
if __name__ == '__main__':
    logfile = "/var/log/hlsconvert.log"
    if os.name == 'nt':
        logfile = "C:/hlsconvert.log"
    else:
        logfile = "/var/log/hlsconvert.log"               
    logging.basicConfig(filename = logfile,level = logging.DEBUG)    
    parser = OptionParser()
    parser.add_option("-i",type="string",dest="input")
    parser.add_option("-o",type="string",dest="output")
    (options,args) = parser.parse_args()
    source = options.input
    desc = options.output
    if source == None:
        logging.debug("no input source")
        exit(1) 

    if not desc:
        logging.debug("no input destination")
        exit(1)        
        
    if  not os.path.isdir(desc):
        logging.debug("destination no exist")
        exit(1)
    try:  
            convert = Convert(source,desc)
    except Exception, e:
        logging.debug(e)
        raise exit(1)   