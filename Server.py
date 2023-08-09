import socket
import threading
import rsa
import pickle
import time
# later: comment document and fix light warnings
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# for encryption
public_key, private_key = rsa.newkeys(1024)
PROFILE_PIC_PATH = 'Resources/profile_pic'  # '/' already used in string path


class ChatRoom:
    def __init__(self):
        self.clients = {}
        # for name of clients
        self.client_usernames = {}
        # for public keys of the clients
        self.public_partner = {}
        self.conversation = []

    def add_client(self, client_name, client_socket, profile_pic):
        self.client_usernames[client_name] = {"pic": profile_pic}
        self.clients[client_name] = client_socket

        # send client names to others
        for name, cl_socket in self.clients.items():
            public_partner = self.public_partner[name]
            cl_socket.send(rsa.encrypt(f"@clients#".encode("utf-8"), public_partner))
            # rest is done by handle client function

    def remove_client(self, client_name):
        if client_name in self.clients:
            del self.clients[client_name]
            del self.client_usernames[client_name]
            # send client names to others
            for name, cl_socket in self.clients.items():
                public_partner = self.public_partner[name]
                cl_socket.send(
                    rsa.encrypt(
                        f"@clients#{self.client_usernames}".encode("utf-8"),
                        public_partner,
                    )
                )

    def send_message(
        self, sender_name, message, recipient_name=""
    ):  # send message to a particular client or broadcast
        limit = 100
        mes_len = len(message)
        mes_chunk = []
        for i in range(0, mes_len, limit):
            s = ""
            if i + limit < mes_len:
                for j in range(i, i + limit):
                    s += message[j]
            else:
                for j in range(i, mes_len):
                    s += message[j]
            mes_chunk.append(s)
        if recipient_name != "":
            if recipient_name in self.clients:
                recipient_socket = self.clients[recipient_name]
                public_partner = self.public_partner[recipient_name]
                recipient_socket.send(
                    rsa.encrypt(f"{len(mes_chunk)}".encode("utf-8"), public_partner)
                )
                time.sleep(0.05)
                if len(mes_chunk) == 1:  # single message chunk
                    recipient_socket.send(
                        rsa.encrypt(
                            f"{sender_name}:{mes_chunk[0]}:private#".encode("utf-8"),
                            public_partner,
                        )
                    )
                    time.sleep(0.05)
                else:  # Multi message chunk
                    for i in range(len(mes_chunk)):
                        if i == 0:  # beginning
                            recipient_socket.send(
                                rsa.encrypt(
                                    f"{sender_name}:{mes_chunk[i]}".encode("utf-8"),
                                    public_partner,
                                )
                            )
                            time.sleep(0.05)
                            continue
                        if i == len(mes_chunk) - 1:  # ending
                            recipient_socket.send(
                                rsa.encrypt(
                                    f"{mes_chunk[i]}:private#".encode("utf-8"),
                                    public_partner,
                                )
                            )
                            time.sleep(0.05)
                            break
                        # rest
                        recipient_socket.send(
                            rsa.encrypt(f"{mes_chunk[i]}".encode("utf-8"), public_partner)
                        )
                        time.sleep(0.05)
            else:
                public_partner = self.public_partner[sender_name]
                self.clients[sender_name].send(
                    rsa.encrypt(
                        f"@server#'{recipient_name}' not found".encode("utf-8"),
                        public_partner,
                    )
                )
        else:
            print('Sending publicly')
            for name, cl_socket in self.clients.items():
                if name != sender_name:
                    public_partner = self.public_partner[name]
                    cl_socket.send(
                        rsa.encrypt(f"{len(mes_chunk)}".encode("utf-8"), public_partner)
                    )
                    time.sleep(0.05)
                    for i in range(len(mes_chunk)):
                        if i == 0:
                            cl_socket.send(
                                rsa.encrypt(
                                    f"{sender_name}:{mes_chunk[i]}".encode("utf-8"),
                                    public_partner,
                                )
                            )
                            time.sleep(0.05)
                            continue
                        cl_socket.send(
                            rsa.encrypt(
                                f"{mes_chunk[i]}".encode("utf-8"), public_partner
                            )
                        )
                        time.sleep(0.05)

    @staticmethod
    def receive_file(client_socket, save_file_dir):
        # receive the picture data
        data = b""
        while True:
            packet = client_socket.recv(4096)
            data += packet
            if data[-5:] == b"<END>":
                data = data[:-5]
                break
        # deserialize the picture data using pickle
        picture = pickle.loads(data)
        # save the picture to a file
        with open(save_file_dir, "wb") as f:
            f.write(picture)
        f.close()
        client_socket.send(f"{client_socket} received picture".encode())
        print("Picture received and saved to file")

    @staticmethod
    def send_file(client_socket, file_dir):
        # load the picture from a file
        with open(file_dir, "rb") as f:
            picture = f.read()
        f.close()
        # serialize the picture data using pickle
        data = pickle.dumps(picture)
        # send the picture data
        client_socket.send(data)
        # send end file
        client_socket.send(b"<END>")
        client_socket.recv(1024).decode()
        print("image sent")

    def start_server(self, host, port):
        server_socket.bind((host, port))
        server_socket.listen(1)

        print(f"Chat room started on {host}:{port}")

        while True:
            client_socket, client_address = server_socket.accept()
            # get the name of client
            client_name = client_socket.recv(1024).decode("utf-8")
            # get profile pic
            client_socket.send(f"{client_name} received client name".encode())
            self.receive_file(client_socket, f"server_profile_pic/{client_name}.png")
            profile_pic = f"server_profile_pic/{client_name}.png"

            # getting encryption keys
            self.public_partner[client_name] = rsa.PublicKey.load_pkcs1(
                client_socket.recv(1024)
            )
            client_socket.send(public_key.save_pkcs1("PEM"))

            # send previous conversation
            client_socket.send(
                rsa.encrypt(
                    str(len(self.conversation)).encode("utf-8"),
                    self.public_partner[client_name],
                )
            )
            client_socket.recv(1024).decode("utf-8")
            for i in self.conversation:
                limit = 100
                i = str(i)
                cons_len = len(i)
                cons_chunk = []
                for m in range(0, cons_len, limit):
                    s = ""
                    if m + limit < cons_len:
                        for j in range(m, m + limit):
                            s += i[j]
                    else:
                        for j in range(m, cons_len):
                            s += i[j]
                    cons_chunk.append(s)
                client_socket.send(
                    rsa.encrypt(
                        f"{len(cons_chunk)}".encode("utf-8"),
                        self.public_partner[client_name],
                    )
                )
                client_socket.recv(1024).decode()
                for elem in cons_chunk:
                    client_socket.send(
                        rsa.encrypt(
                            elem.encode("utf-8"), self.public_partner[client_name]
                        )
                    )
                    client_socket.recv(1024).decode("utf-8")
            client_socket.recv(1024).decode("utf-8")

            # add client to client info dictionary
            self.add_client(client_name, client_socket, profile_pic)
            print(f"{client_name} joined the chat room")

            # Start a new thread to handle the client's connection
            threading.Thread(
                target=self.handle_client_connection, args=(client_socket, client_name)
            ).start()

    def handle_client_connection(self, client_socket, client_name):
        while True:
            try:
                message = rsa.decrypt(client_socket.recv(1024), private_key).decode(
                    "utf-8"
                )
                print(message)
                mes_chunk = []
                if message.startswith("@") and message.endswith("#"):
                    mes_len = eval(message[1:-1])
                    for i in range(mes_len):
                        mes = rsa.decrypt(client_socket.recv(1024), private_key).decode(
                            "utf-8"
                        )
                        mes_chunk.append(mes)

                # sending all user info of all clients joined in the server to the joined client
                if message.endswith("@clients#"):
                    client_socket.send(str(len(self.client_usernames)).encode())
                    client_socket.recv(1024).decode()
                    for u_name, val in self.client_usernames.items():
                        client_socket.send(u_name.encode())
                        client_socket.recv(1024).decode()
                        self.send_file(client_socket, val["pic"])
                        client_socket.recv(1024).decode()
                elif not message:
                    raise Exception()
                # for getting the command from client to send a message to specific user
                if mes_chunk:
                    message = ""
                    for i in mes_chunk:
                        message += i
                    if message.startswith("@"):
                        if len(message[1:].split(" ", 1)) == 2:
                            recipient_name, message = message[1:].split(" ", 1)
                            message = message.split(":")
                            timestamp = message[-1]
                            message = "".join(message[:-1])
                            self.conversation.append(
                                {
                                    'uname': client_name,
                                    "pic": f'{PROFILE_PIC_PATH}/{self.client_usernames[client_name]["pic"][19:]}',
                                    "message": message,
                                    "private": True,
                                    "time": timestamp,
                                }
                            )
                            self.send_message(
                                client_name, message + ":" + timestamp, recipient_name
                            )
                        else:
                            public_partner = self.public_partner[client_name]
                            client_socket.send(
                                rsa.encrypt(
                                    "@server#Please enter the message with a space after @username".encode(
                                        "utf-8"
                                    ),
                                    public_partner,
                                )
                            )
                    else:  # broadcasting messages
                        message = message.split(":")
                        timestamp = message[-1]
                        message = "".join(message[:-1])
                        self.conversation.append(
                            {
                                'uname': client_name,
                                "pic": f'{PROFILE_PIC_PATH}/{self.client_usernames[client_name]["pic"][19:]}',
                                "message": message,
                                "private": False,
                                "time": timestamp,
                            }
                        )
                        self.send_message(client_name, message + ":" + timestamp)
                print(self.conversation)
            except Exception as e:  # removing client and ending the process
                self.remove_client(client_name)
                print(f"{client_name} left the chat room ", str(e))
                break


if __name__ == "__main__":
    chat_room = ChatRoom()
    chat_room.start_server("localhost", 8888)
