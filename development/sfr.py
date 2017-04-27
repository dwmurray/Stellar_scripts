import shutil
import matplotlib 
matplotlib.use("Agg")
import argparse
import os
import sys
import yt
import numpy
import matplotlib.pyplot as pl
import math

parser = argparse.ArgumentParser(description = "start number to end number")

parser.add_argument('start', metavar='N1', type=int)
parser.add_argument('end', metavar='N2', type=int)
parser.add_argument('step', metavar='N3', type=int)
args = parser.parse_args()

dirs = ["ultrares/jet", "highres/jet", "highres/nojet", "medres/jet", "medres/nojet"]
labels = ["$32K^3$ jet", "$16K^3$ jet", "no jet", "$8K^3$ jet", "no jet"]
ltypes = ["solid", "solid", "dashed", "solid", "dashed"]
lweights = [6, 4, 4, 2, 2]

#dirs = ["highres/jet", "highres/nojet", "medres/jet", "medres/nojet"]
#labels = ["$16K^3$ jet", "no jet", "$8K^3$ jet", "no jet"]
#ltypes = ["solid", "dashed", "solid", "dashed"]
#lweights = [4, 4, 2, 2]

for dir, label, ltype, lw in zip(dirs,labels,ltypes,lweights): 
	first_time = True
	t_start = 0.
	tarray = []
	mtot = []
	prefix = "output_"
	for i in range(args.start,args.end,args.step) :	
		file = "{0}/{1}".format(dir,prefix)+"{0:05d}/info_{0:05d}.txt".format(i)
		sinkfile = "{0}/{1}".format(dir,prefix)+"{0:05d}/sink_{0:05d}.info".format(i)
                if( not os.path.isfile(sinkfile)) : 
			continue
                print "opening {0}".format(sinkfile)
		mass = None
		try : 
			mass, xstar, ystar, zstar = numpy.loadtxt( sinkfile, usecols=[1,2,3,4], unpack=True, skiprows=3, comments="=")
			pf = yt.load(file)
			time = pf.current_time#.convert_to_cgs()
			if( first_time and mass.size > 0) :
				t_start = time
				first_time = False
			if( not first_time) :
				mtot.append(mass.sum())
				tarray.append(time-t_start)
                                #print "time = " + str(tarray[-1]/3.15e7)
		except ValueError : 
			print sinkfile + " empty" 
	gasMass = 4.8e19**3 * 3e-22 / 2e33
	tarray = numpy.log10(tarray) 
	mtot = numpy.log10(mtot) - math.log10(gasMass)
	mtot = 1e1**mtot
	tarray = 1e1**tarray/3.1558e7
	for t, m in zip(tarray, mtot) :
		print t, m
	
	lm = numpy.log10(mtot)
        lt = numpy.log10(tarray)

	lt_min = 0.5
	lt_kink = 6.6
	lt_mask = lt[lt>lt_min]
	lm_mask = lm[lt>lt_min]
        p = numpy.polyfit( lt[lt>lt_min], lm[lt>lt_min], 1)
#        p = numpy.polyfit( lt_mask[lt_mask<lt_kink], lm_mask[lt_mask<lt_kink], 1)
#	try :
#		k = numpy.polyfit( lt[lt>lt_kink], lm[lt>lt_kink], 1)
#	except TypeError :
#		k = [0, 0]
#		pass
	pl.loglog( tarray, mtot, linewidth=lw,label="{0} $\\alpha_1={1:2.1f}$".format(label, p[0]),ls=ltype)
#	pl.loglog( tarray, mtot, linewidth=lw,label="{0} $\\alpha_1={1:2.1f}$ $\\alpha_2={2:2.1f}$".format(label, p[0], k[0]),ls=ltype)
        lt =  numpy.arange(lt_min, lt_kink, 0.1 )
	pl.loglog( 1e1**lt, 1e1**(p[0]*lt + p[1]), ls="dotted", linewidth=1,color="black")
#        ltk =  numpy.arange(lt_kink, 6.2, 0.1 )
#	pl.loglog( 1e1**ltk, 1e1**(k[0]*ltk + k[1]), ls="dotted", linewidth=1,color="black")

pl.xlim(1e5, 2e6)
#arr =  numpy.arange(2e5, 3e6, 2e5)
#pl.loglog( arr, 0.1*(arr/1e6)**2, linewidth=2, ls="dotted",label="$\\propto (t-t_*)^2$")
pl.ylim(5e-4, 0.2)
pl.xlabel("$t-t_*$ [yrs]", fontsize=20)
pl.ylabel("$M_*/M_{\\rm tot}$", fontsize=20)
pl.legend(loc="best",fontsize=15)
pl.xticks(fontsize=17)
pl.yticks(fontsize=17)

pl.savefig("sfr.pdf")
