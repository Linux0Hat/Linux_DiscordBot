# MIT License
#
# Copyright (c) 2022 Linux_Hat
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


# French discord bot
# Made by Linux_Hat https://github.com/Linux0Hat/LinuxBot

import sqlite3
import os
import time
from inspect import ArgInfo
from posixpath import join
import discord
from dotenv import load_dotenv
from blagues_api import *


# config
default_intents = discord.Intents.default()
load_dotenv()
TOKEN = os.getenv("TOKEN")
BLAGUE_API = os.getenv("BLAGUE_API")
ARIVEE_CHANELL = os.getenv("ARIVEE_CHANELL")
DEPART_CHANNEL = os.getenv("DEPART_CHANNEL")
NOMBRE_WARN_BAN = os.getenv("NOMBRE_WARN_BAN")
QUOI_FEUR= os.getenv("QUOI_FEUR")
STATUS_MESSAGE = os.getenv("STATUS_MESSAGE")
blagues = BlaguesAPI(BLAGUE_API)
anniv_wait_list = []
rm_data_wait_list = []
bon_anniv_wait_list = []


# SQL
db = sqlite3.connect("database.db")
cursor = db.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS "classement" ( "user_id"	INTEGER, "nbr_msg"	INTEGER );''')
cursor.execute('''CREATE TABLE IF NOT EXISTS "anniversaire" ( "user_id"	INTEGER, "date"	TEXT );''')
cursor.execute('''CREATE TABLE IF NOT EXISTS "warn" ( "user_id"	INTEGER, "num_warn"	INTEGER );''')

# Linux_DiscordBot
class LinuxBotClient(discord.Client):
    # Annonce quand le bot est prêt
    async def on_ready(self):
        print(f"Le bot est prêt et connécté en tant que {self.user} (id:{self.user.id}).")
        # apparance
        await self.change_presence(status=discord.Status.online, activity=None)
        if not STATUS_MESSAGE == "None":
            game = discord.Game(STATUS_MESSAGE)
            await self.change_presence(status=discord.Status.online, activity=game)
    
    
    # arrivées / départs
    async def on_member_join(self, member):
        arivee_channel: discord.TextChannel = self.get_channel(int(ARIVEE_CHANELL))
        embedVar=discord.Embed(title=f"Bienvenue sur le serveur {member} !! :partying_face:", description="", color=0xcc00ff)
        await arivee_channel.send(embed=embedVar)
        print(f"{member.display_name} est arrivé sur le serveur.")  
    
    async def on_member_remove(self, member):
        depart_channel: discord.TextChannel = self.get_channel(int(DEPART_CHANNEL))
        embedVar=discord.Embed(title=f"{member} est parti du serveur. :sob:", description="", color=0xcc00ff)
        await depart_channel.send(embed=embedVar)
        print(f"{member.display_name} est parti du serveur.")    
    

    # !clean-warn [mention] permet de supprimer les warns d'un utilisateur
    async def cmd_clean_warn(self, message):
        if message.author.permissions_in(message.channel).administrator :
            try :
                user = int(message.content.split("!clean-warn <@")[1].split(">")[0])
                if UserData.check_if_user_is_in_data_warn(user):
                    UserData.set_warn_to_0(user)
                else:
                    embedVar = discord.Embed(title=f":x: Cet utilisateur n'a pas encore été warn.", description='''''', color=0xff0000)
                    await message.channel.send(embed=embedVar)
                embedVar = discord.Embed(title=f"Le membre {self.get_user(user)} a été clean-warn.", description='''''', color=0x00ff00)
                await message.channel.send(embed=embedVar)
            except :
                embedVar = discord.Embed(title=f":x: Erreur de syntaxe", description='''Ecris bien "!clean-warn [mention]" c;''', color=0xff0000)
                await message.channel.send(embed=embedVar)
        else :
            embedVar = discord.Embed(title=f":x: Tu n'as pas la permission de faire ça.", description="", color=0xff0000)
            await message.channel.send(embed=embedVar) 
    

    # !warn [mention] permet de warn un utilisateur
    async def cmd_warn(self, message):
        if message.author.permissions_in(message.channel).administrator :
            try :
                user = int(message.content.split("!warn <@")[1].split(">")[0])
                warn_user : discord.Member = message.channel.guild.get_member(user)
                if warn_user == None :
                    embedVar = discord.Embed(title=f":x: Erreur, cet utilisateur ne fait pas parti du serveur.", description='''''', color=0xff0000)
                    await message.channel.send(embed=embedVar)
                    return
                else :    
                    if not warn_user.permissions_in(message.channel).administrator:
                        if UserData.check_if_user_is_in_data_warn(user):
                            UserData.update_warn_1(user)
                        else:
                            UserData.creat_user_warn(user)
                        embedVar = discord.Embed(title=f"Le membre {self.get_user(user)} as été warn.", description='''''', color=0x00ff00)
                        await message.channel.send(embed=embedVar)
                        num_warn = (UserData.get_warn_user(user))[0][0]
                        if num_warn >= int(NOMBRE_WARN_BAN):
                            embedVar = discord.Embed(title=f"Le membre {self.get_user(user)} va devoir être ban... Il a été warn {NOMBRE_WARN_BAN} fois...", description='''''', color=0xff0000)
                            await message.channel.send(embed=embedVar)
                            await warn_user.ban(reason=f"{self.get_user(user)} a été warn {NOMBRE_WARN_BAN} fois")
                    else :
                        embedVar = discord.Embed(title=f":x: Tu ne peux pas warn un administrateur c;", description="Bien essayé", color=0xff0000)
                        await message.channel.send(embed=embedVar) 
            except :
                embedVar = discord.Embed(title=f":x: Erreur de syntaxe", description='''Ecris bien "!warn [mention]" c;''', color=0xff0000)
                await message.channel.send(embed=embedVar)
        else :
            embedVar = discord.Embed(title=f":x: Tu n'as pas la permission de faire ça.", description="", color=0xff0000)
            await message.channel.send(embed=embedVar) 

    # cette commande renvoie des blagues
    async def cmd_blague(self, message):
        try :
            type_ = message.content.split()[1]
            blagues_str2type = {"global": BlagueType.GLOBAL,
                                "dev": BlagueType.DEV,
                                "dark": BlagueType.DARK,
                                "limit": BlagueType.LIMIT,
                                "beauf": BlagueType.BEAUF,
                                "blondes": BlagueType.BLONDES}
            type_ = blagues_str2type.get(type_)    
            if type_:
                blague = str(await blagues.random_categorized(type_))
                joke = blague.split("joke=")[1].split(" answer=")[0]
                joke = joke.replace("'", "")
                joke = joke.replace('''"''', "")
                answer = blague.split('''answer=''')[1]
                answer = answer.replace("'", "")
                answer = answer.replace('''"''', "")
                embedVar = discord.Embed(title=joke, description=f"||{answer}||", color=0x1ADE15)
            else:
                print("test")
                embedVar = discord.Embed(title=f":x: Erreur de syntaxe", description='''Les types de blagues sont : global, dev, dark, limit, beauf, blondes''', color=0xff0000)
        except :
            blague = str(await blagues.random(disallow=[BlagueType.LIMIT, BlagueType.BEAUF]))
            joke = blague.split("joke=")[1].split(" answer=")[0]
            joke = joke.replace("'", "")
            joke = joke.replace('''"''', "")
            answer = blague.split('''answer=''')[1]
            answer = answer.replace("'", "")
            answer = answer.replace('''"''', "")
            embedVar = discord.Embed(title=joke, description=f"||{answer}||", color=0x1ADE15)
        await message.channel.send(embed=embedVar)
    

     # permet de recevoir les info sur les données enregistré d'anniversaire
    async def cmd_info_anniv(self, message):
        rep = UserData.get_anniv_user(message.author.id)[0]
        if rep:
            embedVar = discord.Embed(title=f"{message.author}, Ta date d'anniversaire a été enregistrée en tant que {rep[1]}. Si tu souhaites la changer fais !add-anniversaire.", description="", color=0xffff00)
        else:
            embedVar = discord.Embed(title=f"{message.author}, Ta date d'anniversaire n'a pas été encore enregistrée. Pour enregistrer ta date d'anniversaire fais !add-anniversaire.", description="", color=0xff0000)
        await message.channel.send(embed=embedVar)


    # commande qui renvoie les anniversairs d'aujourd'hui et les futurs anniversaires ou la date d'anniversaire d'un utilisateur
    async def cmd_anniv(self, message):
        date = time.strftime("%d/%m/%Y")
        try :
            get_user_anniv = str((message.content.split("!anniversaire <@")[1]).split(">")[0])
            rep = UserData.get_anniv_user(get_user_anniv)
            embedVar = discord.Embed(title=f":x: {self.get_user(int(get_user_anniv))} n'a pas encore enregistré sa date d'anniversaire :disappointed:", description="", color=0xff0000)
            if rep:
               embedVar = discord.Embed(title=f''':cake: {self.get_user(int(get_user_anniv))} fête son anniversaire le {(rep[0])[1]}. Il/elle a actuellement {(int(date.split("/")[2])) - (int(((rep[0])[1]).split("/")[2]))} ans. :cake:''', description="", color=0xffff00)   
        except:
            rep = UserData.get_anniv_table()
            if rep == []:
                embedVar = discord.Embed(title=f"Personne n'a enregistré son anniversaire. :disappointed:", description="", color=0xffff00)
                await message.channel.send(embed=embedVar)
                return
            temp_value = []
            embedVar = discord.Embed(title=f"Aujourd'hui personne ne fête son anniversaire. :disappointed:", description="", color=0xffff00)  
            for i in rep:
                if f'''{i[1].split("/")[0]}/{i[1].split("/")[1]}''' == f'''{date.split("/")[0]}/{date.split("/")[1]}''':
                    temp_value.append(i)
            if temp_value:
                embedVar = discord.Embed(title=f":cake: Aujourd'hui, le {date} on fête l'anniversaire de :", description="", color=0xffff00) 
                for e in temp_value:
                    embedVar.add_field(name=f"{self.get_user(int(e[0]))}", value=f'''Il a maintenant {(int(date.split("/")[2]))-(int(e[1].split("/")[2]))} ans''', inline=False)
        rep = UserData.get_anniv_table()
        if rep == []:
            embedVar = discord.Embed(title=f"Personne n'a enregistré son anniversaire. :disappointed:", description="", color=0xffff00)
            await message.channel.send(embed=embedVar)
            return
        temp_value = []
        for y in range(int(date.split("/")[0])+1, 32):
            for x in rep :
                if f'''{x[1].split("/")[0]}/{x[1].split("/")[1]}''' == f'''{y}/{date.split("/")[1]}''':
                    temp_value.append(x)
        for i in range(1+int(date.split("/")[1]),12+int(date.split("/")[1])):
            if i>= 13:
                i=i-12
            i = str(i)
            if int(i) <= 9:
                i=f"{0}{i}"
            for e in range(1,32):
                e = str(e)
                if int(e) <= 9:
                    e=f"{0}{e}"
                for x in rep :
                    if f'''{x[1].split("/")[0]}/{x[1].split("/")[1]}''' == f'''{e}/{i}''':
                        temp_value.append(x)
        if temp_value:
            embedVar2 = discord.Embed(title="**:cake: Autres anniversaires à venir :**", description="", color=0xffff00)
            ii = 0
            for i in temp_value:
                ii = ii +1
                if ii == 3:
                    break
                ans = f'''{i[1].split("/")[0]}/{i[1].split("/")[1]}'''
                embedVar2.add_field(name=f"{self.get_user(i[0])} fêtera son anniversaire le {ans}", value=f'''Il aura {1+((int(date.split("/")[2]))-(int(i[1].split("/")[2])))} ans.''', inline=False)                    
        else:
            embedVar.add_field(name="Aucun autre annversaire n'est enregistré. :disappointed:", value="", inline=False)
        await message.channel.send(embed=embedVar)
        await message.channel.send(embed=embedVar2)
    
    
    # set anniv
    async def set_anniv(self, message):     
        if not message.content == "Annuler":
            temp_value=message.content.split("/")
            if len(temp_value[0])==2 and len(temp_value[1])==2 and len(temp_value[2])==4 and int(temp_value[0]) <= 31 and int(temp_value[1]) <= 12:
                if UserData.check_if_user_is_in_data_anniv(message.author.id):
                    UserData.update_anniv(message.author.id, message.content)
                else:
                    UserData.create_user_anniv(message.author.id, message.content)
                embedVar= discord.Embed(title=f":white_check_mark: Ta date d'anniversaire a bien été changée pour le {message.content}.", description='''''', color=0x00ff00)
                await message.channel.send(embed=embedVar)
                anniv_wait_list.remove(message.author.id)
            else:
                embedVar = discord.Embed(title=f":x: Erreur de syntaxe", descripion='''''', color=0xff0000)
                await message.channel.send(embed=embedVar)
        else:
            embedVar= discord.Embed(title=f":white_check_mark: Ta demande a bien été annulée.", description='''''', color=0x00ff00)
            await message.author.send(embed=embedVar)
            anniv_wait_list.remove(message.author.id)
    

    # ajout des anniversairs des membres
    async def cmd_add_anniv(self, message):
        embedVar= discord.Embed(title=f":white_check_mark: {message.author} nous t'avons envoyé un mp pour que tu puisse modifier ta date d'anniversaire.", description="", color=0xffff00)
        await message.reply(embed=embedVar)
        embedVar= discord.Embed(title=f"CHANGER SA DATE D'ANNIVERSAIRE", description='''Pour changer ta date d'anniversaire écrit ta date de naissance dans ce channel au format JJ/MM/AAAA. Ecris "Annuler" si tu souaites annuler ce changement.''', color=0xffff00)
        await message.author.send(embed=embedVar)
        anniv_wait_list.append(message.author.id)


    # ajout des message au classement
    async def add_msg_classement(self, message):
        if UserData.check_if_user_is_in_data_classement(message.author.id):
            UserData.update_classement_1(message.author.id)
        else:
            UserData.create_user_classement(message.author.id)


    # !classement revoyer le top 10 du classement
    async def cmd_classement(self, message):
        temp_list = []
        ii = 1
        for i in UserData.return_top_classement():
            temp_list.append(f"\n**{ii} : {self.get_user(i[0])}** : {i[1]} messages.") 
            ii=ii+1
        embedVar = discord.Embed(title=f"Classement Top 10", description=" ".join(temp_list), color=0xffff00)
        await message.channel.send(embed=embedVar)


    # renvoyer les scores personnels ou d'autre membres
    async def cmd_score(self, message):
        try :
            user = int(((message.content.split("!score ")[1]).split("<@")[1]).split(">")[0])
            user_score = self.get_user(user)
            nbr_msg_user = UserData.get_score_user(user)[0][0]
            found = False
            while found==False:
                for i in UserData.get_top_classement():
                    if i[0]==user:
                        myRank = i[2]
                        found = True
            embedVar = discord.Embed(title=f"Rank : {myRank}.  Le score de {user_score} est a {nbr_msg_user}.", description="", color=0xffff00)
            await message.channel.send(embed=embedVar)
        except:
            nbr_msg_user = UserData.get_score_user(message.author.id)[0][0]
            found = False
            while found==False:
                for i in UserData.get_top_classement():
                    if i[0]==message.author.id:
                        myRank = i[2]
                        found = True
            embedVar = discord.Embed(title=f"Rank : {myRank}.  Le score de {message.author} est a {nbr_msg_user}.", description="", color=0xffff00)
            await message.channel.send(embed=embedVar)


    # permet de changer le score d'un utilisateur
    async def cmd_change_score(self, message):
        if message.author.permissions_in(message.channel).administrator:
            try :
                score_user_id=int((message.content.split("!change-score <@")[1]).split(">")[0])
                score_user=self.get_user(score_user_id)
                change_score=int((message.content.split("!change-score <@")[1]).split("> ")[1])
                if UserData.check_if_user_is_in_data_classement(score_user_id):
                    UserData.change_score(score_user_id, change_score)
                else :
                    UserData.create_user_classement(score_user_id, change_score)    
                embedVar = discord.Embed(title=f":white_check_mark: Le score de {score_user} a été bien changé pour {change_score}", description="", color=0x00ff00)
                await message.channel.send(embed=embedVar)
            except :
                embedVar = discord.Embed(title=f":x: Erreur de syntaxe", description="", color=0xff0000)
                await message.channel.send(embed=embedVar)                   
        else :
            embedVar = discord.Embed(title=f":x: Tu n'as pas la permission de faire ça.", description="", color=0xff0000)
            await message.channel.send(embed=embedVar)   
    

    # quoi feur / oui stiti
    async def quoi_feur(self, message):
        quoi_oui = [w for w in message.content.lower().split() if w]
        if 'quoi' in quoi_oui:
           await message.channel.send("feur")
        if 'oui' in quoi_oui:
           await message.channel.send("stiti")
    

    # commade !del supprime les derniers messages (!del [nombre de message a supprimer])
    async def cmd_del(self, message):
        if message.author.permissions_in(message.channel).manage_messages:
            try :
                number = int(message.content.split()[1])
            except :
                number = 1    
            messages = await message.channel.history(limit=number+1).flatten()
            for each_messages in messages:
                await each_messages.delete()
            embedVar = discord.Embed(title=f":white_check_mark: {number} messages ont bien été supprimés.", description="", color=0x00ff00)
            await message.channel.send(embed=embedVar)    
        else:
            embedVar = discord.Embed(title=f":x: Tu n'as pas la permission de faire ça.", description="", color=0xff0000)
            await message.channel.send(embed=embedVar) 


    # commande !stop-bot permet de stopper le bot
    async def cmd_stop_bot(self, message):
        if message.author.permissions_in(message.channel).administrator:
            db.close()
            embedVar = discord.Embed(title=f":white_check_mark: Le bot s'est bien stoppé.", description="", color=0x00ff00)
            await message.channel.send(embed=embedVar)
            exit()
        else :
            embedVar = discord.Embed(title=f":x: Tu n'as pas la permission de faire ça.", description="", color=0xff0000)
            await message.channel.send(embed=embedVar)       
    

    # !help renvoie la liste des commandes 
    async def cmd_help(self, message):
        embedVar = discord.Embed(title=f"Liste de commandes :", description="", color=0xcc00ff)
        embedVar.add_field(name="!classement", value="Cette commande renvoie le top 10 des membres qui parlent le plus sur le serveur.", inline=False)
        embedVar.add_field(name="!score [membre (mention)]", value="Cette commande renvoie le score personnel en segond argument.", inline=False)
        embedVar.add_field(name="!add-anniversaire", value="Cette commande permet d'ajouter ou de modifier sa date d'anniversaire", inline=False)
        embedVar.add_field(name="!anniversaire [membre (mention)]", value="Cette commande permet de s'informer sur les anniversairs des membres", inline=False)
        embedVar.add_field(name="!info-anniversaire", value="Cette commande permet d'obtenir des infos sur les données enregistrées sur votre anniversaire", inline=False)
        embedVar.add_field(name="!blague [type]", value="Cette commande permet d'obtenir des blagues", inline=False)
        await message.channel.send(embed=embedVar)


    # !help-admin renvoie la liste des commandes admin
    async def cmd_help_admin(self, message):
        if message.author.permissions_in(message.channel).administrator :
            embedVar = discord.Embed(title=f"Liste de commandes admin:", description="", color=0xcc00ff)
            embedVar.add_field(name="!change-score [membre (mention)] [nouveau score du membre]", value="Cette commande change le score d'un membre.", inline=False)
            embedVar.add_field(name=f"!stop-bot", value="Cette commande stoppe le bot {self.user} (réservé aux administrateurs).", inline=False)
            embedVar.add_field(name=f"!del [value]", value="Permet de supprimer les derniers messages.", inline=False)
            embedVar.add_field(name=f"!warn [mention]", value=f"Permet de warn un utilisateur (si il est warn {NOMBRE_WARN_BAN} fois il sera ban).", inline=False)
            embedVar.add_field(name=f"!clean-warn [mention]", value="Permet de retirer les warns d'un utilisateur", inline=False)
            await message.channel.send(embed=embedVar)
        else:
            embedVar = discord.Embed(title=f":x: Tu n'as pas la permission de faire ça.", description="", color=0xff0000)
            await message.channel.send(embed=embedVar)   

    # cmd reset user data
    async def cmd_rest_data(self, message):
        if message.author.permissions_in(message.channel).administrator :
            embed = discord.Embed(title=f"EST TU SUR DE VOULOIR SUPPRIMER LES DONNEES UTILISATEURS ? CETTE ACTION EST IRREVERSIBLE", description='''Envois "Oui" pour confirmer sinon répons "Annuler"''', color=0xff0000)
            await message.author.send(embed=embed)
            embed = discord.Embed(title=f"Nous t'avons envoyer un mp.", description="", color=0xff0000)
            await message.reply(embed=embed)
            rm_data_wait_list.append(message.author.id)
        else :
            embedVar = discord.Embed(title=f":x: Tu n'as pas la permission de faire ça.", description="", color=0xff0000)
            await message.channel.send(embed=embedVar)

    async def confirm_rm_data(self, message):
        if message.content.startswith("Oui"):
            os.remove("database.db")
            UserData()
            embedVar = discord.Embed(title=f"Données utilisateurs supprimées.", description="", color=0xff0000)
            await message.channel.send(embed=embedVar)

        elif message.content.startswith("Annuler"):
            embedVar = discord.Embed(title=f"Demande annulée", description="", color=0x00ff00)
            await message.channel.send(embed=embedVar)

    # interaction textuel
    async def on_message(self, message):
        if not message.author.id == self.user.id:
            # écrit les messages reçus
            print(f"{message.author} from {message.channel}: {message.content}")

            # other
            await self.add_msg_classement(message)
            if message.author.id in anniv_wait_list and str(message.channel) == f"Direct Message with {message.author}":
                await self.set_anniv(message)
    
            elif message.author.id in rm_data_wait_list and str(message.channel) == f"Direct Message with {message.author}":
                await self.confirm_rm_data(message)

            # commandes
            elif message.content.startswith("!blague") :
                await self.cmd_blague(message)
    
            elif message.content == "!info-anniversaire":
                await self.cmd_info_anniv(message)
    
            elif message.content.startswith("!anniversaire"):
                await self.cmd_anniv(message)
    
            elif message.content.startswith("!add-anniversaire"):
                await self.cmd_add_anniv(message)

            elif message.content.startswith("!classement"):
                await self.cmd_classement(message)
    
            elif message.content.startswith("!score"):
                await self.cmd_score(message)
    
            elif message.content.startswith("!del"):
                await self.cmd_del(message)
    
            elif message.content == "!help":
                await self.cmd_help(message)

            # commandes administrateur
            elif message.content.startswith("!stop-bot"):   
                await self.cmd_stop_bot(message)

            elif message.content.startswith("!change-score"):
                await self.cmd_change_score(message)
       
            elif message.content.startswith("!warn"):
                await self.cmd_warn(message)

            elif message.content.startswith("!help-admin"):
                await self.cmd_help_admin(message)

            elif message.content.startswith("!clean-warn"):
                await self.cmd_clean_warn(message)
    
            elif message.content == "!reset-data":
                await self.cmd_rest_data(message)

            # other
            elif QUOI_FEUR == "on":
                await self.quoi_feur(message)

