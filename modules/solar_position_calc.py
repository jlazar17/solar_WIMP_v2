import numpy as np
import astropy

auToCm = 1.496e13 # conversion to cm from au

def nParameter(JD):
    return JD - 2451545.

def solarObliquity(x):
    return np.radians(23.439) + np.radians(0.0000004)*x

def g(x):
    return np.radians((557.528 + 0.9856003*x))

def L(x):
    return np.radians(280.46+0.9856474*x)

def solarLambda(L, g):
    return L + np.radians(1.915)*np.sin(g) + np.radians(0.02)*np.sin(2*g)

def solarR(g):
    return (1.00014 - 0.01671*np.cos(g) - 0.00014*np.cos(2*g))*auToCm

# Convert ecliptic coordinates to equatorial coordinates of sun following https://en.wikipedia.org/wiki/Position_of_the_Sun#Equatorial_coordinates

def rightAscension(obliquity,lamb):
    return np.arctan2(np.cos(obliquity)*np.sin(lamb),np.cos(lamb))

def equatorialDeclination(obliquity, lamb):
    return np.arcsin(np.sin(obliquity) * np.sin(lamb))

def equatorialZenith(obliquity, lamb):
    return equatorialDeclination(obliquity, lamb) + np.pi/2

# Convert equatorial coordinates to horizontal coordinates following https://en.wikipedia.org/wiki/Celestial_coordinate_system#Equatorial_%E2%86%94_horizontal


def auxilaryX(dec, latitude=-1*np.pi/2, hourAngle=0):
    return -np.sin(latitude)*np.cos(dec)*np.cos(hourAngle)+np.cos()

def azimuth(dec, latitude=-1*np.pi/2, hourAngle=0):
    pass

def altitude(eqDeclination,latitude=-1*np.pi/2,hourAngle=0):
    return np.arcsin(np.sin(eqDeclination)*np.sin(latitude) + np.cos(eqDeclination)*np.cos(latitude)*np.cos(hourAngle))

def horizontalZenith(eqDeclination,latitude=-1*np.pi/2,hourAngle=0):
    return np.pi/2 - altitude(eqDeclination,latitude=-1*np.pi/2,hourAngle=0)
