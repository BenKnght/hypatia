#
# Copyright Natalie R. Hinkel
# (2010 -- Present)
#

import numpy
import atpy
from math import *
import subprocess
import datetime
from time import sleep
import sys

now1 = datetime.datetime.now()
print now1

hipnames = atpy.Table("hipparcos_names.tsv", type="ascii", delimiter="|")
tycho = atpy.Table("hipparcos-tycho.csv", type="ascii", delimiter=",")
all_hipnums = hipnames.HIP
all_hdnums = [int(x.strip()) for x in hipnames.HD if not x == '']
all_bdnums = [x.strip("B").strip() for x in hipnames.BD if not x == '']

starlist = raw_input('Which star list would you like to use? ')

if starlist=='' or starlist=='hip' or starlist=='hipp' or starlist=='hipparcos':
    all_hipnums = hipnames.HIP
    all_hdnums = [int(x.strip()) for x in hipnames.HD if not x == '']
    all_bdnums = [x.strip().replace("D", "") for x in hipnames.BD if not x == '']
elif starlist=='exo' or starlist=='exoplanet' or starlist=='exoplanets':
    urllib.urlretrieve('http://www.exoplanets.org/csv-files/exoplanets.csv','exo.csv')
    exo = atpy.Table("exo.csv", type="ascii", delimiter=",")
    all_hipnums = [int(x) for ii, x in enumerate(exo.HIPP) if (not x=='' and not exo.EOD[ii]==0)]
    all_hdnums = [int(x.strip()) for ii,x in enumerate(exo.HD) if (not x == '' and not exo.EOD[ii]==0)]
    all_bdnums = [x.strip().replace("D", "") for ii,x in enumerate(exo.NAME) if (not x=='' and "BD" in x and not exo.EOD[ii]==0)]

#-------------
# Changeable parameters

hypatia_dist_cutoff = 150.  #pc
spec_type_cuts = ['O','B', 'A'] #don't include these spectral types

TOTsolar_norm_index = ''  # 4: to renormalize, '': to use the internal solar_index for unnorm

#-------------


hipparcos = atpy.Table("hipparcos.tsv", type="ascii", delimiter="|")
solar = atpy.Table("solar_abund.csv", type="ascii", delimiter=",")
spectral = atpy.Table("hip_spec.csv", type="ascii", delimiter="|")
anders = atpy.Table("uvw/Anderson12-uvw.tsv",type="ascii",delimiter="|")
tycho = atpy.Table("hipparcos-tycho.csv", type="ascii", delimiter=",")


def calcPos(hip):
    line = hipparcos.where(hipparcos.HIP==hip)
    ra = line.RA
    dec = line.DEC
    par = line.PARX
    # parallax angle in milliarcseconds converted to distance in parsecs
    dist = 1./(float(par) * 0.001)
    # cartesian coordinates
    return [dist*cos(dec)*cos(ra), dist*cos(dec)*sin(ra), dist*sin(dec)]

def calcDist(hip):
    line = hipparcos.where(hipparcos.HIP==hip)
    par = line.PARX
    # parallax angle in milliarcseconds converted to distance in parsecs
    dist = 1./(float(par) * 0.001)
    return [dist]


def defRD(hip):
    line = hipparcos.where(hipparcos.HIP==hip)
    ra = line.RA
    dec = line.DEC
    return [ra, dec]

def Type(hip):
    line = spectral.where(spectral.HIP==int(hip))
    st = line.SpType
    return st

def color(hip):
    line = hipparcos.where(hipparcos.HIP==hip)
    beve = line.BV
    return [beve]

def appmag(hip):
    line = hipparcos.where(hipparcos.HIP==hip)
    vmag = line.V
    return [vmag]

def uxux(hip):
    line = anders.where(anders.HIP==hip)
    ufoo = line.U[0]
    if len(ufoo)>0.:
        ufoo = float(line.U[0])
    return [ufoo]

def vxvx(hip):
    line = anders.where(anders.HIP==hip)
    vfoo = line.V[0]
    if len(vfoo)>0.:
        vfoo = float(line.V[0])
    return [vfoo]

