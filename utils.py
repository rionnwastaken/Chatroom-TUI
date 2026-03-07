import struct
import enum
import json
import socket

class MessageType(bytes,enum.Enum):
    JSON = b"j"
    PLAIN = b"p"



class UserData():

    def __init__(self) -> None:
        self.username = ""
        pass

    def set_username(self,username):
        self.username = username


class Utils:

    PREFIX_LENGTH = struct.calcsize(">ci")

    

    def pack_message_prefix(self,c:MessageType,message_size):
        data = struct.pack(">ci",c,message_size)
        return data

    def unpack_message_prefix(self,message_bytes):
        data = struct.unpack(">ci",message_bytes)
        t = data[0]
        size = data[1]
        return t,size

    def encode_dict(self,python_json):

        data = json.dumps(python_json).encode("utf8")
        size = len(data)
        prefix_bytes = self.pack_message_prefix(MessageType.JSON,size)
        return data,size,prefix_bytes

    def encode_plain(self,plain_text):
        data = plain_text.encode("utf8")
        size = len(data)
        prefix_bytes = self.pack_message_prefix(MessageType.PLAIN,size)
        return data,size,prefix_bytes

    def sendJson(self,conn,python_json):
        data,size,prefix_size = self.encode_dict(python_json)
        self.sendData(conn,self.PREFIX_LENGTH,prefix_size)
        self.sendData(conn,size,data)

    def sendPlain(self,conn:socket.socket,plain_text:str):
        data,size,prefix_size = self.encode_plain(plain_text)
        self.sendData(conn,self.PREFIX_LENGTH,prefix_size)
        self.sendData(conn,size,data)

    def recvJson(self,conn:socket.socket)-> tuple[dict,bool]:
        prefix_size = self.readData(conn,self.PREFIX_LENGTH)
        message_type,message_size = self.unpack_message_prefix(prefix_size)

        if message_type == MessageType.PLAIN:
            data = self.readData(conn,message_size)
            print("Error, should not receive plain data in recvJson")
            print(prefix_size,message_type,message_size,data)
            return {},True
        data = self.readData(conn,message_size)
        data_json = json.loads(data)
        return data_json,False

    def recvPlain(self,conn:socket.socket)-> bytearray | bytes:
        prefix_size = self.readData(conn,self.PREFIX_LENGTH)
        message_type,message_size = self.unpack_message_prefix(prefix_size)

        if message_type == MessageType.JSON:
            print("Error, should not receive json data in recvPlain")
        data = self.readData(conn,message_size)
        return data


    def readData(self,sock,data_length):

        data_bytes = bytearray(b"")
        consume = data_length

        while (consume > 0):
            recv_bytes = sock.recv(consume)
            recv_bytes_len = len(recv_bytes)

            if recv_bytes_len <=0:
                return b""

            data_bytes.extend(recv_bytes)
            consume = consume - recv_bytes_len

        return data_bytes

    def sendData(self,sock,data_length,data_bytes):
        total_sent = 0
        while (total_sent < data_length):
            data_sent = sock.send(data_bytes)
            total_sent += data_sent

        return total_sent


    def sendSuccess(self,conn,message,success):
        self.sendJson(conn,{
            "message":message,
            "success":success
            })


if __name__ == '__main__':
    a = b'p'

    print(MessageType.JSON)
    if a == MessageType.JSON:
        print("json")

    if a == MessageType.PLAIN:
        print("plain")

