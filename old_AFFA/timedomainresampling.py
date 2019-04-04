# Splited from one file pipeline 22th Mar 2019 

#import modules
from sigpyproc.Readers import readDat
from multiprocessing import Pool
from multiprocessing import Process
import glob
import os
#Doing actual TDR 
def tdr(name,a,nfilpath):
        TS=readDat(name) #read dat file
        nTS=TS*0 #copy TS array but with all element equla to zero
        n_samp=nTS.header.nsamples #get number of sample 
        t_samp=nTS.header.tsamp #get sampling time
        nTS=TS.resample(a) #doing resample at specific a 
        nTS.toDat(nfilpath+"/"+str(a)+"/"+TS.header.basename) #savefile 

#reading tim file and multithres processing 
def TDR2(nfilpath,a):
        os.chdir(nfilpath+"/timeseries") #change the directory
        L=glob.glob("Out_DM*.dat") #get all of the file with specific pattern 
        from multiprocessing import Pool
        pool = Pool(10) #define the number of cpu
        for f in L:
                if os.path.exists(nfilpath+"/"+str(a)) == False: #check if the folder is created, if not, create a new one 
                        os.system("mkdir -p "+nfilpath+"/"+str(a))
                p = Process(target=tdr, args=(f,a,nfilpath)) #
                p.start()
                p.join()