def wxwx(hip):
    line = anders.where(anders.HIP==hip)
    wfoo = line.W[0]
    if len(wfoo)>0.:
        wfoo = float(line.W[0])
    return [wfoo]

def thickOrthin(hip):
    if (not uxux(hip)[0]=='' and not vxvx(hip)[0]=='' and not wxwx(hip)[0]==''):
        hips_u = uxux(hip)[0]
        hips_v = vxvx(hip)[0]
        hips_w = wxwx(hip)[0]
        kd = 1./((2.*pi)**1.5*35.*20.*16.)  #Calculations from Benbsy et al. (2003)
        ktd = 1./((2.*pi)**1.5*67.*38.*35.)
        ud = (hips_u)**2./(2.*35.**2.)
        vd = ((hips_v+15.)**2.)/(2.*20.**2.)
        wd = (hips_w)**2./(2.*16.**2.)
        ffd = kd*exp(-ud-vd-wd)
        #
        utd = (hips_u)**2./(2.*67.**2.)
        vtd = ((hips_v+36.)**2.)/(2.*38.**2.)
        wtd = (hips_w)**2./(2.*35.**2.)
        fftd = ktd*exp(-utd-vtd-wtd)
        #
        td_d = ((0.18/0.82)*(fftd/ffd))  #Value changed to match Adibekyan et al. (2013)
        if td_d > 10.:
            disk = "thick"
        else:
            disk = "thin"
    else:
        disk = "N/A"
    return disk

def hdname(hip):
    line = hipnames.where(hipnames.HIP==hip)
    hhdd = line.HD[0]
    if len(hhdd)==1.:
        hhdd = line.HD
    return [hhdd]

def bdname(hip):
    line = hipnames.where(hipnames.HIP==hip)
    bbdd = str(line.BD[0])
    if len(bbdd)==1.:
        bbdd = line.BD
    return [bbdd]


def velo(hip):
    line = exo.where(exo.HIPP==str(hip))
    if len(line.VSINI)==0:
        vsini = 999.
    elif line.VSINI[0]=='':
        vsini = 999.
    else:
        vsini = float(line.VSINI[0]) #[0][8]
    return [vsini]

def tee(hip):
    line = exo.where(exo.HIPP==str(hip))
    if len(line.TEFF)==0:
        ttt = 9999.
    elif line.TEFF[0]=='':
        ttt= 9999.
    else:
        ttt = float(line.TEFF[0]) #[0][5]
    return [ttt]

def loog(hip):
    line = exo.where(exo.HIPP==str(hip))
    if len(line.LOGG)==0:
        ggg = 9.99
    elif line.LOGG[0]=='':
        ggg = 9.99
    else:
        ggg = float(line.LOGG[0]) #[0][6]
    return [ggg]

def smasss(hip):
    line = exo.where(exo.HIPP==str(hip))
    if len(line.MSTAR)==0:
        smsm = 999.
    elif line.MSTAR[0]=='':
        smsm = 999.
    else:
        smsm = line.MSTAR[0] #[0][7]
    return [smsm]

def mull(hip):
    line = exo.where(exo.HIPP==str(hip))
    if len(line.MULT)==0:
        mpmp = 2
    else:
        mpmp = int(line.MULT[0])
    return [mpmp]

