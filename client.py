import socket
import enum
from utils import Utils,MessageType,UserData
from miscutils import Misc
import json




u = Utils()






class UserClient():

    def __init__(self,conn) -> None:
        self.conn:socket.socket = conn
        self.user_data:UserData = UserData()
        self.register_username()()



    def register_username(self):
        registered = False
        username = ""
        def inner():
            nonlocal registered,username
            while not registered:
                username = input("Username:")
                u.sendJson(self.conn,{
                    "type":"register",
                    "username":username
                    })

                #response
                json_dict,error = u.recvJson(self.conn)
                if error:
                    return

                success = json_dict['success']
                message = json_dict['message']

                registered = success
                print(f"\n{message} [success {success}]")

            self.user_data.set_username(username)
        return inner


    def request_messages(self):

        u.sendJson(self.conn,{
            "type":"view_messages",
            "username":self.user_data.username
            })

        data_json,error = u.recvJson(self.conn)

        if error:
            return


        success = data_json.get('success')
        data = data_json.get("data")
        message = data_json.get("message")

        if not success:
            print(message)
            return

        if success and data == None:
            print(message)
            return

        print(data)


    def get_users(self):

        u.sendJson(self.conn,{
            "type":"get_active_users",
            "username":self.user_data.username
            })

        data_json,error = u.recvJson(self.conn)
        if error:
            return



        success = data_json.get("success")
        data = data_json.get("data")
        message = data_json.get("message")



        if not success or data == None:
            return [],message

        return data,message


    def send_message(self):


        users,message = self.get_users()
        users_size = len(users)

        if users_size <= 0:
            print("no peps")
            print(message)
            return


        print("USERS")
        [print(f"({i}){users[i]}") for i in range(0,users_size)]
        index = int( input("Choose to send message:") )

        if (index >=0 and index <= users_size-1):

            message = input("Enter message:")

            user_chosen = users[index]
            u.sendJson(self.conn,{
                "type":"send_message",
                "to":user_chosen,
                "from":self.user_data.username,
                "message":message
                })
            data_json,error = u.recvJson(self.conn)
            if error:
                return
            success = data_json['success']
            message = data_json['message']
            print(message)


        pass

    def listen(self):
        print("Listen mode")
        while (True):
            data_bytes = u.recvPlain(self.conn)
            print(data_bytes)
            pass

    def exit(self):

        self.conn.close()
        exit(0)



    def menu(self):
        options = [
            ("View my messages", self.request_messages),
            ("Send message", self.send_message),
            ("Listen mode", self.listen),
            ("exit", self.exit),
        ]
        options_size = len(options)
        for i in range(0,options_size):
            print(f"({i}){options[i][0]}")

        index = int(input("Select option:"))
        Misc.cleanScreen()
        if (index >=0 and index <= options_size-1):
            options[index][1]()






address = ( "",9999 )
conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
conn.connect(address)


userclient = UserClient(conn)
while True:
    userclient.menu()


