from django.db import models


class Team(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    logo = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name


class Player(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)

    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, blank=True)

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

    LPC = models.IntegerField(null=True, blank=True)
    LPHistory = models.TextField(null=True, blank=True)
    nameHistory = models.TextField(null=True, blank=True)
    
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def getLpc(self):
        self.LPC = dico_tier[self.tier] + dico_rank[self.rank] + self.leaguePoints
        return True



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