import shutil
import argparse
import os
import numpy as np
#from yt.mods import * # depricated in yt3
import yt
import matplotlib.colorbar as cb
import glob
import sys

def particle_ID_locations(sinkfile, current_item) :
	try : 
		ID, mass, rstar, xstar, ystar, zstar = np.loadtxt( sinkfile, usecols=[0,1,2,3,4,5], unpack=True, skiprows=3, comments="=")
	except ValueError : 
		pass
	return ID[current_item], mass[current_item], xstar[current_item], ystar[current_item], zstar[current_item]

def Fullprojection_plotting(pf):
	fileout="{0}_{1:05d}_fullprojection.{2}".format(plot_out_prefix, i, out_format)
	print "Doing a projection plot of the Full Box."
	p = yt.ProjectionPlot(pf, "z", "density")
	p.set_zlim("density", 1e-3 , 1e0)
	if(withParticles) :
		print 'Annotating particles now'
		p.annotate_particles(width = (16, 'pc'))
		fileout="{0}_{1:05d}_fullprojection_particle.{2}".format(plot_out_prefix, i, out_format)
	p.set_font({'size':25})
	p.set_colorbar_label("Density", "$\\Sigma\\,({\\rm g\\,cm}^{-2})$")
	print fileout
	p.save(fileout)


def Projection_plotting(pf, ParticleID, part_center, zoom_width=2):
	#plot_field = 'velocity' + plot_axis
	plot_field = 'density'

	#p = yt.ProjectionPlot(pf, plot_axis, plot_field, weight_field = 'density', center = (xc, yc, zc), width = (zoom_width, 'pc'))
	# CODE UNITS ARE ASSUMED FOR Center!
	p = yt.ProjectionPlot(pf, plot_axis, plot_field, center = part_center, width = (zoom_width, 'pc'))
	#p.set_zlim("Density", 1e-23 , 1e-14)
	#pid = os.getpid()
	p.set_font({'size':25})
	if(withParticles) :
		p.annotate_particles(width = (zoom_width, 'pc'))
	p.set_colorbar_label("Density", "$\\Sigma\\,({\\rm g\\,cm}^{-2})$")
	fileout="{0}_{1:05d}_{2}_{3}_{4}pc_{5}.{6}".format(plot_out_prefix, i, plot_axis, plot_field, zoom_width, ParticleID, out_format)
	print fileout
	p.save(fileout)


def Slice(pf, ParticleID, part_center, zoom_width=2.0) :
#	sp = pf.h.sphere([xc, yc, zc], (zoom_width + 0.5, "pc"))
	sp = pf.h.sphere(part_center, (zoom_width + 0.5, "pc"))
	# Get the angular momentum vector for the sphere. # Currently nan nan nan.
	L = sp.quantities.angular_momentum_vector()
	orthog_to_L_1 = np.array([L[2], L[2], -L[0]-L[1]])
	orthog_to_L_2 = np.array([L[1], -L[0]-L[2], L[1]])
	print L
	#print np.dot(L, orthog_to_L_1)
	#print np.dot(L, orthog_to_L_2)
	# Create an OffAxisSlicePlot on the object with the L vector as its normal
	plot_field = 'density'
	#plot_field = 'VelocityMagnitude'
	# What axis do we plot along?
	Axis_to_plot = L
#	p = yt.OffAxisSlicePlot(pf, Axis_to_plot, plot_field, center=sp.center, width=(zoom_width, "pc"))
	p = yt.OffAxisSlicePlot(pf, Axis_to_plot, plot_field, center=part_center, width=(zoom_width, "pc"))
	p.set_cmap(field="density", cmap='bds_highcontrast')#yt2 default cmap
	p.set_zlim("density", 1e-23,1e-14)
	p.set_font({'size':25})
	if(withArrows):
		#p.annotate_velocity(factor=16)
