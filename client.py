import socket
import enum

import miscutils
from utils import Utils,MessageType,UserData,ServerApi,ClientApi,NotificationApi
from miscutils import Misc
import json
import queue
import _thread




u = Utils()
s = ServerApi
c = ClientApi
n = NotificationApi





class MessageInbox():

    inbox = {}


    def add(self,who,message):
        if who not in self.inbox:
            self.inbox[who] = []
        self.inbox[who].append(message)

    def printFormattedMessages(self,who):

        if len(self.inbox) <= 0 :
            print("There are no messages")
            return


        if who == "all":
            for person in list(self.inbox):
                for message in self.inbox[person]:
                    print(f"[{person}] {message}")

                print("-"*9)
            return



        if who in self.inbox and len(self.inbox) > 0:
            for message in self.inbox[who]:
                print(f"[{who}] {message}")

            return
        else:
            print(f"You have no messages from {who}")




    def getUsersInInbox(self):
        return list( self.inbox.keys() )






class UserClient():

    def __init__(self,conn) -> None:
        self.conn:socket.socket = conn
        self.user_data:UserData = UserData()

        self.responses_data_type_queue_map = {}
        self.message_inbox = MessageInbox()


        self.mainLoops()
        self.register_username()()



    def _request(self,response_type,data_json):
        q = queue.Queue()
        self.responses_data_type_queue_map[response_type] = q

        u.sendJson(self.conn,data_json)


        try:
            response = q.get(timeout=5)
            del self.responses_data_type_queue_map[response_type]
            return response,len(response)
        except:
            return {},0




    # def get_active_users_reponse(self,json_data):
    #     pass
    #
    # def register_response(self,json_data):
    #     pass
    # def get_messages_response(self,json_data):
    #     pass
    # def send_message_response(self,json_data):
    #     pass
    #
    # def receive_message_from_another_client(self,json_data):
    #     pass





    def register_username(self):
        registered = False
        username = ""
        def inner():
            nonlocal registered,username
            while not registered:
                username = input("Username:")

                response,size = self._request(c.REGISTER_RESPONSE,{
                    "type":s.REGISTER,
                    "username":username
                    })

                if (size <=0):
                    print("Error in register_username")
                    return



                success = response['success']
                message = response['message']

                registered = success
                print(f"\n{message} [success {success}]")

            self.user_data.set_username(username)
        return inner

    def view_messages(self):

        users = self.message_inbox.getUsersInInbox()

        if len(users) <= 0 :
            print("You have zero inbox")
            return

        index = 0
        users.append("all")
        for i,user in enumerate(users,0):
            print(f"({i}){user}")
            index = i


        chosen_index = Misc.getInt("Choose:")
        if (chosen_index >= 0 and chosen_index <= index):
            Misc.cleanScreen()
            user = users[chosen_index]
            self.message_inbox.printFormattedMessages(user)
        pass


    # def request_messages(self):
    #
    #     response,size = self._request(c.GET_MESSAGES_RESPONSE,{
    #         "type":s.GET_MESSAGES,
    #         "username":self.user_data.username
    #         })
    #
    #     if (size <=0):
    #         print("Error in request_messages")
    #         return
    #
    #
    #
    #
    #     success = response.get('success')
    #     data = response.get("data")
    #     message = response.get("message")
    #
    #     if not success:
    #         print(message)
    #         return
    #
    #     if success and data == None:
    #         print(message)
    #         return
    #
    #     print(data)


    def get_active_users(self):

        response,size = self._request(c.GET_ACTIVE_USERS_REPONSE,{
            "type":s.GET_ACTIVE_USERS,
            "username":self.user_data.username
            })

        if (size <= 0):
            print("Error in get_active_users")
            return None




        success = response.get("success")
        data = response.get("data")
        message = response.get("message")



        if not success or data == None:
            return [],message

        return data,message


    def send_message(self):


        tupac = self.get_active_users()
        if tupac == None:
            print("send_message error")
            return

        users,message = tupac



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

            response,size = self._request(c.SEND_MESSAGE_RESPONSE,{
                "type":s.SEND_MESSAGE,
                "to":user_chosen,
                "from":self.user_data.username,
                "message":message
                })

            if size <=0:
                print("Error in send_message")
                return



            success = response['success']
            message = response['message']
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
            ("View my messages", self.view_messages),
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

    def receive_message(self,data_json):
        message = data_json['message']
        who = data_json['from']
        self.message_inbox.add(who,message)

    def someone_disconnected(self,data_json):
        pass



    def handle_not_requested_messages(self,data_type,data_json):

        if data_type == n.RECEIVE_MESSAGE:
            self.receive_message(data_json)

        if data_type == n.SOMEONE_DISCONNECTED:
            self.someone_disconnected(data_json)
        pass

    def mainLoops(self):

        def recvLoop():
            while True:
                data = u.readData(self.conn,u.PREFIX_LENGTH)


                type_m,message_size = u.unpack_message_prefix(data)
                print(message_size)
                data = u.readData(self.conn,message_size)

                if (type_m == MessageType.PLAIN):
                    print("its plain")

                if (type_m == MessageType.JSON):
                    data_json = json.loads(data)
                    d_type = data_json["type"]


                    if d_type in self.responses_data_type_queue_map:
                        q:queue.Queue = self.responses_data_type_queue_map[d_type]
                        q.put(data_json)
                        


                    else:
                        self.handle_not_requested_messages(d_type,data_json)




        _thread.start_new_thread(recvLoop,()) 




             






address = ( "",9999 )
conn = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
conn.connect(address)


userclient = UserClient(conn)
while True:
    userclient.menu()


