from lark import Lark, Transformer, common
from collections import defaultdict
import os.path
import os
import sys

comboparser = Lark(r"""
    combo: input (SEPARATOR input)*

    SEPARATOR : ","
              | ">"

    TILDE : "~"

    input : MOVEMENT
          | norm_input
          | var_input
          | opt_input
          | multi_input
          | follow_input
          | hit_input
          | MOVEMENT

    norm_input : [ DELAY ] [ CH ] [ JUMP ] [ TK ] [ SPACING ] [ DIRECTION ] BUTTON [ NOTES ]
               | AIRTHROW
               | THROW
               | series_input
               | HEAT
               | ARCDRIVE
    var_input : "(" input ")" "/" "(" input ")"
    opt_input : "|" input "|"
    follow_input : input  [ " | "] TILDE input [ "|" ] [ [ " | "] TILDE input [ "|" ] ]
    multi_input : [ DELAY ] [ JUMP ] [ DIRECTION ] BUTTON ( BUTTON )*
    hit_input : [ DELAY ] [ JUMP ] [ DIRECTION ] BUTTON "(" NUMBER (TEXT)* ")"
    series_input : [ DELAY ] ONETWOTHREE

    MOVEMENT : "walk forward"
             | "walk"
             | "dash"
             | "microdash"
             | "airdash"
             | "jumpcancel"
             | "air backdash"
             | "airbackdash"
             | "airdodge"
             | "catch"
             | "jc" [ "7" | "8" | "9" ]
             | "djc"
             | "dj"
             | "66"
             | "j.66"
             | "j.22"
             | "2" | "4" | "7" | "8" | "9"

    HEAT : "Heat" | "Heat"
         | "IH" | "Initiative Heat"
         | "j.IH" | "Initiative Heat"

    ARCDRIVE : "AD" ["(~2)"] | "Arc Drive"
             | "AAD" | "Another Arc Drive"

    ONETWOTHREE : "5A6AA"
                | "5A6A"

    JUMP : [ "s" ] [ "d" ] "j" [ "7" | "8" | "9" ] ["."]
         //| "dj" ["."]
         //| "sj" ["."]
         //| "sdj" ["."]
    TK : "tk" ["."]
    CH : "ch" ["."]
    SPACING : ( "c" | "f" ) ["."]
    DELAY : "dl[.]"
          | "(" "delay" ")"
    AIRTHROW : [ "4" | "6" ] ["g"] "AT"
             | "Airthrow"
             | "airthrow"
    THROW : [ "4" | "6" ] ( "Throw" | "Grab" ) [ TILDE "2" ]
    DIRECTION : NUMBER
    BUTTON : ( "A".."D" | "X" )
           | LBRACKET ("A".."D") RBRACKET
           | ("a".."d" | "x" )
           | LBRACKET ("a".."d") RBRACKET
    NOTES : "(" TEXT ")"
    TEXT : STRING
    LBRACKET : "[" | "{"
    RBRACKET : "]" | "}"

    %import common.SIGNED_NUMBER -> NUMBER
    %import common.WS
    %import common.WORD -> STRING
    %ignore WS
    """, start='combo' )#, parser="lalr")

charaNames = [
"Aoko",
"Tohno",
"Hime",
"Nanaya",
"Kouma",
"Miyako",
"Ciel",
"Sion",
"Ries",
"V.Sion",
"Wara",
"Roa",
"Maids",
"Akiha",
"Arc",
"P.Ciel",
"Warc",
"V.Akiha",
"M.Hisui",
"S.Akiha",
"Satsuki",
"Len",
"Ryougi",
"W.Len",
"Nero",
"NAC",
"KohaMech",
"Hisui",
"Neko",
"Kohaku",
"NekoMech",
]

moons = [ 'C','F','H' ]

def toArrow( d ):
    return d
    output = u""
    for s in d:
        if s == '1':
            output += u"\u2199"
        if s == '2':
            output += u"\u2b07"
        if s == '3':
            output += u"\u2198"
        if s == '4':
            output += u"\u2b05"
        if s == '6':
            output += u"\u27a1"
        if s == '7':
            output += u"\u2196"
        if s == '8':
            output += u"\u2b06"
        if s == '9':
            output += u"\u2197"
    return output

def trace():
    import pdb; pdb.set_trace()

def flatten(l):
    mid = [ x for x in l if x != ">" ]
    #trace()
    temp = []
    for x in mid:
        if type(x[0]) == list and len(mid) > 1:
            for y in x:
                temp.append(y)
        else:
            temp.append(x)
    print( "flattened: ", temp )
    return temp