#		#v_vector_bulk=pf.h.disk([xc, yc, zc], Axis_to_plot, (1e-2, "pc"), (0.001, "pc")).quantities["BulkVelocity"]()
#		v_vector_bulk=pf.h.sphere(part_center, (2e-2, "pc")).quantities["BulkVelocity"]()
#		p = yt.OffAxisSlicePlot(pf, Axis_to_plot, plot_field, sp.center, (zoom_width, "pc"), field_parameters={"bulk_velocity": v_vector_bulk})
#		#p.set_zlim("Density", 1e-23,1e-14
#		p.set_cmap(field="density", cmap='bds_highcontrast')
#		p.set_zlim("density", 1e-23,1e-14)
#		#p.annotate_cquiver('CuttingPlaneVelocityX', 'CuttingPlaneVelocityY', 12)# yt2
#		p.annotate_cquiver('cutting_plane_velocity_x', 'cutting_plane_velocity_y', 20)# yt3
		p.annotate_contour("density")
        fileout="{0}_{1:05d}_{2}_{3}pc_{4}.{5}".format(plot_out_prefix, i, plot_field, zoom_width, ParticleID, out_format)
	print fileout
        p.save(name=fileout)


parser = argparse.ArgumentParser(description = "start number to end number, step size, zoom width, plot axis and optional particle ID")
parser.add_argument('start', metavar='N1', type=int)
parser.add_argument('end', metavar='N2', type=int)
parser.add_argument('step', metavar='N3', type=int)
parser.add_argument('ParticleID', metavar='N4', type=int, nargs='?', default=42, help='Particle ID you want to reduce.')
parser.add_argument('zoom_width', metavar='N5', type=float, nargs='?', default=3.0, help='width of the plot in parsecs.')
parser.add_argument('plot_axis', metavar='axis_', type=str, nargs='?', default='z', help='Axis along which to project/slice')
parser.add_argument('--particle', action='store_true')
parser.add_argument('--noparticle', action='store_true')
parser.add_argument('--location', action='store_true')
# What kind of visualization do we want?
parser.add_argument('--project', action='store_true')
parser.add_argument('--projectfull', action='store_true')
parser.add_argument('--slice', action='store_true')
parser.add_argument('--arrow', action='store_true')
parser.add_argument('--allparticles', action='store_true')
parser.add_argument('--pdf', action='store_true')
#parser.add_argument('--parsec', metavar='N4', action='store_true')
args = parser.parse_args()
zoom_width = args.zoom_width
withParticles=args.particle
withNoParticles = args.noparticle
withProjection=args.project
withProjectionFull=args.projectfull
withLocationSpecified=args.location
withParticleIDValue = args.ParticleID
withAllParticles = args.allparticles
withSlice=args.slice
withArrows=args.arrow
plot_axis = args.plot_axis
withPDF = args.pdf

prefix = 'output'
plot_out_prefix = 'movieframe'

if (withPDF):
	out_format = 'pdf'
else:
	out_format = 'png'

for i in range(args.start,args.end,args.step) :
	if not glob.glob("{0}_{1:05d}".format(prefix, i)):
		continue
	print 'On Folder: {0}_{1:05d}'.format(prefix, i)
	file = '{0}_{1:05d}/info_{1:05d}.txt'.format(prefix, i)
	sinkfile = "{0}_{1:05d}/sink_{1:05d}.info".format(prefix, i)	
	if( not os.path.isfile( sinkfile)) :
		continue
 	pf = yt.load(file)
	if (withProjectionFull):
		Fullprojection_plotting(pf)
		
	try : 
		ID = np.loadtxt( sinkfile, usecols=[0], unpack=True, skiprows=3, comments="=")
	except ValueError : 
		pass
	print ID
	print type(ID)
	for current_item in range(len(ID)):	
		ParticleID, ParticleMass, xc, yc, zc = particle_ID_locations(sinkfile, current_item)
		part_center = yt.YTArray([xc, yc, zc], 'cm')
		if ParticleID == withParticleIDValue or withAllParticles:
			if (withProjection):
				Projection_plotting(pf, ParticleID, part_center, zoom_width=2.0)
			elif (withSlice):
				print 'in slice'
				Slice(pf, ParticleID, part_center, zoom_width)
print "Finished, closing up shop"
