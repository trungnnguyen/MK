"""
Example of cpb iso Cazacu et al., IJP (2006) 1171-1194
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy.optimize
import mk.library.lib

def eq4(S,a,k):
    """
    Eq4 in Cazacu et al.
    F=(|S_1|-k*S_1)**a + (|S_2|-k*S_2)**a +(|S_3|-k*S_3)**a
    with S_i, i.e., the principal values of the stress deviator.

    F: the size of the yield locus (should be a constant for any
      stress state that meets the given yield condition)

    F is the homogeneous function of degree a.


    *** if S is given as the 'transformed' stress,
    Eq (9) is obtained.

    Arguments
    ---------
    S
    a
    k

    Returns
    -------
    F
    """
    ## Find principal values of sigma1, sigma2
    sig,dum = mk.library.lib.convert_6sig_princ(S)
    sig=np.sort(sig)[::-1] ## descending order (large to small)
    f = 0.
    for i in xrange(len(sig)):
        f = f + (np.abs(sig[i])-k*sig[i])**a
    return f

def eq5a(a,k):
    """
    Calculate ratio of tension to compression yield stress
    using the exponent a and parameter k

    Arguments
    ---------
    a
    k

    Returns
    -------
    tension to compression ratio (left-hand-side of Eq 5a)
    """
    p1=2./3.
    p2=1./3.
    rst =(( (p1*(1+k))**a+2*(p2*(1-k))**a )/  \
          ( (p1*(1-k))**a+2*(p2*(1+k))**a )  )\
          **(1./a)
    return rst

def eq5b(x,a):
    """
    Convert tension/compression ratio (x) to k
    with the given value of exponent a

    Arguments
    ---------
    x
    a

    Returns
    -------
    k
    """
    h = eq5c(x,a)
    k = (1-h)/(1+h)
    return k

def eq5c(x,a):
    """
    Convert tension/compression ratio (x) to
    obtain h(value)

    Arguments
    ---------
    x
    a

    Returns
    -------
    h (the left-hand-side of Eq 5c)
    """
    return ((2.**a - 2.*(x**a)) / ( (2*x)**a - 2   )) **(1./a)



def main(s=[1,0,0,0,0,0],a=4,k=0.):
    """
    Argument
    --------
    s=[1,0,0,0,0,0]
    a
    k
    """
    import cpb_lib
    if type(s).__name__=='ndarray':
        S=s.copy()
    else:
        S=np.array(s,dtype='float')
    Sdev = cpb_lib.deviator(S)

    f=eq4(S=Sdev.copy(),a=a,k=k)
    f1=(f)**(1./a)
    # Sdev2 = cpb_lib.deviator(S.copy()/f1)
    # f2=eq4(Sdev2.copy(),a=a,k=k)
    # print 'f2:',f2

    return S.copy()/f1

def ut(**kwargs):
    s=np.array([1.,0.,0.,0.,0.,0.])
    newStress = main(s,**kwargs)
    return newStress[0]

def locus(yfunc=main,nth=100,iplot=False,**kwargs):
    """
    in-plane biaxial locus using cpb_iso.main

    Argument
    --------
    yfunc
    nth = 100
    iplot
    **kwargs
    """
    import numpy as np
    pi = np.pi
    cos=np.cos
    sin=np.sin
    th=np.linspace(-pi,pi,nth)
    x=cos(th); y=sin(th)
    z=np.zeros(len(th))
    s=np.array([x,y,z,z,z,z]).T
    fs=[]; fsinv=[]
    sigma=[]
    X=np.zeros(len(s))
    Y=np.zeros(len(s))
    for i in xrange(len(s)):
        newStress  = yfunc(s[i].copy(),**kwargs)
        X[i]=newStress[0]
        Y[i]=newStress[1]

    fs=np.array(fs)
    fsinv=np.array(fsinv)

    if iplot:
        ft=dict(fontsize=18)
        fig=plt.figure()
        ax1=fig.add_subplot(121)
        ax1.plot(X,Y)
        ax1.set_xlabel(r'$\bar{\Sigma}_{RD}$',ft)
        ax1.set_ylabel(r'$\bar{\Sigma}_{TD}$',ft)
        ax1.grid('on')
        ax1.set_aspect('equal')
        ax1.set_xlim(-2.0,3.0); ax1.set_ylim(-2.0,3.0)
        ticks=np.linspace(-2,3,6)
        ax1.set_xticks(ticks)
        ax1.set_yticks(ticks)
        fig.savefig('cpb_iso_locus.pdf',bbox_inches='tight')
        pass
    return X,Y

if __name__=='__main__':
    locus()
