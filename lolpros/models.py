from django.db import models
from django.utils import timezone


class Team(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    logo = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    discordId = models.BigIntegerField(primary_key=True) 
    name = models.CharField(max_length=150, null=True, blank=True)
    role = models.CharField(max_length=50, null=True, blank=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

    def getMainAccount(self):
        accounts = list(Account.objects.filter(player=self))
        accounts.sort(key=lambda x:x.LPC, reverse=True) 

        return accounts[0]

    def getRankByRole(self):
        players = list(Player.objects.filter(role=self.role))
        accounts = [player.getMainAccount() for player in players]
        accounts.sort(key=lambda x:x.LPC, reverse=True)

        return f"{accounts.index(self.getMainAccount()) + 1}/{len(players)}"


    def __str__(self):
        return self.name



class Account(models.Model):
    id = models.CharField(primary_key=True, max_length=200)
    name = models.CharField(max_length=20, null=True, blank=True)
    summonerLvl = models.BigIntegerField(null=True, blank=True)
    profileIcon = models.CharField(max_length=200, null=True, blank=True)

    tier = models.CharField(max_length=100, null=True, blank=True)
    rank = models.CharField(max_length=100, null=True, blank=True)
    leaguePoints = models.IntegerField(null=True, blank=True)
    wins = models.IntegerField(null=True, blank=True)
    losses = models.IntegerField(null=True, blank=True)

    avgWins = models.IntegerField(default=0, null=True, blank=True)
    avgLosses = models.IntegerField(default=0, null=True, blank=True)

    LPC = models.IntegerField(null=True, blank=True)

    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def getLpHisto(self):
        updates = list(lpUpdate.objects.filter(account=self))
        updates.sort(key=lambda x:x.date, reverse=True)
        response = []

        for update in updates:
            infos = {
                'LP': update.lp,
                'date': update.date.isoformat(),
            }
            response.append(infos)
        return response

    def getPreviousUpdate(self, update):
        try:
            return lpUpdate.objects.filter(account = self).filter(date__lte=update.date).order_by("-date")[1]
        except IndexError:
            return update

    def get24hGains(self):
        updates = list(lpUpdate.objects.filter(account=self).filter(date__gte=timezone.now() - timezone.timedelta(1)).order_by("-date"))
        if updates != []:
            first = updates[0].lp
            last = updates[-1].lp
            return first-last
        return 0

    def getLpc(self):
        if self.tier != '':
            if self.tier == 'MASTER' or self.tier == 'GRANDMASTER' or self.tier == 'CHALLENGER':
                self.LPC = dico_tier[self.tier] + self.leaguePoints
            else:
                self.LPC = dico_tier[self.tier] + dico_rank[self.rank] + self.leaguePoints
            return True
        self.LPC = 0
        return False

    def getLpHistoDiff(self, nbGames = False):
        if nbGames: 
            updates = list(lpUpdate.objects.filter(account=self).order_by("-date")[:nbGames])
        else:
            updates = list(lpUpdate.objects.filter(account=self).order_by("-date"))
        res = []
        for update in updates:
            previousUpdate = update.account.getPreviousUpdate(update)
            if update == previousUpdate:
                continue
            diff = update.lp - previousUpdate.lp
            res.append(diff)
        return res
        
    def getAverageGains(self, nbGames = False):
        updates = self.getLpHistoDiff(nbGames)
        wins = [update for update in updates if update > 0]
        losses = [update for update in updates if update < 0]

        self.avgWins = round(sum(wins)/len(wins) if wins else 0)
        self.avgLosses = round(sum(losses)/len(losses) if losses else 0)

        return {
            "avgWins": self.avgWins,
            "avgLosses": self.avgLosses
        }


class lpUpdate(models.Model):
    lp = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)

    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.lp} {self.account}"


dico_tier = {
    "IRON": 0,
    "BRONZE": 400,
    "SILVER": 800,
    "GOLD": 1200,
    "PLATINUM": 1600,
    "DIAMOND": 2000,
    "MASTER": 2400,
    "GRANDMASTER": 2900,
    "CHALLENGER": 3300,
}

dico_rank = {
    "IV": 0,
    "III": 100,
    "II": 200, 
    "I": 300
}
