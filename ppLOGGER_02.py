import time
import os
import string
import subprocess
from Tkinter import *
from tkFileDialog import *
from tkMessageBox import *

import tkFont
import random
import math
import imp


try:
    import piplates.DAQCplate as DAQC
    #import DAQCplate as DAQC    
except ImportError:
    print "To run this program you need to install the Pi-Plates library."
    print "Do so by executing the following from the command line:"
    print "sudo pip install Pi-Plates"
    response=raw_input("Would you like to install it now? (y/n)")
    print response, response.lower
    if (response.lower()=='y'):
        os.system("sudo pip install pi-plates")
        print('Pi-Plates module installed. Please restart the program')
        sys.exit()
    else:
        sys.exit() 

def VersionErr():
    print "For best performance, please install the latest Pi-Plates library."
    print "Do so by executing the following from the command line:"
    print "sudo pip install --upgrade pi-plates"    
    response=raw_input("Would you like to upgrade now? (y/n)")
    if (response.lower()=='y'):
        os.system("sudo pip install --upgrade pi-plates")
        reload(DAQC)
    else:
        sys.exit() 
        
try:
    version=DAQC.getVersion()     
    if (version<1.02):
        VersionErr()    
except AttributeError:
    VersionErr()     

try:    #ensure that the PMW module has been installed
    imp.find_module('Pmw')
    PMWfound = True
    import Pmw
except ImportError:
    PMWfound = False
    print "A module called PMW is required to run this program."
    print "Get it by executing the following from the command line:"
    print "sudo apt-get install python-pmw"
    response=raw_input("Would you like to instal pwm now? (y/n)")
    if (response.lower()=='y'):
#        os.system("sudo apt-get install python-pmw")
        os.system("pip install pmw")
        import Pmw
    else:
        sys.exit()     

################################################################################
############### Start Program! #################################################
################################################################################
Version = 1.0    


# define options for opening or saving a log file
newlogfile_opt = options = {}
options['defaultextension'] = '.log'
options['filetypes'] = [('log files', '.log')]
#options['initialdir'] = 'C:\\'
#options['initialfile'] = 'mylog.log'
#options['parent'] = root
options['title'] = 'Open new log file'

# define options for opening or saving an existing log file
xlogfile_opt = options = {}
options['defaultextension'] = '.log'
options['filetypes'] = [('log files', '.log')]
#options['initialdir'] = 'C:\\'
#options['initialfile'] = 'mylog.log'
#options['parent'] = viewroot
options['title'] = 'Open existing log file'

# define options for opening or saving a setup file
setupfile_opt = options = {}
options['defaultextension'] = '.stp'
options['filetypes'] = [('setup files', '.stp')]
#options['initialdir'] = 'C:\\'
#options['initialfile'] = 'mysetup.stp'
#options['parent'] = root
options['title'] = 'Open setup file'

def on_closing():
    shutdown()

def NewLogFile():
    global logFile, lfOpen, fName
    if (Logging==False):
        fName=''
        fName=asksaveasfilename(**newlogfile_opt)
        if ('.log' in fName):
            lfOpen=True   

def NewSetupFile():
    suFilename=asksaveasfilename(**setupfile_opt)
    if ('.stp' in suFilename):
        sufile=open(suFilename,'w')
        desc=range(8)
        setup=''
        for i in range(8):
            if (DAQCpresent[i]==1):
                setup= setup+str(i)+','
            else:
                setup= setup+'X,'
        for i in range(8):
            if (DAQCpresent[i]==1):
                desc=daqc[i].a2dGetLabels()
                for k in range(8):
                    setup= setup+desc[k]+','
#                desc=daqc[i].dinGetLabels()
                for k in range(8):
                    setup = setup+desc[k]+','
                desc=daqc[i].a2dGetStates()
                for k in range(8):
                    setup= setup+str(desc[k])+','
#                desc=daqc[i].dinGetStates()
                for k in range(8):
                    setup = setup+str(desc[k])+',' 
