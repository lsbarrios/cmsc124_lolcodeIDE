import re

class Token:
    def __init__(self, type, lexeme, line):
        self.type = type
        self.lexeme = lexeme
        self.line = line

KEYWORDS = {
    "Code Delimiter" : ["HAI", "KTHXBYE"],
    "Variable Delimiter" : ["WAZZUP", "BUHBYE"],
    "Variable Declaration" : ["I HAS A"],
    "Variable Assignment" : ["ITZ", "R"],
    "Operand Separator" : ["AN"],
    "Arithmetic Operation" : ["SUM OF", "DIFF OF", "PRODUKT OF", "QUOSHUNT OF","MOD OF", "BIGGR OF", "SMALLR OF"],
    "Boolean Operation" : ["BOTH OF", "EITHER OF", "WON OF", "NOT","ANY OF", "ALL OF"],
    "Comparison Operation" : ["BOTH SAEM", "DIFFRINT"],
    "Concatenation" : ["SMOOSH"],
    "Typecast" : ["MAEK", "A", "IS NOW A"],
    "Output Keyword" : ["VISIBLE"],
    "Input Keyword" : ["GIMMEH"],
    "If-Else Keyword" : ["YA RLY", "MEBBE", "NO WAI"],
    "Switch-Case Keyword" : ["WTF?", "OMG", "OMGWTF"],
    "Conditional Delimiter" : ["O RLY?", "OIC"],
    "Loop Delimiter" : ["IM IN YR", "IM OUTTA YR"],
    "Loop Operation" : ["UPPIN", "NERFIN"], 
    "Loop Condition" : ["TIL", "WILE"],
    "Argument Marker" : ["YR"],
    "Function Delimiter" : ["HOW IZ I", "IF U SAY SO"],
    "Function Call" : ["I IZ"],
    "Return Keyword" : ["FOUND YR"],
    "Break Keyword" : ["GTFO"],
    "List Terminator" : ["MKAY"],
}

#sort by putting the keywords with the most words first
KEYWORD_LIST = []
for size in [4,3,2,1]:
    for category in KEYWORDS:
        for kw in KEYWORDS[category]:
            if len(kw.split()) == size:
                KEYWORD_LIST.append(kw)

#return the group a keyword belongs to
def get_category(kw):
    for category in KEYWORDS:
        if kw in KEYWORDS[category]:
            return category
    return None

PATTERNS = [
    ("NUMBAR", r"^\-?\d+\.\d+$"),                     
    ("NUMBR",  r"^\-?\d+$"),
    ("TROOF",  r"^(WIN|FAIL)$"),
    ("TYPE",   r"^(NUMBR|NUMBAR|YARN|TROOF|NOOB)$"),
    ("IT",     r"^IT$"),                              
    ("PLUS",   r"^\+$"),                               
    ("IDENT",  r"^[a-zA-Z][0-9A-Za-z_]*$"),  
]

#return the token type of a single word, None if it matches nothing
def classify(word):
    for name, pattern in PATTERNS:
        if re.match(pattern, word):
            return name
    return None

#if keyword starts at words[i] where the list is sorted with the longest first, return the whole keyword, else return None
def match_keyword(words,i):
    for kw in KEYWORD_LIST:
        kw_words = kw.split()
        n = len(kw_words)
        if i + n > len(words):
            continue #not enough words

        matched = True
        #compare word for word
        for j in range(n):
            if words[i+j] != kw_words[j]:
                matched = False
                break
        if matched:
            return kw
    return None

