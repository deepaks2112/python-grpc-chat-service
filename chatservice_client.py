import logging
import threading

import grpc
from chatservice_pb2 import ChatMessageRequest, ChatClient
from chatservice_pb2_grpc import ChatServiceStub


def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = ChatServiceStub(channel)
        client_id = int(input("Enter client id: "))

        read_thread = threading.Thread(
            target=read_handler,
            args=(
                client_id,
                stub,
            ),
        )
        write_thread = threading.Thread(
            target=write_handler,
            args=(
                client_id,
                stub,
            ),
        )

        write_thread.start()
        read_thread.start()

        write_thread.join()
        read_thread.join()

        print("Quitting!")


def read_handler(client_id, stub):
    read_stream = stub.ReceiveMessages(ChatClient(recipient_id=client_id))
    for response in read_stream:
        print(f"\r{response.sender_id}: {response.message}")


def write_handler(client_id, stub):
    while True:
        message = input()
        recipient_id = 2 if client_id == 1 else 1

        stub.SendMessage(
            ChatMessageRequest(
                thread_id=1,
                message=message,
                sender_id=client_id,
                recipient_id=recipient_id,
            )
        )

        if message == "X":
            break


if __name__ == "__main__":
    logging.basicConfig()
    run()
