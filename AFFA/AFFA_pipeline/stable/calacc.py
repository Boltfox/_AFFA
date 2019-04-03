import numpy as np 
import yaml

def calyaml(configname,a_min=1,a_max=256,dm_max=2048,t_obs=2160,dm_min=2):
	import numpy as np
	import yaml 	
	stream = file('EPICS_manager.yaml', 'r')
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
		if pf>=10*pb and bins_min<512:
			pb=pf
			bin.append(bins_min)
		p.append(pi)
		a.append(int(pi*3*10**8/(2*t_obs*t_obs)))
		na.append(pi*3*10**8/(2*t_obs*t_obs))
		pi=pf
		t=pi/bins_min
	
	if a[0]<= a_max:
		if a[0]>a_min:
			acc=acc*(a[0]/a_min)
		while acc <= a_max*2:
			sa.append(p[np.where(np.asarray(a)/acc==1)[0][0]])
			bacc.append(acc)
			acc=acc*2
		#print sa
	else :
		print("no need for acceration search")

	for i in range(0,len(bacc)):
#		manager['search_configs'][0]=str(bacc[i])+".0.yaml"
#		with open(str(bacc[i])+".0_manager.yaml", 'w') as yaml_file:
#			yaml.dump(manager, yaml_file, default_flow_style=False)
		search['search']['period_max']=sa[i]*2
		search['search']['period_min']=sa[i]
		with open(str(bacc[i])+".0.yaml", 'w') as yaml_file:
			yaml.dump(search, yaml_file, default_flow_style=False)
                manager['search_configs'][0]=str(bacc[i])+".0.yaml"
		manager['dm_step']=dm_min*(bacc[i]/bacc[0])
                with open(str(bacc[i])+".0_manager.yaml", 'w') as yaml_file:
                        yaml.dump(manager, yaml_file, default_flow_style=False)
calyaml('555')
