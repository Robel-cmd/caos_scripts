import bs
import bsInternal
import bsPowerup
import bsUtils
import random
import json
import coinSystem
from threading import Timer
import AutoAdmin
from settings import *
import cmdsetg
import floater
import re
import datetime
import logger
import os
import handleRol
import mystats

from logger import storage


reply = None

stats = logger.stats
pStats = logger.pStats
roles = storage.roles

def extract_command(msg):
    for prefix in prefixComand:
        if msg.startswith(prefix):
            return msg[len(prefix):].split(' ')[0].lower() # lower() Por si Escriben en Mayusculas...
    return
            
def accountIDFromClientID(n):
    """retorna el account_id del jugador"""
    if len(str(n)) > 1:
        for i in bsInternal._getForegroundHostActivity().players:
            if int(i.getInputDevice().getClientID()) == int(n):
                return i.get_account_id()
    else:
        if int(n) < len(bsInternal._getForegroundHostActivity().players):
            return bsInternal._getForegroundHostActivity().players[int(n)].get_account_id()
    
    
    return None


def getDisplayString(n):
    """Retorna el name del jugador"""
    for i in bsInternal._getGameRoster():
        if i['clientID'] == int(n):
            return i['displayString']

    return None


def playerFromClientID(n):
    """Retorna el jugador indexado"""
    if len(n) > 1:
        for i in bsInternal._getForegroundHostActivity().players:
            if str(i.getInputDevice().getClientID()) == n:
                return i
    else:
        if int(n) < len(bsInternal._getForegroundHostActivity().players):
            return bsInternal._getForegroundHostActivity().players[int(n)]
    
    return None #'Player Not Found'


class Custom(object):

    def __init__(self, id, tag):
        self.id = id
        self.tag = tag


def make_custom(id, tag):
    custom = Custom(id, tag)
    return custom


