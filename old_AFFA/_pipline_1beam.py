#1.0 create pipeline for 1 beam 
#1.1fix bug from .dat-->.inf
#1.1.1 fck I forgot to import numpyi
#beam test:test full pipe with beam 6
#Huge upgrade to get any filfile copy that to scarch process and copy back using yaml 17/03/2018
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

def remove(pattern):
        for f in glob.glob(pattern):
                os.remove(f)

def downsamp(fil,dfil,ndf):
	myFil = FilReader(fil)
	myFil.header.telescope_id=8
	if not os.path.exists(dfil):
		myFil.downsample(tfactor=ndf,filename=dfil,gulp=1024)
	return myFil.header.source_name,myFil.header.tstart,myFil.header.ibeam


def dedisprse(fil,nfilpath,dmstep,numdm):                                                                 
        #os.system("rm "+nfilpath+"/timeseries/Out*")
	os.system("prepsubband -mask "+nfilpath+"/mask_rfifind.mask -ncpus 48 -lodm 0 -dmstep "+str(dmstep)+" -numdms "+str(numdm)+" -o "+nfilpath+"/timeseries/Out "+fil)

def zero_rfi(nfilpath):
	TS=riptide.TimeSeries.from_presto_inf(nfilpath+"/timeseries/Out_DM0.00")
        re=riptide.ffa_search(TS,period_min=0.50,period_max=321)
        p=riptide.peak_detection.find_peaks(re[2])
        blist=[]
        for i in range(0,len(p)-1):
        	blist.append([1.0/p[i].period,1,1])                 
		numpy.savetxt(nfilpath+"/blist",numpy.asarray(blist))

def TDR(nfilpath,al):
	os.chdir(nfilpath+"/timeseries")
	start = time.time()
	L=glob.glob("Out_DM*.dat")
#	al=[1.5,3.0,6.0,9.0,18.0,36.0,78.0]
	#sa=[1.5,6,24,96]
	#al=numpy.arange(-128.0,129.0,1.0)
	for na in al:
		for f in L:
			TS=readDat(f)
			nTS=TS*0
			n_samp=nTS.header.nsamples
			t_samp=nTS.header.tsamp
			os.system("mkdir -p "+nfilpath+"/"+str(na))
			#if not os.path.exists(str(na)+"_"+f):
			nTS=TS.resample(na)
			nTS.toDat(nfilpath+"/"+str(na)+"/"+TS.header.basename)
	end = time.time()
	print(end - start)


def fold(clist,filhome,pshome):
    for i in ranige(0,len(clist)-1):
    	os.system("prepfold -ncpus 24 -coarse -nosearch -n 128 -nsub 256 -noxwin -p "+str(clist[i][0])+" -dm "+str(clist[i][2])+" -o "+pshome+"/P_i"+str(clist[i][0])+"DM_i"+str(clist[i][1])+" "+filhome)

def pipe(nfilpath,setting,fil,confighome,beam,ver,step,al):
	dmstep=setting['para']['dm_step']
	dm_num=setting['para']['dm_num']
        if os.path.exists(nfilpath+"/timeseries/Out_DM0.00.inf") == False :
		dedisprse(fil,nfilpath,int(dmstep),int(dm_num))
	os.chdir(nfilpath+"/timeseries")
	TDR(nfilpath,al)
	os.system("pyon /home/psr/software/riptide/pipelines/pipeline.py "+confighome+"/EPICS_manager.yaml  \"Out*.inf\" "+nfilpath+"/prepfold" )
	#ripfold(nfilpath+"/prepfold")
	remove(nfilpath+"/timeseries/Out*")
	#step=[1.0,2.0,4.0,8.0,16.0,32.0,64.0,128.0]
	#al=numpy.arange(-128.0,129.0,1.0)
	for i in al:
		os.chdir(nfilpath+"/"+str(i))
		for s in step:
			if int(i)%int(s)==0 and i != 0:
				os.system("mkdir -p "+str(s))
				os.system("python /home/psr/software/riptide/pipelines/pipeline.py "+confighome+"/"+str(numpy.abs(s))+"_manager.yaml \"*.inf\" "+str(s))
		remove(nfilpath+"/"+str(i)+"/Out*")
	a,al=ripsiftest(nfilpath,step,al)
	his,k,hismap=sif(a,nfilpath)
	para=best(his)
	ripfold2(nfilpath,para,hismap,al,k,his,beam,ver)
	
def ripsiftest(nfilpath,step,al):
	cube=[]
        cube=ripsif(nfilpath+"/prepfold",0,0,cube)
#        step=[6.0,12.0,24.0,48.0,96.0]
#        al=numpy.arange(-96.0,102.0,6.0)
        #step=[1.0,2.0,4.0,8.0,16.0,32.0,64.0,128.0]
        #al=numpy.arange(-128.0,129.0,1.0)

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

