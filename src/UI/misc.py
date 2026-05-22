from abc import ABC,abstractmethod
import logging
from UI.utils import CustomAdapter,root_logger_name,initialize_root_logger
from UI.properties import Where,Padding,Push,Direction,Status
from typing import Callable, Dict,Literal, Tuple,TypedDict,Protocol,Required,NotRequired, Unpack
from UI.types import ButtonBaseType,Coordinates,LayoutType,ButtonGlobalKeyType,BaseType,ItemAttributesType, ScreenType
from UI.bases import Base



root = logging.getLogger(root_logger_name)
logger = CustomAdapter(root)

class FocusManager:
    """ 
    In charge of giving focus to clients 

    A client can receive focus when self.move(Direction) lands on that client or by specifically setting the focus with self.set_spotlight

    When the current pos exceeds the list boundaries, it requests to the parent focus manager to move

    """


    def __init__(self,class_name,id) -> None:
        self.clients:list["FocusableClient"]  = []
        self.pos = -1 #As clients are added, it increases, so to start with the correct index
        self.spotlight:FocusableClient | None = None


        
        self.fullname = self._get_class_name(class_name,id)
        self.logger = CustomAdapter(root,{"focusmanager":self.fullname})
        self.clients_map:dict[object,FocusableClient] = {}


        self.focus_parent:FocusManager | None = None


        self.should_empty_layout_be_focusable = False

    def _get_class_name(self,class_name,id):
        id = id or ""
        return f"FocusManager({class_name})({id})"

    def __len__(self):
        """
        Length of self.clients
        """     
        return len(self.clients)

    def add_client(self,client:"Base"):
        if client == None:
            raise Exception("Error: Trying to add client that is None")

        if not isinstance(client,FocusableClient):
            raise Exception("Client is not instance of Focusable Client")

        GlobalFocusManager._register(client)
        self.clients.append(client)
        self.spotlight = client
        self.pos = self.pos + 1




        self.logger.info(f"Id is {client.id} | {type(client)} ")
        if client.id == None: return

        if self.clients_map.get(client.id) != None:
            raise Exception(f"Adding client that has the same id ({client.id})as {self.clients_map.get(client.id)}")

        self.clients_map[client.id] = client



    def tell_current_client_lose_focus(self,direction:Direction):
        if self.spotlight != None:
            self.logger.info(f"Tell Current client lose focus {self.spotlight.__class__}")
            self.spotlight.handleLoseFocus(Direction.JUMP)
        pass


    def tell_current_client_gain_focus(self,direction:Direction):
        if self.spotlight != None:

            self.logger.info(f"Tell Current client gain focus {self.spotlight.__class__}")
            self.logger.debug(f"Clients are {self.clients}")
            self.spotlight.handleGetFocus(direction)
        pass
    

    
    
    def set_spotlight(self,client:"FocusableClient") -> Status:
        """
        Set the spotlight by reference
        """ 

        
        if self.spotlight == client:
            self.logger.debug("Skipping setting spotlight cause the requested client is the current spotlight")
            return Status.OK
        
        

        self.tell_current_client_lose_focus(Direction.JUMP)

        if client not in self.clients:
            raise Exception(f"The client with id {client.id} is not registered to {self.fullname}")

        index = self.clients.index(client)
        self.pos = index
        self.spotlight = client

        
        self.tell_current_client_gain_focus(Direction.JUMP)
        
        return Status.OK

    def set_spotlight_byid(self,id:object):

        client = self.clients_map.get(id)

        if client == None:
            self.logger.debug(f"{list( self.clients_map.keys() )}")
            raise Exception(f"Error: Client could not be found with the id of {id}")

        status = self.set_spotlight(client)

        if status == Status.ERR:
            raise Exception(f"The client with id {id} is not registered")


    def set_spotlight_first(self,direction:Direction):
        self.tell_current_client_lose_focus(direction)

        
        if len(self.clients) >= 1:
            if isinstance(self.spotlight,Base):
                self.logger.debug(f"Set spotlight first client {self.spotlight.full_name}")

            self.pos = 0
            self.spotlight = self.clients[0]
            self.tell_current_client_gain_focus(direction)




    def set_spotlight_last(self,direction:Direction):
        if len(self.clients) >= 1:
            if isinstance(self.spotlight,Base):
                self.logger.debug(f"Set spotlight last {self.spotlight.full_name}")

            self.tell_current_client_lose_focus(direction)
            self.pos = len(self.clients) -1
            self.spotlight = self.clients[-1]
            self.tell_current_client_gain_focus(direction)


    def move(self, direction:Direction):
        """
        walked_off_the_edge -> Reached the end of the list


        """

        if self.spotlight != None:
            self.spotlight.handleLoseFocus(direction)

        previous_pos = self.pos
        power = 1 if direction == Direction.FORWARD else -1


        if len(self.clients ) >= 1:
            self.pos = (self.pos + power) % len(self.clients)
        
        self.logger.debug(f"Has spotlight ? f{self.spotlight != None} and pos is {self.pos}")
        
        #Has moved passed the edge
        if direction == Direction.FORWARD and previous_pos > self.pos:
            self.logger.debug(f"Moved passed RIGHT EDGE")
            self.logger.debug(f"Has parent ?{self.focus_parent != None }")

            self.pos = 0
            if self.focus_parent != None:
                self.focus_parent.move(direction)
                return

        if direction == Direction.BACKWARD and previous_pos < self.pos:
            self.logger.debug("FocusManager: LEFT EDGE; We have moved passed the left edge")
            self.pos = len(self.clients) -1
            if self.focus_parent != None:
                self.focus_parent.move(direction)
                return


        #Manager has only 1 client so pos always is the same
        if previous_pos == self.pos:
            self.logger.debug("Previous pos == self.pos which means there is only 1 client in this focusmanager")
            if self.focus_parent != None:
                self.focus_parent.move(direction)
                return
     
    

        if len( self.clients ) >=1:
            self.spotlight = self.clients[self.pos]


        if self.spotlight != None:
            self.spotlight.handleGetFocus(direction)

