#1.0 create pipeline for 1 beam 
#1.1fix bug from .dat-->.inf
#1.1.1 fck I forgot to import numpyi
#beam test:test full pipe with beam 6
#Huge upgrade to get any filfile copy that to scarch process and copy back using yaml 17/03/2018
#Acceleration tree search is working 
#Include header corrector for Eff 24/01/2019
#Splited the pipeline into a fews modules 
#Update help interface

import matplotlib
matplotlib.use('Agg')
import os 
import riptide
import datetime
import glob
import sys
import numpy
from riptide.pipelines import Candidate
import matplotlib.pyplot as plt
import yaml
from sigpyproc.Readers import FilReader
import subprocess
from sigpyproc.Readers import readDat
import time
from correct_header import Headercorrector
from multiprocessing import Pool
from multiprocessing import Process

#local module
from dedisprse import dedisprse
from downsamp import downsamp
from timedomainresampling import TDR2
from sifandfold import ripsiftest,sif,best,ripfold2 
 
global nfilpath

def remove(pattern):
        for f in glob.glob(pattern):
                os.remove(f)

def zero_rfi(nfilpath):
	TS=riptide.TimeSeries.from_presto_inf(nfilpath+"/timeseries/Out_DM0.00")
        re=riptide.ffa_search(TS,period_min=0.50,period_max=321)
        p=riptide.peak_detection.find_peaks(re[2])
        blist=[]
        for i in range(0,len(p)-1):
        	blist.append([1.0/p[i].period,1,1])                 
		numpy.savetxt(nfilpath+"/blist",numpy.asarray(blist))

def fold(clist,filhome,pshome):
    for i in ranige(0,len(clist)-1):
    	os.system("prepfold -ncpus 24 -coarse -nosearch -n 128 -nsub 256 -noxwin -p "+str(clist[i][0])+" -dm "+str(clist[i][2])+" -o "+pshome+"/P_i"+str(clist[i][0])+"DM_i"+str(clist[i][1])+" "+filhome)

def pipe(nfilpath,setting,manage,fil,confighome,beam,ver,step,al):
        if os.path.exists(nfilpath+"/timeseries/Out_DM0.00.inf") == False :
                dedisprse(fil,nfilpath,manage)
        elif os.path.exists(nfilpath+"/timeseries/Out_DM0.00.inf") == False :
                print("already dedisprsed")
        os.chdir(nfilpath+"/timeseries")
        os.system("python /home/psr/software/riptide/pipelines/pipeline.py "+confighome+"/HTRUNll3_manager.yaml  \"Out*.inf\" "+nfilpath+"/prepfold" )
        for i in al:
                TDR2(nfilpath,i)
                os.chdir(nfilpath+"/"+str(i))
                for s in step:
                        if int(i)%int(s)==0 and i != 0:
                                os.system("mkdir -p "+str(s))
                                os.system("python /home/psr/software/riptide/pipelines/pipeline.py "+confighome+"/"+str(numpy.abs(s))+"_manager.yaml \"*.inf\" "+str(s))
                remove(nfilpath+"/"+str(i)+"/Out*")
        remove(nfilpath+"/timeseries/Out*")
        a,al=ripsiftest(nfilpath,step,al)
        stream = file(confighome+manage['search_configs'][0], 'r')
	search = yaml.load(stream)
        his,k,hismap=sif(a,nfilpath,step_dm=manage['dm_step'],max_dm=manage['dm_max'],max_a=al.max(),step_a=step[0],max_period=search['search']['period_max'],period_min=search['search']['period_min'])
        para=best(his)
        ripfold2(nfilpath,para,hismap,al,k,his,beam,ver,step,confighome)
	
def main():
	if sys.argv[1] == "-h":
		os.system('clear')
		print "=========================================================================="
		print "============Welcome to the Acceleration FFA search pipeline==============="
		print "===========This pipeline is created by J. Wongphechauxsorn================"
		print "===================Jompoj@mpifr-bonn.mpg.de==============================="
		print "pipeline_1beam.py /path/to/fillterbank fillterbankname /path/to/configfile"  
		exit(0) 
	ver="FEB/19_Eff"
	print ver
	#parser = argparse.ArgumentParser()
	#parser.add_argument('-v', action='v', dest='simple_value',
        #            help='Store a simple value')

	#Acceration search with basic folding, no rfi mitigation
	filhome=sys.argv[1] #path to filterbank file
	filname=sys.argv[2] #filterbank name
	confighome=sys.argv[3] #path to setting.yaml
	stream = file(confighome+'setting.yaml', 'r') #open yaml file, make sure you have manage_config.yaml and search.yaml in the same folder 
	setting=yaml.load(stream)
	stream = file(confighome+'HTRUNll3_manager.yaml', 'r')
	manage = yaml.load(stream)
	df=setting['para']['downsamp']
	work_dir=setting['dir']['work_dir']
	print("donwsamping")
	os.system("python "+confighome+"plot_candidate.py")
	Source,MJD,Beam=downsamp(filhome+"/"+filname,filhome+"/"+str(df)+"_"+filname,df)
	MJD=str(MJD)
	Beam=str(Beam)
	Source=Source.replace(' ','')
	os.system("mkdir -p "+work_dir+"/"+Source+"/"+MJD+"/"+Beam)
	os.system("mkdir -p"+setting['dir']['home_dir']+"/"+Source+"/"+MJD+"/"+Beam)
	nfilpath=work_dir+"/"+Source+"/"+MJD+"/"+Beam  #set nfil path 
	os.system("mv "+filhome+"/"+str(df)+"_"+filname+" "+work_dir+"/"+Source+"/"+MJD+"/"+Beam)
	print("load file")
	fil=nfilpath+"/"+str(df)+"_"+filname
	if os.path.exists(nfilpath+"/mask_rfifind.mask") == False :
		os.system("rfifind -o "+nfilpath+"/mask -clip 3 -time 35 -timesig 3 -freqsig 3 "+fil)
	os.system("mkdir "+nfilpath+"/timeseries")
	os.system("mkdir "+nfilpath+"/prepfold")
	# Accleration range
        #step=numpy.asarray([1.0,2.0,4.0,8.0,16.0,32.0,64.0,128.0])
        #al=numpy.arange(-128.0,129.0,1.0)
	step=numpy.asarray([256.0])
	al=numpy.arange(-256.0,512.0,256.0)
	os.chdir(confighome)
	#calyaml('HTRUNll3_manager.yaml',a_min=step[0],a_max=step.max(),dm_min=manage['dm_step'],dm_max=manage['dm_max'],t_obs=180)
	os.chdir(nfilpath)
	pipe(nfilpath,setting,manage,fil,confighome,Beam,ver,step,al)
	os.chdir(nfilpath)
	#os.system("mv -f "+nfilpath+" "+setting['dir']['home_dir'])
	#os.system("tar -czf "+setting['dir']['home_dir']+"/"+Source+"_"+MJD+"_"+Beam+"h5.tar.gz *.h5")
	os.system("tar -czf "+setting['dir']['home_dir']+"/"+Source+"_"+MJD+"_"+Beam+"png.tar.gz *.png")

if __name__== "__main__":
	main()
