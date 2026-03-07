import _thread
import struct
import time
import random
import pprint
import socket
from utils import Utils,MessageType,UserData
import json

u = Utils()


class UsersController:



    def __init__(self) -> None:

        self.users_inbox = {}
        self.users_sockets:list["UserSocket"] = []

        
        self.api = {
        "register":self.register,
        "view_messages":self.view_messages,
        "get_active_users":self.get_active_users,
        "send_message":self.send_message,
        "user_quit":self.user_quit,
        }

    
    def _get_user_socket(self,_username:str) -> "UserSocket | None":

        for obj in self.users_sockets:
            username = obj.user_data.username
            if  _username == username:
                return obj

        return None


    def _add_user_socket(self,usersocket:'UserSocket'):
        self.users_sockets.append(usersocket)

    def _del_user_socket(self,usersocket:'UserSocket'):
        current_username  = usersocket.user_data.username

        i = 0
        for obj in self.users_sockets:
            username = obj.user_data.username

            if current_username == username:
                self.users_sockets.pop(i)
                break

            i += 1


        
            

        self.users_sockets.append(usersocket)




    def register(self,usersocket:'UserSocket',json_data):

        username = json_data["username"]
        if username in self.users_inbox:
            u.sendJson(usersocket.conn,{
                    'message': 'Name is used',
                    'success':False,
                    })
            return
        self.users_inbox[username] = {}

        u.sendJson(conn,{
                'message': 'You are registered',
                'success':True,
                })
        usersocket.user_data = UserData()
        usersocket.user_data.set_username(username)
        self._add_user_socket(usersocket)
        

    def view_messages(self,usersocket:'UserSocket',json_data):
        username:str = json_data["username"]

        if username == None:
            return

        if username  not in self.users_inbox:
            u.sendJson(usersocket.conn,{
                'message':'Your username not registed lol?',
                'success':False
                })
            return

        if len( self.users_inbox[username].keys() ) <= 0:
            u.sendJson(usersocket.conn,{
                'message': "You have zero message",
                'success':True
                })
            return

        
        u.sendJson(usersocket.conn,{
            'success':True,
            'data':self.users_inbox[username]
            })

        return

    def get_active_users(self,usersocket:'UserSocket',json_data):
        username:str = json_data["username"]
        active_users = list(self.users_inbox.keys())
        active_users = [user for user in active_users if user != username]

        if len(active_users) <= 0:
            u.sendJson(usersocket.conn,{
                "success":False,
                "message":"There are no other users connected"
                })
            return

        u.sendJson(usersocket.conn,{
            "success":True,
            "data":active_users,
            "message":f"There are {len(active_users)} users"

            })




    def send_message(self,usersocket:'UserSocket',json_data):
         
        to_user = json_data.get("to")
        from_user = json_data.get("from")
        message = json_data.get("message")

        user_inbox:dict = self.users_inbox[to_user]

        if from_user not in user_inbox.keys():
            user_inbox[from_user] = []
            pass

        user_inbox[from_user].append(message)
        u.sendSuccess(usersocket.conn,"Message sent",success=True)

        to_usersocket = self._get_user_socket(to_user)
        if (to_usersocket != None):
            print(f"sending message to {to_usersocket.user_data.username}")
            to_usersocket.send(message)

        
    def user_quit(self,usersocket:'UserSocket'):
        username = usersocket.user_data.username
        del self.users_inbox[username]
        print(self.users_inbox)
        print(f"User {username} quits")

        self._del_user_socket(usersocket)

        pass
        

        
    def json_type_do_action(self,usersocket:'UserSocket',json_data):
        type_d = json_data["type"]

        if type_d not in self.api:
            print(f"Error, {type_d} is not in api")
            return

        self.api[type_d](usersocket,json_data)





        
        


users_controller = UsersController()



sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(( "",9999 ))
sock.listen(1)





class UserSocket():

    def __init__(self,conn,conn_ip,conn_port) -> None:
        self.conn = conn
        self.conn_ip = conn_ip
        self.conn_port = conn_port
        self.user_data: UserData = UserData()
        self.communication()


    def send(self,message):
        u.sendPlain(self.conn,message)



    def communication(self):


        def main():
            while True:
                data = u.readData(self.conn,u.PREFIX_LENGTH)

                print(len(data))
                if (len(data) <=0):
                    print("Connection ended")
                    users_controller.user_quit(self)
                    self.conn.close()
                    break

                type_m,message_size = u.unpack_message_prefix(data)
                print(message_size)
                data = u.readData(self.conn,message_size)

                if (type_m == MessageType.PLAIN):
                    print("its plain")

                if (type_m == MessageType.JSON):
                    data = json.loads(data)
                    users_controller.json_type_do_action(self,data)

                print(data)
        _thread.start_new_thread(main,())





while True:
    conn,address = sock.accept()
    # print(address,conn)
    print("connected")
    UserSocket(conn,address[0],address[1])

