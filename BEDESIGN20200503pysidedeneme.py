from PySide2.QtWidgets import QDialog,QListWidget,QColorDialog,QFontDialog,QFileDialog,QCheckBox,QSpinBox,QDoubleSpinBox,QComboBox, QRadioButton, QAbstractItemView,QStyledItemDelegate,QItemDelegate,QWidget,QTableWidget,QTableWidgetItem,QVBoxLayout,QHBoxLayout,QApplication, QMainWindow, QMdiArea, QAction, QMdiSubWindow, QTextEdit,QOpenGLWidget,QMenu,QShortcut,QLabel,QLineEdit,QSpinBox,QDoubleSpinBox,QPushButton
import sys , os
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from Var import Variables
from Undo import UndoReundo
from FJ import Frame , Joint , Unit , Steel, Concrete ,Materials , Sections,Ishapes,Ushapes,Lshape,Rectangular,Rectangularbar,Circular,Circularbar , DLshape
import numpy as np
import math
from PySide2.QtGui import QPainter, QColor, QFont,QWheelEvent, QIcon ,QPen ,QKeySequence,QCursor,QIntValidator,QDoubleValidator ,QValidator
from PySide2.QtCore import Qt,QRegExp,QLocale

import string
import ast
import logging
# import pyglet.gl as pyleted
# from PIL import Image

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='bedesign.log',
                    filemode='w')

locale = QLocale()
locale1 = QLocale(locale.English, locale.UnitedStates)
locale1.setNumberOptions(locale1.RejectGroupSeparator)
QLocale.setDefault(locale1)

class MDIWindow(QMainWindow):
    subWinDict=[]
    count = 0
    y=0
    x=0
    z=0
    def __init__(self):
        super().__init__()
        self.InitUI()
        self.lockUI()
        self.loadoptions()

    def InitUI(self):
        logging.info("main window started")
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        self.menubar = self.menuBar()
        self.statusBar().showMessage('Ready')
        self.setWindowTitle("BEDESIGN")
        self.setWindowIcon(QIcon('Icons/ekru1_icon.ico'))
        self.toolbarundoact= QAction(QIcon('Icons/undo.png'), "Undo      <Ctrl + Z>", self)
        self.toolbarundoact.triggered.connect(UndoReundo.undo)

        self.toolbarredoact= QAction(QIcon('Icons/redo.png'), "Redo      <Ctrl + Y>", self)
        self.toolbarredoact.triggered.connect(UndoReundo.reundo)

        toolbarnewfile= QAction(QIcon('Icons/newfile.png'), "New      <Ctrl + N>", self)
        toolbarnewfile.triggered.connect(self.newfile)

        toolbaropenfile= QAction(QIcon('Icons/openfile.png'), "Open      <Ctrl + O>", self)
        toolbaropenfile.triggered.connect(self.openFileNameDialog)

        self.toolbarsavefile= QAction(QIcon('Icons/save.png'), "Save      <Ctrl + S>", self)
        self.toolbarsavefile.triggered.connect(self.savefiletrig)

        self.toolbarsaveasfile= QAction(QIcon('Icons/saveas.png'), "Save As      <Ctrl + Shift + S>", self)
        self.toolbarsaveasfile.triggered.connect(self.saveFileDialog)
        
        self.toolbar = self.addToolBar("File Toolbar")
        self.toolbar.addAction(toolbarnewfile)
        self.toolbar.addAction(toolbaropenfile)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.toolbarsavefile)
        self.toolbar.addAction(self.toolbarsaveasfile)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.toolbarundoact)
        self.toolbar.addAction(self.toolbarredoact)        

        filemenu = self.menubar.addMenu("&File")
        filemenu.addAction(toolbarnewfile)
        filemenu.addAction(toolbaropenfile)
        filemenu.addSeparator()
        filemenu.addAction(self.toolbarsavefile)
        filemenu.addAction(self.toolbarsaveasfile)
        filemenu.addSeparator()
        filemenu.addAction(self.toolbarundoact)
        filemenu.addAction(self.toolbarredoact)        

        toolbardrawact= QAction(QIcon('Icons/drawframe.png'), "Draw Frame      <Ctrl + F>", self)
        toolbardrawact.triggered.connect(OpenGLWidget.DrawFrameTrig)
        toolbardeleteframeact= QAction(QIcon('Icons/deleteframe.png'), "Delete Frame      <Delete>", self)
        toolbardeleteframeact.triggered.connect(self.deleteframeTrig)
        self.toolbardraw = self.addToolBar("Draw Toolbar")
        self.toolbardraw.addAction(toolbardrawact)
        self.toolbardraw.addAction(toolbardeleteframeact)
        self.draw = self.menubar.addMenu("&Draw")
        self.draw.addAction(toolbardrawact)
        self.draw.addAction(toolbardeleteframeact)

        toolbarmaterialproperties= QAction( "&Materials", self)
        toolbarmaterialproperties.triggered.connect(self.materialWindowtrig)
        toolbarsectionproperties= QAction( "&Sections", self)
        toolbarsectionproperties.triggered.connect(self.sectionWindowtrig)        
        self.properties = self.menubar.addMenu("&Properties")
        self.properties.addAction(toolbarmaterialproperties)
        self.properties.addAction(toolbarsectionproperties)

        toolbarmoveact= QAction(QIcon('Icons/move.png'), "Move      <Ctrl + M>", self)
        toolbarmoveact.triggered.connect(self.moveWindowTrig)
        toolbarcopyact= QAction(QIcon('Icons/copy.png'), "Copy      <Ctrl + R>", self)
        toolbarcopyact.triggered.connect(self.copyWindowTrig)
        self.toolbarEdit = self.addToolBar("Edit Toolbar")
        self.toolbarEdit.addAction(toolbarmoveact)
        self.toolbarEdit.addAction(toolbarcopyact)
        
        self.edit = self.menubar.addMenu("&Edit")
        self.edit.addAction(toolbarmoveact)
        self.edit.addAction(toolbarcopyact)

        toolbarsupportassign= QAction(QIcon('Icons/support.png'), "Joint Support", self)
        toolbarsupportassign.triggered.connect(self.jointsupportWindowTrig)
        toolbarjointlocalaxes= QAction(QIcon('Icons/jointlocalaxes.png'), "Joint Local Axes", self)
        toolbarjointlocalaxes.triggered.connect(self.jointLocalAxesWinTrig)
        toolbarframesection= QAction(QIcon('Icons/framesection.png'), "Frame Section", self)
        toolbarframesection.triggered.connect(self.framesectionWindowtrig)
        toolbarframelocalaxes= QAction(QIcon('Icons/framelocalaxes.png'), "Frame Local Axes", self)
        toolbarframelocalaxes.triggered.connect(self.frameLocalAxesWinTrig)
        self.Assign = self.menubar.addMenu("&Assign")
        Assignjoint=self.Assign.addMenu("&Joint")
        Assignjoint.addAction(toolbarsupportassign)
        Assignjoint.addAction(toolbarjointlocalaxes)
        Assignframe=self.Assign.addMenu("&Frame")
        Assignframe.addAction(toolbarframesection)
        Assignframe.addAction(toolbarframelocalaxes)

        self.toolbarjointAssign = self.addToolBar("Joint Assignment")
        self.toolbarjointAssign.addAction(toolbarsupportassign)
        self.toolbarjointAssign.addAction(toolbarjointlocalaxes)

        self.toolbarframeAssign = self.addToolBar("Frame Assignment")
        self.toolbarframeAssign.addAction(toolbarframesection)
        self.toolbarframeAssign.addAction(toolbarframelocalaxes)
        
        self.show1 = self.menubar.addMenu("&Show")
        self.show1.addAction(QAction( "Extrude View", self, checkable=True , checked=Variables.showextrudeview))
        self.show1.addSeparator()
        self.show1.addAction(QAction( "Frame Self", self, checkable=True , checked=True))        
        self.show1.addAction(QAction( "Frame Number", self, checkable=True , checked=Variables.framenametextdraw))
        self.show1.addAction(QAction( "Frame Section", self, checkable=True , checked=Variables.showframesectionname))
        self.show1.addAction(QAction( "Frame Local Axes", self, checkable=True , checked=Variables.showframeLocalAxes))
        self.show1.addSeparator()
        self.show1.addAction(QAction( "Joint Self", self, checkable=True , checked=True))        
        self.show1.addAction(QAction( "Joint Number", self, checkable=True , checked=Variables.jointnametextdraw))
        self.show1.addAction(QAction( "Joint Supports", self, checkable=True , checked=Variables.showjointsupport))
        self.show1.addAction(QAction( "Joint Local Axes", self, checkable=True , checked=Variables.showjointLocalAxes))
        self.show1.addAction(QAction( "Joint Node", self, checkable=True , checked=Variables.showjointnode))
        self.show1.addSeparator()
        self.show1.addAction(QAction( "Show Grids", self, checkable=True , checked=Variables.showgrid))
        self.show1.addSeparator()
        self.show1.addAction(QAction( "Show Orgin", self, checkable=True , checked=Variables.showorgin))
        self.show1.triggered[QAction].connect(self.showsTrig)

        toolbarPselect= QAction("Previous Select     <Ctrl + P>", self)
        toolbarPselect.triggered.connect(OpenGLWidget.previousselect)

        toolbarselectAll= QAction("Select All               <Ctrl + A>", self)
        toolbarselectAll.triggered.connect(OpenGLWidget.selectAll)

        toolbarshowselect= QAction("Show Selected Only", self)
        toolbarshowselect.triggered.connect(OpenGLWidget.showselected)

        toolbarhideselect= QAction("Hide Selected", self)
        toolbarhideselect.triggered.connect(OpenGLWidget.hideselected)

        toolbarshowAll= QAction("Show All", self)
        toolbarshowAll.triggered.connect(OpenGLWidget.showAll)

        self.select = self.menubar.addMenu("Se&lection")
        self.select.addAction(toolbarselectAll)
        self.select.addAction(toolbarPselect)
        self.select.addSeparator()
        self.select.addAction(toolbarshowselect)
        self.select.addAction(toolbarhideselect)
        self.select.addAction(toolbarshowAll)

        toolbaraddGrid= QAction(QIcon('Icons/grids.png'),"Edit Grid", self)
        toolbaraddGrid.triggered.connect(self.gridWindowTrig)
        self.grid = self.menubar.addMenu("&Grid")
        self.grid.addAction(toolbaraddGrid)

        self.toolbarGrids = self.addToolBar("Grid Toolbar")
        self.toolbarGrids.addAction(toolbaraddGrid)

        toolbar3d= QAction(QIcon('Icons/3d.png'),"3D View", self)
        toolbar3d.triggered.connect(self.view3dTrig)
        toolbarxz= QAction(QIcon('Icons/xz.png'),"XZ Plan", self)
        toolbarxz.triggered.connect(self.viewxzTrig)
        toolbaryz= QAction(QIcon('Icons/yz.png'),"YZ Plan", self)
        toolbaryz.triggered.connect(self.viewyzTrig)
        toolbarxy= QAction(QIcon('Icons/xy.png'),"XY Plan", self)
        toolbarxy.triggered.connect(self.viewxyTrig)
        toolbarleft= QAction(QIcon('Icons/left.png'),"Previous Plan", self)
        toolbarleft.triggered.connect(self.viewpreviousplanTrig)
        toolbarright= QAction(QIcon('Icons/right.png'),"Next Plan", self)
        toolbarright.triggered.connect(self.viewnextplanTrig)
        
        self.view = self.menubar.addMenu("&View")
        self.view.addAction(toolbar3d)
        self.view.addAction(toolbarxz)
        self.view.addAction(toolbaryz)
        self.view.addAction(toolbarxy)
        self.view.addAction(toolbarleft)
        self.view.addAction(toolbarright)

        self.toolbarview = self.addToolBar("View Toolbar")
        self.toolbarview.addAction(toolbar3d)
        self.toolbarview.addAction(toolbarxz)
        self.toolbarview.addAction(toolbaryz)
        self.toolbarview.addAction(toolbarxy)
        self.toolbarview.addAction(toolbarleft)
        self.toolbarview.addAction(toolbarright)

        self.window = self.menubar.addMenu("&Window")
        self.window.addAction("Add New Window")
        self.window.addAction("Tile All Windows")
        self.window.triggered[QAction].connect(self.WindowTrig)

        optionsthemes= QAction("Themes", self)
        optionsthemes.triggered.connect(self.themesWindowTrig)
        optionsdimensions= QAction("Dimensions", self)
        optionsdimensions.triggered.connect(self.dimensionsWindowTrig)
        self.options1 = self.menubar.addMenu("&Options")
        self.options1.addAction(optionsthemes)
        self.options1.addAction(optionsdimensions)

        self.hepmenu = self.menubar.addMenu("&Help")

        self.combounit=QComboBox()
        self.toolbarunit = self.addToolBar("Unit Toolbar")
        self.toolbarunit.addWidget(self.combounit)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)
        logging.info("main window ended")
    
    def on_combobox_changed(self,index):
        Unit.index(self,index)
        try:
            mdi.movewindlg.text1.setText(str(Unit.dimension(self,float(mdi.movewindlg.text1.text()),2)))
            mdi.movewindlg.text2.setText(str(Unit.dimension(self,float(mdi.movewindlg.text2.text()),2)))
            mdi.movewindlg.text3.setText(str(Unit.dimension(self,float(mdi.movewindlg.text3.text()),2)))
        except:
            print("move win is not exist")
        try:
            mdi.CopyWindlg.text1.setText(str(Unit.dimension(self,float(mdi.CopyWindlg.text1.text()),2)))
            mdi.CopyWindlg.text2.setText(str(Unit.dimension(self,float(mdi.CopyWindlg.text2.text()),2)))
            mdi.CopyWindlg.text3.setText(str(Unit.dimension(self,float(mdi.CopyWindlg.text3.text()),2)))
        except:
            print("copy win is not exist")

    def loadoptions(self):
        dir_path = dir_path = os.path.dirname(os.path.realpath(__file__))
        real_path =dir_path+"/options.ini"
        if os.path.exists(real_path):
            with open(real_path, 'r') as reader:
                loadoptionsdict=ast.literal_eval(reader.read())
                Variables.textfont=loadoptionsdict['textfont']
                Variables.bubletextwidth=loadoptionsdict['bubletextwidth']
                Variables.localaxescale=loadoptionsdict['localaxescale']
                Variables.supportscale=loadoptionsdict['supportscale']
                Variables.framewidth=loadoptionsdict['framewidth']
                Variables.pointwidth=loadoptionsdict['pointwidth']
                Variables.pickingrange=loadoptionsdict['pickingrange']
                Variables.pingrange=loadoptionsdict['pingrange']
                Variables.pinsize=loadoptionsdict['pinsize']
                Variables.selectedpointsize=loadoptionsdict['selectedpointsize']
                Variables.blackorwhitetheme=loadoptionsdict['blackorwhitetheme']

                Variables.wframeColor=loadoptionsdict['wframeColor']
                Variables.wpointColor=loadoptionsdict['wpointColor']
                Variables.wselectedframecolor=loadoptionsdict['wselectedframecolor']
                Variables.wpreframecolor=loadoptionsdict['wpreframecolor']
                Variables.wselectrectanglecolor=loadoptionsdict['wselectrectanglecolor']
                Variables.wselectedpointcolor=loadoptionsdict['wselectedpointcolor']
                
                Variables.wpincolor=loadoptionsdict['wpincolor']
                Variables.wsupportcolor=loadoptionsdict['wsupportcolor']
                Variables.wgridcolor=loadoptionsdict['wgridcolor']
                Variables.wbubletextcolor=loadoptionsdict['wbubletextcolor']
                Variables.wtextcolor=loadoptionsdict['wtextcolor']

                Variables.bframeColor=loadoptionsdict['bframeColor']
                Variables.bpointColor=loadoptionsdict['bpointColor']
                Variables.bselectedframecolor=loadoptionsdict['bselectedframecolor']
                Variables.bpreframecolor=loadoptionsdict['bpreframecolor']
                Variables.bselectrectanglecolor=loadoptionsdict['bselectrectanglecolor']
                Variables.bselectedpointcolor=loadoptionsdict['bselectedpointcolor']
                Variables.bpincolor=loadoptionsdict['bpincolor']
                Variables.bsupportcolor=loadoptionsdict['bsupportcolor']
                Variables.bgridcolor=loadoptionsdict['bgridcolor']
                Variables.bbubletextcolor=loadoptionsdict['bbubletextcolor']
                Variables.btextcolor=loadoptionsdict['btextcolor']

            if Variables.blackorwhitetheme==0:
                Variables.clearcolorfloat=(1,1,1,0)
                Variables.frameColor=Variables.wframeColor
                Variables.pointColor=Variables.wpointColor
                Variables.selectedframecolor=Variables.wselectedframecolor
                Variables.preframecolor=Variables.wpreframecolor
                Variables.selectrectanglecolor=Variables.wselectrectanglecolor
                Variables.selectedpointcolor=Variables.wselectedpointcolor
                Variables.pincolor=Variables.wpincolor                
                Variables.supportcolor=Variables.wsupportcolor
                Variables.gridcolor=Variables.wgridcolor
                Variables.bubletextcolor=Variables.wbubletextcolor
                Variables.textcolor=Variables.wtextcolor
            else:
                Variables.clearcolorfloat=(0,0,0,0)
                Variables.frameColor=Variables.bframeColor
                Variables.pointColor=Variables.bpointColor
                Variables.selectedframecolor=Variables.bselectedframecolor
                Variables.preframecolor=Variables.bpreframecolor
                Variables.selectrectanglecolor=Variables.bselectrectanglecolor
                Variables.selectedpointcolor=Variables.bselectedpointcolor
                Variables.pincolor=Variables.bpincolor
                Variables.supportcolor=Variables.bsupportcolor
                Variables.gridcolor=Variables.bgridcolor
                Variables.bubletextcolor=Variables.bbubletextcolor
                Variables.textcolor=Variables.btextcolor

    def lockUI(self):
        self.toolbardraw.setEnabled(False)
        self.toolbarEdit.setEnabled(False)
        self.toolbarframeAssign.setEnabled(False)
        self.toolbarGrids.setEnabled(False)
        self.toolbarjointAssign.setEnabled(False)
        self.toolbarview.setEnabled(False)
        self.view.setEnabled(False)
        self.grid.setEnabled(False)
        self.select.setEnabled(False)
        self.show1.setEnabled(False)
        self.Assign.setEnabled(False)
        self.edit.setEnabled(False)
        self.draw.setEnabled(False)
        self.window.setEnabled(False)
        self.toolbarundoact.setEnabled(False)
        self.toolbarsavefile.setEnabled(False)
        self.toolbarsaveasfile.setEnabled(False)
        self.toolbarredoact.setEnabled(False)
        self.toolbarunit.setEnabled(False)
        self.options1.setEnabled(False)
        self.properties.setEnabled(False)

    def unlockUI(self):
        self.toolbardraw.setEnabled(True)
        self.toolbarEdit.setEnabled(True)
        self.toolbarframeAssign.setEnabled(True)
        self.toolbarGrids.setEnabled(True)
        self.toolbarjointAssign.setEnabled(True)
        self.toolbarview.setEnabled(True)
        self.view.setEnabled(True)
        self.grid.setEnabled(True)
        self.select.setEnabled(True)
        self.show1.setEnabled(True)
        self.Assign.setEnabled(True)
        self.edit.setEnabled(True)
        self.draw.setEnabled(True)
        self.window.setEnabled(True)
        self.toolbarundoact.setEnabled(True)
        self.toolbarsavefile.setEnabled(True)
        self.toolbarsaveasfile.setEnabled(True)
        self.toolbarredoact.setEnabled(True)
        self.toolbarunit.setEnabled(True)
        self.options1.setEnabled(True)
        self.properties.setEnabled(True)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_O and event.modifiers() == Qt.ControlModifier:
            mdi.openFileNameDialog()        
        if event.key() == Qt.Key_N and event.modifiers() == Qt.ControlModifier:
            mdi.newfile()

    def view3dTrig(self,p):
        for windows in self.mdi.subWindowList():
            if self.mdi.focusWidget().windowTitle()==windows.windowTitle():
                windows.widget().view['3d']=True
                x = windows.windowTitle().split("/", 1)
                self.mdi.focusWidget().setWindowTitle(x[0]+"/3D view")
                self.x=0
                self.y=0
                self.z=0

    def viewxzTrig(self,p):
        for windows in self.mdi.subWindowList():
            if self.mdi.focusWidget().windowTitle()==windows.windowTitle():
                windows.widget().view['3d']=False
                windows.widget().view['closed']='Y'
                self.x=0
                self.y=0
                self.z=0
                if Variables.gridy != None:
                    windows.widget().view['yaxeloc']=Variables.gridy[0][1]
                else:
                    windows.widget().view['yaxeloc']=0
                y = windows.windowTitle().split("/", 1)
                self.mdi.focusWidget().setWindowTitle(y[0]+"/XZ-"+str(windows.widget().view['yaxeloc']))

    def viewyzTrig(self,p):
        for windows in self.mdi.subWindowList():
            if self.mdi.focusWidget().windowTitle()==windows.windowTitle():
                windows.widget().view['3d']=False
                windows.widget().view['closed']='X'
                self.x=0
                self.y=0
                self.z=0
                if Variables.gridx != None:
                    windows.widget().view['xaxeloc']=Variables.gridx[0][1]
                else:
                    windows.widget().view['xaxeloc']=0
                x = windows.windowTitle().split("/", 1)
                self.mdi.focusWidget().setWindowTitle(x[0]+"/YZ-"+str(windows.widget().view['xaxeloc']))

    def viewxyTrig(self,p):
        for windows in self.mdi.subWindowList():
            if self.mdi.focusWidget().windowTitle()==windows.windowTitle():
                windows.widget().view['3d']=False
                windows.widget().view['closed']='Z'
                self.x=0
                self.y=0
                self.z=0
                if Variables.gridz != []:
                    windows.widget().view['zaxeloc']=Variables.gridz[0][1]
                else:
                    windows.widget().view['zaxeloc']=0
                z = windows.windowTitle().split("/", 1)
                self.mdi.focusWidget().setWindowTitle(z[0]+"/XY-"+str(windows.widget().view['zaxeloc']))

    def viewnextplanTrig(self,p):
        #TODO: bu kısımda grid lerden çekmeli
        for windows in self.mdi.subWindowList():
            if self.mdi.focusWidget().windowTitle()==windows.windowTitle():
                if windows.widget().view['3d']==False:
                    if windows.widget().view['closed']=='Y':
                        if windows.widget().view['yaxeloc'] < Variables.gridy[len(Variables.gridy)-1][1]:   
                            self.y +=1                            
                            windows.widget().view['yaxeloc']=Variables.gridy[self.y][1]
                            x = windows.windowTitle().split("/", 1)
                            self.mdi.focusWidget().setWindowTitle(x[0]+"/XZ-"+str(windows.widget().view['yaxeloc']))
                    elif windows.widget().view['closed']=='X':
                        if windows.widget().view['xaxeloc'] < Variables.gridx[len(Variables.gridx)-1][1]:   
                            self.x +=1                         
                            windows.widget().view['xaxeloc']=Variables.gridx[self.x][1]
                            x = windows.windowTitle().split("/", 1)
                            self.mdi.focusWidget().setWindowTitle(x[0]+"/YZ-"+str(windows.widget().view['xaxeloc']))
                    elif windows.widget().view['closed']=='Z':
                        if windows.widget().view['zaxeloc'] < Variables.gridz[len(Variables.gridz)-1][1]:   
                            self.z +=1                         
                            windows.widget().view['zaxeloc']=Variables.gridz[self.z][1]
                            x = windows.windowTitle().split("/", 1)
                            self.mdi.focusWidget().setWindowTitle(x[0]+"/XY-"+str(windows.widget().view['zaxeloc']))

    def viewpreviousplanTrig(self,p):
        for windows in self.mdi.subWindowList():
            if self.mdi.focusWidget().windowTitle()==windows.windowTitle():
                if windows.widget().view['3d']==False:
                    if windows.widget().view['closed']=='Y':
                        if windows.widget().view['yaxeloc'] > Variables.gridy[0][1]: 
                            self.y -=1
                            #TODO: gridspan olarak yapmaya kalkarsam += olacak
                            windows.widget().view['yaxeloc']=Variables.gridy[self.y][1]                                
                            x = windows.windowTitle().split("/", 1)
                            self.mdi.focusWidget().setWindowTitle(x[0]+"/XZ-"+str(windows.widget().view['yaxeloc']))
                    elif windows.widget().view['closed']=='X':
                        if windows.widget().view['xaxeloc'] > Variables.gridx[0][1]: 
                            self.x -=1                               
                            windows.widget().view['xaxeloc']=Variables.gridx[self.x][1]
                            x = windows.windowTitle().split("/", 1)
                            self.mdi.focusWidget().setWindowTitle(x[0]+"/YZ-"+str(windows.widget().view['xaxeloc']))
                    elif windows.widget().view['closed']=='Z':
                        if windows.widget().view['zaxeloc'] > Variables.gridz[0][1]: 
                            self.z -=1                               
                            windows.widget().view['zaxeloc']=Variables.gridz[self.z][1]
                            x = windows.windowTitle().split("/", 1)
                            self.mdi.focusWidget().setWindowTitle(x[0]+"/XY-"+str(windows.widget().view['zaxeloc']))

    def gridWindowTrig(self):
        self.griddlg = GridWin(self)
        self.griddlg.exec_()

    def themesWindowTrig(self):
        self.themesdlg = ThemesWindow(self)
        self.themesdlg.exec_()
    
    def dimensionsWindowTrig(self):
        self.dimensionsdlg = DimensionsWindow(self)
        self.dimensionsdlg.exec_()

    def moveWindowTrig(self):
        self.movewindlg = MoveWin(self)
        self.movewindlg.show()
    
    def copyWindowTrig(self):
        self.CopyWindlg = CopyWin(self)
        self.CopyWindlg.show()        

    def deleteframeTrig(self):
        Frame.deleteFrame()
        self.sub.selectionClear()
        self.statusBar().showMessage('Selected frames deleted!')

    def showsTrig(self,p):
        if p.text() == "Frame Self":
            if p.isChecked()==False:
                OpenGLWidget.selectionClear()
                for frame in Frame.framedict:
                    frame['show']=False
            elif p.isChecked():
                for frame in Frame.framedict:
                    frame['show']=True
        elif p.text() == "Frame Number":
            if p.isChecked()==False:
                Variables.framenametextdraw=False
            elif p.isChecked():
                Variables.framenametextdraw=True
        elif p.text() == "Joint Self":
            if p.isChecked()==False:
                OpenGLWidget.selectionClear()
                for joint in Joint.jointdict:
                    joint['show']=False
            elif p.isChecked():
                for joint in Joint.jointdict:
                    joint['show']=True
        elif p.text() == "Joint Number":
            if p.isChecked()==False:
                Variables.jointnametextdraw=False
            elif p.isChecked():
                Variables.jointnametextdraw=True
        elif p.text() == "Show Grids":
            if p.isChecked()==False:
                Variables.showgrid=False
            elif p.isChecked():
                Variables.showgrid=True
        elif p.text() == "Show Orgin":
            if p.isChecked()==False:
                Variables.showorgin=False
            elif p.isChecked():
                Variables.showorgin=True
        elif p.text() == "Joint Node":
            if p.isChecked()==False:
                Variables.showjointnode=False
            elif p.isChecked():
                Variables.showjointnode=True
        elif p.text() == "Joint Supports":
            if p.isChecked()==False:
                Variables.showjointsupport=False
            elif p.isChecked():
                Variables.showjointsupport=True
        elif p.text() == "Joint Local Axes":
            if p.isChecked()==False:
                Variables.showjointLocalAxes=False
            elif p.isChecked():
                Variables.showjointLocalAxes=True
        elif p.text() == "Frame Local Axes":
            if p.isChecked()==False:
                Variables.showframeLocalAxes=False
            elif p.isChecked():
                Variables.showframeLocalAxes=True
        elif p.text() == "Frame Section":
            if p.isChecked()==False:
                Variables.showframesectionname=False
            elif p.isChecked():
                Variables.showframesectionname=True
        elif p.text() == "Extrude View":
            if p.isChecked()==False:
                Variables.showextrudeview=False
            elif p.isChecked():
                Variables.showextrudeview=True
        
    def WindowTrig(self, p):
        if p.text() == "Add New Window":
            MDIWindow.count = MDIWindow.count + 1
            self.sub = OpenGLWidget()
            self.sub.setWindowIcon(QIcon('Icons/ekru1_icon.ico'))
            self.sub.setWindowTitle( "Window-"+str(MDIWindow.count)+"/3D view" )
            self.mdi.addSubWindow(self.sub)            
            self.sub.setFocusPolicy(Qt.StrongFocus)
            self.sub.view['3d']=True
            self.sub.show()
            self.mdi.tileSubWindows()
            self.statusBar().showMessage('New Window Created!')            
        if p.text() == "Tile All Windows":
            self.mdi.tileSubWindows()

    def jointsupportWindowTrig(self):
        JointSupportWindlg = JointSupportWin(self)
        JointSupportWindlg.show()
    
    def jointLocalAxesWinTrig(self):
        JointLocalAxesWindlg = JointLocalAxesWin(self)
        JointLocalAxesWindlg.show()
    
    def frameLocalAxesWinTrig(self):
        FrameLocalAxesWindlg = FrameLocalAxesWin(self)
        FrameLocalAxesWindlg.show()

    def savefiletrig(self):
        if Variables.path==None:
            self.saveFileDialog()
        else:
            Savefile(Variables.path)

    def saveFileDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save","","bedesign file(*.bedb)", options=options)
        if fileName:
            if fileName.split(".")[-1]=="bedb":
                path=fileName
            else:
                path=fileName+".bedb"

            projectname=path.split("/")
            Variables.path=path
            Variables.projectname=projectname[-1].split(".")[0]
            mdi.setWindowTitle("BEDESIGN-"+Variables.projectname)
            Savefile(path)
    
    def openFileNameDialog(self):
        try:
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self,"Open", "","bedesign file(*.bedb)", options=options)
            if fileName:
                if fileName.split(".")[-1]=="bedb":
                    path=fileName
                else:
                    path=fileName+".bedb"

                projectname=path.split("/")
                Variables.path=path
                Variables.projectname=projectname[-1].split(".")[0]            
                OpenFile(path)
        except Exception as e:
            logging.debug(e)

    def newfile(self):
        quicstartdlg = QuickStartWindow(self)
        quicstartdlg.exec_()

    def materialWindowtrig(self):
        self.materialsdlg = MaterialWindow(self)
        self.materialsdlg.exec_()

    def sectionWindowtrig(self):
        self.sectiondlg = SectionWindow(self)
        self.sectiondlg.exec_()
    
    def framesectionWindowtrig(self):
        self.framesectiondlg = FrameSectionWindow(self)
        self.framesectiondlg.show()

class CopyWin(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(CopyWin, self).__init__(*args, **kwargs)
        self.title = 'Copy'
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 200
        self.height = 160        
        self.initUI()
    
    def initUI(self):
        logging.info("Copy Window started")
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
        

        button_apply=QPushButton(self)
        button_apply.setGeometry(20,130,50,22)
        button_apply.setText("APPLY")
        button_apply.clicked.connect(self.on_click_apply)

        button_ok=QPushButton(self)
        button_ok.setGeometry(75,130,50,22)
        button_ok.setText("OK")
        button_ok.clicked.connect(self.on_click_ok)
        
        button_cancel=QPushButton(self)
        button_cancel.setGeometry(130,130,50,22)
        button_cancel.setText("CANCEL")
        button_cancel.clicked.connect(self.on_click_cancel)

        label1 = QLabel(self)
        label1.setGeometry(20,20,100,20)
        label1.setText("X:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,100,20)
        label2.setText("Y:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,100,20)
        label3.setText("Z:")
        label4 = QLabel(self)
        label4.setGeometry(20,80,100,20)
        label4.setText("Number of copy:")

        valid = QDoubleValidator(-99999.9999,99999.9999,4,self)
        valid.setNotation(QDoubleValidator.StandardNotation)

        self.text1 = QLineEdit(self)
        self.text1.setGeometry(35,22,100,18)
        self.text1.setValidator(valid)
        self.text1.setText(str( Unit.dimension(self,Variables.xdistanceforMove,0)))

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(35,42,100,18)
        self.text2.setValidator(valid)
        self.text2.setText(str( Unit.dimension(self,Variables.ydistanceforMove,0)))

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(35,62,100,18)
        self.text3.setValidator(valid)
        self.text3.setText(str( Unit.dimension(self,Variables.zdistanceforMove,0)))

        self.text4 = QLineEdit(self)
        self.text4.setGeometry(105,82,30,18)
        self.text4.setValidator(QIntValidator(0,39,self))
        self.text4.setText(str(Variables.numberofcopy))        

        button_pick=QPushButton(self)
        button_pick.setGeometry(20,105,160,22)
        button_pick.setText("Pick from window")
        button_pick.clicked.connect(self.on_click_pick)
        logging.info("Copy Window ended")

    def on_click_apply(self):
        self.copy()

    def on_click_ok(self):
        self.copy()
        self.close()

    def on_click_cancel(self):
        self.close()

    def closeEvent(self,event):
        Variables.xdistanceforMove= Unit.dimension(self, float(self.text1.text()),1)
        Variables.ydistanceforMove= Unit.dimension(self, float(self.text2.text()),1)
        Variables.zdistanceforMove= Unit.dimension(self, float(self.text3.text()),1)
        Variables.numberofcopy=self.text4.text()              
        self.close()

    def on_click_pick(self):
        if Variables.isDrawing==False:
            Variables.ispickingPoint=True
            Variables.ismovepicking=False
            Variables.iscopypicking=True
            if Variables.ispickingPoint:
                self.setEnabled(False)
                QApplication.setOverrideCursor(Qt.CrossCursor)                
                mdi.statusBar().showMessage('Move: Pick First Point')
    
    def copy(self):
        logging.info("Move function started")
        try:
            if Variables.isDrawing==False:
                if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!="" and self.text4.text()!="" :
                    if Variables.selectedFrames!=[]:
                        if (float(self.text1.text())==0 and float(self.text2.text())==0 and float(self.text3.text())==0)==False :
                        
                            undoobj=[]                    
                            for i in range(1,int(self.text4.text())+1):
                                for newframe in Variables.selectedFrames:
                                    destinationPoint1=0
                                    destinationPoint2=0
                                    new1=False
                                    new2=False
                                    copiedjoint1=None
                                    copiedjoint2=None
                                    for joint in Joint.jointdict:                                    
                                        if joint['deleted']!=True:
                                            if newframe['joint0']==joint['name']:
                                                for jointselected1 in Variables.selectedJoints:
                                                    if jointselected1['name']==newframe['joint0']:
                                                        new1=True
                                                copiedjoint1=joint
                                                destinationPoint1=(joint['coords'][0]+i*Unit.dimension(self, float(self.text1.text()),1),joint['coords'][1]-i*Unit.dimension(self, float(self.text3.text()),1),joint['coords'][2]+i*Unit.dimension(self, float(self.text2.text()),1))
                                            if newframe['joint1']==joint['name']:
                                                for jointselected2 in Variables.selectedJoints:
                                                    if jointselected2['name']==newframe['joint1']:
                                                        new2=True
                                                copiedjoint2=joint
                                                destinationPoint2=(joint['coords'][0]+i*Unit.dimension(self, float(self.text1.text()),1),joint['coords'][1]-i*Unit.dimension(self, float(self.text3.text()),1),joint['coords'][2]+i*Unit.dimension(self, float(self.text2.text()),1))
                                    for joint1 in Joint.jointdict:
                                        if joint1['deleted']==False:
                                            if joint1['coords']==destinationPoint1:
                                                new1=False
                                            if joint1['coords']==destinationPoint2:
                                                new2=False
                                    if destinationPoint1!=0 and destinationPoint2!=0:
                                        frame=Frame(destinationPoint1,destinationPoint2)
                                        for frame1 in Frame.framedict:
                                            if frame1['name']== frame.id+1:
                                                #framein özelliklerini kopyalama
                                                frame1['angle']=newframe['angle']
                                                frame1['section']=newframe['section']
                                        for joint2 in Joint.jointdict:
                                            if joint2['deleted']==False:
                                                if joint2['coords']==destinationPoint1:
                                                    if new1:
                                                        joint2['restraints']=copiedjoint1['restraints']
                                                        joint2['angle1']=copiedjoint1['angle1']
                                                        joint2['angle2']=copiedjoint1['angle2']
                                                        joint2['angle3']=copiedjoint1['angle3']
                                                if joint2['coords']==destinationPoint2:
                                                    if new2:
                                                        joint2['restraints']=copiedjoint2['restraints']
                                                        joint2['angle1']=copiedjoint2['angle1']
                                                        joint2['angle2']=copiedjoint2['angle2']
                                                        joint2['angle3']=copiedjoint2['angle3']
                                        try:
                                            for newundoobj in UndoReundo.undodict[-1]: # son undo listesindekileri şuan oluşturduğumuz undo listesine aktarıyoruz
                                                undoobj.append(newundoobj)
                                            UndoReundo.undodict.remove(UndoReundo.undodict[-1]) # sonra siliyoruz
                                        except:
                                            print('sadasd')
                            UndoReundo(undoobj)
                            OpenGLWidget.selectionClear()
                            mdi.statusBar().showMessage('')
        except Exception as e:
            logging.debug(e)
        logging.info("Move function ended")

class JointLocalAxesWin(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(JointLocalAxesWin, self).__init__(*args, **kwargs)
        self.title = 'Joint Local Axes Rotate'
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 200
        self.height = 160
        self.initUI()
    
    def initUI(self):
        logging.info("Joint local axes Window started")
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
        

        button_apply=QPushButton(self)
        button_apply.setGeometry(20,130,50,22)
        button_apply.setText("APPLY")
        button_apply.clicked.connect(self.on_click_apply)

        button_ok=QPushButton(self)
        button_ok.setGeometry(75,130,50,22)
        button_ok.setText("OK")
        button_ok.clicked.connect(self.on_click_ok)
        
        button_cancel=QPushButton(self)
        button_cancel.setGeometry(130,130,50,22)
        button_cancel.setText("CANCEL")
        button_cancel.clicked.connect(self.on_click_cancel)

        label4 = QLabel(self)
        label4.setGeometry(20,20,150,20)
        label4.setText("Joint Local Axes Rotate")

        label1 = QLabel(self)
        label1.setGeometry(20,40,100,20)
        label1.setText("Rotation About X:")
        label2 = QLabel(self)
        label2.setGeometry(20,60,100,20)
        label2.setText("Rotation About Y:")
        label3 = QLabel(self)
        label3.setGeometry(20,80,100,20)
        label3.setText("Rotation About Z:")        

        valid = QDoubleValidator(-999.99,999.99,2,self)
        valid.setNotation(QDoubleValidator.StandardNotation)

        self.text1 = QLineEdit(self)
        self.text1.setGeometry(110,42,50,18)
        self.text1.setValidator(valid)
        self.text1.setText(str(Variables.jointLocalAxe1))

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(110,62,50,18)
        self.text2.setValidator(valid)
        self.text2.setText(str(Variables.jointLocalAxe2))

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(110,82,50,18)
        self.text3.setValidator(valid)
        self.text3.setText(str(Variables.jointLocalAxe3))
        logging.info("Joint local axes Window ended")

    def on_click_apply(self):
        self.change_angle()

    def on_click_ok(self):
        self.change_angle()
        self.close()

    def on_click_cancel(self):
        self.close()
    
    def change_angle(self):
        if Variables.selectedJoints!=[]:
            if self.text1.text() !="" and self.text2.text()!='' and self.text3.text()!='' :
                Variables.jointLocalAxe1=float(self.text1.text())
                Variables.jointLocalAxe2=float(self.text2.text())
                Variables.jointLocalAxe3=float(self.text3.text())
                undoobj=[]
                for joint in Variables.selectedJoints:
                    if joint['show'] and joint['deleted']==False:
                        undoobj.append((joint,'angle1',joint['angle1'],Variables.jointLocalAxe1))
                        undoobj.append((joint,'angle2',joint['angle2'],Variables.jointLocalAxe2))
                        undoobj.append((joint,'angle3',joint['angle3'],Variables.jointLocalAxe3))
                        joint['angle1']=Variables.jointLocalAxe1
                        joint['angle2']=Variables.jointLocalAxe2
                        joint['angle3']=Variables.jointLocalAxe3
                UndoReundo(undoobj)
                OpenGLWidget.selectionClear()
                mdi.statusBar().showMessage('')

class FrameLocalAxesWin(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(FrameLocalAxesWin, self).__init__(*args, **kwargs)
        self.title = 'Frame Local Axes Rotate'
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 200
        self.height = 140
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
        

        button_apply=QPushButton(self)
        button_apply.setGeometry(20,110,50,22)
        button_apply.setText("APPLY")
        button_apply.clicked.connect(self.on_click_apply)

        button_ok=QPushButton(self)
        button_ok.setGeometry(75,110,50,22)
        button_ok.setText("OK")
        button_ok.clicked.connect(self.on_click_ok)
        
        button_cancel=QPushButton(self)
        button_cancel.setGeometry(130,110,50,22)
        button_cancel.setText("CANCEL")
        button_cancel.clicked.connect(self.on_click_cancel)

        label4 = QLabel(self)
        label4.setGeometry(20,20,170,20)
        label4.setText("Frame Local Axes Rotate")

        label1 = QLabel(self)
        label1.setGeometry(20,40,110,20)
        label1.setText("Rotation Angle:")
        
        valid = QDoubleValidator(-999.99,999.99,2,self)
        valid.setNotation(QDoubleValidator.StandardNotation)

        self.text1 = QLineEdit(self)
        self.text1.setGeometry(110,42,50,18)
        self.text1.setValidator(valid)
        self.text1.setText(str(Variables.frameLocalAxe))

        button_pick=QPushButton(self)
        button_pick.setGeometry(20,85,160,22)
        button_pick.setText("Change Frame Direction")
        button_pick.clicked.connect(self.on_click_change_dir)

    def on_click_apply(self):
        self.change_angle()

    def on_click_ok(self):
        self.change_angle()
        self.close()

    def on_click_cancel(self):
        self.close()
    
    def on_click_change_dir(self):
        if Variables.selectedFrames!=[]:
            undoobj=[]
            for frame in Variables.selectedFrames:
                if frame['deleted']==False and frame['show']:
                    taken0=frame['joint0']
                    taken1=frame['joint1']
                    undoobj.append((frame,'joint0',taken0,taken1))
                    undoobj.append((frame,'joint1',taken1,taken0))
                    frame['joint0']=taken1
                    frame['joint1']=taken0
            UndoReundo(undoobj)
            OpenGLWidget.selectionClear()
            mdi.statusBar().showMessage('')
    
    def change_angle(self):
        if Variables.selectedFrames!=[]:
            if self.text1.text() !="":
                Variables.frameLocalAxe=float(self.text1.text())               
                undoobj=[]
                for frame in Variables.selectedFrames:
                    if frame['deleted']==False and frame['show']:
                        undoobj.append((frame,'angle',frame['angle'],Variables.frameLocalAxe))                        
                        frame['angle']=Variables.frameLocalAxe                        
                UndoReundo(undoobj)
                OpenGLWidget.selectionClear()
                mdi.statusBar().showMessage('')

class MoveWin(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(MoveWin, self).__init__(*args, **kwargs)
        
        self.title = 'Move'
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 200
        self.height = 140        
        self.initUI()
    
    def initUI(self):
        logging.info("Move Window started")
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
        

        button_apply=QPushButton(self)
        button_apply.setGeometry(20,110,50,22)
        button_apply.setText("APPLY")
        button_apply.clicked.connect(self.on_click_apply)

        button_ok=QPushButton(self)
        button_ok.setGeometry(75,110,50,22)
        button_ok.setText("OK")
        button_ok.clicked.connect(self.on_click_ok)
        
        button_cancel=QPushButton(self)
        button_cancel.setGeometry(130,110,50,22)
        button_cancel.setText("CANCEL")
        button_cancel.clicked.connect(self.on_click_cancel)

        label1 = QLabel(self)
        label1.setGeometry(20,20,100,20)
        label1.setText("X:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,100,20)
        label2.setText("Y:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,100,20)
        label3.setText("Z:")

        valid = QDoubleValidator(-99999.9999,99999.9999,2,self)
        valid.setNotation(QDoubleValidator.StandardNotation)

        self.text1 = QLineEdit(self)
        self.text1.setGeometry(35,22,100,18)
        self.text1.setValidator(valid)
        self.text1.setText(str( Unit.dimension(self,Variables.xdistanceforMove,0)))

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(35,42,100,18)
        self.text2.setValidator(valid)
        self.text2.setText(str( Unit.dimension(self,Variables.ydistanceforMove,0)))

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(35,62,100,18)
        self.text3.setValidator(valid)
        self.text3.setText(str( Unit.dimension(self,Variables.zdistanceforMove,0)))

        button_pick=QPushButton(self)
        button_pick.setGeometry(20,85,160,22)
        button_pick.setText("Pick from window")
        button_pick.clicked.connect(self.on_click_pick)
        logging.info("Move Window ended")

    def on_click_apply(self):
        self.move()

    def on_click_ok(self):
        self.move()
        self.close()

    def on_click_cancel(self):
        self.close()
    
    def on_click_pick(self):
        if Variables.isDrawing==False:
            Variables.ispickingPoint=True
            Variables.ismovepicking=True
            Variables.iscopypicking=False
            if Variables.ispickingPoint:
                self.setEnabled(False)
                QApplication.setOverrideCursor(Qt.CrossCursor)                
                mdi.statusBar().showMessage('Move: Pick First Point')
    
    def closeEvent(self,event):
        Variables.xdistanceforMove= Unit.dimension(self, float(self.text1.text()),1)
        Variables.ydistanceforMove= Unit.dimension(self, float(self.text2.text()),1)
        Variables.zdistanceforMove= Unit.dimension(self, float(self.text3.text()),1)
        self.close()
    
    def move(self):
        logging.info("Move function started")
        try:
            if Variables.isDrawing==False:
                if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!="" :
                    if Variables.selectedFrames!=[] or Variables.selectedJoints!=[]:
                        if (float(self.text1.text())==0 and float(self.text2.text())==0 and float(self.text3.text())==0)==False :
                            undoobj=[]
                            onePointSelectedFrames=[]
                            twoPointSelectedFrames=[]
                            noPointSelectedFrames=[]

                            #seçili noktalara bağlı framelerin diğer noktaları da seçili mi diye bakacak
                            for frameSelected in Variables.selectedFrames:
                                for jointSelected in Variables.selectedJoints:
                                    if frameSelected['joint0']==jointSelected['name']: #başlangıç noktası seçili frame
                                        endpointselected=0
                                        for jointSelected1 in Variables.selectedJoints:
                                            if frameSelected['joint1']==jointSelected1['name']: #başlangıç noktası seçili frame in bitiş noktasıda seçili.
                                                endpointselected=1
                                                if twoPointSelectedFrames.count(frameSelected)==False:
                                                    twoPointSelectedFrames.append(frameSelected)
                                                    #print("iki nokta da seçili",frameSelected)
                                        if endpointselected==0:
                                            onePointSelectedFrames.append(('joint1',frameSelected))
                                            #print("ilk nokta seçili son nokta seçili değil", frameSelected)
                                    elif frameSelected['joint1']==jointSelected['name']: #bitiş noktası seçili frame
                                        endpointselected=0
                                        for jointSelected1 in Variables.selectedJoints:
                                            if frameSelected['joint0']==jointSelected1['name']: #bitiş noktası seçili frame in başlangıç noktasıda seçili.
                                                endpointselected=1
                                                if twoPointSelectedFrames.count(frameSelected)==False:
                                                    twoPointSelectedFrames.append(frameSelected)
                                                    #print("iki nokta da seçili",frameSelected)
                                        if endpointselected==0:
                                            onePointSelectedFrames.append(('joint0',frameSelected))
                                            #print("son nokta seçili ilk nokta seçili değil", frameSelected)

                            for frame in Variables.selectedFrames:
                                noPointSelectedFrames.append(frame)
                                for frametwo in twoPointSelectedFrames:
                                    if frame ==frametwo:
                                        noPointSelectedFrames.remove(frame)
                                for frameOne in onePointSelectedFrames:
                                    if frame == frameOne[1]:
                                        noPointSelectedFrames.remove(frame)

                            #print("no",noPointSelectedFrames)
                            #print("one",onePointSelectedFrames)
                            #print("two",twoPointSelectedFrames)
                            
                            
                            oldjointDict=[] # yeni oluşan joint loopa girmesin diye eskisini kopyalıyoruz
                            for joint in Joint.jointdict:                
                                oldjointDict.append(joint)

                            freeJoints=[]
                            for frameNo in noPointSelectedFrames:
                                for jointfree in oldjointDict:
                                    if jointfree['name']==frameNo['joint0']:
                                        freeJoints.append({'joint':jointfree,'frame':frameNo,'changes':'joint0','ischanged':0})
                                    if jointfree['name']==frameNo['joint1']:
                                        freeJoints.append({'joint':jointfree,'frame':frameNo,'changes':'joint1','ischanged':0})                    
                                    
                            freeJointsmovable=[]
                            for frameNo in noPointSelectedFrames:
                                for jointfree in oldjointDict:
                                    if jointfree['name']==frameNo['joint0']:
                                        freeJointsmovable.append(jointfree)
                                    if jointfree['name']==frameNo['joint1']:
                                        freeJointsmovable.append(jointfree)
                                    
                                for frame in Frame.framedict:
                                    if frame['deleted']==False:
                                        if frame['name']!=frameNo['name']:
                                            if frame['joint0']==frameNo['joint0'] or frame['joint1']==frameNo['joint0']:
                                                for jointfree1 in oldjointDict:
                                                    if jointfree1['name']==frameNo['joint0']:
                                                        if sum(x.get('name')==jointfree1['name'] for x in freeJointsmovable)!=0:
                                                            freeJointsmovable.remove(jointfree1)                                        
                                            if frame['joint0']==frameNo['joint1'] or frame['joint1']==frameNo['joint1']:
                                                for jointfree2 in oldjointDict:
                                                    if jointfree2['name']==frameNo['joint1']:
                                                        if sum(x.get('name')==jointfree2['name'] for x in freeJointsmovable)!=0:
                                                            freeJointsmovable.remove(jointfree2)
                            
                            for onePointSelectedFrame in onePointSelectedFrames:
                                for jointfree in oldjointDict:
                                    if jointfree['name']==onePointSelectedFrame[1][onePointSelectedFrame[0]]:
                                        freeJoints.append({'joint':jointfree,'frame':onePointSelectedFrame[1],'changes':onePointSelectedFrame[0],'ischanged':0})

                                        freeJointsmovable.append(jointfree)
                                        for frame in Frame.framedict:
                                            if frame['deleted']==False:
                                                if frame['name']!=onePointSelectedFrame[1]['name']:
                                                    if frame['joint0']==onePointSelectedFrame[1]['joint0'] or frame['joint1']==onePointSelectedFrame[1]['joint0']:
                                                        for jointfree1 in oldjointDict:
                                                            if jointfree1['name']==onePointSelectedFrame[1]['joint0']:
                                                                if sum(x.get('name')==jointfree1['name'] for x in freeJointsmovable)!=0:
                                                                    freeJointsmovable.remove(jointfree1)

                                                    if frame['joint0']==onePointSelectedFrame[1]['joint1'] or frame['joint1']==onePointSelectedFrame[1]['joint1']:
                                                        for jointfree2 in oldjointDict:
                                                            if jointfree2['name']==onePointSelectedFrame[1]['joint1']:
                                                                if sum(x.get('name')==jointfree2['name'] for x in freeJointsmovable)!=0:
                                                                    freeJointsmovable.remove(jointfree2)
                            print("free",freeJoints)
                            #print("moveable",freeJointsmovable)
                            for freejoint in freeJoints:# gittiği yerde engel var mı kontrol ediyoruz  
                                
                                if freejoint['ischanged']==0:
                                    # for jointdestination in oldjointDict:
                                    #     if jointdestination['coords']==freejoint['joint']['coords']:                                    
                                            destinationPoint=(freejoint['joint']['coords'][0]+Unit.dimension(self, float(self.text1.text()),1),freejoint['joint']['coords'][1]-Unit.dimension(self, float(self.text3.text()),1),freejoint['joint']['coords'][2]+Unit.dimension(self, float(self.text2.text()),1))
                                            for joint1 in oldjointDict:
                                                if joint1['coords']==destinationPoint and joint1['deleted']==False:
                                                    if sum(y.get('coords')==destinationPoint for y in Variables.selectedJoints)==0 and sum(y.get('coords')==destinationPoint for y in freeJointsmovable)==0: 
                                                        print("engel var")
                                                        
                                                        # Engel varsa ve free ise siliyoruz
                                                        for freejointmove in freeJointsmovable:
                                                            if freejointmove==freejoint['joint']:
                                                                print("fj12",freejoint['frame'],id(freejoint['frame']))
                                                                freejoint['joint']['deleted']=True
                                                                undoobj.append((freejoint['joint'],'deleted',False,True))
                                                                print("fj12",freejoint['frame'],id(freejoint['frame']))
                                                                
                                                        # engel varsa framein noktalarını değiştiriyoruz
                                                        print("fj11",freejoint['frame'],id(freejoint['frame']))
                                                        undoobj.append((freejoint['frame'],freejoint['changes'],freejoint['frame'][freejoint['changes']],joint1['name']))
                                                        freejoint['frame'][freejoint['changes']]=joint1['name']                                                
                                                        freejoint['ischanged']=1
                                                        print("fj11",freejoint['frame'],id(freejoint['frame']))
                            

                            print("moveable joint list",freeJointsmovable)
                            for freejointmove in freeJointsmovable: # moveable engel yoksa
                                for freejoint in freeJoints:
                                    if freejoint['ischanged']==0:
                                        if freejointmove==freejoint['joint']:                                    
                                            destinationPoint=(freejointmove['coords'][0]+Unit.dimension(self, float(self.text1.text()),1),freejointmove['coords'][1]-Unit.dimension(self, float(self.text3.text()),1),freejointmove['coords'][2]+Unit.dimension(self, float(self.text2.text()),1))
                                            if sum((x.get('coords') == destinationPoint and x.get('deleted')==False) for x in oldjointDict)==0:                                        
                                                # engel yoksa free leri hareket ettiriyoruz
                                                print("fj",freejointmove,id(freejointmove))
                                                undoobj.append((freejointmove,'coords',freejointmove['coords'],destinationPoint))
                                                freejointmove['coords']=destinationPoint                                                
                                                freejoint['ischanged']=1
                                                print("fj",freejointmove,id(freejointmove))


                            
                            for freejoint in freeJoints: # gittiği yerde engel olmayanların noktalarını oluşturuyoruz
                                
                                if freejoint['ischanged']==0:                                                                
                                        destinationPoint=(freejoint['joint']['coords'][0]+Unit.dimension(self, float(self.text1.text()),1),freejoint['joint']['coords'][1]-Unit.dimension(self, float(self.text3.text()),1),freejoint['joint']['coords'][2]+Unit.dimension(self, float(self.text2.text()),1))
                                    
                                        isfreejoint =0

                                        for freejointmove in freeJointsmovable:
                                            if freejointmove==freejoint['joint']:
                                                print("fj12",freejoint['frame'],id(freejoint['frame']))                                                
                                                undoobj.append((freejointmove,'coords',freejointmove['coords'],destinationPoint))
                                                freejointmove['coords']=destinationPoint
                                                print("fj12",freejoint['frame'],id(freejoint['frame']))
                                                isfreejoint=1

                                        if isfreejoint==0:
                                            j=Joint(destinationPoint[0],destinationPoint[1],destinationPoint[2])
                                            for joint in Joint.jointdict:
                                                if joint['name']==j.count:
                                                    undoobj.append((joint,'deleted',True,False))                                                        
                                                    print("f1",freejoint['frame'],id(freejoint['frame']))
                                                    undoobj.append((freejoint['frame'],freejoint['changes'],freejoint['frame'][freejoint['changes']],joint['name']))
                                                    freejoint['frame'][freejoint['changes']]=joint['name']
                                                    print("f1",freejoint['frame'],id(freejoint['frame']))
                                                    freejoint['ischanged']=1

                            
                            for freejoint in freeJoints:  #gittiği yerde frame varsa siliyoruz
                                if freejoint['changes']=='joint0':
                                    for frame in Frame.framedict:
                                        if frame!=freejoint['frame']:
                                            if (frame['joint0']==freejoint['frame']['joint0'] and frame['joint1']==freejoint['frame']['joint1']) :
                                                frame['deleted']=True
                                                undoobj.append((frame,'deleted',False,True))
                                            if (frame['joint1']==freejoint['frame']['joint0'] and frame['joint0']==freejoint['frame']['joint1']):
                                                frame['deleted']=True
                                                undoobj.append((frame,'deleted',False,True))


                            
                            #Bu noktadan sonrası Joint kaydırıyor.
                            for joint in Variables.selectedJoints:
                                destinationJoint=0
                                destinationPoint=(joint['coords'][0]+Unit.dimension(self, float(self.text1.text()),1),joint['coords'][1]-Unit.dimension(self, float(self.text3.text()),1),joint['coords'][2]+Unit.dimension(self, float(self.text2.text()),1))                
                                for joint1 in Joint.jointdict:
                                    if joint1['coords']==destinationPoint and joint1['deleted']==False:
                                        if sum(y.get('coords')==destinationPoint for y in Variables.selectedJoints)==0 and sum(y.get('coords')==destinationPoint for y in freeJointsmovable)==0:                        
                                            destinationJoint=1
                                            print("j1",joint,id(joint))
                                            joint['deleted']=True
                                            undoobj.append((joint,'deleted',False,True))
                                            print("j1",joint,id(joint))                            
                                            for frame in Frame.framedict:
                                                if frame['joint0']==joint['name']:
                                                    if frame['joint1']==joint1['name']:
                                                        
                                                        if frame['deleted']==False:
                                                            print("f11",frame,id(frame))
                                                            frame['deleted']=True
                                                            undoobj.append((frame,'deleted',False,True))
                                                            print("f11",frame,id(frame))
                                                    else:
                                                        crashed=0
                                                        for frame1 in Frame.framedict:
                                                            if frame1['name']!=frame['name']:
                                                                if frame1['joint0']==frame['joint1'] and frame1['joint1']==joint1['name'] and frame1['deleted']==False:

                                                                    if frame['deleted']==False:
                                                                        print("f55",frame,id(frame))
                                                                        frame['deleted']=True
                                                                        undoobj.append((frame,'deleted',False,True))
                                                                        print("f55",frame,id(frame))
                                                                    crashed=1
                                                                elif frame1['joint1']==frame['joint1'] and frame1['joint0']==joint1['name'] and frame1['deleted']==False:
                                                                    if frame['deleted']==False:
                                                                        print("f99",frame,id(frame))
                                                                        frame['deleted']=True
                                                                        undoobj.append((frame,'deleted',False,True))
                                                                        print("f99",frame,id(frame))
                                                                        crashed=1

                                                        if crashed==0:#gittiği yerde başka çubuk yok 
                                                            
                                                            print(1,frame,id(frame))
                                                            undoobj.append((frame,'joint0',frame['joint0'],joint1['name']))
                                                            frame['joint0']=joint1['name']
                                                            print(1,frame,id(frame))

                                                if frame['joint1']==joint['name']:
                                                    if frame['joint0']==joint1['name']:
                                                        if frame['deleted']==False:
                                                            print("f22",frame,id(frame))
                                                            frame['deleted']=True
                                                            undoobj.append((frame,'deleted',False,True))
                                                            print("f22",frame,id(frame))
                                                    else:
                                                        crashed=0
                                                        for frame1 in Frame.framedict:
                                                            if frame1['name']!=frame['name']:
                                                                if frame1['joint0']==frame['joint0'] and frame1['joint1']==joint1['name'] and frame1['deleted']==False:
                                                                    if frame['deleted']==False:
                                                                        print("f66",frame,id(frame))
                                                                        frame['deleted']=True
                                                                        undoobj.append((frame,'deleted',False,True))
                                                                        print("f66",frame,id(frame))
                                                                    crashed=1
                                                                elif frame1['joint1']==frame['joint0'] and frame1['joint0']==joint1['name'] and frame1['deleted']==False:
                                                                    if frame['deleted']==False:
                                                                        print("f1000",frame,id(frame))
                                                                        frame['deleted']=True
                                                                        undoobj.append((frame,'deleted',False,True))
                                                                        print("f1000",frame,id(frame))
                                                                    crashed=1

                                                        if crashed==0: #gittiği yerde başka çubuk yok
                                                            print("f",frame,id(frame))
                                                            undoobj.append((frame,'joint1',frame['joint1'],joint1['name']))
                                                            frame['joint1']=joint1['name']
                                                            print("f",frame,id(frame))

                                if destinationJoint==0:
                                    print("j2",joint,id(joint),destinationPoint)
                                    undoobj.append((joint,'coords',joint['coords'],destinationPoint))
                                    joint['coords']=destinationPoint
                                    print("j2",joint,id(joint),destinationPoint)
                        
                            oldjointDict.clear()                        
                            UndoReundo(undoobj)
                            OpenGLWidget.selectionClear()
                            mdi.statusBar().showMessage('')
        except Exception as e:
            logging.debug(e)
        logging.info("Move function ended")

class JointSupportWin(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(JointSupportWin, self).__init__(*args, **kwargs)
        self.title = 'Joint Support Assigment'
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 400
        self.height = 230        
        self.initUI()
    
    def initUI(self):
        self.t1=Variables.jointsupportTemp[0]
        self.t2=Variables.jointsupportTemp[1]
        self.t3=Variables.jointsupportTemp[2]
        self.r1=Variables.jointsupportTemp[3]
        self.r2=Variables.jointsupportTemp[4]
        self.r3=Variables.jointsupportTemp[5]

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
        

        button_apply=QPushButton(self)
        button_apply.setGeometry(220,200,50,22)
        button_apply.setText("APPLY")
        button_apply.clicked.connect(self.on_click_apply)

        button_ok=QPushButton(self)
        button_ok.setGeometry(275,200,50,22)
        button_ok.setText("OK")
        button_ok.clicked.connect(self.on_click_ok)
        
        button_cancel=QPushButton(self)
        button_cancel.setGeometry(330,200,50,22)
        button_cancel.setText("CANCEL")
        button_cancel.clicked.connect(self.on_click_cancel)

        label1 = QLabel(self)
        label1.setGeometry(20,20,100,20)
        label1.setText("Translations:")

        checktransx = QCheckBox(self)
        checktransx.setGeometry(20,50,200,20)
        checktransx.setText("Translation Local Direction 1")
        checktransx.toggled.connect(self.on_click_check_t1)
        if self.t1==1:
            checktransx.setChecked(True)
        else :
            checktransx.setChecked(False)

        checktransy = QCheckBox(self)
        checktransy.setGeometry(20,80,200,20)
        checktransy.setText("Translation Local Direction 2")
        checktransy.toggled.connect(self.on_click_check_t1)
        if self.t2==1:
            checktransy.setChecked(True)
        else :
            checktransy.setChecked(False)

        checktransz = QCheckBox(self)
        checktransz.setGeometry(20,110,200,20)
        checktransz.setText("Translation Local Direction 3")
        checktransz.toggled.connect(self.on_click_check_t1)
        if self.t3==1:
            checktransz.setChecked(True)
        else :
            checktransz.setChecked(False)

        label2 = QLabel(self)
        label2.setGeometry(210,20,100,20)
        label2.setText("Rotations:")

        checkrotx = QCheckBox(self)
        checkrotx.setGeometry(210,50,200,20)
        checkrotx.setText("Rotation About Local Direction 1")
        checkrotx.toggled.connect(self.on_click_check_t1)
        if self.r1==1:
            checkrotx.setChecked(True)
        else :
            checkrotx.setChecked(False)

        checkroty = QCheckBox(self)
        checkroty.setGeometry(210,80,200,20)
        checkroty.setText("Rotation About Local Direction 2")
        checkroty.toggled.connect(self.on_click_check_t1)
        if self.r2==1:
            checkroty.setChecked(True)
        else :
            checkroty.setChecked(False)

        checkrotz = QCheckBox(self)
        checkrotz.setGeometry(210,110,200,20)
        checkrotz.setText("Rotation About Local Direction 3")
        checkrotz.toggled.connect(self.on_click_check_t1)
        if self.r3==1:
            checkrotz.setChecked(True)
        else :
            checkrotz.setChecked(False)

    def on_click_apply(self):
        if Variables.selectedJoints!=[]:
            undoobj=[]
            for joint in Variables.selectedJoints:
                if joint['show'] and joint['deleted']==False:
                    undoobj.append((joint,'restraints',joint['restraints'],Variables.jointsupportTemp))
                    joint['restraints']=Variables.jointsupportTemp
            UndoReundo(undoobj)
        OpenGLWidget.selectionClear()
        mdi.statusBar().showMessage('')

    def on_click_ok(self):
        if Variables.selectedJoints!=[]:
            for joint in Variables.selectedJoints:
                if joint['show'] and joint['deleted']==False:
                    joint['restraints']=Variables.jointsupportTemp
        OpenGLWidget.selectionClear()
        mdi.statusBar().showMessage('')
        self.close()

    def on_click_cancel(self):
        self.close()

    def on_click_check_t1(self,p):
        if self.sender().text()=="Translation Local Direction 1":            
            if p==True:
                Variables.jointsupportTemp=[1,Variables.jointsupportTemp[1],Variables.jointsupportTemp[2],Variables.jointsupportTemp[3],
                                                Variables.jointsupportTemp[4],Variables.jointsupportTemp[5]]
            else:
                Variables.jointsupportTemp=[0,Variables.jointsupportTemp[1],Variables.jointsupportTemp[2],Variables.jointsupportTemp[3],
                                                Variables.jointsupportTemp[4],Variables.jointsupportTemp[5]]
        if self.sender().text()=="Translation Local Direction 2":            
            if p==True:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],1,Variables.jointsupportTemp[2],Variables.jointsupportTemp[3],
                                                Variables.jointsupportTemp[4],Variables.jointsupportTemp[5]]
            else:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],0,Variables.jointsupportTemp[2],Variables.jointsupportTemp[3],
                                                Variables.jointsupportTemp[4],Variables.jointsupportTemp[5]]
        if self.sender().text()=="Translation Local Direction 3":            
            if p==True:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],Variables.jointsupportTemp[1],1,Variables.jointsupportTemp[3],
                                                Variables.jointsupportTemp[4],Variables.jointsupportTemp[5]]
            else:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],Variables.jointsupportTemp[1],0,Variables.jointsupportTemp[3],
                                                Variables.jointsupportTemp[4],Variables.jointsupportTemp[5]]
        if self.sender().text()=="Rotation About Local Direction 1":            
            if p==True:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],Variables.jointsupportTemp[1],Variables.jointsupportTemp[2],1,
                                                Variables.jointsupportTemp[4],Variables.jointsupportTemp[5]]
            else:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],Variables.jointsupportTemp[1],Variables.jointsupportTemp[2],0,
                                                Variables.jointsupportTemp[4],Variables.jointsupportTemp[5]]
        if self.sender().text()=="Rotation About Local Direction 2":            
            if p==True:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],Variables.jointsupportTemp[1],Variables.jointsupportTemp[2],
                                                Variables.jointsupportTemp[3],1,Variables.jointsupportTemp[5]]
            else:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],Variables.jointsupportTemp[1],Variables.jointsupportTemp[2],
                                                Variables.jointsupportTemp[3],0,Variables.jointsupportTemp[5]]
        if self.sender().text()=="Rotation About Local Direction 3":            
            if p==True:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],Variables.jointsupportTemp[1],Variables.jointsupportTemp[2],
                                                Variables.jointsupportTemp[3],Variables.jointsupportTemp[4],1]
            else:
                Variables.jointsupportTemp=[Variables.jointsupportTemp[0],Variables.jointsupportTemp[1],Variables.jointsupportTemp[2],
                                                Variables.jointsupportTemp[3],Variables.jointsupportTemp[4],0]

class QuickGridWindow(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(QuickGridWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 240
        self.height = 180
        self.initUI()

    def initUI(self):
        
        self.setWindowTitle("Grid Window")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
        #self.setWindowState()
        label1 = QLabel(self)
        label1.setGeometry(20,20,100,20)
        label1.setText("Number of X axes:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,100,20)
        label2.setText("Number of Y axes:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,100,20)
        label3.setText("Number of Z axes:")

        label4 = QLabel(self)
        label4.setGeometry(20,80,100,20)
        label4.setText("Span of X axes:")
        label5 = QLabel(self)
        label5.setGeometry(20,100,100,20)
        label5.setText("Span of Y axes:")
        label6 = QLabel(self)
        label6.setGeometry(20,120,100,20)
        label6.setText("Span of Z axes:")
        
        
        self.text1 =QSpinBox(self)
        self.text1.setValue(Variables.gridxcount)
        self.text1.setRange(1, 40)
        self.text1.setGeometry(120,22,100,18)

        self.text2 =QSpinBox(self)
        self.text2.setValue(Variables.gridycount)
        self.text2.setRange(1, 40)
        self.text2.setGeometry(120,42,100,18)

        self.text3 =QSpinBox(self)
        self.text3.setValue(Variables.gridzcount)
        self.text3.setRange(1, 40)
        self.text3.setGeometry(120,62,100,18)

        valid = QDoubleValidator(0.0,99999.9999,2,self)
        valid.setNotation(QDoubleValidator.StandardNotation)

        self.text4 = QLineEdit(self)
        self.text4.setGeometry(120,82,100,18)
        self.text4.setValidator(valid)
        self.text4.setText(str(Unit.dimension(self,Variables.gridxspan,0)))

        self.text5 = QLineEdit(self)
        self.text5.setGeometry(120,102,100,18)
        self.text5.setValidator(valid)
        self.text5.setText(str(Unit.dimension(self,Variables.gridyspan,0)))

        self.text6 = QLineEdit(self)
        self.text6.setGeometry(120,122,100,18)
        self.text6.setValidator(valid)
        self.text6.setText(str(Unit.dimension(self,Variables.gridzspan,0)))

        okButton = QPushButton('OK',self)
        okButton.setGeometry(120,145,100,20)
        okButton.clicked.connect(self.on_click_ok)

    def on_click_ok(self,event):
        if self.text1.text() !="" and self.text2.text()!='' and self.text3.text()!='' and self.text4.text()!=''and self.text5.text()!='' and self.text6.text()!='':
            Variables.gridxTemp.clear()
            Variables.gridxcount=int(self.text1.text())
            Variables.gridycount=int(self.text2.text())
            Variables.gridzcount=int(self.text3.text())
            Variables.gridxspan=Unit.dimension(self,float(self.text4.text()),1)
            Variables.gridyspan=Unit.dimension(self,float(self.text5.text()),1)
            Variables.gridzspan=Unit.dimension(self,float(self.text6.text()),1)
            list1=list(string.ascii_uppercase)
            for i in range(int(self.text1.text())):
                if i<25:
                    Variables.gridxTemp.append((list1[i],i*Unit.dimension(self,float(self.text4.text()),1)))
                else:
                    Variables.gridxTemp.append(('A',i*Unit.dimension(self,float(self.text4.text()),1)))
            Variables.gridyTemp.clear()
            for i in range(int(self.text2.text())):
                Variables.gridyTemp.append((i+1,i*Unit.dimension(self,float(self.text5.text()),1)))
            Variables.gridzTemp.clear()
            for i in range(int(self.text3.text())):
                Variables.gridzTemp.append(("Z"+str(i+1),i*Unit.dimension(self,float(self.text6.text()),1)))
            mdi.griddlg.tablefiller()
            self.close()

class QuickStartWindow(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(QuickStartWindow, self).__init__(*args, **kwargs)
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 240
        self.height = 180
        self.initUI()

    def initUI(self):
        logging.info("Quick Start Window started")
        self.setWindowTitle("New Project")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
        
        #self.setWindowState()
        label1 = QLabel(self)
        label1.setGeometry(20,20,100,20)
        label1.setText("Number of X axes:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,100,20)
        label2.setText("Number of Y axes:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,100,20)
        label3.setText("Number of Z axes:")

        label4 = QLabel(self)
        label4.setGeometry(20,80,100,20)
        label4.setText("Span of X axes:")
        label5 = QLabel(self)
        label5.setGeometry(20,100,100,20)
        label5.setText("Span of Y axes:")
        label6 = QLabel(self)
        label6.setGeometry(20,120,100,20)
        label6.setText("Span of Z axes:")
        
        
        self.text1 =QSpinBox(self)
        self.text1.setValue(Variables.gridxcount)
        self.text1.setRange(1, 40)
        self.text1.setGeometry(120,22,100,18)

        self.text2 =QSpinBox(self)
        self.text2.setValue(Variables.gridycount)
        self.text2.setRange(1, 40)
        self.text2.setGeometry(120,42,100,18)

        self.text3 =QSpinBox(self)
        self.text3.setValue(Variables.gridzcount)
        self.text3.setRange(1, 40)
        self.text3.setGeometry(120,62,100,18)

        valid = QDoubleValidator(0.0,99999.9999,4,self)
        valid.setNotation(QDoubleValidator.StandardNotation)
               
        self.text4 = QLineEdit(self)
        self.text4.setGeometry(120,82,100,18)
        self.text4.setValidator(valid)
        self.text4.setText(str(Unit.dimension(self,Variables.gridxspan,0)))

        self.text5 = QLineEdit(self)
        self.text5.setGeometry(120,102,100,18)
        self.text5.setValidator(valid)
        self.text5.setText(str(Unit.dimension(self,Variables.gridyspan,0)))

        self.text6 = QLineEdit(self)
        self.text6.setGeometry(120,122,100,18)
        self.text6.setValidator(valid)
        self.text6.setText(str(Unit.dimension(self,Variables.gridzspan,0)))

        okButton = QPushButton('OK',self)
        okButton.setGeometry(120,145,100,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,145,80,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)
        logging.info("Quick Start Window ended")

    def on_click_ok(self,event):
        logging.info("Quick Start Window ok_button start")
        try:
            if self.text1.text() !="" and self.text2.text()!='' and self.text3.text()!='' and self.text4.text()!=''and self.text5.text()!='' and self.text6.text()!='':
                Variables.gridx.clear()
                list1=list(string.ascii_uppercase)
                for i in range(int(self.text1.text())):
                    if i<25:
                        Variables.gridx.append((list1[i],i*Unit.dimension(self,float(self.text4.text()),1)))
                    else:
                        Variables.gridx.append(('A',i*Unit.dimension(self,float(self.text4.text()),1)))
                Variables.gridy.clear()
                for i in range(int(self.text2.text())):
                    Variables.gridy.append((i+1,i*Unit.dimension(self,float(self.text5.text()),1)))
                Variables.gridz.clear()
                for i in range(int(self.text3.text())):
                    Variables.gridz.append(("Z"+str(i+1),i*Unit.dimension(self,float(self.text6.text()),1)))
                
                NewFile(int(self.text1.text()),int(self.text2.text()),int(self.text3.text()),Unit.dimension(self,float(self.text4.text()),1),Unit.dimension(self,float(self.text5.text()),1),Unit.dimension(self,float(self.text6.text()),1))
                
                self.close()
        except Exception as e:
            logging.debug(e)
        logging.info("Quick Start Window ok_button end")
    
    def on_combobox_changed(self,index):
        Unit.index(self,index)
        self.text4.setText(str(Unit.dimension(self,float(self.text4.text()),2)))
        self.text5.setText(str(Unit.dimension(self,float(self.text5.text()),2)))
        self.text6.setText(str(Unit.dimension(self,float(self.text6.text()),2)))

class MaterialWindow(QDialog):
    selectedmat=None
    addmatbool=False
    def __init__(self, *args, **kwargs):
        super(MaterialWindow, self).__init__(*args, **kwargs)       
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 210
        self.height = 210
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Materials")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
       
        self.listbox=QListWidget(self)
        self.listbox.setGeometry(20,20,170,135)
        self.listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listbox.itemDoubleClicked.connect(self.on_click_list)
        self.listboxfiller()

        okButton = QPushButton('OK',self)
        okButton.setGeometry(140,175,50,20)
        okButton.clicked.connect(self.on_click_ok)

        okButton = QPushButton('DELETE',self)
        okButton.setGeometry(80,175,50,20)
        okButton.clicked.connect(self.on_click_delete)

        okButton = QPushButton('ADD',self)
        okButton.setGeometry(20,175,50,20)
        okButton.clicked.connect(self.on_click_add)

    def listboxfiller(self):
        self.listbox.clear()
        for mat in Materials.materialdict:            
            if mat['deleted']==False:
                self.listbox.addItem(mat['name'])

    def on_click_ok(self,event):
        self.close()

    def on_click_add(self,event):
        self.addmatbool=True
        materialpropsdlg = MaterialPropertyWindow(self)
        materialpropsdlg.exec_()        

    def on_click_delete(self,event):
        for item in self.listbox.selectedItems():
            for mat in Materials.materialdict:
                if mat['name']==item.text():
                    if sum(y.get('matindex')==mat['index'] and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                        mat['deleted']=True
                    else:
                        mdi.statusBar().showMessage('Can not delete while the material is already assigned in a section !')

        self.listboxfiller()

    def on_click_list(self,p):
        for mat in Materials.materialdict:
            if mat['name']==p.text():
                self.selectedmat=mat
                self.addmatbool=False
                materialpropsdlg = MaterialPropertyWindow(self)
                materialpropsdlg.exec_()
                break

class MaterialPropertyWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(MaterialPropertyWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 335
        self.height = 225
        if mdi.materialsdlg.addmatbool==False:
            self.mat=mdi.materialsdlg.selectedmat
            self.selectedmatname=mdi.materialsdlg.selectedmat['name']
            self.matdict=[]
            for mat in Materials.materialdict:
                if mat['name']!=self.selectedmatname:
                    if mat['deleted']==False:
                        self.matdict.append(mat)
        else:
            self.matname="mat"
            self.mattype="Steel"
            self.matW=0.00785
            self.matE=2039432.425956
            self.matU=0.3
            self.matA=1
            self.matFY=2396.333100
            self.matFU=3670.978367
            self.matFC=300
        self.initUI()

    def initUI(self):
        if mdi.materialsdlg.addmatbool==False:
            self.setWindowTitle("Material Properties of "+self.mat['name'])
        else:
            self.setWindowTitle("Add New Material")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label10 = QLabel(self)
        label10.setGeometry(20,20,120,20)
        label10.setText("Material Type:")
        label1 = QLabel(self)
        label1.setGeometry(20,40,120,20)
        label1.setText("Material Name:")
        label2 = QLabel(self)
        label2.setGeometry(20,60,120,20)
        label2.setText("Material Density:")
        label3 = QLabel(self)
        label3.setGeometry(20,80,120,20)
        label3.setText("Modulus of Elasticity: E:")

        label4 = QLabel(self)
        label4.setGeometry(20,100,120,20)
        label4.setText("Poisson: U:")
        label5 = QLabel(self)
        label5.setGeometry(20,120,120,20)
        label5.setText("Shear Modulus: G:")
        
        self.label6 = QLabel(self)
        self.label6.setGeometry(20,140,120,20)
        self.label6.setText("Compressive Stregth: Fc:")

        self.label7 = QLabel(self)
        self.label7.setGeometry(20,140,120,20)
        self.label7.setText("Yield Stress: Fy:")
        self.label8 = QLabel(self)
        self.label8.setGeometry(20,160,120,20)
        self.label8.setText("Ultimate Stress: Fu:")
                
        valid = QDoubleValidator(0.0,999999999999.999999999999,12,self)
        valid.setNotation(QDoubleValidator.StandardNotation)
        self.forcename=Variables.units[Variables.unitindex].split('-')[0]
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]
        
        if self.dimensionname=='mm':
            round1=13
            round2=8
        elif self.dimensionname=='cm':
            round1=8
            round2=6
        else:
            round1=4
            round2=4
        
        if mdi.materialsdlg.addmatbool:
            self.combmattype=QComboBox(self)
            self.combmattype.addItems(['Steel','Concrete'])            
            self.combmattype.setGeometry(150,22,120,18)
            self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)
        else:
            label9 = QLineEdit(self)
            label9.setGeometry(150,22,120,18)
            label9.setText(self.mat['type'])
            label9.setEnabled(False)

        self.text1 =QLineEdit(self)
        if mdi.materialsdlg.addmatbool==False:
            self.text1.setText(self.mat['name'])
        else:
            self.text1.setText(self.matname)
        self.text1.setMaxLength(20)
        self.text1.setGeometry(150,42,120,18)
        self.text1.textEdited.connect(self.text1_changed)

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(150,62,120,18)
        self.text2.setValidator(valid)
        if mdi.materialsdlg.addmatbool==False:
            self.text2.setText(str(format(round(float(Unit.density(self,self.mat['W'],0)),round1),'.'+str(round1)+'f')))
        else:
            self.text2.setText(str(format(round(float(Unit.density(self,self.matW,0)),round1),'.'+str(round1)+'f')))
        self.text2.textEdited.connect(self.text2_changed)

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(150,82,120,18)
        self.text3.setValidator(valid)
        if mdi.materialsdlg.addmatbool==False:
            self.text3.setText(str(format(round(float(Unit.stress(self,self.mat['E'],0)),round2),'.'+str(round2)+'f')))
        else:
            self.text3.setText(str(format(round(float(Unit.stress(self,self.matE,0)),round2),'.'+str(round2)+'f')))
        self.text3.textEdited.connect(self.text3_changed)

        self.text4 = QLineEdit(self)
        self.text4.setGeometry(150,102,120,18)
        self.text4.setValidator(valid)
        if mdi.materialsdlg.addmatbool==False:
            self.text4.setText(str(self.mat['U']))
        else:
            self.text4.setText(str(self.matU))
        self.text4.textEdited.connect(self.text4_changed)

        self.text5 = QLineEdit(self)
        self.text5.setGeometry(150,122,120,18)
        self.text5.setValidator(valid)
        if mdi.materialsdlg.addmatbool==False:
            shearmodulus=round(float(Unit.stress(self,self.mat['E'],0))/(2*(1+float(self.mat['U']))),5)
            self.text5.setText(str(shearmodulus))
        else:
            shearmodulus=round(float(Unit.stress(self,self.matE,0))/(2*(1+float(self.matU))),5)
            self.text5.setText(str(shearmodulus))
        self.text5.setEnabled(False)

        self.text6 = QLineEdit(self)
        self.text6.setGeometry(150,142,120,18)
        self.text6.setValidator(valid)
        self.text6.textEdited.connect(self.text6_changed)
        
        self.text7 = QLineEdit(self)
        self.text7.setGeometry(150,142,120,18)
        self.text7.setValidator(valid)
        self.text7.textEdited.connect(self.text7_changed)

        self.text8 = QLineEdit(self)
        self.text8.setGeometry(150,162,120,18)
        self.text8.setValidator(valid)
        self.text8.textEdited.connect(self.text8_changed)
        if mdi.materialsdlg.addmatbool==False:
            if self.mat['type']=='Concrete':
                self.label6.show()
                self.text6.show()
                self.text6.setText(str(format(round(float(Unit.stress(self,self.mat['FC'],0)),round2),'.'+str(round2)+'f')))            
                self.label7.hide()
                self.label8.hide()
                self.text7.hide()
                self.text8.hide()
            else:
                self.label6.hide()
                self.text6.hide()
                self.label7.show()
                self.label8.show()
                self.text7.show()
                self.text8.show()
                self.text7.setText(str(format(round(float(Unit.stress(self,self.mat['FY'],0)),round2),'.'+str(round2)+'f')))     
                self.text8.setText(str(format(round(float(Unit.stress(self,self.mat['FU'],0)),round2),'.'+str(round2)+'f')))
        else:
            if self.mattype=='Concrete':
                self.label6.show()
                self.text6.show()
                self.text6.setText(str(format(round(float(Unit.stress(self,self.matFC,0)),round2),'.'+str(round2)+'f')))            
                self.label7.hide()
                self.label8.hide()
                self.text7.hide()
                self.text8.hide()
            else:
                self.label6.hide()
                self.text6.hide()
                self.label7.show()
                self.label8.show()
                self.text7.show()
                self.text8.show()
                self.text7.setText(str(format(round(float(Unit.stress(self,self.matFY,0)),round2),'.'+str(round2)+'f')))     
                self.text8.setText(str(format(round(float(Unit.stress(self,self.matFU,0)),round2),'.'+str(round2)+'f')))

        okButton = QPushButton('OK',self)
        okButton.setGeometry(150,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,185,100,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)

        densityUnit=self.forcename+"/"+self.dimensionname+"³" #alt+0179
        stressUnit=self.forcename+"/"+self.dimensionname+"²" #alt+0178
        self.label11 = QLabel(self)
        self.label11.setGeometry(275,62,50,18)
        self.label11.setText(densityUnit)

        self.label12 = QLabel(self)
        self.label12.setGeometry(275,82,50,18)
        self.label12.setText(stressUnit)

        self.label13 = QLabel(self)
        self.label13.setGeometry(275,122,50,18)
        self.label13.setText(stressUnit)
        self.label14 = QLabel(self)
        self.label14.setGeometry(275,142,50,18)
        self.label14.setText(stressUnit)

        self.label15 = QLabel(self)
        self.label15.setGeometry(275,162,50,18)
        self.label15.setText(stressUnit)

        if mdi.materialsdlg.addmatbool==False:
            if self.mat['type']=='Steel':
                self.label15.show()
            else:
                self.label15.hide()
        else:
            if self.mattype=='Steel':
                self.label15.show()
            else:
                self.label15.hide()

    def closeEvent(self,event):
        mdi.materialsdlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        self.mattype=self.combmattype.currentText()
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]        
        if self.dimensionname=='mm':
            round2=8
        elif self.dimensionname=='cm':            
            round2=6
        else:            
            round2=4

        if self.mattype=='Concrete':
            self.label6.show()
            self.text6.show()
            self.text6.setText(str(format(round(float(Unit.stress(self,self.matFC,0)),round2),'.'+str(round2)+'f')))            
            self.label7.hide()
            self.label8.hide()
            self.text7.hide()
            self.text8.hide()
            self.label15.hide()
        else:
            self.label6.hide()
            self.text6.hide()
            self.label7.show()
            self.label8.show()
            self.text7.show()
            self.text8.show()
            self.text7.setText(str(format(round(float(Unit.stress(self,self.matFY,0)),round2),'.'+str(round2)+'f')))     
            self.text8.setText(str(format(round(float(Unit.stress(self,self.matFU,0)),round2),'.'+str(round2)+'f')))
            self.label15.show()

    def on_click_ok(self,event):
        if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!="" and self.text4.text()!="" and (self.text6.text()!="" or (self.text7.text()!="" and self.text8.text()!="")) :
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.materialsdlg.addmatbool==False:
                if sum(y.get('name')==self.text1.text()  for y in self.matdict)==0 :
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Materials.materialdict)==0:
                    if self.mattype=='Steel':
                        Steel(self.matname,self.matE,self.matU,self.matA,self.matW,self.matFY,self.matFU)
                    else:
                        Concrete(self.matname,self.matE,self.matU,self.matA,self.matW,self.matFC)
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")

    def text1_changed(self,p):
        if self.text1.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.materialsdlg.addmatbool==False:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Materials.materialdict)==0 or self.text1.text()==self.selectedmatname:
                    self.mat['name']=self.text1.text()
                else:
                    self.mat['name']=self.selectedmatname
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Materials.materialdict)==0:
                    self.matname=self.text1.text()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
        else:
            self.text1.setStyleSheet("border: 1px solid red;")

    def text2_changed(self,p):
        if self.text2.text()!="":
            self.text2.setStyleSheet("border: 1px solid black;")
            if mdi.materialsdlg.addmatbool==False:
                self.mat['W']=float(Unit.density(self,float(self.text2.text()),1))
            else:
                self.matW=float(Unit.density(self,float(self.text2.text()),1))
        else:
            self.text2.setStyleSheet("border: 1px solid red;")

    def text3_changed(self,p):
        if self.text3.text()!="":
            self.text3.setStyleSheet("border: 1px solid black;")
            if mdi.materialsdlg.addmatbool==False:
                self.mat['E']=float(Unit.stress(self,float(self.text3.text()),1))
                shearmodulus=round(float(Unit.stress(self,self.mat['E'],0))/(2*(1+float(self.mat['U']))),5)
                self.text5.setText(str(shearmodulus))
            else:
                self.matE=float(Unit.stress(self,float(self.text3.text()),1))
                shearmodulus=round(float(Unit.stress(self,self.matE,0))/(2*(1+float(self.matU))),5)
                self.text5.setText(str(shearmodulus))
        else:
            self.text3.setStyleSheet("border: 1px solid red;")

    def text4_changed(self,p):
        if self.text4.text()!="":
            self.text4.setStyleSheet("border: 1px solid black;")
            if mdi.materialsdlg.addmatbool==False:
                self.mat['U']=float(self.text4.text())
                shearmodulus=round(float(Unit.stress(self,self.mat['E'],0))/(2*(1+float(self.mat['U']))),5)
                self.text5.setText(str(shearmodulus))
            else:
                self.matU=float(self.text4.text())
                shearmodulus=round(float(Unit.stress(self,self.matE,0))/(2*(1+float(self.matU))),5)
                self.text5.setText(str(shearmodulus))
        else:
            self.text4.setStyleSheet("border: 1px solid red;")

    def text6_changed(self,p):
        if self.text6.text()!="":
            self.text6.setStyleSheet("border: 1px solid black;")
            if mdi.materialsdlg.addmatbool==False:
                self.mat['FC']=float(Unit.stress(self,float(self.text6.text()),1))
            else:
                self.matFC=float(Unit.stress(self,float(self.text6.text()),1))
        else:
            self.text6.setStyleSheet("border: 1px solid red;")
    
    def text7_changed(self,p):
        if self.text7.text()!="":
            self.text7.setStyleSheet("border: 1px solid black;")
            if mdi.materialsdlg.addmatbool==False:
                self.mat['FY']=float(Unit.stress(self,float(self.text7.text()),1))
            else:
                self.matFY=float(Unit.stress(self,float(self.text7.text()),1))
        else:
            self.text7.setStyleSheet("border: 1px solid red;")
    
    def text8_changed(self,p):
        if self.text8.text()!="":
            self.text8.setStyleSheet("border: 1px solid black;")
            if mdi.materialsdlg.addmatbool==False:
                self.mat['FU']=float(Unit.stress(self,float(self.text8.text()),1))
            else:
                self.matFU=float(Unit.stress(self,float(self.text8.text()),1))
        else:
            self.text8.setStyleSheet("border: 1px solid red;")
    
    def on_combobox_changed(self,index):
        mdi.combounit.setCurrentIndex(index)
        Unit.index(self,index)
        self.forcename=Variables.units[Variables.unitindex].split('-')[0]
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]
        if self.dimensionname=='mm':
            round1=13
            round2=8
        elif self.dimensionname=='cm':
            round1=8
            round2=6
        else:
            round1=4
            round2=4
        densityUnit=self.forcename+"/"+self.dimensionname+"³" #alt+0179
        stressUnit=self.forcename+"/"+self.dimensionname+"²" #alt+0178
        self.label11.setText(densityUnit)
        self.label12.setText(stressUnit)
        self.label13.setText(stressUnit)
        self.label14.setText(stressUnit)

        if mdi.materialsdlg.addmatbool==False:
            self.text2.setText(str(format(round(float(Unit.density(self,self.mat['W'],0)),round1),'.'+str(round1)+'f')))
            self.text3.setText(str(format(round(float(Unit.stress(self,self.mat['E'],0)),round2),'.'+str(round2)+'f')))
            shearmodulus=round(float(Unit.stress(self,self.mat['E'],0))/(2*(1+float(self.mat['U']))),5)
            self.text5.setText(str(shearmodulus))
            if self.mat['type']=='Concrete':
                self.text6.setText(str(format(round(float(Unit.stress(self,self.mat['FC'],0)),round2),'.'+str(round2)+'f'))) 
            else:
                self.text7.setText(str(format(round(float(Unit.stress(self,self.mat['FY'],0)),round2),'.'+str(round2)+'f')))     
                self.text8.setText(str(format(round(float(Unit.stress(self,self.mat['FU'],0)),round2),'.'+str(round2)+'f')))
            if self.mat['type']=='Steel':
                self.label15.setText(stressUnit)
        else:
            self.text2.setText(str(format(round(float(Unit.density(self,self.matW,0)),round1),'.'+str(round1)+'f')))
            self.text3.setText(str(format(round(float(Unit.stress(self,self.matE,0)),round2),'.'+str(round2)+'f')))
            shearmodulus=round(float(Unit.stress(self,self.matE,0))/(2*(1+float(self.matU))),5)
            self.text5.setText(str(shearmodulus))
            if self.mattype=='Concrete':
                self.text6.setText(str(format(round(float(Unit.stress(self,self.matFC,0)),round2),'.'+str(round2)+'f'))) 
            else:
                self.text7.setText(str(format(round(float(Unit.stress(self,self.matFY,0)),round2),'.'+str(round2)+'f')))     
                self.text8.setText(str(format(round(float(Unit.stress(self,self.matFU,0)),round2),'.'+str(round2)+'f')))
            if self.mattype=='Steel':
                self.label15.setText(stressUnit)

class ISectionPropertyWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(ISectionPropertyWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 355
        self.height = 225
        if mdi.sectiondlg.addsectionbool==False:            
            self.h=mdi.sectiondlg.selectedsection['h']
            self.btop=mdi.sectiondlg.selectedsection['btop']
            self.btopthickness=mdi.sectiondlg.selectedsection['btopthickness']
            self.bbottom=mdi.sectiondlg.selectedsection['bbottom']
            self.bbottomthickness=mdi.sectiondlg.selectedsection['bbottomthickness']
            self.wthickness=mdi.sectiondlg.selectedsection['wthickness']
            self.sectionname=mdi.sectiondlg.selectedsection['name']
            self.sectiondict=[]
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['index']==mdi.sectiondlg.selectedsection['matindex']:
                        self.mat=mat
            for section in Sections.sectiondict:
                if section['name']!=self.sectionname:
                    if section['deleted']==False:
                        self.sectiondict.append(section)
        else:
            self.sectionname="section"
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['type']=='Steel':
                        self.mat=mat
                        break
            self.h=20
            self.btop=9
            self.btopthickness=1.13
            self.bbottom=9
            self.bbottomthickness=1.13
            self.wthickness=0.75

        self.initUI()

    def initUI(self):
        if mdi.sectiondlg.addsectionbool==False:
            self.setWindowTitle("Section Properties of "+self.sectionname)
        else:
            self.setWindowTitle("Add New Section")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label1 = QLabel(self)
        label1.setGeometry(20,20,180,20)
        label1.setText("Section Name:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,180,20)
        label2.setText("Total Height of Section: h:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,180,20)
        label3.setText("Top Flange Width: b-top:")
        label4 = QLabel(self)
        label4.setGeometry(20,80,180,20)
        label4.setText("Top Flange Thickness: bt-Top:")
        label5 = QLabel(self)
        label5.setGeometry(20,100,180,20)
        label5.setText("Bottom Flange Width: b-Bottom:")
        label6 = QLabel(self)
        label6.setGeometry(20,120,180,20)
        label6.setText("Bottom Flange Thickness: bt-Bottom:")        
        label7 = QLabel(self)
        label7.setGeometry(20,140,180,20)
        label7.setText("Web Thickness: wt:")
        label8 = QLabel(self)
        label8.setGeometry(20,160,180,20)
        label8.setText("Material:")

        valid = QDoubleValidator(0.0,99999.999999,6,self)
        valid.setNotation(QDoubleValidator.StandardNotation)        
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.combmattype=QComboBox(self)
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                if mat['type']=='Steel':
                    self.combmattype.addItem(mat['name'])        
        self.combmattype.setCurrentText(self.mat['name'])
        self.combmattype.setGeometry(200,162,120,18)        
        self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)
                        
        self.text1 =QLineEdit(self)        
        self.text1.setText(self.sectionname)
        self.text1.setMaxLength(30)
        self.text1.setGeometry(200,22,120,18)
        self.text1.textEdited.connect(self.text1_changed)

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(200,42,120,18)
        self.text2.setValidator(valid)        
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text2.textEdited.connect(self.text2_changed)

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(200,62,120,18)
        self.text3.setValidator(valid)        
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.btop,0)),6),'.'+str(6)+'f')))
        self.text3.textEdited.connect(self.text3_changed)

        self.text4 = QLineEdit(self)
        self.text4.setGeometry(200,82,120,18)
        self.text4.setValidator(valid)        
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.btopthickness,0)),6),'.'+str(6)+'f')))
        self.text4.textEdited.connect(self.text4_changed)

        self.text5 = QLineEdit(self)
        self.text5.setGeometry(200,102,120,18)
        self.text5.setValidator(valid)        
        self.text5.setText(str(format(round(float(Unit.dimension(self,self.bbottom,0)),6),'.'+str(6)+'f')))
        self.text5.textEdited.connect(self.text5_changed)

        self.text6 = QLineEdit(self)
        self.text6.setGeometry(200,122,120,18)
        self.text6.setValidator(valid)        
        self.text6.setText(str(format(round(float(Unit.dimension(self,self.bbottomthickness,0)),6),'.'+str(6)+'f')))
        self.text6.textEdited.connect(self.text6_changed)

        self.text7 = QLineEdit(self)
        self.text7.setGeometry(200,142,120,18)
        self.text7.setValidator(valid)        
        self.text7.setText(str(format(round(float(Unit.dimension(self,self.wthickness,0)),6),'.'+str(6)+'f')))
        self.text7.textEdited.connect(self.text7_changed)

        okButton = QPushButton('OK',self)
        okButton.setGeometry(200,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,185,100,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)

        self.label11 = QLabel(self)
        self.label11.setGeometry(325,42,50,18)
        self.label11.setText(self.dimensionname)

        self.label12 = QLabel(self)
        self.label12.setGeometry(325,62,50,18)
        self.label12.setText(self.dimensionname)

        self.label13 = QLabel(self)
        self.label13.setGeometry(325,82,50,18)
        self.label13.setText(self.dimensionname)

        self.label14 = QLabel(self)
        self.label14.setGeometry(325,102,50,18)
        self.label14.setText(self.dimensionname)

        self.label15 = QLabel(self)
        self.label15.setGeometry(325,122,50,18)
        self.label15.setText(self.dimensionname)

        self.label16 = QLabel(self)
        self.label16.setGeometry(325,142,50,18)
        self.label16.setText(self.dimensionname)

    def closeEvent(self,event):
        mdi.sectiondlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                if mat['name']==self.combmattype.currentText():    
                    self.mat=mat

    def on_click_ok(self,event):
        if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!="" and self.text4.text()!="" and self.text5.text()!=""  and self.text6.text()!="" and self.text7.text()!="" :
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.sectiondlg.addsectionbool==False:
                if sum(y.get('name')==self.text1.text()  for y in self.sectiondict)==0 :
                    mdi.sectiondlg.selectedsection['h']=self.h
                    mdi.sectiondlg.selectedsection['btop']=self.btop
                    mdi.sectiondlg.selectedsection['btopthickness']=self.btopthickness
                    mdi.sectiondlg.selectedsection['bbottom']=self.bbottom
                    mdi.sectiondlg.selectedsection['bbottomthickness']=self.bbottomthickness
                    mdi.sectiondlg.selectedsection['wthickness']=self.wthickness
                    mdi.sectiondlg.selectedsection['name']=self.sectionname
                    mdi.sectiondlg.selectedsection['matindex']=self.mat['index']
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                    Ishapes(self.sectionname,self.mat['index'],self.h,self.btop,self.btopthickness,self.bbottom,self.bbottomthickness,self.wthickness)
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")

    def text1_changed(self,p):
        if self.text1.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")
            # if mdi.sectiondlg.addsectionbool==False:
            #     if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0 or self.text1.text()==self.sectionname:
            #         self.section['name']=self.text1.text()
            #     else:
            #         self.section['name']=self.sectionname
            #         self.text1.setStyleSheet("border: 1px solid red;")
            # else:
            if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                self.sectionname=self.text1.text()
            else:
                self.text1.setStyleSheet("border: 1px solid red;")
        else:
            self.text1.setStyleSheet("border: 1px solid red;")

    def text2_changed(self,p):
        if self.text2.text()!="":
            self.text2.setStyleSheet("border: 1px solid black;")            
            self.h=float(Unit.dimension(self,float(self.text2.text()),1))
        else:
            self.text2.setStyleSheet("border: 1px solid red;")

    def text3_changed(self,p):
        if self.text3.text()!="":
            self.text3.setStyleSheet("border: 1px solid black;")
            
            self.btop=float(Unit.dimension(self,float(self.text3.text()),1))
        else:
            self.text3.setStyleSheet("border: 1px solid red;")

    def text4_changed(self,p):
        if self.text4.text()!="":
            self.text4.setStyleSheet("border: 1px solid black;")
            
            self.btopthickness=float(Unit.dimension(self,float(self.text4.text()),1))
        else:
            self.text4.setStyleSheet("border: 1px solid red;")

    def text5_changed(self,p):
        if self.text5.text()!="":
            self.text5.setStyleSheet("border: 1px solid black;")
            
            self.bbottom=float(Unit.dimension(self,float(self.text5.text()),1))
        else:
            self.text5.setStyleSheet("border: 1px solid red;")

    def text6_changed(self,p):
        if self.text6.text()!="":
            self.text6.setStyleSheet("border: 1px solid black;")
            
            self.bbottomthickness=float(Unit.dimension(self,float(self.text6.text()),1))
        else:
            self.text6.setStyleSheet("border: 1px solid red;")
    
    def text7_changed(self,p):
        if self.text7.text()!="":
            self.text7.setStyleSheet("border: 1px solid black;")
            
            self.wthickness=float(Unit.dimension(self,float(self.text7.text()),1))
        else:
            self.text7.setStyleSheet("border: 1px solid red;")
    
    def on_combobox_changed(self,index):
        mdi.combounit.setCurrentIndex(index)
        Unit.index(self,index)
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.label11.setText(self.dimensionname)
        self.label12.setText(self.dimensionname)
        self.label13.setText(self.dimensionname)
        self.label14.setText(self.dimensionname)
        self.label15.setText(self.dimensionname)
        self.label16.setText(self.dimensionname)

        
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.btop,0)),6),'.'+str(6)+'f')))
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.btopthickness,0)),6),'.'+str(6)+'f')))
        self.text5.setText(str(format(round(float(Unit.dimension(self,self.bbottom,0)),6),'.'+str(6)+'f')))
        self.text6.setText(str(format(round(float(Unit.dimension(self,self.bbottomthickness,0)),6),'.'+str(6)+'f')))
        self.text7.setText(str(format(round(float(Unit.dimension(self,self.wthickness,0)),6),'.'+str(6)+'f')))

class USectionPropertyWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(USectionPropertyWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 355
        self.height = 225
        if mdi.sectiondlg.addsectionbool==False:
            
            self.sectionname=mdi.sectiondlg.selectedsection['name']
            self.h=mdi.sectiondlg.selectedsection['h']
            self.b=mdi.sectiondlg.selectedsection['b']
            self.bthickness=mdi.sectiondlg.selectedsection['bthickness']
            self.wthickness=mdi.sectiondlg.selectedsection['wthickness']

            self.sectiondict=[]
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['index']==mdi.sectiondlg.selectedsection['matindex']:
                        self.mat=mat
            for section in Sections.sectiondict:
                if section['name']!=self.sectionname:
                    if section['deleted']==False:
                        self.sectiondict.append(section)
        else:
            self.sectionname="section"
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['type']=='Steel':
                        self.mat=mat
                        break            
            self.h=20
            self.b=9
            self.bthickness=1.13
            self.wthickness=0.75

        self.initUI()

    def initUI(self):
        if mdi.sectiondlg.addsectionbool==False:
            self.setWindowTitle("Section Properties of "+self.sectionname)
        else:
            self.setWindowTitle("Add New Section")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label1 = QLabel(self)
        label1.setGeometry(20,20,180,20)
        label1.setText("Section Name:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,180,20)
        label2.setText("Total Height of Section: h:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,180,20)
        label3.setText("Flange Width: b:")
        label4 = QLabel(self)
        label4.setGeometry(20,80,180,20)
        label4.setText("Flange Thickness: bt:")
        label7 = QLabel(self)
        label7.setGeometry(20,100,180,20)
        label7.setText("Web Thickness: wt:")
        label8 = QLabel(self)
        label8.setGeometry(20,160,180,20)
        label8.setText("Material:")

        valid = QDoubleValidator(0.0,99999.999999,6,self)
        valid.setNotation(QDoubleValidator.StandardNotation)        
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.combmattype=QComboBox(self)
        for mat in Materials.materialdict:            
            if mat['deleted']==False:
                if mat['type']=='Steel':
                    self.combmattype.addItem(mat['name'])        
        self.combmattype.setCurrentText(self.mat['name'])
        self.combmattype.setGeometry(200,162,120,18)        
        self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)
                        
        self.text1 =QLineEdit(self)        
        self.text1.setText(self.sectionname)
        self.text1.setMaxLength(30)
        self.text1.setGeometry(200,22,120,18)
        self.text1.textEdited.connect(self.text1_changed)

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(200,42,120,18)
        self.text2.setValidator(valid)        
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text2.textEdited.connect(self.text2_changed)

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(200,62,120,18)
        self.text3.setValidator(valid)        
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))
        self.text3.textEdited.connect(self.text3_changed)

        self.text4 = QLineEdit(self)
        self.text4.setGeometry(200,82,120,18)
        self.text4.setValidator(valid)        
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.bthickness,0)),6),'.'+str(6)+'f')))
        self.text4.textEdited.connect(self.text4_changed)
        
        self.text7 = QLineEdit(self)
        self.text7.setGeometry(200,102,120,18)
        self.text7.setValidator(valid)        
        self.text7.setText(str(format(round(float(Unit.dimension(self,self.wthickness,0)),6),'.'+str(6)+'f')))
        self.text7.textEdited.connect(self.text7_changed)

        okButton = QPushButton('OK',self)
        okButton.setGeometry(200,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,185,100,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)

        self.label11 = QLabel(self)
        self.label11.setGeometry(325,42,50,18)
        self.label11.setText(self.dimensionname)

        self.label12 = QLabel(self)
        self.label12.setGeometry(325,62,50,18)
        self.label12.setText(self.dimensionname)

        self.label13 = QLabel(self)
        self.label13.setGeometry(325,82,50,18)
        self.label13.setText(self.dimensionname)

        self.label14 = QLabel(self)
        self.label14.setGeometry(325,102,50,18)
        self.label14.setText(self.dimensionname)

    def closeEvent(self,event):
        mdi.sectiondlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                if mat['name']==self.combmattype.currentText():                    
                    self.mat=mat

    def on_click_ok(self,event):
        if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!="" and self.text4.text()!="" and self.text7.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.sectiondlg.addsectionbool==False:
                if sum(y.get('name')==self.text1.text()  for y in self.sectiondict)==0 :
                    mdi.sectiondlg.selectedsection['name']=self.sectionname
                    mdi.sectiondlg.selectedsection['h']=self.h
                    mdi.sectiondlg.selectedsection['b']=self.b
                    mdi.sectiondlg.selectedsection['bthickness']=self.bthickness
                    mdi.sectiondlg.selectedsection['wthickness']=self.wthickness
                    mdi.sectiondlg.selectedsection['matindex']=self.mat['index']
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                    Ushapes(self.sectionname,self.mat['index'],self.h,self.b,self.bthickness,self.wthickness)
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")

    def text1_changed(self,p):
        if self.text1.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")
            
            if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                self.sectionname=self.text1.text()
            else:
                self.text1.setStyleSheet("border: 1px solid red;")
        else:
            self.text1.setStyleSheet("border: 1px solid red;")

    def text2_changed(self,p):
        if self.text2.text()!="":
            self.text2.setStyleSheet("border: 1px solid black;")
            
            self.h=float(Unit.dimension(self,float(self.text2.text()),1))
        else:
            self.text2.setStyleSheet("border: 1px solid red;")

    def text3_changed(self,p):
        if self.text3.text()!="":
            self.text3.setStyleSheet("border: 1px solid black;")
            
            self.b=float(Unit.dimension(self,float(self.text3.text()),1))
        else:
            self.text3.setStyleSheet("border: 1px solid red;")

    def text4_changed(self,p):
        if self.text4.text()!="":
            self.text4.setStyleSheet("border: 1px solid black;")
            
            self.bthickness=float(Unit.dimension(self,float(self.text4.text()),1))
        else:
            self.text4.setStyleSheet("border: 1px solid red;")
    
    def text7_changed(self,p):
        if self.text7.text()!="":
            self.text7.setStyleSheet("border: 1px solid black;")            
            self.wthickness=float(Unit.dimension(self,float(self.text7.text()),1))
        else:
            self.text7.setStyleSheet("border: 1px solid red;")
    
    def on_combobox_changed(self,index):
        mdi.combounit.setCurrentIndex(index)
        Unit.index(self,index)
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.label11.setText(self.dimensionname)
        self.label12.setText(self.dimensionname)
        self.label13.setText(self.dimensionname)
        self.label14.setText(self.dimensionname)
        
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.bthickness,0)),6),'.'+str(6)+'f')))
        self.text7.setText(str(format(round(float(Unit.dimension(self,self.wthickness,0)),6),'.'+str(6)+'f')))

class DLSectionPropertyWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(DLSectionPropertyWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 355
        self.height = 225
        if mdi.sectiondlg.addsectionbool==False:            
            self.h=mdi.sectiondlg.selectedsection['h']
            self.b=mdi.sectiondlg.selectedsection['b']
            self.bthickness=mdi.sectiondlg.selectedsection['bthickness']
            self.hthickness=mdi.sectiondlg.selectedsection['hthickness']
            self.distance=mdi.sectiondlg.selectedsection['distance']
            self.sectionname=mdi.sectiondlg.selectedsection['name']
            self.sectiondict=[]
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['index']==mdi.sectiondlg.selectedsection['matindex']:
                        self.mat=mat
            for section in Sections.sectiondict:
                if section['name']!=self.sectionname:
                    if section['deleted']==False:
                        self.sectiondict.append(section)
        else:
            self.sectionname="section"
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['type']=='Steel':
                        self.mat=mat
                        break            
            self.h=10
            self.b=10
            self.bthickness=1
            self.hthickness=1
            self.distance=2

        self.initUI()

    def initUI(self):
        if mdi.sectiondlg.addsectionbool==False:
            self.setWindowTitle("Section Properties of "+self.sectionname)
        else:
            self.setWindowTitle("Add New Section")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label1 = QLabel(self)
        label1.setGeometry(20,20,180,20)
        label1.setText("Section Name:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,180,20)
        label2.setText("Vertical Leg Height: h:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,180,20)
        label3.setText("Vertical Leg Thickness: ht:")
        label4 = QLabel(self)
        label4.setGeometry(20,80,180,20)
        label4.setText("Horizontal Leg Width: b:")
        label5 = QLabel(self)
        label5.setGeometry(20,100,180,20)
        label5.setText("Horizontal Leg Thickness: bt:")
        label6 = QLabel(self)
        label6.setGeometry(20,120,180,20)
        label6.setText("Distance Between Sections: d:")        
        label8 = QLabel(self)
        label8.setGeometry(20,160,180,20)
        label8.setText("Material:")

        valid = QDoubleValidator(0.0,99999.999999,6,self)
        valid.setNotation(QDoubleValidator.StandardNotation)        
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.combmattype=QComboBox(self)
        for mat in Materials.materialdict:            
            if mat['deleted']==False:
                if mat['type']=='Steel':
                    self.combmattype.addItem(mat['name'])                       
        self.combmattype.setCurrentText(self.mat['name'])
        self.combmattype.setGeometry(200,162,120,18)        
        self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)
                        
        self.text1 =QLineEdit(self)
        self.text1.setText(self.sectionname)
        self.text1.setMaxLength(30)
        self.text1.setGeometry(200,22,120,18)
        self.text1.textEdited.connect(self.text1_changed)

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(200,42,120,18)
        self.text2.setValidator(valid)
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text2.textEdited.connect(self.text2_changed)

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(200,62,120,18)
        self.text3.setValidator(valid)
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.hthickness,0)),6),'.'+str(6)+'f')))
        self.text3.textEdited.connect(self.text3_changed)

        self.text4 = QLineEdit(self)
        self.text4.setGeometry(200,82,120,18)
        self.text4.setValidator(valid)
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))
        self.text4.textEdited.connect(self.text4_changed)

        self.text5 = QLineEdit(self)
        self.text5.setGeometry(200,102,120,18)
        self.text5.setValidator(valid)
        self.text5.setText(str(format(round(float(Unit.dimension(self,self.bthickness,0)),6),'.'+str(6)+'f')))
        self.text5.textEdited.connect(self.text5_changed)

        self.text6 = QLineEdit(self)
        self.text6.setGeometry(200,122,120,18)
        self.text6.setValidator(valid)
        self.text6.setText(str(format(round(float(Unit.dimension(self,self.distance,0)),6),'.'+str(6)+'f')))
        self.text6.textEdited.connect(self.text6_changed)

        okButton = QPushButton('OK',self)
        okButton.setGeometry(200,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,185,100,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)

        self.label11 = QLabel(self)
        self.label11.setGeometry(325,42,50,18)
        self.label11.setText(self.dimensionname)

        self.label12 = QLabel(self)
        self.label12.setGeometry(325,62,50,18)
        self.label12.setText(self.dimensionname)

        self.label13 = QLabel(self)
        self.label13.setGeometry(325,82,50,18)
        self.label13.setText(self.dimensionname)

        self.label14 = QLabel(self)
        self.label14.setGeometry(325,102,50,18)
        self.label14.setText(self.dimensionname)

        self.label15 = QLabel(self)
        self.label15.setGeometry(325,122,50,18)
        self.label15.setText(self.dimensionname)

    def closeEvent(self,event):
        mdi.sectiondlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                if mat['name']==self.combmattype.currentText():    
                    self.mat=mat

    def on_click_ok(self,event):
        if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!="" and self.text4.text()!="" and self.text5.text()!="" and self.text6.text()!="" :
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.sectiondlg.addsectionbool==False:
                if sum(y.get('name')==self.text1.text()  for y in self.sectiondict)==0 :
                    mdi.sectiondlg.selectedsection['h']=self.h
                    mdi.sectiondlg.selectedsection['b']=self.b
                    mdi.sectiondlg.selectedsection['bthickness']=self.bthickness
                    mdi.sectiondlg.selectedsection['hthickness']=self.hthickness
                    mdi.sectiondlg.selectedsection['distance']=self.distance
                    mdi.sectiondlg.selectedsection['name']=self.sectionname
                    mdi.sectiondlg.selectedsection['matindex']=self.mat['index']
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                    DLshape(self.sectionname,self.mat['index'],self.h,self.b,self.bthickness,self.hthickness,self.distance)
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")

    def text1_changed(self,p):
        if self.text1.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")
            
            if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                self.sectionname=self.text1.text()
            else:
                self.text1.setStyleSheet("border: 1px solid red;")
        else:
            self.text1.setStyleSheet("border: 1px solid red;")

    def text2_changed(self,p):
        if self.text2.text()!="":
            self.text2.setStyleSheet("border: 1px solid black;")
            
            self.h=float(Unit.dimension(self,float(self.text2.text()),1))
        else:
            self.text2.setStyleSheet("border: 1px solid red;")

    def text3_changed(self,p):
        if self.text3.text()!="":
            self.text3.setStyleSheet("border: 1px solid black;")
            
            self.hthickness=float(Unit.dimension(self,float(self.text3.text()),1))
        else:
            self.text3.setStyleSheet("border: 1px solid red;")

    def text4_changed(self,p):
        if self.text4.text()!="":
            self.text4.setStyleSheet("border: 1px solid black;")
            
            self.b=float(Unit.dimension(self,float(self.text4.text()),1))
        else:
            self.text4.setStyleSheet("border: 1px solid red;")

    def text5_changed(self,p):
        if self.text5.text()!="":
            self.text5.setStyleSheet("border: 1px solid black;")
            
            self.bthickness=float(Unit.dimension(self,float(self.text5.text()),1))
        else:
            self.text5.setStyleSheet("border: 1px solid red;")

    def text6_changed(self,p):
        if self.text6.text()!="":
            self.text6.setStyleSheet("border: 1px solid black;")
            
            self.distance=float(Unit.dimension(self,float(self.text6.text()),1))
        else:
            self.text6.setStyleSheet("border: 1px solid red;")

    def on_combobox_changed(self,index):
        mdi.combounit.setCurrentIndex(index)
        Unit.index(self,index)
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.label11.setText(self.dimensionname)
        self.label12.setText(self.dimensionname)
        self.label13.setText(self.dimensionname)
        self.label14.setText(self.dimensionname)
        self.label15.setText(self.dimensionname)


        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.hthickness,0)),6),'.'+str(6)+'f')))
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))
        self.text5.setText(str(format(round(float(Unit.dimension(self,self.bthickness,0)),6),'.'+str(6)+'f')))
        self.text6.setText(str(format(round(float(Unit.dimension(self,self.distance,0)),6),'.'+str(6)+'f')))

class LSectionPropertyWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(LSectionPropertyWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 355
        self.height = 225
        if mdi.sectiondlg.addsectionbool==False:
            self.h=mdi.sectiondlg.selectedsection['h']
            self.b=mdi.sectiondlg.selectedsection['b']
            self.bthickness=mdi.sectiondlg.selectedsection['bthickness']
            self.hthickness=mdi.sectiondlg.selectedsection['hthickness']
            self.sectionname=mdi.sectiondlg.selectedsection['name']
            self.sectiondict=[]
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['index']==mdi.sectiondlg.selectedsection['matindex']:
                        self.mat=mat
            for section in Sections.sectiondict:
                if section['name']!=self.sectionname:
                    if section['deleted']==False:
                        self.sectiondict.append(section)
        else:
            self.sectionname="section"
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['type']=='Steel':
                        self.mat=mat
                        break            
            self.h=10
            self.b=10
            self.bthickness=1
            self.hthickness=1
            

        self.initUI()

    def initUI(self):
        if mdi.sectiondlg.addsectionbool==False:
            self.setWindowTitle("Section Properties of "+self.sectionname)
        else:
            self.setWindowTitle("Add New Section")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label1 = QLabel(self)
        label1.setGeometry(20,20,180,20)
        label1.setText("Section Name:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,180,20)
        label2.setText("Vertical Leg Height: h:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,180,20)
        label3.setText("Vertical Leg Thickness: ht:")
        label4 = QLabel(self)
        label4.setGeometry(20,80,180,20)
        label4.setText("Horizontal Leg Width: b:")
        label5 = QLabel(self)
        label5.setGeometry(20,100,180,20)
        label5.setText("Horizontal Leg Thickness: bt:")
            
        label8 = QLabel(self)
        label8.setGeometry(20,160,180,20)
        label8.setText("Material:")

        valid = QDoubleValidator(0.0,99999.999999,6,self)
        valid.setNotation(QDoubleValidator.StandardNotation)        
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.combmattype=QComboBox(self)
        for mat in Materials.materialdict:            
            if mat['deleted']==False:
                if mat['type']=='Steel':
                    self.combmattype.addItem(mat['name'])        
        self.combmattype.setCurrentText(self.mat['name'])
        self.combmattype.setGeometry(200,162,120,18)        
        self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)
                        
        self.text1 =QLineEdit(self)
        self.text1.setText(self.sectionname)
        self.text1.setMaxLength(30)
        self.text1.setGeometry(200,22,120,18)
        self.text1.textEdited.connect(self.text1_changed)

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(200,42,120,18)
        self.text2.setValidator(valid)
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text2.textEdited.connect(self.text2_changed)

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(200,62,120,18)
        self.text3.setValidator(valid)
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.hthickness,0)),6),'.'+str(6)+'f')))
        self.text3.textEdited.connect(self.text3_changed)

        self.text4 = QLineEdit(self)
        self.text4.setGeometry(200,82,120,18)
        self.text4.setValidator(valid)
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))
        self.text4.textEdited.connect(self.text4_changed)

        self.text5 = QLineEdit(self)
        self.text5.setGeometry(200,102,120,18)
        self.text5.setValidator(valid)
        self.text5.setText(str(format(round(float(Unit.dimension(self,self.bthickness,0)),6),'.'+str(6)+'f')))
        self.text5.textEdited.connect(self.text5_changed)

        okButton = QPushButton('OK',self)
        okButton.setGeometry(200,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,185,100,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)

        self.label11 = QLabel(self)
        self.label11.setGeometry(325,42,50,18)
        self.label11.setText(self.dimensionname)

        self.label12 = QLabel(self)
        self.label12.setGeometry(325,62,50,18)
        self.label12.setText(self.dimensionname)

        self.label13 = QLabel(self)
        self.label13.setGeometry(325,82,50,18)
        self.label13.setText(self.dimensionname)

        self.label14 = QLabel(self)
        self.label14.setGeometry(325,102,50,18)
        self.label14.setText(self.dimensionname)

    def closeEvent(self,event):
        mdi.sectiondlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                if mat['name']==self.combmattype.currentText():    
                    self.mat=mat

    def on_click_ok(self,event):
        if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!="" and self.text4.text()!="" and self.text5.text()!=""  :
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.sectiondlg.addsectionbool==False:
                if sum(y.get('name')==self.text1.text()  for y in self.sectiondict)==0 :
                    mdi.sectiondlg.selectedsection['h']=self.h
                    mdi.sectiondlg.selectedsection['b']=self.b
                    mdi.sectiondlg.selectedsection['bthickness']=self.bthickness
                    mdi.sectiondlg.selectedsection['hthickness']=self.hthickness
                    mdi.sectiondlg.selectedsection['name']=self.sectionname
                    mdi.sectiondlg.selectedsection['matindex']=self.mat['index']
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                    Lshape(self.sectionname,self.mat['index'],self.h,self.b,self.bthickness,self.hthickness)
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")

    def text1_changed(self,p):
        if self.text1.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")

            if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                self.sectionname=self.text1.text()
            else:
                self.text1.setStyleSheet("border: 1px solid red;")
        else:
            self.text1.setStyleSheet("border: 1px solid red;")

    def text2_changed(self,p):
        if self.text2.text()!="":
            self.text2.setStyleSheet("border: 1px solid black;")
            self.h=float(Unit.dimension(self,float(self.text2.text()),1))
        else:
            self.text2.setStyleSheet("border: 1px solid red;")

    def text3_changed(self,p):
        if self.text3.text()!="":
            self.text3.setStyleSheet("border: 1px solid black;")
            self.hthickness=float(Unit.dimension(self,float(self.text3.text()),1))
        else:
            self.text3.setStyleSheet("border: 1px solid red;")

    def text4_changed(self,p):
        if self.text4.text()!="":
            self.text4.setStyleSheet("border: 1px solid black;")

            self.b=float(Unit.dimension(self,float(self.text4.text()),1))
        else:
            self.text4.setStyleSheet("border: 1px solid red;")

    def text5_changed(self,p):
        if self.text5.text()!="":
            self.text5.setStyleSheet("border: 1px solid black;")

            self.bthickness=float(Unit.dimension(self,float(self.text5.text()),1))
        else:
            self.text5.setStyleSheet("border: 1px solid red;")

    def on_combobox_changed(self,index):
        mdi.combounit.setCurrentIndex(index)
        Unit.index(self,index)
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.label11.setText(self.dimensionname)
        self.label12.setText(self.dimensionname)
        self.label13.setText(self.dimensionname)
        self.label14.setText(self.dimensionname)        

        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.hthickness,0)),6),'.'+str(6)+'f')))
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))
        self.text5.setText(str(format(round(float(Unit.dimension(self,self.bthickness,0)),6),'.'+str(6)+'f')))

class RecSectionPropertyWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(RecSectionPropertyWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 355
        self.height = 225
        if mdi.sectiondlg.addsectionbool==False:
            self.h=mdi.sectiondlg.selectedsection['h']
            self.b=mdi.sectiondlg.selectedsection['b']
            self.thickness=mdi.sectiondlg.selectedsection['thickness']
            self.sectionname=mdi.sectiondlg.selectedsection['name']
            self.sectiondict=[]
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['index']==mdi.sectiondlg.selectedsection['matindex']:
                        self.mat=mat
            for section in Sections.sectiondict:
                if section['name']!=self.sectionname:
                    if section['deleted']==False:
                        self.sectiondict.append(section)
        else:
            self.sectionname="section"
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['type']=='Steel':
                        self.mat=mat
                        break            
            self.h=10
            self.b=10
            self.thickness=1


        self.initUI()

    def initUI(self):
        if mdi.sectiondlg.addsectionbool==False:
            self.setWindowTitle("Section Properties of "+self.sectionname)
        else:
            self.setWindowTitle("Add New Section")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label1 = QLabel(self)
        label1.setGeometry(20,20,180,20)
        label1.setText("Section Name:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,180,20)
        label2.setText("Height: h:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,180,20)
        label3.setText("Width: b:")
        label4 = QLabel(self)
        label4.setGeometry(20,80,180,20)
        label4.setText("Thickness: t:")

            
        label8 = QLabel(self)
        label8.setGeometry(20,160,180,20)
        label8.setText("Material:")

        valid = QDoubleValidator(0.0,99999.999999,6,self)
        valid.setNotation(QDoubleValidator.StandardNotation)        
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.combmattype=QComboBox(self)
        for mat in Materials.materialdict:            
            if mat['deleted']==False:
                if mat['type']=='Steel':
                    self.combmattype.addItem(mat['name'])       
        self.combmattype.setCurrentText(self.mat['name'])
        self.combmattype.setGeometry(200,162,120,18)        
        self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)
                        
        self.text1 =QLineEdit(self)
        self.text1.setText(self.sectionname)
        self.text1.setMaxLength(30)
        self.text1.setGeometry(200,22,120,18)
        self.text1.textEdited.connect(self.text1_changed)

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(200,42,120,18)
        self.text2.setValidator(valid)
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text2.textEdited.connect(self.text2_changed)

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(200,62,120,18)
        self.text3.setValidator(valid)
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))
        self.text3.textEdited.connect(self.text3_changed)

        self.text4 = QLineEdit(self)
        self.text4.setGeometry(200,82,120,18)
        self.text4.setValidator(valid)
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.thickness,0)),6),'.'+str(6)+'f')))
        self.text4.textEdited.connect(self.text4_changed)

        okButton = QPushButton('OK',self)
        okButton.setGeometry(200,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,185,100,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)

        self.label11 = QLabel(self)
        self.label11.setGeometry(325,42,50,18)
        self.label11.setText(self.dimensionname)

        self.label12 = QLabel(self)
        self.label12.setGeometry(325,62,50,18)
        self.label12.setText(self.dimensionname)

        self.label13 = QLabel(self)
        self.label13.setGeometry(325,82,50,18)
        self.label13.setText(self.dimensionname)

    def closeEvent(self,event):
        mdi.sectiondlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                if mat['name']==self.combmattype.currentText():    
                    self.mat=mat

    def on_click_ok(self,event):
        if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!="" and self.text4.text()!="" :
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.sectiondlg.addsectionbool==False:
                if sum(y.get('name')==self.text1.text()  for y in self.sectiondict)==0 :
                    mdi.sectiondlg.selectedsection['h']=self.h
                    mdi.sectiondlg.selectedsection['b']=self.b
                    mdi.sectiondlg.selectedsection['thickness']=self.thickness
                    mdi.sectiondlg.selectedsection['name']=self.sectionname
                    mdi.sectiondlg.selectedsection['matindex']=self.mat['index']
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                    Rectangular(self.sectionname,self.mat['index'],self.h,self.b,self.thickness)
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")

    def text1_changed(self,p):
        if self.text1.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")

            if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                self.sectionname=self.text1.text()
            else:
                self.text1.setStyleSheet("border: 1px solid red;")
        else:
            self.text1.setStyleSheet("border: 1px solid red;")

    def text2_changed(self,p):
        if self.text2.text()!="":
            self.text2.setStyleSheet("border: 1px solid black;")

            self.h=float(Unit.dimension(self,float(self.text2.text()),1))
        else:
            self.text2.setStyleSheet("border: 1px solid red;")

    def text3_changed(self,p):
        if self.text3.text()!="":
            self.text3.setStyleSheet("border: 1px solid black;")

            self.b=float(Unit.dimension(self,float(self.text3.text()),1))
        else:
            self.text3.setStyleSheet("border: 1px solid red;")

    def text4_changed(self,p):
        if self.text4.text()!="":
            self.text4.setStyleSheet("border: 1px solid black;")
            self.thickness=float(Unit.dimension(self,float(self.text4.text()),1))
        else:
            self.text4.setStyleSheet("border: 1px solid red;")

    def on_combobox_changed(self,index):
        mdi.combounit.setCurrentIndex(index)
        Unit.index(self,index)
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.label11.setText(self.dimensionname)
        self.label12.setText(self.dimensionname)
        self.label13.setText(self.dimensionname)     

        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))
        self.text4.setText(str(format(round(float(Unit.dimension(self,self.thickness,0)),6),'.'+str(6)+'f')))

class CirSectionPropertyWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(CirSectionPropertyWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 355
        self.height = 225
        if mdi.sectiondlg.addsectionbool==False:
            self.d=mdi.sectiondlg.selectedsection['d']
            self.thickness=mdi.sectiondlg.selectedsection['thickness']
            self.sectionname=mdi.sectiondlg.selectedsection['name']
            self.sectiondict=[]
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['index']==mdi.sectiondlg.selectedsection['matindex']:
                        self.mat=mat
            for section in Sections.sectiondict:
                if section['name']!=self.sectionname:
                    if section['deleted']==False:
                        self.sectiondict.append(section)
        else:
            self.sectionname="section"
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['type']=='Steel':
                        self.mat=mat
                        break            
            self.d=10
            self.thickness=0.5

        self.initUI()

    def initUI(self):
        if mdi.sectiondlg.addsectionbool==False:
            self.setWindowTitle("Section Properties of "+self.sectionname)
        else:
            self.setWindowTitle("Add New Section")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label1 = QLabel(self)
        label1.setGeometry(20,20,180,20)
        label1.setText("Section Name:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,180,20)
        label2.setText("Diameter: d:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,180,20)
        label3.setText("Thickness: t:")
            
        label8 = QLabel(self)
        label8.setGeometry(20,160,180,20)
        label8.setText("Material:")

        valid = QDoubleValidator(0.0,99999.999999,6,self)
        valid.setNotation(QDoubleValidator.StandardNotation)        
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.combmattype=QComboBox(self)
        for mat in Materials.materialdict:            
            if mat['deleted']==False:
                if mat['type']=='Steel':
                    self.combmattype.addItem(mat['name'])       
        self.combmattype.setCurrentText(self.mat['name'])
        self.combmattype.setGeometry(200,162,120,18)        
        self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)
                        
        self.text1 =QLineEdit(self)
        self.text1.setText(self.sectionname)
        self.text1.setMaxLength(30)
        self.text1.setGeometry(200,22,120,18)
        self.text1.textEdited.connect(self.text1_changed)

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(200,42,120,18)
        self.text2.setValidator(valid)
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.d,0)),6),'.'+str(6)+'f')))
        self.text2.textEdited.connect(self.text2_changed)

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(200,62,120,18)
        self.text3.setValidator(valid)
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.thickness,0)),6),'.'+str(6)+'f')))
        self.text3.textEdited.connect(self.text3_changed)

        okButton = QPushButton('OK',self)
        okButton.setGeometry(200,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,185,100,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)

        self.label11 = QLabel(self)
        self.label11.setGeometry(325,42,50,18)
        self.label11.setText(self.dimensionname)

        self.label12 = QLabel(self)
        self.label12.setGeometry(325,62,50,18)
        self.label12.setText(self.dimensionname)

    def closeEvent(self,event):
        mdi.sectiondlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                if mat['name']==self.combmattype.currentText():    
                    self.mat=mat

    def on_click_ok(self,event):
        if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!=""  :
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.sectiondlg.addsectionbool==False:
                if sum(y.get('name')==self.text1.text()  for y in self.sectiondict)==0 :
                    mdi.sectiondlg.selectedsection['d']=self.d
                    mdi.sectiondlg.selectedsection['thickness']=self.thickness
                    mdi.sectiondlg.selectedsection['name']=self.sectionname
                    mdi.sectiondlg.selectedsection['matindex']=self.mat['index']

                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                    Circular(self.sectionname,self.mat['index'],self.d,self.thickness)
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")

    def text1_changed(self,p):
        if self.text1.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")
            if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                self.sectionname=self.text1.text()
            else:
                self.text1.setStyleSheet("border: 1px solid red;")
        else:
            self.text1.setStyleSheet("border: 1px solid red;")

    def text2_changed(self,p):
        if self.text2.text()!="":
            self.text2.setStyleSheet("border: 1px solid black;")

            self.d=float(Unit.dimension(self,float(self.text2.text()),1))
        else:
            self.text2.setStyleSheet("border: 1px solid red;")

    def text3_changed(self,p):
        if self.text3.text()!="":
            self.text3.setStyleSheet("border: 1px solid black;")

            self.thickness=float(Unit.dimension(self,float(self.text3.text()),1))
        else:
            self.text3.setStyleSheet("border: 1px solid red;")

    def on_combobox_changed(self,index):
        mdi.combounit.setCurrentIndex(index)
        Unit.index(self,index)
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.label11.setText(self.dimensionname)
        self.label12.setText(self.dimensionname)


        self.text2.setText(str(format(round(float(Unit.dimension(self,self.d,0)),6),'.'+str(6)+'f')))
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.thickness,0)),6),'.'+str(6)+'f')))

class RecBarSectionPropertyWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(RecBarSectionPropertyWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 355
        self.height = 225
        if mdi.sectiondlg.addsectionbool==False:
            self.h=mdi.sectiondlg.selectedsection['h']
            self.b=mdi.sectiondlg.selectedsection['b']
            self.sectionname=mdi.sectiondlg.selectedsection['name']
            self.sectiondict=[]
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['index']==mdi.sectiondlg.selectedsection['matindex']:
                        self.mat=mat
            for section in Sections.sectiondict:
                if section['name']!=self.sectionname:
                    if section['deleted']==False:
                        self.sectiondict.append(section)
        else:
            self.sectionname="section"
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['type']=='Steel':
                        self.mat=mat
                        break            
            self.h=10
            self.b=10

        self.initUI()

    def initUI(self):
        if mdi.sectiondlg.addsectionbool==False:
            self.setWindowTitle("Section Properties of "+self.sectionname)
        else:
            self.setWindowTitle("Add New Section")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label1 = QLabel(self)
        label1.setGeometry(20,20,180,20)
        label1.setText("Section Name:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,180,20)
        label2.setText("Height: h:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,180,20)
        label3.setText("Width: b:")
            
        label8 = QLabel(self)
        label8.setGeometry(20,160,180,20)
        label8.setText("Material:")

        valid = QDoubleValidator(0.0,99999.999999,6,self)
        valid.setNotation(QDoubleValidator.StandardNotation)        
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.combmattype=QComboBox(self)
        for mat in Materials.materialdict:            
            if mat['deleted']==False:
                if mat['type']==Variables.selectionmattype:
                    self.combmattype.addItem(mat['name'])
        self.combmattype.setCurrentText(self.mat['name'])
        self.combmattype.setGeometry(200,162,120,18)        
        self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)

        self.text1 =QLineEdit(self)
        self.text1.setText(self.sectionname)
        self.text1.setMaxLength(30)
        self.text1.setGeometry(200,22,120,18)
        self.text1.textEdited.connect(self.text1_changed)

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(200,42,120,18)
        self.text2.setValidator(valid)
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text2.textEdited.connect(self.text2_changed)

        self.text3 = QLineEdit(self)
        self.text3.setGeometry(200,62,120,18)
        self.text3.setValidator(valid)
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))
        self.text3.textEdited.connect(self.text3_changed)

        okButton = QPushButton('OK',self)
        okButton.setGeometry(200,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,185,100,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)

        self.label11 = QLabel(self)
        self.label11.setGeometry(325,42,50,18)
        self.label11.setText(self.dimensionname)

        self.label12 = QLabel(self)
        self.label12.setGeometry(325,62,50,18)
        self.label12.setText(self.dimensionname)

    def closeEvent(self,event):
        mdi.sectiondlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                if mat['name']==self.combmattype.currentText():    
                    self.mat=mat

    def on_click_ok(self,event):
        if self.text1.text()!="" and self.text2.text()!="" and self.text3.text()!="" :
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.sectiondlg.addsectionbool==False:
                if sum(y.get('name')==self.text1.text()  for y in self.sectiondict)==0 :
                    mdi.sectiondlg.selectedsection['h']=self.h
                    mdi.sectiondlg.selectedsection['b']=self.b
                    mdi.sectiondlg.selectedsection['name']=self.sectionname
                    mdi.sectiondlg.selectedsection['matindex']=self.mat['index']
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                    Rectangularbar(self.sectionname,self.mat['index'],self.h,self.b)
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")

    def text1_changed(self,p):
        if self.text1.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")

            if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                self.sectionname=self.text1.text()
            else:
                self.text1.setStyleSheet("border: 1px solid red;")
        else:
            self.text1.setStyleSheet("border: 1px solid red;")

    def text2_changed(self,p):
        if self.text2.text()!="":
            self.text2.setStyleSheet("border: 1px solid black;")

            self.h=float(Unit.dimension(self,float(self.text2.text()),1))
        else:
            self.text2.setStyleSheet("border: 1px solid red;")

    def text3_changed(self,p):
        if self.text3.text()!="":
            self.text3.setStyleSheet("border: 1px solid black;")

            self.b=float(Unit.dimension(self,float(self.text3.text()),1))
        else:
            self.text3.setStyleSheet("border: 1px solid red;")

    def on_combobox_changed(self,index):
        mdi.combounit.setCurrentIndex(index)
        Unit.index(self,index)
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.label11.setText(self.dimensionname)
        self.label12.setText(self.dimensionname)

        self.text2.setText(str(format(round(float(Unit.dimension(self,self.h,0)),6),'.'+str(6)+'f')))
        self.text3.setText(str(format(round(float(Unit.dimension(self,self.b,0)),6),'.'+str(6)+'f')))

class CirBarSectionPropertyWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(CirBarSectionPropertyWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 355
        self.height = 225
        if mdi.sectiondlg.addsectionbool==False:
            self.d=mdi.sectiondlg.selectedsection['d']
            self.sectionname=mdi.sectiondlg.selectedsection['name']
            self.sectiondict=[]
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['index']==mdi.sectiondlg.selectedsection['matindex']:
                        self.mat=mat
            for section in Sections.sectiondict:
                if section['name']!=self.sectionname:
                    if section['deleted']==False:
                        self.sectiondict.append(section)
        else:
            self.sectionname="section"
            for mat in Materials.materialdict:
                if mat['deleted']==False:
                    if mat['type']=='Steel':
                        self.mat=mat
                        break            
            self.d=10

        self.initUI()

    def initUI(self):
        if mdi.sectiondlg.addsectionbool==False:
            self.setWindowTitle("Section Properties of "+self.sectionname)
        else:
            self.setWindowTitle("Add New Section")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label1 = QLabel(self)
        label1.setGeometry(20,20,180,20)
        label1.setText("Section Name:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,180,20)
        label2.setText("Diameter: d:")
            
        label8 = QLabel(self)
        label8.setGeometry(20,160,180,20)
        label8.setText("Material:")

        valid = QDoubleValidator(0.0,99999.999999,6,self)
        valid.setNotation(QDoubleValidator.StandardNotation)        
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.combmattype=QComboBox(self)
        for mat in Materials.materialdict:            
            if mat['deleted']==False:
                if mat['type']==Variables.selectionmattype:
                    self.combmattype.addItem(mat['name'])      
        self.combmattype.setCurrentText(self.mat['name'])
        self.combmattype.setGeometry(200,162,120,18)        
        self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)

        self.text1 =QLineEdit(self)
        self.text1.setText(self.sectionname)
        self.text1.setMaxLength(30)
        self.text1.setGeometry(200,22,120,18)
        self.text1.textEdited.connect(self.text1_changed)

        self.text2 = QLineEdit(self)
        self.text2.setGeometry(200,42,120,18)
        self.text2.setValidator(valid)
        self.text2.setText(str(format(round(float(Unit.dimension(self,self.d,0)),6),'.'+str(6)+'f')))
        self.text2.textEdited.connect(self.text2_changed)

        okButton = QPushButton('OK',self)
        okButton.setGeometry(200,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

        self.combounit=QComboBox(self)
        self.combounit.addItems(Variables.units)
        self.combounit.setCurrentIndex(Variables.unitindex)
        self.combounit.setGeometry(20,185,100,20)
        self.combounit.currentIndexChanged.connect(self.on_combobox_changed)

        self.label11 = QLabel(self)
        self.label11.setGeometry(325,42,50,18)
        self.label11.setText(self.dimensionname)

    def closeEvent(self,event):
        mdi.sectiondlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                if mat['name']==self.combmattype.currentText():    
                    self.mat=mat

    def on_click_ok(self,event):
        if self.text1.text()!="" and self.text2.text()!="" :
            self.text1.setStyleSheet("border: 1px solid black;")
            if mdi.sectiondlg.addsectionbool==False:
                if sum(y.get('name')==self.text1.text()  for y in self.sectiondict)==0 :
                    mdi.sectiondlg.selectedsection['d']=self.d
                    mdi.sectiondlg.selectedsection['name']=self.sectionname
                    mdi.sectiondlg.selectedsection['matindex']=self.mat['index']
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")
            else:
                if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                    Circularbar(self.sectionname,self.mat['index'],self.d)
                    self.close()
                else:
                    self.text1.setStyleSheet("border: 1px solid red;")

    def text1_changed(self,p):
        if self.text1.text()!="":
            self.text1.setStyleSheet("border: 1px solid black;")

            if sum(y.get('name')==self.text1.text() and y.get('deleted')==False  for y in Sections.sectiondict)==0:
                self.sectionname=self.text1.text()
            else:
                self.text1.setStyleSheet("border: 1px solid red;")
        else:
            self.text1.setStyleSheet("border: 1px solid red;")

    def text2_changed(self,p):
        if self.text2.text()!="":
            self.text2.setStyleSheet("border: 1px solid black;")

            self.d=float(Unit.dimension(self,float(self.text2.text()),1))
        else:
            self.text2.setStyleSheet("border: 1px solid red;")

    def on_combobox_changed(self,index):
        mdi.combounit.setCurrentIndex(index)
        Unit.index(self,index)
        self.dimensionname=Variables.units[Variables.unitindex].split('-')[1]

        self.label11.setText(self.dimensionname)

        self.text2.setText(str(format(round(float(Unit.dimension(self,self.d,0)),6),'.'+str(6)+'f')))

class SectionSelectionWindow(QDialog):

    def __init__(self,*args, **kwargs):
        super(SectionSelectionWindow, self).__init__(*args, **kwargs)      
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 295
        self.height = 225
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Select New Section Shape")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)        
        
        label10 = QLabel(self)
        label10.setGeometry(20,20,120,20)
        label10.setText("Material Type:")
         
        self.combmattype=QComboBox(self)
        self.combmattype.addItems(['Steel','Concrete'])            
        self.combmattype.setGeometry(150,22,120,18)
        self.combmattype.currentIndexChanged.connect(self.on_combmattype_changed)

        self.isection_button = QPushButton('I Section',self)
        self.isection_button.setGeometry(20,45,60,60)        
        self.isection_button.clicked.connect(self.on_click_section_Ishape)

        self.usection_button = QPushButton('U Section',self)
        self.usection_button.setGeometry(85,45,60,60)
        self.usection_button.clicked.connect(self.on_click_section_Ushape)

        self.lsection_button = QPushButton('L Section',self)
        self.lsection_button.setGeometry(150,45,60,60)
        self.lsection_button.clicked.connect(self.on_click_section_Lshape)

        self.dlsection_button = QPushButton('DL Section',self)
        self.dlsection_button.setGeometry(215,45,60,60)
        self.dlsection_button.clicked.connect(self.on_click_section_DLshape)

        self.recsection_button = QPushButton('Tube\nSection',self)
        self.recsection_button.setGeometry(20,110,60,60)
        self.recsection_button.clicked.connect(self.on_click_section_rectshape)

        self.cirsection_button = QPushButton('Pipe\nSection',self)
        self.cirsection_button.setGeometry(85,110,60,60)
        self.cirsection_button.clicked.connect(self.on_click_section_cirshape)

        self.recbarsection_button = QPushButton('Rectangle\nSection',self)
        self.recbarsection_button.setGeometry(150,110,60,60)
        self.recbarsection_button.clicked.connect(self.on_click_section_rectbarshape)

        self.cirbarlsection_button = QPushButton('Circular\nSection',self)
        self.cirbarlsection_button.setGeometry(215,110,60,60)
        self.cirbarlsection_button.clicked.connect(self.on_click_section_cirbarshape)
        
        okButton = QPushButton('OK',self)
        okButton.setGeometry(150,185,120,20)
        okButton.clicked.connect(self.on_click_ok)

    def closeEvent(self,event):
        mdi.sectiondlg.listboxfiller()
        self.close()
    
    def on_combmattype_changed(self,event):
        Variables.selectionmattype=self.combmattype.currentText()
        if Variables.selectionmattype=='Steel':
            self.isection_button.show()
            self.usection_button.show()
            self.lsection_button.show()
            self.dlsection_button.show()
            self.recsection_button.show()
            self.cirsection_button.show()
            self.recbarsection_button.setGeometry(150,110,60,60)
            self.cirbarlsection_button.setGeometry(215,110,60,60)

        elif Variables.selectionmattype=='Concrete':
            self.isection_button.hide()
            self.usection_button.hide()
            self.lsection_button.hide()
            self.dlsection_button.hide()
            self.recsection_button.hide()
            self.cirsection_button.hide()
            self.recbarsection_button.setGeometry(20,45,60,60)
            self.cirbarlsection_button.setGeometry(85,45,60,60)

    def on_click_ok(self,event):
        self.close()
    
    def on_click_section_Ishape(self,event):
        if sum(y.get('type')=='Steel' and y.get('deleted')==False  for y in Materials.materialdict)==0:
            mdi.statusBar().showMessage('No avaible Steel material !, Firstly add a new Steel material !')
        else:
            mdi.sectiondlg.sectiontype='ishape'
            self.hide()
            sectionpropdlg = ISectionPropertyWindow(self)
            sectionpropdlg.exec_()
            self.close()
    
    def on_click_section_Ushape(self,event):
        if sum(y.get('type')=='Steel' and y.get('deleted')==False  for y in Materials.materialdict)==0:
            mdi.statusBar().showMessage('No avaible Steel material !, Firstly add a new Steel material !')
        else:
            mdi.sectiondlg.sectiontype='ushape'
            self.hide()
            sectionpropdlg = USectionPropertyWindow(self)
            sectionpropdlg.exec_()
            self.close()
    
    def on_click_section_Lshape(self,event):
        if sum(y.get('type')=='Steel' and y.get('deleted')==False  for y in Materials.materialdict)==0:
            mdi.statusBar().showMessage('No avaible Steel material !, Firstly add a new Steel material !')
        else:
            mdi.sectiondlg.sectiontype='lshape'
            self.hide()
            sectionpropdlg = LSectionPropertyWindow(self)
            sectionpropdlg.exec_()
            self.close()
    
    def on_click_section_DLshape(self,event):
        if sum(y.get('type')=='Steel' and y.get('deleted')==False  for y in Materials.materialdict)==0:
            mdi.statusBar().showMessage('No avaible Steel material !, Firstly add a new Steel material !')
        else:
            mdi.sectiondlg.sectiontype='dlshape'
            self.hide()
            sectionpropdlg = DLSectionPropertyWindow(self)
            sectionpropdlg.exec_()
            self.close()
    
    def on_click_section_rectshape(self,event):
        if sum(y.get('type')=='Steel' and y.get('deleted')==False  for y in Materials.materialdict)==0:
            mdi.statusBar().showMessage('No avaible Steel material !, Firstly add a new Steel material !')
        else:
            mdi.sectiondlg.sectiontype='rectangular'
            self.hide()
            sectionpropdlg = RecSectionPropertyWindow(self)
            sectionpropdlg.exec_()
            self.close()

    def on_click_section_cirshape(self,event):
        if sum(y.get('type')=='Steel' and y.get('deleted')==False  for y in Materials.materialdict)==0:
            mdi.statusBar().showMessage('No avaible Steel material !, Firstly add a new Steel material !')
        else:
            mdi.sectiondlg.sectiontype='circular'
            self.hide()
            sectionpropdlg = CirSectionPropertyWindow(self)
            sectionpropdlg.exec_()
            self.close()

    def on_click_section_rectbarshape(self,event):
        
        if sum(y.get('type')==Variables.selectionmattype and y.get('deleted')==False  for y in Materials.materialdict)==0:
            mdi.statusBar().showMessage('No avaible '+Variables.selectionmattype+' material !, Firstly add a new '+Variables.selectionmattype+' material !')
        else:
            mdi.sectiondlg.sectiontype='rectangularbar'
            self.hide()
            sectionpropdlg = RecBarSectionPropertyWindow(self)
            sectionpropdlg.exec_() 
            self.close()

    def on_click_section_cirbarshape(self,event):
        if sum(y.get('type')==Variables.selectionmattype and y.get('deleted')==False  for y in Materials.materialdict)==0:
            mdi.statusBar().showMessage('No avaible '+Variables.selectionmattype+' material !, Firstly add a new '+Variables.selectionmattype+' material !')
        else:
            mdi.sectiondlg.sectiontype='circularbar'
            self.hide()
            sectionpropdlg = CirBarSectionPropertyWindow(self)
            sectionpropdlg.exec_()
            self.close()

class SectionWindow(QDialog):
    selectedsection=None
    addsectionbool=False
    sectiontype=None
    mattype='Steel'
    def __init__(self, *args, **kwargs):
        super(SectionWindow, self).__init__(*args, **kwargs)       
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 210
        self.height = 210
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Sections")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
       
        self.listbox=QListWidget(self)
        self.listbox.setGeometry(20,20,170,135)
        self.listbox.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listbox.itemDoubleClicked.connect(self.on_click_list)
        self.listboxfiller()

        okButton = QPushButton('OK',self)
        okButton.setGeometry(140,175,50,20)
        okButton.clicked.connect(self.on_click_ok)

        okButton = QPushButton('DELETE',self)
        okButton.setGeometry(80,175,50,20)
        okButton.clicked.connect(self.on_click_delete)

        okButton = QPushButton('ADD',self)
        okButton.setGeometry(20,175,50,20)
        okButton.clicked.connect(self.on_click_add)

    def listboxfiller(self):
        self.listbox.clear()
        
        for section in Sections.sectiondict:            
            if section['deleted']==False:
                self.listbox.addItem(section['name'])
        try:            
            mdi.framesectiondlg.listboxfiller()
        except:
            print('assign frame section not opened')

    def on_click_ok(self,event):
        self.close()

    def on_click_add(self,event):
        self.addsectionbool=True
        matdict=[]
        for mat in Materials.materialdict:
            if mat['deleted']==False:
                matdict.append(mat)
        if matdict!=[]:
            Variables.selectionmattype="Steel"
            self.sectionadddlg = SectionSelectionWindow(self)
            self.sectionadddlg.exec_()
        else:
            mdi.statusBar().showMessage('No avaible material !, Firstly add a new material !')

    def on_click_delete(self,event):
        for item in self.listbox.selectedItems():
            for section in Sections.sectiondict:
                if section['name']==item.text():
                    section['deleted']=True
        self.listboxfiller()

    def on_click_list(self,p):
        for section in Sections.sectiondict:
            if section['name']==p.text():
                self.selectedsection=section
                self.addsectionbool=False
                self.sectiontype=section['type']
                if self.sectiontype=='ishape':
                    sectionpropdlg = ISectionPropertyWindow(self)
                    sectionpropdlg.exec_()
                elif self.sectiontype=='ushape':
                    sectionpropdlg = USectionPropertyWindow(self)
                    sectionpropdlg.exec_()
                elif self.sectiontype=='dlshape':
                    sectionpropdlg = DLSectionPropertyWindow(self)
                    sectionpropdlg.exec_()
                elif self.sectiontype=='lshape':
                    sectionpropdlg = LSectionPropertyWindow(self)
                    sectionpropdlg.exec_()
                elif self.sectiontype=='rectangular':
                    sectionpropdlg = RecSectionPropertyWindow(self)
                    sectionpropdlg.exec_()
                elif self.sectiontype=='circular':
                    sectionpropdlg = CirSectionPropertyWindow(self)
                    sectionpropdlg.exec_()
                elif self.sectiontype=='rectangularbar':
                    sectionpropdlg = RecBarSectionPropertyWindow(self)
                    sectionpropdlg.exec_()
                elif self.sectiontype=='circularbar':
                    sectionpropdlg = CirBarSectionPropertyWindow(self)
                    sectionpropdlg.exec_()
                break

class FrameSectionWindow(QDialog):
    selectedsection=None
    addsectionbool=False
    sectiontype=None
    def __init__(self, *args, **kwargs):
        super(FrameSectionWindow, self).__init__(*args, **kwargs)       
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 210
        self.height = 210
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Assign Frame Section")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
       
        self.listbox=QListWidget(self)
        self.listbox.setGeometry(20,20,170,135)
        self.listbox.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listboxfiller()

        okButton = QPushButton('CANCEL',self)
        okButton.setGeometry(140,175,50,20)
        okButton.clicked.connect(self.on_click_cancel)

        okButton = QPushButton('OK',self)
        okButton.setGeometry(80,175,50,20)
        okButton.clicked.connect(self.on_click_ok)

        okButton = QPushButton('APPLY',self)
        okButton.setGeometry(20,175,50,20)
        okButton.clicked.connect(self.on_click_apply)

    def listboxfiller(self):
        self.listbox.clear()
        for section in Sections.sectiondict:            
            if section['deleted']==False:
                self.listbox.addItem(section['name'])

    def on_click_ok(self,event):
        if Variables.selectedFrames!=[]:
            for frame in Variables.selectedFrames:
                if frame['deleted']==False:
                    for item in self.listbox.selectedItems():
                        for section in Sections.sectiondict:
                            if section['name']==item.text():
                                frame['section']=section['index']
            OpenGLWidget.selectionClear()
            mdi.statusBar().showMessage('')
        self.close()

    def on_click_apply(self,event):
        if Variables.selectedFrames!=[]:
            for frame in Variables.selectedFrames:
                if frame['deleted']==False:
                    for item in self.listbox.selectedItems():
                        for section in Sections.sectiondict:
                            if section['name']==item.text():
                                frame['section']=section['index']
            OpenGLWidget.selectionClear()
            mdi.statusBar().showMessage('')
    
    def on_click_cancel(self,event):
        self.close()    

class DimensionsWindow(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(DimensionsWindow, self).__init__(*args, **kwargs)
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 350
        self.height = 270
        self.initUI()

    def initUI(self):
        
        self.setWindowTitle("Dimensions")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)

        label1 = QLabel(self)
        label1.setGeometry(20,20,200,20)
        label1.setText("Text height:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,200,20)
        label2.setText("Buble text thickness:")
        label3 = QLabel(self)
        label3.setGeometry(20,60,200,20)
        label3.setText("Frame thickness:")
        label4 = QLabel(self)
        label4.setGeometry(20,80,200,20)
        label4.setText("Node thickness:")
        label5 = QLabel(self)
        label5.setGeometry(20,100,200,20)
        label5.setText("Local axes scale:")
        label6 = QLabel(self)
        label6.setGeometry(20,120,200,20)
        label6.setText("Joint support scale:")
        label7 = QLabel(self)
        label7.setGeometry(20,145,200,20)
        label7.setText("Snap thickness:")
        label8 = QLabel(self)
        label8.setGeometry(20,165,200,20)
        label8.setText("Snap range:")
        label9 = QLabel(self)
        label9.setGeometry(20,185,200,20)
        label9.setText("Selected joint thickness:")
        label10 = QLabel(self)
        label10.setGeometry(20,205,200,20)
        label10.setText("Selection range:")
                
        self.text1 =QSpinBox(self)
        self.text1.setValue(Variables.textfont[1])
        self.text1.setRange(6, 32)
        self.text1.setGeometry(230,22,100,18)

        self.text2 =QSpinBox(self)
        self.text2.setValue(Variables.bubletextwidth)
        self.text2.setRange(1, 5)
        self.text2.setGeometry(230,42,100,18)

        self.text3 =QSpinBox(self)
        self.text3.setValue(Variables.framewidth)
        self.text3.setRange(1, 5)
        self.text3.setGeometry(230,62,100,18)

        self.text4 =QSpinBox(self)
        self.text4.setValue(Variables.pointwidth)
        self.text4.setRange(5, 30)
        self.text4.setGeometry(230,82,100,18)
        
        self.text5 = QDoubleSpinBox(self)
        self.text5.setGeometry(230,102,100,18)
        self.text5.setRange(1,100)
        self.text5.setValue(Variables.localaxescale)

        self.text6 = QDoubleSpinBox(self)
        self.text6.setGeometry(230,122,100,18)
        self.text6.setRange(1,100)
        self.text6.setValue(Variables.supportscale)

        self.text7 =QSpinBox(self)
        self.text7.setValue(Variables.pinsize)
        self.text7.setRange(1, 5)
        self.text7.setGeometry(230,147,100,18)

        self.text8 =QSpinBox(self)
        self.text8.setValue(Variables.pingrange)
        self.text8.setRange(1, 20)
        self.text8.setGeometry(230,167,100,18)

        self.text9 =QSpinBox(self)
        self.text9.setValue(Variables.selectedpointsize)
        self.text9.setRange(1, 5)
        self.text9.setGeometry(230,187,100,18)

        self.text10 =QSpinBox(self)
        self.text10.setValue(Variables.pickingrange)
        self.text10.setRange(1, 20)
        self.text10.setGeometry(230,207,100,18)
        
        button_apply=QPushButton(self)
        button_apply.setGeometry(260,240,70,22)
        button_apply.setText("DEFAULT")
        button_apply.clicked.connect(self.on_click_default)

        button_ok=QPushButton(self)
        button_ok.setGeometry(150,240,50,22)
        button_ok.setText("OK")
        button_ok.clicked.connect(self.on_click_ok)
        
        button_cancel=QPushButton(self)
        button_cancel.setGeometry(205,240,50,22)
        button_cancel.setText("CANCEL")
        button_cancel.clicked.connect(self.on_click_cancel)

    def on_click_cancel(self,event):
        self.close()

    def on_click_ok(self,event):
        Variables.textfont=(Variables.textfont[0],self.text1.value())
        Variables.bubletextwidth=self.text2.value()
        Variables.framewidth=self.text3.value()
        Variables.pointwidth=self.text4.value()
        Variables.localaxescale=self.text5.value()
        Variables.supportscale=self.text6.value()
        Variables.pinsize=self.text7.value()
        Variables.pingrange=self.text8.value()
        Variables.selectedpointsize=self.text9.value()
        Variables.pickingrange=self.text10.value()
        self.saveoptions()
        self.close()

    def on_click_default(self,event):
        self.text1.setValue(Variables.deftextfont[1])
        self.text2.setValue(Variables.defbubletextwidth)
        self.text3.setValue(Variables.defframewidth)
        self.text4.setValue(Variables.defpointwidth)
        self.text5.setValue(Variables.deflocalaxescale)
        self.text6.setValue(Variables.defsupportscale)
        self.text7.setValue(Variables.defpinsize)
        self.text8.setValue(Variables.defpingrange)
        self.text9.setValue(Variables.defselectedpointsize)
        self.text10.setValue(Variables.defpickingrange)
        
    def saveoptions(self):
        dir_path = dir_path = os.path.dirname(os.path.realpath(__file__))
        real_path =dir_path+"/options.ini"
        Saveoptionsdict={'textfont':Variables.textfont,'bubletextwidth':Variables.bubletextwidth,'localaxescale':Variables.localaxescale,
        'supportscale':Variables.supportscale,'framewidth':Variables.framewidth,'pointwidth':Variables.pointwidth,
        'pickingrange':Variables.pickingrange,'pingrange':Variables.pingrange,'pinsize':Variables.pinsize,'selectedpointsize':Variables.selectedpointsize,
        'blackorwhitetheme':Variables.blackorwhitetheme,'wframeColor':Variables.wframeColor,'wpointColor':Variables.wpointColor,
        'wselectedframecolor':Variables.wselectedframecolor,'wpreframecolor':Variables.wpreframecolor,'wselectrectanglecolor':Variables.wselectrectanglecolor,
        'wselectedpointcolor':Variables.wselectedpointcolor,'wpincolor':Variables.wpincolor,'wgridcolor':Variables.wgridcolor,'wsupportcolor':Variables.wsupportcolor,
        'wbubletextcolor':Variables.wbubletextcolor,'wtextcolor':Variables.wtextcolor,       
        'bframeColor':Variables.bframeColor,'bpointColor':Variables.bpointColor,
        'bselectedframecolor':Variables.bselectedframecolor,'bpreframecolor':Variables.bpreframecolor,'bselectrectanglecolor':Variables.bselectrectanglecolor,
        'bselectedpointcolor':Variables.bselectedpointcolor,'bpincolor':Variables.bpincolor,'bgridcolor':Variables.bgridcolor,'bsupportcolor':Variables.bsupportcolor,
        'bbubletextcolor':Variables.bbubletextcolor,'btextcolor':Variables.btextcolor
        }
        with open(real_path, 'w') as writer:
            writer.write(str(Saveoptionsdict))

class ThemesWindow(QDialog):
    
    def __init__(self, *args, **kwargs):
        super(ThemesWindow, self).__init__(*args, **kwargs)
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 350
        self.height = 310
        self.initUI()

    def initUI(self):
        
        self.setWindowTitle("Themes")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)

        label1 = QLabel(self)
        label1.setGeometry(20,20,200,20)
        label1.setText("Select Theme:")
        label2 = QLabel(self)
        label2.setGeometry(20,40,200,20)
        label2.setText("Frame Color:")
        label11 = QLabel(self)
        label11.setGeometry(20,60,200,20)
        label11.setText("Node color:")
        label3 = QLabel(self)
        label3.setGeometry(20,80,200,20)
        label3.setText("Text color:")
        label4 = QLabel(self)
        label4.setGeometry(20,100,200,20)
        label4.setText("Grid color:")
        label5 = QLabel(self)
        label5.setGeometry(20,120,200,20)
        label5.setText("Buble text color:")
        label6 = QLabel(self)
        label6.setGeometry(20,140,200,20)
        label6.setText("Preframe color:")
        label11 = QLabel(self)
        label11.setGeometry(20,160,200,20)
        label11.setText("Joint support color:")
        label7 = QLabel(self)
        label7.setGeometry(20,185,200,20)
        label7.setText("Selected frame color:")
        label8 = QLabel(self)
        label8.setGeometry(20,205,200,20)
        label8.setText("Selected joint color:")
        label9 = QLabel(self)
        label9.setGeometry(20,225,200,20)
        label9.setText("Selection rectangle color:")
        label10 = QLabel(self)
        label10.setGeometry(20,245,200,20)
        label10.setText("Snap color:")
        
                
        self.comb1 =QComboBox(self)
        self.comb1.addItems(("White Theme","Black Theme"))
        self.comb1.setCurrentIndex(Variables.blackorwhitetheme)
        self.comb1.setGeometry(230,22,100,18)
        self.comb1.currentIndexChanged.connect(self.on_combobox_changed)


        self.button1=QPushButton(self)
        self.button1.setGeometry(230,42,100,18)
        self.button1.setStyleSheet("background-color:rgb"+str(Variables.frameColor))
        self.button1.clicked.connect(self.button_click_trig_1)

        self.button2=QPushButton(self)
        self.button2.setGeometry(230,62,100,18)
        self.button2.setStyleSheet("background-color:rgb"+str(Variables.pointColor))
        self.button2.clicked.connect(self.button_click_trig_2)        

        self.button3=QPushButton(self)
        self.button3.setGeometry(230,82,100,18)
        self.button3.setStyleSheet("background-color:rgb"+str(Variables.textcolor))
        self.button3.clicked.connect(self.button_click_trig_3) 

        self.button4=QPushButton(self)
        self.button4.setGeometry(230,102,100,18)
        self.button4.setStyleSheet("background-color:rgb"+str(Variables.gridcolor))
        self.button4.clicked.connect(self.button_click_trig_4)

        self.button5=QPushButton(self)
        self.button5.setGeometry(230,122,100,18)
        self.button5.setStyleSheet("background-color:rgb"+str(Variables.bubletextcolor))
        self.button5.clicked.connect(self.button_click_trig_5)

        self.button6=QPushButton(self)
        self.button6.setGeometry(230,142,100,18)
        self.button6.setStyleSheet("background-color:rgb"+str(Variables.preframecolor))
        self.button6.clicked.connect(self.button_click_trig_6)

        self.button11=QPushButton(self)
        self.button11.setGeometry(230,162,100,18)
        self.button11.setStyleSheet("background-color:rgb"+str(Variables.supportcolor))
        self.button11.clicked.connect(self.button_click_trig_11)

        self.button7=QPushButton(self)
        self.button7.setGeometry(230,187,100,18)
        self.button7.setStyleSheet("background-color:rgb"+str(Variables.selectedframecolor))
        self.button7.clicked.connect(self.button_click_trig_7)

        self.button8=QPushButton(self)
        self.button8.setGeometry(230,207,100,18)
        self.button8.setStyleSheet("background-color:rgb"+str(Variables.selectedpointcolor))
        self.button8.clicked.connect(self.button_click_trig_8)

        self.button9=QPushButton(self)
        self.button9.setGeometry(230,227,100,18)
        self.button9.setStyleSheet("background-color:rgb"+str(Variables.selectrectanglecolor))
        self.button9.clicked.connect(self.button_click_trig_9)

        self.button10=QPushButton(self)
        self.button10.setGeometry(230,247,100,18)
        self.button10.setStyleSheet("background-color:rgb"+str(Variables.pincolor))
        self.button10.clicked.connect(self.button_click_trig_10)

        
        
        button_apply=QPushButton(self)
        button_apply.setGeometry(260,280,70,22)
        button_apply.setText("DEFAULT")
        button_apply.clicked.connect(self.on_click_default)

        button_ok=QPushButton(self)
        button_ok.setGeometry(150,280,50,22)
        button_ok.setText("OK")
        button_ok.clicked.connect(self.on_click_ok)
        
        button_cancel=QPushButton(self)
        button_cancel.setGeometry(205,280,50,22)
        button_cancel.setText("CANCEL")
        button_cancel.clicked.connect(self.on_click_cancel)

    def on_combobox_changed(self, value):
        Variables.blackorwhitetheme=value
        if Variables.blackorwhitetheme==0: #white
            self.button1.setStyleSheet("background-color:rgb"+str(Variables.wframeColor))
            self.button2.setStyleSheet("background-color:rgb"+str(Variables.wpointColor))
            self.button3.setStyleSheet("background-color:rgb"+str(Variables.wtextcolor))
            self.button4.setStyleSheet("background-color:rgb"+str(Variables.wgridcolor))
            self.button5.setStyleSheet("background-color:rgb"+str(Variables.wbubletextcolor))
            self.button6.setStyleSheet("background-color:rgb"+str(Variables.wpreframecolor))
            self.button7.setStyleSheet("background-color:rgb"+str(Variables.wselectedframecolor))
            self.button8.setStyleSheet("background-color:rgb"+str(Variables.wselectedpointcolor))
            self.button9.setStyleSheet("background-color:rgb"+str(Variables.wselectrectanglecolor))
            self.button10.setStyleSheet("background-color:rgb"+str(Variables.wpincolor))
            self.button11.setStyleSheet("background-color:rgb"+str(Variables.wsupportcolor))
        else:
            self.button1.setStyleSheet("background-color:rgb"+str(Variables.bframeColor))
            self.button2.setStyleSheet("background-color:rgb"+str(Variables.bpointColor))
            self.button3.setStyleSheet("background-color:rgb"+str(Variables.btextcolor))
            self.button4.setStyleSheet("background-color:rgb"+str(Variables.bgridcolor))
            self.button5.setStyleSheet("background-color:rgb"+str(Variables.bbubletextcolor))
            self.button6.setStyleSheet("background-color:rgb"+str(Variables.bpreframecolor))
            self.button7.setStyleSheet("background-color:rgb"+str(Variables.bselectedframecolor))
            self.button8.setStyleSheet("background-color:rgb"+str(Variables.bselectedpointcolor))
            self.button9.setStyleSheet("background-color:rgb"+str(Variables.bselectrectanglecolor))
            self.button10.setStyleSheet("background-color:rgb"+str(Variables.bpincolor))
            self.button11.setStyleSheet("background-color:rgb"+str(Variables.bsupportcolor))

    def on_click_cancel(self,event):
        self.close()

    def on_click_ok(self,event):
        if Variables.blackorwhitetheme==0: #white
            Variables.clearcolorfloat=(1,1,1,0)
            Variables.frameColor=Variables.wframeColor
            Variables.pointColor=Variables.wpointColor
            Variables.textcolor=Variables.wtextcolor
            Variables.gridcolor=Variables.wgridcolor
            Variables.bubletextcolor=Variables.wbubletextcolor
            Variables.preframecolor=Variables.wpreframecolor
            Variables.selectedframecolor=Variables.wselectedframecolor
            Variables.selectedpointcolor=Variables.wselectedpointcolor
            Variables.selectrectanglecolor=Variables.wselectrectanglecolor
            Variables.pincolor=Variables.wpincolor
            Variables.supportcolor=Variables.wsupportcolor

        else:
            Variables.clearcolorfloat=(0,0,0,0)
            Variables.frameColor=Variables.bframeColor
            Variables.pointColor=Variables.bpointColor
            Variables.textcolor=Variables.btextcolor
            Variables.gridcolor=Variables.bgridcolor
            Variables.bubletextcolor=Variables.bbubletextcolor
            Variables.preframecolor=Variables.bpreframecolor
            Variables.selectedframecolor=Variables.bselectedframecolor
            Variables.selectedpointcolor=Variables.bselectedpointcolor
            Variables.selectrectanglecolor=Variables.bselectrectanglecolor
            Variables.pincolor=Variables.bpincolor
            Variables.supportcolor=Variables.bsupportcolor

        self.saveoptions()
        self.close()

    def on_click_default(self,event):
        if Variables.blackorwhitetheme==0: #white            
            self.button1.setStyleSheet("background-color:rgb"+str(Variables.defWframeColor))
            self.button2.setStyleSheet("background-color:rgb"+str(Variables.defWpointColor))
            self.button3.setStyleSheet("background-color:rgb"+str(Variables.defWtextcolor))
            self.button4.setStyleSheet("background-color:rgb"+str(Variables.defWgridcolor))
            self.button5.setStyleSheet("background-color:rgb"+str(Variables.defWbubletextcolor))
            self.button6.setStyleSheet("background-color:rgb"+str(Variables.defWpreframecolor))
            self.button7.setStyleSheet("background-color:rgb"+str(Variables.defWselectedframecolor))
            self.button8.setStyleSheet("background-color:rgb"+str(Variables.defWselectedpointcolor))
            self.button9.setStyleSheet("background-color:rgb"+str(Variables.defWselectrectanglecolor))
            self.button10.setStyleSheet("background-color:rgb"+str(Variables.defWpincolor))
            self.button11.setStyleSheet("background-color:rgb"+str(Variables.defWsupportcolor))
        else:
            self.button1.setStyleSheet("background-color:rgb"+str(Variables.defBframeColor))
            self.button2.setStyleSheet("background-color:rgb"+str(Variables.defBpointColor))
            self.button3.setStyleSheet("background-color:rgb"+str(Variables.defBtextcolor))
            self.button4.setStyleSheet("background-color:rgb"+str(Variables.defBgridcolor))
            self.button5.setStyleSheet("background-color:rgb"+str(Variables.defBbubletextcolor))
            self.button6.setStyleSheet("background-color:rgb"+str(Variables.defBpreframecolor))
            self.button7.setStyleSheet("background-color:rgb"+str(Variables.defBselectedframecolor))
            self.button8.setStyleSheet("background-color:rgb"+str(Variables.defBselectedpointcolor))
            self.button9.setStyleSheet("background-color:rgb"+str(Variables.defBselectrectanglecolor))
            self.button10.setStyleSheet("background-color:rgb"+str(Variables.defBpincolor))
            self.button11.setStyleSheet("background-color:rgb"+str(Variables.defBsupportcolor))
        if Variables.blackorwhitetheme==0: #white            
            Variables.wframeColor=Variables.defWframeColor
            Variables.wpointColor=Variables.defWpointColor
            Variables.wtextcolor=Variables.defWtextcolor
            Variables.wgridcolor=Variables.defWgridcolor
            Variables.wbubletextcolor=Variables.defWbubletextcolor
            Variables.wpreframecolor=Variables.defWpreframecolor
            Variables.wselectedframecolor=Variables.defWselectedframecolor
            Variables.wselectedpointcolor=Variables.defWselectedpointcolor
            Variables.wselectrectanglecolor=Variables.defWselectrectanglecolor
            Variables.wpincolor=Variables.defWpincolor
            Variables.wsupportcolor=Variables.defWsupportcolor
        else:            
            Variables.bframeColor=Variables.defBframeColor
            Variables.bpointColor=Variables.defBpointColor
            Variables.btextcolor=Variables.defBtextcolor
            Variables.bgridcolor=Variables.defBgridcolor
            Variables.bbubletextcolor=Variables.defBbubletextcolor
            Variables.bpreframecolor=Variables.defBpreframecolor
            Variables.bselectedframecolor=Variables.defBselectedframecolor
            Variables.bselectedpointcolor=Variables.defBselectedpointcolor
            Variables.bselectrectanglecolor=Variables.defBselectrectanglecolor
            Variables.bpincolor=Variables.defBpincolor
            Variables.bsupportcolor=Variables.defBsupportcolor

    def button_click_trig_1(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)            
            getcolor=color.getColor(QColor(Variables.wframeColor[0], Variables.wframeColor[1], Variables.wframeColor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button1.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wframeColor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bframeColor[0], Variables.bframeColor[1], Variables.bframeColor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button1.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bframeColor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))

    def button_click_trig_2(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wpointColor[0], Variables.wpointColor[1], Variables.wpointColor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button2.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wpointColor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bpointColor[0], Variables.bpointColor[1], Variables.bpointColor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button2.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bpointColor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))
    
    def button_click_trig_3(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wtextcolor[0], Variables.wtextcolor[1], Variables.wtextcolor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button3.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wtextcolor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.btextcolor[0], Variables.btextcolor[1], Variables.btextcolor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button3.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.btextcolor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))

    def button_click_trig_4(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wgridcolor[0], Variables.wgridcolor[1], Variables.wgridcolor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button4.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wgridcolor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bgridcolor[0], Variables.bgridcolor[1], Variables.bgridcolor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button4.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bgridcolor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))

    def button_click_trig_5(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wbubletextcolor[0], Variables.wbubletextcolor[1], Variables.wbubletextcolor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button5.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wbubletextcolor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bbubletextcolor[0], Variables.bbubletextcolor[1], Variables.bbubletextcolor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button5.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bbubletextcolor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))

    def button_click_trig_6(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wpreframecolor[0], Variables.wpreframecolor[1], Variables.wpreframecolor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button6.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wpreframecolor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bpreframecolor[0], Variables.bpreframecolor[1], Variables.bpreframecolor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button6.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bpreframecolor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))
    
    def button_click_trig_7(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wselectedframecolor[0], Variables.wselectedframecolor[1], Variables.wselectedframecolor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button7.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wselectedframecolor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bselectedframecolor[0], Variables.bselectedframecolor[1], Variables.bselectedframecolor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button7.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bselectedframecolor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))
    
    def button_click_trig_8(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wselectedpointcolor[0], Variables.wselectedpointcolor[1], Variables.wselectedpointcolor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button8.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wselectedpointcolor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bselectedpointcolor[0], Variables.bselectedpointcolor[1], Variables.bselectedpointcolor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button8.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bselectedpointcolor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))
    
    def button_click_trig_9(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wselectrectanglecolor[0], Variables.wselectrectanglecolor[1], Variables.wselectrectanglecolor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button9.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wselectrectanglecolor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bselectrectanglecolor[0], Variables.bselectrectanglecolor[1], Variables.bselectrectanglecolor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button9.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bselectrectanglecolor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))
    
    def button_click_trig_10(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wpincolor[0], Variables.wpincolor[1], Variables.wpincolor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button10.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wpincolor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bpincolor[0], Variables.bpincolor[1], Variables.bpincolor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button10.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bpincolor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))

    def button_click_trig_11(self):
        if Variables.blackorwhitetheme==0: #white
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.wsupportcolor[0], Variables.wsupportcolor[1], Variables.wsupportcolor[2]))            
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button11.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2])))
                Variables.wsupportcolor=(color1[0],color1[1],color1[2])
        else:
            color = QColorDialog(self)
            getcolor=color.getColor(QColor(Variables.bsupportcolor[0], Variables.bsupportcolor[1], Variables.bsupportcolor[2]))
            if getcolor.isValid():
                color1=getcolor.getRgb()
                self.button11.setStyleSheet("background-color:rgb"+str((color1[0],color1[1],color1[2]))) 
                Variables.bsupportcolor=(color1[0],color1[1],color1[2])
                print((color1[0],color1[1],color1[2]))


    def saveoptions(self):
        dir_path = dir_path = os.path.dirname(os.path.realpath(__file__))
        real_path =dir_path+"/options.ini"
        Saveoptionsdict={'textfont':Variables.textfont,'bubletextwidth':Variables.bubletextwidth,'localaxescale':Variables.localaxescale,
        'supportscale':Variables.supportscale,'framewidth':Variables.framewidth,'pointwidth':Variables.pointwidth,
        'pickingrange':Variables.pickingrange,'pingrange':Variables.pingrange,'pinsize':Variables.pinsize,'selectedpointsize':Variables.selectedpointsize,
        'blackorwhitetheme':Variables.blackorwhitetheme,'wframeColor':Variables.wframeColor,'wpointColor':Variables.wpointColor,
        'wselectedframecolor':Variables.wselectedframecolor,'wpreframecolor':Variables.wpreframecolor,'wselectrectanglecolor':Variables.wselectrectanglecolor,
        'wselectedpointcolor':Variables.wselectedpointcolor,'wpincolor':Variables.wpincolor,'wgridcolor':Variables.wgridcolor,'wsupportcolor':Variables.wsupportcolor,
        'wbubletextcolor':Variables.wbubletextcolor,'wtextcolor':Variables.wtextcolor,       
        'bframeColor':Variables.bframeColor,'bpointColor':Variables.bpointColor,
        'bselectedframecolor':Variables.bselectedframecolor,'bpreframecolor':Variables.bpreframecolor,'bselectrectanglecolor':Variables.bselectrectanglecolor,
        'bselectedpointcolor':Variables.bselectedpointcolor,'bpincolor':Variables.bpincolor,'bgridcolor':Variables.bgridcolor,'bsupportcolor':Variables.bsupportcolor,
        'bbubletextcolor':Variables.bbubletextcolor,'btextcolor':Variables.btextcolor
        }
        with open(real_path, 'w') as writer:
            writer.write(str(Saveoptionsdict))

class GridWin(QDialog):

    text1="Ordinate"

    def __init__(self, *args, **kwargs):
        super(GridWin, self).__init__(*args, **kwargs)

        self.title = 'Edit Grid'
        self.left = int(mdi.width()/2)
        self.top = int(mdi.height()/2)
        self.width = 530
        self.height = 570
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setFixedSize(self.width,self.height)
        
        label1 = QLabel(self)
        label1.setGeometry(20,20,100,20)
        label1.setText("X axes:")
        label2 = QLabel(self)
        label2.setGeometry(20,200,100,20)
        label2.setText("Y axes:")
        label3 = QLabel(self)
        label3.setGeometry(20,380,100,20)
        label3.setText("Z axes:")
        button_add_1=QPushButton(self)
        button_add_1.setGeometry(280,60,50,22)
        button_add_1.setText("ADD")
        button_add_1.clicked.connect(self.on_click_add_1)
        button_delete_1=QPushButton(self)
        button_delete_1.setGeometry(280,85,50,22)
        button_delete_1.setText("DELETE")
        button_delete_1.clicked.connect(self.on_click_delete_1)

        button_add_2=QPushButton(self)
        button_add_2.setGeometry(280,240,50,22)
        button_add_2.setText("ADD")
        button_add_2.clicked.connect(self.on_click_add_2)
        button_delete_2=QPushButton(self)
        button_delete_2.setGeometry(280,265,50,22)
        button_delete_2.setText("DELETE")
        button_delete_2.clicked.connect(self.on_click_delete_2)

        button_add_3=QPushButton(self)
        button_add_3.setGeometry(280,420,50,22)
        button_add_3.setText("ADD")
        button_add_3.clicked.connect(self.on_click_add_3)
        button_delete_3=QPushButton(self)
        button_delete_3.setGeometry(280,445,50,22)
        button_delete_3.setText("DELETE")
        button_delete_3.clicked.connect(self.on_click_delete_3)

        button_ok=QPushButton(self)
        button_ok.setGeometry(400,540,50,22)
        button_ok.setText("OK")
        button_ok.clicked.connect(self.on_click_ok)
        button_cancel=QPushButton(self)
        button_cancel.setGeometry(460,540,50,22)
        button_cancel.setText("CANCEL")
        button_cancel.clicked.connect(self.on_click_cancel)

        button_quick=QPushButton(self)
        button_quick.setGeometry(400,100,100,22)
        button_quick.setText("Quick Grid Create")
        button_quick.clicked.connect(self.Quick_Grid_button_Clicked)

        radiobutton = QRadioButton(self)
        radiobutton.setGeometry(380,180,80,22)
        radiobutton.setChecked(True)
        radiobutton.setText("Ordinate")
        radiobutton1 = QRadioButton(self)
        radiobutton1.setGeometry(460,180,80,22)
        radiobutton1.setText("Space")
        radiobutton.toggled.connect(self.on_click_radio1)
        radiobutton1.toggled.connect(self.on_click_radio2)

        labelbublex = QLabel(self)
        labelbublex.setGeometry(70,20,80,20)
        labelbublex.setText("Buble Size:")
        self.textbublex =QSpinBox(self)
        self.textbublex.setValue(Variables.xbublesize)
        self.textbublex.setRange(5, 40)
        self.textbublex.setGeometry(125,22,40,18)
        
        labelbubley = QLabel(self)
        labelbubley.setGeometry(70,200,80,20)
        labelbubley.setText("Buble Size:")
        self.textbubley =QSpinBox(self)
        self.textbubley.setValue(Variables.ybublesize)
        self.textbubley.setRange(5, 40)
        self.textbubley.setGeometry(125,202,40,18)
        
        labelbublez = QLabel(self)
        labelbublez.setGeometry(70,380,80,20)
        labelbublez.setText("Buble Size:")
        self.textbublez =QSpinBox(self)
        self.textbublez.setValue(Variables.zbublesize)
        self.textbublez.setRange(5, 40)
        self.textbublez.setGeometry(125,382,40,18)
        
        labelbublex1 = QLabel(self)
        labelbublex1.setGeometry(170,20,80,20)
        labelbublex1.setText("Buble Loc:")
        self.xcombobox = QComboBox(self)
        self.xcombobox.addItems(("Start","End"))
        self.xcombobox.setGeometry(220,22,50,18)
        self.xcombobox.setCurrentText(Variables.xbubleLoc)

        labelbubley1 = QLabel(self)
        labelbubley1.setGeometry(170,200,80,20)
        labelbubley1.setText("Buble Loc:")
        self.ycombobox = QComboBox(self)
        self.ycombobox.addItems(("Start","End"))
        self.ycombobox.setGeometry(220,202,50,18)
        self.ycombobox.setCurrentText(Variables.ybubleLoc)
        
        labelbublez1 = QLabel(self)
        labelbublez1.setGeometry(170,380,80,20)
        labelbublez1.setText("Buble Loc:")
        self.zcombobox = QComboBox(self)
        self.zcombobox.addItems(("Start","End"))
        self.zcombobox.setGeometry(220,382,50,18)
        self.zcombobox.setCurrentText(Variables.zbubleLoc)

       # Create table
        self.tableWidgetx = QTableWidget(self)
        self.tableWidgetx.setGeometry(20,40,250,150)
        self.tableWidgetx.setRowCount(len(Variables.gridxTemp))        
        self.tableWidgetx.setColumnCount(2)
        self.tableWidgetx.setHorizontalHeaderLabels(("Name",self.text1))
        self.tableWidgetx.setItemDelegate(ValidatedItemDelegate())        
        self.tableWidgetx.verticalHeader().hide()
        self.tableWidgetx.itemChanged.connect(self.on_click_change_1)
        self.tableWidgetx.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetx.horizontalHeader().sectionPressed.disconnect()
        self.tableWidgetx.setSelectionMode(QAbstractItemView.SingleSelection)

        # Create table
        self.tableWidgety = QTableWidget(self)
        self.tableWidgety.setGeometry(20,220,250,150)
        self.tableWidgety.setRowCount(len(Variables.gridyTemp))
        self.tableWidgety.setColumnCount(2)
        self.tableWidgety.setHorizontalHeaderLabels(("Name",self.text1))
        self.tableWidgety.setItemDelegate(ValidatedItemDelegate())
        self.tableWidgety.verticalHeader().hide()
        self.tableWidgety.itemChanged.connect(self.on_click_change_2)
        self.tableWidgety.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgety.horizontalHeader().sectionPressed.disconnect()
        self.tableWidgetx.setSelectionMode(QAbstractItemView.SingleSelection)

        # Create table
        self.tableWidgetz = QTableWidget(self)
        self.tableWidgetz.setGeometry(20,400,250,150)
        self.tableWidgetz.setRowCount(len(Variables.gridzTemp))
        self.tableWidgetz.setColumnCount(2)
        self.tableWidgetz.setHorizontalHeaderLabels(("Name",self.text1))
        self.tableWidgetz.setItemDelegate(ValidatedItemDelegate())
        self.tableWidgetz.verticalHeader().hide()
        self.tableWidgetz.itemChanged.connect(self.on_click_change_3)
        self.tableWidgetz.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetz.horizontalHeader().sectionPressed.disconnect()
        self.tableWidgetx.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tablefillerfirst()
        self.tablefiller()
        # Show widget

    def tablefillerfirst(self):
        Variables.gridxTemp.clear()
        Variables.gridxTemp=Variables.gridx.copy()
        Variables.gridyTemp.clear()
        Variables.gridyTemp=Variables.gridy.copy()
        Variables.gridzTemp.clear()
        Variables.gridzTemp=Variables.gridz.copy()

    def tablefiller(self):
        if self.text1=='Ordinate':
            self.tableWidgetx.clear()
            self.tableWidgetx.setRowCount(len(Variables.gridxTemp))
            self.tableWidgetx.setHorizontalHeaderLabels(("Name",self.text1))
            for i in range(len(Variables.gridxTemp)):
                self.tableWidgetx.setItem(i,0,QTableWidgetItem(str(Variables.gridxTemp[i][0])))
                self.tableWidgetx.setItem(i,1,QTableWidgetItem(str(Unit.dimension(self,float(Variables.gridxTemp[i][1]),0))))
            self.tableWidgety.clear()
            self.tableWidgety.setRowCount(len(Variables.gridyTemp))
            self.tableWidgety.setHorizontalHeaderLabels(("Name",self.text1))
            for i in range(len(Variables.gridyTemp)):
                self.tableWidgety.setItem(i,0,QTableWidgetItem(str(Variables.gridyTemp[i][0])))
                self.tableWidgety.setItem(i,1,QTableWidgetItem(str(Unit.dimension(self,float(Variables.gridyTemp[i][1]),0))))
            self.tableWidgetz.clear()
            self.tableWidgetz.setRowCount(len(Variables.gridzTemp))
            self.tableWidgetz.setHorizontalHeaderLabels(("Name",self.text1))
            for i in range(len(Variables.gridzTemp)):
                self.tableWidgetz.setItem(i,0,QTableWidgetItem(str(Variables.gridzTemp[i][0])))
                self.tableWidgetz.setItem(i,1,QTableWidgetItem(str(Unit.dimension(self,float(Variables.gridzTemp[i][1]),0))))
        elif self.text1=='Space':
            self.tableWidgetx.clear()
            self.tableWidgetx.setRowCount(len(Variables.gridxTemp))
            self.tableWidgetx.setHorizontalHeaderLabels(("Name",self.text1))
            self.tableWidgetx.setItem(0,0,QTableWidgetItem(str(Variables.gridxTemp[0][0])))
            self.tableWidgetx.setItem(0,1,QTableWidgetItem(str(Unit.dimension(self,float(Variables.gridxTemp[0][1]),0))))
            for i in range(1,len(Variables.gridxTemp)):
                self.tableWidgetx.setItem(i,0,QTableWidgetItem(str(Variables.gridxTemp[i][0])))
                self.tableWidgetx.setItem(i,1,QTableWidgetItem(str(Unit.dimension(self,float(Variables.gridxTemp[i][1]-Variables.gridxTemp[i-1][1]),0))))

            self.tableWidgety.clear()
            self.tableWidgety.setRowCount(len(Variables.gridyTemp))
            self.tableWidgety.setHorizontalHeaderLabels(("Name",self.text1))
            self.tableWidgety.setItem(0,0,QTableWidgetItem(str(Variables.gridyTemp[0][0])))
            self.tableWidgety.setItem(0,1,QTableWidgetItem(str(Unit.dimension(self,float(Variables.gridyTemp[0][1]),0))))
            for i in range(1,len(Variables.gridyTemp)):
                self.tableWidgety.setItem(i,0,QTableWidgetItem(str(Variables.gridyTemp[i][0])))
                self.tableWidgety.setItem(i,1,QTableWidgetItem(str(Unit.dimension(self,float(Variables.gridyTemp[i][1]-Variables.gridyTemp[i-1][1]),0))))

            self.tableWidgetz.clear()
            self.tableWidgetz.setRowCount(len(Variables.gridzTemp))
            self.tableWidgetz.setHorizontalHeaderLabels(("Name",self.text1))
            self.tableWidgetz.setItem(0,0,QTableWidgetItem(str(Variables.gridzTemp[0][0])))
            self.tableWidgetz.setItem(0,1,QTableWidgetItem(str(Unit.dimension(self,float(Variables.gridzTemp[0][1]),0))))
            for i in range(1,len(Variables.gridzTemp)):
                self.tableWidgetz.setItem(i,0,QTableWidgetItem(str(Variables.gridzTemp[i][0])))
                self.tableWidgetz.setItem(i,1,QTableWidgetItem(str(Unit.dimension(self,float(Variables.gridzTemp[i][1]-Variables.gridzTemp[i-1][1]),0))))

    def on_click_radio1(self,p):
        if p==True:
            self.text1='Ordinate'
            self.tableWidgetx.setItemDelegate(ValidatedItemDelegate())
            self.tableWidgety.setItemDelegate(ValidatedItemDelegate())
            self.tableWidgetz.setItemDelegate(ValidatedItemDelegate())
            self.tablefiller()
    
    def on_click_radio2(self,p):
        if p==True:
            self.text1='Space'
            self.tableWidgetx.setItemDelegate(ValidatedItemDelegatePos())
            self.tableWidgety.setItemDelegate(ValidatedItemDelegatePos())
            self.tableWidgetz.setItemDelegate(ValidatedItemDelegatePos())
            self.tablefiller()

    def takeSecond(self,elem):
        return elem[1]
    
    def on_click_change_1(self):
        item=self.tableWidgetx.currentItem()        
        if item != None:            
            if self.text1=='Ordinate':
                takenItem=Variables.gridxTemp[self.tableWidgetx.currentRow()]
                Variables.gridxTemp.remove(takenItem)
                if self.tableWidgetx.currentColumn()==0:
                    Variables.gridxTemp.insert(self.tableWidgetx.currentRow(),(item.text(),takenItem[1]))
                else:
                    Variables.gridxTemp.insert(self.tableWidgetx.currentRow(),(takenItem[0],Unit.dimension(self,float(item.text()),1)))
                Variables.gridxTemp.sort(key=self.takeSecond)
            elif self.text1=='Space':                
                index=self.tableWidgetx.currentRow()-1
                value1=Variables.gridxTemp[self.tableWidgetx.currentRow()-1][1]
                if index<0:
                    value1=0
                maxindex=len(Variables.gridxTemp)
                value2=Variables.gridxTemp[self.tableWidgetx.currentRow()][1]
                space =float(value2)-float(value1)
                newspace= Unit.dimension(self,float(item.text()),1)
                diff =float(newspace)-float(space)                
                if self.tableWidgetx.currentColumn()==0:
                    takenItem=Variables.gridxTemp[self.tableWidgetx.currentRow()]
                    Variables.gridxTemp.remove(takenItem)
                    Variables.gridxTemp.insert(self.tableWidgetx.currentRow(),(item.text(),takenItem[1]))
                else:
                    for i in range(index+1,maxindex):
                        takenItem=Variables.gridxTemp[i]
                        Variables.gridxTemp.remove(takenItem)
                        Variables.gridxTemp.insert(i,(takenItem[0],takenItem[1]+diff))
                    Variables.gridxTemp.sort(key=self.takeSecond)
            self.tablefiller()
    
    def on_click_change_2(self):
        item=self.tableWidgety.currentItem()
        if item != None:
            if self.text1=='Ordinate':
                takenItem=Variables.gridyTemp[self.tableWidgety.currentRow()]
                Variables.gridyTemp.remove(takenItem)
                if self.tableWidgety.currentColumn()==0:
                    Variables.gridyTemp.insert(self.tableWidgety.currentRow(),(item.text(),takenItem[1]))
                else:
                    Variables.gridyTemp.insert(self.tableWidgety.currentRow(),(takenItem[0],Unit.dimension(self,float(item.text()),1)))
                Variables.gridyTemp.sort(key=self.takeSecond)
            elif self.text1=='Space':                
                index=self.tableWidgety.currentRow()-1
                value1=Variables.gridyTemp[self.tableWidgety.currentRow()-1][1]
                if index<0:
                    value1=0
                maxindex=len(Variables.gridyTemp)
                value2=Variables.gridyTemp[self.tableWidgety.currentRow()][1]
                space =float(value2)-float(value1)
                newspace= Unit.dimension(self,float(item.text()),1)
                diff =float(newspace)-float(space)                
                if self.tableWidgety.currentColumn()==0:
                    takenItem=Variables.gridyTemp[self.tableWidgety.currentRow()]
                    Variables.gridyTemp.remove(takenItem)
                    Variables.gridyTemp.insert(self.tableWidgety.currentRow(),(item.text(),takenItem[1]))
                else:
                    for i in range(index+1,maxindex):
                        takenItem=Variables.gridyTemp[i]
                        Variables.gridyTemp.remove(takenItem)
                        Variables.gridyTemp.insert(i,(takenItem[0],takenItem[1]+diff))
                    Variables.gridyTemp.sort(key=self.takeSecond)
            self.tablefiller()
    
    def on_click_change_3(self):
        item=self.tableWidgetz.currentItem()
        if item != None:
            if self.text1=='Ordinate':
                takenItem=Variables.gridzTemp[self.tableWidgetz.currentRow()]
                Variables.gridzTemp.remove(takenItem)
                if self.tableWidgetz.currentColumn()==0:
                    Variables.gridzTemp.insert(self.tableWidgetz.currentRow(),(item.text(),takenItem[1]))
                else:
                    Variables.gridzTemp.insert(self.tableWidgetz.currentRow(),(takenItem[0],Unit.dimension(self,float(item.text()),1)))
                Variables.gridzTemp.sort(key=self.takeSecond)
            elif self.text1=='Space':                
                index=self.tableWidgetz.currentRow()-1
                value1=Variables.gridzTemp[self.tableWidgetz.currentRow()-1][1]
                if index<0:
                    value1=0
                maxindex=len(Variables.gridzTemp)
                value2=Variables.gridzTemp[self.tableWidgetz.currentRow()][1]
                space =float(value2)-float(value1)
                newspace= Unit.dimension(self,float(item.text()),1)
                diff =float(newspace)-float(space)                
                if self.tableWidgetz.currentColumn()==0:
                    takenItem=Variables.gridzTemp[self.tableWidgetz.currentRow()]
                    Variables.gridzTemp.remove(takenItem)
                    Variables.gridzTemp.insert(self.tableWidgetz.currentRow(),(item.text(),takenItem[1]))
                else:
                    for i in range(index+1,maxindex):
                        takenItem=Variables.gridzTemp[i]
                        Variables.gridzTemp.remove(takenItem)
                        Variables.gridzTemp.insert(i,(takenItem[0],takenItem[1]+diff))
                    Variables.gridzTemp.sort(key=self.takeSecond)
            self.tablefiller()

    def Quick_Grid_button_Clicked(self):
        quicgriddlg = QuickGridWindow(self)
        quicgriddlg.exec_()
    
    def on_click_ok(self):
        Variables.gridx.clear()
        Variables.gridy.clear()
        Variables.gridz.clear()
        for grid in Variables.gridxTemp:
            Variables.gridx.append(grid)
        for grid in Variables.gridyTemp:
            Variables.gridy.append(grid)
        for grid in Variables.gridzTemp:
            Variables.gridz.append(grid)
        if self.textbublex.text()!="":
            if int(self.textbublex.text())>0 :
                Variables.xbublesize=int(self.textbublex.text())
        if self.textbubley.text()!="":
            if int(self.textbubley.text())>0 :
                Variables.ybublesize=int(self.textbubley.text())
        if self.textbublez.text()!="":
            if int(self.textbublez.text())>0 :
                Variables.zbublesize=int(self.textbublez.text())
        Variables.xbubleLoc= self.xcombobox.currentText()
        Variables.ybubleLoc= self.ycombobox.currentText()
        Variables.zbubleLoc= self.zcombobox.currentText()
        
        self.close()
    
    def on_click_cancel(self):
        self.close()
    
    def on_click_delete_1(self):
        if self.tableWidgetx.rowCount()>1 and self.tableWidgetx.currentRow() !=-1:
            if self.text1=='Ordinate':
                takenItem=Variables.gridxTemp[self.tableWidgetx.currentRow()]
                Variables.gridxTemp.remove(takenItem)
                self.tableWidgetx.removeRow(self.tableWidgetx.currentRow())
            elif self.text1=='Space':
                takenItem=Variables.gridxTemp[self.tableWidgetx.currentRow()]
                takenitem1=Unit.dimension(self,float(self.tableWidgetx.item(self.tableWidgetx.currentRow(),1).text()),1)
                currentrw=self.tableWidgetx.currentRow()
                Variables.gridxTemp.remove(takenItem)
                self.tableWidgetx.removeRow(self.tableWidgetx.currentRow())                
                for i in range(self.tableWidgetx.currentRow(),len(Variables.gridxTemp)):
                    item=Variables.gridxTemp[i]
                    if currentrw != len(Variables.gridxTemp):
                        Variables.gridxTemp.remove(Variables.gridxTemp[i])
                        Variables.gridxTemp.insert(i,(item[0],float(item[1])-takenitem1))
            Variables.gridxTemp.sort(key=self.takeSecond)
            self.tablefiller()
    
    def on_click_delete_2(self):
        if self.tableWidgety.rowCount()>1 and self.tableWidgety.currentRow() !=-1:
            if self.text1=='Ordinate':
                takenItem=Variables.gridyTemp[self.tableWidgety.currentRow()]
                Variables.gridyTemp.remove(takenItem)
                self.tableWidgety.removeRow(self.tableWidgety.currentRow())
            elif self.text1=='Space':
                takenItem=Variables.gridyTemp[self.tableWidgety.currentRow()]
                takenitem1=Unit.dimension(self,float(self.tableWidgety.item(self.tableWidgety.currentRow(),1).text()),1)
                currentrw=self.tableWidgety.currentRow()
                Variables.gridyTemp.remove(takenItem)
                self.tableWidgety.removeRow(self.tableWidgety.currentRow())                
                for i in range(self.tableWidgety.currentRow()+1,len(Variables.gridyTemp)):
                    item=Variables.gridyTemp[i]
                    if currentrw != len(Variables.gridyTemp):
                        Variables.gridyTemp.remove(Variables.gridyTemp[i])
                        Variables.gridyTemp.insert(i,(item[0],float(item[1])-takenitem1))
            Variables.gridyTemp.sort(key=self.takeSecond)
            self.tablefiller()
    
    def on_click_delete_3(self):
       if self.tableWidgetz.rowCount()>1 and self.tableWidgetz.currentRow() !=-1:
            if self.text1=='Ordinate':
                takenItem=Variables.gridzTemp[self.tableWidgetz.currentRow()]
                Variables.gridzTemp.remove(takenItem)
                self.tableWidgetz.removeRow(self.tableWidgetz.currentRow())
            elif self.text1=='Space':
                takenItem=Variables.gridzTemp[self.tableWidgetz.currentRow()]
                takenitem1=Unit.dimension(self,float(self.tableWidgetz.item(self.tableWidgetz.currentRow(),1).text()),1)
                currentrw=self.tableWidgetz.currentRow()
                Variables.gridzTemp.remove(takenItem)
                self.tableWidgetz.removeRow(self.tableWidgetz.currentRow())                
                for i in range(self.tableWidgetz.currentRow()+1,len(Variables.gridzTemp)):
                    item=Variables.gridzTemp[i]
                    if currentrw != len(Variables.gridzTemp):
                        Variables.gridzTemp.remove(Variables.gridzTemp[i])
                        Variables.gridzTemp.insert(i,(item[0],float(item[1])-takenitem1))                    
            Variables.gridzTemp.sort(key=self.takeSecond)
            self.tablefiller()
    
    def on_click_add_1(self):
        if self.text1=='Ordinate':
            if self.tableWidgety.rowCount()>1:
                item=float(self.tableWidgetx.item(self.tableWidgetx.rowCount()-1,1).text())+float(self.tableWidgetx.item(self.tableWidgetx.rowCount()-1,1).text())-float(self.tableWidgetx.item(self.tableWidgetx.rowCount()-2,1).text())        
                self.tableWidgetx.setRowCount(self.tableWidgetx.rowCount()+1)
                self.tableWidgetx.setItem((self.tableWidgetx.rowCount()-1),0,QTableWidgetItem( self.tableWidgetx.item(self.tableWidgetx.rowCount()-2,0)))
                self.tableWidgetx.setItem((self.tableWidgetx.rowCount()-1),1,QTableWidgetItem( str(item)))
                Variables.gridxTemp.append((str(self.tableWidgetx.item(self.tableWidgetx.rowCount()-2,0).text()),Unit.dimension(self,item,1)))
            else:
                item=0
                self.tableWidgetx.setRowCount(self.tableWidgetx.rowCount()+1)
                self.tableWidgetx.setItem((self.tableWidgetx.rowCount()-1),0,QTableWidgetItem( 'A'))
                self.tableWidgetx.setItem((self.tableWidgetx.rowCount()-1),1,QTableWidgetItem( str(item)))
                Variables.gridxTemp.append((str(self.tableWidgetx.item(self.tableWidgetx.rowCount()-1,0).text()),item))
        elif self.text1=='Space':
            item1=QTableWidgetItem( self.tableWidgetx.item(self.tableWidgetx.rowCount()-1,0))
            item2=QTableWidgetItem( self.tableWidgetx.item(self.tableWidgetx.rowCount()-1,1))
            item3=Variables.gridxTemp[self.tableWidgetx.rowCount()-1][1]
            Variables.gridxTemp.append((str(item1.text()),float(item3)+Unit.dimension(self,float(item2.text()),1)))
            self.tableWidgetx.setRowCount(self.tableWidgetx.rowCount()+1)
            self.tableWidgetx.setItem((self.tableWidgetx.rowCount()-1),0,item1)
            self.tableWidgetx.setItem((self.tableWidgetx.rowCount()-1),1,item2)
        Variables.gridxTemp.sort(key=self.takeSecond)
        self.tablefiller()
    
    def on_click_add_2(self):
        if self.text1=='Ordinate':
            if self.tableWidgety.rowCount()>1 :
                item=float(self.tableWidgety.item(self.tableWidgety.rowCount()-1,1).text())+float(self.tableWidgety.item(self.tableWidgety.rowCount()-1,1).text())-float(self.tableWidgety.item(self.tableWidgety.rowCount()-2,1).text())
                self.tableWidgety.setRowCount(self.tableWidgety.rowCount()+1)
                self.tableWidgety.setItem((self.tableWidgety.rowCount()-1),0,QTableWidgetItem( self.tableWidgety.item(self.tableWidgety.rowCount()-2,0)))
                self.tableWidgety.setItem((self.tableWidgety.rowCount()-1),1,QTableWidgetItem( str(item)))
                Variables.gridyTemp.append((str(self.tableWidgety.item(self.tableWidgety.rowCount()-2,0).text()),Unit.dimension(self,item,1)))
            else:
                item=0
                self.tableWidgety.setRowCount(self.tableWidgety.rowCount()+1)
                self.tableWidgety.setItem((self.tableWidgety.rowCount()-1),0,QTableWidgetItem( '1'))
                self.tableWidgety.setItem((self.tableWidgety.rowCount()-1),1,QTableWidgetItem( str(item)))
                Variables.gridyTemp.append((str(self.tableWidgety.item(self.tableWidgety.rowCount()-1,0).text()),item))
        elif self.text1=='Space':
            item1=QTableWidgetItem( self.tableWidgety.item(self.tableWidgety.rowCount()-1,0))
            item2=QTableWidgetItem( self.tableWidgety.item(self.tableWidgety.rowCount()-1,1))
            item3=Variables.gridyTemp[self.tableWidgety.rowCount()-1][1]            
            Variables.gridyTemp.append((str(item1.text()),float(item3)+Unit.dimension(self,float(item2.text()),1)))
            self.tableWidgety.setRowCount(self.tableWidgety.rowCount()+1)
            self.tableWidgety.setItem((self.tableWidgety.rowCount()-1),0,item1)
            self.tableWidgety.setItem((self.tableWidgety.rowCount()-1),1,item2)
        Variables.gridyTemp.sort(key=self.takeSecond)
        self.tablefiller()
    
    def on_click_add_3(self):
        if self.text1=='Ordinate':
            if self.tableWidgetz.rowCount()>1 :
                item=float(self.tableWidgetz.item(self.tableWidgetz.rowCount()-1,1).text())+float(self.tableWidgetz.item(self.tableWidgetz.rowCount()-1,1).text())-float(self.tableWidgetz.item(self.tableWidgetz.rowCount()-2,1).text())
                self.tableWidgetz.setRowCount(self.tableWidgetz.rowCount()+1)
                self.tableWidgetz.setItem((self.tableWidgetz.rowCount()-1),0,QTableWidgetItem( self.tableWidgetz.item(self.tableWidgetz.rowCount()-2,0)))
                self.tableWidgetz.setItem((self.tableWidgetz.rowCount()-1),1,QTableWidgetItem( str(item)))
                Variables.gridzTemp.append((str(self.tableWidgetz.item(self.tableWidgetz.rowCount()-2,0).text()),Unit.dimension(self,item,1)))
            else:
                item=0
                self.tableWidgetz.setRowCount(self.tableWidgetz.rowCount()+1)
                self.tableWidgetz.setItem((self.tableWidgetz.rowCount()-1),0,QTableWidgetItem( 'Z1'))
                self.tableWidgetz.setItem((self.tableWidgetz.rowCount()-1),1,QTableWidgetItem( str(item)))
                Variables.gridzTemp.append((str(self.tableWidgetz.item(self.tableWidgetz.rowCount()-1,0).text()),item))
        elif self.text1=='Space':
            item1=QTableWidgetItem( self.tableWidgetz.item(self.tableWidgetz.rowCount()-1,0))
            item2=QTableWidgetItem( self.tableWidgetz.item(self.tableWidgetz.rowCount()-1,1))
            item3=Variables.gridzTemp[self.tableWidgetz.rowCount()-1][1]
            Variables.gridzTemp.append((str(item1.text()),float(item3)+Unit.dimension(self,float(item2.text()),1)))
            self.tableWidgetz.setRowCount(self.tableWidgetz.rowCount()+1)
            self.tableWidgetz.setItem((self.tableWidgetz.rowCount()-1),0,item1)
            self.tableWidgetz.setItem((self.tableWidgetz.rowCount()-1),1,item2)
        Variables.gridzTemp.sort(key=self.takeSecond)
        self.tablefiller()

class OpenGLWidget(QOpenGLWidget):
    width=300
    height=500
    xcurrentMousePos=0
    ycurrentMousePos=0
    xmousePos=0
    ymousePos=0
    xmouseDif=0
    ymouseDif=0
    scale=1
    xAngle=20
    yAngle=20

    def focusInEvent(self,event):
        super(OpenGLWidget, self).focusInEvent(event)
        self.setFocus()

    def contextMenuEvent(self,pos):
        if Variables.isDrawing==False and Variables.ispickingPoint==False:
            if pos.modifiers() == Qt.ControlModifier:
                menu = QMenu(self)
                toolbarPselect= QAction("Previous Select <Ctrl + P>", self)
                toolbarPselect.triggered.connect(OpenGLWidget.previousselect)

                toolbarselectAll= QAction("Select All <Ctrl + A>", self)
                toolbarselectAll.triggered.connect(OpenGLWidget.selectAll)

                toolbarshowselect= QAction("Show Selected Only", self)
                toolbarshowselect.triggered.connect(OpenGLWidget.showselected)

                toolbarhideselect= QAction("Hide Selected", self)
                toolbarhideselect.triggered.connect(OpenGLWidget.hideselected)

                toolbarshowAll= QAction("Show All", self)
                toolbarshowAll.triggered.connect(OpenGLWidget.showAll)

                menu.addAction(toolbarselectAll)
                menu.addAction(toolbarPselect)
                menu.addSeparator()
                menu.addAction(toolbarshowselect)
                menu.addAction(toolbarhideselect)
                menu.addAction(toolbarshowAll)

                menu.exec_(self.mapToGlobal(pos.pos()))

    @staticmethod
    def showAll():

        for frame in Frame.framedict:
            frame['show']=True
        for joint in Joint.jointdict:
            joint['show']=True
        OpenGLWidget.selectionClear()
        mdi.statusBar().showMessage('')

    @staticmethod
    def showselected():
        if len(Variables.selectedFrames)==0 and len(Variables.selectedJoints)==0:
            mdi.statusBar().showMessage('Nothing Selected!')
        else:
            for frame in Frame.framedict:
                if Variables.selectedFrames.count(frame)==False:
                    if frame['deleted']==False:
                        frame['show']=False


            for joint in Joint.jointdict:
                if Variables.selectedJoints.count(joint)==False:
                    if joint['deleted']==False:
                        joint['show']=False
            OpenGLWidget.selectionClear()
            mdi.statusBar().showMessage('')

    @staticmethod
    def hideselected():
        for frame in Variables.selectedFrames:
            frame['show']=False
        for joint in Variables.selectedJoints:
            joint['show']=False
        OpenGLWidget.selectionClear()
        mdi.statusBar().showMessage('')

    def changeEvent(self,event):
        self.update()
        #window state değiştiğinde trigırlanıyor yani maximized olduğunda

    def initializeGL(self):
        logging.info("Opengl initializing start")
        try:
            self.view={'3d':True,'closed':'Z','yaxeloc':0,'xaxeloc':0,'zaxeloc':0 }
            self.setFocusPolicy(Qt.StrongFocus)            
            
            self.setMouseTracking(True)
            glLineStipple(8, 0x5555)
        except Exception as e:
            logging.debug(e)
        logging.info("Opengl initializing end")
    
    def paintGL(self):
        
        try:
            #glEnable(GL_DEPTH_TEST)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)          
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_BLEND)
            glEnable(GL_LINE_SMOOTH)
            glShadeModel(GL_SMOOTH)
            glEnable(GL_MULTISAMPLE)
            geo =self.geometry()
            self.width=geo.width()
            self.height=geo.height()
            self.resizeGL(self.width,self.height)        
            self.drawGrid()
            self.extrudeview()
            self.drawFrame()
            self.drawPoints()
            self.preFrameDraw()
            self.selectedPointDraw()
            self.PointSelectWRectDraw()
            self.drawSelectedFrame()
            self.drawJointLocalAxes()
            self.drawFrameLocalAxes()
            self.drawOrgin()
            self.drawGridText()
            self.drawSupport()
            self.pindraw()
            self.frametext()
            self.jointtext()
        except Exception as e:
            logging.debug(e)
            logging.info("Opengl PaintGL Crashed")

    def resizeGL(self, width, height):
        try:
            glClearColor(Variables.clearcolorfloat[0],Variables.clearcolorfloat[1],Variables.clearcolorfloat[2],Variables.clearcolorfloat[3])
        except Exception as e:
            logging.debug(e)
            logging.info("Opengl glClearColor crashed")

        try:
            glViewport(0, 0, width, height)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            
            if self.view['3d']:
                glOrtho(0, width,height,0, 10000, -10000)
                glTranslatef(width/2,height/2, 0)
                glTranslatef(self.xmouseDif,self.ymouseDif, 0)
                glRotatef(self.yAngle,1,0,0)
                glRotatef(self.xAngle,0,1,0)
                glScalef(self.scale,self.scale, self.scale)
                
            else:
                if self.view['closed']=='Y':
                    glOrtho(0, width,height,0, -self.view['yaxeloc']+1,-self.view['yaxeloc']-1)
                    glTranslatef(width/2,height/2, 0)
                    glTranslatef(self.xmouseDif,self.ymouseDif, 0)
                    glRotatef(0,1,0,0)
                    glRotatef(0,0,1,0)
                    glScalef(self.scale,self.scale, 1)
                elif self.view['closed']=='X':
                    glOrtho(0, width,height,0, self.view['xaxeloc']-1,self.view['xaxeloc']+1)
                    glTranslatef(width/2,height/2, 0)
                    glTranslatef(self.xmouseDif,self.ymouseDif, 0)
                    glRotatef(0,1,0,0)
                    glRotatef(90,0,1,0)
                    glScalef(1,self.scale, self.scale)
                elif self.view['closed']=='Z':
                    glOrtho(0, width,height,0, self.view['zaxeloc']-1,self.view['zaxeloc']+1)
                    glTranslatef(width/2,height/2, 0)
                    glTranslatef(self.xmouseDif,self.ymouseDif, 0)
                    glRotatef(90,1,0,0)
                    glRotatef(0,0,1,0)
                    glScalef(self.scale,1, self.scale)
            
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            self.update()
        except Exception as e:
            logging.debug(e)
            logging.info("Opengl ResizeGL crashed")
    
    def mousePressEvent(self, event):
        super(OpenGLWidget, self).mousePressEvent(event)
        x=event.pos()

        if event.button() == 1: #sol tık

            if Variables.isDrawing:
                if self.pinselect()!=None:
                    if Variables.isFirstJoint:
                        Variables.preFramepoints[0]=self.pinselect()
                        Variables.isFirstJoint=False
                        mdi.statusBar().showMessage('Draw Frame: Select Second Joint')
                    else:
                        Variables.preFramepoints[1]=self.pinselect()
                        frame = Frame((Variables.preFramepoints[0][0],Variables.preFramepoints[0][1],Variables.preFramepoints[0][2]),(Variables.preFramepoints[1][0],Variables.preFramepoints[1][1],Variables.preFramepoints[1][2]))
                        Variables.preFramepoints[0]=self.pinselect()
                        Variables.preFramepoints[1]=(None,None,None)
                        mdi.statusBar().showMessage('Frame No: '+ str(frame.count)+' added! / ' +'Draw Frame: Select Second Joint')

                else:
                    print("boşluğa tıklandı")
            elif Variables.ispickingPoint:
                
                    if self.pinselect()!=None:
                        if Variables.isFirstJoint:
                            Variables.preFramepoints[0]=self.pinselect()
                            Variables.isFirstJoint=False
                            mdi.statusBar().showMessage('Move: Pick Second Point')
                        else:
                            Variables.preFramepoints[1]=self.pinselect()
                            if Variables.ismovepicking :
                                mdi.movewindlg.text1.setText(str(Unit.dimension(self,Variables.preFramepoints[1][0]-Variables.preFramepoints[0][0],0)))
                                mdi.movewindlg.text3.setText(str(Unit.dimension(self,Variables.preFramepoints[0][1]-Variables.preFramepoints[1][1],0)))
                                mdi.movewindlg.text2.setText(str(Unit.dimension(self,Variables.preFramepoints[1][2]-Variables.preFramepoints[0][2],0)))                                
                                mdi.movewindlg.setEnabled(True)
                            if Variables.iscopypicking:
                                mdi.CopyWindlg.text1.setText(str(Unit.dimension(self,Variables.preFramepoints[1][0]-Variables.preFramepoints[0][0],0)))
                                mdi.CopyWindlg.text3.setText(str(Unit.dimension(self,Variables.preFramepoints[0][1]-Variables.preFramepoints[1][1],0)))
                                mdi.CopyWindlg.text2.setText(str(Unit.dimension(self,Variables.preFramepoints[1][2]-Variables.preFramepoints[0][2],0)))                                
                                mdi.CopyWindlg.setEnabled(True)
                            
                            QApplication.setOverrideCursor(Qt.CustomCursor)
                            Variables.isDrawing=False
                            Variables.isFirstJoint=True
                            Variables.takenPoint=(None,None,None)
                            Variables.preFramepoints=[(None,None,None),(None,None,None)]
                            Variables.ispickingPoint=False
                            
                            mdi.statusBar().showMessage('')
            else:
                self.xcurrentMousePos=x.x()
                self.ycurrentMousePos=x.y()
                self.pointAndframeSelect(x.x(),x.y())

        elif event.button() == 2 and event.modifiers() != Qt.ControlModifier: #sağ tık
            if Variables.isDrawing:
                Variables.isFirstJoint=True
                Variables.takenPoint=(None,None,None)
                Variables.preFramepoints=[(None,None,None),(None,None,None)]
                mdi.statusBar().showMessage('Draw Frame: Select First Joint')
            elif Variables.ispickingPoint:
                Variables.isFirstJoint=True
                Variables.takenPoint=(None,None,None)
                Variables.preFramepoints=[(None,None,None),(None,None,None)]
                mdi.statusBar().showMessage('Move: Pick First Point')
            else:
                self.selectionClear()
                mdi.statusBar().showMessage('')

        elif event.button() == 4: #tekerlek tık
            QApplication.setOverrideCursor(Qt.ClosedHandCursor)
            self.xmousePos=x.x()
            self.ymousePos=x.y()
            self.xcurrentMousePos=x.x()
            self.ycurrentMousePos=x.y()

    def mouseReleaseEvent(self, event):
        super(OpenGLWidget, self).mouseReleaseEvent(event)
        x=event.pos()

        if event.button() == 1:
            if Variables.isDrawing==False and Variables.ispickingPoint==False:
                if Variables.isrectdrawing:                    
                    self.PointSelectWRect(x.x(),x.y())
                    Variables.isrectdrawing=False
                # else:
                #     #TODO: picking bitmiş oluyor tıkladığı noktayı seçiyor
                #     self.pointAndframeSelect(x.x(),x.y())
        elif event.button() == 2:
            print("right")
        elif event.button() == 4:
            if Variables.isDrawing or Variables.ispickingPoint:
                QApplication.setOverrideCursor(Qt.CrossCursor)
            else:
                QApplication.setOverrideCursor(Qt.CustomCursor)
            print("middle")

    def mouseMoveEvent(self, event):
        super(OpenGLWidget, self).mouseMoveEvent(event)
        pos = event.pos()

        if event.buttons() == Qt.MiddleButton and event.modifiers() != Qt.ControlModifier:

            self.xcurrentMousePos=pos.x()
            self.ycurrentMousePos=pos.y()
            self.xmouseDif+=self.xcurrentMousePos-self.xmousePos
            self.ymouseDif+=self.ycurrentMousePos-self.ymousePos

        if event.buttons() == Qt.MiddleButton and event.modifiers() == Qt.ControlModifier:
            self.xcurrentMousePos=pos.x()
            self.ycurrentMousePos=pos.y()
            if (self.xcurrentMousePos-self.xmousePos)<0:
                self.xAngle+=1.2
            elif   (self.xcurrentMousePos-self.xmousePos)>0:
                self.xAngle-=1.2

            if (self.ycurrentMousePos-self.ymousePos)<0:
                self.yAngle-=1.2
            elif   (self.ycurrentMousePos-self.ymousePos)>0:
                self.yAngle+=1.2

        if event.buttons()==Qt.LeftButton :
            if Variables.isDrawing==False and Variables.ispickingPoint==False:
                Variables.isrectdrawing=True
            else:
                Variables.isrectdrawing=False

        self.xmousePos=pos.x()
        self.ymousePos=pos.y()

    def wheelEvent(self, event):
        super(OpenGLWidget, self).wheelEvent(event)
        delta = event.angleDelta()

        if self.scale > 0.02 :
            if self.scale < 10:

                self.scale+=delta.y()/7000
            else:
                self.scale = 9.99
        else:
            self.scale=0.021

    def keyPressEvent(self, event):
            if event.key() == Qt.Key_Escape:
                if Variables.isDrawing or Variables.ispickingPoint:
                    QApplication.setOverrideCursor(Qt.CustomCursor)
                    Variables.isDrawing=False
                    Variables.isFirstJoint=True
                    Variables.takenPoint=(None,None,None)
                    Variables.preFramepoints=[(None,None,None),(None,None,None)]
                    if Variables.ispickingPoint:
                        Variables.ispickingPoint=False
                        if Variables.ismovepicking:
                            mdi.movewindlg.setEnabled(True)
                        if Variables.iscopypicking:
                            mdi.CopyWindlg.setEnabled(True)
                    mdi.statusBar().showMessage('')
                else:
                    self.selectionClear()
                    mdi.statusBar().showMessage('')

            if event.key() == Qt.Key_Delete:
                if Variables.isDrawing==False and Variables.ispickingPoint==False:
                    Frame.deleteFrame()
                    mdi.sub.selectionClear()
                    mdi.statusBar().showMessage('Selected frames deleted!')
                #Frame.deleteJoint()

            if event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
                if Variables.isDrawing==False and Variables.ispickingPoint==False:
                    UndoReundo.undo()
                    self.selectionClear()

            if event.key() == Qt.Key_Y and event.modifiers() == Qt.ControlModifier:
                if Variables.isDrawing==False and Variables.ispickingPoint==False:
                    UndoReundo.reundo()
                    self.selectionClear()

            if event.key() == Qt.Key_F and event.modifiers() == Qt.ControlModifier:
                if  Variables.ispickingPoint==False:
                    self.DrawFrameTrig()
            if event.key() == Qt.Key_P and event.modifiers() == Qt.ControlModifier:
                if Variables.isDrawing==False and Variables.ispickingPoint==False:
                    self.previousselect()
            if event.key() == Qt.Key_A and event.modifiers() == Qt.ControlModifier:
                if Variables.isDrawing==False and Variables.ispickingPoint==False:
                    self.selectAll()
            if event.key() == Qt.Key_M and event.modifiers() == Qt.ControlModifier:
                if Variables.isDrawing==False and Variables.ispickingPoint==False:
                    mdi.moveWindowTrig()
            if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
                if Variables.isDrawing==False and Variables.ispickingPoint==False:
                    mdi.copyWindowTrig()
            if event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
                if Variables.path==None:
                    mdi.saveFileDialog()
                else:
                    Savefile(Variables.path)
            if event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier |  Qt.ShiftModifier:
                mdi.saveFileDialog()
                
            if event.key() == Qt.Key_O and event.modifiers() == Qt.ControlModifier:
                mdi.openFileNameDialog()

            if event.key() == Qt.Key_N and event.modifiers() == Qt.ControlModifier:
                mdi.newfile()

    def drawPoints(self):
        glPointSize(Variables.pointwidth)
        glBegin (GL_POINTS)
        glColor3ub(Variables.pointColor[0],Variables.pointColor[1],Variables.pointColor[2])
        for joint in Joint.jointdict:
            if joint['show'] and joint['deleted']==False and Variables.showjointnode:
                glVertex3d(joint['coords'][0],joint['coords'][1],joint['coords'][2])
        glEnd()

    def preFrameDraw(self):
        if (Variables.isDrawing and Variables.isFirstJoint==False and Variables.preFramepoints[0][0]!=None) or (Variables.ispickingPoint and Variables.isFirstJoint==False and Variables.preFramepoints[0][0]!=None) :
            x,y,z=self.mouse_project(Variables.preFramepoints[0][0],Variables.preFramepoints[0][1],Variables.preFramepoints[0][2])
            qp = QPainter(self)
            qp.beginNativePainting()
            qp.endNativePainting()
            qp.setRenderHint(QPainter.Antialiasing)            
            qp.setPen(QColor(Variables.preframecolor[0], Variables.preframecolor[1], Variables.preframecolor[2]))
            qp.drawLine(int(x),int(y),int(self.xmousePos),int(self.ymousePos))
            qp.end()

    def drawFrame(self):
        try:
            glLineWidth(Variables.framewidth)
            glBegin(GL_LINES)
            glColor3ub(Variables.frameColor[0],Variables.frameColor[1],Variables.frameColor[2])
            for frame in Frame.framedict:
                if frame['show'] and frame['deleted']==False:
                    for joint in Joint.jointdict:
                        if joint['name']==frame['joint0']:
                            glVertex3d(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        if joint['name']==frame['joint1']:
                            glVertex3d(joint['coords'][0],joint['coords'][1],joint['coords'][2])
            glEnd()
        except Exception as e:
            logging.debug(e)
            logging.info("Opengl drawframe Crashed")

    def drawSelectedFrame(self):
        try:
            glLineWidth(Variables.framewidth)
            glEnable(GL_LINE_STIPPLE)
            glBegin(GL_LINES)
            glColor3ub(Variables.selectedframecolor[0],Variables.selectedframecolor[1],Variables.selectedframecolor[2])
            for frame in Variables.selectedFrames:
                for joint in Joint.jointdict:
                        if joint['name']==frame['joint0']:
                            glVertex3d(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        if joint['name']==frame['joint1']:
                            glVertex3d(joint['coords'][0],joint['coords'][1],joint['coords'][2])
            glEnd()
            glDisable(GL_LINE_STIPPLE)
        except Exception as e:
            logging.debug(e)
            logging.info("Opengl drawselectedframe Crashed")

    def frametext(self):
        if Variables.framenametextdraw and Variables.showframesectionname==False:
            for frame in Frame.framedict:
                if frame['deleted']==False and frame['show']:
                    if self.view['3d']:
                        x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                        for joint in Joint.jointdict:
                                if joint['name']==frame['joint0']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                if joint['name']==frame['joint1']:
                                    x2,y2,z2=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                        qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                        qp.save()
                        qp.translate((x1+x2)/2,(y1+y2)/2)
                        angle = math.atan2(y2-y1, x2-x1)
                        angledeg= math.degrees(angle)
                        if angledeg<91 and angledeg>-89:
                            pass
                        else:
                            angledeg=(angledeg-180)
                        qp.rotate(angledeg)                        
                        qp.drawText(-(Variables.textfont[1]*len(str(frame['name']))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(frame['name'])),(Variables.textfont[1]*2),Qt.AlignCenter, str(frame['name']))
                        qp.restore()
                        qp.end()
                    else:
                        if self.view['closed']=='Y':
                            x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                            for joint in Joint.jointdict:
                                if joint['name']==frame['joint0'] and joint['coords'][2]==self.view['yaxeloc']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                    for joint1 in Joint.jointdict:
                                        if joint1['name']==frame['joint1'] and joint1['coords'][2]==self.view['yaxeloc']:
                                            x2,y2,z2=self.mouse_project(joint1['coords'][0],joint1['coords'][1],joint1['coords'][2])
                                            qp = QPainter(self)
                                            qp.beginNativePainting()
                                            qp.endNativePainting()
                                            qp.setRenderHint(QPainter.Antialiasing)
                                            qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                            qp.save()
                                            qp.translate((x1+x2)/2,(y1+y2)/2)
                                            angle = math.atan2(y2-y1, x2-x1)
                                            angledeg= math.degrees(angle)
                                            if angledeg<91 and angledeg>-89:
                                                pass
                                            else:
                                                angledeg=(angledeg-180)
                                            qp.rotate(angledeg)                                            
                                            qp.drawText(-(Variables.textfont[1]*len(str(frame['name']))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(frame['name'])),(Variables.textfont[1]*2),Qt.AlignCenter, str(frame['name']))
                                            qp.restore()
                                            qp.end()
                        elif self.view['closed']=='X':
                            x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                            for joint in Joint.jointdict:
                                if joint['name']==frame['joint0'] and joint['coords'][0]==self.view['xaxeloc']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                    for joint1 in Joint.jointdict:
                                        if joint1['name']==frame['joint1'] and joint1['coords'][0]==self.view['xaxeloc']:
                                            x2,y2,z2=self.mouse_project(joint1['coords'][0],joint1['coords'][1],joint1['coords'][2])
                                            qp = QPainter(self)
                                            qp.beginNativePainting()
                                            qp.endNativePainting()
                                            qp.setRenderHint(QPainter.Antialiasing)
                                            qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                            qp.save()
                                            qp.translate((x1+x2)/2,(y1+y2)/2)
                                            angle = math.atan2(y2-y1, x2-x1)
                                            angledeg= math.degrees(angle)
                                            if angledeg<91 and angledeg>-89:
                                                pass
                                            else:
                                                angledeg=(angledeg-180)
                                            qp.rotate(angledeg)
                                            qp.drawText(-(Variables.textfont[1]*len(str(frame['name']))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(frame['name'])),(Variables.textfont[1]*2),Qt.AlignCenter, str(frame['name']))
                                            qp.restore()
                                            qp.end()
                        elif self.view['closed']=='Z':
                            x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                            for joint in Joint.jointdict:
                                if joint['name']==frame['joint0'] and joint['coords'][1]==-self.view['zaxeloc']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                    for joint1 in Joint.jointdict:
                                        if joint1['name']==frame['joint1'] and joint1['coords'][1]==-self.view['zaxeloc']:
                                            x2,y2,z2=self.mouse_project(joint1['coords'][0],joint1['coords'][1],joint1['coords'][2])
                                            qp = QPainter(self)
                                            qp.beginNativePainting()
                                            qp.endNativePainting()
                                            qp.setRenderHint(QPainter.Antialiasing)
                                            qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                            qp.save()
                                            qp.translate((x1+x2)/2,(y1+y2)/2)
                                            angle = math.atan2(y2-y1, x2-x1)
                                            angledeg= math.degrees(angle)
                                            if angledeg<91 and angledeg>-89:
                                                pass
                                            else:
                                                angledeg=(angledeg-180)
                                            qp.rotate(angledeg)
                                            qp.drawText(-(Variables.textfont[1]*len(str(frame['name']))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(frame['name'])),(Variables.textfont[1]*2),Qt.AlignCenter, str(frame['name']))
                                            qp.restore()
                                            qp.end()
        elif Variables.framenametextdraw==False and Variables.showframesectionname:
            for frame in Frame.framedict:
                if frame['deleted']==False and frame['show']:
                    if self.view['3d']:
                        x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                        for joint in Joint.jointdict:
                                if joint['name']==frame['joint0']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                if joint['name']==frame['joint1']:
                                    x2,y2,z2=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                        qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                        qp.save()
                        qp.translate((x1+x2)/2,(y1+y2)/2)
                        angle = math.atan2(y2-y1, x2-x1)
                        angledeg= math.degrees(angle)
                        if angledeg<91 and angledeg>-89:
                            pass
                        else:
                            angledeg=(angledeg-180)
                        qp.rotate(angledeg)

                        sectionname="No Section"
                        if frame['section']=="No Section":
                            sectionname="No Section"
                        else:
                            for section in Sections.sectiondict:
                                if section['deleted']==False:
                                    if section['index']==frame['section']:
                                        sectionname=section['name']
                        qp.drawText(-(Variables.textfont[1]*len(str(sectionname))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(sectionname)),(Variables.textfont[1]*2),Qt.AlignCenter, str(sectionname))

                        qp.restore()
                        qp.end()
                    else:
                        if self.view['closed']=='Y':
                            x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                            for joint in Joint.jointdict:
                                if joint['name']==frame['joint0'] and joint['coords'][2]==self.view['yaxeloc']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                    for joint1 in Joint.jointdict:
                                        if joint1['name']==frame['joint1'] and joint1['coords'][2]==self.view['yaxeloc']:
                                            x2,y2,z2=self.mouse_project(joint1['coords'][0],joint1['coords'][1],joint1['coords'][2])
                                            qp = QPainter(self)
                                            qp.beginNativePainting()
                                            qp.endNativePainting()
                                            qp.setRenderHint(QPainter.Antialiasing)
                                            qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                            qp.save()
                                            qp.translate((x1+x2)/2,(y1+y2)/2)
                                            angle = math.atan2(y2-y1, x2-x1)
                                            angledeg= math.degrees(angle)
                                            if angledeg<91 and angledeg>-89:
                                                pass
                                            else:
                                                angledeg=(angledeg-180)
                                            qp.rotate(angledeg)  
                                            
                                            sectionname="No Section"
                                            if frame['section']=="No Section":
                                                sectionname="No Section"
                                            else:
                                                for section in Sections.sectiondict:
                                                    if section['deleted']==False:
                                                        if section['index']==frame['section']:
                                                            sectionname=section['name']
                                            qp.drawText(-(Variables.textfont[1]*len(str(sectionname))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(sectionname)),(Variables.textfont[1]*2),Qt.AlignCenter, str(sectionname))
                                          
                                            qp.restore()
                                            qp.end()
                        elif self.view['closed']=='X':
                            x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                            for joint in Joint.jointdict:
                                if joint['name']==frame['joint0'] and joint['coords'][0]==self.view['xaxeloc']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                    for joint1 in Joint.jointdict:
                                        if joint1['name']==frame['joint1'] and joint1['coords'][0]==self.view['xaxeloc']:
                                            x2,y2,z2=self.mouse_project(joint1['coords'][0],joint1['coords'][1],joint1['coords'][2])
                                            qp = QPainter(self)
                                            qp.beginNativePainting()
                                            qp.endNativePainting()
                                            qp.setRenderHint(QPainter.Antialiasing)
                                            qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                            qp.save()
                                            qp.translate((x1+x2)/2,(y1+y2)/2)
                                            angle = math.atan2(y2-y1, x2-x1)
                                            angledeg= math.degrees(angle)
                                            if angledeg<91 and angledeg>-89:
                                                pass
                                            else:
                                                angledeg=(angledeg-180)
                                            qp.rotate(angledeg)
                                            
                                            sectionname="No Section"
                                            if frame['section']=="No Section":
                                                sectionname="No Section"
                                            else:
                                                for section in Sections.sectiondict:
                                                    if section['deleted']==False:
                                                        if section['index']==frame['section']:
                                                            sectionname=section['name']
                                            qp.drawText(-(Variables.textfont[1]*len(str(sectionname))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(sectionname)),(Variables.textfont[1]*2),Qt.AlignCenter, str(sectionname))

                                            qp.restore()
                                            qp.end()
                        elif self.view['closed']=='Z':
                            x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                            for joint in Joint.jointdict:
                                if joint['name']==frame['joint0'] and joint['coords'][1]==-self.view['zaxeloc']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                    for joint1 in Joint.jointdict:
                                        if joint1['name']==frame['joint1'] and joint1['coords'][1]==-self.view['zaxeloc']:
                                            x2,y2,z2=self.mouse_project(joint1['coords'][0],joint1['coords'][1],joint1['coords'][2])
                                            qp = QPainter(self)
                                            qp.beginNativePainting()
                                            qp.endNativePainting()
                                            qp.setRenderHint(QPainter.Antialiasing)
                                            qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                            qp.save()
                                            qp.translate((x1+x2)/2,(y1+y2)/2)
                                            angle = math.atan2(y2-y1, x2-x1)
                                            angledeg= math.degrees(angle)
                                            if angledeg<91 and angledeg>-89:
                                                pass
                                            else:
                                                angledeg=(angledeg-180)
                                            qp.rotate(angledeg)
                                            
                                            sectionname="No Section"
                                            if frame['section']=="No Section":
                                                sectionname="No Section"
                                            else:
                                                for section in Sections.sectiondict:
                                                    if section['deleted']==False:
                                                        if section['index']==frame['section']:
                                                            sectionname=section['name']
                                            qp.drawText(-(Variables.textfont[1]*len(str(sectionname))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(sectionname)),(Variables.textfont[1]*2),Qt.AlignCenter, str(sectionname))

                                            qp.restore()
                                            qp.end()
        elif Variables.framenametextdraw and Variables.showframesectionname:
            for frame in Frame.framedict:
                if frame['deleted']==False and frame['show']:
                    if self.view['3d']:
                        x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                        for joint in Joint.jointdict:
                                if joint['name']==frame['joint0']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                if joint['name']==frame['joint1']:
                                    x2,y2,z2=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                        qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                        qp.save()
                        qp.translate((x1+x2)/2,(y1+y2)/2)
                        angle = math.atan2(y2-y1, x2-x1)
                        angledeg= math.degrees(angle)
                        if angledeg<91 and angledeg>-89:
                            pass
                        else:
                            angledeg=(angledeg-180)
                        qp.rotate(angledeg)

                        sectionname="No Section"
                        if frame['section']=="No Section":
                            sectionname="No Section"
                        else:
                            for section in Sections.sectiondict:
                                if section['deleted']==False:
                                    if section['index']==frame['section']:
                                        sectionname=section['name']
                        qp.drawText(-(Variables.textfont[1]*len(str(frame['name'])+"-"+ str(sectionname))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(frame['name'])+"-"+ str(sectionname)),(Variables.textfont[1]*2),Qt.AlignCenter, str(frame['name'])+"-"+ str(sectionname))
                        qp.restore()
                        qp.end()
                    else:
                        if self.view['closed']=='Y':
                            x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                            for joint in Joint.jointdict:
                                if joint['name']==frame['joint0'] and joint['coords'][2]==self.view['yaxeloc']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                    for joint1 in Joint.jointdict:
                                        if joint1['name']==frame['joint1'] and joint1['coords'][2]==self.view['yaxeloc']:
                                            x2,y2,z2=self.mouse_project(joint1['coords'][0],joint1['coords'][1],joint1['coords'][2])
                                            qp = QPainter(self)
                                            qp.beginNativePainting()
                                            qp.endNativePainting()
                                            qp.setRenderHint(QPainter.Antialiasing)
                                            qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                            qp.save()
                                            qp.translate((x1+x2)/2,(y1+y2)/2)
                                            angle = math.atan2(y2-y1, x2-x1)
                                            angledeg= math.degrees(angle)
                                            if angledeg<91 and angledeg>-89:
                                                pass
                                            else:
                                                angledeg=(angledeg-180)
                                            qp.rotate(angledeg)  
                                            
                                            sectionname="No Section"
                                            if frame['section']=="No Section":
                                                sectionname="No Section"
                                            else:
                                                for section in Sections.sectiondict:
                                                    if section['deleted']==False:
                                                        if section['index']==frame['section']:
                                                            sectionname=section['name']
                                            qp.drawText(-(Variables.textfont[1]*len(str(frame['name'])+"-"+ str(sectionname))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(frame['name'])+"-"+ str(sectionname)),(Variables.textfont[1]*2),Qt.AlignCenter, str(frame['name'])+"-"+ str(sectionname))
                                            qp.restore()
                                            qp.end()
                        elif self.view['closed']=='X':
                            x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                            for joint in Joint.jointdict:
                                if joint['name']==frame['joint0'] and joint['coords'][0]==self.view['xaxeloc']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                    for joint1 in Joint.jointdict:
                                        if joint1['name']==frame['joint1'] and joint1['coords'][0]==self.view['xaxeloc']:
                                            x2,y2,z2=self.mouse_project(joint1['coords'][0],joint1['coords'][1],joint1['coords'][2])
                                            qp = QPainter(self)
                                            qp.beginNativePainting()
                                            qp.endNativePainting()
                                            qp.setRenderHint(QPainter.Antialiasing)
                                            qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                            qp.save()
                                            qp.translate((x1+x2)/2,(y1+y2)/2)
                                            angle = math.atan2(y2-y1, x2-x1)
                                            angledeg= math.degrees(angle)
                                            if angledeg<91 and angledeg>-89:
                                                pass
                                            else:
                                                angledeg=(angledeg-180)
                                            qp.rotate(angledeg)
                                            
                                            sectionname="No Section"
                                            if frame['section']=="No Section":
                                                sectionname="No Section"
                                            else:
                                                for section in Sections.sectiondict:
                                                    if section['deleted']==False:
                                                        if section['index']==frame['section']:
                                                            sectionname=section['name']
                                            qp.drawText(-(Variables.textfont[1]*len(str(frame['name'])+"-"+ str(sectionname))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(frame['name'])+"-"+ str(sectionname)),(Variables.textfont[1]*2),Qt.AlignCenter, str(frame['name'])+"-"+ str(sectionname))
                                            qp.restore()
                                            qp.end()
                        elif self.view['closed']=='Z':
                            x1,y1,z1,x2,y2,z2=None,None,None,None,None,None
                            for joint in Joint.jointdict:
                                if joint['name']==frame['joint0'] and joint['coords'][1]==-self.view['zaxeloc']:
                                    x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                    for joint1 in Joint.jointdict:
                                        if joint1['name']==frame['joint1'] and joint1['coords'][1]==-self.view['zaxeloc']:
                                            x2,y2,z2=self.mouse_project(joint1['coords'][0],joint1['coords'][1],joint1['coords'][2])
                                            qp = QPainter(self)
                                            qp.beginNativePainting()
                                            qp.endNativePainting()
                                            qp.setRenderHint(QPainter.Antialiasing)
                                            qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                            qp.save()
                                            qp.translate((x1+x2)/2,(y1+y2)/2)
                                            angle = math.atan2(y2-y1, x2-x1)
                                            angledeg= math.degrees(angle)
                                            if angledeg<91 and angledeg>-89:
                                                pass
                                            else:
                                                angledeg=(angledeg-180)
                                            qp.rotate(angledeg)
                                            
                                            sectionname="No Section"
                                            if frame['section']=="No Section":
                                                sectionname="No Section"
                                            else:
                                                for section in Sections.sectiondict:
                                                    if section['deleted']==False:
                                                        if section['index']==frame['section']:
                                                            sectionname=section['name']
                                            qp.drawText(-(Variables.textfont[1]*len(str(frame['name'])+"-"+ str(sectionname))/2),-(Variables.textfont[1]*2),Variables.textfont[1]*len(str(frame['name'])+"-"+ str(sectionname)),(Variables.textfont[1]*2),Qt.AlignCenter, str(frame['name'])+"-"+ str(sectionname))
                                            qp.restore()
                                            qp.end()

    def jointtext(self):
        if Variables.jointnametextdraw:
            for joint in Joint.jointdict:
                if joint['deleted']==False and joint['show']:
                    if self.view['3d']:
                        x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                        qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                        qp.translate(x1+10,y1)
                        qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, str(joint['name']))
                        qp.end()
                    else:
                        if self.view['closed']=='Y':
                            if joint['coords'][2]==self.view['yaxeloc']:
                                x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                qp = QPainter(self)
                                qp.beginNativePainting()
                                qp.endNativePainting()
                                qp.setRenderHint(QPainter.Antialiasing)
                                qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                qp.translate(x1+10,y1)
                                qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, str(joint['name']))
                                qp.end()
                        elif self.view['closed']=='X':
                            if joint['coords'][0]==self.view['xaxeloc']:
                                x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                qp = QPainter(self)
                                qp.beginNativePainting()
                                qp.endNativePainting()
                                qp.setRenderHint(QPainter.Antialiasing)
                                qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                qp.translate(x1+10,y1)
                                qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, str(joint['name']))
                                qp.end()
                        elif self.view['closed']=='Z':
                            if joint['coords'][1]==-self.view['zaxeloc']:
                                x1,y1,z1=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                qp = QPainter(self)
                                qp.beginNativePainting()
                                qp.endNativePainting()
                                qp.setRenderHint(QPainter.Antialiasing)
                                qp.setPen(QColor(Variables.textcolor[0], Variables.textcolor[1], Variables.textcolor[2]))
                                qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                                qp.translate(x1+10,y1)
                                qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, str(joint['name']))
                                qp.end()

    def mouse_project(self,x,y,z):
        geo =self.geometry()
        Variables.width=geo.width()
        Variables.height=geo.height()
        self.resizeGL(Variables.width,Variables.height)
        pmat = (GLdouble * 16)()
        mvmat = (GLdouble * 16)()
        view = (GLint * 4)()
        px = (GLdouble)()
        py = (GLdouble)()
        pz = (GLdouble)()
        glGetDoublev(GL_MODELVIEW_MATRIX, mvmat)
        glGetDoublev(GL_PROJECTION_MATRIX, pmat)
        glGetIntegerv(GL_VIEWPORT, view)
        px,py,pz= gluProject(x, y, z, mvmat, pmat, view)
        return (px,view[3]-py,pz)

    def PointSelectWRectDraw(self):
        if Variables.isrectdrawing and Variables.isDrawing==False and Variables.ispickingPoint==False:
            qp = QPainter(self)
            qp.beginNativePainting()
            qp.endNativePainting()
            qp.setRenderHint(QPainter.Antialiasing)
            qp.setPen(QColor(Variables.selectrectanglecolor[0], Variables.selectrectanglecolor[1], Variables.selectrectanglecolor[2]))
            qp.drawRect(self.xcurrentMousePos,self.ycurrentMousePos,self.xmousePos-self.xcurrentMousePos,self.ymousePos-self.ycurrentMousePos)
            qp.end()

    def PointSelectWRect(self,xmouse,ymouse):
        currentselectedpoints=[]
        for joint in Joint.jointdict:
            if joint['deleted']==False:
                if self.view['3d']:
                    x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                    if xmouse<self.xcurrentMousePos and ymouse<self.ycurrentMousePos:
                        if x>xmouse and x<self.xcurrentMousePos and y>ymouse and y<self.ycurrentMousePos:
                            print("sol üst")
                            currentselectedpoints.append(joint)
                            if joint['show'] :
                                if Variables.selectedJoints.count(joint)==False:
                                    Variables.selectedJoints.append(joint)
                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                    elif xmouse>self.xcurrentMousePos and ymouse>self.ycurrentMousePos:
                        if x<xmouse and x>self.xcurrentMousePos and y<ymouse and y>self.ycurrentMousePos:
                            print("sağ alt")
                            currentselectedpoints.append(joint)
                            if joint['show'] :
                                if Variables.selectedJoints.count(joint)==False:
                                    Variables.selectedJoints.append(joint)
                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                    elif xmouse<self.xcurrentMousePos and ymouse>self.ycurrentMousePos:
                        if x>xmouse and x<self.xcurrentMousePos and y<ymouse and y>self.ycurrentMousePos:
                            print("sol alt")
                            currentselectedpoints.append(joint)
                            if joint['show'] :
                                if Variables.selectedJoints.count(joint)==False:
                                    Variables.selectedJoints.append(joint)
                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                    elif xmouse>self.xcurrentMousePos and ymouse<self.ycurrentMousePos:
                        if x<xmouse and x>self.xcurrentMousePos and y>ymouse and y<self.ycurrentMousePos:
                            print("sağ üst")
                            currentselectedpoints.append(joint)
                            if joint['show'] :
                                if Variables.selectedJoints.count(joint)==False:
                                    Variables.selectedJoints.append(joint)
                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                else:
                    if self.view['closed']=='Y':
                        if joint['coords'][2]==self.view['yaxeloc']:
                            x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                            if xmouse<self.xcurrentMousePos and ymouse<self.ycurrentMousePos:
                                if x>xmouse and x<self.xcurrentMousePos and y>ymouse and y<self.ycurrentMousePos:
                                    print("sol üst")
                                    currentselectedpoints.append(joint)
                                    if joint['show'] :
                                        if Variables.selectedJoints.count(joint)==False:
                                            Variables.selectedJoints.append(joint)
                                            mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                            elif xmouse>self.xcurrentMousePos and ymouse>self.ycurrentMousePos:
                                if x<xmouse and x>self.xcurrentMousePos and y<ymouse and y>self.ycurrentMousePos:
                                    print("sağ alt")
                                    currentselectedpoints.append(joint)
                                    if joint['show'] :
                                        if Variables.selectedJoints.count(joint)==False:
                                            Variables.selectedJoints.append(joint)
                                            mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                            elif xmouse<self.xcurrentMousePos and ymouse>self.ycurrentMousePos:
                                if x>xmouse and x<self.xcurrentMousePos and y<ymouse and y>self.ycurrentMousePos:
                                    print("sol alt")
                                    currentselectedpoints.append(joint)
                                    if joint['show'] :
                                        if Variables.selectedJoints.count(joint)==False:
                                            Variables.selectedJoints.append(joint)
                                            mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                            elif xmouse>self.xcurrentMousePos and ymouse<self.ycurrentMousePos:
                                if x<xmouse and x>self.xcurrentMousePos and y>ymouse and y<self.ycurrentMousePos:
                                    print("sağ üst")
                                    currentselectedpoints.append(joint)
                                    if joint['show'] :
                                        if Variables.selectedJoints.count(joint)==False:
                                            Variables.selectedJoints.append(joint)
                                            mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                    elif self.view['closed']=='X':
                            if joint['coords'][0]==self.view['xaxeloc']:
                                x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                if xmouse<self.xcurrentMousePos and ymouse<self.ycurrentMousePos:
                                    if x>xmouse and x<self.xcurrentMousePos and y>ymouse and y<self.ycurrentMousePos:
                                        print("sol üst")
                                        currentselectedpoints.append(joint)
                                        if joint['show'] :
                                            if Variables.selectedJoints.count(joint)==False:
                                                Variables.selectedJoints.append(joint)
                                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                elif xmouse>self.xcurrentMousePos and ymouse>self.ycurrentMousePos:
                                    if x<xmouse and x>self.xcurrentMousePos and y<ymouse and y>self.ycurrentMousePos:
                                        print("sağ alt")
                                        currentselectedpoints.append(joint)
                                        if joint['show'] :
                                            if Variables.selectedJoints.count(joint)==False:
                                                Variables.selectedJoints.append(joint)
                                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                elif xmouse<self.xcurrentMousePos and ymouse>self.ycurrentMousePos:
                                    if x>xmouse and x<self.xcurrentMousePos and y<ymouse and y>self.ycurrentMousePos:
                                        print("sol alt")
                                        currentselectedpoints.append(joint)
                                        if joint['show'] :
                                            if Variables.selectedJoints.count(joint)==False:
                                                Variables.selectedJoints.append(joint)
                                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                elif xmouse>self.xcurrentMousePos and ymouse<self.ycurrentMousePos:
                                    if x<xmouse and x>self.xcurrentMousePos and y>ymouse and y<self.ycurrentMousePos:
                                        print("sağ üst")
                                        currentselectedpoints.append(joint)
                                        if joint['show'] :
                                            if Variables.selectedJoints.count(joint)==False:
                                                Variables.selectedJoints.append(joint)
                                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                    elif self.view['closed']=='Z':
                            if joint['coords'][1]==-self.view['zaxeloc']:
                                x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                if xmouse<self.xcurrentMousePos and ymouse<self.ycurrentMousePos:
                                    if x>xmouse and x<self.xcurrentMousePos and y>ymouse and y<self.ycurrentMousePos:
                                        print("sol üst")
                                        currentselectedpoints.append(joint)
                                        if joint['show'] :
                                            if Variables.selectedJoints.count(joint)==False:
                                                Variables.selectedJoints.append(joint)
                                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                elif xmouse>self.xcurrentMousePos and ymouse>self.ycurrentMousePos:
                                    if x<xmouse and x>self.xcurrentMousePos and y<ymouse and y>self.ycurrentMousePos:
                                        print("sağ alt")
                                        currentselectedpoints.append(joint)
                                        if joint['show'] :
                                            if Variables.selectedJoints.count(joint)==False:
                                                Variables.selectedJoints.append(joint)
                                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                elif xmouse<self.xcurrentMousePos and ymouse>self.ycurrentMousePos:
                                    if x>xmouse and x<self.xcurrentMousePos and y<ymouse and y>self.ycurrentMousePos:
                                        print("sol alt")
                                        currentselectedpoints.append(joint)
                                        if joint['show'] :
                                            if Variables.selectedJoints.count(joint)==False:
                                                Variables.selectedJoints.append(joint)
                                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                elif xmouse>self.xcurrentMousePos and ymouse<self.ycurrentMousePos:
                                    if x<xmouse and x>self.xcurrentMousePos and y>ymouse and y<self.ycurrentMousePos:
                                        print("sağ üst")
                                        currentselectedpoints.append(joint)
                                        if joint['show'] :
                                            if Variables.selectedJoints.count(joint)==False:
                                                Variables.selectedJoints.append(joint)
                                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

        if len(currentselectedpoints)>1:
            for frame in Frame.framedict:
                if frame['show'] and frame['deleted']==False:
                    for joint in currentselectedpoints:
                        for joint1 in Joint.jointdict:
                            if joint1==joint:
                                if frame['joint0']==joint1['name']:
                                    for joint2 in currentselectedpoints:
                                        for joint3 in Joint.jointdict:
                                            if joint3==joint2:
                                                if frame['joint1']==joint3['name']:
                                                    if Variables.selectedFrames.count(frame)==False:
                                                        Variables.selectedFrames.append(frame)
                                                        mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

        #frame select with rect intersect
        for frame in Frame.framedict:
            if frame['show'] and frame['deleted']==False:
                if self.view['3d']:
                    joint1=None
                    joint2=None
                    for jointindex in Joint.jointdict:
                        if jointindex['name']==frame['joint0']:
                            joint1=jointindex['coords']
                        if jointindex['name']==frame['joint1']:
                            joint2=jointindex['coords']

                    x1,y1,z1=self.mouse_project(joint1[0],joint1[1],joint1[2])
                    x2,y2,z2=self.mouse_project(joint2[0],joint2[1],joint2[2])
                    line1=((x1,y1),(x2,y2))
                    line2=((xmouse,ymouse),(xmouse,self.ycurrentMousePos))
                    line3=((self.xcurrentMousePos,ymouse),(self.xcurrentMousePos,self.ycurrentMousePos))
                    line4=((xmouse,ymouse),(self.xcurrentMousePos,ymouse))
                    line5=((xmouse,self.ycurrentMousePos),(self.xcurrentMousePos,self.ycurrentMousePos))

                    x3,y3 = self.line_intersection(line1,line2)
                    x4,y4 = self.line_intersection(line1,line3)
                    x5,y5 = self.line_intersection(line1,line4)
                    x6,y6 = self.line_intersection(line1,line5)

                    if self.isBetween(line1[0],line1[1],(x3,y3)):
                        #sol üst
                        if x3>xmouse-1 and x3<self.xcurrentMousePos+1 and y3>ymouse-1 and y3<self.ycurrentMousePos+1:
                            if Variables.selectedFrames.count(frame)==False:
                                Variables.selectedFrames.append(frame)
                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                        #sol alt
                        if x3>xmouse-1 and x3<self.xcurrentMousePos+1 and y3<ymouse+1 and y3>self.ycurrentMousePos-1:
                            if Variables.selectedFrames.count(frame)==False:
                                Variables.selectedFrames.append(frame)
                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                    if self.isBetween(line1[0],line1[1],(x4,y4)):
                        #sol üst
                        if x4>xmouse-1 and x4<self.xcurrentMousePos+1 and y4>ymouse-1 and y4<self.ycurrentMousePos+1:
                            if Variables.selectedFrames.count(frame)==False:
                                Variables.selectedFrames.append(frame)
                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                        #sol alt
                        if x4>xmouse-1 and x4<self.xcurrentMousePos+1 and y4<ymouse+1 and y4>self.ycurrentMousePos-1:
                            if Variables.selectedFrames.count(frame)==False:
                                Variables.selectedFrames.append(frame)
                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                    if self.isBetween(line1[0],line1[1],(x5,y5)):
                        #sol üst
                        if x5>xmouse-1 and x5<self.xcurrentMousePos+1 and y5>ymouse-1 and y5<self.ycurrentMousePos+1:
                            if Variables.selectedFrames.count(frame)==False:
                                Variables.selectedFrames.append(frame)
                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                        #sol alt
                        if x5>xmouse-1 and x5<self.xcurrentMousePos+1 and y5<ymouse+1 and y5>self.ycurrentMousePos-1:
                            if Variables.selectedFrames.count(frame)==False:
                                Variables.selectedFrames.append(frame)
                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                    if self.isBetween(line1[0],line1[1],(x6,y6)):
                        #sol üst
                        if x6>xmouse-1 and x6<self.xcurrentMousePos+1 and y6>ymouse-1 and y6<self.ycurrentMousePos+1:
                            if Variables.selectedFrames.count(frame)==False:
                                Variables.selectedFrames.append(frame)
                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                        #sol alt
                        if x6>xmouse-1 and x6<self.xcurrentMousePos+1 and y6<ymouse+1 and y6>self.ycurrentMousePos-1:
                            if Variables.selectedFrames.count(frame)==False:
                                Variables.selectedFrames.append(frame)
                                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                else:
                    if self.view['closed']=='Y':
                        joint1=None
                        joint2=None
                        for jointindex in Joint.jointdict:
                            if jointindex['name']==frame['joint0'] and jointindex['coords'][2]==self.view['yaxeloc']:
                                joint1=jointindex['coords']
                                for jointindex1 in Joint.jointdict:
                                    if jointindex1['name']==frame['joint1'] and jointindex1['coords'][2]==self.view['yaxeloc']:
                                        joint2=jointindex1['coords']
                                        x1,y1,z1=self.mouse_project(joint1[0],joint1[1],joint1[2])
                                        x2,y2,z2=self.mouse_project(joint2[0],joint2[1],joint2[2])
                                        line1=((x1,y1),(x2,y2))
                                        line2=((xmouse,ymouse),(xmouse,self.ycurrentMousePos))
                                        line3=((self.xcurrentMousePos,ymouse),(self.xcurrentMousePos,self.ycurrentMousePos))
                                        line4=((xmouse,ymouse),(self.xcurrentMousePos,ymouse))
                                        line5=((xmouse,self.ycurrentMousePos),(self.xcurrentMousePos,self.ycurrentMousePos))

                                        x3,y3 = self.line_intersection(line1,line2)
                                        x4,y4 = self.line_intersection(line1,line3)
                                        x5,y5 = self.line_intersection(line1,line4)
                                        x6,y6 = self.line_intersection(line1,line5)

                                        if self.isBetween(line1[0],line1[1],(x3,y3)):
                                            #sol üst
                                            if x3>xmouse-1 and x3<self.xcurrentMousePos+1 and y3>ymouse-1 and y3<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                            #sol alt
                                            if x3>xmouse-1 and x3<self.xcurrentMousePos+1 and y3<ymouse+1 and y3>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                        if self.isBetween(line1[0],line1[1],(x4,y4)):
                                            #sol üst
                                            if x4>xmouse-1 and x4<self.xcurrentMousePos+1 and y4>ymouse-1 and y4<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                                            #sol alt
                                            if x4>xmouse-1 and x4<self.xcurrentMousePos+1 and y4<ymouse+1 and y4>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                        if self.isBetween(line1[0],line1[1],(x5,y5)):
                                            #sol üst
                                            if x5>xmouse-1 and x5<self.xcurrentMousePos+1 and y5>ymouse-1 and y5<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                                            #sol alt
                                            if x5>xmouse-1 and x5<self.xcurrentMousePos+1 and y5<ymouse+1 and y5>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                        if self.isBetween(line1[0],line1[1],(x6,y6)):
                                            #sol üst
                                            if x6>xmouse-1 and x6<self.xcurrentMousePos+1 and y6>ymouse-1 and y6<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                                            #sol alt
                                            if x6>xmouse-1 and x6<self.xcurrentMousePos+1 and y6<ymouse+1 and y6>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                    elif self.view['closed']=='X':
                        joint1=None
                        joint2=None
                        for jointindex in Joint.jointdict:
                            if jointindex['name']==frame['joint0'] and jointindex['coords'][0]==self.view['xaxeloc']:
                                joint1=jointindex['coords']
                                for jointindex1 in Joint.jointdict:
                                    if jointindex1['name']==frame['joint1'] and jointindex1['coords'][0]==self.view['xaxeloc']:
                                        joint2=jointindex1['coords']
                                        x1,y1,z1=self.mouse_project(joint1[0],joint1[1],joint1[2])
                                        x2,y2,z2=self.mouse_project(joint2[0],joint2[1],joint2[2])
                                        line1=((x1,y1),(x2,y2))
                                        line2=((xmouse,ymouse),(xmouse,self.ycurrentMousePos))
                                        line3=((self.xcurrentMousePos,ymouse),(self.xcurrentMousePos,self.ycurrentMousePos))
                                        line4=((xmouse,ymouse),(self.xcurrentMousePos,ymouse))
                                        line5=((xmouse,self.ycurrentMousePos),(self.xcurrentMousePos,self.ycurrentMousePos))

                                        x3,y3 = self.line_intersection(line1,line2)
                                        x4,y4 = self.line_intersection(line1,line3)
                                        x5,y5 = self.line_intersection(line1,line4)
                                        x6,y6 = self.line_intersection(line1,line5)

                                        if self.isBetween(line1[0],line1[1],(x3,y3)):
                                            #sol üst
                                            if x3>xmouse-1 and x3<self.xcurrentMousePos+1 and y3>ymouse-1 and y3<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                            #sol alt
                                            if x3>xmouse-1 and x3<self.xcurrentMousePos+1 and y3<ymouse+1 and y3>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                        if self.isBetween(line1[0],line1[1],(x4,y4)):
                                            #sol üst
                                            if x4>xmouse-1 and x4<self.xcurrentMousePos+1 and y4>ymouse-1 and y4<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                                            #sol alt
                                            if x4>xmouse-1 and x4<self.xcurrentMousePos+1 and y4<ymouse+1 and y4>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                        if self.isBetween(line1[0],line1[1],(x5,y5)):
                                            #sol üst
                                            if x5>xmouse-1 and x5<self.xcurrentMousePos+1 and y5>ymouse-1 and y5<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                                            #sol alt
                                            if x5>xmouse-1 and x5<self.xcurrentMousePos+1 and y5<ymouse+1 and y5>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                        if self.isBetween(line1[0],line1[1],(x6,y6)):
                                            #sol üst
                                            if x6>xmouse-1 and x6<self.xcurrentMousePos+1 and y6>ymouse-1 and y6<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                                            #sol alt
                                            if x6>xmouse-1 and x6<self.xcurrentMousePos+1 and y6<ymouse+1 and y6>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                    elif self.view['closed']=='Z':
                        joint1=None
                        joint2=None
                        for jointindex in Joint.jointdict:
                            if jointindex['name']==frame['joint0'] and jointindex['coords'][1]==-self.view['zaxeloc']:
                                joint1=jointindex['coords']
                                for jointindex1 in Joint.jointdict:
                                    if jointindex1['name']==frame['joint1'] and jointindex1['coords'][1]==-self.view['zaxeloc']:
                                        joint2=jointindex1['coords']
                                        x1,y1,z1=self.mouse_project(joint1[0],joint1[1],joint1[2])
                                        x2,y2,z2=self.mouse_project(joint2[0],joint2[1],joint2[2])
                                        line1=((x1,y1),(x2,y2))
                                        line2=((xmouse,ymouse),(xmouse,self.ycurrentMousePos))
                                        line3=((self.xcurrentMousePos,ymouse),(self.xcurrentMousePos,self.ycurrentMousePos))
                                        line4=((xmouse,ymouse),(self.xcurrentMousePos,ymouse))
                                        line5=((xmouse,self.ycurrentMousePos),(self.xcurrentMousePos,self.ycurrentMousePos))

                                        x3,y3 = self.line_intersection(line1,line2)
                                        x4,y4 = self.line_intersection(line1,line3)
                                        x5,y5 = self.line_intersection(line1,line4)
                                        x6,y6 = self.line_intersection(line1,line5)

                                        if self.isBetween(line1[0],line1[1],(x3,y3)):
                                            #sol üst
                                            if x3>xmouse-1 and x3<self.xcurrentMousePos+1 and y3>ymouse-1 and y3<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                            #sol alt
                                            if x3>xmouse-1 and x3<self.xcurrentMousePos+1 and y3<ymouse+1 and y3>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                        if self.isBetween(line1[0],line1[1],(x4,y4)):
                                            #sol üst
                                            if x4>xmouse-1 and x4<self.xcurrentMousePos+1 and y4>ymouse-1 and y4<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                                            #sol alt
                                            if x4>xmouse-1 and x4<self.xcurrentMousePos+1 and y4<ymouse+1 and y4>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                        if self.isBetween(line1[0],line1[1],(x5,y5)):
                                            #sol üst
                                            if x5>xmouse-1 and x5<self.xcurrentMousePos+1 and y5>ymouse-1 and y5<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                                            #sol alt
                                            if x5>xmouse-1 and x5<self.xcurrentMousePos+1 and y5<ymouse+1 and y5>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

                                        if self.isBetween(line1[0],line1[1],(x6,y6)):
                                            #sol üst
                                            if x6>xmouse-1 and x6<self.xcurrentMousePos+1 and y6>ymouse-1 and y6<self.ycurrentMousePos+1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))
                                            #sol alt
                                            if x6>xmouse-1 and x6<self.xcurrentMousePos+1 and y6<ymouse+1 and y6>self.ycurrentMousePos-1:
                                                if Variables.selectedFrames.count(frame)==False:
                                                    Variables.selectedFrames.append(frame)
                                                    mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

    def pointAndframeSelect(self,xmouse,ymouse):
        if Variables.isrectdrawing==False:
            selected=[] #her tıklayışta 1 tane seçer ya da siler Nokta öncelikli
            #Point select with click
            for joint in Joint.jointdict:                
                if joint['show'] and joint['deleted']==False:
                    if self.view['3d']:
                        x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        if x>xmouse-Variables.pickingrange and x<xmouse+Variables.pickingrange and y>ymouse-Variables.pickingrange and y<ymouse+Variables.pickingrange:
                            if Variables.selectedJoints.count(joint)==False:
                                selected.append((joint,0))
                            elif Variables.selectedJoints.count(joint):
                                selected.append((joint,1))
                    else:
                        if self.view['closed']=='Y':
                            if joint['coords'][2]==self.view['yaxeloc']:
                                x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                if x>xmouse-Variables.pickingrange and x<xmouse+Variables.pickingrange and y>ymouse-Variables.pickingrange and y<ymouse+Variables.pickingrange:
                                    if Variables.selectedJoints.count(joint)==False:
                                        selected.append((joint,0))
                                    elif Variables.selectedJoints.count(joint):
                                        selected.append((joint,1))
                        elif self.view['closed']=='X':
                            if joint['coords'][0]==self.view['xaxeloc']:
                                x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                if x>xmouse-Variables.pickingrange and x<xmouse+Variables.pickingrange and y>ymouse-Variables.pickingrange and y<ymouse+Variables.pickingrange:
                                    if Variables.selectedJoints.count(joint)==False:
                                        selected.append((joint,0))
                                    elif Variables.selectedJoints.count(joint):
                                        selected.append((joint,1))
                        elif self.view['closed']=='Z':
                            if joint['coords'][1]==-self.view['zaxeloc']:
                                x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                                if x>xmouse-Variables.pickingrange and x<xmouse+Variables.pickingrange and y>ymouse-Variables.pickingrange and y<ymouse+Variables.pickingrange:
                                    if Variables.selectedJoints.count(joint)==False:
                                        selected.append((joint,0))
                                    elif Variables.selectedJoints.count(joint):
                                        selected.append((joint,1))
            #frame select with click
            for frame in Frame.framedict:
                if frame['show'] and frame['deleted']==False:

                    if self.view['3d']:
                        joint1=None
                        joint2=None
                        for jointindex in Joint.jointdict:
                            if jointindex['name']==frame['joint0'] :
                                joint1=jointindex['coords']
                            if jointindex['name']==frame['joint1']:
                                joint2=jointindex['coords']

                        x1,y1,z1=self.mouse_project(joint1[0],joint1[1],joint1[2])
                        x2,y2,z2=self.mouse_project(joint2[0],joint2[1],joint2[2])
                        line1=((x1,y1),(x2,y2))
                        line2=((xmouse+Variables.pickingrange,ymouse+Variables.pickingrange),(xmouse-Variables.pickingrange,ymouse-Variables.pickingrange))
                        line3=((xmouse+Variables.pickingrange,ymouse-Variables.pickingrange),(xmouse-Variables.pickingrange,ymouse+Variables.pickingrange))
                        x3,y3 = self.line_intersection(line1,line2)
                        x4,y4 = self.line_intersection(line1,line3)
                        if self.isBetween(line1[0],line1[1],(x3,y3)):
                            if x3>xmouse-Variables.pickingrange and x3<xmouse+Variables.pickingrange and y3>ymouse-Variables.pickingrange and y3<ymouse+Variables.pickingrange:
                                if Variables.selectedFrames.count(frame)==False:
                                    selected.append((frame,0))
                                elif Variables.selectedFrames.count(frame):
                                    selected.append((frame,1))
                        if self.isBetween(line1[0],line1[1],(x4,y4)):
                            if x4>xmouse-Variables.pickingrange and x4<xmouse+Variables.pickingrange and y4>ymouse-Variables.pickingrange and y4<ymouse+Variables.pickingrange:
                                if Variables.selectedFrames.count(frame)==False:
                                    selected.append((frame,0))
                                elif Variables.selectedFrames.count(frame):
                                    selected.append((frame,1))
                    else:
                        if self.view['closed']=='Y':
                            joint1=None
                            joint2=None
                            for jointindex in Joint.jointdict:
                                if jointindex['name']==frame['joint0'] and jointindex['coords'][2]==self.view['yaxeloc']:
                                    joint1=jointindex['coords']
                                    for jointindex1 in Joint.jointdict:
                                        if jointindex1['name']==frame['joint1'] and jointindex1['coords'][2]==self.view['yaxeloc']:
                                            joint2=jointindex1['coords']
                                            x1,y1,z1=self.mouse_project(joint1[0],joint1[1],joint1[2])
                                            x2,y2,z2=self.mouse_project(joint2[0],joint2[1],joint2[2])
                                            line1=((x1,y1),(x2,y2))
                                            line2=((xmouse+Variables.pickingrange,ymouse+Variables.pickingrange),(xmouse-Variables.pickingrange,ymouse-Variables.pickingrange))
                                            line3=((xmouse+Variables.pickingrange,ymouse-Variables.pickingrange),(xmouse-Variables.pickingrange,ymouse+Variables.pickingrange))
                                            x3,y3 = self.line_intersection(line1,line2)
                                            x4,y4 = self.line_intersection(line1,line3)
                                            if self.isBetween(line1[0],line1[1],(x3,y3)):
                                                if x3>xmouse-Variables.pickingrange and x3<xmouse+Variables.pickingrange and y3>ymouse-Variables.pickingrange and y3<ymouse+Variables.pickingrange:
                                                    if Variables.selectedFrames.count(frame)==False:
                                                        selected.append((frame,0))
                                                    elif Variables.selectedFrames.count(frame):
                                                        selected.append((frame,1))
                                            if self.isBetween(line1[0],line1[1],(x4,y4)):
                                                if x4>xmouse-Variables.pickingrange and x4<xmouse+Variables.pickingrange and y4>ymouse-Variables.pickingrange and y4<ymouse+Variables.pickingrange:
                                                    if Variables.selectedFrames.count(frame)==False:
                                                        selected.append((frame,0))
                                                    elif Variables.selectedFrames.count(frame):
                                                        selected.append((frame,1))
                        elif self.view['closed']=='X':
                            joint1=None
                            joint2=None
                            for jointindex in Joint.jointdict:
                                if jointindex['name']==frame['joint0'] and jointindex['coords'][0]==self.view['xaxeloc']:
                                    joint1=jointindex['coords']
                                    for jointindex1 in Joint.jointdict:
                                        if jointindex1['name']==frame['joint1'] and jointindex1['coords'][0]==self.view['xaxeloc']:
                                            joint2=jointindex1['coords']
                                            x1,y1,z1=self.mouse_project(joint1[0],joint1[1],joint1[2])
                                            x2,y2,z2=self.mouse_project(joint2[0],joint2[1],joint2[2])
                                            line1=((x1,y1),(x2,y2))
                                            line2=((xmouse+Variables.pickingrange,ymouse+Variables.pickingrange),(xmouse-Variables.pickingrange,ymouse-Variables.pickingrange))
                                            line3=((xmouse+Variables.pickingrange,ymouse-Variables.pickingrange),(xmouse-Variables.pickingrange,ymouse+Variables.pickingrange))
                                            x3,y3 = self.line_intersection(line1,line2)
                                            x4,y4 = self.line_intersection(line1,line3)
                                            if self.isBetween(line1[0],line1[1],(x3,y3)):
                                                if x3>xmouse-Variables.pickingrange and x3<xmouse+Variables.pickingrange and y3>ymouse-Variables.pickingrange and y3<ymouse+Variables.pickingrange:
                                                    if Variables.selectedFrames.count(frame)==False:
                                                        selected.append((frame,0))
                                                    elif Variables.selectedFrames.count(frame):
                                                        selected.append((frame,1))
                                            if self.isBetween(line1[0],line1[1],(x4,y4)):
                                                if x4>xmouse-Variables.pickingrange and x4<xmouse+Variables.pickingrange and y4>ymouse-Variables.pickingrange and y4<ymouse+Variables.pickingrange:
                                                    if Variables.selectedFrames.count(frame)==False:
                                                        selected.append((frame,0))
                                                    elif Variables.selectedFrames.count(frame):
                                                        selected.append((frame,1))
                        elif self.view['closed']=='Z':
                            joint1=None
                            joint2=None
                            for jointindex in Joint.jointdict:
                                if jointindex['name']==frame['joint0'] and jointindex['coords'][1]==-self.view['zaxeloc']:
                                    joint1=jointindex['coords']
                                    for jointindex1 in Joint.jointdict:
                                        if jointindex1['name']==frame['joint1'] and jointindex1['coords'][1]==-self.view['zaxeloc']:
                                            joint2=jointindex1['coords']
                                            x1,y1,z1=self.mouse_project(joint1[0],joint1[1],joint1[2])
                                            x2,y2,z2=self.mouse_project(joint2[0],joint2[1],joint2[2])
                                            line1=((x1,y1),(x2,y2))
                                            line2=((xmouse+Variables.pickingrange,ymouse+Variables.pickingrange),(xmouse-Variables.pickingrange,ymouse-Variables.pickingrange))
                                            line3=((xmouse+Variables.pickingrange,ymouse-Variables.pickingrange),(xmouse-Variables.pickingrange,ymouse+Variables.pickingrange))
                                            x3,y3 = self.line_intersection(line1,line2)
                                            x4,y4 = self.line_intersection(line1,line3)
                                            if self.isBetween(line1[0],line1[1],(x3,y3)):
                                                if x3>xmouse-Variables.pickingrange and x3<xmouse+Variables.pickingrange and y3>ymouse-Variables.pickingrange and y3<ymouse+Variables.pickingrange:
                                                    if Variables.selectedFrames.count(frame)==False:
                                                        selected.append((frame,0))
                                                    elif Variables.selectedFrames.count(frame):
                                                        selected.append((frame,1))
                                            if self.isBetween(line1[0],line1[1],(x4,y4)):
                                                if x4>xmouse-Variables.pickingrange and x4<xmouse+Variables.pickingrange and y4>ymouse-Variables.pickingrange and y4<ymouse+Variables.pickingrange:
                                                    if Variables.selectedFrames.count(frame)==False:
                                                        selected.append((frame,0))
                                                    elif Variables.selectedFrames.count(frame):
                                                        selected.append((frame,1))

            if len(selected)>0:
                if selected[0][1]==0:
                    if selected[0][0]['type']=='joint':
                        Variables.selectedJoints.append(selected[0][0])
                    else:
                        Variables.selectedFrames.append(selected[0][0])

                else:
                    if selected[0][0]['type']=='joint':
                        Variables.selectedJoints.remove(selected[0][0])
                    else:
                        Variables.selectedFrames.remove(selected[0][0])
                mdi.statusBar().showMessage('Selected frame count: '+ str(len(Variables.selectedFrames))+' / Selected Joint Count: ' + str(len(Variables.selectedJoints)))

    def isBetween(self, a, b, c):
        crossproduct = (c[1] - a[1]) * (b[0] - a[0]) - (c[0] - a[0]) * (b[1] - a[1])
        epsilon=0.00001
        # compare versus epsilon for floating point values, or != 0 if using integers
        if abs(crossproduct) > epsilon:
            return False
        dotproduct = (c[0] - a[0]) * (b[0] - a[0]) + (c[1] - a[1])*(b[1] - a[1])
        if dotproduct < 0:
            return False
        squaredlengthba = (b[0] - a[0])*(b[0] - a[0]) + (b[1] - a[1])*(b[1] - a[1])
        if dotproduct > squaredlengthba:
            return False
        return True

    def line_intersection(self,line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]
        div = det(xdiff, ydiff)
        if div == 0:
           return 0,0
        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

    def selectedPointDraw(self):
        for joint in Variables.selectedJoints:
            if self.view['3d']:
                x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                qp = QPainter(self)
                qp.beginNativePainting()
                qp.endNativePainting()
                qp.setRenderHint(QPainter.Antialiasing)
                qp.setPen(QPen(QColor(Variables.selectedpointcolor[0], Variables.selectedpointcolor[1], Variables.selectedpointcolor[2]),Variables.selectedpointsize))
                qp.drawLine(int(x)+8,int(y)+8,int(x)-8,int(y)-8)
                qp.drawLine(int(x)-8,int(y)+8,int(x)+8,int(y)-8)
                qp.end()
            else:
                if self.view['closed']=='Y':
                    if joint['coords'][2]==self.view['yaxeloc']:
                        x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QPen(QColor(Variables.selectedpointcolor[0], Variables.selectedpointcolor[1], Variables.selectedpointcolor[2]),Variables.selectedpointsize))
                        qp.drawLine(int(x)+8,int(y)+8,int(x)-8,int(y)-8)
                        qp.drawLine(int(x)-8,int(y)+8,int(x)+8,int(y)-8)
                        qp.end()
                elif self.view['closed']=='X':
                    if joint['coords'][0]==self.view['xaxeloc']:
                        x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QPen(QColor(Variables.selectedpointcolor[0], Variables.selectedpointcolor[1], Variables.selectedpointcolor[2]),Variables.selectedpointsize))
                        qp.drawLine(int(x)+8,int(y)+8,int(x)-8,int(y)-8)
                        qp.drawLine(int(x)-8,int(y)+8,int(x)+8,int(y)-8)
                        qp.end()
                elif self.view['closed']=='Z':
                    if joint['coords'][1]==-self.view['zaxeloc']:
                        x,y,z=self.mouse_project(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QPen(QColor(Variables.selectedpointcolor[0], Variables.selectedpointcolor[1], Variables.selectedpointcolor[2]),Variables.selectedpointsize))
                        qp.drawLine(int(x)+8,int(y)+8,int(x)-8,int(y)-8)
                        qp.drawLine(int(x)-8,int(y)+8,int(x)+8,int(y)-8)
                        qp.end()

    def pindraw(self):
        if Variables.isDrawing or Variables.ispickingPoint:
            allPointsCanPinable=[]
            for point in Joint.jointdict:
                if point['show'] and point['deleted']==False:
                    allPointsCanPinable.append(point['coords'])
            for gridPoint in Variables.gridPoints:
                if gridPoint not in allPointsCanPinable:
                    allPointsCanPinable.append(gridPoint)
            for pinnablePoint in allPointsCanPinable:
                if self.view['3d']:
                    x,y,z=self.mouse_project(pinnablePoint[0],pinnablePoint[1],pinnablePoint[2])
                    if x>self.xmousePos - Variables.pingrange and x<self.xmousePos+Variables.pingrange and y>self.ymousePos-Variables.pingrange and y<self.ymousePos+Variables.pingrange:
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QPen(QColor(Variables.pincolor[0], Variables.pincolor[1], Variables.pincolor[2]),Variables.pinsize))
                        qp.drawEllipse(int(x)-Variables.pingrange,int(y)-Variables.pingrange,Variables.pingrange*2,Variables.pingrange*2)
                        qp.end()
                else:
                    if self.view['closed']=='Y':
                        if pinnablePoint[2]==self.view['yaxeloc']:
                            x,y,z=self.mouse_project(pinnablePoint[0],pinnablePoint[1],pinnablePoint[2])
                            if x>self.xmousePos - Variables.pingrange and x<self.xmousePos+Variables.pingrange and y>self.ymousePos-Variables.pingrange and y<self.ymousePos+Variables.pingrange:
                                qp = QPainter(self)
                                qp.beginNativePainting()
                                qp.endNativePainting()
                                qp.setRenderHint(QPainter.Antialiasing)
                                qp.setPen(QPen(QColor(Variables.pincolor[0], Variables.pincolor[1], Variables.pincolor[2]),Variables.pinsize))
                                qp.drawEllipse(int(x)-Variables.pingrange,int(y)-Variables.pingrange,Variables.pingrange*2,Variables.pingrange*2)
                                qp.end()
                    elif self.view['closed']=='X':
                        if pinnablePoint[0]==self.view['xaxeloc']:
                            x,y,z=self.mouse_project(pinnablePoint[0],pinnablePoint[1],pinnablePoint[2])
                            if x>self.xmousePos - Variables.pingrange and x<self.xmousePos+Variables.pingrange and y>self.ymousePos-Variables.pingrange and y<self.ymousePos+Variables.pingrange:
                                qp = QPainter(self)
                                qp.beginNativePainting()
                                qp.endNativePainting()
                                qp.setRenderHint(QPainter.Antialiasing)
                                qp.setPen(QPen(QColor(Variables.pincolor[0], Variables.pincolor[1], Variables.pincolor[2]),Variables.pinsize))
                                qp.drawEllipse(int(x)-Variables.pingrange,int(y)-Variables.pingrange,Variables.pingrange*2,Variables.pingrange*2)
                                qp.end()
                    elif self.view['closed']=='Z':
                        if pinnablePoint[1]==-self.view['zaxeloc']:
                            x,y,z=self.mouse_project(pinnablePoint[0],pinnablePoint[1],pinnablePoint[2])
                            if x>self.xmousePos - Variables.pingrange and x<self.xmousePos+Variables.pingrange and y>self.ymousePos-Variables.pingrange and y<self.ymousePos+Variables.pingrange:
                                qp = QPainter(self)
                                qp.beginNativePainting()
                                qp.endNativePainting()
                                qp.setRenderHint(QPainter.Antialiasing)
                                qp.setPen(QPen(QColor(Variables.pincolor[0], Variables.pincolor[1], Variables.pincolor[2]),Variables.pinsize))
                                qp.drawEllipse(int(x)-Variables.pingrange,int(y)-Variables.pingrange,Variables.pingrange*2,Variables.pingrange*2)
                                qp.end()

    def pinselect(self):
        Variables.takenPoint=()
        allPointsCanPinable=[]
        for point in Joint.jointdict:
            if point['show'] and point['deleted']==False:
                allPointsCanPinable.append(point['coords'])
        for gridPoint in Variables.gridPoints:
            if gridPoint not in allPointsCanPinable:
                allPointsCanPinable.append(gridPoint)
        for pinnablePoint in allPointsCanPinable:
            geo =self.geometry()
            Variables.width=geo.width()
            Variables.height=geo.height()
            if self.view['3d']:
                x,y,z=self.mouse_project(pinnablePoint[0],pinnablePoint[1],pinnablePoint[2])
                if x>self.xmousePos-Variables.pingrange and x<self.xmousePos+Variables.pingrange and y>self.ymousePos-Variables.pingrange and y<self.ymousePos+Variables.pingrange:
                    if Variables.takenPoint!=pinnablePoint:
                        Variables.takenPoint=pinnablePoint
                        return pinnablePoint
            else:
                if self.view['closed']=='Y':
                    if pinnablePoint[2]==self.view['yaxeloc']:
                        x,y,z=self.mouse_project(pinnablePoint[0],pinnablePoint[1],pinnablePoint[2])
                        if x>self.xmousePos-Variables.pingrange and x<self.xmousePos+Variables.pingrange and y>self.ymousePos-Variables.pingrange and y<self.ymousePos+Variables.pingrange:
                            if Variables.takenPoint!=pinnablePoint:
                                Variables.takenPoint=pinnablePoint
                                return pinnablePoint
                elif self.view['closed']=='X':
                    if pinnablePoint[0]==self.view['xaxeloc']:
                        x,y,z=self.mouse_project(pinnablePoint[0],pinnablePoint[1],pinnablePoint[2])
                        if x>self.xmousePos-Variables.pingrange and x<self.xmousePos+Variables.pingrange and y>self.ymousePos-Variables.pingrange and y<self.ymousePos+Variables.pingrange:
                            if Variables.takenPoint!=pinnablePoint:
                                Variables.takenPoint=pinnablePoint
                                return pinnablePoint
                elif self.view['closed']=='Z':
                    if pinnablePoint[1]==-self.view['zaxeloc']:
                        x,y,z=self.mouse_project(pinnablePoint[0],pinnablePoint[1],pinnablePoint[2])
                        if x>self.xmousePos-Variables.pingrange and x<self.xmousePos+Variables.pingrange and y>self.ymousePos-Variables.pingrange and y<self.ymousePos+Variables.pingrange:
                            if Variables.takenPoint!=pinnablePoint:
                                Variables.takenPoint=pinnablePoint
                                return pinnablePoint

    def drawGrid(self):
        try:
            xbublesize=Variables.xbublesize/10
            zbublesize=Variables.zbublesize/10
            ybublesize=Variables.ybublesize/10
            ybubleLoc=Variables.ybubleLoc
            xbubleLoc=Variables.xbubleLoc
            zbubleLoc=Variables.zbubleLoc
            if xbubleLoc=="End":
                xbubleindex=-1
                xbublesize=xbublesize
            elif xbubleLoc=="Start":
                xbubleindex=0
                xbublesize=xbublesize*-1
            if ybubleLoc=="End":
                ybubleindex=-1
                ybublesize=ybublesize
            elif ybubleLoc=="Start":
                ybubleindex=0
                ybublesize=ybublesize*-1
            if zbubleLoc=="End":
                zbubleindex=-1
                zbublesize=zbublesize
            elif zbubleLoc=="Start":
                zbubleindex=0
                zbublesize=zbublesize*-1

            if self.view['3d']:                
                    
                    gridy1 =Variables.gridy[xbubleindex][1]
                    gridy2 =Variables.gridy[xbubleindex][1]
                    gridx1 =Variables.gridx[ybubleindex][1]
                    gridx2 =Variables.gridx[ybubleindex][1]
                    gridz1=Variables.gridz[0][1]
            else:
                if self.view['closed']=='Z':               
                    gridy1 =Variables.gridy[xbubleindex][1]
                    gridy2 =Variables.gridy[xbubleindex][1]
                    gridx1 =Variables.gridx[ybubleindex][1]
                    gridx2 =Variables.gridx[ybubleindex][1]                
                    gridz1=self.view['zaxeloc']

                if self.view['closed']=='Y':
                    gridy1 =self.view['yaxeloc']
                    gridx1 =Variables.gridx[zbubleindex][1]
                    gridx2 =Variables.gridx[zbubleindex][1]
                    gridz1 =Variables.gridz[xbubleindex][1]
                    gridz2 =Variables.gridz[xbubleindex][1]

                if self.view['closed']=='X':
                    
                    gridy1 = Variables.gridy[zbubleindex][1]
                    gridy2 = Variables.gridy[zbubleindex][1]
                    gridx1 =self.view['xaxeloc']
                    gridz1=Variables.gridz[ybubleindex][1]
                    gridz2=Variables.gridz[ybubleindex][1]

            #uzunlukları toplayarak gitmesi lazım çarparak değil
            Variables.gridPoints.clear()
            if Variables.showgrid:
                glLineWidth(0.5)
                glBegin(GL_LINES)
                gridy=0
                # kırmızı x leri yazdır
                for y in range(len(Variables.gridy)): #1
                    gridz=0
                    gridy = Variables.gridy[y][1]
                    for z in range(len(Variables.gridz)): #1
                        gridx=0
                        gridz = Variables.gridz[z][1]
                        for x in range(len(Variables.gridx)):
                            glColor3ub(Variables.gridcolor[0],Variables.gridcolor[1],Variables.gridcolor[2])
                            gridx = Variables.gridx[x-1][1]
                            glVertex3d(gridx,-gridz,gridy)
                            Variables.gridPoints.append([gridx,-gridz,gridy])
                            gridx = Variables.gridx[x][1]
                            glVertex3d(gridx,-gridz,gridy)
                            Variables.gridPoints.append([gridx,-gridz,gridy])
                                                    
                            if self.view['3d']: #Tamam
                                # balon ve çizgisi için
                                # çizgi
                                glVertex3d(gridx1+10*ybublesize,-gridz1,gridy)                        
                                glVertex3d(gridx2+30*ybublesize,-gridz1,gridy)                            
                                # ilk düz çizgi
                                glVertex3d(gridx1+30*ybublesize,-gridz1,gridy+15*ybublesize)
                                glVertex3d(gridx2+30*ybublesize,-gridz1,gridy-15*ybublesize)
                                # sağ ve sol eğik1
                                glVertex3d(gridx1+30*ybublesize,-gridz1,gridy+15*ybublesize)                        
                                glVertex3d(gridx2+40*ybublesize,-gridz1,gridy+30*ybublesize)
                                
                                glVertex3d(gridx1+30*ybublesize,-gridz1,gridy-15*ybublesize)                        
                                glVertex3d(gridx2+40*ybublesize,-gridz1,gridy-30*ybublesize)                        
                                # sağ ve sol düz
                                glVertex3d(gridx1+40*ybublesize,-gridz1,gridy+30*ybublesize)                        
                                glVertex3d(gridx2+80*ybublesize,-gridz1,gridy+30*ybublesize)                            
                                glVertex3d(gridx1+40*ybublesize,-gridz1,gridy-30*ybublesize)                        
                                glVertex3d(gridx2+80*ybublesize,-gridz1,gridy-30*ybublesize)
                                # sağ ve sol eğik 2                        
                                glVertex3d(gridx1+80*ybublesize,-gridz1,gridy+30*ybublesize)                        
                                glVertex3d(gridx2+90*ybublesize,-gridz1,gridy+15*ybublesize)
                                glVertex3d(gridx1+80*ybublesize,-gridz1,gridy-30*ybublesize)
                                glVertex3d(gridx2+90*ybublesize,-gridz1,gridy-15*ybublesize)
                                # son düz çizgi
                                glVertex3d(gridx1+90*ybublesize,-gridz1,gridy+15*ybublesize)
                                glVertex3d(gridx2+90*ybublesize,-gridz1,gridy-15*ybublesize)                            
                            else:
                                if self.view['closed']=='Z': # tamam
                                    # balon ve çizgisi için
                                    # çizgi
                                    glVertex3d(gridx1+10*ybublesize,-gridz1,gridy)                        
                                    glVertex3d(gridx2+30*ybublesize,-gridz1,gridy)                                
                                    # ilk düz çizgi
                                    glVertex3d(gridx1+30*ybublesize,-gridz1,gridy+15*ybublesize)
                                    glVertex3d(gridx2+30*ybublesize,-gridz1,gridy-15*ybublesize)
                                    # sağ ve sol eğik1                        
                                    glVertex3d(gridx1+30*ybublesize,-gridz1,gridy+15*ybublesize)                        
                                    glVertex3d(gridx2+40*ybublesize,-gridz1,gridy+30*ybublesize)                                
                                    glVertex3d(gridx1+30*ybublesize,-gridz1,gridy-15*ybublesize)                        
                                    glVertex3d(gridx2+40*ybublesize,-gridz1,gridy-30*ybublesize)                            
                                    # sağ ve sol düz                        
                                    glVertex3d(gridx1+40*ybublesize,-gridz1,gridy+30*ybublesize)                        
                                    glVertex3d(gridx2+80*ybublesize,-gridz1,gridy+30*ybublesize)                                
                                    glVertex3d(gridx1+40*ybublesize,-gridz1,gridy-30*ybublesize)                        
                                    glVertex3d(gridx2+80*ybublesize,-gridz1,gridy-30*ybublesize)
                                    # sağ ve sol eğik 2                        
                                    glVertex3d(gridx1+80*ybublesize,-gridz1,gridy+30*ybublesize)                        
                                    glVertex3d(gridx2+90*ybublesize,-gridz1,gridy+15*ybublesize)
                                    glVertex3d(gridx1+80*ybublesize,-gridz1,gridy-30*ybublesize)
                                    glVertex3d(gridx2+90*ybublesize,-gridz1,gridy-15*ybublesize)
                                    # son düz çizgi
                                    glVertex3d(gridx1+90*ybublesize,-gridz1,gridy+15*ybublesize)
                                    glVertex3d(gridx2+90*ybublesize,-gridz1,gridy-15*ybublesize)
                                if self.view['closed']=='Y':
                                    # balon ve çizgisi için
                                    # çizgi
                                    glVertex3d(gridx1+10*zbublesize,-gridz,gridy1)                        
                                    glVertex3d(gridx2+30*zbublesize,-gridz,gridy1)
                                    # ilk düz çizgi
                                    glVertex3d(gridx1+30*zbublesize,-gridz+15*zbublesize,gridy1)
                                    glVertex3d(gridx2+30*zbublesize,-gridz-15*zbublesize,gridy1)
                                    # sağ ve sol eğik1                        
                                    glVertex3d(gridx1+30*zbublesize,-gridz+15*zbublesize,gridy1)                        
                                    glVertex3d(gridx2+40*zbublesize,-gridz+30*zbublesize,gridy1)                                
                                    glVertex3d(gridx1+30*zbublesize,-gridz-15*zbublesize,gridy1)                        
                                    glVertex3d(gridx2+40*zbublesize,-gridz-30*zbublesize,gridy1)                            
                                    # sağ ve sol düz                        
                                    glVertex3d(gridx1+40*zbublesize,-gridz+30*zbublesize,gridy1)                        
                                    glVertex3d(gridx2+80*zbublesize,-gridz+30*zbublesize,gridy1)                                
                                    glVertex3d(gridx1+40*zbublesize,-gridz-30*zbublesize,gridy1)                        
                                    glVertex3d(gridx2+80*zbublesize,-gridz-30*zbublesize,gridy1)
                                    # sağ ve sol eğik 2                        
                                    glVertex3d(gridx1+80*zbublesize,-gridz+30*zbublesize,gridy1)                        
                                    glVertex3d(gridx2+90*zbublesize,-gridz+15*zbublesize,gridy1)
                                    glVertex3d(gridx1+80*zbublesize,-gridz-30*zbublesize,gridy1)
                                    glVertex3d(gridx2+90*zbublesize,-gridz-15*zbublesize,gridy1)
                                    # son düz çizgi
                                    glVertex3d(gridx1+90*zbublesize,-gridz+15*zbublesize,gridy1)
                                    glVertex3d(gridx2+90*zbublesize,-gridz-15*zbublesize,gridy1)
                
                gridy =0
                for y in range(len(Variables.gridy)): #1
                    gridx =0
                    gridy = Variables.gridy[y][1]
                    for x in range(len(Variables.gridx)): #1
                        gridz=0
                        gridx = Variables.gridx[x][1]
                        for z in range(len(Variables.gridz)):
                            glColor3ub(Variables.gridcolor[0],Variables.gridcolor[1],Variables.gridcolor[2])
                            gridz = Variables.gridz[z-1][1]
                            glVertex3d(gridx,-gridz,gridy)
                            gridz = Variables.gridz[z][1]
                            glVertex3d(gridx,-gridz,gridy)
                            Variables.gridPoints.append([gridx,-gridz,gridy])

                            
                            if self.view['3d']==False:
                                
                                if self.view['closed']=='X':
                                    # balon ve çizgisi için
                                    # çizgi
                                    ybublesize=ybublesize*-1
                                    glVertex3d(gridx1,-gridz1+10*ybublesize,gridy)                        
                                    glVertex3d(gridx1,-gridz2+30*ybublesize,gridy)                        
                                    # ilk düz çizgi                                
                                    glVertex3d(gridx1,-gridz1+30*ybublesize,gridy+15*ybublesize)
                                    glVertex3d(gridx1,-gridz2+30*ybublesize,gridy-15*ybublesize)
                                    # sağ ve sol eğik1                                
                                    glVertex3d(gridx1,-gridz1+30*ybublesize,gridy+15*ybublesize)                        
                                    glVertex3d(gridx1,-gridz2+40*ybublesize,gridy+30*ybublesize)                                
                                    glVertex3d(gridx1,-gridz1+30*ybublesize,gridy-15*ybublesize)                        
                                    glVertex3d(gridx1,-gridz2+40*ybublesize,gridy-30*ybublesize) 
                                    # sağ ve sol düz
                                    glVertex3d(gridx1,-gridz1+40*ybublesize,gridy+30*ybublesize)                        
                                    glVertex3d(gridx1,-gridz2+80*ybublesize,gridy+30*ybublesize)
                                    glVertex3d(gridx1,-gridz1+40*ybublesize,gridy-30*ybublesize)                        
                                    glVertex3d(gridx1,-gridz2+80*ybublesize,gridy-30*ybublesize)
                                    # sağ ve sol eğik 2                                
                                    glVertex3d(gridx1,-gridz1+80*ybublesize,gridy+30*ybublesize)                        
                                    glVertex3d(gridx1,-gridz2+90*ybublesize,gridy+15*ybublesize)
                                    glVertex3d(gridx1,-gridz1+80*ybublesize,gridy-30*ybublesize)
                                    glVertex3d(gridx1,-gridz2+90*ybublesize,gridy-15*ybublesize)
                                    # son düz çizgi                                
                                    glVertex3d(gridx1,-gridz1+90*ybublesize,gridy+15*ybublesize)
                                    glVertex3d(gridx1,-gridz2+90*ybublesize,gridy-15*ybublesize)
                                    ybublesize=ybublesize*-1
                                if self.view['closed']=='Y':
                                    # balon ve çizgisi için
                                    # çizgi
                                    xbublesize=xbublesize*-1
                                    glVertex3d(gridx,-gridz1+10*xbublesize,gridy1)                        
                                    glVertex3d(gridx,-gridz2+30*xbublesize,gridy1)
                                    # ilk düz çizgi                                
                                    glVertex3d(gridx+15*xbublesize,-gridz1+30*xbublesize,gridy1)
                                    glVertex3d(gridx-15*xbublesize,-gridz2+30*xbublesize,gridy1)
                                    # sağ ve sol eğik1                                
                                    glVertex3d(gridx+15*xbublesize,-gridz1+30*xbublesize,gridy1)                        
                                    glVertex3d(gridx+30*xbublesize,-gridz2+40*xbublesize,gridy1)
                                    glVertex3d(gridx-15*xbublesize,-gridz1+30*xbublesize,gridy1)                        
                                    glVertex3d(gridx-30*xbublesize,-gridz2+40*xbublesize,gridy1)
                                    # sağ ve sol düz                                
                                    glVertex3d(gridx+30*xbublesize,-gridz1+40*xbublesize,gridy1)                        
                                    glVertex3d(gridx+30*xbublesize,-gridz2+80*xbublesize,gridy1)
                                    glVertex3d(gridx-30*xbublesize,-gridz1+40*xbublesize,gridy1)                        
                                    glVertex3d(gridx-30*xbublesize,-gridz2+80*xbublesize,gridy1)
                                    # sağ ve sol eğik 2                                
                                    glVertex3d(gridx+30*xbublesize,-gridz1+80*xbublesize,gridy1)                        
                                    glVertex3d(gridx+15*xbublesize,-gridz2+90*xbublesize,gridy1)
                                    glVertex3d(gridx-30*xbublesize,-gridz1+80*xbublesize,gridy1)
                                    glVertex3d(gridx-15*xbublesize,-gridz2+90*xbublesize,gridy1)
                                    # son düz çizgi
                                    glVertex3d(gridx+15*xbublesize,-gridz1+90*xbublesize,gridy1)
                                    glVertex3d(gridx-15*xbublesize,-gridz2+90*xbublesize,gridy1)
                                    xbublesize=xbublesize*-1

                
                gridz =0
                # mavi Y leri yazdır
                for z in range(len(Variables.gridz)): #1
                    gridx =0
                    gridz = Variables.gridz[z][1]
                    for x in range(len(Variables.gridx)): #1
                        gridy=0
                        gridx = Variables.gridx[x][1]
                        for y in range(len(Variables.gridy)):
                            glColor3ub(Variables.gridcolor[0],Variables.gridcolor[1],Variables.gridcolor[2])
                            gridy =Variables.gridy[y-1][1]
                            glVertex3d(gridx,-gridz,gridy)
                            gridy = Variables.gridy[y][1]
                            glVertex3d(gridx,-gridz,gridy)
                            Variables.gridPoints.append([gridx,-gridz,gridy])
                            
                            if self.view['3d']: #tamam
                                
                                # balon ve çizgisi için
                                # çizgi
                                glVertex3d(gridx,-gridz1,gridy1+10*xbublesize)                        
                                glVertex3d(gridx,-gridz1,gridy2+30*xbublesize)
                                # ilk düz çizgi
                                glVertex3d(gridx+15*xbublesize,-gridz1,gridy1+30*xbublesize)
                                glVertex3d(gridx-15*xbublesize,-gridz1,gridy2+30*xbublesize)
                                # sağ ve sol eğik1
                                glVertex3d(gridx+15*xbublesize,-gridz1,gridy1+30*xbublesize)                        
                                glVertex3d(gridx+30*xbublesize,-gridz1,gridy2+40*xbublesize)
                                glVertex3d(gridx-15*xbublesize,-gridz1,gridy1+30*xbublesize)                        
                                glVertex3d(gridx-30*xbublesize,-gridz1,gridy2+40*xbublesize)                       
                                # sağ ve sol düz
                                glVertex3d(gridx+30*xbublesize,-gridz1,gridy1+40*xbublesize)                        
                                glVertex3d(gridx+30*xbublesize,-gridz1,gridy2+80*xbublesize)
                                glVertex3d(gridx-30*xbublesize,-gridz1,gridy1+40*xbublesize)                        
                                glVertex3d(gridx-30*xbublesize,-gridz1,gridy2+80*xbublesize)
                                # sağ ve sol eğik 2
                                glVertex3d(gridx+30*xbublesize,-gridz1,gridy1+80*xbublesize)                        
                                glVertex3d(gridx+15*xbublesize,-gridz1,gridy2+90*xbublesize)
                                glVertex3d(gridx-30*xbublesize,-gridz1,gridy1+80*xbublesize)
                                glVertex3d(gridx-15*xbublesize,-gridz1,gridy2+90*xbublesize)
                                # son düz çizgi
                                glVertex3d(gridx+15*xbublesize,-gridz1,gridy1+90*xbublesize)
                                glVertex3d(gridx-15*xbublesize,-gridz1,gridy2+90*xbublesize)
                            else:
                                if self.view['closed']=='Z': # tamam
                                    # balon ve çizgisi için
                                    # çizgi                        
                                    glVertex3d(gridx,-gridz1,gridy1+10*xbublesize)                        
                                    glVertex3d(gridx,-gridz1,gridy2+30*xbublesize)                        
                                    # ilk düz çizgi
                                    glVertex3d(gridx+15*xbublesize,-gridz1,gridy1+30*xbublesize)
                                    glVertex3d(gridx-15*xbublesize,-gridz1,gridy2+30*xbublesize)
                                    # sağ ve sol eğik1
                                    glVertex3d(gridx+15*xbublesize,-gridz1,gridy1+30*xbublesize)                        
                                    glVertex3d(gridx+30*xbublesize,-gridz1,gridy2+40*xbublesize)
                                    glVertex3d(gridx-15*xbublesize,-gridz1,gridy1+30*xbublesize)                        
                                    glVertex3d(gridx-30*xbublesize,-gridz1,gridy2+40*xbublesize)                       
                                    # sağ ve sol düz
                                    glVertex3d(gridx+30*xbublesize,-gridz1,gridy1+40*xbublesize)                        
                                    glVertex3d(gridx+30*xbublesize,-gridz1,gridy2+80*xbublesize)
                                    glVertex3d(gridx-30*xbublesize,-gridz1,gridy1+40*xbublesize)                        
                                    glVertex3d(gridx-30*xbublesize,-gridz1,gridy2+80*xbublesize)
                                    # sağ ve sol eğik 2
                                    glVertex3d(gridx+30*xbublesize,-gridz1,gridy1+80*xbublesize)                        
                                    glVertex3d(gridx+15*xbublesize,-gridz1,gridy2+90*xbublesize)
                                    glVertex3d(gridx-30*xbublesize,-gridz1,gridy1+80*xbublesize)
                                    glVertex3d(gridx-15*xbublesize,-gridz1,gridy2+90*xbublesize)
                                    # son düz çizgi
                                    glVertex3d(gridx+15*xbublesize,-gridz1,gridy1+90*xbublesize)
                                    glVertex3d(gridx-15*xbublesize,-gridz1,gridy2+90*xbublesize)
                                if self.view['closed']=='X':
                                    # balon ve çizgisi için
                                    # çizgi
                                    glVertex3d(gridx1,-gridz,gridy1+10*zbublesize)                        
                                    glVertex3d(gridx1,-gridz,gridy2+30*zbublesize)                        
                                    # ilk düz çizgi
                                    glVertex3d(gridx1,-gridz+15*zbublesize,gridy1+30*zbublesize)
                                    glVertex3d(gridx1,-gridz-15*zbublesize,gridy2+30*zbublesize)
                                    # sağ ve sol eğik1
                                    glVertex3d(gridx1,-gridz+15*zbublesize,gridy1+30*zbublesize)                        
                                    glVertex3d(gridx1,-gridz+30*zbublesize,gridy2+40*zbublesize)
                                    glVertex3d(gridx1,-gridz-15*zbublesize,gridy1+30*zbublesize)                        
                                    glVertex3d(gridx1,-gridz-30*zbublesize,gridy2+40*zbublesize)                       
                                    # sağ ve sol düz
                                    glVertex3d(gridx1,-gridz+30*zbublesize,gridy1+40*zbublesize)                        
                                    glVertex3d(gridx1,-gridz+30*zbublesize,gridy2+80*zbublesize)
                                    glVertex3d(gridx1,-gridz-30*zbublesize,gridy1+40*zbublesize)                        
                                    glVertex3d(gridx1,-gridz-30*zbublesize,gridy2+80*zbublesize)
                                    # sağ ve sol eğik 2
                                    glVertex3d(gridx1,-gridz+30*zbublesize,gridy1+80*zbublesize)                        
                                    glVertex3d(gridx1,-gridz+15*zbublesize,gridy2+90*zbublesize)
                                    glVertex3d(gridx1,-gridz-30*zbublesize,gridy1+80*zbublesize)
                                    glVertex3d(gridx1,-gridz-15*zbublesize,gridy2+90*zbublesize)
                                    # son düz çizgi
                                    glVertex3d(gridx1,-gridz+15*zbublesize,gridy1+90*zbublesize)
                                    glVertex3d(gridx1,-gridz-15*zbublesize,gridy2+90*zbublesize)

                glEnd()
        except Exception as e:
            logging.debug(e)
            logging.info("Opengl drawgrid Crashed")
    
    def drawGridText(self):
        try:
            number1=15
            number2=30
            glutInit(sys.argv)
            font = GLUT_STROKE_MONO_ROMAN
            glLineWidth(Variables.bubletextwidth)
            glColor3ub(Variables.bubletextcolor[0],Variables.bubletextcolor[1],Variables.bubletextcolor[2])
            xbublesize=Variables.xbublesize/10
            zbublesize=Variables.zbublesize/10
            ybublesize=Variables.ybublesize/10
            ybubleLoc=Variables.ybubleLoc
            xbubleLoc=Variables.xbubleLoc
            zbubleLoc=Variables.zbubleLoc
            if xbubleLoc=="End":
                xbubleindex=-1
                xbublesize=xbublesize
            elif xbubleLoc=="Start":
                xbubleindex=0
                xbublesize=xbublesize*-1
            if ybubleLoc=="End":
                ybubleindex=-1
                ybublesize=ybublesize
            elif ybubleLoc=="Start":
                ybubleindex=0
                ybublesize=ybublesize*-1
            if zbubleLoc=="End":
                zbubleindex=-1
                zbublesize=zbublesize
            elif zbubleLoc=="Start":
                zbubleindex=0
                zbublesize=zbublesize*-1

            if self.view['3d']:
                    gridy1 =Variables.gridy[xbubleindex][1]                
                    gridx1 =Variables.gridx[ybubleindex][1]                
                    gridz1=Variables.gridz[0][1]
            else:
                if self.view['closed']=='Z':               
                    gridy1 =Variables.gridy[xbubleindex][1]                
                    gridx1 =Variables.gridx[ybubleindex][1]                                
                    gridz1=self.view['zaxeloc']

                if self.view['closed']=='Y':
                    gridy1 =self.view['yaxeloc']
                    gridx1 =Variables.gridx[zbubleindex][1]                
                    gridz1 =Variables.gridz[xbubleindex][1]               

                if self.view['closed']=='X':
                    
                    gridy1 = Variables.gridy[zbubleindex][1]                
                    gridx1 =self.view['xaxeloc']
                    gridz1=Variables.gridz[ybubleindex][1]
            
            if Variables.showgrid:            
                gridy=0
                # kırmızı x leri yazdır
                for y in range(len(Variables.gridy)): #1
                    gridz=0
                    gridy = Variables.gridy[y][1]
                    for z in range(len(Variables.gridz)): #1
                            gridz = Variables.gridz[z][1]                    
                            labely=Variables.gridy[y][0]                        
                            labelz=Variables.gridz[z][0]
                            if self.view['3d']: #Tamam
                                text=str(labely)
                                glPushMatrix()
                                                        
                                if len(text)>1:
                                    glTranslate(gridx1+45*ybublesize,-gridz1,gridy+number2*ybublesize)                                
                                    glScale((1/3.5)*ybublesize,(1/3.5)*ybublesize,(1/3.5)*ybublesize)
                                else:
                                    glTranslate(gridx1+45*ybublesize,-gridz1,gridy+number1*ybublesize)
                                    glScale((1/3)*ybublesize,(1/3)*ybublesize,(1/3)*ybublesize)
                                glRotatef(90,1,0,0)
                                glRotatef(-90,0,0,1)
                                
                                glutStrokeString(font,str.encode(text))                            
                                glPopMatrix()                            
                            else:
                                if self.view['closed']=='Z':
                                    text=str(labely) 
                                    glPushMatrix()
                                    if len(text)>1:
                                        
                                        glTranslate(gridx1+45*ybublesize,-gridz1,gridy+number2*ybublesize)
                                        glScale((1/3.5)*ybublesize,(1/3.5)*ybublesize,(1/3.5)*ybublesize)
                                    else:
                                        glTranslate(gridx1+45*ybublesize,-gridz1,gridy+number1*ybublesize)
                                        glScale((1/3)*ybublesize,(1/3)*ybublesize,(1/3)*ybublesize)
                                    glRotatef(90,1,0,0)
                                    glRotatef(-90,0,0,1)
                                    
                                    
                                    glutStrokeString(font,str.encode(text))                                    
                                    glPopMatrix()
                                if self.view['closed']=='Y':
                                    text=str(labelz)
                                    glPushMatrix()
                                    if len(text)>1:
                                        glTranslate(gridx1+45*zbublesize,-gridz-number2*zbublesize,gridy1)
                                        glScale((1/3.5)*zbublesize,(1/3.5)*zbublesize,(1/3.5)*zbublesize)
                                    else:
                                        glTranslate(gridx1+45*zbublesize,-gridz-number1*zbublesize,gridy1)
                                        glScale((1/3)*zbublesize,(1/3)*zbublesize,(1/3)*zbublesize)                               
                                                                
                                    glRotatef(180,1,0,0)
                                    glRotatef(0,0,1,0)
                                    glRotatef(-90,0,0,1)
                                                                                            
                                    
                                    glutStrokeString(font,str.encode(text))                                    
                                    glPopMatrix()
                
                gridy =0
                for y in range(len(Variables.gridy)): #1
                    gridx =0
                    gridy = Variables.gridy[y][1]
                    for x in range(len(Variables.gridx)): #1
                            gridx = Variables.gridx[x][1]                    
                            if self.view['3d']==False:                            
                                if self.view['closed']=='X':
                                    labely=Variables.gridy[y][0]
                                    text=str(labely)
                                    glPushMatrix()
                                    if len(text)>1:
                                        glTranslate(gridx1,-gridz1-45*ybublesize,gridy-number2*ybublesize)
                                        glScale((1/3.5)*ybublesize,(1/3.5)*ybublesize,(1/3.5)*ybublesize)
                                    else:
                                        glTranslate(gridx1,-gridz1-45*ybublesize,gridy-number1*ybublesize)
                                        glScale((1/3)*ybublesize,(1/3)*ybublesize,(1/3)*ybublesize)
                                    glRotatef(180,1,0,0)
                                    glRotatef(90,0,1,0)
                                    
                                    
                                    glutStrokeString(font,str.encode(text))                                    
                                    glPopMatrix()
                                if self.view['closed']=='Y':
                                    labelx=Variables.gridx[x][0]
                                    text=str(labelx)
                                    glPushMatrix()
                                    if len(text)>1:
                                        glTranslate(gridx-number2*xbublesize,-gridz1-45*xbublesize,gridy1)
                                        glScale((1/3.5)*xbublesize,(1/3.5)*xbublesize,(1/3.5)*xbublesize)
                                    else:
                                        glTranslate(gridx-number1*xbublesize,-gridz1-45*xbublesize,gridy1)
                                        glScale((1/3)*xbublesize,(1/3)*xbublesize,(1/3)*xbublesize)                                
                                    glRotatef(180,1,0,0)
                                    glRotatef(0,0,1,0)
                                    glRotatef(0,0,0,1)
                                                                                            
                                    
                                    glutStrokeString(font,str.encode(text))                                   
                                    glPopMatrix()  
                
                gridz =0
                # mavi Y leri yazdır
                for z in range(len(Variables.gridz)): #1
                    gridx =0
                    gridz = Variables.gridz[z][1]
                    for x in range(len(Variables.gridx)): #1                    
                            gridx = Variables.gridx[x][1] 
                            if self.view['3d']:
                                labelx=Variables.gridx[x][0]
                                text=str(labelx)
                                glPushMatrix()
                                if len(text)>1:
                                    glTranslate(gridx-number2*xbublesize,-gridz1,gridy1+45*xbublesize)
                                    glScale((1/3.5)*xbublesize,(1/3.5)*xbublesize,(1/3.5)*xbublesize)
                                else:
                                    glTranslate(gridx-number1*xbublesize,-gridz1,gridy1+45*xbublesize)
                                    glScale((1/3)*xbublesize,(1/3)*xbublesize,(1/3)*xbublesize)
                                glRotatef(90,1,0,0)
                                #glRotatef(-90,0,0,1)
                                
                                
                                glutStrokeString(font,str.encode(text))                              
                                glPopMatrix() 
                            else:
                                if self.view['closed']=='Z':
                                    labelx=Variables.gridx[x][0]
                                    text=str(labelx)
                                    glPushMatrix()
                                    if len(text)>1:
                                        glTranslate(gridx-number2*xbublesize,-gridz1,gridy1+45*xbublesize)
                                        glScale((1/3.5)*xbublesize,(1/3.5)*xbublesize,(1/3.5)*xbublesize)
                                    else:
                                        glTranslate(gridx-number1*xbublesize,-gridz1,gridy1+40*xbublesize)
                                        glScale((1/3)*xbublesize,(1/3)*xbublesize,(1/3)*xbublesize)
                                    glRotatef(90,1,0,0)
                                    #glRotatef(-90,0,0,1)
                                                                                            
                                    
                                    glutStrokeString(font,str.encode(text))                                    
                                    glPopMatrix()                                
                                if self.view['closed']=='X':
                                    labelz=Variables.gridz[z][0]
                                    text=str(labelz)
                                    glPushMatrix()
                                    if len(text)>1:                                    
                                        glTranslate(gridx1,-gridz-number2*zbublesize,gridy1+45*zbublesize)
                                        glScale((1/3.5)*zbublesize,(1/3.5)*zbublesize,(1/3.5)*zbublesize)
                                    else:
                                        glTranslate(gridx1,-gridz-number1*zbublesize,gridy1+45*zbublesize)
                                        glScale((1/3)*zbublesize,(1/3)*zbublesize,(1/3)*zbublesize)
                                    glRotatef(90,1,0,0)
                                    glRotatef(90,0,1,0)
                                    
                                    
                                    glutStrokeString(font,str.encode(text))
                                    glPopMatrix()
        except Exception as e:
            logging.debug(e)
            logging.info("Opengl drawgridtext Crashed")
    
    def drawOrgin(self):
        try:
            if self.view['3d']:
                if Variables.showorgin:
                    glLineWidth(2)
                    glBegin(GL_LINES)
                    glColor3ub(0,0,250)
                    glVertex3d(0,0,0)
                    glVertex3d(40/self.scale,0,0)
                    glEnd()
                    x1,y1,z1=self.mouse_project(40/self.scale,0,0)
                    qp = QPainter(self)
                    qp.beginNativePainting()
                    qp.endNativePainting()
                    qp.setRenderHint(QPainter.Antialiasing)
                    qp.setPen(QColor(0,0,250))
                    qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                    qp.translate(x1,y1)
                    qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, "X")
                    qp.end()

                    glBegin(GL_TRIANGLES)
                    glColor3ub(0,0,250)
                    glVertex3d(40/self.scale,0,0)
                    glVertex3d(30/self.scale,10/self.scale,0)
                    glVertex3d(30/self.scale,-10/self.scale,0)

                    glVertex3d(40/self.scale,0,0)
                    glVertex3d(30/self.scale,0,10/self.scale)
                    glVertex3d(30/self.scale,0,-10/self.scale)
                    glEnd()

                    glBegin(GL_LINES)
                    glColor3ub(250,0,250)
                    glVertex3d(0,0,0)
                    glVertex3d(0,-40/self.scale,0)
                    glEnd()
                    x1,y1,z1=self.mouse_project(0,-40/self.scale,0)
                    qp = QPainter(self)
                    qp.beginNativePainting()
                    qp.endNativePainting()
                    qp.setRenderHint(QPainter.Antialiasing)
                    qp.setPen(QColor(250,0,250))
                    qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                    qp.translate(x1,y1)
                    qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, "Z")
                    qp.end()

                    glBegin(GL_TRIANGLES)
                    glColor3ub(250,0,250)
                    glVertex3d(0,-40/self.scale,0)
                    glVertex3d(10/self.scale,-30/self.scale,0)
                    glVertex3d(-10/self.scale,-30/self.scale,0)

                    glVertex3d(0,-40/self.scale,0)
                    glVertex3d(0,-30/self.scale,10/self.scale)
                    glVertex3d(0,-30/self.scale,-10/self.scale)
                    glEnd()

                    glBegin(GL_LINES)
                    glColor3ub(0,250,0)
                    glVertex3d(0,0,0)
                    glVertex3d(0,0,40/self.scale)
                    glEnd()
                    x1,y1,z1=self.mouse_project(0,0,40/self.scale)
                    qp = QPainter(self)
                    qp.beginNativePainting()
                    qp.endNativePainting()
                    qp.setRenderHint(QPainter.Antialiasing)
                    qp.setPen(QColor(0,250,0))
                    qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                    qp.translate(x1,y1)
                    qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, "Y")
                    qp.end()

                    glBegin(GL_TRIANGLES)
                    glColor3ub(0,250,0)
                    glVertex3d(0,0,40/self.scale)
                    glVertex3d(0,10/self.scale,30/self.scale)
                    glVertex3d(0,-10/self.scale,30/self.scale)

                    glVertex3d(0,0,40/self.scale)
                    glVertex3d(10/self.scale,0,30/self.scale)
                    glVertex3d(-10/self.scale,0,30/self.scale)

                    glEnd()
            else:
                if self.view['closed']=='Y':
                    if Variables.showorgin:
                        if Variables.showorgin:
                            glLineWidth(3)
                            glBegin(GL_LINES)
                            glColor3ub(0,0,250)
                            glVertex3d(0,0,self.view['yaxeloc'])
                            glVertex3d(40/self.scale,0,self.view['yaxeloc'])
                            glEnd()
                            x1,y1,z1=self.mouse_project(40/self.scale,0,self.view['yaxeloc'])
                            qp = QPainter(self)
                            qp.beginNativePainting()
                            qp.endNativePainting()
                            qp.setRenderHint(QPainter.Antialiasing)
                            qp.setPen(QColor(0,0,250))
                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                            qp.translate(x1,y1)
                            qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, "X")
                            qp.end()

                            glBegin(GL_TRIANGLES)
                            glColor3ub(0,0,250)
                            glVertex3d(40/self.scale,0,self.view['yaxeloc'])
                            glVertex3d(30/self.scale,10/self.scale,self.view['yaxeloc'])
                            glVertex3d(30/self.scale,-10/self.scale,self.view['yaxeloc'])

                            glVertex3d(40/self.scale,0,self.view['yaxeloc'])
                            glVertex3d(30/self.scale,0,self.view['yaxeloc']+10/self.scale)
                            glVertex3d(30/self.scale,0,self.view['yaxeloc']-10/self.scale)
                            glEnd()

                            glBegin(GL_LINES)
                            glColor3ub(250,0,250)
                            glVertex3d(0,0,self.view['yaxeloc'])
                            glVertex3d(0,-40/self.scale,self.view['yaxeloc'])
                            glEnd()
                            x1,y1,z1=self.mouse_project(0,-40/self.scale,self.view['yaxeloc'])
                            qp = QPainter(self)
                            qp.beginNativePainting()
                            qp.endNativePainting()
                            qp.setRenderHint(QPainter.Antialiasing)
                            qp.setPen(QColor(250,0,250))
                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                            qp.translate(x1,y1)
                            qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, "Z")
                            qp.end()

                            glBegin(GL_TRIANGLES)
                            glColor3ub(250,0,250)
                            glVertex3d(0,-40/self.scale,self.view['yaxeloc'])
                            glVertex3d(10/self.scale,-30/self.scale,self.view['yaxeloc'])
                            glVertex3d(-10/self.scale,-30/self.scale,self.view['yaxeloc'])

                            glVertex3d(0,-40/self.scale,self.view['yaxeloc'])
                            glVertex3d(0,-30/self.scale,self.view['yaxeloc']+10/self.scale)
                            glVertex3d(0,-30/self.scale,self.view['yaxeloc']-10/self.scale)
                            glEnd()
                elif self.view['closed']=='X':
                    if Variables.showorgin:

                            glBegin(GL_LINES)
                            glColor3ub(250,0,250)
                            glVertex3d(self.view['xaxeloc'],0,0)
                            glVertex3d(self.view['xaxeloc'],-40/self.scale,0)
                            glEnd()
                            x1,y1,z1=self.mouse_project(self.view['xaxeloc'],-40/self.scale,0)
                            qp = QPainter(self)
                            qp.beginNativePainting()
                            qp.endNativePainting()
                            qp.setRenderHint(QPainter.Antialiasing)
                            qp.setPen(QColor(250,0,250))
                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                            qp.translate(x1,y1)
                            qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, "Z")
                            qp.end()

                            glBegin(GL_TRIANGLES)
                            glColor3ub(250,0,250)
                            glVertex3d(self.view['xaxeloc'],-40/self.scale,0)
                            glVertex3d(self.view['xaxeloc']+10/self.scale,-30/self.scale,0)
                            glVertex3d(self.view['xaxeloc']-10/self.scale,-30/self.scale,0)

                            glVertex3d(self.view['xaxeloc'],-40/self.scale,0)
                            glVertex3d(self.view['xaxeloc'],-30/self.scale,10/self.scale)
                            glVertex3d(self.view['xaxeloc'],-30/self.scale,-10/self.scale)
                            glEnd()

                            glBegin(GL_LINES)
                            glColor3ub(0,250,0)
                            glVertex3d(self.view['xaxeloc'],0,0)
                            glVertex3d(self.view['xaxeloc'],0,40/self.scale)
                            glEnd()
                            x1,y1,z1=self.mouse_project(self.view['xaxeloc'],0,40/self.scale)
                            qp = QPainter(self)
                            qp.beginNativePainting()
                            qp.endNativePainting()
                            qp.setRenderHint(QPainter.Antialiasing)
                            qp.setPen(QColor(0,250,0))
                            qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                            qp.translate(x1,y1)
                            qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, "Y")
                            qp.end()

                            glBegin(GL_TRIANGLES)
                            glColor3ub(0,250,0)
                            glVertex3d(self.view['xaxeloc'],0,40/self.scale)
                            glVertex3d(self.view['xaxeloc'],10/self.scale,30/self.scale)
                            glVertex3d(self.view['xaxeloc'],-10/self.scale,30/self.scale)

                            glVertex3d(self.view['xaxeloc'],0,40/self.scale)
                            glVertex3d(self.view['xaxeloc']+10/self.scale,0,30/self.scale)
                            glVertex3d(self.view['xaxeloc']-10/self.scale,0,30/self.scale)

                            glEnd()
                elif self.view['closed']=='Z':
                    if Variables.showorgin:
                        glLineWidth(3)
                        glBegin(GL_LINES)
                        glColor3ub(0,0,250)
                        glVertex3d(0,-self.view['zaxeloc'],0)
                        glVertex3d(40/self.scale,-self.view['zaxeloc'],0)
                        glEnd()
                        x1,y1,z1=self.mouse_project(40/self.scale,-self.view['zaxeloc'],0)
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QColor(0,0,250))
                        qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                        qp.translate(x1,y1)
                        qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, "X")
                        qp.end()

                        glBegin(GL_TRIANGLES)
                        glColor3ub(0,0,250)
                        glVertex3d(40/self.scale,-self.view['zaxeloc'],0)
                        glVertex3d(30/self.scale,-self.view['zaxeloc']+10/self.scale,0)
                        glVertex3d(30/self.scale,-self.view['zaxeloc']-10/self.scale,0)

                        glVertex3d(40/self.scale,-self.view['zaxeloc'],0)
                        glVertex3d(30/self.scale,-self.view['zaxeloc'],10/self.scale)
                        glVertex3d(30/self.scale,-self.view['zaxeloc'],-10/self.scale)
                        glEnd()

                        glBegin(GL_LINES)
                        glColor3ub(0,250,0)
                        glVertex3d(0,-self.view['zaxeloc'],0)
                        glVertex3d(0,-self.view['zaxeloc'],40/self.scale)
                        glEnd()
                        x1,y1,z1=self.mouse_project(0,-self.view['zaxeloc'],40/self.scale)
                        qp = QPainter(self)
                        qp.beginNativePainting()
                        qp.endNativePainting()
                        qp.setRenderHint(QPainter.Antialiasing)
                        qp.setPen(QColor(0,250,0))
                        qp.setFont(QFont(Variables.textfont[0],Variables.textfont[1]))
                        qp.translate(x1,y1)
                        qp.drawText(0,-(Variables.textfont[1]*2),1000,(Variables.textfont[1]*2),0, "Y")
                        qp.end()

                        glBegin(GL_TRIANGLES)
                        glColor3ub(0,250,0)
                        glVertex3d(0,-self.view['zaxeloc'],40/self.scale)
                        glVertex3d(0,-self.view['zaxeloc']+10/self.scale,30/self.scale)
                        glVertex3d(0,-self.view['zaxeloc']-10/self.scale,30/self.scale)

                        glVertex3d(0,-self.view['zaxeloc'],40/self.scale)
                        glVertex3d(10/self.scale,-self.view['zaxeloc'],30/self.scale)
                        glVertex3d(-10/self.scale,-self.view['zaxeloc'],30/self.scale)

                        glEnd()
        except Exception as e:
            logging.debug(e)
            logging.info("Opengl draworigin Crashed")
    @staticmethod
    def selectionClear():
        if Variables.selectedFrames!=[]:
            Variables.pselectedFrames.clear()                    
            for selectf in Variables.selectedFrames:
                Variables.pselectedFrames.append(selectf)            
            Variables.selectedFrames.clear()
        if Variables.selectedJoints!=[]:
            Variables.pselectedJoints.clear()
            for selectj in Variables.selectedJoints:
                Variables.pselectedJoints.append(selectj)
            Variables.selectedJoints.clear()

    def previousselect(self):
        if Variables.pselectedFrames!=[]:
            Variables.selectedFrames.clear()
            for selectf in Variables.pselectedFrames:
                if selectf['show'] and selectf['deleted']==False:
                    Variables.selectedFrames.append(selectf)
            Variables.pselectedFrames.clear()
        if Variables.pselectedJoints!=[]:
            Variables.selectedJoints.clear()        
            for selectj in Variables.pselectedJoints:
                if selectj['show'] and selectj['deleted']==False:
                    Variables.selectedJoints.append(selectj)
            Variables.pselectedJoints.clear()

    @staticmethod
    def selectAll():
        OpenGLWidget.selectionClear()
        for frame in Frame.framedict:
            if frame['deleted']==False:
                Variables.selectedFrames.append(frame)
        for joint in Joint.jointdict:
            if joint['deleted']==False:
                Variables.selectedJoints.append(joint)

    def DrawFrameTrig(self):
        if Variables.ispickingPoint==False:
            if Variables.isDrawing==False:
                QApplication.setOverrideCursor(Qt.CrossCursor)
                Variables.isDrawing=True
                Variables.pselectedFrames.clear()
                Variables.pselectedJoints.clear()
                for selectf in Variables.selectedFrames:
                    Variables.pselectedFrames.append(selectf)
                for selectj in Variables.selectedJoints:
                    Variables.pselectedJoints.append(selectj)
                Variables.selectedJoints.clear()
                Variables.selectedFrames.clear()
                mdi.statusBar().showMessage('Draw Frame: Select First Joint')
            else:
                QApplication.setOverrideCursor(Qt.CustomCursor)
                Variables.isDrawing=False
                Variables.isFirstJoint=True
                Variables.takenPoint=(None,None,None)
                Variables.preFramepoints=[(None,None,None),(None,None,None)]
                mdi.statusBar().showMessage('')

    def drawSupport(self):
        if Variables.showjointsupport:
            jointcoord=()
            supportscale=Variables.supportscale
            glColor3ub(Variables.supportcolor[0],Variables.supportcolor[1],Variables.supportcolor[2])
            glLineWidth(1)
            for joint in Joint.jointdict:
                if joint['show'] and joint['deleted']==False:
                    jointcoord=(0,0,0)
                    glPushMatrix()
                    glTranslate(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                    glRotatef(joint['angle1'],1,0,0)
                    glRotatef(-joint['angle3'],0,1,0)
                    glRotatef(joint['angle2'],0,0,1)
                    
                    if joint['restraints']!=[0,0,0,0,0,0]:
                        if joint['restraints']==[1,1,1,1,1,1]:
                            #X yönünde fix içi boş
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])        
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glEnd()

                            #Y yönünde fix içi boş 
                            
                            glBegin(GL_LINES)        
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])        
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glEnd()

                        elif joint['restraints']==[1,1,1,0,1,1]:
                            
                            #X yönünde fix içi boş 
                        
                            glBegin(GL_LINES)        
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])        
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glEnd()

                            #Y yönünde pin içi boş                    
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()

                        elif joint['restraints']==[1,1,1,1,0,1]:
                            #Y yönünde fix içi boş                        
                            glBegin(GL_LINES)        
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2])        
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+0.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glEnd()

                            #X yönünde pin içi boş 
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()

                        elif joint['restraints']==[1,1,1,0,0,1]:
                            #Y yönünde pin içi boş
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()

                            #X yönünde pin içi boş 
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()

                        elif joint['restraints']==[1,1,1,0,0,0]:
                            #Y yönünde pin içi boş                    
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()

                            #X yönünde pin içi boş 
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()
                        
                        elif joint['restraints']==[0,1,1,0,0,0]:
                            #Y yönünde pin içi boş                    
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()

                            #X yönünde roler içi boş                    
                            
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+2*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+2*supportscale/self.scale,jointcoord[2])
                            glEnd()

                        elif joint['restraints']==[0,1,1,0,0,1]:
                            #Y yönünde pin içi boş                    
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()

                            #X yönünde roler içi boş                    
                            
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+2*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+2*supportscale/self.scale,jointcoord[2])
                            glEnd()
                        elif joint['restraints']==[1,0,1,0,0,1]:
                            #X yönünde pin içi boş 
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()
                            #Y yönünde roler içi boş                    
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+2*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+2*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glEnd()
                        elif joint['restraints']==[1,0,1,0,0,0]:
                            #X yönünde pin içi boş
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glEnd()
                            #Y yönünde roler içi boş                    
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+2*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+2*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glEnd()
                    
                        elif joint['restraints']==[0,0,1,0,0,0]:
                            #X yönünde roler içi boş                        
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+2*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+2*supportscale/self.scale,jointcoord[2])
                            glEnd()
                            #Y yönünde roler içi boş                    
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+2*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+2*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glEnd()
                        elif joint['restraints']==[0,0,1,0,0,1]:
                            #X yönünde roler içi boş                        
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1]+2*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1]+2*supportscale/self.scale,jointcoord[2])
                            glEnd()
                            #Y yönünde roler içi boş                    
                            glBegin(GL_LINES)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+1.5*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+2*supportscale/self.scale,jointcoord[2]+1*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]+2*supportscale/self.scale,jointcoord[2]-1*supportscale/self.scale)
                            glEnd()
                        

                        else:
                            #belirsiz support                        
                            glBegin(GL_LINES)
                            # glVertex3d(jointcoord[0],jointcoord[1]+1*supportscale/self.scale,jointcoord[2])
                            # glVertex3d(jointcoord[0],jointcoord[1]-1*supportscale/self.scale,jointcoord[2])
                            # glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+1*supportscale/self.scale) 
                            # glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]-1*supportscale/self.scale)
                            # glVertex3d(jointcoord[0]+1*supportscale/self.scale,jointcoord[1],jointcoord[2]) 
                            # glVertex3d(jointcoord[0]-1*supportscale/self.scale,jointcoord[1],jointcoord[2])
                            glVertex3d(jointcoord[0]+0.75*supportscale/self.scale,jointcoord[1],jointcoord[2]+0.75*supportscale/self.scale) 
                            glVertex3d(jointcoord[0]-0.75*supportscale/self.scale,jointcoord[1],jointcoord[2]-0.75*supportscale/self.scale)
                            glVertex3d(jointcoord[0]-0.75*supportscale/self.scale,jointcoord[1],jointcoord[2]+0.75*supportscale/self.scale) 
                            glVertex3d(jointcoord[0]+0.75*supportscale/self.scale,jointcoord[1],jointcoord[2]-0.75*supportscale/self.scale)
                            glVertex3d(jointcoord[0]+0.75*supportscale/self.scale,jointcoord[1]+0.75*supportscale/self.scale,jointcoord[2]) 
                            glVertex3d(jointcoord[0]-0.75*supportscale/self.scale,jointcoord[1]-0.75*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0]-0.75*supportscale/self.scale,jointcoord[1]+0.75*supportscale/self.scale,jointcoord[2]) 
                            glVertex3d(jointcoord[0]+0.75*supportscale/self.scale,jointcoord[1]-0.75*supportscale/self.scale,jointcoord[2])
                            glVertex3d(jointcoord[0],jointcoord[1]+0.75*supportscale/self.scale,jointcoord[2]+0.75*supportscale/self.scale) 
                            glVertex3d(jointcoord[0],jointcoord[1]-0.75*supportscale/self.scale,jointcoord[2]-0.75*supportscale/self.scale)
                            glVertex3d(jointcoord[0],jointcoord[1]-0.75*supportscale/self.scale,jointcoord[2]+0.75*supportscale/self.scale) 
                            glVertex3d(jointcoord[0],jointcoord[1]+0.75*supportscale/self.scale,jointcoord[2]-0.75*supportscale/self.scale)        
                            glEnd()
                    
                    glPopMatrix()

    def drawJointLocalAxes(self):
        if Variables.showjointLocalAxes:
            jointcoord=()
            localaxescale=Variables.localaxescale            
            glLineWidth(1)
            for joint in Joint.jointdict:
                if joint['show'] and joint['deleted']==False:
                    jointcoord=(0,0,0)
                    glPushMatrix()
                    glTranslate(joint['coords'][0],joint['coords'][1],joint['coords'][2])
                    glRotatef(joint['angle1'],1,0,0)
                    glRotatef(-joint['angle3'],0,1,0)
                    glRotatef(joint['angle2'],0,0,1)
                    
                    glBegin(GL_LINES)
                    glColor3ub(0,0,250)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])
                    
                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1]+0.25*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1]+0.25*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1]-0.25*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1]-0.25*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])

                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1],jointcoord[2]+0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1],jointcoord[2]+0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1],jointcoord[2]-0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1],jointcoord[2]-0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])
                    glEnd()

                    glBegin(GL_LINES)
                    glColor3ub(250,0,250)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])
                    
                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+0.25*localaxescale/self.scale,jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+0.25*localaxescale/self.scale,jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]-0.25*localaxescale/self.scale,jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]-0.25*localaxescale/self.scale,jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])

                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0],jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2]+0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2]-0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2]+0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2]-0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])
                    glEnd()

                    glBegin(GL_LINES)
                    glColor3ub(0,250,0)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)
                    
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]+0.25*localaxescale/self.scale,jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]+0.25*localaxescale/self.scale,jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-0.25*localaxescale/self.scale,jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-0.25*localaxescale/self.scale,jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)

                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+0.25*localaxescale/self.scale,jointcoord[1],jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+0.25*localaxescale/self.scale,jointcoord[1],jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]-0.25*localaxescale/self.scale,jointcoord[1],jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]-0.25*localaxescale/self.scale,jointcoord[1],jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)

                    glEnd()
                    glPopMatrix()

    def drawFrameLocalAxes(self):
        if Variables.showframeLocalAxes:
            jointcoord=()
            localaxescale=Variables.localaxescale            
            glLineWidth(1)
            for frame in Frame.framedict:
                if frame['show'] and frame['deleted']==False:
                    jointcoord=(0,0,0)
                    jointstartcoord=(0,0,0)
                    jointendcoord=(0,0,0)
                    glPushMatrix()
                    for joint in Joint.jointdict:
                        if joint['deleted']==False:
                            if joint['name']==frame['joint0']:
                                jointstartcoord=joint['coords']
                            if joint['name']==frame['joint1']:
                                jointendcoord=joint['coords']

                    jointcoord1=((jointstartcoord[0]+jointendcoord[0])/2,(jointstartcoord[1]+jointendcoord[1])/2,(jointstartcoord[2]+jointendcoord[2])/2)                    
                    
                    anglez = math.atan2(jointendcoord[2]-jointstartcoord[2],jointendcoord[0]-jointstartcoord[0] )
                    angledegz= math.degrees(anglez)
                    # anglex = math.atan2(jointendcoord[2]-jointstartcoord[2],-jointendcoord[1]+jointstartcoord[1] )
                    # angledegx= math.degrees(anglex)
                    # angley = math.atan2(-jointendcoord[1]+jointstartcoord[1] ,jointendcoord[0]-jointstartcoord[0] )
                    # angledegy= math.degrees(angley)
                    vx=jointendcoord[0]-jointstartcoord[0]
                    vy=-jointendcoord[1]+jointstartcoord[1]
                    vz=jointendcoord[2]-jointstartcoord[2]
                    framelength=math.sqrt(math.pow(vx,2)+math.pow(vy,2)+math.pow(vz,2))
                    # anglealfa=math.acos(vx/framelength)
                    # angledegalfa=math.degrees(anglealfa)
                    anglebeta=math.acos(vy/framelength)
                    angledegbeta=math.degrees(anglebeta)
                    # anglegama=math.acos(vz/framelength)
                    # angledeggama=math.degrees(anglegama)
                    z=-angledegz                    
                    glTranslate(jointcoord1[0],jointcoord1[1],jointcoord1[2])
                    glRotatef(z,0,1,0)
                    x=angledegbeta-90
                    glRotatef(x,0,0,1)
                    glRotatef(frame['angle'],1,0,0) #bu kısımda sadece kullanıcının girdiği açı değişecek
             

                    glBegin(GL_LINES)
                    glColor3ub(0,0,250)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])
                    
                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1]+0.25*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1]+0.25*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1]-0.25*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1]-0.25*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])

                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1],jointcoord[2]+0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1],jointcoord[2]+0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1],jointcoord[2]-0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+1.5*localaxescale/self.scale,jointcoord[1],jointcoord[2]-0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+2*localaxescale/self.scale,jointcoord[1],jointcoord[2])
                    glEnd()

                    glBegin(GL_LINES)
                    glColor3ub(250,0,250)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])
                    
                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+0.25*localaxescale/self.scale,jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]+0.25*localaxescale/self.scale,jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]-0.25*localaxescale/self.scale,jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0]-0.25*localaxescale/self.scale,jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])

                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])
                    glVertex3d(jointcoord[0],jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2]+0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2]-0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2]+0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-1.5*localaxescale/self.scale,jointcoord[2]-0.25*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-2*localaxescale/self.scale,jointcoord[2])
                    glEnd()

                    glBegin(GL_LINES)
                    glColor3ub(0,250,0)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2])
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)
                    
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]+0.25*localaxescale/self.scale,jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]+0.25*localaxescale/self.scale,jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-0.25*localaxescale/self.scale,jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1]-0.25*localaxescale/self.scale,jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)

                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+0.25*localaxescale/self.scale,jointcoord[1],jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]+0.25*localaxescale/self.scale,jointcoord[1],jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]-0.25*localaxescale/self.scale,jointcoord[1],jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0]-0.25*localaxescale/self.scale,jointcoord[1],jointcoord[2]+1.5*localaxescale/self.scale)
                    glVertex3d(jointcoord[0],jointcoord[1],jointcoord[2]+2*localaxescale/self.scale)

                    glEnd()
                    glPopMatrix()

    def extrudeview(self):
        try:
            if Variables.showextrudeview:
                extrudescale=1
                
                for frame in Frame.framedict:
                    if frame['show'] and frame['deleted']==False:
                        jointstartcoord=(0,0,0)
                        jointendcoord=(0,0,0)
                        jointcoord=(0,0,0)                    
                        framesection=None
                        e2=0
                        if frame['section']!='No Section':
                            for section in Sections.sectiondict:
                                if section['deleted']==False:
                                    if section['index']==frame['section']:
                                        framesection=section
                            for joint in Joint.jointdict:
                                if joint['deleted']==False:
                                    if joint['name']==frame['joint0']:
                                        jointstartcoord=joint['coords']
                                    if joint['name']==frame['joint1']:
                                        jointendcoord=joint['coords']
                            
                            glPushMatrix()
                           
                            anglez = math.atan2(jointendcoord[2]-jointstartcoord[2],jointendcoord[0]-jointstartcoord[0] )
                            angledegz= math.degrees(anglez)
                            vx=jointendcoord[0]-jointstartcoord[0]
                            vy=-jointendcoord[1]+jointstartcoord[1]
                            vz=jointendcoord[2]-jointstartcoord[2]
                            framelength=math.sqrt(math.pow(vx,2)+math.pow(vy,2)+math.pow(vz,2))
                            anglebeta=math.acos(vy/framelength)
                            angledegbeta=math.degrees(anglebeta)
                            z=-angledegz

                            glTranslate(jointstartcoord[0],jointstartcoord[1],jointstartcoord[2])
                            #glTranslate(-e2,0,0)
                            glRotatef(z,0,1,0)
                            x=angledegbeta-90
                            glRotatef(x,0,0,1)
                            glRotatef(frame['angle'],1,0,0) #bu kısımda sadece kullanıcının girdiği açı değişecek

                            if framesection['type']=='ishape':
                                #####################AĞIRLIK MERKEZİ###################################
                                e2=0
                                Aw=(framesection['h']-(framesection['btopthickness']+framesection['bbottomthickness']))*framesection['wthickness']
                                Aftop=framesection['btop']*framesection['btopthickness']
                                Afbottom=framesection['bbottom']*framesection['bbottomthickness']
                                try:
                                    e3=(Aftop*((framesection['h']/2)-(framesection['btopthickness']/2)) + Afbottom*((-framesection['h']/2)+(framesection['bbottomthickness']/2)))/(Aftop+Afbottom)
                                except Exception as e:
                                    logging.debug(e)
                                    logging.info('divide 0,e3')
                                #glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image.width,image.height,0,GL_RGBA,GL_UNSIGNED_BYTE,image_data)
                                glColor3ub(Variables.frameColor[0],Variables.frameColor[1],Variables.frameColor[2])
                                #glEnable(GL_TEXTURE_2D)
                                #glColor4f(1,0,0,0.5)
                                glEnable(GL_CULL_FACE)
                                glBegin(GL_QUADS)
                                #SCALE ETMEK GEREKİRSE /self.scale yapmalıyım.
                                
                                #ÜST BAŞLIK üst
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))

                                #üst başlık sol yan
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                
                                #üst başlık sağ yan
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))

                                #üst başlık sol yan alt                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                

                                #üst başlık sağ yan alt                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                

                                #ALT BAŞLIK                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                

                                #alt başlık sol yan
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))

                                #alt başlık sağ yan                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                

                                #alt başlık sol yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))

                                #alt başlık sağ yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))

                                #sağ yan gövde                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                
                                
                                # sol yan gövde
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                
                                glEnd()

                                glBegin(GL_QUADS)
                                #ÖN YÜZ
                                #üst başlık sol yan
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                
                                #üst başlık sağ yan
                                                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                
                                #alt başlık sol yan                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                
                                #alt başlık sağ yan
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                
                                #sağ yan gövde                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                                            
                                # sol yan gövde
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                
                                glEnd()

                                glBegin(GL_QUADS)
                                #ARKA YÜZ
                                #üst başlık sol yan
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))                            
                                
                                #üst başlık sağ yan
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                
                                #alt başlık sol yan
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                
                                #alt başlık sağ yan
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                
                                #sağ yan gövde
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                                            
                                # sol yan gövde
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                
                                glEnd()
                                #glDisable(GL_TEXTURE_2D)
                                glDisable(GL_CULL_FACE)

                                glLineWidth(1)
                                glColor3ub((Variables.frameColor[0]+7)*2,(Variables.frameColor[1]+7)*2,(Variables.frameColor[2]+7)*2)
                                
                                glBegin(GL_LINES)
                                #SCALE ETMEK GEREKİRSE /self.scale yapmalıyım.

                                #ÜST BAŞLIK üst
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))

                                #üst başlık sol yan                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))

                                #üst başlık sağ yan
                                
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))

                                #üst başlık sol yan alt

                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))

                                #üst başlık sağ yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))


                                #ALT BAŞLIK
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))

                                #alt başlık sol yan

                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))

                                #alt başlık sağ yan

                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))

                                #alt başlık sol yan alt

                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))

                                #alt başlık sağ yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                
                                ####################### ÖN YÜZ #############################
                                #ÜST BAŞLIK üst                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))

                                #üst başlık sol yan
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                
                                #üst başlık sağ yan
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                
                                #üst başlık sol yan alt
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                
                                #üst başlık sağ yan alt
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))

                                #ALT BAŞLIK
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                
                                #alt başlık sol yan

                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                #alt başlık sağ yan

                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                #alt başlık sol yan alt

                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                #alt başlık sağ yan alt
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))


                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))

                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                
                                ####################### ARKA YÜZ #############################
                                #ÜST BAŞLIK üst                            
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))

                                #üst başlık sol yan
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                
                                #üst başlık sağ yan
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                
                                #üst başlık sol yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                
                                #üst başlık sağ yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['btop']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))

                                #ALT BAŞLIK
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                
                                #alt başlık sol yan

                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                #alt başlık sağ yan

                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))
                                #alt başlık sol yan alt

                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['bbottom']/2))
                                #alt başlık sağ yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['bbottom']/2))


                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2+extrudescale*(framesection['wthickness']/2))

                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bbottomthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['btopthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']/2))
                                
                                glEnd()
                            elif framesection['type']=='ushape':
                                #######AĞIRLIK MERKEZİ###########
                                Aw=framesection['h']*framesection['wthickness']
                                Af=(framesection['b']-framesection['wthickness'])*framesection['bthickness']
                                try:
                                    e2=((Aw*framesection['wthickness']/2 )+2*(Af*(framesection['wthickness']+(framesection['b']/2))))/(Aw+2*Af)
                                except Exception as e:                                    
                                    logging.debug(e)
                                    logging.info('divide 0,e2')
                                e3=0
                                #glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,image.width,image.height,0,GL_RGBA,GL_UNSIGNED_BYTE,image_data)
                                glColor3ub(Variables.frameColor[0],Variables.frameColor[1],Variables.frameColor[2])
                                #glEnable(GL_TEXTURE_2D)
                                #glColor4f(1,0,0,0.5)
                                glEnable(GL_CULL_FACE)
                                glBegin(GL_QUADS)
                                #SCALE ETMEK GEREKİRSE /self.scale yapmalıyım.
                                
                                #ÜST BAŞLIK üst
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)

                                #üst başlık sağ yan                                
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                                                
                                #üst başlık sağ yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                                                
                                #ALT BAŞLIK
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                
                                #alt başlık sağ yan                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                
                                #alt başlık sağ yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))

                                #sağ yan gövde                            
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                
                                # sol yan gövde
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                
                                glEnd()

                                glBegin(GL_QUADS)
                                ############################# ÖN YÜZ #################################33
                                #ÜST BAŞLIK                             
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                
                                #ALT BAŞLIK
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                # gövde
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))  
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)

                                glEnd()

                                glBegin(GL_QUADS)
                                ############################# ARKA YÜZ #################################33
                                #ÜST BAŞLIK                             
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                
                                #ALT BAŞLIK
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                # gövde
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))  
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                
                                glEnd()
                                #glDisable(GL_TEXTURE_2D)
                                glDisable(GL_CULL_FACE)
                                glLineWidth(1)
                                glColor3ub((Variables.frameColor[0]+7)*2,(Variables.frameColor[1]+7)*2,(Variables.frameColor[2]+7)*2)
                                
                                glBegin(GL_LINES)
                                
                                #ÜST BAŞLIK üst
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)

                                #üst başlık sağ yan                                
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))

                                #üst başlık sağ yan alt
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                                                
                                #ALT BAŞLIK
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)

                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                
                                #alt başlık sağ yan
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                
                                #alt başlık sağ yan alt
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))

                                glEnd()

                                glBegin(GL_LINES)
                                ############################# ÖN YÜZ #################################33
                                #ÜST BAŞLIK
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))

                                #ALT BAŞLIK
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                # gövde
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))  
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0],jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0],jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)

                                glEnd()

                                glBegin(GL_LINES)
                                ############################# ARKA YÜZ #################################33
                                #ÜST BAŞLIK
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))

                                #ALT BAŞLIK
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['b']))
                                # gövde
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2)-extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))  
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2)+extrudescale*(framesection['bthickness']),jointcoord[2]+e2-extrudescale*(framesection['wthickness']))
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3-extrudescale*(framesection['h']/2),jointcoord[2]+e2)
                                glVertex3d(jointcoord[0]+framelength,jointcoord[1]-e3+extrudescale*(framesection['h']/2),jointcoord[2]+e2)

                                glEnd()
                            glPopMatrix()
        except Exception as e:
            logging.debug(e)
            logging.info("Opengl extrudeview Crashed")
    
class ValidatedItemDelegate(QStyledItemDelegate):
    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0
        if index.column() == 1: #only on the cells in the first column
            editor = QLineEdit(widget)
            #editor.setMaxLength(10)
            validator = QDoubleValidator(-999999.9999,999999.9999,4,self)
            validator.setNotation(QDoubleValidator.StandardNotation)
            editor.setValidator(validator)
            return editor
        if index.column() == 0: #only on the cells in the first column
            editor = QLineEdit(widget)
            editor.setMaxLength(2)
            return editor
        return super(ValidatedItemDelegate, self).createEditor(widget, option, index)

class ValidatedItemDelegatePos(QStyledItemDelegate):
    def createEditor(self, widget, option, index):
        if not index.isValid():
            return 0
        if index.column() == 1: #only on the cells in the first column
            editor = QLineEdit(widget)
            #editor.setMaxLength(10)
            validator = QDoubleValidator(0,999999.9999,4,self)
            validator.setNotation(QDoubleValidator.StandardNotation)
            editor.setValidator(validator)
            return editor
        if index.column() == 0: #only on the cells in the first column
            editor = QLineEdit(widget)
            editor.setMaxLength(2)
            return editor
        return super(ValidatedItemDelegatePos, self).createEditor(widget, option, index)

class Savefile():
    def __init__(self, _path):
        self.path=_path
        Savedict={'frames':Frame.framedict,'framelast':Frame.count,'joints':Joint.jointdict,'jointlast':Joint.count,
        'gridxTemp':Variables.gridxTemp,'gridyTemp':Variables.gridyTemp,'gridzTemp':Variables.gridzTemp,
        'gridx':Variables.gridx,'gridy':Variables.gridy,'gridz':Variables.gridz,
        'ybublesize':Variables.ybublesize,'xbublesize':Variables.xbublesize,'zbublesize':Variables.zbublesize,
        'xbubleLoc':Variables.xbubleLoc,'ybubleLoc':Variables.ybubleLoc,'zbubleLoc':Variables.zbubleLoc,
        'framenametextdraw':Variables.framenametextdraw,'jointnametextdraw':Variables.jointnametextdraw,'showgrid':Variables.showgrid,'showorgin':Variables.showorgin,
        'showjointnode':Variables.showjointnode,'showjointsupport':Variables.showjointsupport,'showjointLocalAxes':Variables.showjointLocalAxes,'showframeLocalAxes':Variables.showframeLocalAxes,
        'unitindex':Variables.unitindex,'unitindexlast':Variables.unitindexlast , 'materials':Materials.materialdict,'matindex':Materials.count,
        'sections':Sections.sectiondict,'sectionindex':Sections.count,'showframesectionname':Variables.showframesectionname}
        with open(self.path, 'w') as writer:
            writer.write(str(Savedict))
        mdi.statusBar().showMessage('File saved!')

class OpenFile():
    def __init__(self, _path):
        logging.info("open file function start")
        try:
            self.path=_path
            with open(self.path, 'r') as reader:
                Savedict=ast.literal_eval(reader.read())
                Joint.jointdict.clear()
                Joint.jointdict=Savedict['joints']
                Joint.count=Savedict['jointlast']
                Frame.framedict.clear()
                Frame.framedict=Savedict['frames']
                Frame.count=Savedict['framelast']
                for joint in Joint.jointdict:
                    joint['show']=True
                for frame in Frame.framedict:
                    frame['show']=True
                Materials.materialdict.clear()
                Materials.materialdict=Savedict['materials']
                Materials.count=Savedict['matindex']
                Sections.sectiondict.clear()
                Sections.sectiondict=Savedict['sections']
                Sections.count=Savedict['sectionindex']
                Variables.gridxTemp=Savedict['gridxTemp']
                Variables.gridyTemp=Savedict['gridyTemp']
                Variables.gridzTemp=Savedict['gridzTemp']
                Variables.gridx=Savedict['gridx']
                Variables.gridy=Savedict['gridy']
                Variables.gridz=Savedict['gridz']
                Variables.xbublesize=Savedict['xbublesize']
                Variables.ybublesize=Savedict['ybublesize']
                Variables.zbublesize=Savedict['zbublesize']
                Variables.xbubleLoc=Savedict['xbubleLoc']
                Variables.ybubleLoc=Savedict['ybubleLoc']
                Variables.zbubleLoc=Savedict['zbubleLoc']
                Variables.framenametextdraw=Savedict['framenametextdraw']
                Variables.jointnametextdraw=Savedict['jointnametextdraw']
                Variables.showgrid=Savedict['showgrid']
                Variables.showorgin=Savedict['showorgin']
                Variables.showjointnode=Savedict['showjointnode']
                Variables.showjointsupport=Savedict['showjointsupport']
                Variables.showjointLocalAxes=Savedict['showjointLocalAxes']
                Variables.showframeLocalAxes=Savedict['showframeLocalAxes']
                Variables.unitindex=Savedict['unitindex']
                Variables.unitindexlast=Savedict['unitindexlast']
                Variables.showframesectionname=Savedict['showframesectionname']
                mdi.menubar.clear()
                mdi.toolbar.close()
                mdi.toolbardraw.close()
                mdi.toolbarEdit.close()
                mdi.toolbarframeAssign.close()
                mdi.toolbarGrids.close()
                mdi.toolbarjointAssign.close()
                mdi.toolbarview.close()
                mdi.toolbarunit.close()
                mdi.InitUI()
                MDIWindow.count = 1
                mdi.sub = OpenGLWidget()
                mdi.sub.setWindowIcon(QIcon('Icons/ekru1_icon.ico'))
                mdi.sub.setWindowTitle( "Window-"+str(MDIWindow.count)+"/3D view" )
                mdi.mdi.addSubWindow(mdi.sub)            
                mdi.sub.setFocusPolicy(Qt.StrongFocus)
                mdi.sub.view['3d']=True
                mdi.mdi.tileSubWindows()
                mdi.setWindowTitle("BEDESIGN-"+Variables.projectname)
                mdi.statusBar().showMessage(Variables.projectname+' - File opened!')
        except Exception as e:
            logging.debug(e)
        logging.info("open file function end")

class NewFile():
    def __init__(self,_gridxcount,_gridycount,_gridzcount,_gridxspan,_gridyspan,_gridzspan):
        logging.info("new file function start")
        try:
            Variables.path=None
            Joint.jointdict.clear()        
            Joint.count=0
            Frame.framedict.clear()        
            Frame.count=0
            Materials.materialdict.clear()
            Materials.count=0
            Sections.sectiondict.clear()
            Sections.count=0
            Variables.gridxcount=_gridxcount
            Variables.gridycount=_gridycount
            Variables.gridzcount=_gridzcount
            Variables.gridxspan=_gridxspan
            Variables.gridyspan=_gridyspan
            Variables.gridzspan=_gridzspan
            Variables.projectname="Un Saved Project"
            Variables.xbublesize=20
            Variables.ybublesize=20
            Variables.zbublesize=20
            Variables.xbubleLoc="End"
            Variables.ybubleLoc="End"
            Variables.zbubleLoc="End"
            Variables.framenametextdraw=False
            Variables.jointnametextdraw=False
            Variables.showgrid=True
            Variables.showorgin=True
            Variables.showjointnode=False
            Variables.showjointsupport=True
            Variables.showjointLocalAxes=False
            Variables.showframeLocalAxes=False
            Variables.showframesectionname=False
            mdi.menubar.clear()
            mdi.toolbar.close()
            mdi.toolbardraw.close()
            mdi.toolbarEdit.close()
            mdi.toolbarframeAssign.close()
            mdi.toolbarGrids.close()
            mdi.toolbarjointAssign.close()
            mdi.toolbarview.close()
            mdi.toolbarunit.close()
            mdi.InitUI()
            MDIWindow.count = 1
            mdi.sub = OpenGLWidget()
            mdi.sub.setWindowIcon(QIcon('Icons/ekru1_icon.ico'))
            mdi.sub.setWindowTitle( "Window-"+str(MDIWindow.count)+"/3D view" )
            mdi.mdi.addSubWindow(mdi.sub)
            mdi.sub.setFocusPolicy(Qt.StrongFocus)
            mdi.sub.view['3d']=True
            mdi.mdi.tileSubWindows()
            mdi.setWindowTitle("BEDESIGN-"+Variables.projectname)
            mdi.statusBar().showMessage(Variables.projectname+' - File created!')
        except Exception as e:
            logging.debug(e)
        logging.info("new file function end")


#TODO: Grid space ken delete 0 dan sonraki patlıyor(geçici çözdüm hala sıkıntı olabilir)
#TODO: material silerken sectiona tanımlı mı diye sorgulayalım

app = QApplication(sys.argv)
mdi  = MDIWindow()
mdi.show()
app.exec_()

#NOT: y ve z nin yerini değişip z yi negatif yaptım

# class Grid():
#     count=0
#     griddict=[]
#     def __init__(self,_Orgin,_gridx,_gridy,_gridz):
#         self.orgin=_Orgin
#         self.gridx=_gridx
#         self.gridy=_gridy
#         self.gridz=_gridz
#         Grid.count += 1
#         self.griddict.append({'name:':Grid.count,'orgin':self.orgin,
#                                 'gridx':self.gridx,'gridy':self.gridy,'gridz':self.gridz})