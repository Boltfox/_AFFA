#A script to do sifing and folding using riptide 
#Splited form one file pipeline in 22th March 2019

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
#os.system("python /home1/til/FFA-Acceration-pipeline/candidate_plot.")
from correct_header import Headercorrector
from multiprocessing import Pool
from multiprocessing import Process
global nfilpath


def ripsiftest(nfilpath,step,al):
        cube=[]
        cube=ripsif(nfilpath+"/prepfold",0,0,cube)
        for i in al:
                os.chdir(nfilpath)
                os.chdir("./"+str(i))
                for s in step:
                        if int(i)%int(s)==0 and i != 0:
                                cube=ripsif(nfilpath+"/"+str(i)+"/"+str(s),i,s,cube)
                        elif i==0:
                                cube=ripsif(nfilpath+"/prepfold",i,s,cube)
        return cube,al


def ripsif(nfilpath,a,da,cube):
        os.chdir(nfilpath)
        canlist=glob.glob('*.h5')
        for i in canlist:
                cand=Candidate.load_hdf5(i)
                cube.append((cand.metadata['best_period'],cand.metadata['best_dm'],cand.metadata['best_snr'],i,a,da))
        return cube

def sif(cube,nfilpath,step_dm=6.0,max_period=432,max_dm=3072,max_a=128.0,step_a=4,t_obs=4320/2,bins_max=128,period_min=0.14):
        pi=period_min
        numcube=numpy.asarray(cube)
        numa=numpy.int(numpy.ceil(numpy.log2(max_period/period_min)))
        his=numpy.zeros((int(numa*bins_max+1),int(max_dm/step_dm),int(2*max_a/step_a+1)))
        hismap=numpy.zeros((int(numa*bins_max+1),int(max_dm/step_dm),int(2*max_a/step_a+1)))
        hismap=hismap.astype(str)
        for i in range(0,len(cube)):
                #pi=period_min
                t=period_min/bins_max
                k=[]
                p=0
                for dex in range(0,numa):
                        p_s_min=pi*2**dex
                        t=p_s_min/bins_max
                        for j in range(0,int(bins_max)):
                                ps=p_s_min+j*t
                                k.append(ps)
                                if (float(numcube[i][0]) > p_s_min-t and float(numcube[i][0]) <= ps):
                                        #p=int((float(numcube[i][0])/t)-max_a+(dex*max_a))
                                        p=int((ps-p_s_min)/t+(dex*bins_max))
                                        #print ps,p_s_min,j
                d=int(float(numcube[i][1])/step_dm)
                a=int((float(numcube[i][4])+max_a)/step_a)
                print p,d,a
                try:
                        his[p][d][a]=numpy.max([float(numcube[i][2]),his[p-1:p+2].max(axis=0)[d][a]])
                except ValueError:
                        his[p][d][a]=numpy.max([float(numcube[i][2]),his[p][d][a]])
                if a>max_a/step_a:
                        hismap[p][d][a]=str(numcube[i][4])+"/"+str(numcube[i][5])+"/"+numcube[i][3]
                        print hismap[p][d][a]
                elif a<max_a/step_a:
                        hismap[p][d][a]=str(numcube[i][4])+"/"+str(numcube[i][5])+"/"+numcube[i][3]
                        print hismap[p][d][a]
                elif a==max_a/step_a:
                        hismap[p][d][a]="/prepfold/"+numcube[i][3]
                        print hismap[p][d][a]
        return his,k,hismap

def ripfold(nfilpath):
        os.chdir(nfilpath)
        canlist=glob.glob('*.h5')
        ccanlist=[]
        if os.path.exists(nfilpath+"/blist"):
                blist=zapp(nfilpath+"/blist")
                for i in canlist:
                        cand=Candidate.load_hdf5(i)
                        for j in blist[:,0]:
                                if((numpy.abs(cand.metadata['best_period']-1/j)) > 0.01 ) :
                                        if not i in ccanlist:
                                                ccanlist.append(i)
                                        else :
                                                print "unsafe",1/j,cand.metadata['best_period'],i
                                if i in ccanlist:
                                        ccanlist.remove(i)
                                break
                for i in ccanlist:
            #print i
                        cand=Candidate.load_hdf5(i)
                        cplot=CandidatePlot(cand)
                        plt.savefig(i+".png")
                        plt.close()

        else :
                for i in canlist:
                        cand=Candidate.load_hdf5(i)
                        cplot=CandidatePlot(cand)
                        plt.savefig(i+".png")
                        plt.close()

