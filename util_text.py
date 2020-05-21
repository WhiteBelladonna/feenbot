#function to parse a faq message
def faqParse(arg1):
    txt = str(arg1)
    txt = unLeet(txt)
    txt = txt.upper()
    return txt

#function to replace leetspeak with proper text
def unLeet(strIn):
    txt = strIn
    txt = txt.replace("!","i")
    txt = txt.replace("1","i")
    txt = txt.replace("$","s")
    txt = txt.replace("5","s")
    txt = txt.replace("7","t")
    txt = txt.replace("4","a")
    txt = txt.replace("3","e")
    txt = txt.replace("@","a")
    return txt

def kwdstring(lst):
    nlst = []
    for i in range(len(lst)):
        nlst.append(lst[i][0])
    string = ' | '.join(nlst)
    return string

def createDate(dtobj):
    string = parseNum(int(dtobj.day))+"."
    string = string + parseNum(int(dtobj.month))+"."
    string = string + str(dtobj.year)+" um "
    string = string + parseNum(int(dtobj.hour))+":"
    string = string + parseNum(int(dtobj.minute))
    return string

def parseNum(int):
    if int < 10:
        string = "0" + str(int)
    else:
        string = str(int)
    return string

def createHeader(txt):
    header = ""
    header = header + "**==============================\n"
    header = header + txt + "\n"
    header = header + "==============================**\n"
    return header