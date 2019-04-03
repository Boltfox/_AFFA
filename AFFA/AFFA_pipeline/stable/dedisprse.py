# Split from one file pipeline in 22th Mar 2019

#import os
import os

def dedisprse(fil,nfilpath,manage):
        #os.system("rm "+nfilpath+"/timeseries/Out*")
        lodm=float(manage['dm_min']) #read minimum dm
        hidm=float(manage['dm_max']) # read maximum dm
        dmstep=float(manage['dm_step']) # read dm step
        numdm=int((hidm-lodm)/dmstep) # calculate number of dm
        os.system("prepsubband -mask "+nfilpath+"/mask_rfifind.mask -ncpus 24 -lodm "+str(lodm)+" -dmstep "+str(dmstep)+" -numdms "+str(numdm/4)+" -o "+nfilpath+"/timeseries/Out "+fil)
        os.system("prepsubband -mask "+nfilpath+"/mask_rfifind.mask -ncpus 24 -lodm "+str(numdm/4*dmstep)+" -dmstep "+str(dmstep)+" -numdms "+str(numdm/4)+" -o "+nfilpath+"/timeseries/Out "+fil)
        os.system("prepsubband -mask "+nfilpath+"/mask_rfifind.mask -ncpus 24 -lodm "+str(2*numdm/4*dmstep)+" -dmstep "+str(dmstep)+" -numdms "+str(numdm/4)+" -o "+nfilpath+"/timeseries/Out "+fil)
        os.system("prepsubband -mask "+nfilpath+"/mask_rfifind.mask -ncpus 24 -lodm "+str(3*numdm/4*dmstep)+" -dmstep "+str(dmstep)+" -numdms "+str(numdm/4)+" -o "+nfilpath+"/timeseries/Out "+fil)
