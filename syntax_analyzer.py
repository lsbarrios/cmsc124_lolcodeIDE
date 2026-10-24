import sys
from lexical_analyzer import tokenize

#parse tree
class Node:
    def __init__(self, label, children = None):
        self.label = label
        self.children = children or []
        
    #parse tree shown (presented like tree function in bash)
    def show(self, level = 0):
        text = "    " * level + self.label + "\n"
        for child in self.children:
            text += child.show(level + 1)
        return text
        

#keyword groups
TWO_OPERANDS = ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF", "MOD OF", "BIGGR OF", "SMALLR OF", "BOTH OF", "EITHER OF", "WON OF", "BOTH SAEM", "DIFFRINT"]

MANY_OPERANDS = ["ALL OF", "ANY OF", "SMOOSH"]

LITERALS = ["NUMBR", "NUMBAR", "YARN", "TROOF"]

#keywords that end a block of statements
PAIRED_KEYWORDS = ["HAI", "KTHXBYE", "OIC", "YA RLY", "NO WAI", "OMG", "OMGWTF","IM OUTTA YR", "IF U SAY SO"]

