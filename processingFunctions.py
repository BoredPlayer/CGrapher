import numpy as np

def availProcMethods():
    print("plain\t\tvisualisation of singular column")
    print("QCriterion\tvisualisation of q-criterion (requires 9 derivatives)")
    print("vmag\t\tvisualisation of velocity magnitude (requires 3 velocity components)")
    print("Cfgen\t\tcalculation of friction coefficient")
    #print("average\t\tanimate in time changes of the processing function")

def findPlainAvail(vis, args=[]):
    if(len(args)<1):
        intext = input(f"Please provide index (ending with d) or name of visualised column:\n[{vis}]\n/processing plain vis > ")
    else:
        print(f"Please provide index (ending with d) or name of visualised column:\n[{vis}]\n/processing plain vis > "+args[0])
        intext = args[0]
    if(intext!=""):
        if(intext[-1]=="!"):
            try:
                vis = int(intext[:-1])
            except:
                print("Could not read column index. Falling back to default value")
        else:
            vis = intext
    return vis
    
    
def findQCriterionAvail(vis, args = []):
    if(not isinstance(vis, list)):
        vis = [None for var in range(9)]
    column_names = ["du/dx", "du/dy", "du/dz", "dv/dx", "dv/dy", "dv/dz", "dw/dx", "dw/dy", "dw/dz"]
    for i in range(9):
        if(len(args)<i+1):
            intext = input(f"Please provide index or name of {column_names[i]} column:\n[{vis[i]}]\n/processing QCriterion vis {column_names[i]} > ")
        else:
            print(f"Please provide index or name of {column_names[i]} column:\n[{vis[i]}]\n/processing QCriterion vis {column_names[i]} > "+args[i])
            intext = args[i]
        if(intext!=""):
            if(intext[-1]=="!"):
                try:
                    vis[i] = int(intext[-1])
                except:
                    print("Could not read column index. Falling back to default value")
            else:
                vis[i] = intext
    return vis

def findVMagAvail(vis, args):
    if(not isinstance(vis, list)):
        vis = [None for var in range(3)]
    column_names = ["X-velocity", "Y-velocity", "Z-velocity"]
    for i in range(3):
        if(len(args)<i+1):
            intext = input(f"Please provide index or name of {column_names[i]} column:\n[{vis[i]}]\n/processing vmag vis {column_names[i]} > ")
        else:
            print(f"Please provide index or name of {column_names[i]} column:\n[{vis[i]}]\n/processing vmag vis {column_names[i]} > "+args[i])
            intext = args[i]
        if(intext!=""):
            if(intext[-1]=="!"):
                try:
                    vis[i] = int(intext[:-1])
                except:
                    print("Could not read column index. Falling back to default value.")
            else:
                vis[i] = intext
    return vis

def findCf(vis, args):
    print("findCf")
    column_names = ["dx-velocity-dx", "dy-velocity-dx", "dx-velocity-dy", "dy-velocity-dy"]
    if(not isinstance(vis, list)):
        vis = [column_names[var] for var in range(4)]
    for i in range(4):
        if(len(args)<i+1):
            intext = input(f"Please provide index or name of {column_names[i]} column:\n[{vis[i]}]\n/processing Cf vis {column_names[i]} > ")
        else:
            print(f"Please provide index or name of {column_names[i]} column:\n[{vis[i]}]\n/processing Cf vis {column_names[i]} > "+args[i])
            vis[i] = args[i]
        if(intext!=""):
            if(intext[-1]=="!"):
                try:
                    vis[i] = int(intext[:-1])
                except:
                    print("Could not read column index. Falling back to default value.")
            else:
                vis[i] = intext
    return vis

def findVis(processing_method, vis, args = []):
    if(processing_method.__name__=="plainProcess"):
        vis = findPlainAvail(vis, args)
    if(processing_method.__name__=="QCriterion"):
        vis = findQCriterionAvail(vis, args)
    if(processing_method.__name__=="VelocityMagnitude"):
        vis = findVMagAvail(vis, args)
    if(processing_method.__name__=="Cfgen"):
        vis = findCf(vis, args)
    