class MyTransformer(Transformer):

    def __init__(self, fname ):
        Transformer.__init__(self)
        self.seqDict, self.hitDict = self.parseSeq( fname )
        self.inputs = 0
    def parseSeq( self, fname ):
        seqDict = defaultdict(lambda: "-0")
        hitDict = defaultdict(lambda: "1")
        with open( fname, 'r' ) as f:
            f.readline()
            for line in f:
                l = line.strip().split(',')
                name = l[0]
                seq = l[1]
                seqDict[ name ] = seq
                if len(l) >= 3 and l[2]:
                    hit = l[2]
                    if hit == "Yes" or hit == "yes":
                        hit = "1"
                    if hit == "No" or hit == "no":
                        hit = "0"
                    hitDict[name] = hit
        return seqDict, hitDict

    def combo(self, items):
        return flatten(items)
    def input(self, items):
        (items,) = items
        return items
    def opt_input(self, items):
        return items[0]
    def SEPARATOR(self, items):
        return ">"
    def hit_input(self, items):
        dispString = ""
        moveString = ""
        textOpen = False
        for item in items:
            if ( item.type == "NUMBER" ):
                dispString += " ("
                textOpen = True
            if (item.type == "TEXT" ):
                dispString += " "
                if not textOpen:
                    dispString += "("
                    textOpen = True
            if ( item.type == "DIRECTION" ):
                dispString += toArrow( item )
            else:
                dispString += item
            if ( item.type == "JUMP" or
                 item.type == "BUTTON" or
                 item.type == "DIRECTION" ):
                if ( item[0] == "[" or item[0] == "{" ):
                    moveString += item[1:-1].upper()
                else:
                    moveString += item.upper()
        if (item.type == "TEXT" ):
            dispString += ")"

        return [ dispString, self.seqDict[moveString], "1", moveString ]
    def multi_input(self, items):
        delayString = ""
        prefixString = ""
        dispPrefString = ""
        moveString = ""
        dirMark = False
        direction = None
        outputs = []
        for item in items:
            if ( item.type == "DELAY" ):
                delayString += item
            if ( item.type == "JUMP" ):
                dispPrefString += item
                prefixString += "j."
            if ( item.type == "DIRECTION" ):
                direction = item
            if ( item.type == "BUTTON" ):
                if not direction:
                    direction = "5"
                dispString = delayString + dispPrefString + \
                    toArrow(direction) + item.upper()
                delayString = ""
                moveString = prefixString + direction + item.upper()
                outputs.append( [dispString, self.seqDict[ moveString ], self.hitDict[ moveString ], moveString ] )
        return outputs

    def series_input( self, items ):
        return items[0]

    def follow_input(self, items):
        delayString = ""
        prefixString = ""
        dispPrefString = ""
        moveString = ""
        dispString = ""
        dispString2 = ""
        dirMark = False
        direction = None
        outputs = []
        lastDirection = 0
        numitems = len(items)
        for i in range(numitems):
            item = items[i]
            if ( item.type == "DELAY" ):
                delayString += item
            elif ( item.type == "JUMP" ):
                dispPrefString += item
                prefixString += "j."
            elif ( item.type == "DIRECTION" ):
                direction = item
            elif ( item.type == "BUTTON" ):
                if not direction:
                    direction = "5"
                if not dispString:
                    dispString = delayString + dispPrefString + toArrow(direction) + item.upper()
                    delayString = ""
                    dispString2 = delayString + dispPrefString + toArrow(direction) + item.upper()
                else:
                    if ( lastDirection == direction and len(direction) == 1 ):
                        dispString2 += item
                    else:
                        dispString2 += toArrow(direction) + item
                    dispString = dispString2
                if ( lastDirection == direction and len(direction) == 1):
                    moveString += prefixString + item
                else:
                    moveString += prefixString + direction + item
                outputs.append( [dispString, self.seqDict[ moveString ],
                                 self.hitDict[moveString],
                                 moveString ] )
                lastDirection = direction
            elif (item.type == "NOTES"):
                outputs[-1][0] += item
                if "whiff" in item:
                    outputs[-1][2] = "0"
        return outputs

    def var_input(self, items):
        return items[0]
    def MOVEMENT( self, items ):
        dispString = items.value
        moveString = items.value
        return ( dispString, self.seqDict[moveString], "0",
                 moveString )
    def norm_input(self, items):
        dispString = ""
        moveString = ""
        dirMark = False
        sethit = False
        exhit = 0
        for item in items:
            if ( item.type == "DELAY" ):
                dispString += item
            elif ( item.type == "JUMP" or item.type == "TK"):
                dispString += item
                moveString += "j."
            elif ( item.type == "DIRECTION" ):
                dispString += toArrow(item)
                moveString += item
                dirMark = True
            elif ( item.type == "BUTTON" ):
                if not dirMark:
                    moveString += toArrow("5")
                    #dispString += "5"
                dispString += item.upper()
                if ( item[0] == "[" or "{" in item ):
                    moveString += item[1:-1].upper()
                else:
                    moveString += item.upper()
            elif ( item.type == "ONETWOTHREE" ):
                dispString += item
                moveString += item
            elif ( item.type == "AIRTHROW"):
                if item[0] == "4":
                    dispString += toArrow("4")
                elif item[0] == "6":
                    dispString += toArrow("6")
                if "g" in item:
                    dispString += "g"
                    moveString += "g"
                dispString += "AT"
                moveString += "AT"
            elif ( item.type == "THROW"):
                if item[0] == "4":
                    dispString += toArrow("4")
                elif item[0] == "6":
                    dispString += toArrow("6")
                dispString += "Throw"
                moveString += "Throw"
            elif ( item.type == "HEAT"):
                dispString += item
                moveString += item
            elif ( item.type == "ARCDRIVE"):
                dispString += item
                moveString += item
            elif ( item.type == "NOTES" ):
                if 'whiff' in item:
                    setHit = True
                    exhit = '0'
                dispString +=  item
            else:
                dispString += item
                print( dispString )
                print( moveString )
                assert False
        #trace()
        return [ dispString, self.seqDict[moveString],
                 self.hitDict[moveString] if not sethit else exhit,
                 moveString ]

