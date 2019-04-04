from sigpyproc.Readers import FilReader 
from sigpyproc import Header
import numpy as np

from astropy import units as u
from astropy.coordinates import SkyCoord
from astropy.coordinates import ICRS, Galactic

def checkminus(source_name): #Check source name if it has '-' which implys negative Dec 
	negative=False
	for i in source_name:
		negative=(i=='-') or negative
	return negative 

def Headercorrector(mFil):
  ra=mFil.header.ra_rad
  dec=mFil.header.dec_rad
#check for - if true change dec 

  if checkminus(mFil.header.source_name):
	  dec=-mFil.header.dec_rad

  beam=mFil.header.ibeam
#define beam 1-6 position for HTRU-N
  if  mFil.header.telescope_id == 8:
    be=np.asarray([ 7,  9, 11,  1,  3,  5])*np.pi/6.0
  else :
    print "Telescope/Reciver unidentify"
  
  print "Beam:"+str(beam)
#RA/DEC to GB/GL
  pos=SkyCoord(ra*u.rad,dec*u.rad).galactic
  gb=pos.b.rad
  gl=pos.l.rad

#calculate shift 
  Theta=np.pi/6
  R=np.deg2rad(0.25167)
  if beam > 0:
    GL=R*np.cos(Theta+be[beam-1])+gl
    GB=R*np.sin(Theta+be[beam-1])+gb
  else :
     GL=gl
     GB=gb
#GB/GL to RA/DEC 
  npos=SkyCoord(b=GB*u.rad,l=GL*u.rad,frame=Galactic).icrs

  Ra_rad=npos.ra.rad
  Ra_deg=npos.ra.deg
  tmp=Header.rad_to_hms(Ra_rad)
  Ra=str(tmp[0])+":"+str(tmp[1])+":"+str(tmp[2])
  scr_Raj=str(tmp[0])+str(tmp[1])+str(int(tmp[2]))+".0"
  Dec_rad=npos.dec.rad
  Dec_deg=npos.dec.deg
  tmp=Header.rad_to_dms(Dec_rad)
  Dec=str(tmp[0])+":"+str(tmp[1])+":"+str(tmp[2])
  scr_Decj=str(tmp[0])+str(tmp[1])+str(int(tmp[2]))+".0"
  mFil.header.ra=Ra
  mFil.header.ra_deg=Ra_deg
  mFil.header.ra_rad=Ra_rad
  mFil.header.scr_raj=scr_Raj 
  mFil.header.dec=Dec
  mFil.header.dec_deg=Dec_deg
  mFil.header.dec_rad=Dec_rad
  mFil.header.scr_decj=scr_Decj
  #print mFil.header.scr_decj

  return mFil

#Load fill get coor in rad
#m_0Fil=FilReader("1855_0001_00_8bit.fil") 
#n_0Fil=Headercorrector(m_0Fil)
#Load fill get coor in rad
#m_1Fil=FilReader("1855_0001_01_8bit.fil") 
#n_1Fil=Headercorrector(m_1Fil)
