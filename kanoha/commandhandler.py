import shlex

class CommandHandler:
    transport = None

    def __init__(self, applogic):
        self.applogic = applogic

    def exec_command(self, s):
        command = shlex.split(s)
        
        if command[0] == "welcome_message":
            try:
                result = self.applogic.welcome_message();
            except Exception as e:
                result = str(e)
            finally:
                self.answer(str(result))
        elif command[0] == "login":
            try:
                result = self.applogic.login(command[1], command[2]);
            except Exception as e:
                result = str(e)
            finally:
                self.answer(str(result))
        elif command[0] == "register":
            try:
                result = self.applogic.register(command[1], command[2]);
            except Exception as e:
                result = str(e)
            finally:
                self.answer(str(result))
        elif command[0] == "create":
            try:
                if len(command) == 3:
                    result = self.applogic.create(command[1], command[2]);
                if len(command) == 4:
                    result = self.applogic.create(command[1], command[2], command[3]);
                if len(command) == 5:
                    result = self.applogic.create(command[1], command[2], command[3], command[4]);
                if len(command) == 6:
                    result = self.applogic.create(command[1], command[2], command[3], command[4], command[5]);
            except Exception as e:
                result = str(e)
            finally:
                self.answer(str(result))
        elif command[0] == "bet":
            try:
                if len(command) == 3:
                    result = self.applogic.bet(command[1], command[2]);
                if len(command) == 4:
                    result = self.applogic.bet(command[1], command[2], command[3]);
            except Exception as e:
                result = str(e)
            finally:
                self.answer(str(result))
        elif command[0] == "list":
            try:
                result = self.applogic.list();
            except Exception as e:
                result = str(e)
            finally:
                self.answer(str(result))
        elif command[0] == "history":
            try:
                result = self.applogic.history();
            except Exception as e:
                result = str(e)
            finally:
                self.answer(str(result))
        elif command[0] == "info":
            try:
                result = self.applogic.info();
            except Exception as e:
                result = str(e)
            finally:
                self.answer(str(result))
        elif command[0] == "godmode":
            try:
                result = self.applogic.godmode(command[1]);
            except Exception as e:
                result = str(e)
            finally:
                self.answer(str(result))
        else:
            self.answer("MDAAAAAAAAAAAAAAAAAAAAAAAAAA")

    def answer(self, s, end="\n> "):
        self.transport.write((s + end).encode())
