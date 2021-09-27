from Undo import UndoReundo
from Var import Variables
import math

class Frame():
    framedict=[]
    count=0
    def __init__(self, JointStart, JointEnd):
        if JointStart!=JointEnd:
            self.jointStart = JointStart
            self.jointEnd = JointEnd
            self.id=Frame.count
            undoobj=[]
            
            if sum(x.get('coords') == JointStart and x.get('deleted')==False for x in Joint.jointdict)==0: # başlangıçta nokta yoksa oluşturuyoruz
                Joint(JointStart[0],JointStart[1],JointStart[2])
                for joint in Joint.jointdict:
                    if joint['coords']==JointStart:
                        self.jointStartIndex=joint['name']
                        undoobj.append((joint,'deleted',True,False))

            if sum(x.get('coords') == JointEnd and x.get('deleted')==False for x in Joint.jointdict)==0: # bitişte nokta yoksa oluşturuyoruz
                Joint(JointEnd[0],JointEnd[1],JointEnd[2])
                for joint in Joint.jointdict:
                    if joint['coords']==JointEnd:
                        self.jointEndIndex=joint['name']
                        undoobj.append((joint,'deleted',True,False))

            for joint in Joint.jointdict:
                if joint['coords']==JointStart :                    
                    if joint['deleted']==False:
                        self.jointStartIndex=joint['name']

            for joint in Joint.jointdict:
                if joint['coords']==JointEnd:
                    if joint['deleted']==False:
                        self.jointEndIndex=joint['name']

            if sum(y.get('joint0')==self.jointStartIndex and y.get('joint1')==self.jointEndIndex and y.get('deleted')==False for y in Frame.framedict)==0 and sum(y.get('joint0')==self.jointEndIndex and y.get('joint1')==self.jointStartIndex and y.get('deleted')==False for y in Frame.framedict)==0:
                Frame.count += 1
                self.framedict.append( {'name':Frame.count,'joint0':self.jointStartIndex, 'joint1' :self.jointEndIndex,'show':True,'type':'frame','deleted':False ,'angle':0,'section':'No Section'})        
                for frame in Frame.framedict:
                    if frame['joint0']==self.jointStartIndex and frame['joint1']==self.jointEndIndex:
                        undoobj.append((frame,'deleted',True,False))
            UndoReundo(undoobj)

    @staticmethod
    def deleteFrame():
        if Variables.selectedFrames!=[]:
            undoobj=[]
            
            for frame in Variables.selectedFrames:            
                frame['deleted']=True
                undoobj.append((frame,'deleted',False,True))

                for joint in Joint.jointdict:
                    if joint['name']==frame['joint0']: # silinen framein 0 noktasına bağlı başka frame var mı ?
                        deletejointcheck=0
                        for framecheck1 in Frame.framedict:
                            if framecheck1['name']!=frame['name'] and (framecheck1['joint0']==joint['name'] or framecheck1['joint1']==joint['name']) and framecheck1['deleted']==False:
                                deletejointcheck=1
                        if deletejointcheck==0:
                            joint['deleted']=True
                            undoobj.append((joint,'deleted',False,True))

                for joint in Joint.jointdict:
                    if joint['name']==frame['joint1']: # silinen framein 1 noktasına bağlı başka frame var mı ?
                        deletejointcheck=0
                        for framecheck1 in Frame.framedict:
                            if framecheck1['name']!=frame['name'] and (framecheck1['joint0']==joint['name'] or framecheck1['joint1']==joint['name']) and framecheck1['deleted']==False:
                                deletejointcheck=1
                        if deletejointcheck==0:
                            joint['deleted']=True
                            undoobj.append((joint,'deleted',False,True))
            
            
            UndoReundo(undoobj)

class Joint():
    jointdict=[]
    count=0
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        Joint.count += 1
        self.jointdict.append({'name':Joint.count,'coords':(self.x,self.y,self.z) ,'show':True,'type':'joint', 'deleted':False , 'restraints':[0,0,0,0,0,0], 'angle1':0 ,'angle2':0 ,'angle3':0})