class Star():
    def __init__(self,hip,hd=None,bd=None,hr=None):
        self.hip = hip
        self.hd = hdname(hip)
        self.bd = bdname(hip)
        self.hr = hr
        self.radec = defRD(hip)
        self.pos = calcPos(hip)
        self.dist = calcDist(hip)
        self.spec = Type(hip)
        self.bv = color(hip)
        self.appv = appmag(hip)
        self.u = uxux(hip)
        self.v = vxvx(hip)
        self.w = wxwx(hip)
        self.disk = thickOrthin(hip)
        self.abundances = []
        if starlist=='exo' or starlist=='exoplanet' or starlist=='exoplanets':
            self.smass = smasss(hip)
            self.vel = velo(hip)
            self.teff = tee(hip)
            self.logg = loog(hip)
            self.multi = mull(hip)
            self.planets = []
    def __str__(self):
        return "Star: hip=%d"%self.hip  #print star by name
    def longDescription(self):
        description = "Star: hip=%s\n"%self.hip #print star by name
        description += "hd = %s\n" % self.hd[0]
        description += "bd = %s\n" % self.bd[0]
        description += ("Spec Type = %s\n" % self.spec[0] )
        description += ("Vmag = %s\n" % self.appv[0] )
        description += ("dist (pc) = %.2f \n" % self.dist[0] )
        description += ("RA/Dec = (%.2f,%.2f)\n" % (self.radec[0],self.radec[1]) )
        description += "Disk component: %s\n" % self.disk
        if starlist=='exo' or starlist=='exoplanet' or starlist=='exoplanets':
            description += ("B-V, mass(M_S) = %s, %s\n" % (self.bv[0][0], self.smass[0]) )
            description += ("Teff, logg = %s, %s \n" % (self.teff[0], self.logg[0]) )
            description += ("Vsini (km/s) = %s\n" % self.vel[0] )
            for a in self.planets:
                description += a.__str__() + "\n"  #also
        for b in self.abundances:
            description += b.__str__() + "\n"
        return description

class AbundanceData():
    def __init__(self,name,value,ref):
        self.name = name
        self.value = value
        self.ref = ref
    def __str__(self):
        return "%s %g [%s]" % (self.name, self.value, self.ref)


class PlanetData():
    def __init__(self,letter,pmass,period,ecc,sma):
        self.letter = letter
        self.pmass = pmass
        self.period = period
        self.ecc = ecc
        self.sma = sma
    def __str__(self):
        return "[%s] %s(Mj) %s(days) e=%s %s(AU)" % (self.letter, self.pmass, self.period, self.ecc, self.sma)

hipList = []


def findOrCreate(hip):
    starSearch = [x for x in hipList if x.hip==hip]
    if len(starSearch)==1:  #star exists
        star=starSearch[0]
    else:              #new star
        star = Star(hip=hip)
        if abs(star.dist[0]) > hypatia_dist_cutoff:  #take out those stars too far away
            None
        else:    #stars that are close
            if not star.spec=='':   #that have a spectral type
                if star.spec[0][0] in spec_type_cuts:  #take out if giants
                    None
                else:   #keep the dwarfs
                    if not (star.hip in all_hipnums or star.hd in all_hdnums or star.bd in all_bdnums): #star not in starlist
                        None
                    else:  #star in starlist
                        hipList.append(star)
                        if starlist=='exo' or starlist=='exoplanet' or starlist=='exoplanets':
                            line = exo.where(exo.HIPP==str(hip))
                            for ii in range(len(line)):
                                star.planets.append(PlanetData(line.NAME[ii][-1],float(line.MSINI[ii]),float(line.PER[ii]),float(line.ECC[ii]),float(line.A[ii])))
            else:
                None
    return star

els = []  # record all of the elements in the catalog

#--------------------------BEGIN DEFINITIONS/MODULES--------------------------------------#
# NOTE NOTE NOTE NOTE NOTE
# When a catalog is read into python and there are null entries, it is converted into
# "0.0".  This is indistinguishable from when an entry is actually measured as 0.0 or
# the solar value.  To be as rigorous as possible, each catalog would need to be altered
# such that every null value is "99.99."  The criteria for adding to star.abundances would
# need to be changed here, also, since non are going to be ''.  This has not been done and
# for the moment, any entry equal 0.0 is not included.

#
# This routine renormalizes the abundances, using the solar values of Lodders '09 or
# Asplund '09, depending on which is being referenced as the denominator.  Note
# that when there was an ionized element, the same abundance was used as for the neutral
# element.  Also, when changing between catalogs, go back and double check by hand since
# there are a lot of exceptions.
#


def oneStar(hip):
    if not hdname(hip)[0]=='':
        if isinstance(hdname(hip)[0], numpy.ndarray):
            starhd = numpy.asscalar(hdname(hip)[0])
        else:
            starhd = int(hdname(hip)[0])
    else:
        starhd = 999999
    starbd = bdname(hip)[0]
    return hip, starhd, starbd

