import datetime
import json
import os
from http.client import HTTPResponse
import time

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.timezone import get_current_timezone
from dotenv import find_dotenv, load_dotenv

from lolpros.models import Account, Player, Team, lpUpdate

load_dotenv(find_dotenv())


def index(request):
    return HttpResponse("YES")


def fetchAccount(account, api_key):
    url = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{account}?api_key={api_key}"
    res = requests.get(url)

    if res.status_code != 200:
        return {}

    return res.json()


def fetchLp(id, api_key):
    url = f"https://euw1.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}?api_key={api_key}"
    res = requests.get(url)

    if res.status_code != 200:
        return {}

    res = res.json()
    
    if res != []:
        for league in res:
            if league['queueType'] == "RANKED_SOLO_5x5":
                return league

    account = Account.objects.get(id=id)
    return {
        'summonerName': account.name,
        'id' : id,
        'tier': '',
        'rank': '',
        'leaguePoints': 0,
        'wins': 0,
        'losses': 0
    }

def addAccount(request, account = None, id = None):
    api_key = os.getenv('RIOT_API_KEY')
    if account:
        resAccount = fetchAccount(account, api_key)
        resLp = fetchLp(resAccount["id"], api_key)
    
    elif id:
        resLp = fetchLp(id, api_key)
        if resLp == {} : 
            return JsonResponse({"response":"error in fetchLp"})
            
        resAccount = fetchAccount(resLp["summonerName"], api_key)   

    data = resAccount | resLp


    try:
        if Account.objects.get(id=data['id']):
            print(f"Le compte {data['name']} existe déja, mise à jour...")
            a = Account.objects.filter(id=data['id'])
            a.update(
                name=data['name'], 
                summonerLvl=data['summonerLevel'], 
                profileIcon=f"https://ddragon.leagueoflegends.com/cdn/12.21.1/img/profileicon/{data['profileIconId']}.png",
                tier=data['tier'],
                rank=data['rank'],
                leaguePoints=data['leaguePoints'],
                wins=data['wins'],
                losses=data['losses']
            )
            a = Account.objects.get(id=data['id'])

            oldLPC = a.LPC
            a.getLpc()
            a.save()
            a.refresh_from_db()
            a.getAverageGains(20)
            
            if oldLPC != a.LPC:
                lp = lpUpdate(
                    lp=a.LPC,
                    date=datetime.datetime.now().replace(tzinfo=get_current_timezone()),
                    account=a
                )
                lp.save()
                
                a.save()
                a.refresh_from_db()
            
    except Account.DoesNotExist:
        a = Account(
            id=data['id'],
            name=data['name'], 
            summonerLvl=data['summonerLevel'], 
            profileIcon=f"https://ddragon.leagueoflegends.com/cdn/12.19.1/img/profileicon/{data['profileIconId']}.png",
            tier=data['tier'],
            rank=data['rank'],
            leaguePoints=data['leaguePoints'],
            wins=data['wins'],
            losses=data['losses']
        )
        a.getLpc()
        a.save()

        lp = lpUpdate(
            lp=a.LPC,
            date=datetime.datetime.now().replace(tzinfo=get_current_timezone()),
            account=a
        )
        lp.save()
    
    return JsonResponse(data)


def updateAll(request):
    accounts = Account.objects.all()

    for account in accounts:
        print(f"Update {account.name}, id {account.id}")
        addAccount(request, id=account.id)
    return HttpResponse("accounts updated")
    


def getPlayerDb(player):
    try:
        playerInfos = Player.objects.get(name__iexact=player)

    except Player.DoesNotExist:
        response = {
            "response": "Le joueur n'existe pas"
        }
        return response

    print(player, playerInfos, playerInfos.name)

    accountsInfos = list(Account.objects.filter(player__name=playerInfos.name))
    accountsInfos.sort(key=lambda x:x.LPC, reverse=True)
    
    response = {
        "name" : playerInfos.name,
        "role" : playerInfos.role,
        "rankByRole": playerInfos.getRankByRole(),
        "team" : playerInfos.team.name.capitalize() if playerInfos.team else None,
        "teamId" : playerInfos.team.id if playerInfos.team else None,
        "accounts" : [],
    }

    for account in accountsInfos:
        response['accounts'].append({
            'name': account.name,
            'summonerLvl': account.summonerLvl, 
            'profileIcon': account.profileIcon,
            'tier': account.tier,
            'rank': account.rank,
            'LP': account.leaguePoints,
            'wins': account.wins,
            'losses': account.losses,
            'LPC': account.LPC,
            'LPHisto': account.getLpHisto(),
            'agvWins': account.avgWins,
            'avgLosses': account.avgLosses
        })
    return response