class Unit():
    def dimension(self,value,index) -> object:   #sadece uzunluk olduğunda
        dimensionnamelast=Variables.units[Variables.unitindexlast].split('-')[1]
        dimensionlast=Variables.unitdict[dimensionnamelast]
        dimensionname=Variables.units[Variables.unitindex].split('-')[1]
        dimension=Variables.unitdict[dimensionname]  
        
        if index==0:
            return value*dimension
        if index==1:
            return value/dimension
        if index==2:
            return value*dimension/dimensionlast
    
    def density(self,value,index):   #sadece yoğunluk olduğunda
        
        dimensionnamelast=Variables.units[Variables.unitindexlast].split('-')[1]
        dimensionlast=Variables.unitdict[dimensionnamelast]
        dimensionname=Variables.units[Variables.unitindex].split('-')[1]
        dimension=Variables.unitdict[dimensionname]
        forcenamelast=Variables.units[Variables.unitindexlast].split('-')[0]
        forcelast=Variables.unitdict[forcenamelast]
        forcename=Variables.units[Variables.unitindex].split('-')[0]
        force=Variables.unitdict[forcename]

        if index==0:
            return format((value*force/(dimension*dimension*dimension)),'.15f')
        if index==1:
            return format((value/force)*(dimension*dimension*dimension),'.15f')
        if index==2:
            return format(((value*force/(dimension*dimension*dimension))/forcelast)*(dimensionlast*dimensionlast*dimensionlast),'.15f')
    
    def stress(self,value,index):   #sadece yoğunluk olduğunda
        dimensionnamelast=Variables.units[Variables.unitindexlast].split('-')[1]
        dimensionlast=Variables.unitdict[dimensionnamelast]
        dimensionname=Variables.units[Variables.unitindex].split('-')[1]
        dimension=Variables.unitdict[dimensionname]
        forcenamelast=Variables.units[Variables.unitindexlast].split('-')[0]
        forcelast=Variables.unitdict[forcenamelast]
        forcename=Variables.units[Variables.unitindex].split('-')[0]
        force=Variables.unitdict[forcename]

        if index==0:
            return format(value*force/(dimension*dimension),'.15f')
        if index==1:
            return format((value/force)*(dimension*dimension),'.15f')
        if index==2:
            return format(((value*force/(dimension*dimension))/forcelast)*(dimensionlast*dimensionlast),'.15f')

    def index(self,index):
        Variables.unitindexlast=Variables.unitindex
        Variables.unitindex=index

class Materials():
    materialdict=[]
    count=0

class Steel():
    steeldict=[]
    def __init__(self,_name,_E,_U,_A,_W,_FY,_FU):
        self.name=str(_name)
        self.E=_E
        self.U=_U
        self.A=_A
        self.W=_W
        self.FY=_FY
        self.FU=_FU
        if sum(y.get('name')==self.name and y.get('deleted')==False  for y in Materials.materialdict)==0:
            Materials.count+=1
            Materials.materialdict.append({'name':self.name,'index':Materials.count,'E':self.E,'U':self.U,'A':self.A,'W':self.W,'FY':self.FY,'FU':self.FU,'type':'Steel','deleted':False})
    
class Concrete():
    concretedict=[]
    def __init__(self,_name,_E,_U,_A,_W,_FC):
        self.name=str(_name)
        self.E=_E
        self.U=_U
        self.A=_A
        self.W=_W
        self.FC=_FC
        if sum(y.get('name')==_name and y.get('deleted')==False for y in Materials.materialdict)==0:
            Materials.count+=1
            Materials.materialdict.append({'name':self.name,'index':Materials.count,'E':self.E,'U':self.U,'A':self.A,'W':self.W,'FC':self.FC,'type':'Concrete','deleted':False})

class Sections():
    sectiondict=[]
    count=0

class Ishapes():
    ishapesdict=[]
    def __init__(self,_name,_mat,_h,_btop,_btopthickness,_bbottom,_bbottomthickness,_wthickness):
         self.name=str(_name)
         self.mat=_mat
         self.h=_h
         self.btop=_btop
         self.btopthickness=_bbottomthickness
         self.bbottom=_bbottom
         self.bbottomthickness=_bbottomthickness
         self.wthickness=_wthickness
         if sum(y.get('name')==_name and y.get('deleted')==False for y in Sections.sectiondict)==0:
            Sections.count+=1
            Sections.sectiondict.append({'name':self.name,'type':'ishape','index':Sections.count,'matindex':self.mat,'h':self.h,
                                            'btop':self.btop,'btopthickness':self.btopthickness,'bbottom':self.bbottom,
                                            'bbottomthickness':self.bbottomthickness,'wthickness':self.wthickness,'deleted':False})

