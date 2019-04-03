import numpy as np 
import yaml
import argparse

def calyaml(configname,a_min=1,a_max=256,dm_max=2048,t_obs=2160,dm_min=2):
#	import numpy as np
#	import yaml 	
	stream = file(configname, 'r')
	manager=yaml.load(stream)
	stream = file(manager['search_configs'][0], 'r')
	search=yaml.load(stream)
	pi=search['search']['period_min']
	pm=search['search']['period_max']
	pb=pi
	acc=a_min
	#acc_m=96
	bacc=[]
	sa=[]
	sdm=[]
	bins_min=search['search']['bins_min']
	bins_max=search['search']['bins_max']
	#t_obs=4320
	p=[]
	a=[]
	t=pi/bins_min
	nb=bins_max-bins_min
	bin=[]
	na=[]
	bin.append(bins_min)
	while pi<=pm:
		pf=pi+(nb*t)
#		if pf>=10*pb and bins_min<512:
#			pb=pf
#			bin.append(bins_min)
		p.append(pi)
		a_th=int(pi*3*10**8/(2*t_obs*t_obs))
	#	a.append(int(pi*3*10**8/(2*t_obs*t_obs)))
		a.append(a_th)
		#na.append(pi*3*10**8/(2*t_obs*t_obs))
		na.append(2**round(np.log2(a_th)))
		pi=pf
		t=pi/bins_min
	print p	
	#if na[0]<= a_max:
#		if na[0]>a_min:
#			acc=acc*(na[0]/a_min)
#		while acc <= a_max*2:
#			sa.append(p[np.where(np.asarray(na)/acc==1)[0][0]])
#			bacc.append(acc)
#			acc=acc*2
#		print sa
	for i in na:
		if i >=a_min and i<=a_max:
			sa.append(i)
	print sa
	#else :
	#	print("no need for acceleration search")

	for i in range(0,len(sa)):
#		manager['search_configs'][0]=str(bacc[i])+".0.yaml"
#		with open(str(bacc[i])+".0_manager.yaml", 'w') as yaml_file:
#			yaml.dump(manager, yaml_file, default_flow_style=False)
#Working on searching yaml files
		search['search']['period_max']=p[i+1]
		search['search']['period_min']=p[i]
		with open(str(sa[i])+".yaml", 'w') as yaml_file:
			yaml.dump(search, yaml_file, default_flow_style=False)
#Working on manager yaml files
		dm_step=manager['dm_step']
		manager['search_configs'][0]=str(sa[i])+".yaml"
		manager['dm_step']=dm_step*(2**i)
                with open(str(sa[i])+"_manager.yaml", 'w') as yaml_file:
                        yaml.dump(manager, yaml_file, default_flow_style=False)
		print p[i],p[i+1],dm_step*(2**i),sa[i]
	al=np.arange(-sa[i],sa[i]+sa[0],sa[0])
	print al
	return sa,al
#calyaml('555')

def main():
#	print "Welcome"
	parser = argparse.ArgumentParser()
	parser.add_argument('-n', action='store', dest='configname',
                    help='Configfile (manager) name')
	parser.add_argument('-a_min', action='store', dest='a_min',
                    help='Minimum accleration (m/s)')
        parser.add_argument('-a_max', action='store', dest='a_max',
                    help='Maximum accleration (m/s)')
	parser.add_argument('-dm_max', action='store', dest='dm_max',
                    help='Maximum DM')
        parser.add_argument('-dm_min', action='store', dest='dm_min',
                    help='Minimum DM')
        parser.add_argument('-t', action='store', dest='t_obs',
                    help='Observation time (s)')

	results = parser.parse_args()
	#print 'configname =', results.configname
	print results.configname,results.a_min,results.a_max,results.dm_max,results.t_obs,results.dm_min
	calyaml(results.configname,np.float(results.a_min),np.float(results.a_max),np.float(results.dm_max),np.float(results.t_obs),np.float(results.dm_min))
if __name__ == "__main__":
	main()
