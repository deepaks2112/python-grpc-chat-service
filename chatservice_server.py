import asyncio
import grpc
import logging

from chatservice_pb2_grpc import ChatServiceServicer, add_ChatServiceServicer_to_server
from chatservice_pb2 import (
    ChatMessageRequest,
    ChatMessageResponse,
    ChatMessage,
    ChatClient,
)
from chat_service import ChatService


class Server(ChatServiceServicer):
    chat_service: ChatService = ChatService()

    async def SendMessage(
        self, request: ChatMessageRequest, context: grpc.aio.ServicerContext
    ) -> ChatMessageResponse:
        logging.info(f"SendMessage called with {request=}")
        await self.chat_service.write_message(request)
        return ChatMessageRequest()

    async def ReceiveMessages(
        self, request: ChatClient, context: grpc.aio.ServicerContext
    ) -> ChatMessage:
        logging.info(f"ReceiveMessages called with {request=}")
        while True:
            message_object = await self.chat_service.read_next_message(request)
            if message_object.message == "X":
                logging.info(
                    f"Terminating connection with client_id={message_object.recipient_id}"
                )
                break
            yield message_object


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
