# TODO

BDD
Pour un utilisateur
Pseudo IRL (un joueur peut avoir des smurfs)
Type: (Smurf main)
Pseudo LoL
Role
Team
PP LoL
Ses noms(lorsqu'il rename)

Pour une equipe :
Nom
Joueurs (role:staff, player)
Logo

Ensuite un cron qui récupère :
Les LP à un instant t et en faire un historique

API

/player/Matéo (me donne mon main et tous mes smurfs)
/team/BlueShift (une équipe)

FUNCTIONS
Rank to LPC (LP Cumulés)
La première chose à faire c'est de transformer le retour de l'api de Riot en LP Cumulés
Ex : Mateleo Rank:Gold Tier:IV LP:12 => 1212

Déduire si win ou loose
Tu regardes si il a gagné des LP ou non

Calculer le WR
Calculer le nombre total de games

Gérer les changements de noms (facile avec l'id Riot) et les stocker
