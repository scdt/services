#!/usr/bin/env python3
import asyncio
from datetime import datetime
from sqlitedict import SqliteDict
import random

class Timer:
    def __init__(self):
        self.users = SqliteDict("/data/users.sqlite", autocommit=True)
        self.historys = SqliteDict("/data/history.sqlite", autocommit=True)
        self.auctions = SqliteDict("/data/auctions.sqlite", autocommit=True)
    
    async def time(self):
        while True:
            auctions = []
            now = datetime.now();
            for auction in list(self.auctions.keys()):
                auctionTime = (now - self.auctions[auction]["auction"].timeStart).seconds
                if (auctionTime >= self.auctions[auction]["auction"].time):
                    auctions.append(self.auctions[auction]["title"])
            for auction in auctions:
                cost = 0;
                time = (now - self.auctions[auction]["auction"].timeStart).seconds
                for bet in self.auctions[auction]["auction"].bets:
                    if bet['user'] == self.auctions[auction]["auction"].winner['user']:
                        cost = bet['money'];
                        break;
                self.giveLot(auction, self.auctions[auction]["auction"].owner, self.auctions[auction]["auction"].winner, cost, self.auctions[auction]["auction"].lot, self.auctions[auction]["auction"].bets, time)
                
            self.commitAll();
            
            await asyncio.sleep(1)
            
    def commitAll(self):
        self.users.commit();
        self.auctions.commit();
        self.historys.commit();
        return;
            
    def giveLot(self, title, owner, winner, cost, lot, bets, auctionTime):
        if len(bets) <= 0:
            if self.auctions.get(title, None) != None:
                self.auctions.pop(title); 
                historyTitle = title;
                if (self.historys.get(title, None) != None):
                    historyTitle += str(random.randint(0, 1000000));
                self.historys[historyTitle] = {"owner": owner["login"], "title": historyTitle, "winner": "Naruto", "lot": lot, "time": auctionTime};
                self.historys.commit();
                self.auctions.commit();
                self.users.commit();
            return;
        
        bets = sorted(bets, key=lambda x: x["money"], reverse=True)
        if winner != None:
            winnerName = winner["user"] 
            if self.users[winnerName]["balance"] < cost:
                bets = bets[1:];
                if len(bets) <= 0:
                    self.auctions.pop(title);
                    self.auctions.commit();
                    historyTitle = title;
                    if (self.historys.get(title, None) != None):
                        historyTitle += str(random.randint(0, 1000000));
                    self.historys[historyTitle] = {"owner": owner["login"], "title": historyTitle, "winner": "Naruto", "lot": lot, "time": auctionTime};
                    self.historys.commit();
                    self.users.commit();
                    return;
                self.giveLot(title, owner, bets[0], bets[0]["money"], lot, bets);
            else:
                oldWinner = self.users[winnerName];
                copyWinner = self.users[winnerName];
                newBalance = copyWinner["balance"] - cost;
                newLots = copyWinner["lots"];
                newLots.append(lot);
                updateUser = {"login": oldWinner["login"], "password": oldWinner["password"], "balance": newBalance, "lots": newLots } 
                self.users.update({winnerName: updateUser})
                self.users.commit();
                
                oldOwner = self.users[owner["login"]];
                copyOwner = self.users[owner["login"]];
                newOwnerBalance = copyOwner["balance"] + cost;
                updateOwner = {"login": oldOwner["login"], "password": oldOwner["password"], "balance": newOwnerBalance, "lots": oldOwner["lots"] }
                self.users.update({owner["login"]: updateOwner})
                self.users.commit();
                
                self.auctions.pop(title);
                self.auctions.commit();
                
                historyTitle = title;
                if (self.historys.get(title, None) != None):
                    historyTitle += str(random.randint(0, 1000000));
                self.historys[historyTitle] = {"owner": owner["login"], "title": historyTitle, "winner": winnerName, "lot": lot, "time": auctionTime};
                self.historys.commit();
        else:
            if self.auctions.get(title, None) != None:
                historyTitle = title;
                if (self.historys.get(title, None) != None):
                    historyTitle += str(random.randint(0, 1000000));
                self.historys[historyTitle] = {"owner": owner["login"], "title": historyTitle, "winner": "Naruto", "lot": lot, "time": auctionTime};
                self.historys.commit();
                self.auctions.pop(title);
                self.auctions.commit(); 
                self.users.commit();
        return;
    
    def deleteAuction(self, title):
        cost = 0;
        now = datetime.now();
        time = (now - self.auctions[title]["auction"].timeStart).seconds
        for bet in self.auctions[title]["auction"].bets:
            if bet['user'] == self.auctions[title]["auction"].winner['user']:
                cost = bet['money'];
                break;
        self.giveLot(title, self.auctions[title]["auction"].owner, self.auctions[title]["auction"].winner, cost, self.auctions[title]["auction"].lot, self.auctions[title]["auction"].bets, time)