#        setup = setup + StreamBucket.get() + ',' + StreamIdentifier.get() + ',' + StreamKey.get()+ ','
        setup = setup + str(AoutSignal.get()) + ',' + str(DoutSignal.get())+ ','
        setup = setup + SampleCount.get() + ',' + SamplePeriod.get()
        sufile.write(setup)
        sufile.write('\n')      
        sufile.close()


def OpenSetupFile():
    suFilename = askopenfilename(**setupfile_opt)
    if ('.stp' in suFilename):    
        sufile=open(suFilename,'r')
        setup=''
        setup=sufile.read()
        sufile.close()
        setup=setup[:-1]
        setupList=setup.split(",")
        #print setupList
        #check validity
        current=range(8)
        for i in range(8):
            if (DAQCpresent[i]==1):
                current[i]=str(i)
            else:
                current[i]='X'    
        setup=setupList[0:8]
        if (setup != current):
            showwarning('Load Setup','Setup file does NOT match your hardware.')
        else:
            k=8
            dBlock=range(8)
            for i in range(8):
                if (DAQCpresent[i]==1):
                    sBlock=setupList[k:k+8]
                    daqc[i].a2dSetLabels(sBlock)        
                    sBlock=setupList[k+8:k+16]
#                    daqc[i].dinSetLabels(sBlock)
                    sBlock=setupList[k+16:k+24]
                    daqc[i].a2dSetStates(sBlock)        
                    sBlock=setupList[k+24:k+32]
#                    daqc[i].dinSetStates(sBlock)                
                    k+=32
            AoutSignal.set(int(setupList[k+3]))
            DoutSignal.set(int(setupList[k+4]))
            SampleCount.set(setupList[k+5])
            SamplePeriod.set(setupList[k+6])
    
def StartLog():
    global logFile, lfOpen, Logging, streamOpen, fName, SampleC, logHeader, streamer
    if (((lfOpen) or (streamOpen)) and  (Logging==False)):
        root.wm_title("DAQCplate Data Logger - LOGGING")

        Header="Time,"
        for i in range(8):
            if (DAQCpresent[i]==1):
                desc=['','','','','','','','']
                desc=daqc[i].a2dDescriptors()
                for k in range(8):
                    if (desc[k] != ''):
                        Header= Header+'DAQC'+str(i)+'.'+desc[k]+','
                desc=['','','','','','','','']
#                desc=daqc[i].dinDescriptors()
                for k in range(8):
                    if (desc[k] != ''):
                        Header= Header+'DAQC'+str(i)+'.'+desc[k]+','                       
        Header = Header[:-1] 
        logHeader=Header
        if (lfOpen):
            logFile=open(fName,'w')
            logFile.write(Header)
            logFile.write('\n')
        Logging=True   
        SampleC=int(SampleCount.get())
    else:
        showerror(
            "Logging",
            "You must open a log file or a stream before you can start logging"
        )
    
def StopLog():
    global logFile, lfOpen, Logging, streamOpen, streamer
    if (Logging):
        Logging=False
        root.wm_title("DAQCplate Data Logger")
        if (lfOpen):
            logFile.close()   
        if (streamOpen):
            streamer.close()
    
def About():
    Pmw.aboutversion('1.0')
    Pmw.aboutcopyright('Copyright Wallyware, inc 2016\nAll rights reserved')
    Pmw.aboutcontact(
        'For information about this application contact:\n' +
        'support@pi-plates.com'
    )
    about = Pmw.AboutDialog(root, applicationname = 'ppLogger')
    about.activate(globalMode = 0, geometry = 'centerscreenfirst')
    about.withdraw()
    about.show() 

def Docs():   
    cmd_line = "xpdf ppLOGGER-Documentation.pdf"
    p = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()[0]

def License():   
    cmd_line = "xpdf GNUpublicLicense.pdf"
    p = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = p.communicate()[0]    
    
def shutDown():
    global lfOpen, Logging, streamOpen, streamer
    StopLog()
    if (lfOpen):
        logFile.close()   
#    if (streamOpen):
#        streamer.close()   
    root.quit()
    
