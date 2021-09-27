class UndoReundo():
    undodict=[]
    reundodict=[]

    def __init__(self, _obj):
        self.obj=_obj
        if _obj!=[]:
            self.undodict.append((self.obj))
        self.reundodict.clear()

    @staticmethod
    def undo():
        if UndoReundo.undodict!=[]:
            for undoobj in UndoReundo.undodict[-1]:
                    undoobj[0].update({undoobj[1]:undoobj[2]})
            UndoReundo.reundodict.append(UndoReundo.undodict[-1])
            UndoReundo.undodict.remove(UndoReundo.undodict[-1])

    @staticmethod
    def reundo():
        if UndoReundo.reundodict!=[]:
            for undoobj in UndoReundo.reundodict[-1]:
                    undoobj[0].update({undoobj[1]:undoobj[3]})
            UndoReundo.undodict.append(UndoReundo.reundodict[-1])
            UndoReundo.reundodict.remove(UndoReundo.reundodict[-1])
