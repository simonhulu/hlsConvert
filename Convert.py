#coding=utf-8  
'''
Created on 2013-7-15

@author: zhangshijie
'''
from OpenSSL import rand
import binascii
import subprocess
import re
import os
class Convert(object):
    default_m3u8FileSuffix = "v.m3u8"
    default_segment_duration = 10
    duration = 0 
    hexKey  = 0  
    duration_in_file = 0 ;
    '''
    classdocs
    '''
    def gneratem3u8(self,source,descpath):
        keyFilePath = descpath+"/video.key"
        self.generateKey(keyFilePath); 
        self.duration = self.getVideoDuration(source)
        self.convert2Mts(source, descpath, self.default_segment_duration)
        self.encryMtsIndex(self.hexKey, descpath, descpath+"/"+self.default_m3u8FileSuffix)
    def convert2Mts(self,source,descFilePath,segmentDuration):
        mtscommand = "ffmpeg -y -i "+source+" -map 0 -c copy -vbsf h264_mp4toannexb  -f hls  -hls_time "+str(segmentDuration)+" -hls_list_size 999 "+descFilePath+"/"+self.default_m3u8FileSuffix;
        conver2ts = subprocess.Popen(mtscommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True);
        conver2ts.communicate()
        if(conver2ts.returncode!=0):
            #convert to mp4 the convert to ts
            tsFile = source+".ts"
            mp4command = "ffmpeg -y -i "+source+" -c copy -bsf:v  h264_mp4toannexb "+ tsFile+" 1>>/dev/null 2>&1"
            mp4Pop = subprocess.Popen(mp4command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True);
            mp4Pop.communicate() 
            if(mp4Pop.returncode == 0):
                #convert ts success then to convert ts
                mtscommand = "ffmpeg -y -i "+tsFile+" -map 0 -c copy -vbsf h264_mp4toannexb  -f hls  -hls_time "+str(segmentDuration)+" -hls_list_size 999 "+descFilePath+"/"+self.default_m3u8FileSuffix;                
                conver2ts = subprocess.Popen(mtscommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True);
                conver2ts.communicate()
                os.remove(tsFile)
                if(conver2ts.returncode!=0):
                    raise Exception,mtscommand+" convert fail"
            else:
                raise Exception,mp4command+" convert fail"
        #没有m3u8则转换失败
        try:
            with open(descFilePath+"/"+self.default_m3u8FileSuffix):pass
        except IOError:
            raise Exception,"v.m3u8 no exist convert fail"
        
    def encryMtsIndex(self,encrykey,descFilePath,m3u8Path):
        #创建一个临时m3u8文件
        try:
            tempM3u8File = open(descFilePath+"/temp.m3u8",'w')
        except:
            raise "create temp m3u8 file fail"
        #需要写进temp m3u8的
        linestr = '';
        num = 0 ;
        m3u8FilePath = descFilePath+"/"+self.default_m3u8FileSuffix
        count = 0 ;
        #先计算有多少个文件 得到self.duration_in_file
        m3u8File = open(m3u8FilePath)
        time_last = 0 ;
        time = 0 ;
        for line in m3u8File:
                pattern = re.compile(r'#EXTINF:([\w.]+),')   
                match = pattern.search(line)
                if match:
                    count+=1
                    numberpattern =  re.compile(r'([\d.]+)')
                    numbermatch =   numberpattern.search(line);
                    if numbermatch:
                        time_str  = numbermatch.group(0)
                        time = int(time_str);
                        self.duration_in_file+=time
        
        time_distance = self.duration - self.duration_in_file
        if time_distance>=1:
            #补上 得到正确的最后时间
            time_last = time+time_distance; 
        m3u8File.seek(0)            
        for line in  m3u8File:
            #加密
            tspattern = re.compile(r'.ts')
            tsmatch = tspattern.search(line)
            if tsmatch:
                tsname =  line.strip("\n")
                tapath = descFilePath+tsname
                temptspath = tapath+"t"
                encrycommand = "openssl aes-128-cbc -e -in "+tapath+"  -out "+temptspath+"  -p  -nosalt -iv 0  -K "+str(self.hexKey)
                encry = subprocess.Popen(encrycommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True);
                encry.communicate()
                encry.stderr.close();
                encry.stdout.close();
                if encry.returncode != 0:
                    encry.kill()
                    raise Exception,"encrypt "+tapath+" fail"
                else:
                    encry.kill()
                    try:
                        os.remove(tapath)
                    except OSError,e:
                        print e
                        raise Exception,"delete "+tapath+" fail"
                    #重命名
                    try:
                        os.rename(temptspath, tapath)
                    except OSError,e:
                        raise Exception,"rename "+tapath+" fail"
            pattern = re.compile(r'#EXTINF:([\w.]+),')   
            match = pattern.search(line)
            if match:
                num+=1;
                #最后一个补上 
                if num == count:
                #如果是最后一个了 检查duration_in_file和原始duration的差距
                    #补上
                    line = "#EXTINF:"+str(time_last)+",\n";                              
            #修正碎片最长时间
            targetDurationPattern = re.compile(r'#EXT-X-TARGETDURATION:')
            targetMatch = targetDurationPattern.search(line)
            if targetMatch:
                #得到时间
                maxDurationPattern = re.compile(r'([\d.]+)')
                maxMatch = maxDurationPattern.search(line);
                if maxMatch:
                    maxtime = int(maxMatch.group(0));
                    if maxtime < time_last:
                        line = "#EXT-X-TARGETDURATION:"+str(time_last)+"\n"
            linestr = line ;
            if line == "#EXTM3U\n":
                linestr+="#EXT-X-KEY:METHOD=AES-128,URI=\"video.key\"\n"
                            
            tempM3u8File.write(linestr) 
        m3u8File.close()            
            #删除tempM3u8File
        try:
            os.remove(m3u8FilePath);
        except OSError,e:
            raise e
        tempM3u8File.close()
        try:
            os.rename(descFilePath+"/temp.m3u8",m3u8FilePath)
        except OSError,e:
            raise Exception,"rename "+descFilePath+"/temp.m3u8"+" fail"
                                                
    def generateKey(self,keyFilepath):
        b1 = rand.bytes(16)
        self.hexKey = binascii.hexlify(b1)
        try:
            keyFile = open(keyFilepath,"wb");
        except:
            print "can't open "+keyFilepath;
            raise
        keyFile.write(b1)
        keyFile.close();
    def getduration(self,source):
        global duration

    def searchForDuration (self,ffmpeg_output):
        pattern = re.compile(r'Duration: ([\w.-]+):([\w.-]+):([\w.-]+),')   
        match = pattern.search(ffmpeg_output)   
    
        if match:
            hours = match.group(1)
            minutes = match.group(2)
            seconds = match.group(3)
        else:
            hours = minutes = seconds = 0
        seconds_m = seconds.split('.')[0];
        # return a dictionary containing our duration values
        return int(hours)*3600+int(minutes)*60+int(seconds_m)

    # -----------------------------------------------------------
    # Get the dimensions from the specified file using ffmpeg
    # -----------------------------------------------------------
    def getFFMPEGInfo (self,src_file):
    
        p = subprocess.Popen(['ffmpeg', '-i', src_file],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        stdout, stderr = p.communicate()
        return stderr

    # -----------------------------------------------------------
    # Get the duration by pulling out the FFMPEG info and then
    # searching for the line that contains our duration values
    # -----------------------------------------------------------
    def getVideoDuration (self,src_file):
    
        ffmpeg_output = self.getFFMPEGInfo (src_file)
        return self.searchForDuration (ffmpeg_output)

    def __init__(self,source,descpath):
        '''
        Constructor
        '''
        try:
            with open(source) as f:pass
        except IOError,e:
            raise Exception,"source not exist"
        self.gneratem3u8(source,descpath);
        