def HDStars(in_good_hdinds, columnName, cat):
    out_good_hiphdnums = []
    for jj,u in enumerate(in_good_hdinds): #where both the hd and hr exist in the cat table
        if isinstance(columnName[u], str):
            hd = str(columnName[u].rstrip("A").strip("HD").replace(" ", ""))
        else:
            hd = str(columnName[u])
        temp = numpy.where(hipnames.HD == hd)[0][0]
        out_good_hiphdnums.append(hipnames.HIP[temp])
    out_tab = cat[in_good_hdinds]
    return out_good_hiphdnums, out_tab

def HIPStars(in_good_hipinds, columnName, cat):  #for when HIP stars are primary but mixed in
    out_good_hipnums = []
    for jj,u in enumerate(in_good_hipinds): #where both the hd and hr exist in the cat table
        hip = int(columnName[u].rstrip("A").strip("HIP").replace(" ", ""))
        out_good_hipnums.append(hip)
    out_tab = cat[in_good_hipinds]
    return out_good_hipnums, out_tab

def BDStars(in_good_bdinds, columnName, cat):
    out_good_hipbdnums = []
    for jj,u in enumerate(in_good_bdinds): #where both the hd and hr exist in the cat table
        bd = columnName[u].replace("D", "") #hipparcos naming scheme has no "D"
        temp = numpy.where(hipnames.BD == bd)[0][0]
        out_good_hipbdnums.append(hipnames.HIP[temp])
    out_tab = cat[in_good_bdinds]
    return out_good_hipbdnums, out_tab

def HRStars(in_good_hdhrinds, columnName, cat):
    out_good_hiphrnums = []
    for jj,u in enumerate(in_good_hdhrinds): #where both the hd and hr exist in the cat table
        if isinstance(columnName[u], str):
            hr = int(columnName[u].strip("HR").replace(" ", ""))
        else:
            hr = int(columnName[u])
        hdd = [v for k,v in hd_from_hr.iteritems() if k==hr]
        hdd = hdd[0]
        temp = numpy.where(hipnames.HD == str(hdd))[0][0]
        out_good_hiphrnums.append(hipnames.HIP[temp])
    out_tab = cat[in_good_hdhrinds]
    return out_good_hiphrnums, out_tab

def TYCStars(in_good_tycinds, columnName, cat):
    out_good_hiptycnums = []
    for jj,u in enumerate(in_good_tycinds): #where both the hd and hr exist in the cat table
        if isinstance(columnName[u], str):
            tyc = str(columnName[u].strip("TYC").replace('-',' '))
        else:
            tyc = str(columnName[u])
        temp = numpy.where(tycho.tycho == tyc)[0][0]
        out_good_hiptycnums.append(tycho.hip[temp])
    out_tab = cat[in_good_tycinds]
    return out_good_hiptycnums, out_tab

#------------------

