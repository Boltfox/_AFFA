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
os.system("python ~/dev_pipe/plot_candidate.py")
def remove(pattern):
	for f in glob.glob(pattern):
		os.remove(f)


def downsamp(fil,dfil,ndf):
	myFil = FilReader(fil)
	myFil.header.telescope_id=4
	if not os.path.exists(dfil):
		myFil.downsample(tfactor=ndf,filename=dfil,gulp=1024)
	return myFil.header.source_name,myFil.header.tstart,myFil.header.ibeam


def dedisprse(fil,nfilpath):                                                                 
        #os.system("rm "+nfilpath+"/timeseries/Out*")
	#os.system("prepsubband -ncpus 48 -lodm 0 -dmstep "+str(3)+" -numdms "+str(1)+" -o "+nfilpath+"/timeseries/Out "+fil)
	myFil = FilReader(fil)
	TS=myFil.dedisperse(0)
	TS.toDat(nfilpath+"/timeseries/Out_DM0.00")	

def zero_rfi(nfilpath):
	TS=riptide.TimeSeries.from_presto_inf(nfilpath+"/timeseries/Out_DM0.00")
        re=riptide.ffa_search(TS,period_min=0.50,period_max=321)
        p=riptide.peak_detection.find_peaks(re[2])
        blist=[]
        for i in range(0,len(p)-1):
        	blist.append([1.0/p[i].period,1,1])                 
		numpy.savetxt(nfilpath+"/blist",numpy.asarray(blist))

def TDR(nfilpath):
	os.chdir(nfilpath+"/timeseries")
	start = time.time()
	L=glob.glob("Out_DM*.dat")
#	al=[1.5,3.0,6.0,9.0,18.0,36.0,78.0]
	#sa=[1.5,6,24,96]
	al=numpy.arange(-96.0,102.0,6.0)
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

def pipe(nfilpath,setting,fil,confighome):
	dmstep=setting['para']['dm_step']
	dm_num=setting['para']['dm_num']
        if os.path.exists(nfilpath+"/timeseries/Out_DM0.00.inf") == False :
		dedisprse(fil,nfilpath)
	os.chdir(nfilpath+"/timeseries")
	TDR(nfilpath)
	os.system("python /home/psr/software/riptide/pipelines/pipeline.py "+confighome+"/HTRU-acc-S_manager_config.yaml  \"Out*.inf\" "+nfilpath+"/prepfold" )
	#ripfold(nfilpath+"/prepfold")
	remove(nfilpath+"/timeseries/Out*.inf")
	remove(nfilpath+"/timeseries/Out*.dat")
	step=[6.0,12.0,24.0,48.0,96.0]
	#step=[24.0]
	al=numpy.arange(-96.0,102.0,6.0)
#	for j in step:
#		al=numpy.arange(j,96.0,j)
	for i in al:
		os.chdir(nfilpath+"/"+str(i))
		for s in step:
			if int(i)%int(s)==0 and i != 0:
				if s>0:
					os.system("mkdir -p p"+str(s))
					os.system("python /home/psr/software/riptide/pipelines/pipeline.py "+confighome+"/"+str(numpy.abs(s))+"_manager.yaml \"*.inf\" p"+str(s))
				        print("building "+nfilpath+"/"+str(i)+"/"+"p"+str(s))
				if s<0:
					os.system("mkdir -p m"+str(-1*s))
                                        os.system("python /home/psr/software/riptide/pipelines/pipeline.py "+confighome+"/"+str(numpy.abs(s))+"_manager.yaml \"*.inf\" m"+str(-1*s))
					print("building "+nfilpath+"/"+str(i)+"/"+"m"+str(-1*s))
		remove(nfilpath+"/"+str(i)+"/Out*.inf")
		remove(nfilpath+"/"+str(i)+"/Out*.dat")

	a,al=ripsiftest(nfilpath)
	his,k,hismap=sif(a,nfilpath)
	#hismap[numpy.where(his==his.max())][0]
	#p=maxpara[0][0]
	#d=maxpara[0][1]
	#a=maxpara[0][2]
	#return his.max()
	#np.save("aray", his,hismap,al,k)
	return his.max()

