from http.client import HTTPResponse
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import os
from dotenv import load_dotenv, find_dotenv
from lolpros.models import Account, Team, Player

load_dotenv(find_dotenv())


def index(request):
    return HttpResponse("YES")


def addAccount(request, account):
    api_key = os.getenv('RIOT_API_KEY')
    urlAccount = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{account}?api_key={api_key}"

    res = requests.get(urlAccount)
    res = res.json()
    urlLp = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{res['id']}?api_key={api_key}"

    res2 = requests.get(urlLp)
    res2 = res2.json()

    if res2 != []:
        for league in res2:
            if league['queueType'] == "RANKED_SOLO_5x5":
                res2 = league
    else:
        res2 = {
            'tier': '',
            'rank': '',
            'leaguePoints': 0,
            'wins': 0,
            'losses': 0,
        }

    res = res | res2

    try:
        if Account.objects.get(id=res['id']):
            print(f"Le compte {res['name']} existe déja, mise à jour...")
            a = Account.objects.filter(id=res['id'])
            a.update(
                name=res['name'], 
                summonerLvl=res['summonerLevel'], 
                profileIcon=f"https://ddragon.leagueoflegends.com/cdn/12.17.1/img/profileicon/{res['profileIconId']}.png",
                tier=res['tier'],
                rank=res['rank'],
                leaguePoints=res['leaguePoints'],
                wins=res['wins'],
                losses=res['losses']
            )
            a = Account.objects.get(id=res['id'])
            a.getLpc()
            a.save()
            a.refresh_from_db()
            
    except Account.DoesNotExist:
        a = Account(
            id=res['id'],
            name=res['name'], 
            summonerLvl=res['summonerLevel'], 
            profileIcon=f"https://ddragon.leagueoflegends.com/cdn/12.17.1/img/profileicon/{res['profileIconId']}.png",
            tier=res['tier'],
            rank=res['rank'],
            leaguePoints=res['leaguePoints'],
            wins=res['wins'],
            losses=res['losses']
        )
        a.getLpc()
        a.save()

    return JsonResponse(res)


def getPlayerDb(player):
    player = player.lower()

    try:
        playerInfos = Player.objects.get(name=player)

    except Player.DoesNotExist:
        response = {
            "response": "Le joueur n'existe pas"
        }
        return response

    accountsInfos = list(Account.objects.filter(player__name=player))
    accountsInfos.sort(key=lambda x:x.LPC, reverse=True)
    

    response = {
        "id" : playerInfos.id,
        "name" : playerInfos.name.capitalize(),
        "role" : playerInfos.role,
        "team" : playerInfos.team.name.capitalize() if playerInfos.team else None,
        "teamId" : playerInfos.team.id if playerInfos.team else None,
        "accounts" : [],
    }

    for account in accountsInfos:
        response['accounts'].append({
            "playerId": playerInfos.id,
            'name': account.name,
            'summonerLvl': account.summonerLvl, 
            'profileIcon': account.profileIcon,
            'tier': account.tier,
            'rank': account.rank,
            'LP': account.leaguePoints,
            'wins': account.wins,
            'losses': account.losses,
            'LPC': account.LPC,
        })
    return response


def playerDb(request, player):
    return JsonResponse(getPlayerDb(player))


def getTeamDb(team):
    team = team.lower()

    try:
        teamInfos = Team.objects.get(name=team)

    except Team.DoesNotExist:
        response = {
            "response": "La Team n'existe pas"
        }
        return JsonResponse(response)

    playersInfos = Player.objects.filter(team__name=team)

    response = {
        "id" : teamInfos.id,
        "name" : teamInfos.name.capitalize(),
        "teamLogo" : teamInfos.logo,
        "players" : [],
    }

    for player in playersInfos:
        playerIntermediaire = getPlayerDb(player.name)

        playerAccountInfos = {
            'name': playerIntermediaire['accounts'][0]['name'],
            'logo': playerIntermediaire['accounts'][0]['profileIcon'],
            'role': playerIntermediaire['role'],
            'LPC': playerIntermediaire['accounts'][0]['LPC'],
            'tier': playerIntermediaire['accounts'][0]['tier'],
            'rank': playerIntermediaire['accounts'][0]['rank'],
            'LP': playerIntermediaire['accounts'][0]['LP'],
        }

        del playerIntermediaire['accounts']

        playerIntermediaire = playerIntermediaire | playerAccountInfos



        response['players'].append(playerIntermediaire)

    return response

    # liste des joueurs (meme infos que leaderboard)

def teamDb(request, team):
    return JsonResponse(getTeamDb(team))



def leaderboard(request):
    accounts = list(Account.objects.all())
    accounts.sort(key=lambda x:x.LPC, reverse=True)

    players = []

    for account in accounts:
        if account.player.name not in players:
            players.append(account.player.name)
        else :
            accounts.remove(account)

    response = {
        'response': []
    }

    for account in accounts:
        player = {
            'name': account.player.name.capitalize() if account.player else None,
            'logo': account.profileIcon,
            'role': account.player.role if account.player else None,
            'LPC': account.LPC,
            'tier': account.tier,
            'rank': account.rank,
            'LP': account.leaguePoints,
            'team': account.player.team.name.capitalize() if account.player.team else None,
            'teamLogo': account.player.team.logo if account.player.team else None,
        }
 
        response['response'].append(player)

    return JsonResponse(response)
