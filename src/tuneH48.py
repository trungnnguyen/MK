"""
Tune-up parameters of Hill48 using Hill Quad

"""
from for_lib import vm
from yf2 import HillQuad,Hill48
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

from vpscyld.lib_dat import xy2rt


pi=np.pi
sin=np.sin
cos=np.cos
nth = 800

def main(r0=1.,r90=1.):
    th=np.linspace(-pi,+pi,nth)
    x=cos(th); y=sin(th)
    z=np.zeros(len(th))
    s=np.array([x,y,z,z,z,z]).T
    X=[]; Y=[]

    for i in xrange(len(s)):
        rst = HillQuad(s[i],r0=r0,r90=r90)
        ys = rst[0]
        X.append(ys[0])
        Y.append(ys[1])

    ysHQ=np.array([X,Y])
    objf = returnObj(ysHQ)

    res = minimize(fun=objf, x0=[0.5,0.5,0.5,1],method='BFGS',
                   jac=False,tol=1e-20,options=dict(maxiter=400))
    popt = res.x
    n_it = res.nit
    fopt = res.fun

    print 'popt:',popt
    f,g,h,n=popt

    print ('%6s'*4)%('f','g','h','n')
    print ('%6.3f'*4)%(f,g,h,n)
    return f,g,h,n

def returnObj(ref):
    def objfH48(xs):
        th=np.linspace(-pi,+pi,nth)
        x=cos(th); y=sin(th)
        z=np.zeros(len(th))
        s=np.array([x,y,z,z,z,z]).T
        f,g,h,n = xs

        X=[]; Y=[]
        for i in xrange(len(s)):
            rst=Hill48(s[i],f,g,h,n)
            ys = rst[0]
            X.append(ys[0])
            Y.append(ys[1])

        X=np.array(X)
        Y=np.array(Y)

        ## rst to th-r coordinate
        r,th = xy2rt(X,Y)

        R,TH = xy2rt(ref[0],ref[1])

        diff = ((r-R)**2).sum()/(len(th)-1)
        return diff
    return objfH48