#Configure: Dialog box to get sampling parameters that holds focus until closed.    
def Configure():
    if (Logging==False):
        cBox=Toplevel()    
        cBox.transient(master=root)
        cBox.wm_title("Log Setup")   
        cBox.focus_set()

        sP=Label(cBox,text='Sample Period in Seconds (Minimum is '+str(SampleTmin)+'):', padx=2, pady=2)
        sP.grid(row=0,column=0,sticky="e")
        sPval=Entry(cBox,width=8,textvariable=SamplePeriod)
        sPval.grid(row=0,column=1,sticky="w")
        
        sC=Label(cBox,text="Sample Count:", padx=2, pady=2)
        sC.grid(row=1,column=0,sticky="e")
        sCval=Entry(cBox,width=8,textvariable=SampleCount)
        sCval.grid(row=1,column=1,sticky="w")

        sD1=Label(cBox,text="Log Duration in seconds = ", pady=20)
        sD1.grid(row=2,column=0,sticky="e")
        sD2=Label(cBox,textvariable=sDval, pady=20)
        sD2.grid(row=2,column=1,sticky="w")
    
        sB=Button(cBox, text='Close', command=cBox.destroy)
        sB.grid(row=3, columnspan=2, pady=4)

        cBox.grab_set()
        root.wait_window(cBox)

#signalSetup: Dialog box to control test signals that holds focus until closed.    
def signalSetup():
    global aoutSignalOn, doutSignalOn
    
    sigBox=Toplevel()    
    sigBox.transient(master=root)
    sigBox.wm_title("Test Signal Setup")   
    sigBox.focus_set()

    aoutchk=Checkbutton(sigBox,variable=AoutSignal,onvalue = 1, offvalue = 0)
    aoutchk.grid(row=0,column=0,sticky="e")
    sA=Label(sigBox,text='Enable Analog Signals     ', padx=2, pady=2)
    sA.grid(row=0,column=1,sticky="w")
    
    doutchk=Checkbutton(sigBox,variable=DoutSignal,onvalue = 1, offvalue = 0)
    doutchk.grid(row=1,column=0,sticky="e")
    sD=Label(sigBox,text='Enable Digital Signals     ', padx=2, pady=2)
    sD.grid(row=1,column=1,sticky="w")
        
    cBut=Button(sigBox, text='Close', command=sigBox.destroy)
    cBut.grid(row=2, columnspan=2, padx=2, pady=2)

    sigBox.grab_set()
    root.wait_window(sigBox)  

# doUpdates: a recurring routine to update the value of the displayed test duration value
def doUpdates():
    root.after(500,doUpdates)   
    try:
        sDval.set(str(float(SamplePeriod.get())*float(SampleCount.get())))
    except ValueError:
        sDval.set('0')    

#ViewLog: Functions for providing different methods of exmining data        
def ViewLog():
    global Logging, fName 

    def vPlot():
        pFile=getFile()
        if (pFile==''):
            return
        else:
            os.system('python loggerPLOT.py ' + pFile)
            vBox.destroy()
        
    def vStream():  
        showinfo(
            'View Stream',
            'Log into your account at https://www.initialstate.com to see your streaming data log.')
        vBox.destroy()
    
    def vFile():
        pFile=getFile()
        if (pFile==''):
            return
        else:
            os.system('leafpad ' + pFile)
            vBox.destroy()
            
    def vSpreadsheet():  
        pFile=getFile()
        if (pFile==''):
            return
        else:
            os.system('localc -o ' + pFile)
            vBox.destroy()
            
    def getFile():
        global Logging, fName
        # define options for opening an existing log file
        xlogfile_opt = options = {}
        options['defaultextension'] = '.log'
        options['filetypes'] = [('log files', '.log')]
        options['title'] = 'Open existing log file'
        fLoop=True
        while (fLoop):
            xfName=''
            xfName=askopenfilename(**xlogfile_opt)
            if (xfName==''):
                fLoop=False
            else:
                if (fName==xfName):
                    showerror('Log File','Viewing currently open log file is not allowed')
                else:
                    fLoop=False           
        return xfName
                  
    # define options for opening or saving a setup file
    viewWarning_opt = options = {}
    options['icon'] = WARNING
    options['type'] = OKCANCEL 
    if (Logging==True):
        reply = askquestion('Warning', 'Some viewing features may affect logging.',**viewWarning_opt)
        if (reply=='cancel'):
            return

    vBox=Toplevel()    
    vBox.transient(master=root)
    vBox.wm_title("View Log")   
    vBox.focus_set()
    pBut=Button(vBox, text='Plot Data', command=vPlot)
    pBut.pack(fill=X, padx=4, pady=3)    
    sBut=Button(vBox, text='View Streamed Data', command=vStream)
    sBut.pack(fill=X, padx=4, pady=3)
    fBut=Button(vBox, text='View Data File', command=vFile)
    fBut.pack(fill=X, padx=4, pady=3)
    eBut=Button(vBox, text='Open Data in Spreadsheet', command=vSpreadsheet)
    eBut.pack(fill=X, padx=4, pady=3)
    vBox.grab_set()
    root.wait_window(vBox)            
        