class Transformer(MyTransformer):
    def follow_input(self, items):
        moves = [ items[0] ]
        lastMove = 0
        searchMoves = [ items[0][3][:-1] + "X" ]
        if len(items) > 1:
            i = 2
            while i < len( items ):
                move = items[i]
                move[0] = "Add. " + move[0]
                if "5" == move[3][0]:
                    move[3] = move[3][1:]
                searchMove = searchMoves[lastMove]+"~"+move[3]
                searchMoves.append( searchMoves[lastMove]+"~"+move[3][:-1] + "X" )
                move[3] = moves[lastMove][3]+"~"+move[3]
                move[1] = self.seqDict[move[3]]
                move[2] = self.hitDict[move[3]]
                if move[1] == '-0':
                    move[1] = self.seqDict[searchMove]
                    move[2] = self.hitDict[searchMove]
                moves.append(move)
                i += 2
                lastMove+=1
        return moves

def exportCombos( clist, fname ):
    with open( fname, 'w' ) as f:
        f.write("{}\n".format(len(clist)))
        for combo in clist:
            comboName = combo[0]
            comboText = combo[1]
            f.write( comboName )
            f.write("{}\n".format(len(comboText)))
            try:
                for move in comboText:
                    f.write(move[0])
                    f.write("\n")
                    if move[1] == '-0':
                        print ("unassigned", move)
                    f.write(move[1])
                    f.write("\n")
                    f.write(move[2])
                    f.write("\n")
            except:
                print( move )
                print( comboText )
                print( comboName )
                assert False

def exportComboFolder( clist, fname ):
    if not ( os.path.isdir(fname) ):
        os.mkdir(fname)
    for combo in clist:
        comboName = combo[0]
        with open( fname + "/" + comboName.strip('\n') + ".txt", 'w' ) as f:
            f.write("1\n")
            f.write("Combo\n")
            comboText = combo[1]
            f.write("{}\n".format(len(comboText)))
            try:
                for move in comboText:
                    f.write(move[0])
                    f.write("\n")
                    if move[1] == '-0':
                        print ("unassigned", move)
                    f.write(move[1])
                    f.write("\n")
                    f.write(move[2])
                    f.write("\n")
            except:
                print( move )
                print( comboText )
                print( comboName )
                assert False

def exportCombo( combo ):
    comboName = combo[0]
    with open( "trials/" + comboName.strip('\n') + ".txt", 'w' ) as f:
        f.write("1\n")
        f.write("Combo\n")
        comboText = combo[1]
        f.write("{}\n".format(len(comboText)))
        try:
            for move in comboText:
                f.write(move[0])
                f.write("\n")
                if move[1] == '-0':
                    print ("unassigned", move)
                f.write(move[1])
                f.write("\n")
                f.write(move[2])
                f.write("\n")
        except:
            print( move )
            print( comboText )
            print( comboName )
            assert False

def process( comboList, seqList, outputFolderName ):
    a = Transformer( seqList )
    g = []
    with open( comboList, 'r' ) as f:
        for w in f:
            if w[0] == "[":
                w = next(f, None)
            comboName = w
            print( comboName )
            comboText = next(f, None)
            t = comboparser.parse(comboText)
            print t.pretty()
            g.append([comboName, a.transform(t)])
            #print g
    exportComboFolder( g, outputFolderName )

if __name__ == "__main__":
    comboName = input( "enter name of combo file: " )
    seqName = input( "enter name of sequence file: " )
    outputName = input( "Enter name of output folder" )
    process( comboName, seqName, outputName )
