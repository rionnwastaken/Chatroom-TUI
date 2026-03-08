import _thread
import struct
import time
import random
import pprint
import socket
from typing import Any
from utils import Utils,MessageType,UserData,ServerApi,ClientApi,NotificationApi
import json
import queue 

u = Utils()

s = ServerApi
c = ClientApi
n = NotificationApi

class UsersController:



    def __init__(self) -> None:

        self.active_users = {}
        self.users_sockets:list["UserSocket"] = []

        
        self.api = {
        s.REGISTER:self.register,
        s.GET_ACTIVE_USERS:self.get_active_users,
        s.SEND_MESSAGE:self.send_message,
        s.USER_QUIT:self.user_quit,
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
        response = Response()

        if username in self.active_users:
            usersocket.new_response({
                    'message': 'Name is used',
                    'success':False,
                    'type':c.REGISTER_RESPONSE
                    })
            return
        self.active_users[username] = {}

        usersocket.new_response({
                'message': 'You are registered',
                'success':True,
                'type':c.REGISTER_RESPONSE
                })


        usersocket.user_data = UserData()
        usersocket.user_data.set_username(username)
        self._add_user_socket(usersocket)
        

    # def get_messages(self,usersocket:'UserSocket',json_data):
    #     username:str = json_data["username"]
    #
    #     if username == None:
    #         return
    #
    #     if username  not in self.users_inbox:
    #
    #         usersocket.new_response({
    #             'message':'Your username not registed lol?',
    #             'success':False,
    #             'type':c.GET_MESSAGES_RESPONSE
    #             })
    #         return
    #
    #     if len( self.users_inbox[username].keys() ) <= 0:
    #         usersocket.new_response({
    #             'message': "You have zero message",
    #             'success':True,
    #             'type':c.GET_MESSAGES_RESPONSE
    #             })
    #         return
    #
    #     usersocket.new_response({
    #
    #         'success':True,
    #         'data':self.users_inbox[username],
    #         'type':c.GET_MESSAGES_RESPONSE
    #         })
    #     return

    def get_active_users(self,usersocket:'UserSocket',json_data):
        username:str = json_data["username"]
        active_users = list(self.active_users.keys())
        active_users = [user for user in active_users if user != username]

        if len(active_users) <= 0:
            usersocket.new_response({
                "success":False,
                "message":"There are no other users connected",
                'type':c.GET_ACTIVE_USERS_REPONSE
                })
            return

        usersocket.new_response({
            "success":True,
            "data":active_users,
            "message":f"There are {len(active_users)} users",
                'type':c.GET_ACTIVE_USERS_REPONSE

            })




    def send_message(self,usersocket:'UserSocket',json_data):
         
        to_user = json_data.get("to")
        from_user = json_data.get("from")
        message = json_data.get("message")


        # if from_user not in user_inbox.keys():
        #     user_inbox[from_user] = []
        #     pass
        #
        # user_inbox[from_user].append(message)

        usersocket.new_response({
            "message":"Message sent",
            "success":True,
            'type':c.SEND_MESSAGE_RESPONSE,
            })
        to_usersocket = self._get_user_socket(to_user)
        if (to_usersocket != None):
            print(f"sending message to {to_usersocket.user_data.username}")
            to_usersocket.new_response({"from":from_user, "message":message,"type":n.RECEIVE_MESSAGE})

        
    def user_quit(self,usersocket:'UserSocket'):
        username = usersocket.user_data.username

        if username in self.active_users:
            del self.active_users[username]
            print(f"User {username} quits")

        print(self.active_users)
        self._del_user_socket(usersocket)

        pass
        

        
    def json_type_do_action(self,usersocket:'UserSocket',json_data):
        type_d = json_data["type"]

        if type_d not in self.api:
            print(f"Error, {type_d} is not in api")
            return

        self.api[type_d](usersocket,json_data)


    def notify_clients(self,data_type,data_json,who_ignore = None):
        for user_socket in self.users_sockets:
            self.users_sockets
            pass




        
        


users_controller = UsersController()






class Response():
    def __init__(self) -> None:
        self.type:MessageType
        self.data:Any = None







class UserSocket():

    def __init__(self,conn,conn_ip,conn_port) -> None:
        self.conn = conn
        self.conn_ip = conn_ip
        self.conn_port = conn_port
        self.user_data: UserData = UserData()
        self.responses_queue = queue.Queue()

        self.start_threads()


    def send(self,message):
        u.sendPlain(self.conn,message)



    def new_response(self,_data:Any):
        response = Response()
        response.data = _data

        if (isinstance(_data,dict)):
            response.type = MessageType.JSON

        if (isinstance(_data,str)):
            response.type = MessageType.PLAIN

        if (getattr(response,'type',None) == None):
            print(f"Error, response.type is None. Type is {type(_data)}")
            return

        self.responses_queue.put(response)





    def start_threads(self):


        def recvLoop():
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

        def sendLoop():

            while (True):
                response:Response = self.responses_queue.get(block=True)

                _type = response.type
                _data = response.data

                print(_type)
                print(_data)

                if (_type == MessageType.JSON):
                    print("sending json")
                    u.sendJson(self.conn,_data)

                if (_type == MessageType.PLAIN):
                    u.sendPlain(self.conn,_data)



        _thread.start_new_thread(recvLoop,())
        _thread.start_new_thread(sendLoop,())


sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(( "",9999 ))
sock.listen(1)


while True:
    conn,address = sock.accept()
    # print(address,conn)
    print("connected")
    UserSocket(conn,address[0],address[1])

