from http.client import HTTPResponse
import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import requests
import os
from dotenv import load_dotenv, find_dotenv
from lolpros.models import Account, Team, Player, lpUpdate
import datetime
from django.utils.timezone import get_current_timezone

load_dotenv(find_dotenv())


def index(request):
    return HttpResponse("YES")


def addAccount(request, account):
    api_key = os.getenv('RIOT_API_KEY')
    urlAccount = f"https://euw1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{account}?api_key={api_key}"
    res = requests.get(urlAccount)

    if res.status_code == 404:
        return JsonResponse({'response' : 'Erreur de pseudo'})

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
                profileIcon=f"https://ddragon.leagueoflegends.com/cdn/12.19.1/img/profileicon/{res['profileIconId']}.png",
                tier=res['tier'],
                rank=res['rank'],
                leaguePoints=res['leaguePoints'],
                wins=res['wins'],
                losses=res['losses']
            )
            a = Account.objects.get(id=res['id'])

            oldLPC = a.LPC
            a.getLpc()
            a.save()
            a.refresh_from_db()
            
            if oldLPC != a.LPC:
                lp = lpUpdate(
                    lp=a.LPC,
                    date=datetime.datetime.now().replace(tzinfo=get_current_timezone()),
                    account=a
                )
                lp.save()
            
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

        lp = lpUpdate(
            lp=a.LPC,
            date=datetime.datetime.now().replace(tzinfo=get_current_timezone()),
            account=a
        )
        lp.save()
        

    return JsonResponse(res)


def updateAll(request):
    accounts = Account.objects.all()

    for account in accounts:
        requests.get(f"https://api.4esport.fr/lolpros/addaccount/{account.name}")
        print(f"Update {account.name}")
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
        print(diff)
        response["response"].append({
            "player": update.account.name,
            "date": update.date.isoformat(),
            "diff": diff,
        })

    return JsonResponse(response, status=200)