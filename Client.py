#########################
from __future__ import print_function
import builtins as __builtin__
#######################

# later: comment, document, fix light warnings, optimise code and use tkinter class wherever possible to organise code
# later: For approach to optimise tkinter ui - https://www.youtube.com/watch?v=0y1kYxOp8hE&list=PLpMixYKO4EXflJFPhTvZOVAbs7lBdEBSa&index=11
# packages
import socket
import threading
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image
import datetime
import rsa  # for encrypting
from cryptography.fernet import Fernet
import pickle
import time
import os

import Main
import Utility


####################
def print(*args, **kwargs):
    # Converting anything other than string to string
    values = []
    for i in args:
        try:
            s = str(i)
            values.append(s)
        except Exception:
            values.append(i)
    # Appending the log to list
    Utility.LogCollect.add((' '.join(values), str(**kwargs)))
    return __builtin__.print(*args, **kwargs)
#######################


STORE_PATH = Main.STORE_PATH
# Set up a TCP socket
CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# constants ##
# Set up the server host and port to connect to (note to change the values also in Main.py)
HOST = Utility.HOST
PORT = Utility.PORT
PROFILE_PIC_PATH = 'Resources/profile_pic'  # '/' already used in string path
MEMORY = Utility.MEMORY
IMAGES = Utility.IMAGES
FONT = Utility.FONT
SOUND_EFFECTS = Utility.SOUND_EFFECTS
PIX_LINE = 15
BORDER_PIX = 44
CHAR_SIZE = FONT["Comic"][1]
DPI = Main.DPI
MESSAGE_LINE_LENGTH = 16  # word limit
DPI_ADJ = 2.8  # 2.9 is the adjustment value for tkinter
IMAGES_FOLD_PATH = 'Resources/images/'
REC_IMG_FOLD_PATH = '/Resources/rec_images/'
BG_SIZE = Utility.BG_IMG_SIZE
SIZE_X, SIZE_Y = Main.SIZE_X, Main.SIZE_Y
CAN_TEXT = True

# decryption keys
public_key, private_key = rsa.newkeys(1024)
COLOR = Utility.COLOR

# handles rejoining
IS_REJOINING = False
IS_RECEIVING_MESSAGES = True


# clamp values
def clamp(value, min_value, max_value):
    return max(min(value, max_value), min_value)


