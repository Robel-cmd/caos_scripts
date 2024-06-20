import bs
import bsUtils
import bsGame
rejoin_cooldown = 10 * 1000
bsGame.Session.players_on_wait = {}
bsGame.Session.players_req_identifiers = {}
bsGame.Session.waitlist_timers = {}
def _Modify_Session_onPlayerRequest(self, player):
    global rejoin_cooldown
    """
    Called when a new bs.Player wants to join;
    should return True or False to accept/reject.
    """
    # limit player counts based on pro purchase/etc *unless* we"re in a
    # stress test
    count = 0
    if bsUtils._gStressTestResetTimer is None:

        if len(self.players) >= self._maxPlayers:

            # print a rejection message *only* to the client trying to join
            # (prevents spamming everyone else in the game)
            bs.playSound(bs.getSound("error"))
            bs.screenMessage(
                bs.Lstr(
                    resource="playerLimitReachedText",
                    subs=[("${COUNT}", str(self._maxPlayers))]),
                color=(0.8, 0.0, 0.0),
                clients=[player.getInputDevice().getClientID()],
                transient=True)
            return False
    # rejoin cooldown
    pid = player.get_account_id()
    #print(help(player.setName))
    #print(dir(bsInternal))
    import math
    if pid:
        leave_time = self.players_on_wait.get(pid)
        if leave_time:
            diff = str(
                int((rejoin_cooldown - bs.getRealTime() + leave_time) / 1000)
            )
            bs.screenMessage(
                "You Can Join in {} Seconds.".format(diff),
                clients=[player.getInputDevice().getClientID()],
                transient=True)
            return False
        self.players_req_identifiers[player.getID()] = pid


    if player.get_account_id() is None:
        bs.screenMessage('Loading; try again in a moment......',color=(1,1,0),transient=True,clients=[player.getInputDevice().getClientID()])
        return False

    for current in self.players:
        if current.get_account_id() == player.get_account_id():
            count += 1

    if count >= 1:
        bs.screenMessage("No se permiten bots!",
            clients=[player.getInputDevice().getClientID()], transient=True)
        bs.playSound(bs.getSound("error"))
        return False

    bs.playSound(bs.getSound("pop01"))
    return True




def Modify_onPlayerLeave(self, player):
    global rejoin_cooldown
    """
    Called when a previously-accepted bs.Player leaves the session.
    """
    # remove them from the game rosters
    def delete_player_on_wait(pid):
        try:
            self.players_on_wait.pop(pid)
        except KeyError:
            pass

    identifier = self.players_req_identifiers.get(player.getID())
    if identifier:
        self.players_on_wait[identifier] = bs.getRealTime()
        with bs.Context('UI'):
            self.waitlist_timers[identifier] = bs.realTimer(
                rejoin_cooldown, bs.Call(delete_player_on_wait, identifier))

    if player in self.players:
        bs.playSound(bs.getSound('corkPop'))
        #bs.screenMessage("Adios nos Vemos! :>", clients=[player.getInputDevice().getClientID()], transient=True)
        # this will be None if the player is still in the chooser
        team = player.getTeam()

        activity = self._activityWeak()


        # if he had no team, he's in the lobby
        # if we have a current activity with a lobby, ask them to remove him
        if team is None:
            with bs.Context(self):
                try:
                    self._lobby.removeChooser(player)
                except Exception:
                    bs.printException(
                        'Error: exception in Lobby.removeChooser()')

        # *if* he was actually in the game, announce his departure
        if team is not None and len(activity.players) <= 3:
            bs.screenMessage(
                bs.Lstr(resource='playerLeftText',
                        subs=[('${PLAYER}', player.getName(full=True))]))

        # remove him from his team and session lists
        # (he may not be on the team list since player are re-added to
        # team lists every activity)
        if team is not None and player in team.players:

            # testing.. can remove this eventually
            if isinstance(self, bs.FreeForAllSession):
                if len(team.players) != 1:
                    bs.printError("expected 1 player in FFA team")
            team.players.remove(player)

        # remove player from any current activity
        if activity is not None and player in activity.players:
            activity.players.remove(player)

            # run the activity callback unless its been finalized
            if not activity.isFinalized():
                try:
                    with bs.Context(activity):
                        activity.onPlayerLeave(player)
                except Exception:
                    bs.printException(
                        'exception in onPlayerLeave for activity', activity)
            else:
                bs.printError(
                    "finalized activity in onPlayerLeave; shouldn't happen")

            player._setActivity(None)

            # reset the player - this will remove its actor-ref and clear
            # its calls/etc
            try:
                with bs.Context(activity):
                    player._reset()
            except Exception:
                bs.printException(
                    'exception in player._reset in'
                    ' onPlayerLeave for player', player)

        # if we're a non-team session, remove the player's team completely
        if not self._useTeams and team is not None:

            # if the team's in an activity, call its onTeamLeave callback
            if activity is not None and team in activity.teams:
                activity.teams.remove(team)

                if not activity.isFinalized():
                    try:
                        with bs.Context(activity):
                            activity.onTeamLeave(team)
                    except Exception:
                        bs.printException(
                            'exception in onTeamLeave for activity', activity)
                else:
                    bs.printError("finalized activity in onPlayerLeave p2"
                                  "; shouldn't happen")

                # clear the team's game-data (so dying stuff will
                # have proper context)
                try:
                    with bs.Context(activity):
                        team._resetGameData()
                except Exception:
                    bs.printException('exception clearing gameData for team:',
                                      team, 'for player:', player,
                                      'in activity:', activity)

            # remove the team from the session
            self.teams.remove(team)
            try:
                with bs.Context(self):
                    self.onTeamLeave(team)
            except Exception:
                bs.printException('exception in onTeamLeave for session', self)
            # clear the team's session-data (so dying stuff will
            # have proper context)
            try:
                with bs.Context(self):
                    team._resetSessionData()
            except Exception:
                bs.printException('exception clearing sessionData for team:',
                                  team, 'in session:', self)

        # now remove them from the session list
        self.players.remove(player)

    else:
        print('ERROR: Session.onPlayerLeave called'
              ' for player not in our list.')


bsGame.Session.onPlayerRequest = _Modify_Session_onPlayerRequest
bsGame.Session.onPlayerLeave = Modify_onPlayerLeave