def sif(cube,nfilpath,step_dm=3,max_period=432,max_dm=3000,max_a=128,step_a=1):
	numcube=numpy.asarray(cube)
	his=numpy.zeros((int(9*max_a),int(max_dm/step_dm),int(2*max_a/step_a+1)))
	hismap=numpy.zeros((int(9*max_a),int(max_dm/step_dm),int(2*max_a/step_a+1)))
	hismap=hismap.astype(str)
	for i in range(0,len(numcube)):
		pi=0.131
		t=pi/max_a
		k=[]
		for dex in range(0,9):
			pf=pi+(max_a*t)
			for j in range(0,max_a):
				k.append(pi+j*t)
			if (float(numcube[i][0]) > pi and float(numcube[i][0]) <= pf):
				p=int((float(numcube[i][0])/t)-max_a+(dex*max_a))
			pi=pf
			t=pi/128.0
		d=int(float(numcube[i][1])/step_dm)
		a=int((float(numcube[i][4])+max_a)/step_a)
		#print p,d,a
		his[p][d][a]=numpy.max([float(numcube[i][2]),his[p][d][a]])
		if a>max_a:
			hismap[p][d][a]=str(numcube[i][4])+"/"+str(numcube[i][5])+"/"+numcube[i][3]
			print hismap[p][d][a]
		elif a<max_a:
			hismap[p][d][a]=str(numcube[i][4])+"/"+str(numcube[i][5])+"/"+numcube[i][3]
			print hismap[p][d][a]
		elif a==max_a:
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
		

def ripfold2(nfilpath,para,hismap,al,k,his,beam,ver):
        os.chdir(nfilpath)
        ccanlist=[]
        os.sys.path.append("/home1/til/FFA-Acceration-pipeline") 
	from plot_candidate import CandidatePlot
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
			snr=numpy.format_float_positional(his[para[i][0]][para[i][1]][para[i][2]],precision=2)
			if os.path.isfile(nfilpath+"/"+hismap[para[i][0]][para[i][1]][para[i][2]]):
				path=nfilpath+"/"+hismap[para[i][0]][para[i][1]][para[i][2]]
	                        cand=Candidate.load_hdf5(path)
	                        accurve=numpy.asarray([al,his[para[i][0]][para[i][1]]])
        	                cplot=CandidatePlot(cand,accurve,beam,ver)
                	        plt.savefig(nfilpath+"/"+"Resultisnrpda_"+str(snr)+"_"+str(p)+"_"+str(d)+"_"+str(a)+".png")
                        	plt.close()
			elif os.path.isfile(nfilpath+"/"+hismap[para[i][0]][para[i][1]][para[i][2]]+'5'):
				path=nfilpath+"/"+hismap[para[i][0]][para[i][1]][para[i][2]]+'5'
	                        cand=Candidate.load_hdf5(path)
				accurve=numpy.asarray([al,his[para[i][0]][para[i][1]]])
                	        cplot=CandidatePlot(cand,accurve,beam,ver)
                        	plt.savefig(nfilpath+"/"+"Resultisnrpda_"+str(snr)+"_"+str(p)+"_"+str(d)+"_"+str(a)+".png")
				plt.close()

def best(his):
	para=[]
	for i in range(0,68*16):
		for j in range(0,1000):
			if his[i][j].max()>0:
				a=numpy.where(his[i][j]==his[i][j].max())[0][0]
				p=i
				dm=j
				para.append((p,dm,a))
	return para
	
	
def zapp(blist):
	a=numpy.loadtxt(blist)
	return a

def main():
	ver="Nov/18"
	#Acceration search with basic folding, no rfi mitigation
	#os.system("python "+confighome+"plot_candidate.py")
	filhome=sys.argv[1] #path to filterbank file
	filname=sys.argv[2] #filterbank name
	confighome=sys.argv[3] #path to setting.yaml
	stream = file(confighome+'setting.yaml', 'r') #open yaml file, make sure you have manage_config.yaml and search.yaml in the same folder 
	setting=yaml.load(stream)
	df=setting['para']['downsamp']
	work_dir=setting['dir']['work_dir']
	print("donwsamping")
	os.system("python "+confighome+"plot_candidate.py")
	Source,MJD,Beam=downsamp(filhome+"/"+filname,filhome+"/"+str(df)+"_"+filname,df)
	MJD=str(MJD)
	Beam=str(Beam)
	Source=Source.replace(' ','_')
	os.system("mkdir -p "+work_dir+"/"+Source+"/"+MJD+"/"+Beam)
	os.system("mkdir -p"+setting['dir']['home_dir']+"/"+Source+"/"+MJD+"/"+Beam)
	nfilpath=work_dir+"/"+Source+"/"+MJD+"/"+Beam  #set nfil path 
	os.system("mv "+filhome+"/"+str(df)+"_"+filname+" "+work_dir+"/"+Source+"/"+MJD+"/"+Beam)
	print("load file")
	fil=nfilpath+"/"+str(df)+"_"+filname
	if os.path.exists(nfilpath+"/mask_rfifind.mask") == False :
		os.system("rfifind -o "+nfilpath+"/mask -clip 4 -time 35 -timesig 5 -freqsig 3 "+fil)
	os.system("mkdir "+nfilpath+"/timeseries")
	os.system("mkdir "+nfilpath+"/prepfold")
	
	# Accleration range
        step=numpy.asarray([1.0,2.0,4.0,8.0,16.0,32.0,64.0,128.0])
        al=numpy.arange(-128.0,129.0,1.0)

	pipe(nfilpath,setting,fil,confighome,Beam,ver,step,al)
	os.chdir(nfilpath)
	os.system("tar -czf "+setting['dir']['home_dir']+"/"+Source+"_"+MJD+"_"+Beam+"h5.tar.gz *.h5")
	os.system("tar -czf "+setting['dir']['home_dir']+"/"+Source+"_"+MJD+"_"+Beam+"png.tar.gz *.png")

if __name__== "__main__":
	main()