def tokenize(src, keep_newlines=True):
    tokens = []
    errors = []
    in_comment = False
    line_no = 0

    for line in src.split("\n"):
        line_no += 1

        words_in_line = line.split()

        #check if multi line comment, if yes then ignore
        if in_comment:

            #check if end of multi line comment
            if len(words_in_line) > 0 and words_in_line[0] == "TLDR":
                in_comment = False

                #only a BTW comment can follow TLDR on same line
                if len(words_in_line) > 1 and words_in_line[1] != "BTW":
                    errors.append(f"Line {line_no}: TLDR must be alone on its own line")
            continue

        if len(words_in_line) > 0 and words_in_line[0] == "OBTW":
            in_comment = True
            continue

        parts = line.split('"')
        tokens_before = len(tokens)

        prev_kw =None #key word right before the current word
        stop_line = False #set to True when BTW comment starts

        for p in range(len(parts)):
            if stop_line:
                break

            part = parts[p]

            #inside of quotes which is a YARN or a string
            if p%2==1:
                is_last = (p == len(parts) - 1)
                no_closing_quote = (len(parts)%2 == 0)
                if is_last and no_closing_quote:
                    errors.append(f'Line {line_no}: no matching " for YARN literal')
                else:
                    tokens.append(Token("YARN", '"' + part + '"' , line_no ))
                    prev_kw = None

            #outside of quotes, not YARN or string
            else:
                words = part.split()

                i = 0
                while i < len(words):
                    word = words[i]

                    #check if single line comment then ignore if yes
                    if word == "BTW":
                        stop_line = True
                        break

                    #OBTW and TLDR should be alone on its own line
                    if word == "OBTW" or word == "TLDR":
                        errors.append(f"Line {line_no}: {word} must be on its own line")
                        i+=1
                        continue

                    #keyword with size from 1 to 4, send starting word index
                    kw = match_keyword(words, i)
                    if kw is not None:
                        tokens.append(Token(get_category(kw), kw, line_no))
                        prev_kw = kw
                        i+=len(kw.split())
                        continue

                    #if not from above then identifier or literal
                    kind = classify(word)
                    if kind is None:
                        errors.append(f"Line {line_no}: invalid lexeme {word}")
                    else:
                        if kind=="IDENT":
                            #check what kind of identifier

                            if prev_kw == "HOW IZ I" or prev_kw == "I IZ":
                                kind = "FUNCTION_ID"
                            elif prev_kw == "IM IN YR" or prev_kw == "IM OUTTA YR":
                                kind = "LOOP_ID"
                            else:
                                kind = "VARIABLE_ID"

                        tokens.append(Token(kind, word, line_no))

                    prev_kw = None
                    i += 1
        if keep_newlines and len(tokens) > tokens_before:
            tokens.append(Token("NEWLINE", "\\n", line_no))

    if in_comment:
        errors.append("OBTW without maching TLDR")

    return tokens, errors

DEMO = '''
HOW IZ I addNum YR x AN YR y
    FOUND YR SUM OF x AN y
IF U SAY SO

HOW IZ I printName YR person
    VISIBLE "Hello, " + person
    GTFO
IF U SAY SO

HOW IZ I printNum YR x
    FOUND YR x
IF U SAY SO

HAI
    WAZZUP##
        I HAS A name
        I HAS A num1
        I HAS A num2
        I HAS A thing2 ITZ "some"
    BUHBYE

    GIMMEH num1
    GIMMEH num2

    I IZ addNum YR num1 AN YR num2
    VISIBLE IT

    GIMMEH name
    I IZ printName YR name
    VISIBLE IT

    I IZ printNum YR SUM OF num1 AN 2
    VISIBLE IT

KTHXBYE
'''

def main():
    filename = input("Enter the .lol file (press Enter for the demo): ")
    if filename == "":
        source = DEMO
    else:
        with open(filename, "r", encoding="utf-8") as file:
            source = file.read()

    toks, errs = tokenize(source, keep_newlines=False)

    print(f"{'LINE':<6}{'TYPE':<13}LEXEME")
    for t in toks:
        print(f"{t.line:<6}{t.type:<25}{t.lexeme}")

    if len(errs) > 0:
        print("\nLEXICAL ERRORS:")
        for e in errs:
            print(e)


main()
