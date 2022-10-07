# LinuxBot
LinuxBot est un bot discord français uniquement pour linux permettant de faire beaucoup de choses comme de la modération, souhaiter des anniversaire, faire un classement des personnes les plus actives sur le serveur et peux faire des blagues.
## Instalation 
Pour fonctionner correctement vous devez avoir installer :
- ``python3``
- ``pip``
- ``sqlite3``
- ``git``
### Installation :
#### Ouvrez un terminal et entrez ces commandes
```bash
git clone https://github.com/Linux0Hat/LinuxBot.git
cd LinuxBot
pip install -r requirements.txt
```
## Configuration 
Ouvrez ``.env`` dans un éditeur de text ou de code et mofier le text de cette facon.

```
TOKEN=[le token de votre bot]
ARIVEE_CHANELL=[l'id du salon ou vous souhaiter faire l'annonce des nouveau membres]
DEPART_CHANNEL=[l'id du salon ou vous souhaiter faire l'annonce des départs de membres.]
BLAGUE_API=[token d'api de blague api. token gratuit : https://www.blagues-api.fr/]
NOMBRE_WARN_BAN=[le nombre de warn avant le ban]
```
## Lancer
```bash
python3 main.py
```
## Commandes
La liste de commandes sont disponibles en envoyant ``!help`` au bot quand il est lancer.
Il y a aussi un help avec les commandes réservées au administrateurs qui est  ``!help-admin``.
## Autres info
Le bot détècte automatiquement quel membre est administrateur et autorise les commandes au bonnes personnes.
### French discord bot
### Made by Linux_Hat https://github.com/Linux0Hat/LinuxBot