class UserData():
    def __init__(self):
        db = sqlite3.connect("database.db")
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS "classement" ( "user_id"	INTEGER, "nbr_msg"	INTEGER );''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS "anniversaire" ( "user_id"	INTEGER, "date"	TEXT );''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS "warn" ( "user_id"	INTEGER, "num_warn"	INTEGER );''')
    
    def check_if_user_is_in_data_warn(user): #92 122
        cursor.execute(f"SELECT user_id FROM warn WHERE user_id = {user}")
        return cursor.fetchall()

    def set_warn_to_0(user):
        cursor.execute(f"UPDATE warn SET num_warn = 0 WHERE user_id = {user}")
        db.commit()

    def update_warn_1(user):
        cursor.execute(f"UPDATE warn SET num_warn = num_warn + 1 WHERE user_id = {user}") 
        db.commit()

    def creat_user_warn(user):
        cursor.execute(f"INSERT INTO warn VALUES({user}, 1)")    
        db.commit()

    def get_warn_user(user):
        cursor.execute(f"SELECT num_warn FROM warn WHERE user_id = {user}")
        return cursor.fetchall()

    def get_anniv_user(user):
        cursor.execute(f"SELECT * FROM anniversaire WHERE user_id = {user}")
        return cursor.fetchall()
    
    def get_anniv_table():
        cursor.execute(f"SELECT * FROM anniversaire")
        return cursor.fetchall()

    def check_if_user_is_in_data_anniv(user):
        cursor.execute(f"SELECT user_id FROM anniversaire WHERE user_id = {user}") 
        return cursor.fetchall() 
    
    def update_anniv(user, date):
        cursor.execute(f'''UPDATE anniversaire SET date = "{date}" WHERE user_id = {user}''')
        db.commit()

    def create_user_anniv(user, date):
        cursor.execute(f'''INSERT INTO anniversaire VALUES({user},"{date}")''')
        db.commit()

    def check_if_user_is_in_data_classement(user):
        cursor.execute(f'SELECT user_id from classement where user_id = {user};')
        return cursor.fetchall() 

    def update_classement_1(user):
        cursor.execute(f"UPDATE classement SET nbr_msg = nbr_msg + 1 WHERE user_id = {user}")
        db.commit()

    def create_user_classement(user, value=1):
        cursor.execute(f"INSERT INTO classement VALUES({user},{value})")
        db.commit()
    
    def return_top_classement(top=10):
        cursor.execute(f'SELECT * FROM classement ORDER BY nbr_msg DESC LIMIT {top}')
        return cursor.fetchall()

    def get_score_user(user):
        cursor.execute(f'SELECT nbr_msg FROM classement WHERE user_id = {user}')
        return cursor.fetchall()

    def get_top_classement():
        cursor.execute('SELECT user_id, nbr_msg, RANK () OVER ( ORDER BY nbr_msg DESC) myRank FROM classement;')
        return cursor.fetchall()

    def change_score(user, value):
        cursor.execute(f"UPDATE classement SET nbr_msg = {value} WHERE user_id = {user}")
        db.commit()


        
# lancer le client  
def main(): 
    default_intents = discord.Intents.default()
    default_intents.members = True
    UserData()
    client = LinuxBotClient(intents=default_intents)           
    client.run(TOKEN) 

if __name__ == "__main__":
    main()