#########################
from __future__ import print_function
import builtins as __builtin__
#######################

# todo: comment document and fix light warnings
# packages
import socket
import threading
import customtkinter
from PIL import ImageTk, Image
import datetime
import rsa  # for encrypting more data symmetrical encryption can be done which will be done later
from cryptography.fernet import Fernet
import pickle
import time
import os

import Main
import Utility


####################
def print(*args, **kwargs):
    # Converting anything other than string to string
    l = []
    for i in args:
        try:
            s = str(i)
            l.append(s)
        except Exception:
            l.append(i)
    # Appending the log to list
    Utility.LogCollect.add((' '.join(l), str(**kwargs)))
    return __builtin__.print(*args, **kwargs)
#######################


STORE_PATH = Main.STORE_PATH
# Set up a TCP socket
CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# constants ##
# Set up the server host and port to connect to (note to change the values also in Main.py)
HOST = "localhost"
PORT = 8888
PROFILE_PIC_PATH = 'Resources/profile_pic'  # '/' already used in string path
MEMORY = Utility.MEMORY
IMAGES = Utility.IMAGES
FONT = Utility.FONT
SOUND_EFFECTS = Utility.SOUND_EFFECTS
PIX_LINE = 15
BORDER_PIX = 44
MESSAGE_LINE_LENGTH = 141

# decryption keys
public_key, private_key = rsa.newkeys(1024)


# clamp values
def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


