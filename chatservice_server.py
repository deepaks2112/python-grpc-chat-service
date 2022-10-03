import asyncio
import grpc
import logging

from typing import Dict

from chatservice_pb2_grpc import ChatServiceServicer, add_ChatServiceServicer_to_server
from chatservice_pb2 import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatMessage,
    ChatClient,
)
from chat_service import ChatService
from chat_client import ChatClient


class Server(ChatServiceServicer):
    chat_service: ChatService = ChatService()
    clients: Dict[int, ChatClient] = {}

    async def SendMessage(
        self, request: ChatMessageRequest, context: grpc.aio.ServicerContext
    ) -> ChatMessageResponse:
        logging.info(f"SendMessage called with {request=}")
        if request.message == "X":
            logging.info(f"Sender={request.sender_id} going offline.")
            self.__make_client_offline(request.sender_id)
            self.__transform_recipient_id_for_going_offline_message(request)
        await self.chat_service.write_message(request)
        return ChatMessageRequest()

    async def ReceiveMessages(
        self, request: ChatClient, context: grpc.aio.ServicerContext
    ) -> ChatMessage:
        logging.info(f"ReceiveMessages called with {request=}")
        self.__add_to_clients(request.recipient_id)
        while self.__is_client_online(request.recipient_id):
            message_object = await self.chat_service.read_next_message(request)
            if message_object.message == "X":
                break
            yield message_object

    def __add_to_clients(self, client_id):
        if not self.clients.get(client_id):
            self.clients[client_id] = ChatClient(client_id, True)
            return
        self.clients[client_id].online = True

    def __is_client_online(self, client_id):
        if client_id not in self.clients.keys():
            return False
        return self.clients[client_id].is_online()

    def __make_client_offline(self, client_id):
        if client_id in self.clients.keys():
            self.clients[client_id].set_online(False)

    def __transform_recipient_id_for_going_offline_message(self, message_object):
        message_object.recipient_id = message_object.sender_id


async def serve() -> None:
    server = grpc.aio.server()
    add_ChatServiceServicer_to_server(Server(), server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    logging.info(f"Starting server on {listen_addr}")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(serve())
