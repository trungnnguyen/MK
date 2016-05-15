"""
"""
import matplotlib as mpl
mpl.use('Agg') ## In case X-window is not available.

## running multithreaded mk runs
def read(fn):
    f    = float(fn.split('mk-f')[1].split('-psi')[0])*1e-3
    psi0 = float(fn.split('psi')[1].split('-th')[0])
    th   = float(fn.split('-th')[1][:6])
    with open(fn) as FO:
        data_line = FO.readlines()[1]
        elements = data_line.split()
    return map(float, elements),f,psi0,th, data_line

def pp(masterFileName):
    """
    Argument
    --------
    masterFileName
    """
    import numpy as np
    numFail=0
    fileFail=[]

    fileFLDall = open('allFLD.txt','w')
    fileFLDmin = open('minFLD.txt','w')

    with open(masterFileName) as FO:
        blocks = FO.read().split('--\n')[:-1:]
        dat_min_master=[]
        print 'number of blocks',len(blocks)
        for i in xrange(len(blocks)): ## each block
            eachBlock = blocks[i]
            linesInBlock = eachBlock.split('\n')[0:-1:]
            print linesInBlock

            ## find the minimum |(E1,E2)|
            min_rad =1.5
            dat_min = None
            data_min_line = None
            # print linesInBlock

            for j in xrange(len(linesInBlock)):
                line = linesInBlock[j]
                ind, fn = line.split()
                try:
                    data, f, psi0, th, data_line = read(fn)
                except:
                    pass
                else:
                    fileFLDall.write('%s'%data_line)
                    epsRD, epsTD, psi0, psif, \
                        sigRD,sigTD,sigA,T,dt = data[:9]

                    if np.isnan(epsRD) or np.isnan(epsTD):
                        fileFail.append(fn)
                        numFail=numFail+1
                        pass
                    else:
                        rad = np.sqrt(epsRD**2+epsTD**2)
                        if rad<min_rad:
                            data_min = data[::]
                            min_rad = rad
                            data_min_line = data_line

            dat_min_master.append(dat_min)
            if type(data_min_line).__name__!='NoneType':
                fileFLDmin.write('%s'%data_min_line)

    fileFLDall.close(); fileFLDmin.close()

    print 'numFail:',numFail
    print 'FileFail:'
    for i in xrange(numFail):
        print fileFail[i]

    ## iplot?
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(7,3))

    ax1=fig.add_subplot(121)
    ax2=fig.add_subplot(122)
    dat=np.loadtxt(fileFLDmin.name).T
    ax1.plot(dat[1],dat[0],'o')
    dat=np.loadtxt(fileFLDall.name).T
    ax2.plot(dat[1],dat[0],'o')
    fig.savefig('mk_fld_pp.pdf')

def test_pp(fn='/local_scratch/MK-6e59e6-results.txt'):
    pp(fn)

def makeCommands(f0,psi0,th,logFileName):
    """
    Arguments
    ---------
    f0
    psi0
    th
    logFileName
    """
    from lib      import gen_tempfile
    # stdoutFileName = gen_tempfile(
    #     prefix='stdout-mkrun')
    stdoutFileName ='/tmp/dump'
    cmd = 'python mk.py --fn %s -f %5.4f -p %+6.1f -t %+7.2f > %s'%(
        logFileName,f0,psi0,th,stdoutFileName)
    # print 'cmd:',cmd
    return cmd

def test_run():
    run(f0=0.995,psi0=0.,th=0.,logFileName='dum')

def run(*args):
    import os,subprocess
    cmd = makeCommands(*args)
    os.system(cmd)
    return cmd

def prepRun(*args):
    import os,subprocess
    cmd = makeCommands(*args)
    return cmd

if __name__=='__main__':
    import numpy as np
    from mk import main as mk_main
    from lib import gen_tempfile, rhos2ths
    import os,multiprocessing,time
    from MP import progress_bar
    from mk_paths import findCorrectPsi
    uet = progress_bar.update_elapsed_time

    ## rho to theta? ( should be later passed as arguments)
    f0 = 0.996
    rhos = np.linspace(-0.6,1.,17)
    ths  = rhos2ths(rhos)

    ths=[0] ## to debug

    logFileNames=[]
    k=0
    print '%3s %6s %5s %5s %60s'%('k','rho','th','psi0','logFileName')
    p0s=[]
    print '---'
    for i in xrange(len(ths)): ## each rho
        _psi0s_=findCorrectPsi(ths[i])
        p0s.append(_psi0s_)
        logFileNames.append([])
        for j in xrange(len(_psi0s_)):
            psi0 = _psi0s_[j]
            logFileName = gen_tempfile(
                prefix='mk-f0%3.3i-psi%+6.3f-th%+6.3f'%(
                    int(f0*1e3),psi0,ths[i]),
                affix='log',i=(i*10000+j))
            logFileNames[i].append(logFileName)
            k=k+1
            print '%3i %6.2f %5.1f %5.1f %60s'%(
                k, rhos[i], ths[i]*180/np.pi, psi0*180/np.pi,logFileName)
            pass
        print '-'*83
        pass

    ncpu  = multiprocessing.cpu_count()
    pool  = multiprocessing.Pool(processes=ncpu)

    results = []
    for i in xrange(len(ths)):
        results.append([])
        for j in xrange(len(p0s[i])):
            psi0 = p0s[i][j]
            r=pool.apply_async(
                func=run,
                args=(f0,
                      psi0*180/np.pi,
                      ths[i]*180/np.pi,
                      logFileNames[i][j]))
            results[i].append(r)
            pass
        pass

    t0 = time.time()
    pool.close(); pool.join(); pool.terminate()
    wallClockTime = time.time()-t0

    ## end of calculation
    rstFileName = gen_tempfile(prefix='MK',affix='results')
    with open(rstFileName,'w') as rstFile:
        for i in xrange(len(results)): ## paths
            for j in xrange(len(results[i])): ## psi0s
                cmd = results[i][j].get()
                logFN = logFileNames[i][j]
                rstFile.write('%i %s\n'%(j,logFN))
                logFileNames.append(logFN)
            rstFile.write('--\n')
            pass
        pass

    for i in xrange(len(logFileNames)):
        print '%4.4i   %s'%(i,logFileNames[i])

    uet(wallClockTime,'Total wallclocktime:');print
    print 'All results are saved to %s'%rstFileName
    pp(rstFileName)
    print 'Fin --'