def pipecom(nfilpath,setting,fil,confighome):
        dmstep=setting['para']['dm_step']
        dm_num=setting['para']['dm_num']
        if os.path.exists(nfilpath+"/timeseries/Out_DM0.00.inf") == False :
                dedisprse(fil,nfilpath)
        os.chdir(nfilpath+"/timeseries")
        os.system("python /home/psr/software/riptide/pipelines/pipeline.py "+confighome+"/HTRU-acc-S_manager_config.yaml  \"Out*.inf\" "+nfilpath+"/prepfold" )
	remove(nfilpath+"/timeseries/Out*.inf")
        remove(nfilpath+"/timeseries/Out*.dat")
        a=ripfold(nfilpath)
        return a.max()	
	
def ripsiftest(nfilpath):
	cube=[]
        cube=ripsif(nfilpath+"/prepfold",0,0,cube)
        step=[6.0,12.0,24.0,48.0,96.0]
        #step=[24.0]
	al=numpy.arange(-96.0,102.0,6.0)
        for i in al:
                os.chdir(nfilpath)
		os.chdir("./"+str(i))
                for s in step:
                        if int(i)%int(s)==0 and i != 0:
                                if s>0:
					cube=ripsif(nfilpath+"/"+str(i)+"/p"+str(s),i,s,cube)
                                if s<0:
					cube=ripsif(nfilpath+"/"+str(i)+"/m"+str(-1*s),i,s,cube)
			elif i==0:
				cube=ripsif(nfilpath+"/prepfold",i,s,cube)
                #if int(i)%12==0:
                #       os.system("python /home/psr/software/riptide/pipelines/pipeline.py "+confighome+"/12.0_manager.yaml \"*.inf\" ./")
                                #ripsif(nfilpath+"/"+str(i),i,s)
	return cube,al


def ripsif(nfilpath,a,da,cube):
        os.chdir(nfilpath)
        canlist=glob.glob('*.h5')
        for i in canlist:
        	cand=Candidate.load_hdf5(i)
                cube.append((cand.metadata['best_period'],cand.metadata['best_dm'],cand.metadata['best_snr'],i,a,da))
	return cube

def sif(cube,nfilpath,step_dm=3,max_period=432,max_dm=3000,max_a=96,step_a=6):
	numcube=numpy.asarray(cube)
	his=numpy.zeros((int(68*16),int(max_dm/step_dm),int(2*max_a/step_a+1)))
	hismap=numpy.zeros((int(68*16),int(max_dm/step_dm),int(2*max_a/step_a+1)))
	hismap=hismap.astype(str)
	for i in range(0,len(numcube)):
		pi=0.14
		t=0.14/128.0
		k=[]
		for dex in range(0,68):
			pf=pi+(16*t)
			for j in range(0,16):
				k.append(pi+j*t)
			if (float(numcube[i][0]) > pi and float(numcube[i][0]) <= pf):
				p=int((float(numcube[i][0])/t)-128+(dex*16))
			pi=pf
			t=pi/128.0
		d=int(float(numcube[i][1])/step_dm)
		a=int((float(numcube[i][4])+max_a)/step_a)
		his[p][d][a]=numpy.max([float(numcube[i][2]),his[p][d][a]])
		if a>16:
			hismap[p][d][a]=str(numcube[i][4])+"/p"+str(numcube[i][5])+"/"+numcube[i][3]
			print hismap[p][d][a]
		elif a<16:
			hismap[p][d][a]=str(numcube[i][4])+"/m"+str(numcube[i][5])+"/"+numcube[i][3]
			print hismap[p][d][a]
		elif a==16:
			hismap[p][d][a]="/prepfold/"+numcube[i][3]
			print hismap[p][d][a]
	return his,k,hismap

def ripfold(nfilpath):
	os.sys.path.append("/home1/dev_pipe")
        os.chdir(nfilpath+"/prepfold")
        canlist=glob.glob('*.h5')
        ccanlist=[]
	cube=[]
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
                	#cplot=CandidatePlot(cand)
                	#plt.savefig(i+".png")
                	#plt.close()

	else :
		for i in canlist:
        	        cand=Candidate.load_hdf5(i)
			#cplot=CandidatePlot(cand)
			#plt.savefig(i+".png") 
			#plt.close()
			cube.append(cand.metadata['best_snr'])
	return numpy.asarray(cube)		