def ripfold2(nfilpath,para,hismap,al,k,his,beam,ver,step,confighome):
        os.chdir(nfilpath)
        ccanlist=[]
        os.sys.path.append(confighome)
        from plot_candidate import CandidatePlot
        aaray=numpy.arange(al.min(),al.max()+1,step[0])
        if os.path.exists(nfilpath+"/blist"):
                blist=zapp(nfilpath+"/blist")
                for i in range(0,len(para)):
                        p=para[i][0]
                        d=para[i][1]
                        a=para[i][2]
                        cand=Candidate.load_hdf5(hismap[p][d][a])
                        for j in blist[:,0]:
                                if((numpy.abs(cand.metadata['best_period']-1/j)) > 0.01 ) :
                                        if not i in ccanlist:
                                                ccanlist.append(i)
                                        else :
                                                print "unsafe",1/j,cand.metadata['best_period'],i
                                if i in ccanlist:
                                        ccanlist.remove(i)
                                break
                for i in ccanlist:
                        cand=Candidate.load_hdf5(i)
                        p=para[i][0]
                        d=para[i][1]
                        accurve=numpy.asarray([al,his[p][d]])
                        cplot=CandidatePlot(cand,accurve,beam,ver)
                        plt.savefig(nfilpath+"/"+"Resultpda_"+str(p)+"_"+str(d)+"_"+str(a)+".png")
                        plt.close()
        else :
                for i in range(0,len(para)):
                        p=numpy.format_float_positional(k[para[i][0]],precision=2)
                        d=para[i][1]*3
                        a=al[para[i][2]]
                        snr=numpy.format_float_positional(his[para[i][0]][para[i][1]][para[i][2]]*100,precision=2)
                        if os.path.isfile(nfilpath+"/"+hismap[para[i][0]][para[i][1]][para[i][2]]):
                                path=nfilpath+"/"+hismap[para[i][0]][para[i][1]][para[i][2]]
                                cand=Candidate.load_hdf5(path)
                                try:
                                        if (para[i][0]-1 > 0) and (para[i][0]+2 < his.shape[0]): accurve=numpy.asarray([aaray,his[para[i][0]-1:para[i][0]+2].max(axis=0)[para[i][1]]])
                                        elif (para[i][0]+2 < his.shape[0]): accurve=numpy.asarray([aaray,his[para[i][0]:para[i][0]+2].max(axis=0)[para[i][1]]])
                                        elif (para[i][0] > 0 ): accurve=numpy.asarray([aaray,his[para[i][0]-1:para[i][0]].max(axis=0)[para[i][1]]])
                                except ValueError:
                                        accurve=numpy.asarray([al,his[para[i][0]][para[i][1]]])
                                cplot=CandidatePlot(cand,accurve,beam,ver)
                                plt.savefig(nfilpath+"/"+"Resultisnrpda_"+str(snr)+"_"+str(p)+"_"+str(d)+"_"+str(a)+".png")
                                plt.close()
                        elif os.path.isfile(nfilpath+"/"+hismap[para[i][0]][para[i][1]][para[i][2]]+'5'):
                                path=nfilpath+"/"+hismap[para[i][0]][para[i][1]][para[i][2]]+'5'
                                cand=Candidate.load_hdf5(path)
                                try:
                                        if (para[i][0]-1 > 0) and (para[i][0]+2 < his.shape[0]): accurve=numpy.asarray([aaray,his[para[i][0]-1:para[i][0]+2].max(axis=0)[para[i][1]]])
                                        elif (para[i][0]+2 < his.shape[0]): accurve=numpy.asarray([aaray,his[para[i][0]:para[i][0]+2].max(axis=0)[para[i][1]]])
                                        elif (para[i][0] > 0 ): accurve=numpy.asarray([aaray,his[para[i][0]-1:para[i][0]].max(axis=0)[para[i][1]]])
                                except ValueError:
                                        accurve=numpy.asarray([al,his[para[i][0]][para[i][1]]])
                                cplot=CandidatePlot(cand,accurve,beam,ver)
                                plt.savefig(nfilpath+"/"+"Resultisnrpda_"+str(snr)+"_"+str(p)+"_"+str(d)+"_"+str(a)+".png")
                                plt.close()
def best(his):
         para=[]
         i_m=his.shape[0]
         j_m=his.shape[1]
         for i in range(0,i_m):
                 for j in range(0,j_m):
                         if his[i][j].max()>0:
                                 a=numpy.where(his[i][j]==his[i][j].max())[0][0]
                                 p=i
                                 dm=j
                                 para.append((p,dm,a))
         return para


def zapp(blist):
        a=numpy.loadtxt(blist)
        return a

def pipe(nfilpath,setting,manage,fil,confighome,beam,ver,step,al):
	print "getting h5 files"
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
		print "pipeline_1beam.py /path/to/folder/contain/results fillterbankname /path/to/configfile"  
		exit(0) 

	ver="FEB/19_Eff_refold"
        #Acceration search with basic folding, no rfi mitigation
        filhome=sys.argv[1] #path to filterbank file
        fil=sys.argv[2] #filterbank name
	#print filhome,filname
        confighome=sys.argv[3] #path to setting.yaml
        stream = file(confighome+'setting.yaml', 'r') #open yaml file, make sure you have manage_config.yaml and search.yaml in the same folder 
        setting=yaml.load(stream)
        stream = file(confighome+'HTRUNll3_manager.yaml', 'r')
        manage = yaml.load(stream)
        df=setting['para']['downsamp']
        work_dir=setting['dir']['work_dir']
        print("donwsamping")
        os.system("python "+confighome+"plot_candidate.py")
        Beam=str("refold")
        # Accleration range
        #step=numpy.asarray([2.0,4.0,8.0,16.0,32.0,64.0,128.0])
        #al=numpy.arange(-128.0,130.0,2.0)
	step=numpy.asarray([256.0,512.0,1024.0])
	al=numpy.arange(-1024,1280,256) 
        nfilpath=filhome
	#os.chdir(nfilpath)
        pipe(nfilpath,setting,manage,fil,confighome,Beam,ver,step,al)
        os.chdir(nfilpath)
if __name__ == "__main__":
    main()