def setProcessingMethod(processing_method, vis, args = []):
    intext = ""
    while(intext!="q"):
        if(len(args)<1):
            intext = input("/processing > ")
        else:
            intext = " ".join(args)
        if(intext==""):
            availProcMethods()
        else:
            args = intext.split(" ")
            if(args[0] == "plain"):
                vis = findPlainAvail(vis, args[1:])
                processing_method = plainProcess
                break
            if(args[0] == "QCriterion"):
                vis = findQCriterionAvail(vis, args[1:])
                processing_method = QCriterion
                break
            if(args[0] == "vmag" or args[0] == "velocity-magnitude" or args[0] == "Velocity magnitude"):
                vis = findVMagAvail(vis, args[1:])
                processing_method = VelocityMagnitude
                break
            if(args[0] == "Cfgen"):
                vis = findCf(vis, args[1:])
                processing_method = Cfgen
                break
            if(intext == "q"):
                break
    return processing_method, vis

def plainProcess(xcol, ycol, prev_line, ll, vis, udm=None):
    if(isinstance(vis, str)):
        vis = prev_line.index(vis)
    return float(ll[xcol]), float(ll[ycol]), float(ll[vis]), vis, udm

def QCriterion(xcol, ycol, prev_line, ll, vis, udm=None):
    '''
    Returns QCriterion value based on values from derivative
    columns.
    '''
    ders = []
    for i in range(len(vis)):
        if(not isinstance(vis[i], type(None))):
            if(isinstance(vis[i], str)):
                vis[i] = prev_line.index(vis[i])
            ders.append(float(ll[vis[i]]))
        else:
            ders.append(0.)
    A = lambda i, j : 0.5*(ders[i*3+j]-ders[j*3+i])+0.5*(ders[i*3+j]-ders[j*3+i])
    Q = 0.5*(
            A(0, 0)*A(1, 1)+
            A(1, 1)*A(2, 2)+
            A(0, 0)*A(2, 2)-
            A(0, 1)*A(1, 0)-
            A(1, 2)*A(2, 1)-
            A(0, 2)*A(2, 1)
        )
    return float(ll[xcol]), float(ll[ycol]), Q, vis, udm
    
def VelocityMagnitude(xcol, ycol, prev_line, ll, vis, udm=None):
    vels = []
    V_mag = 0.
    for i in range(len(vis)):
        if(not isinstance(vis[i], type(None))):
            if(isinstance(vis[i], str)):
                vis[i] = prev_line.index(vis[i])
            vels.append(float(ll[vis[i]]))
        else:
            vels.append(0.)
    for vel in vels:
        V_mag += vel*vel
    return float(ll[xcol]), float(ll[ycol]), np.sqrt(V_mag), vis, udm

def Cfgen(xcol, ycol, prev_line, ll, vis, udm=None):
    if(not isinstance(vis[0], int)):
        for i in range(len(vis)):
            if(not isinstance(vis[i], type(None))):
                if(isinstance(vis[i], str)):
                    vis[i] = prev_line.index(vis[i])
    if(isinstance(udm, type(None))):
        udm = [float(ll[xcol]), float(ll[ycol])]
        return float(ll[xcol]), float(ll[ycol]), 0., vis, udm
    xn = float(ll[xcol])
    xn1 = udm[0]
    yn = float(ll[ycol])
    yn1 = udm[1]
    s = np.asarray([xn-xn1, yn-yn1])
    s = s/np.max((np.linalg.norm(s), 1e-10))
    n = np.asarray([-s[1], s[0]])
    Cf = float(ll[vis[0]])*s[0]*n[0]+float(ll[vis[1]])*s[1]*n[0]+float(ll[vis[2]])*s[0]*n[1]+float(ll[vis[3]])*s[1]*n[1]
    return float(ll[xcol]), float(ll[ycol]), Cf, vis, [float(ll[xcol]), float(ll[ycol])]
    