# python-grpc-chat-service
A simple chat service to illustrate a web-sockets like setup using gRPC (underlying HTTP/2)

# Details
A gRPC server is created to which multiple clients can connect. The server is an async one (using async queue). The client uses two threads, one each for sending messages and receiving messages. The receiving messages is achieved by establishing a server-streaming procedure to establish a long-lived connection. The sending messages is achieved using individual requests.

![Architecture](https://i.imgur.com/mHvZgYT.png)