def task():
    global logFile, lfOpen, Logging, streamOpen, fName, SampleC, SampleT, logHeader
    global theta, dnum
    aChannelCount=0
    dChannelCount=0
    try:
        SampleT=float(SamplePeriod.get())
        if (SampleT<SampleTmin):
            SampleT=SampleTmin
    except ValueError:
        SampleT=SampleTmin
    root.after(int(SampleT*1000),task)   
    logString=''
    dTypes=''
    j=0
    for i in range (0,8): #for boards 0 through 8
        a2dvals=range(8)
        if (DAQCpresent[i]==1):
            #Test Signal Generation
            if (DoutSignal.get()==1):
                dnum[i] = (dnum[i]+1)%128
                DAQC.setDOUTall(i,dnum[i])
            if (AoutSignal.get()==1):
                theta[i]=(theta[i]+1)%360
                rad=math.radians(theta[i])
                dacval=2.048*(1+math.sin(rad))
                dacval2=2.048*(1+math.sin(2*rad))          
                DAQC.setDAC(i,0,dacval)
                DAQC.setDAC(i,1,dacval2)

            #Retrieve and plot  values
            a2dvals=daqc[i].a2dupdate() 

            #Convert data to strings for log
            for k in range(8):
                if (a2dvals[k] != ''):
                    logString=logString+str(a2dvals[k])+','
                    aChannelCount += 1
                    dTypes = dTypes+'a,'
     
    dtypes = dTypes[:-1]
    logString = logString[:-1] 
    logString = time.strftime("%H:%M:%S",time.localtime())+','+logString    
    if (Logging and lfOpen):
        #logString = logString[:-1]
        #logString = time.strftime("%H:%M:%S",time.localtime())+','+logString
        logFile.write(logString)
        logFile.write('\n')
        
    if (Logging and streamOpen):
        headerList=logHeader.split(",")
        #logString = logString[:-1]
        dataList=logString.split(",")
        typeList=dTypes.split(",")
        #print aChannelCount, dChannelCount, aChannelCount+dChannelCount
        for i in range(0,aChannelCount+dChannelCount):
            k=i+1           
            if (typeList[i] == 'a'):           
                streamer.log(headerList[k],float(dataList[k]))
                #print i,typeList[i],headerList[k],float(dataList[k])
            else:
                if (dataList[k]=='0'):
                    streamer.log(headerList[k],"false")
                    #print i,typeList[i],headerList[k], 'false'
                else:
                    streamer.log(headerList[k],"true")
                    #print i,typeList[i],headerList[k], 'true'
                    
    if (Logging):
        SampleC -= 1
        root.wm_title("DAQCplate Data Logger - LOGGING - "+str(SampleC)+" Samples and "+str(SampleT*SampleC)+" Seconds Remaining")
        if (SampleC==0):
            StopLog()
            showinfo("Logging","Logging Complete")                                      
            
class daqcDASH:
    def __init__(self,frame,addr):
        self.a2d=range(8)
        
        def deSelect():
            for i in range(0,8):
                self.a2d[i].deSelect()
                
        def selectAll():
            for i in range(0,8):        
                self.a2d[i].Select()
            
        self.addr=addr
        self.root=frame
        
        BG='#888FFF888'