class ChatWindow:
    # User message template
    class User:
        def __init__(self, message, message_area, profile_address):
            self.message = message
            self.message_area = message_area
            self.profile_address = profile_address

        def size_h(self):  # Determines the relative size of message widget
            # Adjustment values
            pix_line = PIX_LINE
            border_pix = BORDER_PIX

            # message
            mes = self.message
            mes = mes.split("\n")

            # finding length
            max_len = max(list(map(len, mes)))
            if max_len >= MESSAGE_LINE_LENGTH:
                mes_len = 1125
            else:
                mes_len = max_len % MESSAGE_LINE_LENGTH
            mes_len = (mes_len * 7) + 10
            mes_len = clamp(mes_len, 50, 915)

            # finding the height
            height = len(mes)
            for i in mes:
                length = len(i) / MESSAGE_LINE_LENGTH
                if length > 1:
                    height += int(length)
            height *= pix_line
            if height == 15:
                return 34, mes_len
            return height + border_pix, mes_len

        def draw(self, current_time=""):
            Utility.SoundManager.play(SOUND_EFFECTS["send"])

            mes_h, mes_y = self.size_h()  # Getting the desired height
            # message holder #size_x - 325
            us_mes = customtkinter.CTkFrame(
                master=self.message_area,
                width=mes_y + 45,
                height=mes_h + 30,
                border_width=1,
            )
            us_mes.pack(anchor="e")

            # display message
            us_txt = customtkinter.CTkTextbox(
                master=us_mes,
                width=mes_y,
                height=mes_h,
                font=FONT["Comic"],
                corner_radius=7,
                border_spacing=1,
            )
            us_txt.insert(customtkinter.END, text=self.message)
            us_txt.place(x=5, y=5)
            us_txt.configure(state=customtkinter.DISABLED)

            # display profile pic
            us_img = customtkinter.CTkImage(Image.open(self.profile_address))
            us_img_l = customtkinter.CTkLabel(
                master=us_mes, image=us_img, width=30, height=30, text=""
            )
            us_img_l.place(x=mes_y + 5, y=8)

            # display current_time stamp
            if current_time == "":
                current_time = str(datetime.datetime.now())
            current_time = current_time.replace('/', ':')
            us_time = customtkinter.CTkLabel(
                master=us_mes,
                text=current_time[:-10],
                width=30,
                height=10,
                font=FONT["t_stamp"],
            )
            us_time.place(x=mes_y - 30, y=mes_h + 12)

    # other client message template
    class Cl:
        def __init__(self, message_area, user_area, clients_widgets):
            self.message_area = message_area
            self.user_area = user_area
            self.clients_widgets = clients_widgets

        @staticmethod  # Determines the relative size of message widget
        def size_h(message):
            # adjustments
            pix_line = PIX_LINE
            border_pix = BORDER_PIX

            # message
            mes = message
            mes = mes.split("\n")

            # finding relative length
            max_len = max(list(map(len, mes)))
            if max_len >= MESSAGE_LINE_LENGTH:
                mes_len = 1125
            else:
                mes_len = max_len % MESSAGE_LINE_LENGTH
            mes_len = (mes_len * 7) + 10
            mes_len = clamp(mes_len, 50, 825)

            # finding relative height
            height = len(mes)
            for i in mes:
                length = len(i) / MESSAGE_LINE_LENGTH
                if length > 1:
                    height += int(length)
            height *= pix_line
            if height == 15:
                return 34, mes_len

            return height + border_pix, mes_len

        @staticmethod
        def un_len_find(username):
            mes_len = len(username)
            mes_len = (mes_len * 9) + 10
            mes_len = clamp(mes_len, 5, 100)
            return mes_len

        # display other clients message
        def draw(self, message, username, profile_address=IMAGES['user'], is_private=False, current_time=""):
            Utility.SoundManager.play(SOUND_EFFECTS["receive"])
            if len(username) > 9:
                username = username[:9] + ".."
            un_len = self.un_len_find(username)
            mes_h, mes_y = self.size_h(message)  # getting relative height

            # message placeholder
            client_mes = customtkinter.CTkFrame(
                master=self.message_area,
                width=mes_y + un_len + 45,
                height=mes_h + 40,
                border_width=1,
            )
            client_mes.pack(anchor="w")

            # other user logo
            if profile_address != IMAGES['user'] and profile_address != IMAGES['bot']:
                profile_address = os.path.join(STORE_PATH, profile_address)
            client_img = customtkinter.CTkImage(Image.open(profile_address))
            client_img_l = customtkinter.CTkLabel(
                master=client_mes, image=client_img, width=30, height=30, text=""
            )
            client_img_l.place(x=5, y=15)

            # username
            client_un = customtkinter.CTkLabel(
                master=client_mes,
                text=username,
                width=30,
                anchor="w",
                height=10,
                font=FONT["Oth_uname"],
            )
            client_un.place(x=38, y=18)

            # timestamp
            if current_time == "":
                current_time = str(datetime.datetime.now())
            current_time = current_time.replace('/', ':')
            client_time = customtkinter.CTkLabel(
                master=client_mes,
                text=current_time[:-10],
                width=30,
                height=10,
                font=FONT["t_stamp"],
            )
            client_time.place(x=mes_y - 30 + un_len, y=mes_h + 22)

            # private
            if is_private:
                client_time = customtkinter.CTkLabel(
                    master=client_mes,
                    text="privately",
                    width=30,
                    height=10,
                    font=FONT["t_stamp"],
                )
                client_time.place(x=mes_y - 5 + un_len, y=2)

            # other user message
            client_txt = customtkinter.CTkTextbox(
                master=client_mes,
                width=mes_y,
                height=mes_h,
                font=FONT["Comic"],
                corner_radius=7,
                border_spacing=1,
            )
            client_txt.insert(customtkinter.END, text=message)
            client_txt.configure(state=customtkinter.DISABLED)
            client_txt.place(x=35 + un_len, y=15)
            return

        # displays which and all user has joined the chatroom
        def draw_oth_uname(self, username, profile_address):
            Utility.SoundManager.play(SOUND_EFFECTS["join"])
            # username template
            us_mes = customtkinter.CTkFrame(
                master=self.user_area, width=200, height=55, border_width=2
            )
            us_mes.pack()
            self.clients_widgets[username] = us_mes.winfo_name()

            # display profile pic
            if profile_address != IMAGES['user'] and profile_address != IMAGES['bot']:
                profile_address = os.path.join(STORE_PATH, profile_address)
            us_img = customtkinter.CTkImage(Image.open(profile_address))
            us_img_l = customtkinter.CTkLabel(
                master=us_mes,
                corner_radius=4,
                width=40,
                height=40,
                text="",
                image=us_img,
            )
            us_img_l.place(x=5, y=7)
            us_name_l = customtkinter.CTkTextbox(
                master=us_mes, width=120, height=40, font=FONT["Oth_uname"]
            )
            us_name_l.insert(customtkinter.END, username)
            us_name_l.place(x=48, y=7)

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
        client_socket.send(b"<END>")
        client_socket.recv(1024).decode()
        print("image sent")

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
        client_socket.send(f"{client_socket}received profile pic".encode())
        print("Picture received and saved to file")

    def __init__(
        self,
        master,
        name,
        size_x,
        size_y,
        client_socket,
        profile_address,
        conversation,
        history,
        password,
    ):
        self.abort = False
        self.password = password
        self.profile_address = profile_address
        self.conversation = conversation  # {'uname':<uname>,'pic':<profile_address>, 'message':<message>, 'private':<private>, 'time':<time_stamp>}
        # Connect to the server
        global CLIENT_SOCKET
        CLIENT_SOCKET = client_socket
        print(CLIENT_SOCKET)

        # username
        self.name = name
        CLIENT_SOCKET.sendall(self.name.encode("utf-8"))
        CLIENT_SOCKET.recv(1024).decode()
        # send profile pic
        self.send_file(CLIENT_SOCKET, profile_address)
        # send public key
        CLIENT_SOCKET.send(public_key.save_pkcs1("PEM"))

        # public key of server for decryption
        self.public_partner = rsa.PublicKey.load_pkcs1(CLIENT_SOCKET.recv(1024))

        # receive previous conversations and store it in conversation_ser
        cons_length = eval(
            rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode("utf-8")
        )
        CLIENT_SOCKET.send(f"{name}received cons_length".encode())
        conversation_ser = []
        for i in range(cons_length):
            cons_len = eval(
                rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode("utf-8")
            )
            CLIENT_SOCKET.send(f"{name}received cons_len".encode())
            rec = ""
            for j in range(cons_len):
                rec += rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode(
                    "utf-8"
                )
                CLIENT_SOCKET.send(f"{name}received client".encode())
            rec = eval(rec)
            print("previous cons", rec)
            conversation_ser.append(rec)

        # Todo: create functionality which will load the latest image of a client (if required, may be done automatically)
        # appending missed conversation which were not saved
        for i in conversation_ser:
            if self.conversation:
                for j in self.conversation:
                    if i['uname'] == j['uname'] and i['message'] == j['message'] and i['time'] == j['time']:
                        break
                else:
                    self.conversation.append(i)
            else:
                self.conversation.append(i)

        CLIENT_SOCKET.send(
            "hi".encode()
        )  # for the server to know that all conversation have been processed

        self.master = master
        self.clients = {}  # <name>: {'pic': <profile_address>}
        self.clients_widgets = {}
        # BG
        bg_img = ImageTk.PhotoImage(Image.open(IMAGES['bg']))
        # noinspection PyTypeChecker
        bg_l1 = customtkinter.CTkLabel(master=master, image=bg_img, text="")
        bg_l1.pack(anchor="center")

        # TODO: make ui grid and make it scalable
        # Main placeholder
        frame = customtkinter.CTkFrame(
            master=bg_l1, width=size_x - 50, height=size_y - 50, corner_radius=15
        )
        frame.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

        # header
        head_frame = customtkinter.CTkFrame(master=master, width=1229, height=40)
        head_frame.place(relx=0.5, rely=0, anchor=customtkinter.N)
        rule_disp = customtkinter.CTkLabel(
            master=head_frame,
            width=30,
            height=30,
            text="Start with @username to message particular user",
            font=FONT["Oth_uname"],
        )
        rule_disp.place(x=400, y=5)
        uname_disp = customtkinter.CTkLabel(
            master=head_frame,
            width=30,
            height=30,
            text="Name: " + str(name),
            font=FONT["Oth_uname"],
        )
        uname_disp.place(x=950, y=5)

        # Back function
        def back():
            bg_l1.destroy()
            self.abort = True
            CLIENT_SOCKET.close()
            main = Main.Main(
                self.name,
                self.conversation,
                self.password,
                self.profile_address,
                history,
            )
            main.run(master)

        # Back button
        back_btn = customtkinter.CTkButton(
            master=head_frame,
            width=30,
            height=30,
            text="Back",
            font=FONT["Comic"],
            command=back,
        )
        back_btn.place(x=25, y=3)

        # input field
        self.input_box = customtkinter.CTkEntry(
            master=frame,
            width=size_x - 130,
            placeholder_text="Type Here",
            font=FONT["Comic"],
        )
        self.input_box.place(x=25, y=size_y - 100)

        # message holder
        self.message_area = customtkinter.CTkScrollableFrame(
            master=frame, width=size_x - 315, height=size_y - 135
        )
        self.message_area.place(x=225, y=15)

        # User holder
        user_head = customtkinter.CTkLabel(
            master=frame,
            width=30,
            height=30,
            font=FONT["Oth_uname"],
            text="USER'S JOINED",
        )
        user_head.place(x=55, y=15)
        self.user_area = customtkinter.CTkScrollableFrame(
            master=frame, width=175, height=size_y - 165
        )
        self.user_area.place(x=25, y=45)

        # load previous conversation
        if self.conversation:
            print("cons received")
            for i in conversation:
                u_name = i['uname']
                if u_name == self.name:
                    user = self.User(
                        i["message"], self.message_area, self.profile_address
                    )
                    user.draw(i["time"])
                else:
                    cl = self.Cl(
                        self.message_area, self.user_area, self.clients_widgets
                    )
                    pic = i["pic"]
                    if pic == "":
                        pic = IMAGES['user']
                    cl.draw(
                        i["message"], u_name, pic, i["private"], i["time"]
                    )

        # sent button
        enter_img = customtkinter.CTkImage(Image.open(IMAGES['send']))
        enter = customtkinter.CTkButton(
            master=frame,
            width=30,
            corner_radius=5,
            command=self.send_message,
            text="",
            image=enter_img,
        )
        enter.place(x=size_x - 100, y=size_y - 100)

        master.bind("<Return>", self.send_message)  # Enter button function

        # display initial message
        cl = self.Cl(self.message_area, self.user_area, self.clients_widgets)
        cl.draw(
            f"Welcome to the Chat room {name}. All messages are end to end encrypted 🔒",
            "Server",
            IMAGES['bot'],
            True,
        )

        # Start a new thread to receive messages from the server
        self.receive_thread = threading.Thread(
            target=self.receive_messages, args=(self.public_partner,)
        )
        self.receive_thread.start()

    def receive_messages(self, public_partner):
        try:
            while not self.abort:
                # Receive messages from the server
                message = rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode(
                    "utf-8"
                )
                ocl = self.Cl(self.message_area, self.user_area, self.clients_widgets)
                if not message:
                    break
                if message.startswith("@server#"):  # Server messages
                    message = message.split("#")[-1]
                    ocl.draw(
                        message,
                        "Server",
                        is_private=True,
                        profile_address=IMAGES['bot'],
                    )
                    self.conversation.append(
                        {
                            'uname': "Server",
                            "pic": IMAGES['bot'],
                            "message": message,
                            "private": True,
                            "time": str(datetime.datetime.now()),
                        }
                    )
                # adding the joined user to GUI
                if message.startswith("@clients#"):  # Client adding or removing messages
                    message = {}
                    CLIENT_SOCKET.send(
                        rsa.encrypt(f"received:@clients#".encode(), public_partner)
                    )
                    length = eval(CLIENT_SOCKET.recv(1024).decode())
                    CLIENT_SOCKET.send(
                        f"{CLIENT_SOCKET}received client length".encode()
                    )
                    for i in range(length):
                        u_name = CLIENT_SOCKET.recv(1024).decode()
                        CLIENT_SOCKET.send(f"{CLIENT_SOCKET}received {u_name}".encode())
                        self.receive_file(CLIENT_SOCKET, f"{os.path.join(STORE_PATH, PROFILE_PIC_PATH)}/{u_name}.png")
                        CLIENT_SOCKET.send(
                            f"{CLIENT_SOCKET}received {u_name} profile pic".encode()
                        )
                        message[u_name] = {"pic": f"{PROFILE_PIC_PATH}/{u_name}.png"}
                    print(message)
                    message.pop(self.name)

                    # finding and adding new clients with their widgets
                    for key in message.keys():
                        if key not in self.clients.keys():
                            self.clients[key] = message[key]
                            # Append the message to the message box in the GUI
                            ocl.draw_oth_uname(key, message[key]["pic"])

                    # finding the clients who left
                    remove_client = []
                    for key in self.clients.keys():
                        if key not in message.keys():
                            remove_client.append(key)

                    # removing the widget of clients who left
                    for key in remove_client:
                        print("removed client", key)
                        for widget in self.user_area.winfo_children():
                            if widget.winfo_name() == self.clients_widgets[key]:
                                widget.destroy()
                                self.clients.pop(key)
                                self.master.update()
                                print("widget destroyed")
                else:  # Handling messages sent by client
                    mes_len = eval(message)
                    print(mes_len)
                    message = ""
                    for i in range(mes_len):
                        message += rsa.decrypt(
                            CLIENT_SOCKET.recv(1024), private_key
                        ).decode("utf-8")
                    # Append the message to the message box in the GUI
                    tokens = message.split(":")
                    recipient = tokens[0]
                    print(tokens[-1])
                    if tokens[-1].startswith("private#"):  # private messages
                        timestamp = tokens[-2]
                        message = "".join(tokens[1:-2])
                        self.conversation.append(
                            {
                                'uname': recipient,
                                "pic": self.clients[recipient]["pic"],
                                "message": message,
                                "private": True,
                                "time": timestamp,
                            }
                        )
                        ocl.draw(
                            message,
                            recipient,
                            is_private=True,
                            profile_address=self.clients[recipient]["pic"],
                        )
                    else:  # public messages
                        timestamp = tokens[-1]
                        message = "".join(tokens[1:-1])
                        ocl.draw(
                            message,
                            recipient,
                            profile_address=self.clients[recipient]["pic"],
                        )
                        self.conversation.append(
                            {
                                'uname': recipient,
                                "pic": self.clients[recipient]["pic"],
                                "message": message,
                                "private": False,
                                "time": timestamp,
                            }
                        )
                    print(message)
        except Exception as e:
            print("error received message", e)

    def send_message(
        self, event=None,
    ):
        print(event)
        # Get the message from the input box
        message = self.input_box.get()
        # display the message to the user
        user = self.User(message, self.message_area, self.profile_address)
        user.draw()
        # add the time stamp
        timestamp = str(datetime.datetime.now())
        timestamp = timestamp.replace(":", "/")
        message += f":{timestamp}"
        # divide the message into chunks
        if message != "":
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
            # append the message into the conversation list
            mes = message.split(":")
            self.conversation.append(
                {
                    'uname': self.name,
                    "pic": self.profile_address,
                    "message": mes[0],
                    "private": False,
                    "time": timestamp,
                }
            )
            print(self.conversation)
            # Send the message to the server
            CLIENT_SOCKET.send(
                rsa.encrypt(f"@{len(mes_chunk)}#".encode("utf-8"), self.public_partner)
            )
            time.sleep(0.05)
            for i in mes_chunk:
                CLIENT_SOCKET.send(rsa.encrypt(i.encode("utf-8"), self.public_partner))
                time.sleep(0.05)
            self.input_box.delete(0, customtkinter.END)

    def close_window(self):
        # Disconnect from the server and exit the application
        self.abort = True
        self.save_files()
        Utility.SoundManager.quit()
        CLIENT_SOCKET.close()
        self.master.destroy()

    def save_files(self):
        # opening the key
        with open(MEMORY['f_key'], "rb") as file_key:
            key = file_key.read()
        fernet = Fernet(key)  # get the generated key

        # encrypting and saving user details
        Main.Main.save_login_cred(self.name, self.password, self.profile_address)

        # save encrypted conversations
        with open(os.path.join(STORE_PATH, MEMORY['cons']), "wb") as encrypted_file:
            encrypted = fernet.encrypt(str(self.conversation).encode())
            encrypted_file.write(encrypted)
            encrypted_file.flush()
            encrypted_file.close()


class Client:
    @staticmethod
    def run(
        root,
        name,
        size_x,
        size_y,
        close_socket,
        profile_address,
        conversation,
        history,
        password,
    ):
        root.geometry(f"{size_x}x{size_y}")  # Set screen size
        root.title("Intelli Chat - Friends")
        chat_window = ChatWindow(
            root,
            name,
            size_x,
            size_y,
            close_socket,
            profile_address,
            conversation,
            history,
            password,
        )
        root.protocol("WM_DELETE_WINDOW", chat_window.close_window)
        root.mainloop()