class Ushapes():
    ushapesdict=[]
    def __init__(self,_name,_mat,_h,_b,_bthickness,_wthickness):
         self.name=str(_name)
         self.mat=_mat
         self.h=_h
         self.b=_b
         self.bthickness=_bthickness
         self.wthickness=_wthickness
         if sum(y.get('name')==_name and y.get('deleted')==False for y in Sections.sectiondict)==0:
            Sections.count+=1
            Sections.sectiondict.append({'name':self.name,'type':'ushape','index':Sections.count,'matindex':self.mat,'h':self.h,
                                            'b':self.b,'bthickness':self.bthickness,'wthickness':self.wthickness,'deleted':False})

class Lshape():
    lshapedict=[]
    def __init__(self,_name,_mat,_h,_hthickness,_b,_bthickness):
         self.name=str(_name)
         self.mat=_mat
         self.h=_h
         self.b=_b
         self.bthickness=_bthickness
         self.hthickness=_hthickness
         if sum(y.get('name')==_name and y.get('deleted')==False for y in Sections.sectiondict)==0:
            Sections.count+=1
            Sections.sectiondict.append({'name':self.name,'type':'lshape','index':Sections.count,'matindex':self.mat,
                                            'h':self.h,'b':self.b,'bthickness':self.bthickness,'hthickness':self.hthickness,'deleted':False})

class DLshape():
    lshapedict=[]
    def __init__(self,_name,_mat,_h,_hthickness,_b,_bthickness,_distance):
         self.name=str(_name)
         self.mat=_mat
         self.h=_h
         self.b=_b
         self.bthickness=_bthickness
         self.hthickness=_hthickness
         self.distance=_distance
         if sum(y.get('name')==_name and y.get('deleted')==False for y in Sections.sectiondict)==0:
            Sections.count+=1
            Sections.sectiondict.append({'name':self.name,'type':'dlshape','index':Sections.count,'matindex':self.mat,
                                            'h':self.h,'b':self.b,'bthickness':self.bthickness,'hthickness':self.hthickness,'distance':self.distance,'deleted':False})

class Rectangular():
    rectangulardict=[]
    def __init__(self,_name,_mat,_h,_b,_thickness):
         self.name=str(_name)
         self.mat=_mat
         self.h=_h
         self.b=_b
         self.thickness=_thickness
         if sum(y.get('name')==_name and y.get('deleted')==False for y in Sections.sectiondict)==0:
            Sections.count+=1
            Sections.sectiondict.append({'name':self.name,'type':'rectangular','index':Sections.count,'matindex':self.mat,
                                            'h':self.h,'b':self.b,'thickness':self.thickness,'deleted':False})

class Circular():
    circulardict=[]
    def __init__(self,_name,_mat,_d,_thickness):
         self.name=str(_name)
         self.mat=_mat
         self.d=_d
         self.thickness=_thickness

         if sum(y.get('name')==_name and y.get('deleted')==False for y in Sections.sectiondict)==0:
            Sections.count+=1
            Sections.sectiondict.append({'name':self.name,'type':'circular','index':Sections.count,'matindex':self.mat,
                                            'd':self.d,'thickness':self.thickness,'deleted':False})

class Rectangularbar():
    rectangularbardict=[]
    def __init__(self,_name,_mat,_h,_b):
         self.name=str(_name)
         self.mat=_mat
         self.h=_h
         self.b=_b
         if sum(y.get('name')==_name and y.get('deleted')==False for y in Sections.sectiondict)==0:
            Sections.count+=1
            Sections.sectiondict.append({'name':self.name,'type':'rectangularbar','index':Sections.count,'matindex':self.mat,'h':self.h,'b':self.b,'deleted':False})

class Circularbar():
    circularbardict=[]
    def __init__(self,_name,_mat,_d):
         self.name=str(_name)
         self.mat=_mat
         self.d=_d
         if sum(y.get('name')==_name and y.get('deleted')==False for y in Sections.sectiondict)==0:
            Sections.count+=1
            Sections.sectiondict.append({'name':self.name,'type':'circularbar','index':Sections.count,'matindex':self.mat,'d':self.d,'deleted':False})