class FocusableClient(Base):
    """
    Anything that needs focus must inherit this class
    """


    def __init__(self, **kwargs:Unpack[BaseType]): 

        self.on_receive_focus:Callable | None = None
        self.on_lose_focus:Callable | None = None
        self.focus:FocusableClient


        super().__init__(**kwargs)

          
    def handleGetFocus(self,direction:Direction):
        self.defaultHandleGetFocus(direction)
        if self.on_receive_focus != None:
            self.on_receive_focus()



    def handleLoseFocus(self,direction:Direction):
        self.defaultHandleLoseFocus(direction)
        if self.on_lose_focus != None:
            self.on_lose_focus()


    @abstractmethod
    def defaultHandleGetFocus(self,direction:Direction):
        return None

    @abstractmethod
    def defaultHandleLoseFocus(self,direction:Direction):
        return None

    @abstractmethod
    def handleKey(self,c):
        raise NotImplementedError()


class GlobalFocusManager:
    """ """

    # screens_map:dict[object,"Base"] = {}
    all_map:dict[object,"Base"] = {}
    all_clients = []
    logger = CustomAdapter(root,{"class_name":"GlobalFocusManager"})

    @staticmethod
    def _register(client:"Base"):

        if client.id != None:
            GlobalFocusManager.logger.debug(f"Registering {client.full_name}")
            GlobalFocusManager.all_map[client.id] = client
            GlobalFocusManager.all_clients.append(client)

        
    

    @staticmethod
    def set_spotlight_byid(id:object):


        client = GlobalFocusManager.all_map.get(id,None)
        if client == None:
            raise Exception(f"Screen not available")
        GlobalFocusManager.set_spotlight(client)



    @staticmethod
    def get_parent_besides_child(client:"Base") ->list[tuple["Base","Base"]]:
        """
        To be able to easily call the focus manager to set the spotlight tahat needs to get it
        [(John.michael),(michael.michaelson)]
        """
        parents = []

        pointer = client
        while True:


            previous = pointer
            parent = pointer.parent 
            pointer = parent
            if parent == None:
                break
            parents.append(( parent,previous ))


        parents.reverse()
        return parents




    @staticmethod
    def set_spotlight(client:"Base"):

        if not isinstance(client,FocusableClient):
            raise Exception(f"Error: Trying to set spotlight to class that is not instance of FocusableClient\n{client}{client.__class__.mro()}")

        if client in GlobalFocusManager.all_clients:
            parents = GlobalFocusManager.get_parent_besides_child(client)
            # GlobalFocusManager.logger.info(parents)
            # return
            length =  len(parents)
            


            for parent,child in parents:
                if hasattr(parent,"focus"):
                    if isinstance(parent.focus,FocusManager): #type:ignore
                        parent.focus.set_spotlight(child)#type:ignore

            return

        raise Exception("Error: client {client} is not registered in GlobalFocusManager")
