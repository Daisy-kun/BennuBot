plugName = 'Love AI'

def plugid_funcName(inMSG):
    if not inMSG or len(inMSG) != 6:
        return
    if inMSG[0] == 'I love you, Namine':
        sendMSG('I love you too, Daisy', inMSG[1], inMSG[2], inMSG[3])    
def load():
        return plugid_funcName
