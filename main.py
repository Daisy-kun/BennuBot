import threading, time, socket, re, sqlite3
from datetime import date
#TODO Garbage collection for unused "outMSG" data
#TODO Alternative hash authentication
#TODO Protocol to integrate GitHub commits with JSON POST

#Database location
dbLoc = 'db'

#Please don't change anything below this line then complain when something breaks
version = 1
admins = {}
funcs = {}
genFuncs = []
protocols = {}

plugName = None
load = None
plugAdmins = None

change = False

def log(text, location='log'):
    msg = time.strftime('%Y-%m-%d %H:%M:%S') + '\t' + text
    try: print msg
    except: None
    open(location, 'a').write(msg + '\r\n')

def delSetting(table, what, conn=None):
    #TODO Make a real fix
    table = table.replace('\'', '')
    what = what.replace('\'', '')

    if not conn:
        conn = sqlite3.connect(dbLoc)
        dontClose = False
    else:
        dontClose = True

    c = conn.cursor()

    try:
        c.execute("delete from "+table+" where id='"+what+"'")
    except:
        return False

    conn.commit()

    if not dontClose:
        conn.close()

    return True

def setSetting(table, what, to, conn=None):
    #TODO Make a real fix
    table = table.replace('\'', '')
    what = what.replace('\'', '')

    vStr = ''
    tStr = ''

    if not conn:
        conn = sqlite3.connect(dbLoc)
        dontClose = False
    else:
        dontClose = True

    c = conn.cursor()

    for i in to.items():
        #TODO Fix this with prepared statements or something
        if type(i[1]) is str:
            temp = i[1].replace('\'', '')
        else:
            temp = i[1]
        vStr += ",'%s'" % temp
        if type(i[1]) is str:
            tType = 'text'
        elif type(i[1]) is int:
            tType = 'integer'
        elif type(i[1]) is float:
            tType = 'real'
        elif type(i[1]) is type(None):
            tType = 'null'
        else:
            tType = 'blob'
        tStr += ",%s %s" % (i[0], tType)

    c.execute("create table if not exists "+table+"(id text primary key"+tStr+")")
    c.execute("replace into "+table+" values ('"+what+"'"+vStr+")")

    conn.commit()

    if not dontClose:
        conn.close()

def getSetting(table, what, conn=None):
    #TODO Make a real fix
    table = table.replace('\'', '')
    what = what.replace('\'', '')

    out = []

    if not conn:
        conn = sqlite3.connect(dbLoc)
        dontClose = False
    else:
        dontClose = True

    c = conn.cursor()

    try:
        c.execute("select * from "+table+" where id='"+what+"'")
    except:
        return False

    for i in c:
        out += [i]

    if not dontClose:
        conn.close()

    return out

def loadSettings():
    global protoList, plugList, protoFolder, plugFolder, nick, quiet, funcPrefix, protoPrefix, inMSG
    global outMSG, mainWait

    #MSG, Protocol, Server, Channel, Nick, UID (May be "None")
    inMSG = []
    #MSG, Protocol, Server, Channel (May be "None")
    outMSG = []

    v = getSetting("System", "version")
    if v:
        if int(v[0][1]) != version:
            log('WARNING BennuBot version different from db version (Current: '+str(v[0][1])+' Expected: '+
                str(version)+')')
            log('Attempting to run patch to address potential issues')
            try:
                name = str(v[0][1]) + '_' + str(version) + '.py'
                eval(compile(open('patches/'+name, 'U').read(), name, 'exec'), globals())
                log('Patch appears to have executed successfully')
                return
            except:
                log('Failed to execute patch, maintaining course ...')

        conn = sqlite3.connect(dbLoc)
        protoList = getSetting("System", "protoList", conn)[0][1].split(',')
        plugList = getSetting("System", "plugList", conn)[0][1].split(',')
        protoFolder = str(getSetting("System", "protoFolder", conn)[0][1])
        plugFolder = str(getSetting("System", "plugFolder", conn)[0][1])
        nick = str(getSetting("System", "nick", conn)[0][1])
        quiet = str(getSetting("System", "quiet", conn)[0][1])
        funcPrefix = str(getSetting("System", "funcPrefix", conn)[0][1])
        protoPrefix = str(getSetting("System", "protoPrefix", conn)[0][1])
        mainWait = float(getSetting("System", "mainWait", conn)[0][1])
        conn.close()
    else:
        log("No db found, making a new one...")
        protoList = ['irc.py'] #Protocols to be loaded
        plugList  = ['say.py', 'pyexec.py', 'irc_commands.py', 'ircop_commands.py', 'time.py',
                     'google.py', 'downloader.py', 'remoteadmin.py', 'titlespam.py', 'tell.py',
                     'loli.py', 'factoids.py'] 
                               #Plugins to be loaded

        protoFolder = 'protocols/'
        plugFolder   = 'plugins/'

        nick = 'BennuBot'

        quiet = True
        funcPrefix = '.'
        protoPrefix = ';'

        mainWait = 0.01

        conn = sqlite3.connect(dbLoc)
        setSetting("System", "version", {"Value":version}, conn)
        setSetting("System", "protoList", {"Value":','.join(protoList)}, conn)
        setSetting("System", "plugList", {"Value":','.join(plugList)}, conn)
        setSetting("System", "protoFolder", {"Value":protoFolder}, conn)
        setSetting("System", "plugFolder", {"Value":plugFolder}, conn)
        setSetting("System", "nick", {"Value":nick}, conn)
        setSetting("System", "quiet", {"Value":int(quiet)}, conn)
        setSetting("System", "funcPrefix", {"Value":funcPrefix}, conn)
        setSetting("System", "protoPrefix", {"Value":protoPrefix}, conn)
        setSetting("System", "mainWait", {"Value":mainWait}, conn)
        conn.close()