#        off=0
        off=250  
        self.mFrame=Frame(self.root,bg=BG,bd=0,relief="ridge")
        self.mFrame.place(x=0,y=off,width=W,height=SLICE+10)   
        self.button1=Button(self.mFrame, text='Clear All', command=deSelect)
        self.button1.grid(row=0, column=0, padx=4,pady=5)
        self.button2=Button(self.mFrame, text='Select All', command=selectAll)  
        self.button2.grid(row=0, column=1, padx=4,pady=5)
        
        self.a2d=range(8)
        for i in range(0,8):
            self.a2d[i]=daqcADC(self.root,self.addr,i)
    
    def a2dupdate(self):
        vals=['','','','','','','','']
        for i in range(0,8):          
            vals[i]=self.a2d[i].update()
        return vals

    def a2dDescriptors(self):
        vals=['','','','','','','','']
        for i in range(0,8):
            vals[i]=self.a2d[i].descriptors()
        return vals   
    
    def a2dGetLabels(self):
        vals=['','','','','','','','']
        for i in range(0,8):
            vals[i]=self.a2d[i].getLabel()
        return vals   

    def a2dGetStates(self):
        vals=['','','','','','','','']
        for i in range(0,8):
            vals[i]=self.a2d[i].getState()
        return vals   

    def a2dSetLabels(self,labels):
        self.vals=labels
        for i in range(0,8):
            self.a2d[i].setLabel(self.vals[i])
        return   
        
    def a2dSetStates(self,states):
        self.vals=states
        for i in range(0,8):
            self.a2d[i].setState(self.vals[i])
        return   
    
class daqcADC:
    def __init__(self,root,addr,channel):
        self.addr=addr
        self.root=root
        self.chan=channel
        self.var=IntVar()   #This is the select button for each channel
        self.var.set(1)
        self.val=DoubleVar()
        self.val.set(DAQC.getADC(self.addr,self.chan))
        self.valstring=StringVar()
        self.valstring.set(str(self.val.get()))
        off=H-2-17*SLICE+self.chan*SLICE
        BG='#888FFFFFF'
        self.CWidth=int(.75*W+20)
        self.a2df=Frame(self.root,bg=BG,bd=0,relief="ridge")
        self.a2df.place(x=0,y=off,width=W,height=SLICE)
        self.a2dc=Checkbutton(self.a2df,fg="Black",bg=BG,variable=self.var,onvalue = 1, offvalue = 0,command=self.cb)
        self.a2dc.grid(row=0,column=0,sticky="w")
        self.var.set(1)
        self.a2dl = StringVar(root, value="A2D Channel "+str(self.chan)+":")
        self.a2dt = Label(self.a2df,textvariable=self.valstring,fg="Black",bg=BG,width=5).grid(row=0,column=2,sticky="w")
        self.a2dtxt=Entry(self.a2df,textvariable=self.a2dl,fg="Black",bg=BG,bd=0,relief="flat",width=12)
        self.a2dtxt.grid(row=0,column=1,sticky="w")
        self.a2dcanvas=Canvas(self.a2df,bg=BG,width=self.CWidth,height=SLICE,bd=0,relief="flat")
        self.a2dcanvas.grid(row=0,column=3,sticky="e")
        self.maxrange=self.CWidth
        self.log=range(self.maxrange)
        for i in range(self.maxrange):
            self.log[i]=0.0
        self.nextPtr=0
        
    def cb(self):
        if (self.var==1):
            a=1
            
    def deSelect(self):
        self.a2dc.deselect()

    def Select(self):
        self.a2dc.select()        
        
        
    def update(self):
        if (self.var.get()==1):
            self.val.set(DAQC.getADC(self.addr,self.chan))
            self.valstring.set(str("{:5.3f}".format(self.val.get())))
            self.log[self.nextPtr]=self.val.get()
            self.nextPtr=(self.nextPtr+1)%self.maxrange
            self.plot()
            return self.val.get()
        else:
            return ''

    def descriptors(self):
        if (self.var.get()==1):
            return self.a2dl.get()
        else:
            return ''

    def getLabel(self):
        return self.a2dl.get()

    def setLabel(self,label):
        self.a2dl.set(label)        
        
    def getState(self):
        return self.var.get()        
 
    def setState(self,state):
        if (state=='1'):
            self.a2dc.select()
        else:
            self.a2dc.deselect()
            
    def plot(self):
        points=range(2*self.CWidth)
        for i in range(self.CWidth):
            j=(self.nextPtr-1+self.CWidth+i)%self.CWidth
            lval=int(self.log[j]*(SLICE-2)/4.096)
            points[2*i]=i
            points[2*i+1]=SLICE-1-lval
        self.a2dcanvas.delete("all")
        self.a2dcanvas.create_line(points, fill="#FF0000",width=2)
                        