def playerDb(request, player):
    return JsonResponse(getPlayerDb(player))


def getTeamDb(team):
    try:
        teamInfos = Team.objects.get(name=team)

    except Team.DoesNotExist:
        response = {
            "response": "La Team n'existe pas"
        }
        return response

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
            'profileIcon': playerIntermediaire['accounts'][0]['profileIcon'],
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



def teamDb(request, team):
    return JsonResponse(getTeamDb(team))



def leaderboard(request):
    players = list(Player.objects.all())

    accounts = [player.getMainAccount() for player in players]
    accounts.sort(key=lambda x:x.LPC, reverse=True)

    response = {
        'response': []
    }

    for account in accounts:
        player = {
            'name': account.player.name if account.player else account.name,
            'profileIcon': account.profileIcon,
            'role': account.player.role if account.player else None,
            'LPC': account.LPC,
            'tier': account.tier,
            'rank': account.rank,
            'LP': account.leaguePoints,
            'team': account.player.team.name.capitalize() if account.player.team else None,
            'teamLogo': account.player.team.logo if account.player.team else None,
            'LPHisto': account.getLpHisto(),
        }
 
        response['response'].append(player)

    return JsonResponse(response)


def registerPlayer(request, discordId, userName, accounts, role, token):
    if token != os.getenv('REGISTER_TOKEN'):
        return JsonResponse({'response' : 'Access Denied + ratio'})

    response = ""

    try:
        p = Player.objects.get(discordId = discordId)
        response += f"Le joueur {p} existe déjà. "

    except Player.DoesNotExist:
        p = Player(
            discordId=discordId,
            name=userName,
            role=role,
        )
        p.save()

        response += f"Création de {p}. "


    accounts = accounts.split(';')

    for account in accounts:
        try:
            a = Account.objects.get(name__iexact = account)
            response += f"Le compte {a} existe déjà. "

        except Account.DoesNotExist:
            addAccount(request, account=account)
            a = Account.objects.filter(name__iexact = account)
            a.update(
                player=p
            )
            print(a)
            a = Account.objects.get(name__iexact = account)
            a.refresh_from_db()
            response += f"Le compte {a} à été ajouté. "

    return JsonResponse({'response': response})


def getPlayerDiscord(request, discordID):

    try:
        player = Player.objects.get(discordId = discordID)

    except Player.DoesNotExist:
        return JsonResponse({
            "response": "Aucun joueur associé a ce discordID" 
        }, status=404)
    
    account = player.getMainAccount()

    return JsonResponse({
        'name': player.name,
        'role': player.role,
        'team': player.team,
        'summonerLvl': account.summonerLvl,
        'profileIcon': account.profileIcon,
        'LPC': account.LPC,
        'tier': account.tier,
        'rank': account.rank,
        'LP': account.leaguePoints,
        'LPHisto': account.getLpHisto(),
    }, status=200)
    

def last10Updates(request):
    updates = [lpUpdate for lpUpdate in lpUpdate.objects.order_by('-date')][:10]

    if updates == []:
        return JsonResponse({"response": "Pas de lpUpdate"}, status=501)

    response = {"response" : []}

    for update in updates:
        previousUpdate = update.account.getPreviousUpdate(update)
        if update == previousUpdate:
            continue
        diff = update.lp - previousUpdate.lp
        response["response"].append({
            "account": update.account.name,
            "name": update.account.player.name,
            "date": update.date.isoformat(),
            "diff": diff,
        })

    return JsonResponse(response, status=200)


def lp24hGains():
    accounts = Account.objects.all()

    res = []

    for account in accounts:
        res.append({
            "name" : account.player.name,
            "gains": account.get24hGains(),
            "profileIcon": account.profileIcon
        })

    res.sort(key=lambda x: x['gains'], reverse=True)
    return res


def playerOfTheDay(request):
    return JsonResponse(lp24hGains()[0], safe=False)

def interOfTheDay(request):
    return JsonResponse(lp24hGains()[-1], safe=False)