class chatOptions(object):

    def __init__(self):
        self.all = True
        self.tint = None
        return

    def checkDevice(self, clientID, command):
        global commandByCoin
        global commandSuccess
        global costOfCommand
        global reply
        global user
        global roles
        commandByCoin = None
        commandSuccess = None
        reply = None
        client_str = ''
        for i in bsInternal._getForegroundHostActivity().players:
            if i.getInputDevice().getClientID() == clientID:
                player = i
                break
        else:
            return None
        rol = handleRol.ver_roles()
        client_str = player.get_account_id()
        try:
            if client_str in rol['owners']:
                reply = u'\ue043|\ue00cCOMMAND ACCEPTED MY LORD\ue00c|\ue043'
                # reply = ':)'
                return 10
            elif client_str in rol['admins']:
                reply = u'\ue049|\ue00cCOMMAND ACCEPTED MR:ADMIN\ue00c|\ue049'
                # reply = ':)'
                return 3
            elif client_str in rol['vips']:
                reply = u'\ue048|\ue00cVIP COMMAND ACCEPTED\ue00c|\ue048'
                # reply = ':)'
                return 2
            elif enableCoinSystem and command in availableCommands:
                costOfCommand = availableCommands[command]
                haveCoins = coinSystem.getCoins(client_str)
                if haveCoins >= costOfCommand:
                    commandByCoin = True
                    user = client_str
                    return 3
                bsInternal._chatMessage('You need ' + bs.getSpecialChar('ticket') + str(
                    costOfCommand) + ' for that. You have ' + bs.getSpecialChar('ticket') + str(haveCoins) + ' only.')
            elif enableTop5commands and client_str in rol['toppers']:
                reply = 'Top 5 player, COMMAND ACCEPTED'
                # reply = ':)'
                return 1
            return 0

        except:
            pass

        return 0
    def get_playerstats(self):
        with open(pStats, 'r') as f:
            try:
                _stats = json.loads(f.read())
            except Exception:
                return None
        return _stats
    def getstats(self):
        with open(stats, 'r') as f:
            try:
                _stats = json.loads(f.read())
            except Exception:
                return None
        return _stats
    def scoretocash(self, player, score, clientID):
        try:
            stat = self.getstats()
            accountID = player.get_account_id()
            haveScore = stat[str(accountID)]['scores']
            if haveScore < score:
                bsInternal._chatMessage('Not enough scores to perform the transaction')
            elif score < 500:
                bsInternal._chatMessage('You can only convert more than 500scores')
            else:
                stat[str(accountID)]['scores'] -= score
                mystats.commit_stats(stat)
                equivalentCoins = int(score / 5 * 0.9)
                coinSystem.addCoins(accountID, equivalentCoins)
                bs.screenMessage('Transaction Successful', color=(0, 1, 0))
                bsInternal._chatMessage(bs.getSpecialChar('ticket') + str(equivalentCoins) + ' added to your account. [10% transaction fee deducted]')
                mystats.refreshStats()

        except Exception as e:
            print(e)
            bs.screenMessage('Usage: /scoretocash amount_of_score', transient=True, color=(1,
                                                                                0.1,
                                                                                0.1), clients=[clientID])
    def cashtoscore(self, player, coins, clientID):
        try:
            stat = self.getstats()
            accountID = player.get_account_id()
            haveCoins = coinSystem.getCoins(accountID)
            if haveCoins < coins:
                bsInternal._chatMessage(
                    'Not enough ' + bs.getSpecialChar('ticket') + ' to perform the transaction')
            elif coins < 100:
                bsInternal._chatMessage(
                    'You can only convert more than ' + bs.getSpecialChar('ticket') + '100')
            else:
                coinSystem.addCoins(accountID, coins * -1)
                equivalentScore = int(coins * 5 * 0.9)
                stat[str(accountID)]['scores'] += equivalentScore
                mystats.commit_stats(stat)
                bs.screenMessage(
                    'Transaction Successful', color=(0, 1, 0))
                bsInternal._chatMessage(str(
                    equivalentScore) + 'score added to your account stats. [10% transaction fee deducted]')
                mystats.refreshStats()

        except Exception as e:
            print e
            bs.screenMessage('Usage: /cashtoscore amount_of_cash', transient=True, color=(1,
                                                                                            0.1,
                                                                                            0.1), clients=[clientID])


                        
    def me(self, player, clientID):
        pats = self.get_playerstats()
        accountID = player.get_account_id()
        string = ""
        if not isinstance(player, bs.Player):
            return
        if accountID in pats:
            if enableCoinSystem:
                haveCoins = coinSystem.getCoins(accountID)
                string = '|| ' + player.getName() + ' | Wallet:' + bs.getSpecialChar('ticket') + str(haveCoins) + ' | Rank:' + pats[str(accountID)]['rank'] + ' | Games:' + pats[str(
                    accountID)]['games'] + ' | Score:' + pats[str(accountID)]['scores'] + ' | Kills:' + pats[str(accountID)]['kills'] + ' | Deaths:' + pats[str(accountID)]['deaths'] + ' ||'
            else:
                string = '|| ' + player.getName() + ' | Rank:' + pats[str(accountID)]['rank'] + ' | Games:' + pats[str(accountID)]['games'] + ' | Score:' + pats[str(
                    accountID)]['scores'] + ' | Kills:' + pats[str(accountID)]['kills'] + ' | Deaths:' + pats[str(accountID)]['deaths'] + ' ||'
            #bsInternal._chatMessage(string)
            
        else:
            string = "No estas registrado."
        
        bs.screenMessage(string, transient=True, clients=[clientID])
        
    def kickByNick(self, nick):
        roster = bsInternal._getGameRoster()
        for i in roster:
            try:
                if i['players'][0]['nameFull'].lower().find(nick.encode('utf-8').lower()) != -1:
                    bsInternal._disconnectClient(int(i['clientID']))
            except:
                pass

    def opt(self, clientID, msg):
        global commandSuccess
        global stats
        global pStats
        global roles
        try:
            m = extract_command(msg)
            a = msg.split(' ')[1:]
            activity = bsInternal._getForegroundHostActivity()
            with bs.Context(activity):
                for i in activity.players:
                    if i.getInputDevice().getClientID() == clientID:
                        player = i
                        break
                else:
                    return
                if player is None:
                    return
                level = self.checkDevice(clientID, m)
                if m in ('stats', 'rank', 'myself', 'me'):
                    if a == []:
                        self.me(player, clientID)
                elif (m == 'emote') or (m == 'em'):
                    if a == []:
                        bs.screenMessage(
                            "Available Emotes fire, angry, lol, dead, huh, what, power")
                    if a[0] == 'fire':
                        ptxt = u'\U0001F525'
                    elif a[0] == 'angry':
                        ptxt = u'\U0001F4A2'
                    elif a[0] == 'lol':
                        ptxt = u'\U0001F602'
                    elif a[0] == 'dead':
                        ptxt = u'\U0001F480'
                    elif a[0] == 'huh':
                        ptxt = u'\U0001F60F'
                    elif a[0] == 'what':
                        ptxt = u'\U0001F611'
                    elif a[0] == 'power':
                        ptxt = u'\U0001F4AA'

                    def CidToActor(cid):
                        for s in bsInternal._getForegroundHostSession().players:
                            try:
                                pcid = int(s.getInputDevice().getClientID())
                            except:
                                continue
                            if pcid == int(cid):
                                return s.actor
                        return None
                    bsUtils.PopupText(ptxt,
                                      scale=2.0,
                                      position=CidToActor(clientID).node.position).autoRetain()
                elif m == 'teamName' and level > 2:
                    if a == []:
                        bs.screenMessage("Try teamName Red Blue")
                        bsInternal._chatMessage(
                            u"Few Emotes \U0001F480,\ue00c,\ue048,\ue046,\ue043")
                    else:
                        cmdsetg.tN(a[0], a[1])
                        commandSuccess = True
                elif m == 'floater' and level > 2:
                    playerlist = bsInternal._getForegroundHostActivity(
                    ).players
                    if not hasattr(bsInternal._getForegroundHostActivity(),
                                   'flo'):
                        # import floater
                        bsInternal._getForegroundHostActivity().flo = floater.Floater(
                            bsInternal._getForegroundHostActivity()._mapType())
                    floaters = bsInternal._getForegroundHostActivity().flo
                    if floaters.controlled:
                        bs.screenMessage(
                            'Floater is already being controlled',
                            color=(1, 0, 0))
                        return
                    for i in playerlist:
                        if i.getInputDevice().getClientID() == clientID:
                            clientID = i.getInputDevice().getClientID()
                            bs.screenMessage(
                                'You\'ve Gained Control Over The Floater!\nPress Bomb to Throw Bombs and Punch to leave!\nYou will automatically get released after some time!',
                                clients=[clientID],
                                transient=True,
                                color=(0, 1, 1))

                            def dis(i, floaters):
                                i.actor.node.invincible = False
                                i.resetInput()
                                i.actor.connectControlsToPlayer()
                                floaters.dis()

                            # bs.gameTimer(15000,bs.Call(dis,i,floater))
                            ps = i.actor.node.position
                            i.actor.node.invincible = True
                            floaters.node.position = (ps[0], ps[1] + 1.5,
                                                      ps[2])
                            i.actor.node.holdNode = bs.Node(None)
                            i.actor.node.holdNode = floaters.node2
                            i.actor.disconnectControlsFromPlayer()
                            i.resetInput()
                            floaters.sourcePlayer = i
                            floaters.con()
                            i.assignInputCall('pickUpPress', floaters.up)
                            i.assignInputCall('pickUpRelease', floaters.upR)
                            i.assignInputCall('jumpPress', floaters.down)
                            i.assignInputCall('jumpRelease', floaters.downR)
                            i.assignInputCall('bombPress', floaters.drop)
                            i.assignInputCall('punchPress',
                                              bs.Call(dis, i, floaters))
                            i.assignInputCall('upDown', floaters.updown)
                            i.assignInputCall('leftRight',
                                              floaters.leftright)

                elif m == 'perk':
                    if a == []:
                        bs.screenMessage("Try /perk heal, damage , health")
                    for i in bsInternal._getForegroundHostSession().players:
                        if i.getInputDevice().getClientID() == clientID:
                            acid = i.get_account_id()
                            f = open(pStats, "r")
                            pats = json.loads(f.read())
                            if acid in pats:
                                kill = pats[acid]["kills"]
                                death = pats[acid]["deaths"]
                                k_d = str(float(kill)/float(death))[:3]
                                if a[0] == "damage":
                                    if int(kill) >= 100:
                                        cmdsetg.damage(acid)
                                    else:
                                        bs.screenMessage(
                                            "You Have Less Kills "+str(kill)+'/100', color=(1, 0, 0))
                                if a[0] == "heal":
                                    if float(k_d) >= 1.3:
                                        cmdsetg.heal(acid)
                                    else:
                                        bs.screenMessage(
                                            "You Must Have 1.3 K/D Ratio!, Your K/D Is "+str(k_d))
                                if a[0] == "health":
                                    if int(kill) >= 100 and float(k_d) >= 1.3:
                                        cmdsetg.health(acid)
                                    else:
                                        bs.screenMessage(
                                            "You Must Have 1.3 K/D Ratio And 100 Kills")
                            else:
                                bs.screenMessage("You Are Not Yet Registerd")

                elif m == 'smg':
                    ptxt = str(a[0])

                    def CidToActor(cid):
                        for s in bsInternal._getForegroundHostSession().players:
                            try:
                                pcid = int(s.getInputDevice().getClientID())
                            except:
                                continue
                            if pcid == int(cid):
                                return s.actor
                        return None
                    bsUtils.PopupText(ptxt,
                                      scale=2.0,
                                      position=CidToActor(clientID).node.position).autoRetain()
                elif m == 'donate' and enableCoinSystem:
                    try:
                        if len(a) < 2:
                            bs.screenMessage(
                                'Usage: /donate amount clientID', transient=True, clients=[clientID])
                        else:
                            transfer = int(a[0])
                            if transfer < 100:
                                bsInternal._chatMessage(
                                    'You can only transfer more than ' + bs.getSpecialChar('ticket') + '100.')
                                return
                            sendersID = None
                            receiversID = None
                            for player in activity.players:
                                clID = player.getInputDevice().getClientID()
                                aid = player.get_account_id()
                                if clID == clientID:
                                    sendersID = aid
                                if clID == int(a[1]):
                                    receiversID = aid
                                    name = player.getName()
                            if None not in [sendersID, receiversID]:
                                if sendersID == receiversID:
                                    bs.screenMessage(
                                        'You can\'t transfer to your own account', color=(1, 0, 0))
                                elif coinSystem.getCoins(sendersID) < transfer:
                                    bsInternal._chatMessage(
                                        'Not enough ' + bs.getSpecialChar('ticket') + ' to perform transaction')
                                else:
                                    coinSystem.addCoins(
                                        sendersID, int(transfer * -1))
                                    coinSystem.addCoins(
                                        receiversID, int(transfer))
                                    bsInternal._chatMessage('Successfully transfered ' + bs.getSpecialChar(
                                        'ticket') + a[0] + ' into ' + name + "'s account.")
                            else:
                                bs.screenMessage(
                                    'Player not Found', color=(1, 0, 0))
                    except:
                        bs.screenMessage('Usage: /donate amount clientID',
                                         transient=True, clients=[clientID])

                elif m == 'buy' and enableCoinSystem:
                    if a == []:
                        bsInternal._chatMessage('Usaage: /buy item_name')
                    elif a[0] in availableEffects:
                        effect = a[0]
                        client_str = None
                        for i in bsInternal._getForegroundHostActivity().players:
                            if i.getInputDevice().getClientID() == clientID:
                                client_str = i.get_account_id()

                        if client_str is not None:
                            costOfEffect = availableEffects[effect]
                            haveCoins = coinSystem.getCoins(client_str)
                            if haveCoins >= costOfEffect:
                                customers = storage.customers
                                from datetime import datetime, timedelta
                                expiry = datetime.now() + timedelta(days=7)
                                
                                if client_str not in customers:
                                    customers[client_str] = {
                                        'effects': {effect: expiry.strftime('%d-%m-%Y %H:%M:%S')}}
                                if effect == 'tag':
                                    tag = ' '.join(a[1:])
                                    if len(tag) > 15:
                                        bs.screenMessage(
                                            "Elige un tag mas corto!")
                                        return
                                    tag = bs.uni(tag)
                                    customers[client_str]["tag"] = tag
                                customers[client_str]['effects'].update({
                                    effect: expiry.strftime('%d-%m-%Y %H:%M:%S')})
                                coinSystem.commit_custom()
                                bsInternal._chatMessage(
                                    'Success! That cost you ' + bs.getSpecialChar('ticket') + str(costOfEffect))
                                coinSystem.addCoins(
                                    client_str, costOfEffect * -1)
                                bs.playSound(bs.getSound('ding'), volume=5)
                            else:
                                bsInternal._chatMessage('You need ' + bs.getSpecialChar('ticket') + str(
                                    costOfEffect) + ' for that. You have ' + bs.getSpecialChar('ticket') + str(haveCoins) + ' only.')

                elif m == 'list':
                    # string = u'==Name========ClientID====PlayerID==\n'
                    string = u'{0:^16}{1:^15}{2:^10}\n------------------------------------------------------------------------------\n'.format(
                        'Name', 'ClientID', 'PlayerID')
                    for s in bsInternal._getForegroundHostSession().players:
                        # string += s.getName()  '========' + str(s.getInputDevice().getClientID()) + '====' + str(bsInternal._getForegroundHostSession().players.index(s)) + '\n'
                        string += u'{0:^16}{1:^15}{2:^10}\n'.format(s.getName(True, True), str(s.getInputDevice(
                        ).getClientID()), str(bsInternal._getForegroundHostSession().players.index(s)))
                    bs.screenMessage(string, transient=True,
                                     color=(1, 1, 1), clients=[clientID])
                    # print string

                elif m == 'shop' and enableCoinSystem:
                    string = '==You can buy following items==\n'
                    if a == []:
                        bs.screenMessage('Usage: /shop commands or /shop effects', transient=True, color=(1,
                                                                                                          0.1,
                                                                                                          0.1), clients=[clientID])
                    elif a[0] == 'effects':
                        for x in availableEffects:
                            string += x + '----' + \
                                bs.getSpecialChar(
                                    'ticket') + str(availableEffects[x]) + '----for 1 day\n'

                        bs.screenMessage(string, transient=True,
                                         color=(0, 1, 0), clients=[clientID])
                    elif a[0] == 'commands':
                        separator = '          '
                        for x in availableCommands:
                            string += x + '----' + \
                                bs.getSpecialChar(
                                    'ticket') + str(availableCommands[x]) + separator
                            if separator == '          ':
                                separator = '\n'
                            else:
                                separator = '          '
                        bs.screenMessage(string, transient=True,
                                         color=(0, 1, 0), clients=[clientID])
                elif m == 'id':
                    if True:
                        clID = int(a[0])
                        for i in bsInternal._getForegroundHostActivity().players:
                            if i.getInputDevice().getClientID() == clID:
                                bsInternal._chatMessage(
                                    i.get_account_id())
                                commandSuccess = True
                elif m == 'cashtoscore' and enableCoinSystem:
                    if a != []:
                        self.cashtoscore(player, int(a[0]), clientID)
                elif m == 'scoretocash' and enableCoinSystem:
                    if a != []:
                        self.scoretocash(player, int(a[0]), clientID)    

                elif level > 0:
                    if m == 'nv':
                        if self.tint is None:
                            self.tint = bs.getSharedObject('globals').tint
                        bs.getSharedObject('globals').tint = (0.5, 0.7, 1) if a == [
                        ] or not a[0] == 'off' else self.tint
                        commandSuccess = True
                    elif m == 'ooh':
                        if a is not None and len(a) > 0:
                            s = 1
                            #int(a[0])

                            def oohRecurce(c):
                                bs.playSound(bs.getSound('ooh'), volume=2)
                                c -= 1
                                if c > 0:
                                    bs.gameTimer(int(a[1]) if len(
                                        a) > 1 and a[1] is not None else 1000, bs.Call(oohRecurce, c=c))
                                return

                            oohRecurce(c=s)
                        else:
                            bs.playSound(bs.getSound('ooh'), volume=2)
                        commandSuccess = True
                    elif m == 'playSound':
                        if a is not None and len(a) > 1:
                            s = 1
                            #int(a[1])

                            def oohRecurce(c):
                                bs.playSound(bs.getSound(str(a[0])), volume=2)
                                c -= 1
                                if c > 0:
                                    bs.gameTimer(int(a[2]) if len(
                                        a) > 2 and a[2] is not None else 1000, bs.Call(oohRecurce, c=c))
                                return

                            oohRecurce(c=s)
                        else:
                            bs.playSound(bs.getSound(str(a[0])), volume=2)
                        commandSuccess = True
                    elif m == 'death':
                                i.actor.node.handleMessage(
                                bs.DieMessage())
                    elif m in ('box', 'boxall'):
                        try:
                            if m == 'boxall':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.node.torsoModel = bs.getModel(
                                            'tnt')
                                        i.actor.node.colorMaskTexture = bs.getTexture(
                                            'tnt')
                                        i.actor.node.colorTexture = bs.getTexture(
                                            'tnt')
                                        i.actor.node.highlight = (1, 1, 1)
                                        i.actor.node.color = (1, 1, 1)
                                        i.actor.node.headModel = None
                                        i.actor.node.style = 'cyborg'
                                    except:
                                        print 'error'

                                commandSuccess = True
                            elif a == []:
                                bsInternal._chatMessage(
                                    'Usage: /boxall or /box player_code')
                            else:
                                try:
                                    n = int(a[0])
                                    bs.getSession().players[n].actor.node.torsoModel = bs.getModel(
                                        'tnt')
                                    bs.getSession().players[n].actor.node.colorMaskTexture = bs.getTexture(
                                        'tnt')
                                    bs.getSession().players[n].actor.node.colorTexture = bs.getTexture(
                                        'tnt')
                                    bs.getSession().players[n].actor.node.highlight = (1,
                                                                                       1,
                                                                                       1)
                                    bs.getSession().players[n].actor.node.color = (1, 1,
                                                                                   1)
                                    bs.getSession(
                                    ).players[n].actor.node.headModel = None
                                    bs.getSession(
                                    ).players[n].actor.node.style = 'cyborg'
                                    commandSuccess = True
                                except:
                                    bsInternal._chatMessage(
                                        'Usage: /boxall or /box player_code')

                        except:
                            bs.screenMessage('Error!', color=(1, 0, 0))

                    elif m in ('spaz', 'spazall'):
                        try:
                            if a == []:
                                bsInternal._chatMessage(
                                    'Failed!! Usage: /spazall or /spaz number of list')
                            elif m == 'spazall':
                                for i in bs.getSession().players:
                                    a.append(a[0])
                                    t = i.actor.node
                                    try:
                                        if a[1] in ['ali', 'neoSpaz', 'wizard', 'cyborg', 'penguin', 'agent', 'pixie', 'bear', 'bunny']:
                                            t.colorTexture = bs.getTexture(
                                                a[1] + 'Color')
                                            t.colorMaskTexture = bs.getTexture(
                                                a[1] + 'ColorMask')
                                            t.headModel = bs.getModel(
                                                a[1] + 'Head')
                                            t.torsoModel = bs.getModel(
                                                a[1] + 'Torso')
                                            t.pelvisModel = bs.getModel(
                                                a[1] + 'Pelvis')
                                            t.upperArmModel = bs.getModel(
                                                a[1] + 'UpperArm')
                                            t.foreArmModel = bs.getModel(
                                                a[1] + 'ForeArm')
                                            t.handModel = bs.getModel(
                                                a[1] + 'Hand')
                                            t.upperLegModel = bs.getModel(
                                                a[1] + 'UpperLeg')
                                            t.lowerLegModel = bs.getModel(
                                                a[1] + 'LowerLeg')
                                            t.toesModel = bs.getModel(
                                                a[1] + 'Toes')
                                            t.style = a[1]
                                    except:
                                        print 'error'
                                    else:
                                        commandSuccess = True

                            else:
                                try:
                                    if a[1] in ['ali', 'neoSpaz', 'wizard', 'cyborg', 'penguin', 'agent', 'pixie', 'bear', 'bunny']:
                                        n = int(a[0])
                                        t = bs.getSession(
                                        ).players[n].actor.node
                                        t.colorTexture = bs.getTexture(
                                            a[1] + 'Color')
                                        t.colorMaskTexture = bs.getTexture(
                                            a[1] + 'ColorMask')
                                        t.headModel = bs.getModel(
                                            a[1] + 'Head')
                                        t.torsoModel = bs.getModel(
                                            a[1] + 'Torso')
                                        t.pelvisModel = bs.getModel(
                                            a[1] + 'Pelvis')
                                        t.upperArmModel = bs.getModel(
                                            a[1] + 'UpperArm')
                                        t.foreArmModel = bs.getModel(
                                            a[1] + 'ForeArm')
                                        t.handModel = bs.getModel(
                                            a[1] + 'Hand')
                                        t.upperLegModel = bs.getModel(
                                            a[1] + 'UpperLeg')
                                        t.lowerLegModel = bs.getModel(
                                            a[1] + 'LowerLeg')
                                        t.toesModel = bs.getModel(
                                            a[1] + 'Toes')
                                        t.style = a[1]
                                        commandSuccess = True
                                except:
                                    bsInternal._chatMessage(
                                        'Failed!! Usage: /spazall or /spaz number of list')

                        except:
                            bs.screenMessage('error', color=(1, 0, 0))

                    elif m in ('inv', 'invall'):
                        try:
                            if m == 'invall':
                                for i in bs.getSession().players:
                                    t = i.actor.node
                                    t.headModel = None
                                    t.torsoModel = None
                                    t.pelvisModel = None
                                    t.upperArmModel = None
                                    t.foreArmModel = None
                                    t.handModel = None
                                    t.upperLegModel = None
                                    t.lowerLegModel = None
                                    t.toesModel = None
                                    t.style = 'cyborg'

                                commandSuccess = True
                            elif a == []:
                                bsInternal._chatMessage(
                                    'Failed!! Usage: /invall or /inv number of list')
                            else:
                                try:
                                    n = int(a[0])
                                    t = bs.getSession().players[n].actor.node
                                    t.headModel = None
                                    t.torsoModel = None
                                    t.pelvisModel = None
                                    t.upperArmModel = None
                                    t.foreArmModel = None
                                    t.handModel = None
                                    t.upperLegModel = None
                                    t.lowerLegModel = None
                                    t.toesModel = None
                                    t.style = 'cyborg'
                                    commandSuccess = True
                                except:
                                    bsInternal._chatMessage(
                                        'Failed!! Usage: /invall or /inv number of list')

                        except:
                            bs.screenMessage('error', color=(1, 0, 0))

                    # elif m == '/bunnyNOtavailabehere':
                    #     if a == []:
                    #         bsInternal._chatMessage(
                    #             'Using: /bunny count owner(number of list)')
                    #     import BuddyBunny
                    #     for i in range(int(a[0])):
                    #         p = bs.getSession().players[int(a[1])]
                    #         if 'bunnies' not in p.gameData:
                    #             p.gameData['bunnies'] = BuddyBunny.BunnyBotSet(p)
                    #         p.gameData['bunnies'].doBunny()

                    elif m in ('tex', 'texall'):
                        if m == 'texall':
                            for i in bs.getSession().players:
                                try:
                                    i.actor.node.colorMaskTexture = bs.getTexture(
                                        'egg1')
                                    i.actor.node.colorTexture = bs.getTexture(
                                        'egg1')
                                except:
                                    print 'error'
                                else:
                                    commandSuccess = True

                        elif a == []:
                            bsInternal._chatMessage(
                                'Failed!! Usage: /texall or /tex number of list')
                        else:
                            try:
                                n = int(a[0])
                                bs.getSession().players[n].actor.node.colorMaskTexture = bs.getTexture(
                                    'egg1')
                                bs.getSession().players[n].actor.node.colorTexture = bs.getTexture(
                                    'egg1')
                                commandSuccess = True
                            except:
                                bs.screenMessage('Error!', color=(1, 0, 0))

                    elif level > 1:
                        if m in ('freeze', 'freezeall'):
                            if m == 'freezeall':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.node.handleMessage(
                                            bs.FreezeMessage())
                                        commandSuccess = True
                                    except:
                                        pass

                            elif a == []:
                                bsInternal._chatMessage(
                                    'Failed!! Usage: /freezeall or /freeze number of list')
                            else:
                                try:
                                    bs.getSession().players[int(a[0])].actor.node.handleMessage(
                                        bs.FreezeMessage())
                                    commandSuccess = True
                                except:
                                    bsInternal._chatMessage(
                                        'Failed!! Usage: /freezeall or /freeze number of list')

                        elif m in ('thaw', 'thawall'):
                            if m == 'thawall':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.node.handleMessage(
                                            bs.ThawMessage())
                                    except:
                                        pass

                                commandSuccess = True
                            elif a == []:
                                bsInternal._chatMessage(
                                    'Failed!! Usage: /thawall or number of list')
                            else:
                                try:
                                    bs.getSession().players[int(a[0])].actor.node.handleMessage(
                                        bs.ThawMessage())
                                    commandSuccess = True
                                except:
                                    bsInternal._chatMessage(
                                        'Failed!! Usage: /thawall or /thaw number of list')

                        elif m in ('sleep', 'sleepall'):
                            if m == 'sleepall':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.node.handleMessage(
                                            'knockout', 5000)
                                    except:
                                        pass

                                commandSuccess = True
                            elif a == []:
                                bsInternal._chatMessage(
                                    'Failed!! Usage: /sleepall or /sleep number of list')
                            else:
                                try:
                                    bs.getSession().players[int(a[0])].actor.node.handleMessage(
                                        'knockout', 5000)
                                    commandSuccess = True
                                except:
                                    bsInternal._chatMessage(
                                        'Failed!! Usage: /sleepall or /sleep number of list')

                        elif m in ('kill', 'killall'):
                            if m == 'killall':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.node.handleMessage(
                                            bs.DieMessage())
                                    except:
                                        pass

                                commandSuccess = True
                            elif a == []:
                                bsInternal._chatMessage(
                                    'Failed!! Usage: /killall or /kill number of list')
                            else:
                                try:
                                    bs.getSession().players[int(a[0])].actor.node.handleMessage(
                                        bs.DieMessage())
                                    commandSuccess = True
                                except:
                                    bsInternal._chatMessage(
                                        'Failed!! Usage: /killall or /kill number of list')

                        elif m == 'curse':
                            if a == []:
                                bsInternal._chatMessage(
                                    'Using: /curse all or number of list')
                            elif a[0] == 'all':
                                for i in bs.getSession().players:
                                    try:
                                        i.actor.curse()
                                    except:
                                        pass

                                commandSuccess = True
                            else:
                                try:
                                    bs.getSession().players[int(
                                        a[0])].actor.curse()
                                    commandSuccess = True
                                except:
                                    pass

                        elif m == 'sm':
                            bs.getSharedObject('globals').slowMotion = bs.getSharedObject(
                                'globals').slowMotion == False
                            commandSuccess = True

                        elif m == 'end':
                            try:
                                bsInternal._getForegroundHostActivity().endGame()
                                commandSuccess = True
                            except:
                                pass

                        elif level > 2:
                            if m == 'quit':
                                commandSuccess = True
                                bsInternal.quit()
                            elif m == 'autoadmin' and level > 3:
                                if a == []:
                                    val = "1"
                                else:
                                    val = str(a[0])
                                AutoAdmin.admin(val)
                                commandSuccess = True
                            elif m == 'autovip' and level > 3:
                                if a == []:
                                    val = "2"
                                else:
                                    val = str(a[0])
                                AutoAdmin.vip(val)
                                commandSuccess = True
                            elif m == 'kick':
                                if a == []:
                                    bsInternal._chatMessage(
                                        'Using: /kick name or number of list')
                                elif len(a[0]) > 3:
                                    self.kickByNick(a[0])
                                    commandSuccess = True
                                else:
                                    try:
                                        s = int(a[0])
                                        bsInternal._disconnectClient(int(a[0]))
                                        commandSuccess = True
                                    except:
                                        self.kickByNick(a[0])
                                        commandSuccess = True

                            elif m == 'admin' and level > 3:
                                if a == []:
                                    bs.screenMessage(
                                        'Format: /admin <clietnID> <add / remove>')
                                else:
                                    n = playerFromClientID(a[0])
                                    n2 = n.get_account_id()
                                    if n is None:
                                        return
                                    if a[1] == 'add':
                                        if n2 not in storage.roles['admins']:
                                            storage.roles['admins'].append(n2)
                                            commandSuccess = True
                                            handleRol.commit_roles()
                                            bs.screenMessage(
                                                u"{} Ahora tiene admin!".format(n.getName(True)))
                                        else:
                                            bs.screenMessage(
                                                u"{} Ya posee este rol".format(n.getName(True)))
                                    elif a[1] == 'remove':
                                        if n2 in storage.roles['admins']:
                                            storage.roles['admins'].remove(n2)
                                            commandSuccess = True
                                            handleRol.commit_roles()
                                            bs.screenMessage(
                                                u"Admin removed")
                                        else:

                                            bs.screenMessage(
                                                u"{} No posee este rol".format(n.getName(True)))

                            elif m == 'vip' and level > 2:
                                if a == []:
                                    bs.screenMessage(
                                        'Format: /vip <clietnID> <add / remove>')
                                else:
                                    n = playerFromClientID(a[0])
                                    n2 = n.get_account_id()
                                    if n is None:
                                        return
                                    if a[1] == 'add':
                                        if n2 not in storage.roles['vips']:
                                            storage.roles['vips'].append(n2)
                                            commandSuccess = True
                                            handleRol.commit_roles()
                                            bs.screenMessage(
                                                u"{} Ahora tiene vip!".format(n.getName()))
                                        else:
                                            bs.screenMessage(
                                                u"{} Ya posee este rol".format(n.getName(True)))
                                    elif a[1] == 'remove':
                                        if n2 in storage.roles['vips']:
                                            storage.roles['vips'].remove(n2)
                                            commandSuccess = True
                                            handleRol.commit_roles()
                                            bs.screenMessage(
                                                u"Vip removed")
                                        else:
                                            bs.screenMessage(
                                                u"{} No posee este rol".format(n.getName(True)))

                            elif m == 'remove':
                                if a == []:
                                    bsInternal._chatMessage(
                                        'Using: /remove all or number of list')
                                elif a[0] == 'all':
                                    for i in bs.getSession().players:
                                        try:
                                            i.removeFromGame()
                                        except:
                                            pass

                                    commandSuccess = True
                                else:
                                    bs.getSession().players[int(
                                        a[0])].removeFromGame()
                                    commandSuccess = True

                            elif m in ('hug', 'hugall'):
                                try:
                                    if m == 'hugall':
                                        try:
                                            bsInternal._getForegroundHostActivity(
                                            ).players[0].actor.node.holdNode = bsInternal._getForegroundHostActivity().players[1].actor.node
                                        except:
                                            pass
                                        else:
                                            try:
                                                bsInternal._getForegroundHostActivity(
                                                ).players[1].actor.node.holdNode = bsInternal._getForegroundHostActivity().players[0].actor.node
                                            except:
                                                pass
                                            else:
                                                try:
                                                    bsInternal._getForegroundHostActivity(
                                                    ).players[3].actor.node.holdNode = bsInternal._getForegroundHostActivity().players[2].actor.node
                                                except:
                                                    pass
                                                else:
                                                    try:
                                                        bsInternal._getForegroundHostActivity(
                                                        ).players[4].actor.node.holdNode = bsInternal._getForegroundHostActivity().players[3].actor.node
                                                    except:
                                                        pass

                                                try:
                                                    bsInternal._getForegroundHostActivity(
                                                    ).players[5].actor.node.holdNode = bsInternal._getForegroundHostActivity().players[6].actor.node
                                                except:
                                                    pass

                                            try:
                                                bsInternal._getForegroundHostActivity(
                                                ).players[6].actor.node.holdNode = bsInternal._getForegroundHostActivity().players[7].actor.node
                                            except:
                                                pass

                                        commandSuccess = True
                                    elif a == []:
                                        bsInternal._chatMessage(
                                            'Failed!! Usage: /hugall or /hug number of list')
                                    else:
                                        try:
                                            bsInternal._getForegroundHostActivity().players[int(
                                                a[0])].actor.node.holdNode = bsInternal._getForegroundHostActivity().players[int(a[1])].actor.node
                                            commandSuccess = True
                                        except:
                                            bsInternal._chatMessage(
                                                'Failed!! Usage: /hugall or /hug number of list')

                                except:
                                    bs.screenMessage('Error!', color=(1, 0, 0))

                            elif m == 'tint':
                                if a == []:
                                    bsInternal._chatMessage(
                                        'Using: /tint R G B')
                                    bsInternal._chatMessage('OR')
                                    bsInternal._chatMessage(
                                        'Using: /tint r bright speed')
                                elif a[0] == 'r':
                                    m = 1.3 if a[1] is None else float(a[1])
                                    s = 1000 if a[2] is None else float(a[2])
                                    bsUtils.animateArray(bs.getSharedObject('globals'), 'tint', 3, {0: (
                                        1 * m, 0, 0), s: (0, 1 * m, 0), s * 2: (0, 0, 1 * m), s * 3: (1 * m, 0, 0)}, True)
                                    commandSuccess = True
                                else:
                                    try:
                                        if a[1] is not None:
                                            bs.getSharedObject('globals').tint = (
                                                float(a[0]), float(a[1]), float(a[2]))
                                            commandSuccess = True
                                        else:
                                            bs.screenMessage(
                                                'Error!', color=(1, 0, 0))
                                    except:
                                        bs.screenMessage(
                                            'Error!', color=(1, 0, 0))

                            elif m == 'pause':
                                bs.getSharedObject('globals').paused = bs.getSharedObject(
                                    'globals').paused == False
                                commandSuccess = True
                            elif m == 'cameraMode':
                                try:
                                    if bs.getSharedObject('globals').cameraMode == 'follow':
                                        bs.getSharedObject(
                                            'globals').cameraMode = 'rotate'
                                    else:
                                        bs.getSharedObject(
                                            'globals').cameraMode = 'follow'
                                    commandSuccess = True
                                except:
                                    pass

                            elif m == 'lm':
                                arr = []
                                for i in range(100):
                                    try:
                                        arr.append(
                                            bsInternal._getChatMessages()[(-1 - i)])
                                    except:
                                        pass

                                arr.reverse()
                                for i in arr:
                                    bsInternal._chatMessage(i)

                                commandSuccess = True
                            elif m == 'gp':
                                if a == []:
                                    bsInternal._chatMessage(
                                        'Using: /gp number of list')
                                else:
                                    s = bsInternal._getForegroundHostSession()
                                    for i in s.players[int(a[0])].getInputDevice()._getPlayerProfiles():
                                        try:
                                            bsInternal._chatMessage(i)
                                        except:
                                            pass

                                    commandSuccess = True
                            elif m == 'icy':
                                bsInternal._getForegroundHostActivity().players[int(
                                    a[0])].actor.node = bsInternal._getForegroundHostActivity().players[int(a[1])].actor.node
                                commandSuccess = True
                            elif m in ('fly', 'flyall'):
                                if m == 'flyall':
                                    for i in bsInternal._getForegroundHostActivity().players:
                                        i.actor.node.fly = True

                                    commandSuccess = True
                                elif a == []:
                                    bsInternal._chatMessage(
                                        'Failed!!! Usage: /flyall or /fly number of list')
                                else:
                                    try:
                                        bsInternal._getForegroundHostActivity().players[int(
                                            a[0])].actor.node.fly = bsInternal._getForegroundHostActivity().players[int(a[0])].actor.node.fly == False
                                        commandSuccess = True
                                    except:
                                        bsInternal._chatMessage(
                                            'Failed!!! Usage: /flyall or /fly number of list')

                            elif m == 'floorReflection':
                                bs.getSharedObject('globals').floorReflection = bs.getSharedObject(
                                    'globals').floorReflection == False
                            elif m == 'ac':
                                if a == []:
                                    bsInternal._chatMessage('Using: /ac R G B')
                                    bsInternal._chatMessage('OR')
                                    bsInternal._chatMessage(
                                        'Using: /ac r bright speed')
                                elif a[0] == 'r':
                                    m = 1.3 if a[1] is None else float(a[1])
                                    s = 1000 if a[2] is None else float(a[2])
                                    bsUtils.animateArray(bs.getSharedObject('globals'), 'ambientColor', 3, {0: (
                                        1 * m, 0, 0), s: (0, 1 * m, 0), s * 2: (0, 0, 1 * m), s * 3: (1 * m, 0, 0)}, True)
                                else:
                                    try:
                                        if a[1] is not None:
                                            bs.getSharedObject('globals').ambientColor = (
                                                float(a[0]), float(a[1]), float(a[2]))
                                        else:
                                            bs.screenMessage(
                                                'Error!', color=(1, 0, 0))
                                    except:
                                        bs.screenMessage(
                                            'Error!', color=(1, 0, 0))

                            elif m == 'iceOff':
                                try:
                                    activity.getMap().node.materials = [
                                        bs.getSharedObject('footingMaterial')]
                                    activity.getMap().isHockey = False
                                except:
                                    pass
                                else:
                                    try:
                                        activity.getMap().floor.materials = [
                                            bs.getSharedObject('footingMaterial')]
                                        activity.getMap().isHockey = False
                                    except:
                                        pass

                                    for i in activity.players:
                                        i.actor.node.hockey = False

                                commandSuccess = True
                            elif m == 'maxPlayers' and level > 3:
                                if a == []:
                                    bsInternal._chatMessage(
                                        'Using: /maxPlayers count of players')
                                else:
                                    try:
                                        bsInternal._getForegroundHostSession(
                                        )._maxPlayers = int(a[0])
                                        bsInternal._setPublicPartyMaxSize(
                                            int(a[0]))
                                        bsInternal._chatMessage(
                                            'Maximum players set to ' + str(int(a[0])))
                                    except:
                                        bs.screenMessage(
                                            'Error!', color=(1, 0, 0))

                                    commandSuccess = True
                            elif m in ('heal', 'healall'):
                                if m == 'healall':
                                    for i in bs.getActivity().players:
                                        try:
                                            if i.actor.exists():
                                                i.actor.node.handleMessage(
                                                    bs.PowerupMessage(powerupType='health'))
                                        except Exception:
                                            pass
                                        else:
                                            commandSuccess = True

                                elif a == []:
                                    bsInternal._chatMessage(
                                        'Failed!! Usage: /healall or /heal number of list')
                                else:
                                    try:
                                        bs.getActivity().players[int(a[0])].actor.node.handleMessage(
                                            bs.PowerupMessage(powerupType='health'))
                                        commandSuccess = True
                                    except Exception:
                                        bsInternal._chatMessage(
                                            'Failed!! Usage: /healall or /heal number of list')

                            elif m == 'gm':
                                try:
                                    if a == []:
                                        for i in range(len(activity.players)):
                                            if activity.players[i].getInputDevice().getClientID() == clientID:
                                                activity.players[i].actor.node.hockey = activity.players[i].actor.node.hockey == False
                                                activity.players[i].actor.node.invincible = activity.players[i].actor.node.invincible == False
                                                activity.players[i].actor._punchPowerScale = 5 if activity.players[
                                                    i].actor._punchPowerScale == 1.2 else 1.2

                                        commandSuccess = True
                                    else:
                                        activity.players[int(a[0])].actor.node.hockey = activity.players[int(
                                            a[0])].actor.node.hockey == False
                                        activity.players[int(a[0])].actor.node.invincible = activity.players[int(
                                            a[0])].actor.node.invincible == False
                                        activity.players[int(a[0])].actor._punchPowerScale = 5 if activity.players[int(
                                            a[0])].actor._punchPowerScale == 1.2 else 1.2
                                        commandSuccess = True
                                except:
                                    bsInternal._chatMessage('PLAYER NOT FOUND')

                            elif m == 'reflections':
                                if len(a) < 2:
                                    bsInternal._chatMessage(
                                        'Usage: /reflections type(1/0) scale')
                                else:
                                    rs = [
                                        int(a[1])]
                                    typee = 'soft' if int(
                                        a[0]) == 0 else 'powerup'
                                    try:
                                        bsInternal._getForegroundHostActivity().getMap().node.reflection = typee
                                        bsInternal._getForegroundHostActivity().getMap().node.reflectionScale = rs
                                        print 'node'
                                    except:
                                        pass
                                    else:
                                        try:
                                            bsInternal._getForegroundHostActivity().getMap().bg.reflection = typee
                                            bsInternal._getForegroundHostActivity().getMap().bg.reflectionScale = rs
                                            print 'bg'
                                        except:
                                            pass
                                        else:
                                            try:
                                                bsInternal._getForegroundHostActivity().getMap().floor.reflection = typee
                                                bsInternal._getForegroundHostActivity().getMap().floor.reflectionScale = rs
                                                print 'floor'
                                            except:
                                                pass

                                        try:
                                            bsInternal._getForegroundHostActivity().getMap().center.reflection = typee
                                            bsInternal._getForegroundHostActivity().getMap().center.reflectionScale = rs
                                            print 'center'
                                        except:
                                            pass

                                    commandSuccess = True

                            elif m == 'shatter':
                                if a == []:
                                    bsInternal._chatMessage(
                                        'Using: /shatter all or number of list')
                                elif a[0] == 'all':
                                    for i in bsInternal._getForegroundHostActivity().players:
                                        i.actor.node.shattered = int(a[1])

                                    commandSuccess = True
                                else:
                                    bsInternal._getForegroundHostActivity().players[int(
                                        a[0])].actor.node.shattered = int(a[1])
                                    commandSuccess = True
                            elif m == '/cm':
                                if a == []:
                                    time = 8000
                                else:
                                    time = int(a[0])
                                    op = 0.08
                                    std = bs.getSharedObject(
                                        'globals').vignetteOuter
                                    bsUtils.animateArray(bs.getSharedObject('globals'), 'vignetteOuter', 3, {
                                        0: bs.getSharedObject('globals').vignetteOuter, 17000: (0, 1, 0)})
                                try:
                                    bsInternal._getForegroundHostActivity().getMap().node.opacity = op
                                except:
                                    pass
                                else:
                                    try:
                                        bsInternal._getForegroundHostActivity().getMap().bg.opacity = op
                                    except:
                                        pass
                                    else:
                                        try:
                                            bsInternal._getForegroundHostActivity().getMap().bg.node.opacity = op
                                        except:
                                            pass
                                        else:
                                            try:
                                                bsInternal._getForegroundHostActivity().getMap().node1.opacity = op
                                            except:
                                                pass
                                            else:
                                                try:
                                                    bsInternal._getForegroundHostActivity().getMap().node2.opacity = op
                                                except:
                                                    pass

                                                try:
                                                    bsInternal._getForegroundHostActivity().getMap().node3.opacity = op
                                                except:
                                                    pass

                                            try:
                                                bsInternal._getForegroundHostActivity().getMap().steps.opacity = op
                                            except:
                                                pass

                                        try:
                                            bsInternal._getForegroundHostActivity().getMap().floor.opacity = op
                                        except:
                                            pass

                                    try:
                                        bsInternal._getForegroundHostActivity().getMap().center.opacity = op
                                    except:
                                        pass

                                def off():
                                    op = 1
                                    try:
                                        bsInternal._getForegroundHostActivity().getMap().node.opacity = op
                                    except:
                                        pass
                                    else:
                                        try:
                                            bsInternal._getForegroundHostActivity().getMap().bg.opacity = op
                                        except:
                                            pass
                                        else:
                                            try:
                                                bsInternal._getForegroundHostActivity().getMap().bg.node.opacity = op
                                            except:
                                                pass
                                            else:
                                                try:
                                                    bsInternal._getForegroundHostActivity().getMap().node1.opacity = op
                                                except:
                                                    pass
                                                else:
                                                    try:
                                                        bsInternal._getForegroundHostActivity().getMap().node2.opacity = op
                                                    except:
                                                        pass

                                                    try:
                                                        bsInternal._getForegroundHostActivity().getMap().node3.opacity = op
                                                    except:
                                                        pass

                                                try:
                                                    bsInternal._getForegroundHostActivity().getMap().steps.opacity = op
                                                except:
                                                    pass

                                            try:
                                                bsInternal._getForegroundHostActivity().getMap().floor.opacity = op
                                            except:
                                                pass

                                        try:
                                            bsInternal._getForegroundHostActivity().getMap().center.opacity = op
                                        except:
                                            pass

                                    bsUtils.animateArray(bs.getSharedObject('globals'), 'vignetteOuter', 3, {
                                        0: bs.getSharedObject('globals').vignetteOuter, 100: std})

                                bs.gameTimer(time, bs.Call(off))
                            elif m == 'help':
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='comandos publicos y comprados').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/me(estadisticas)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/emote 0 /em("fire, angry, lol, dead, huh, what, power")').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/buy tag(etiqueta)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/donate(donacion-tikets)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/list(lista-jugadore)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/shop effects(effectos-comprables))').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/shop commands(comandos-comprables))').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/scoretocash(tranforma score > ticket)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='==================================================').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='comandos admins').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/floater(ufo)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/gm(modo dios)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/kill o /killall').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/icy(controlar-jugador)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/shatter(mutilar-jugador)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/kick(quitar-jugador(id))').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/ban(banear-jugador)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/thaw o /thawall(atraer-jugador)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/fly o /flyall(volar)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/sleep o /sleepall(dormir-jugador)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/curse(detonar-jugador)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='sm(modo normal)').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/hug o /hugall').evaluate())
                                bsInternal._chatMessage(
                                    bs.Lstr(resource='/heal 0 /healall(curar)').evaluate())
                            elif level > 3:
                                if m == 'partyname':
                                    if True:
                                        if a == []:
                                            bsInternal._chatMessage(
                                                'Usage: /partyname Name of party')
                                        else:
                                            # print 'value of a[0] = ' + a[0]
                                            name = a[0].replace('_', ' ')
                                            try:
                                                bsInternal._setPublicPartyName(
                                                    name)
                                                bsInternal._chatMessage(
                                                    'Party name changed to "' + name + '"')
                                                commandSuccess = True
                                            except:
                                                bs.screenMessage(
                                                    'failed to change')

                                elif m == 'settings':
                                    if a == []:
                                        bsInternal._chatMessage(
                                            "Usage /settings (number in list) (0,1)")
                                        bsInternal._chatMessage(
                                            "List Of Settings:")
                                        bsInternal._chatMessage(
                                            "1.Shield On Bomb")
                                        bsInternal._chatMessage(
                                            "2.Lights On Bomb")
                                        bsInternal._chatMessage(
                                            "3.Name On Bomb")
                                        bsInternal._chatMessage("4.Night Mode")
                                    t = int(a[1])
                                    if a[0] == "1":
                                        cmdsetg.sB(t)
                                        commandSuccess = True
                                    if a[0] == "2":
                                        cmdsetg.bL(t)
                                        commandSuccess = True
                                    if a[0] == "3":
                                        cmdsetg.bN(t)
                                        commandSuccess = True
                                    if a[0] == "4":
                                        cmdsetg.nM(t)
                                        commandSuccess = True

                                elif m == 'public':
                                    if True:
                                        if a == []:
                                            bsInternal._chatMessage(
                                                'Usage: /public 0 or 1')
                                        elif a[0] == '0':
                                            try:
                                                bsInternal._setPublicPartyEnabled(
                                                    False)
                                                bsInternal._chatMessage(
                                                    'Party is Private')
                                                commandSuccess = True
                                            except:
                                                bs.screenMessage(
                                                    'failed to change')

                                        elif a[0] == '1':
                                            try:
                                                bsInternal._setPublicPartyEnabled(
                                                    True)
                                                bsInternal._chatMessage(
                                                    'Party is Public')
                                                commandSuccess = True
                                            except:
                                                bs.screenMessage(
                                                    'failed to change')

                                        else:
                                            bsInternal._chatMessage(
                                                'Usage: /public 0 or 1')

                                elif m == 'ban':
                                    if a != []:
                                        bannedId = None
                                        aid = None
                                        try:
                                            clID = a[0]
                                            player = playerFromClientID(clID)
                                            aid = bs.uni(
                                                getDisplayString(clID))
                                            bannedID = player.get_account_id()
                                            client = player.getInputDevice().getClientID()
                                            name = player.getName()
                                            if bannedID is None:
                                                return
                                            if bannedID in roles['owners'] or bannedID in roles['admin']:
                                                bs.screenMessage(
                                                    "You can't kick moderators")
                                                return
                                            if aid is not None:
                                                roles['banned'][bannedID] = aid
                                                handleRol.commit_roles()
                                                bs.screenMessage("Has sido baneado por violar las reglas!", clients=[
                                                                 client], transient=True, color=(2, 0, 0))
                                                bsInternal._chatMessage(
                                                    'banned ' + name)
                                                bsInternal._disconnectClient(
                                                    int(clID))
                                                commandSuccess = True
                                        except Exception:
                                            bsInternal._chatMessage(
                                                'player not found')

                                elif m == 'whois':
                                    try:
                                        clID = int(a[0])
                                        ID = ''
                                        for i in bsInternal._getForegroundHostActivity().players:
                                            if i.getInputDevice().getClientID() == clID:
                                                ID = i.get_account_id()
                                                name = i.getName(True, True)
                                        if ID is not '':
                                            with open('logPlayers.json', 'r') as f:
                                                allPlayers = json.loads(
                                                    f.read())
                                                allID = allPlayers[ID]
                                                string = 'Login ID of %s is:' % name
                                                for i in allID:
                                                    # bsInternal._chatMessage(i)
                                                    string += '\n' + i
                                                    # commandSuccess = True
                                                bs.screenMessage(
                                                    string, transient=True, color=(1, 1, 1))
                                    except:
                                        print 'who is exception'

                                elif m == 'text':
                                    from BsTextOnMap import texts
                                    if a == []:
                                        bsInternal._chatMessage(
                                            "Usage: /text showall or /text add [text] or /text del [textnumber]")
                                    elif a[0] == 'add' and len(a) > 1:
                                        # get whole sentence from argument list
                                        newText = u''
                                        for i in range(1, len(a)):
                                            newText += a[i] + ' '
                                        # print newText
                                        texts.append(newText)

                                        # write to file
                                        with open(bs.getEnvironment()['systemScriptsDirectory'] + '/BsTextOnMap.py') as (file):
                                            s = [row for row in file]
                                            s[0] = 'texts = ' + \
                                                str(texts) + '\n'
                                            f = open(bs.getEnvironment()[
                                                'systemScriptsDirectory'] + '/BsTextOnMap.py', 'w')
                                            for i in s:
                                                f.write(i)
                                            f.close()
                                            commandSuccess = True
                                    elif a[0] == 'showall':
                                        for i in range(len(texts)):
                                            # print texts(i)
                                            bsInternal._chatMessage(
                                                str(i) + '. ' + texts[i])
                                        commandSuccess = True
                                    elif a[0] == 'del' and len(a) > 1:
                                        try:
                                            if len(texts) > 1:
                                                texts.pop(int(a[1]))
                                                # write to file
                                                with open(bs.getEnvironment()['systemScriptsDirectory'] + '/BsTextOnMap.py') as (file):
                                                    s = [row for row in file]
                                                    s[0] = 'texts = ' + \
                                                        str(texts) + '\n'
                                                    f = open(bs.getEnvironment()[
                                                        'systemScriptsDirectory'] + '/BsTextOnMap.py', 'w')
                                                    for i in s:
                                                        f.write(i)
                                                    f.close()
                                                    commandSuccess = True
                                            else:
                                                bs.screenMessage(
                                                    "At least one text should be present", (1, 0, 0))
                                        except:
                                            pass
                                    else:
                                        bsInternal._chatMessage(
                                            "Usage: /text showall or /text add [text] or /text del [textnumber]")
                                elif m == 'whoinqueue':
                                    def _onQueueQueryResult(result):
                                        # print result, ' is result'
                                        inQueue = result['e']
                                        # print inQueue, ' is inQueue'
                                        string = 'No one '
                                        if inQueue != []:
                                            string = ''
                                            for queue in inQueue:
                                                # print queue[3]
                                                string += queue[3] + ' '
                                        bsInternal._chatMessage(
                                            string + 'is in the queue')

                                    bsInternal._addTransaction(
                                        {'type': 'PARTY_QUEUE_QUERY',
                                            'q': "p_S-l150a7a1d-0f12-43de-a3bf-467a7a5bcd72_1029295_13.233.116.32_43210"},
                                        callback=bs.Call(_onQueueQueryResult))
                                    bsInternal._runTransactions()

        except Exception as e:
            print e
            return


c = chatOptions()


def cmd(msg, clientID):
    c.opt(clientID, msg)
    if commandSuccess:
        if commandByCoin:
            coinSystem.addCoins(user, costOfCommand * -1)
            bsInternal._chatMessage(
                'Success! That cost you ' + bs.getSpecialChar('ticket') + str(costOfCommand))
        else:
            try:
                with bs.Context(bsInternal._getForegroundHostActivity()):
                    bs.screenMessage(reply, color=(0.1, 1, 0.1))
                    # bsInternal._chatMessage(reply)
            except:
                pass
    return