SampleT=0.2
theta=[0,0,0,0,0,0,0,0]  
dnum=[0,0,0,0,0,0,0,0]
SampleC=0
logFile=0
lfOpen=False
streamOpen=False
Logging=False
logHeader=''
streamer=0
fName=''
            
root = Tk()
root.resizable(0,0) #This means that the app window is not resizable by the user
#root=Pmw.initialise()

menu=Menu(root)
root.wm_title("DAQCplate Data Logger")
    
W=800
H=480
SLICE=33
#SLICE=35
w = root.winfo_screenwidth()
h = root.winfo_screenheight()
x = w/2 - W/2
y = h/2 - H/2
root.geometry("%dx%d+%d+%d" % (W,H,x, y))

root.config(menu=menu)
filemenu = Menu(menu,tearoff=0)
menu.add_cascade(label="File", menu=filemenu)
filemenu.add_command(label="Open New File for Logging", command=NewLogFile)
filemenu.add_separator()
filemenu.add_command(label="Save Configuration", command=NewSetupFile)
filemenu.add_command(label="Load Configuration", command=OpenSetupFile)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=shutDown)

setupmenu = Menu(menu,tearoff=0)
menu.add_cascade(label="Setup", menu=setupmenu)
setupmenu.add_command(label="Logging", command=Configure)
setupmenu.add_command(label="Test Signals", command=signalSetup)
  
helpmenu = Menu(menu,tearoff=0)
menu.add_cascade(label="Help", menu=helpmenu)
helpmenu.add_command(label="Documentation", command=Docs)
helpmenu.add_command(label="Usage License", command=License)
helpmenu.add_command(label="About", command=About)

menu.add_command(label="START", foreground='green',font="-weight bold", command=StartLog)
menu.add_command(label="STOP", foreground='red',font="-weight bold",command=StopLog)
menu.add_command(label="VIEW", foreground='blue',font="-weight bold",command=ViewLog)

def callback():
    print "click!"

notebook = Pmw.NoteBook(root,borderwidth=2,pagemargin=2)
notebook.pack(fill = 'both', expand = 1)

DAQCpresent=range(8)
daqc=range(8)
DAQCFoundCount=0
#daqcpage=range(8)

SampleTmin=0
for i in range (0,8):
#    rtn = DAQC.getADDR(i)
    rtn = 8
    if ((rtn-8)==i):
        DAQCpresent[i]=1
#        DAQCFoundCount+=1
#        DAQC.setDOUTall(i,0)
#        DAQC.setPWM(i,0,0)
#        DAQC.setPWM(i,1,0)
        page = notebook.add('DAQC'+str(i))
        notebook.tab('DAQC'+str(i)).focus_set()        
        daqc[i]=daqcDASH(page,i)
        SampleTmin+=0.2
    else:
        DAQCpresent[i]=0

if (SampleTmin>0):
    SampleT=SampleTmin
else:
    SampleT=0.2

SamplePeriod=StringVar()
SamplePeriod.set(str(SampleT))

SampleCount=StringVar()
SampleCount.set('1000')

sDval=StringVar()
sDval.set(str(float(SamplePeriod.get())*float(SampleCount.get())))

AoutSignal=IntVar()
AoutSignal.set(0)
DoutSignal=IntVar()
DoutSignal.set(0)
    
notebook.setnaturalsize() 
root.after(int(SampleT*1000),task) 

root.after(500,doUpdates) 
      
root.mainloop()