class ChatWindow:
    # User message template
    class User(ctk.CTkFrame):
        def __init__(self, message, message_area: ctk.CTkScrollableFrame, profile_address, mainframe=None):
            super().__init__(
                message_area,
                border_width=1,
                fg_color=COLOR['user']['frame-fg'],
                border_color=COLOR['user']['frame-border']
            )
            self.pack(anchor="e")
            self.message = message
            self.profile_address = profile_address
            self.mainframe = mainframe

        def draw(self, current_time=""):
            Utility.SoundManager.play(SOUND_EFFECTS["send"])

            # display message
            mes = ''
            ct = 0
            for i in self.message.split():
                if ct >= MESSAGE_LINE_LENGTH:
                    mes += '\n' + i
                    ct = 0
                else:
                    mes += ' ' + i
                ct += 1

            us_txt = ctk.CTkLabel(
                master=self,
                font=FONT["Comic"],
                anchor='w',
                justify='left',
                text=mes,
                corner_radius=7,
                fg_color=COLOR['user']['t-box-fg'],

            )
            us_txt.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

            # display profile pic
            if self.profile_address == IMAGES['user']:
                us_img = ctk.CTkImage(Image.open(self.profile_address))
            else:
                us_img = ctk.CTkImage(Utility.Images.open_as_circle(self.profile_address))
            us_img_l = ctk.CTkLabel(
                master=self, image=us_img, width=30, height=30, text=""
            )
            us_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky='nw')

            # display current_time stamp
            if current_time == "":
                current_time = str(datetime.datetime.now())
            current_time = current_time.replace('/', ':')
            us_time = ctk.CTkLabel(
                master=self,
                text=current_time[:-10],
                width=30,
                height=10,
                font=FONT["t_stamp"],
            )
            us_time.grid(row=1, column=1, padx=5, pady=(0, 5), sticky='se')

        def draw_pic(self, file_path, current_time=""):
            Utility.SoundManager.play(SOUND_EFFECTS["send"])
            file_path = STORE_PATH + '/' + file_path

            # show the full pic in image viewer
            def show():
                image_holder = ctk.CTkFrame(
                    self.mainframe,
                    width=SIZE_X - 315,
                    height=SIZE_Y - 135,
                    fg_color=COLOR['chat']['inside 1']
                )
                image_holder.grid_propagate(False)
                image_holder.grid(row=1, rowspan=2, column=1, padx=(0, 5), pady=5)
                img = ctk.CTkLabel(image_holder, text='', image=ctk.CTkImage(Image.open(file_path), size=(SIZE_X - 315, SIZE_Y - 135)))
                img.pack(anchor='center', pady=15, padx=15)

                # close the image viewer
                def close():
                    image_holder.destroy()

                close_img = ctk.CTkImage(Image.open(IMAGES['close']), size=(30, 30))
                close_btn = ctk.CTkButton(
                    master=image_holder,
                    text='',
                    command=close,
                    width=35,
                    image=close_img,
                    corner_radius=8,
                    text_color=COLOR['font']['1'],
                    fg_color=COLOR['button']['normal'],
                    hover_color=COLOR['button']['hover']
                )
                close_btn.place(relx=0.95, rely=0.02)

            image = ctk.CTkImage(Image.open(file_path), size=(100, 100))
            # display image as message
            us_pic = ctk.CTkButton(
                master=self,
                image=image,
                corner_radius=2,
                width=100,
                height=100,
                text='',
                command=show,
                fg_color=COLOR['user']['t-box-fg']
            )
            us_pic.grid(row=0, column=1, padx=(0, 5), pady=5, sticky='ne')

            # display profile pic
            if self.profile_address == IMAGES['user']:
                us_img = ctk.CTkImage(Image.open(self.profile_address))
            else:
                us_img = ctk.CTkImage(Utility.Images.open_as_circle(self.profile_address))
            us_img_l = ctk.CTkLabel(
                master=self, image=us_img, width=30, height=30, text=""
            )
            us_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky='nw')

            # display current_time stamp
            if current_time == "":
                current_time = str(datetime.datetime.now())
            current_time = current_time.replace('/', ':')
            us_time = ctk.CTkLabel(
                master=self,
                text=current_time[:-10],
                width=30,
                height=10,
                font=FONT["t_stamp"],
            )
            us_time.grid(row=1, column=1, padx=5, pady=(0, 5), sticky='e')

    # other client message template
    class Cl(ctk.CTkFrame):
        def __init__(self, message_area, mainframe):
            super().__init__(
                message_area,
                border_width=1,
                fg_color=COLOR['other cl']['frame-fg'],
                border_color=COLOR['other cl']['frame-border']
            )
            self.pack(anchor="w")
            self.mainframe = mainframe

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

            # other user logo
            if profile_address != IMAGES['user'] and profile_address != IMAGES['bot']:
                profile_address = os.path.join(STORE_PATH, profile_address)
                client_img = ctk.CTkImage(Utility.Images.open_as_circle(profile_address))
            else:
                client_img = ctk.CTkImage(Image.open(profile_address))
            client_img_l = ctk.CTkLabel(
                master=self, image=client_img, width=30, height=30, text=""
            )
            client_img_l.grid(row=1, column=0, padx=(5, 0), pady=7, sticky="nw")

            # username
            client_un = ctk.CTkLabel(
                master=self,
                text=username,
                width=30,
                anchor="w",
                justify='left',
                height=10,
                font=FONT["Oth_uname"],
            )
            client_un.grid(row=1, column=1, padx=(5, 0), pady=10, sticky='nw')

            # timestamp
            if current_time == "":
                current_time = str(datetime.datetime.now())
            current_time = current_time.replace('/', ':')
            client_time = ctk.CTkLabel(
                master=self,
                text=current_time[:-10],
                width=30,
                height=10,
                font=FONT["t_stamp"],
            )
            client_time.grid(row=2, column=2, padx=5, pady=(0, 5), sticky='ne')

            # private
            if is_private:
                client_time = ctk.CTkLabel(
                    master=self,
                    text="privately",
                    width=30,
                    height=10,
                    font=FONT["t_stamp"],
                )
                client_time.grid(row=0, column=2, pady=(5, 0), padx=5, sticky='ne')

            # other user message
            mes = ''
            ct = 0
            for i in message.split():
                if ct >= MESSAGE_LINE_LENGTH:
                    mes += '\n' + i
                    ct = 0
                else:
                    mes += ' ' + i
                ct += 1

            us_txt = ctk.CTkLabel(
                master=self,
                font=FONT["Comic"],
                anchor='w',
                justify='left',
                text=mes,
                corner_radius=7,
                fg_color=COLOR['other cl']['t-box-fg'],
            )
            us_txt.grid(row=1, column=2, padx=5, pady=5, sticky='nsew')
            return

        def draw_pic(self, username, file_path, profile_address=IMAGES['user'], is_private=False, current_time=""):
            Utility.SoundManager.play(SOUND_EFFECTS["receive"])
            file_path = STORE_PATH + '/' + file_path

            # private
            if is_private:
                client_time = ctk.CTkLabel(
                    master=self,
                    text="privately",
                    width=30,
                    height=10,
                    font=FONT["t_stamp"],
                )
                client_time.grid(row=0, column=2, pady=(5, 0), padx=5, sticky='e')

            # show the full pic in image viewer
            def show():
                image_holder = ctk.CTkFrame(
                    self.mainframe,
                    width=SIZE_X - 315,
                    height=SIZE_Y - 135,
                    fg_color=COLOR['chat']['inside 1']
                )
                image_holder.grid_propagate(False)
                image_holder.grid(row=1, rowspan=2, column=1, padx=(0, 5), pady=5)
                img = ctk.CTkLabel(image_holder, text='', image=ctk.CTkImage(Image.open(file_path), size=(SIZE_X - 315, SIZE_Y - 135)))
                img.pack(anchor='center', pady=15, padx=15)

                # close the image viewer
                def close():
                    image_holder.destroy()

                close_img = ctk.CTkImage(Image.open(IMAGES['close']), size=(30, 30))
                close_btn = ctk.CTkButton(
                    master=image_holder,
                    text='',
                    command=close,
                    width=35,
                    image=close_img,
                    corner_radius=8,
                    text_color=COLOR['font']['1'],
                    fg_color=COLOR['button']['normal'],
                    hover_color=COLOR['button']['hover']
                )
                close_btn.place(relx=0.94, rely=0.02)

            image = ctk.CTkImage(Image.open(file_path), size=(100, 100))
            # display image as message
            client_pic = ctk.CTkButton(
                master=self,
                image=image,
                corner_radius=2,
                width=100,
                height=100,
                text='',
                command=show,
            )
            client_pic.grid(row=1, column=2, padx=(0, 5), pady=(5, 5), sticky='ne')

            # other user logo
            if profile_address != IMAGES['user'] and profile_address != IMAGES['bot']:
                profile_address = os.path.join(STORE_PATH, profile_address)
                client_img = ctk.CTkImage(Utility.Images.open_as_circle(profile_address))
            else:
                client_img = ctk.CTkImage(Image.open(profile_address))
            client_img_l = ctk.CTkLabel(
                master=self, image=client_img, width=30, height=30, text=""
            )
            client_img_l.grid(row=1, column=0, padx=(5, 0), pady=7, sticky='nw')

            # other client's username
            client_un = ctk.CTkLabel(
                master=self,
                text=username,
                width=30,
                anchor="w",
                height=10,
                font=FONT["Oth_uname"],
            )
            client_un.grid(row=1, column=1, padx=(5, 0), pady=10, sticky='nw')

            # display current_time stamp
            if current_time == "":
                current_time = str(datetime.datetime.now())
            current_time.replace('.', ':')
            client_time = ctk.CTkLabel(
                master=self,
                text=current_time[:-10],
                width=30,
                height=10,
                font=FONT["t_stamp"],
            )
            client_time.grid(row=2, column=2, padx=5, pady=(0, 5), sticky='e')

    # class which handles the UI of showing names of other clients in user area
    class OthCLIENT(ctk.CTkFrame):
        def __init__(self, user_area, clients_widgets):
            super().__init__(
                user_area,
                width=200,
                height=55,
                border_width=2,
                fg_color=COLOR['other-cl-disp']['frame-fg'],
                border_color=COLOR['other-cl-disp']['frame-border']
            )
            self.pack()
            self.clients_widgets = clients_widgets

        # displays which and all user has joined the chatroom
        def draw(self, username, profile_address):
            Utility.SoundManager.play(SOUND_EFFECTS["join"])

            self.clients_widgets[username] = self.winfo_name()

            # other user logo
            profile_address = os.path.join(STORE_PATH, profile_address)
            client_img = ctk.CTkImage(Utility.Images.open_as_circle(profile_address))
            client_img_l = ctk.CTkLabel(
                master=self,
                corner_radius=4,
                width=40,
                height=40,
                text="",
                image=client_img,
            )
            client_img_l.grid(row=0, column=0, pady=5, padx=(5, 0), sticky='nw')
            client_name_l = ctk.CTkTextbox(
                master=self, width=120, height=40, font=FONT["Oth_uname"], fg_color=COLOR['other-cl-disp']['t-box-fg']
            )
            client_name_l.insert(ctk.END, username)
            client_name_l.grid(row=0, column=1, pady=5, padx=5, sticky='ne')
            client_name_l.configure(state='disabled')

    @staticmethod
    def send_file(client_socket, file_dir):
        try:
            global CAN_TEXT
            CAN_TEXT = False
            # load the picture from a file
            file_dir = file_dir.replace('/', '\\')
            print(file_dir)
            with open(file_dir, "rb") as f:
                picture = f.read()
            # serialize the picture data using pickle
            data = pickle.dumps(picture)
            # send the picture data
            client_socket.sendall(data)
            client_socket.send(b"<END>")
            time.sleep(0.05)
            print("image sent")
            CAN_TEXT = True
        except Exception as e:
            print('Error send pic:-', e)
            Utility.Message.display('Error occurred while sending picture, please try again', 2)

    @staticmethod
    def receive_file(client_socket, save_file_dir):
        try:
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
            time.sleep(0.05)
            print("Picture received and saved to file")
        except Exception as e:
            print('error receiving pic:-', e)
            Utility.Message.display('Error occurred while receiving picture', 2)

    def setup_client(self, client_socket):
        # Connect to the server
        global CLIENT_SOCKET
        CLIENT_SOCKET = client_socket
        print(CLIENT_SOCKET)

        CLIENT_SOCKET.sendall(self.name.encode("utf-8"))
        CLIENT_SOCKET.recv(1024).decode()
        # send profile pic
        self.send_file(CLIENT_SOCKET, self.profile_address)
        # send public key
        CLIENT_SOCKET.send(public_key.save_pkcs1("PEM"))

        # public key of server for decryption
        self.public_partner = rsa.PublicKey.load_pkcs1(CLIENT_SOCKET.recv(1024))

        # receive previous conversations and store it in conversation_ser
        cons_length = eval(
            rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode("utf-8")
        )
        CLIENT_SOCKET.send(f"{self.name}received cons_length".encode())

        try:
            conversation_ser = []
            for i in range(cons_length):
                cons_len = eval(
                    rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode("utf-8")
                )
                CLIENT_SOCKET.send(f"{self.name}received cons_len".encode())
                rec = ""
                for j in range(cons_len):
                    rec += rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode(
                        "utf-8"
                    )
                    CLIENT_SOCKET.send(f"{self.name}received client".encode())
                rec = eval(rec)
                print("previous cons", rec)
                conversation_ser.append(rec)
        except Exception as e:
            conversation_ser = []
            print('error while receiving prev cons from server:-', e)

        # later: create functionality which will load the latest image of a client (if required, may be done automatically)
        # appending missed conversation which were not saved
        img_not_found = []
        print('to get missing arguments', self.conversation)
        for i in conversation_ser:
            if self.conversation:
                for j in self.conversation:
                    if i['uname'] == j['uname'] and i['message'] == j['message'] and i['time'] == j['time']:
                        break
                else:
                    image = i['image']
                    if image and not os.path.isfile(image) and image not in img_not_found:
                        img_not_found.append(image)
                    self.conversation.append(i)
            else:
                image = i['image']
                if image and not os.path.isfile(image):
                    img_not_found.append(image)
                self.conversation.append(i)

        if len(img_not_found) > 0:
            print(img_not_found)
            CLIENT_SOCKET.send(str(len(img_not_found)).encode())
            time.sleep(0.05)
            for i in img_not_found:
                CLIENT_SOCKET.send(i.encode())
                self.receive_file(CLIENT_SOCKET, STORE_PATH + '/' + i)
                time.sleep(0.05)

        # for the server to know that all conversation have been processed
        CLIENT_SOCKET.send("All conversation received".encode())

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
        self.conversation = conversation  # {'uname':<uname>,'pic':<profile_address>, 'message':<message>, 'private':<private>, 'time':<time_stamp>, 'image':<image address>}
        # username
        self.name = name
        self.master = master
        self.clients = {}  # <name>: {'pic': <profile_address>}
        self.clients_widgets = {}

        # Connect to the server
        self.public_partner: rsa.PublicKey = None  # public_key only for server
        self.setup_client(client_socket)

        # BG
        bg_img = ctk.CTkImage(*map(Image.open, IMAGES['bg']), size=BG_SIZE)
        bg_l1 = ctk.CTkLabel(master=master, image=bg_img, text='')
        bg_l1.pack(fill='both', expand=True)

        # Main placeholder
        self.frame = ctk.CTkFrame(
            master=bg_l1,
            width=size_x - 50,
            height=size_y - 50,
            fg_color=COLOR['chat']['darkest'],
            bg_color=COLOR['chat']['darkest']
        )
        self.frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        # header
        head_frame = ctk.CTkFrame(master=self.frame, width=1190, height=40, fg_color=COLOR['chat']['inside 1'])
        head_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=5)
        head_frame.grid_propagate(False)
        rule_disp = ctk.CTkLabel(
            master=head_frame,
            width=30,
            height=30,
            text="Start with @username to message particular user",
            font=FONT["Oth_uname"],
            text_color=COLOR['font']['2'],
        )
        rule_disp.grid(row=0, column=1, padx=(250, 100), pady=5)
        uname_disp = ctk.CTkLabel(
            master=head_frame,
            width=30,
            height=30,
            text="Name: " + str(name),
            font=FONT["Oth_uname"],
            text_color=COLOR['font']['2'],
        )
        uname_disp.grid(row=0, column=2, sticky='e', padx=(100, 100), pady=5)

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
        back_btn = ctk.CTkButton(
            master=head_frame,
            width=30,
            height=30,
            text="Back",
            font=FONT["Comic"],
            command=back,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        back_btn.grid(row=0, column=0, sticky='w', padx=(5, 100), pady=5)

        # message holder
        self.message_area = ctk.CTkScrollableFrame(
            master=self.frame,
            width=size_x - 315,
            height=size_y - 135,
            fg_color=COLOR['chat']['inside 1'],
            scrollbar_button_color=COLOR['chat']['scroll'],
            scrollbar_button_hover_color=COLOR['chat']['scroll hover']
        )
        self.message_area.grid(row=1, rowspan=2, column=1, padx=(0, 5), pady=5)

        # User holder
        user_head = ctk.CTkLabel(
            master=self.frame,
            width=30,
            height=30,
            font=FONT["Oth_uname"],
            text="USER'S JOINED",
            fg_color='transparent',
            text_color=COLOR['font']['2'],
        )
        user_head.grid(row=1, column=0, padx=(5, 0), pady=(5, 0))
        self.user_area = ctk.CTkScrollableFrame(
            master=self.frame,
            width=175,
            height=size_y - 165,
            fg_color=COLOR['chat']['inside 1'],
            scrollbar_button_color=COLOR['chat']['scroll'],
            scrollbar_button_hover_color=COLOR['chat']['scroll hover']
        )
        self.user_area.grid(row=2, column=0, padx=(5, 0), pady=5)

        # load previous conversation
        if self.conversation:
            print("cons received")
            for i in conversation:
                u_name = i['uname']
                if u_name == self.name:
                    user = self.User(
                        i["message"], self.message_area, self.profile_address, self.frame
                    )
                    image = i["image"]
                    if image:
                        user.draw_pic(image, i['time'])
                    else:
                        user.draw(i["time"])
                else:
                    cl = self.Cl(self.message_area, self.frame)
                    pic = i["pic"]
                    if pic == "":
                        pic = IMAGES['user']
                    image = i['image']
                    if image:
                        cl.draw_pic(u_name, image, pic, current_time=i['time'])
                    else:
                        cl.draw(i["message"], u_name, pic, i["private"], i["time"])

        # bottom frame
        btm_frame = ctk.CTkFrame(self.frame, fg_color=COLOR['chat']['inside 1'])
        btm_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5)
        # input field
        self.input_box = ctk.CTkEntry(
            master=btm_frame,
            width=size_x - 175,
            placeholder_text="Type Here",
            font=FONT["Comic"],
            fg_color=COLOR['chat']['inside 2'],
            border_color=COLOR['chat']['scroll']
        )
        self.input_box.grid(row=0, column=0, padx=5, pady=5)

        # sent button
        enter_img = ctk.CTkImage(Image.open(IMAGES['send']))
        enter = ctk.CTkButton(
            master=btm_frame,
            width=30,
            corner_radius=5,
            command=lambda: self.send_message(),
            text="",
            image=enter_img,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        enter.grid(row=0, column=2, padx=(0, 5), pady=5)

        master.bind("<Return>", lambda event: self.send_message())  # Enter button function

        # image attach button
        attach_img = ctk.CTkImage(Image.open(IMAGES['attachment']), size=(20, 20))
        img_attach_btn = ctk.CTkButton(
            btm_frame,
            width=30,
            image=attach_img,
            corner_radius=5,
            command=self.send_pic,
            text="",
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        img_attach_btn.grid(row=0, column=1, padx=(0, 5), pady=5)

        # display initial message
        cl = self.Cl(self.message_area, self.frame)
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
        global IS_RECEIVING_MESSAGES
        try:
            while not self.abort:
                # Receive messages from the server
                message = rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode("utf-8")
                if not message:
                    break
                if message.startswith("@server#"):  # Server messages
                    message = message.split("#")[-1]
                    ocl = self.Cl(self.message_area, self.frame)
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
                            'image': ''
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
                            ocl = self.OthCLIENT(self.user_area, self.clients_widgets)
                            ocl.draw(key, message[key]['pic'])
                        else:
                            widget: ctk.CTkFrame
                            for widget in self.user_area.winfo_children():
                                if widget.winfo_name() == self.clients_widgets[key]:
                                    widget.configure(fg_color=COLOR['other-cl-disp']['frame-fg'], border_color=COLOR['other-cl-disp']['frame-border'])
                                    for i in widget.winfo_children():
                                        if i.winfo_name() == "!ctktextbox":
                                            i.configure(fg_color=COLOR['other-cl-disp']['t-box-fg'])
                                    self.master.update()

                    # finding the clients who left
                    remove_client = []
                    for key in self.clients.keys():
                        if key not in message.keys():
                            remove_client.append(key)

                    # removing the widget of clients who left
                    for key in remove_client:
                        print("disabled client", key)
                        widget: ctk.CTkFrame
                        for widget in self.user_area.winfo_children():
                            if widget.winfo_name() == self.clients_widgets[key]:
                                widget.configure(fg_color=Utility.COLOR['chat']['darkest'], border_color=Utility.COLOR['chat']['inside 2'])
                                for i in widget.winfo_children():
                                    if i.winfo_name() == '!ctktextbox':
                                        i.configure(fg_color=Utility.COLOR['chat']['inside 1'])
                                self.master.update()
                # handling incoming pictures
                elif message.startswith('@picture#'):
                    sender_name = rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode("utf-8")
                    img_name = rsa.decrypt(CLIENT_SOCKET.recv(1024), private_key).decode("utf-8")
                    self.receive_file(CLIENT_SOCKET, STORE_PATH + REC_IMG_FOLD_PATH + img_name + '.png')
                    ocl = self.Cl(self.message_area, self.frame)
                    ocl.draw_pic(sender_name, REC_IMG_FOLD_PATH + img_name + '.png', self.clients[sender_name]["pic"], False, img_name)
                    self.conversation.append(
                        {
                            'uname': sender_name,
                            "pic": self.clients[sender_name]["pic"],
                            "message": '',
                            "private": False,
                            "time": img_name.replace('.', '/'),
                            'image': REC_IMG_FOLD_PATH + img_name + '.png'
                        }
                    )
                    print(self.conversation)

                    print('images received')
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
                                'image': ''
                            }
                        )
                        ocl = self.Cl(self.message_area, self.frame)
                        ocl.draw(
                            message,
                            recipient,
                            is_private=True,
                            profile_address=self.clients[recipient]["pic"],
                        )
                    else:  # public messages
                        timestamp = tokens[-1]
                        message = "".join(tokens[1:-1])
                        ocl = self.Cl(self.message_area, self.frame)
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
                                'image': ''
                            }
                        )
                    print(message)
        except ConnectionAbortedError as e:
            print("Connection aborted", e)
            IS_RECEIVING_MESSAGES = False
            return
        except ConnectionError as e:
            print("Connection error", e)
            IS_RECEIVING_MESSAGES = False
            return
        except Exception as e:
            print("error received message", type(e), e)
            global IS_REJOINING
            IS_RECEIVING_MESSAGES = False
            if not IS_REJOINING:
                threading.Thread(target=self.rejoin_server).start()
                IS_REJOINING = True
            Utility.Message.display('Unable to connect to server', 2)

    # tries to rejoin the server on connection lost
    def rejoin_server(self):
        global IS_REJOINING, IS_RECEIVING_MESSAGES
        if not self.abort:
            joined = False
            while not joined:
                if self.abort:
                    break
                try:
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    client_socket.connect((HOST, PORT))

                    # send public key to be used only in lobby
                    client_socket.send(public_key.save_pkcs1("PEM"))
                    # public key of lobby of server for decryption
                    lobby_public_partner = rsa.PublicKey.load_pkcs1(client_socket.recv(1024))
                    # sending type of join
                    client_socket.send(
                        rsa.encrypt(
                            'direct'.encode("utf-8"),
                            lobby_public_partner,
                        )
                    )
                    time.sleep(0.05)

                    self.setup_client(client_socket)
                    IS_REJOINING = False
                    joined = True
                    if not IS_RECEIVING_MESSAGES:
                        threading.Thread(target=self.receive_messages, args=(self.public_partner,)).start()
                        IS_RECEIVING_MESSAGES = True
                    break
                except Exception as e:
                    print(e)

    def send_message(self):
        if CAN_TEXT:
            # Get the message from the input box
            message = self.input_box.get()
            message = message.strip()
            if message:
                try:
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
                                'image': ''
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
                        self.input_box.delete(0, ctk.END)
                except Exception as e:
                    global IS_REJOINING
                    if not IS_REJOINING:
                        threading.Thread(target=self.rejoin_server).start()
                        IS_REJOINING = True
                    print('Error sending message', e)
                    Utility.Message.display('Error while sending message, please try again', 2)

    def send_pic(self):
        try:
            file_path = filedialog.askopenfilename()
            if file_path:
                # copying the image and saving it to app's storage for safer use
                img = Image.open(file_path)
                img_name = str(datetime.datetime.now()).replace(':', '.')  # same as current date
                image_path = IMAGES_FOLD_PATH.replace('/', '\\') + img_name + '.png'
                save_path = STORE_PATH + '\\' + image_path
                print(save_path)
                img.save(save_path)
                img.close()

                # send the pic to server
                CLIENT_SOCKET.send(rsa.encrypt('@picture'.encode("utf-8"), self.public_partner))
                time.sleep(0.05)
                CLIENT_SOCKET.send(rsa.encrypt(img_name.encode("utf-8"), self.public_partner))
                time.sleep(0.05)
                self.send_file(CLIENT_SOCKET, save_path)

                self.conversation.append(
                    {
                        'uname': self.name,
                        "pic": self.profile_address,
                        "message": '',
                        "private": False,
                        "time": img_name.replace('.', '/'),
                        'image': image_path
                    }
                )
                print(self.conversation)

                # display the message to the user
                user = self.User('', self.message_area, self.profile_address, self.frame)
                user.draw_pic(image_path)
        except Exception as e:
            print('Error send picture', e)
            Utility.Message.display('Error while sending picture, please try again', 2)

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

        root.title(f"Intelli Chat - {Utility.FRIEND_CHAT_NAME}")
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
