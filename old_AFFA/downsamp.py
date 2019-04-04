# Split forom one file pipeline in 22th Mar 2019 

#import FilReader from sigproc
from sigpyproc.Readers import FilReader
#correct header script
from correct_header import Headercorrector
import os

def downsamp(fil,dfil,ndf):
        myFil = FilReader(fil) #import filterbank file 
       # myFil.header.telescope_id=8 # 
        if not os.path.exists(dfil):
                #myFil=Headercorrector(myFil)#Uncoment if you need to correct for header 
                myFil.downsample(tfactor=ndf,filename=dfil) #Downsample witt specific factor and save file 
        return myFil.header.source_name,myFil.header.tstart,myFil.header.ibeam #Return source name, start time, and beam 

