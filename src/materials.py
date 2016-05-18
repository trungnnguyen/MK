## Collection of materials
from constitutive import Constitutive
from func_hard_for import return_swift
from yf2 import wrapHill48R, VonMises

def IFsteel():
    """
    Return constitutive description for
    IF steel parameters
    """
    ## hardening model
    f_hrd = return_swift(n=0.28985,m=5e-2, ks=518.968, e0=0.0007648, qq=1e3)
    ## yield function
    f_yld = wrapHill48R([2.2, 2.0, 2.9]) # r0, r45, r90
    return Constitutive(f_yld=f_yld, f_hrd=f_hrd)

def IsoMat():
    """
    Return constitutive description for
    Isotropic von Mises material
    """
    ## hardening model
    f_hrd = return_swift(n=0.28985,m=5e-2,ks=518.968,e0=0.0007648,qq=1e3)
    ## yield function
    f_yld = VonMises
    return Constitutive(f_yld=f_yld, f_hrd=f_hrd)