def starPipe(out_good_hipnums, out_tab, subtract_iron, iron_index, solar_index, outputName, elem_list, NLTE_inds = None, dup_inds = None, solar_norm_index = TOTsolar_norm_index):
    if solar_norm_index == '': solar_norm_index = solar_index #to unnorm, see topf
    out_hip_rows = [tuple([x]+list(y)) for x,y in zip(out_good_hipnums,out_tab)]
    for ii in range(len(out_hip_rows)):
        hip = out_hip_rows[ii][0]
        starvals = []
        for jj, name in enumerate(elem_list):
            if (NLTE_inds and jj in NLTE_inds): name = name.rstrip(" (NLTE)")
            if subtract_iron=="Y":  #ensure that Fe exists
                iron = out_hip_rows[ii][iron_index+2]
                iron = iron+( solar[name.rstrip("H")][solar_index]-solar[name.rstrip("H")][solar_norm_index] )
                x = out_hip_rows[ii][jj+2]+out_hip_rows[ii][iron_index+2]
                x = x+( solar[name.rstrip("H")][solar_index]-solar[name.rstrip("H")][solar_norm_index] )
                if jj==iron_index: x = iron #so iron x 2 isn't produced
            else:
                #print hip, len(out_hip_rows), ii, len(out_hip_rows[ii]), iron_index+2
                iron = out_hip_rows[ii][iron_index+2] #ensure that Fe exists
                iron = iron+( solar[name.rstrip("H")][solar_index]-solar[name.rstrip("H")][solar_norm_index] )
                x = out_hip_rows[ii][jj+2]
                x = x+( solar[name.rstrip("H")][solar_index]-solar[name.rstrip("H")][solar_norm_index] )
            if (dup_inds and ii in dup_inds): iron = 99.99
            if not (x>90. or iron > 90.):
                starvals.append(x)
                starname = oneStar(hip)
                #print hip, name, x, iron, outputName, starvals
                if (NLTE_inds and jj in NLTE_inds): name = name+" (NLTE)"
                if (hip in all_hipnums or starname[1] in all_hdnums or starname[2] in all_bdnums):
                    star = findOrCreate(hip)
                    els.append(name)
                    star.abundances.append(AbundanceData(name,x,outputName))
                    #print len(hipList)
                    currentList = [v.hip for kk, v in enumerate(hipList)]
            if (jj==len(elem_list)-1 and len(starvals)==1 and hip in currentList): #catch when there is only an iron measurement and all others are blank - note this will not remove the star entry in hipList
                hiptemp = where(array([v.hip for mm, v in enumerate(hipList)])==hip)[0][0]
                cattemp = where(array([w.ref for nn, w in enumerate(hipList[hiptemp].abundances)])==outputName)[0][0]
                del hipList[hiptemp].abundances[cattemp]

def singleStarPipe(hip, table, catalog_index, solar_index, outputName, elem_list, solar_norm_index = TOTsolar_norm_index):
    if solar_norm_index == '': solar_norm_index = solar_index
    starname = oneStar(hip)
    if (hip in all_hipnums or starname[1] in all_hdnums or starname[2] in all_bdnums):
        star = findOrCreate(hip)
        for jj,name in enumerate(elem_list):
            x = table[catalog_index][jj+1]
            if not x > 90.: x = x+( solar[name.rstrip("H")][solar_index]-solar[name.rstrip("H")][solar_norm_index])
            star.abundances.append(AbundanceData(name,x,outputName))
            els.append(name)

#--------------------------END DEFINITIONS/MODULES----------------------------------------#
#
# REMEMBER TO PUT IN THE CORRECT SOLAR NORMALIZATION AND TURN OFF TOTSOLAR_NORM_INDEX FROM ''


mish15 = atpy.Table("abundance_data3/mishenina15.csv", type="ascii", delimiter=",")
mish15 = atpy.Table("abundance_data3/mishenina15.csv", type="ascii", delimiter=",")
mish15_hdinds = numpy.array([ii for ii,v in enumerate(mish15.Star) if ("HD" in v and not "B" in v)])
mish15_hdnums = numpy.array([int(mish15.Star[ii].strip("HD")) for ii in mish15_hdinds])
mish15_good_hdinds = numpy.array([mish15_hdinds[ii] for ii,v in enumerate(mish15_hdnums) if v in all_hdnums])
mish15_good_hdnums = numpy.intersect1d(mish15_hdnums, all_hdnums)


mish15_hdtab = HDStars(mish15_good_hdinds, mish15.Star, mish15)
mish15_class = starPipe(mish15_hdtab[0], mish15_hdtab[1], "Y", 0, 3, "Mishenina et al. (2015)", ["FeH", "MnH"])


#--------------------------------------END CATALOGS_-------------------------------------#

#Remove any stars where FeH is the only abundance
hipList = [star for star in hipList if len(star.abundances) > 1]

for star in hipList:
    print star.longDescription()

if starlist=='exo' or starlist=='exoplanet' or starlist=='exoplanets':
    exoList = []
    exoList = hipList
    speak = 'Natalie, you are awesome.  There are '+str(len(exoList))+'x o planet host stars.'


print "There are a total of", len(hipList), "stars"
print
print "You are doing good."

print now1
print datetime.datetime.now()

subprocess.call(['say',speak])