def loadProtocol(location, name):
    global protocols, plugName, load, plugAdmins, admins
    plugName = None
    load = None
    plugAdmins = None
    try:
        eval(compile(open(location, 'U').read(), name, 'exec'), globals())
        if plugName: name = plugName
        if not load:
            log('Protocol \"' + name + '\" must define \'load\'.')
            return False
        protocols = dict(protocols.items() + load().items())
    except:
        log('Protocol \"' + name + '\" failed to load.')
        return False
    try:
        admins = dict(admins.items() + plugAdmins.items())
    except:
        log('Protocol \"' + name + '\" has not specified any admins.')
    log('Protocol \"' + name + '\" loaded.')
    return True 

#Load all protocols from "protoList".
def loadProtocols():
    global protocols
    protocols = {}
    for i in protoList:
        loadProtocol(protoFolder + i, i)

def loadPlugin(location, name):
    global funcs, genFuncs, plugName, load
    plugName = None
    load = None
    try:
        eval(compile(open(location, 'U').read(), name, 'exec'), globals())
        if plugName: name = plugName
        if not load:
            log('Plugin \"' + name + '\" must define \'load\'.')
            return False
        plugin = load()
        if type(plugin).__name__ == 'dict':
            funcs = dict(funcs.items() + plugin.items())
        elif type(plugin).__name__ == 'function':
            genFuncs += [plugin]
        else:
            log('Plugin \"' + name + '\" must return \'dict\' or \'function\'.')
            return False
    except:
        log('Plugin \"' + name + '\" failed to load.')
        return False

    log('Plugin \"' + name + '\" loaded.')
    return True     

#Load all plugins from "plugList".
def loadPlugins():
    global funcs, genFuncs
    funcs = {}
    genFuncs = []
    for i in plugList:
        loadPlugin(plugFolder + i, i)

#Sends message
def sendMSG(msg, protocol, server, channel):
    handleGenFuncs([msg, protocol, server, channel])
    global outMSG
    outMSG.append([msg, protocol, server, channel])

def getPermission(inMSG):
    try:
        for i in admins[inMSG[1]]:
            if re.search(re.sub('\\\\\*', '.*', re.escape(i[0])), inMSG[5]):
                return i[1]
    except:
        return 0
    return 0

#Handles throwing the general functions into threads
def handleGenFuncs(command=None):
    for i in genFuncs:
        try:
            handleGenFunc(i, command).start()
        except:
            if not quiet:
                outMSG.append(['Error starting a general function. Too many threads?', self.command[1],
                        self.command[2], self.command[3]])
            time.sleep(0.01)

#Handles running the general functions
class handleGenFunc(threading.Thread):

    def __init__(self, func, command=None):
        self.command = command
        self.func = func
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.func(self.command)
        except:
            #TODO Output function name which had the error.
            outMSG.append(['A plugin had an error.', self.command[1], self.command[2], self.command[3]])       

#Parses a command.
class parseCommand(threading.Thread):

    def __init__(self, command):
        self.command = command
        threading.Thread.__init__(self)

    def run(self):
        if len(self.command[0]) > 1 and self.command[0][:len(funcPrefix)] == funcPrefix:
            cmd = self.command[0].split(None, 1)[0][len(funcPrefix):].lower()
            if cmd in funcs:
                try:
                    result = funcs[cmd](self.command)
                    if result:
                        sendMSG(result, self.command[1], self.command[2], self.command[3])
                except Exception as e:
                    sendMSG('Command \"'+cmd+'\" caused error: '+str(e)+'.',
                        self.command[1], self.command[2], self.command[3])
            elif not quiet:
                 sendMSG('Invalid command.', self.command[1], self.command[2], self.command[3])
        elif len(self.command[0]) > 1 and self.command[0][:len(protoPrefix)] == protoPrefix:
            if getPermission(self.command) < 999:
                if not quiet:
                    sendMSG('Not authorized.', self.command[1], self.command[2],
                        self.command[3])
                return
            cmd = self.command[0].split(None, 1)[0][len(protoPrefix):].lower()
            if cmd in protocols:
                try:
                    result = protocols[cmd](self.command)
                    if result:
                        sendMSG(result, self.command[1], self.command[2], self.command[3])
                except Exception as e:
                    sendMSG('Command \"'+cmd+'\" caused error: '+str(e)+'.',
                        self.command[1], self.command[2], self.command[3])
            elif not quiet:
                sendMSG('Invalid command.', self.command[1], self.command[2], self.command[3])

log('Loading Settings...')
loadSettings()
log('Loading Protocols...')
loadProtocols()
log('Loading Plugins...')
loadPlugins()
log('Entering main loop...')

while True:
    if not change:
        #General plugins should prepare for "None".
        handleGenFuncs()
        #As long as plugins are handling their timeouts properly 10ms should be plenty.
        time.sleep(mainWait)
    else:
        change = False
    for i in inMSG:
        if not change: change = True
        parseCommand(i).start()
        handleGenFuncs(i)
        del inMSG[0]
