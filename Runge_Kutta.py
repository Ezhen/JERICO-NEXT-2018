from pylab import *
from netCDF4 import Dataset
from numpy.linalg import inv

# The goal is to compute different drigter trajectories and see, how the flow field will very

latmin = 70 #100
latmax = 240 #200
lonmin = 250 #75
lonmax = 450 #150

n = Dataset('/home/evgeny/Downloads/sv04-med-ingv-cur-an-fc-h_1531404445014.nc', 'r', format='NETCDF4')
lon = n.variables['lon'][lonmin:lonmax]
lat = n.variables['lat'][latmin:latmax]
uu = n.variables['uo'][0,0,latmin:latmax,lonmin:lonmax]
vv = n.variables['vo'][0,0,latmin:latmax,lonmin:lonmax]

def distance_func(lat0,lat1,lon0,lon1):
	# https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
	R = 6373.0

	lat1 = np.radians(lat0)
	lon1 = np.radians(lon0)
	lat2 = np.radians(lat1)
	lon2 = np.radians(lon1)

	dlon = lon2 - lon1
	dlat = lat2 - lat1

	a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
	c = 2 * np.atan2(np.sqrt(a), np.sqrt(1 - a))

	distance = R * c
	return distance


# put them on the cetner of the grid cells

u = (uu[1:-1,0:-1]+uu[1:-1,1:])/2.
v = (vv[1:,1:-1]+vv[0:-1,1:-1])/2.


def pt():
	lats,lons = np.meshgrid(lat,lon)
	#quiver(lats[::3],lons[::3],uu[::3,::3],vv[::3,::3])
	plot(x_free[1,:],x_free[0,:], label='no correction')
	ylim(lat.min(),lat.max()); xlim(lon.min(),lon.max())
	#scatter(x_pos[0,:],x_pos[1,:],s=155,c = P[0,0,:]+P[1,1,:], cmap='rainbow',edgecolors = None)
	#colorbar()
	#legend(loc=1)
	show()


def crd(lat_t,lon_t):
	fract_j = (lon_t-lon[0])/(lon[1]-lon[0])
	fract_i = (lat_t-lat[0])/(lat[1]-lat[0])
	i,j = floor(fract_i),floor(fract_j)
	di,dj = fract_i-i,fract_j-j
	#print(i,j,di,dj,fract_i,fract_j)
	return i,j,di,dj

def vel(t, x):
	# check if a tracer still inside the domain
	if x[1]>lon.max() or x[0]>lat.max() or x[1]<lon.min() or x[0]<lat.min():
		return array([0,0])
	i,j,di,dj = crd(x[0],x[1])
	j,i,dj,di = int(j),int(i),int(dj),int(di)
	u00,u10,u01,u11 = u[i,j],u[i+1,j],u[i,j+1],u[i+1,j+1]
	ub = u00 + di * (u10-u00) 
	ut = u10 + di * (u11-u10) 
	ui = ub + dj * (ut - ub)
	v00,v10,v01,v11 = v[i,j],v[i+1,j],v[i,j+1],v[i+1,j+1]
	vb = v00 + di * (v10-v00) 
	vt = v10 + di * (v11-v10) 
	vi = vb + dj * (vt - vb)
	ui = ui / np.cos(np.deg2rad(x[0])) / 1.11e5
	vi = vi / 1.11e5
	#print ui,vi
	return array([ui,vi])
	
# define runge-kutta function	
def rgk(x, t, dt):
	xp = x + dt * vel(t,x) / 2. 
	x = x + dt * vel(t,xp)
	print(t,x)
	return x

# initialization
dt = 100 	# s
n_it = 2340 	# number of iterations

# declaration of array for a priori quantities
x_free = np.zeros((2,n_it)) # free
x_free[:,0] = [36.3,14.3]

for i in range(1,n_it):
	# calculation  of free x
	x_free[:,i] = rgk(x_free[:,i-1], i, dt)


	
	


