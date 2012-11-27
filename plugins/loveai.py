import random
plugName = 'Love AI'

def loveai_send(inMSG, msg):
    time.sleep (random.randint(2,6))
    sendMSG(msg, inMSG[1], inMSG[2], inMSG[3])

def loveai_Namine(inMSG):
    if not inMSG or len(inMSG) != 6:
        return
    if inMSG[4] == 'Daisy':
        if inMSG[0] == 'I love you, Namine' or inMSG[0] == 'I love you, Namine ':
            loveai_send(inMSG, 'I love you too, Daisy~! <3')
        elif inMSG[0] == 'Hello Namine' or inMSG[0] == 'Hello, Namine' or inMSG[0] == 'Hello, Namine ':
            loveai_send(inMSG, 'Hello, Daisy-kun <3')
        elif inMSG[0] == 'How do you do, love?':
            loveai_send(inMSG, 'I am very well, thank you~')
    if inMSG[0] == 'Namine, what do you look like?' or inMSG[0] == 'Namine: what do you look like?' or inMSG[0] == 'What do you look like, Namine?':
        loveai_send(inMSG, 'https://www.dropbox.com/s/7v9742czmug4jze/namine.jpg')
   # elif 'Namine' in inMSG[0] and inMSG[4] != 'Daisy':
    #    loveai_send(inMSG, 'Pardon me?')       

def load():
        return loveai_Namine
