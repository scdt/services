import shlex
import hashlib
from datetime import datetime
from prettytable import PrettyTable
from sqlitedict import SqliteDict

HELP = """
\033[1;32mregister <login> <password>\033[0m - Register a new user
\033[1;32mlogin <login> <password>\033[0m - Login with given credentials

(if logged in)
\033[1;32mlist\033[0m - List all auctions
\033[1;32minfo\033[0m - List my own lots, auctions and balance
\033[1;32mcreate <title> <lot> <minimalBet = 1> <password = None>\033[0m - Create new Auction with lot
\033[1;32mbet <title> <money> <password = None>\033[0m - Place a bid at an auction (password if needed)

""".strip()

WELCOME = """
\033[1;31m࿋ ࿋ ࿋ \033[0m Welcome to the Secrets of Kanoha Auction! \033[1;31m࿋ ࿋ ࿋ \033[0m 
""".strip()


class AppLogic:
    def __init__(self, timer):
        self.user = None
        self.timer = timer
        self.users = SqliteDict("/data/users.sqlite", autocommit=True)
        self.historys = SqliteDict("/data/history.sqlite", autocommit=True)
        self.auctions = SqliteDict("/data/auctions.sqlite", autocommit=True)

    def __del__(self):
        self.user = None

    def welcome_message(self):
        return WELCOME + "\n\nAvailable commands:\n" + self.help();

    def help(self):
        return HELP

    def create(self, title, lot, minBet=1, time=None, pwd=None):
        if self.user != None:
            if title not in list(self.auctions.keys()):
                self.auctions[title] = {"title": title, "owner": self.user["login"], "minBet": minBet, "auction": Auction(self.user, lot, title, int(minBet), time, pwd)};
                self.auctions.commit()
                return "\033[1;32mSuccessfully create auction - {0}\033[0m".format(title)
            else:
                self.timer.deleteAuction(title)
                self.auctions[title] = {"title": title, "owner": self.user["login"], "minBet": minBet, "auction": Auction(self.user, lot, title, int(minBet), time, pwd)};
                self.auctions.commit()
                return "\033[1;32mSuccessfully create auction - {0}\033[0m".format(title)
        else:
            return "\033[1;31mPlease log in firstly!\033[0m"

    def register(self, login, password):
        if login not in list(self.users.keys()):
            self.users[login] = {"login": login,
                                 "password": password,
                                 "balance": 100,
                                 "lots": []};
            self.users.commit()
            return "\033[1;32mSuccessfully registered\033[0m"
        else:
            return "\033[1;31mSorry but user already exists\033[0m"

    def login(self, login, password):
        if login not in list(self.users.keys()):
            return "\033[1;31mUser doesn't exists\033[0m"
        elif password == self.users[login]['password']:
            self.setUser(self.users[login])
            return "\033[1;32mSuccessfully logged in\033[0m"
        else:
            return "\033[1;31mInvalid password\033[0m"

    def list(self):
        if len(list(self.auctions.keys())) <= 0:
            return "\033[1;31mThere aren't auctions, Datte Bayo\033[0m"

        result = "\033[01;38;05;214m࿋ ࿋ ࿋  This is a list of Auctions ࿋ ࿋ ࿋ \033[0m\n"
        auctionTable = PrettyTable()
        auctionTable.field_names = ["Title", "Owner", "Min Bet"]
        for auction in list(self.auctions.keys()):
            auctionTable.add_row([self.auctions[auction]["title"], self.auctions[auction]["owner"], self.auctions[auction]["minBet"]])

        result += str(auctionTable)
        return result

    def history(self):
        if self.user != None:
            if not self.user.get("naruto", False):
                return "\033[01;38;05;214mDatte Bayo\033[0m"

        result = "\033[01;38;05;214m࿋ ࿋ ࿋  History ࿋ ࿋ ࿋ \033[0m\n"
        historyTable = PrettyTable()
        historyTable.field_names = ["Title", "Winner", "Owner", "Lot", "Time"]
        for key in list(self.historys.keys()):
            historyTable.add_row([self.historys[key]["title"], self.historys[key]["winner"], self.historys[key]["owner"], "\033[1;32m" + self.historys[key]["lot"] + "\033[0m", self.historys[key]["time"]])
        if (len(list(self.historys.keys())) > 0):
            result += str(historyTable)
        return result

    def info(self):
        if self.user == None:
            return "\033[1;31mPlease log in firstly!\033[0m"

        user = self.users.get(self.user["login"], None)
        if user == None:
            return "BAD"

        result = "\033[01;38;05;214m࿋ ࿋ ࿋  Your Nickname ࿋ ࿋ ࿋\033[0m\n"
        result += "Your Name, Datte Bayo : \033[1;32m" + str(self.user["login"]) + "\033[0m\n";

        result += "\033[01;38;05;214m࿋ ࿋ ࿋  Your lots ࿋ ࿋ ࿋\033[0m\n"
        if len(user["lots"]) > 0:
            for lots in user["lots"]:
                result += "Lot : " + lots + "\n";
        else:
            result += "Sorry you don't have lots yet. We'll be lucky another time, Datte Bayo" + "\n"

        result += "\033[01;38;05;214m࿋ ࿋ ࿋  Your balance ࿋ ࿋ ࿋\033[0m\n"
        result += "Your money, Datte Bayo : " + str(user["balance"]) + "\n";

        result += "\033[01;38;05;214m࿋ ࿋ ࿋  Your own running Auctions ࿋ ࿋ ࿋\033[0m\n"
        runningAuctionTable = PrettyTable()
        runningAuctionTable.field_names = ["Title", "Lot", "TimeStart"]
        count = 0
        for key in list(self.auctions.keys()):
            if self.auctions[key]["owner"] == user["login"]:
                count += 1
                runningAuctionTable.add_row([self.auctions[key]["title"], self.auctions[key]["auction"].lot, self.auctions[key]["auction"].timeStart])

        if count > 0:
            result += str(runningAuctionTable) + "\n"
        else:
            result += "Sorry you don't have running auctions, Datte Bayo" + "\n"

        result += "\033[01;38;05;214m࿋ ࿋ ࿋  Your own ended Auctions ࿋ ࿋ ࿋\033[0m\n"
        auctionTable = PrettyTable()
        auctionTable.field_names = ["Title", "Lot", "Winner", "Time"]
        count = 0
        for key in list(self.historys.keys()):
            if self.historys[key]["owner"] == user["login"]:
                count += 1
                auctionTable.add_row([self.historys[key]["title"], self.historys[key]["lot"], self.historys[key]["winner"], self.historys[key]["time"]])

        if count > 0:
            result += str(auctionTable)
        else:
            result += "Sorry you don't have ended auctions, Datte Bayo" + "\n"

        return result

    def bet(self, title, cost, pwd=None):
        if self.user != None and title in list(self.auctions.keys()):
            try:
                intCost = int(cost)
            except:
                return "A CHE MOZNO BUKAVKI POSTAVIT'?!?!?!?!"

            if self.auctions[title]["auction"].pwd != None and self.auctions[title]["auction"].pwd != pwd:
                return "PAROL NE VEREN LOX"

            if intCost < self.auctions[title]["auction"].minBet:
                return "SORRY POSTAV' POBOLSHE PLZ"

            if intCost < 0:
                return "POSHEL TI NAXER KOZEL"

            copy = self.auctions[title]
            copyAuction = self.auctions[title]["auction"]

            if copyAuction.winner != None:
                if copyAuction.winner["money"] < intCost:
                    copyAuction.winner = {'user': self.user["login"], 'money': intCost};
            else:
                copyAuction.winner = {'user': self.user["login"], 'money': intCost};
            copyAuction.bets.append({'user': self.user["login"], 'money': intCost})
            new = {"title": copy["title"], "owner": copy["owner"], "minBet": copy["minBet"], "auction": copyAuction}
            self.auctions[title] = new
            self.auctions.commit()
            return "\033[1;32mYour bet is OK\033[0m"
        else:
            return "\033[1;31mSomething went wrong, Datte Bayo\033[0m"

    def setUser(self, user):
        self.user = user
        return

    def godmode(self, activate):
        if not self.user:
            return "\033[1;31mPlease log in\033[0m"
        hash_object = hashlib.md5(activate.encode())
        if hash_object.hexdigest() == "625a36b8e63c2f4b2d3fb9a07f64235d":
            self.user['naruto'] = True
            return "\033[1;32mOh, you are Naruto\033[0m"
        else:
            self.user['naruto'] = False
            return "\033[1;31mSorry, but you are Sasuke ࿋\033[0m"


class Auction:
    def __init__(self, owner, lot, title, minBet=1, time=None, pwd=None):
        self.title = title
        self.owner = owner
        self.minBet = minBet
        self.pwd = pwd
        self.lot = lot
        if time == None:
            self.time = 60
        else:
            self.time = int(time)
        self.bets = []
        self.winner = None
        self.timeStart = datetime.now()
        self.timeEnd = None

    def __del__(self):
        self.title = None
        self.owner = None
        self.lot = None
        self.winner = None
        self.bets = None

    def bet(self, user, cost):
        if self.winner != None:
            if self.winner["money"] < cost:
                self.winner = {'user': user, 'money': cost};
        else:
            self.winner = {'user': user, 'money': cost};
        self.bets.append({'user': user, 'money': cost})
