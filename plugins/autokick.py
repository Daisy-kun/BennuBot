plugName = 'Auto Kick'

def autokick_channel(inMSG):    

    if not inMSG or len(inMSG) != 6:
        return   
    if inMSG[3] == '#daisy':
        if inMSG[4] != 'Daisy' and inMSG[4] != 'Meowestkitty' and inMSG[4] != 'Namine' and inMSG[4] != 'titegtnodI'  and inMSG[4] != 'doop' and inMSG[4] != 'kittyfish':
            irc_kick(['.kick ' + inMSG[4] + ' Gtfo <3',  inMSG[1], inMSG[2], inMSG[3], inMSG[4], 'daisy@69.196.165.57'])

def load():
        return autokick_channel
