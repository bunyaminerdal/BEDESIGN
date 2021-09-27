class Variables():
    path=None
    projectname="Un Saved Project"
    gridxcount=5
    gridycount=3
    gridzcount=2
    gridxspan=400
    gridyspan=600
    gridzspan=800
    xdistanceforMove=0.0
    ydistanceforMove=0.0
    zdistanceforMove=0.0
    numberofcopy=1
    selectedJoints=[]
    selectedFrames=[]
    pselectedJoints=[]
    pselectedFrames=[]
    isDrawing=False
    isFirstJoint=True
    gridPoints=[]
    preFramepoints=[(None,None,None),(None,None,None)]
    takenPoint=()
    ismovepicking=False
    iscopypicking=False
    ispickingPoint=False
    isrectdrawing=False    
    jointsupportTemp=[0,0,0,0,0,0]
    jointLocalAxe1=0
    jointLocalAxe2=0
    jointLocalAxe3=0
    frameLocalAxe=0
    units=["ton-m","ton-cm","ton-mm","kg-m","kg-cm","kg-mm","kN-m","kN-cm","kN-mm","N-m","N-cm","N-mm"]
    newton=9.80665
    unitdict={"ton":0.001,"kg":1,"kN":0.001*newton,"N":newton,"m":0.01,"cm":1,"mm":10}
    selectionmattype="Steel"

#options
    blackorwhitetheme=0
    clearcolorfloat=(1,1,1,1)
    frameColor=(0,170,250)
    pointColor=(80,80,80)
    textcolor=(0, 0, 0)
    gridcolor=(180,180,180)
    bubletextcolor=(50,50,50)
    preframecolor=(10, 34, 3) 
    selectedframecolor=(255,0,0)
    selectedpointcolor=(250, 0, 0)
    selectrectanglecolor=(250, 0, 0)       
    pincolor=(250, 0, 0)
    supportcolor=(255,0,255)

    textfont=('Decorative', 14)
    bubletextwidth=1
    localaxescale=30
    supportscale=30
    framewidth=2
    pointwidth=8
    pickingrange=5
    pingrange=6
    pinsize=2
    selectedpointsize=2

#default options white
    
    defWframeColor=(0,170,250)
    defWpointColor=(80,80,80)
    defWselectedframecolor=(255,0,0)
    defWpreframecolor=(10, 34, 3)
    defWselectrectanglecolor=(250, 0, 0)
    defWselectedpointcolor=(250, 0, 0)
    defWpincolor=(250, 0, 0)
    defWgridcolor=(180,180,180)
    defWbubletextcolor=(50,50,50)
    defWtextcolor=(0, 0, 0)
    defWsupportcolor=(255,0,255)
    
#default options Black
    
    defBframeColor=(255, 255, 0)
    defBpointColor=(255, 255, 0)
    defBselectedframecolor=(255,0,0)
    defBpreframecolor=(200, 150, 80)
    defBselectrectanglecolor=(250, 0, 0)
    defBselectedpointcolor=(250, 0, 0)
    defBpincolor=(250, 0, 0)
    defBgridcolor=(125,125,125)
    defBbubletextcolor=(180,180,180)
    defBtextcolor=(120, 255, 255)
    defBsupportcolor=(255,0,255)

#white theme options
    
    wframeColor=(0,170,250)
    wpointColor=(80,80,80)
    wselectedframecolor=(255,0,0)
    wpreframecolor=(10, 34, 3)
    wselectrectanglecolor=(250, 0, 0)
    wselectedpointcolor=(250, 0, 0)
    wpincolor=(250, 0, 0)
    wgridcolor=(180,180,180)
    wbubletextcolor=(50,50,50)
    wtextcolor=(0, 0, 0)
    wsupportcolor=(255,0,255)

#black theme options
    
    bframeColor=(255, 255, 0)
    bpointColor=(255, 255, 0)
    bselectedframecolor=(255,0,0)
    bpreframecolor=(200, 150, 80)
    bselectrectanglecolor=(250, 0, 0)
    bselectedpointcolor=(250, 0, 0)
    bpincolor=(250, 0, 0)
    bgridcolor=(125,125,125)
    bbubletextcolor=(180,180,180)
    btextcolor=(120, 255, 255)
    bsupportcolor=(255,0,255)

#default options
    deftextfont=('Decorative', 14)
    defbubletextwidth=1
    deflocalaxescale=30
    defsupportscale=30
    defframewidth=2
    defpointwidth=8
    defpickingrange=5
    defpingrange=6
    defpinsize=2
    defselectedpointsize=2
    
#user defined variables
    gridxTemp=[('A',0),('B',400),('C',800),('D',1200),('E',1600)]
    gridyTemp=[('1',0),('2',600),('3',1200)]
    gridzTemp=[('Z1',0),('Z2',800)]
    gridx=[('A',0),('B',400),('C',800),('D',1200),('E',1600)]
    gridy=[('1',0),('2',600),('3',1200)]
    gridz=[('Z1',0),('Z2',800)]
    xbublesize=20
    ybublesize=20
    zbublesize=20
    xbubleLoc="End"
    ybubleLoc="End"
    zbubleLoc="End"
    framenametextdraw=False
    jointnametextdraw=False
    showgrid=True
    showorgin=True
    showjointnode=False
    showjointsupport=True
    showjointLocalAxes=False
    showframeLocalAxes=False        
    unitindex=0
    unitindexlast=5
    #yeni eklenenler
    showextrudeview=False
    showframesectionname=False