def ripfold2(nfilpath,para,hismap,al,k,his):
        os.chdir(nfilpath)
        ccanlist=[]
        os.sys.path.append("/home1/dev_pipe") 
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
		        cplot=CandidatePlot(cand,accurve)
                        plt.savefig(nfilpath+"/"+"Resultpda_"+str(p)+"_"+str(d)+"_"+str(a)+".png")
			plt.close()
        else :
                for i in range(0,len(para)):
                        p=numpy.format_float_positional(k[para[i][0]],precision=2)
                        d=para[i][1]*3
                        a=al[para[i][2]]
			snr=numpy.format_float_positional(his[para[i][0]][para[i][1]][para[i][2]],precision=2)
                        cand=Candidate.load_hdf5(nfilpath+"/"+hismap[para[i][0]][para[i][1]][para[i][2]])
			accurve=numpy.asarray([al,his[para[i][0]][para[i][1]]])
                        cplot=CandidatePlot(cand,accurve)
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

def a_max(P_orb,mc):
        f=mc**3/(mc+1.4)**2
        T=4.954186016*10**(-6)
        C=2.997*10**(8)
        a=(2*numpy.pi/P_orb)**(4/3.0)*(T*f)**(1/3.0)*C
        return a


def main():
	os.system("python ~/dev_pipe/plot_candidate.py")
	filhome=sys.argv[1] #path to filterbank file
	filname=sys.argv[2] #filterbank name1
	controlname=sys.argv[3] #control filterbank
	confighome=sys.argv[4] #path to setting.yaml
	P=sys.argv[5]
	a=sys.argv[6]
	w=sys.argv[7]
	stream = file(confighome+'setting.yaml', 'r') #open yaml file, make sure you have manage_config.yaml and search.yaml in the same folder 
	setting=yaml.load(stream)
	df=setting['para']['downsamp']
	work_dir=setting['dir']['work_dir']
	print("donwsamping")
	#Source,MJD,Beam=downsamp(filhome+"/"+filname,filhome+"/"+str(df)+"_"+filname,df)
	MJD=str(P)
	Beam=str(a)
	Beam2="0"
	Source="acctest"
	print "Create woking dir"
	os.system("mkdir -p "+work_dir+"/"+Source+"/"+MJD+"/"+Beam)
	os.system("mkdir -p "+work_dir+"/"+Source+"/"+MJD+"/"+Beam2)
	print "Create storing dir"
	os.system("mkdir -p "+setting['dir']['home_dir']+"/"+Source+"/"+MJD+"/"+Beam)
	os.system("mkdir -p "+setting['dir']['home_dir']+"/"+Source+"/"+MJD+"/"+Beam2)
	nfilpath=work_dir+"/"+Source+"/"+MJD+"/"+Beam  #set nfil path 
	nfilpath2=work_dir+"/"+Source+"/"+MJD+"/"+Beam2 
	os.system("cp "+filhome+"/"+filname+" "+work_dir+"/"+Source+"/"+MJD+"/"+Beam)
	os.system("cp "+filhome+"/"+controlname+" "+work_dir+"/"+Source+"/"+MJD+"/"+Beam2)
	print("load file")
	fil=nfilpath+"/"+filname
	fil2=nfilpath2+"/"+controlname
#	if os.path.exists(nfilpath+"/mask_rfifind.mask") == False :
#		os.system("rfifind -o "+nfilpath+"/mask -clip 4 -time 35 -timesig 5 -freqsig 3 "+fil)
	os.system("mkdir "+nfilpath+"/timeseries")
	os.system("mkdir "+nfilpath+"/prepfold")
        os.system("mkdir "+nfilpath2+"/timeseries")
        os.system("mkdir "+nfilpath2+"/prepfold")
	snr1=pipe(nfilpath,setting,fil,confighome)
	snr2=pipecom(nfilpath2,setting,fil2,confighome) 
	os.chdir(filhome)
	input_a=str(snr1/snr2)+","+str(P)+","+str(a)+","+str(w)+"\n"
	with open(filhome+'/data4.txt', 'a') as file2:
    		file2.write(input_a)
		file2.close()
	snr1=0
	snr2=0
if __name__== "__main__":
	main()
