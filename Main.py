#########################
# testing purposes don't put in documentation
from __future__ import print_function
import builtins as __builtin__
#######################
# Importing modules
import os
import shutil
import socket
import threading
import time
import customtkinter as ctk
import rsa
from PIL import Image
from cryptography.fernet import Fernet
from customtkinter import filedialog
import Client
import Utility
import aichat
from Utility import DataStorePath


# urgent: Remove storage files as it reflects while building exe
##################################
# testing purposes don't put in documentation
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


# Configure data storing paths
STORE_PATH = DataStorePath.get_appdata()


# Set up the server host and port to connect to (note to change the values also in client.py)
HOST = Utility.HOST
PORT = Utility.PORT
# Window size
SIZE_X, SIZE_Y = 1280, 720
TITLE = 'Chat'  # window title
# list of fonts
FONT = Utility.FONT
IMAGES_FOLD_PATH = 'Resources/images/'
# list of Images
IMAGES = Utility.IMAGES
# stored files
MEMORY = Utility.MEMORY
# resize bg to fixed size
BG_SIZE = Utility.BG_IMG_SIZE
DPI = 96
COLOR = Utility.COLOR  # list of colors
login_widget: ctk.CTkFrame = None  # login widget instance

# decryption keys to be used only in lobby
public_key, private_key = rsa.newkeys(1024)


class Main:
    def __init__(self, username, conversation, password, profile_address=IMAGES['user'], history=None):
        # opening the key
        if history is None:
            history = []
        self.history = history
        with open(MEMORY['f_key'], 'rb') as file_key:
            key = file_key.read()
        # using the generated key
        fernet = Fernet(key)
        u_name = os.path.join(STORE_PATH, MEMORY['u_name'])
        # getting the username, password and profile address from the stored file
        if os.path.isfile(u_name) and username == '':
            file = open(u_name, 'rb')
            line = file.read()
            line = fernet.decrypt(line).decode()
            line = line.split(':')
            print(line)
            username = line[0]
            password = line[1]
            if len(line) == 4:
                profile_address = line[2] + ':' + line[3]  # because path goes like C:\\
            else:
                profile_address = line[2]

        # load conversation from file
        memory = os.path.join(STORE_PATH, MEMORY['cons'])
        if os.path.isfile(memory) and conversation == []:
            file = open(memory, 'rb')
            lines = file.read()
            lines = fernet.decrypt(lines).decode()
            lines = eval(lines)
            for i in lines:
                conversation.append(i)

        # general attributes
        self.username = username
        self.password = password
        self.profile_address = profile_address
        self.conversation = conversation
        self.client_socket: socket.socket = None

    def run(self, app):
        """
        Displays the main window
        :param app: the root tkinter
        """
        app.title("Intelli chat")  # Set title
        # set the icon for the window
        app.iconbitmap(IMAGES['logo_ico'])
        app.wm_iconbitmap(IMAGES['logo_ico'])

        # create and display the background
        bg_img = ctk.CTkImage(*map(Image.open, IMAGES['bg']), size=BG_SIZE)
        bg_l1 = ctk.CTkLabel(master=app, image=bg_img, text='')
        bg_l1.pack(fill='both', expand=True)

        # The main frane that holds the menu
        frame = ctk.CTkFrame(
            master=bg_l1,
            width=300,
            height=500,
            fg_color=COLOR['main']['darkest'],
            bg_color=COLOR['main']['darkest'],
        )
        frame.place(relx=.5, rely=.5, anchor=ctk.CENTER)
        frame.grid_propagate(False)  # Fix the size

        #####################################################################
        # testing purposes don't put in documentation
        color = ('#ffffff', '#000000')
        console_checkbox = Utility.LogCollect(bg_l1, 25, 25, color)
        console_checkbox.place(relx=1, rely=1, anchor='se')
        #################################################################################

        # logo
        logo_img = Image.open(IMAGES['logo_png'])
        logo_img = ctk.CTkImage(logo_img, size=(216, 216))
        label_logo = ctk.CTkLabel(master=frame, text='', image=logo_img, anchor='center')
        label_logo.grid(column=0, row=0, padx=42, pady=(10, 5), sticky='n')

        def ai():
            """
            calls the AI window
            """
            aicha = aichat.AiChat(self.history)
            bg_l1.destroy()
            # calling the AI Window
            aicha.mainloop(app, SIZE_X, SIZE_Y, self.profile_address, self.username, self.conversation, self.password)

        def friends():
            """
            handles the login if not logged in or calls the chatting window
            """
            if self.username == '':
                self.login(bg_l1, app)  # ask user to login if not logged in
            else:
                errors = False
                client = Client.Client()
                # Connect to the server and start chatting
                try:
                    # Set up a TCP socket
                    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client_socket.connect((HOST, PORT))

                    # send public key to be used only in lobby
                    self.client_socket.send(public_key.save_pkcs1("PEM"))
                    # public key of lobby of server for decryption
                    lobby_public_partner = rsa.PublicKey.load_pkcs1(self.client_socket.recv(1024))
                    # sending type of join
                    self.client_socket.send(
                        rsa.encrypt(
                            'direct'.encode("utf-8"),
                            lobby_public_partner,
                        )
                    )
                    time.sleep(0.05)
                except Exception as e:
                    # print any errors if occurred
                    print(e)
                    errors = True
                if not errors:
                    # call the chat window
                    bg_l1.destroy()
                    client.run(app, self.username, SIZE_X, SIZE_Y, self.client_socket, self.profile_address, self.conversation, self.history, self.password)
                else:
                    # Display error to the user
                    Utility.Message.display('Server Error please try again', 2)

        label = ctk.CTkLabel(
            master=frame,
            width=100,
            height=50,
            text='CHAT WITH',
            font=FONT['Button'],
            anchor='center',
            text_color=COLOR['font']['2'],
        )
        label.grid(column=0, row=1, padx=25, pady=(5, 15), sticky='n')

        # AI button
        ai_btn = Utility.AnimatedButton(
            master=frame,
            light_path=Utility.ANIM_FOLD_PATH['AI'][0],
            dark_path=Utility.ANIM_FOLD_PATH['AI'][1],
            width=150,
            height=50,
            text=Utility.AI_CHAT_NAME.upper(),
            font=FONT['Button'],
            anchor='center',
            command=ai,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover'],
            source=Utility.AI_IMAGE_SEQUENCE
        )
        ai_btn.grid(column=0, row=2, padx=25, pady=8, sticky='n')

        # Friend button
        friend_btn = Utility.AnimatedButton(
            master=frame,
            light_path=Utility.ANIM_FOLD_PATH['friends'][0],
            dark_path=Utility.ANIM_FOLD_PATH['friends'][1],
            width=150,
            height=50,
            text=Utility.FRIEND_CHAT_NAME.upper(),
            font=FONT['Button'],
            anchor='center',
            command=friends,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover'],
            source=Utility.FRIEND_IMAGE_SEQUENCE
        )
        friend_btn.grid(column=0, row=3, padx=25, pady=8, sticky='n')

        # The class that defines the sliding setting panel
        class SettingPanel(ctk.CTkFrame):
            def __init__(self, parent, start_pos, end_pos, main_class_object, bg_li, master, anim_speed=0.008, corner_radius=0):
                """
                Creates a setting panel in any window
                :param parent: binding tkinter widget
                :param start_pos: start position in relative value
                :param end_pos: end position in relative value
                :param main_class_object: the object that contains profile address and username as attributes (mostly pass self)
                :param anim_speed: speed of animation
                :param bg_li: the background image
                :param master: the root window
                """
                super().__init__(parent, corner_radius=corner_radius, fg_color=COLOR['main']['darkest'], bg_color=COLOR['main']['darkest'])

                # general attributes
                self.start_pos = start_pos
                self.end_pos = end_pos
                self.width = abs(start_pos - end_pos)
                self.anim_speed = anim_speed
                self.bg_li = bg_li
                self.root = master

                # positioning children
                profile_pic_address = IMAGES['def_profile']  # Profile picture display
                if main_class_object.profile_address != IMAGES['user']:
                    profile_pic_address = main_class_object.profile_address
                profile_pic = ctk.CTkImage(Utility.Images.open_as_circle(profile_pic_address), size=(250, 250))
                self.profile_pic_btn = ctk.CTkButton(
                    self,
                    fg_color='transparent',
                    hover_color=COLOR['button']['hover'],
                    image=profile_pic,
                    text='',
                    command=lambda: self.profile_get(main_class_object, (250, 250))
                )
                self.profile_pic_btn.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

                # Username
                self.u_name_label = ctk.CTkLabel(
                    self,
                    font=FONT['In_field'],
                    text_color=COLOR['font']['2'],
                )

                # login button
                self.setting_login_btn = ctk.CTkButton(
                    self,
                    text='LOGIN',
                    font=FONT['Button'],
                    command=lambda: self.login(main_class_object),
                    text_color=COLOR['font']['1'],
                    fg_color=COLOR['button']['normal'],
                    hover_color=COLOR['button']['hover']
                )
                # logout btn
                self.setting_logout_btn = ctk.CTkButton(
                    self,
                    text='LOGOUT',
                    font=FONT['Button'],
                    command=lambda: self.logout(main_class_object),
                    text_color=COLOR['font']['1'],
                    fg_color=COLOR['button']['normal'],
                    hover_color=COLOR['button']['hover']
                )
                self.display_elements_on_cond(main_class_object)

                self.display_elements_on_cond(main_class_object)

                # Switch between dark and light mode
                self.appearance_mode = ctk.IntVar(value=Utility.APPEARANCE_MODE)
                appearance_mode_switch = ctk.CTkSwitch(
                    self,
                    variable=self.appearance_mode,
                    font=FONT['Comic'],
                    text='Dark mode',
                    command=self.change_mode,
                    fg_color=COLOR['switch']['fg'],
                    progress_color=COLOR['switch']['progress'],
                    button_color=COLOR['switch']['btn normal'],
                    button_hover_color=COLOR['switch']['btn hover']
                )
                appearance_mode_switch.place(relx=0.05, rely=.99, anchor='sw', relwidth=1)

                # slide back button
                slide_back_image = ctk.CTkImage(*map(Image.open, IMAGES['right_arrow']), size=(20, 20))
                slide_back_btn = ctk.CTkButton(
                    self,
                    text='',
                    width=10,
                    command=self.start_animate,
                    image=slide_back_image,
                    text_color=COLOR['font']['1'],
                    fg_color=COLOR['button']['normal'],
                    hover_color=COLOR['button']['hover']
                )
                slide_back_btn.place(relx=0.005, rely=0.5, anchor='w')

                # animation
                self.pos = self.start_pos
                self.in_start_pos = True

                # layout
                self.place(relx=self.start_pos, rely=0.005, relwidth=self.width, relheight=.985)

            def login(self, main_class_object):
                """
                Handles login from the settings panel
                :param main_class_object: the object of Main
                """
                # close the panel
                self.start_animate()
                # call the login frame to enable user to login
                main_class_object.login(self.bg_li, self.root, False, self)

            def logout(self, main_class_object):
                """
                Logs out the user
                :param main_class_object: the object of Main
                """
                # setting all credential to null
                main_class_object.profile_address = IMAGES['user']
                main_class_object.username = ''
                main_class_object.password = ''

                # loading the default user picture
                profile_pic = ctk.CTkImage(Utility.Images.open_as_circle(IMAGES['def_profile']), size=(250, 250))
                self.profile_pic_btn.configure(image=profile_pic)
                self.display_elements_on_cond(main_class_object)

                # close the panel
                self.start_animate()

            # display elements based on conditions
            def display_elements_on_cond(self, main_class_object):
                """
                displays login if log in is not done or else display user details
                :param main_class_object: the object which contains profile picture, username and password
                Note: if object doesn't contain login function then make sure that this function is only called after the user is logged in
                """
                if main_class_object.username:  # settings panel when logged in
                    self.setting_login_btn.grid_forget()
                    #  display username
                    self.u_name_label.configure(text=f'Welcome! {main_class_object.username}')
                    self.u_name_label.grid(row=1, column=0, padx=5, pady=5)
                    # display logout button
                    self.setting_logout_btn.grid(row=2, column=0, padx=5, pady=5)
                else:  # settings panel when logged out
                    self.u_name_label.grid_forget()
                    self.setting_logout_btn.grid_forget()
                    # login of not logged in
                    self.setting_login_btn.grid(row=1, column=0, padx=5, pady=5)

            def profile_get(self, main_class_object, img_size: tuple):
                """
                Gets a picture from computer and sets it as the profile picture
                :param main_class_object: object of the main class
                :param img_size: Size of the image
                """
                if main_class_object.username:  # Checks if the user has logged in
                    if main_class_object.profile_address == IMAGES['user']:
                        # show the file dialog and get the selected file(s)
                        file_path = filedialog.askopenfilename()
                        if file_path:
                            # saving the new pic's address in profile address
                            main_class_object.profile_address = os.path.join(STORE_PATH, IMAGES_FOLD_PATH) + file_path.split('/')[-1]

                            abs_target_dir = STORE_PATH + '\\' + IMAGES_FOLD_PATH.replace('/', '\\')

                            # check if the file is already in the target directory
                            if os.path.dirname(file_path) != abs_target_dir:
                                # move the file to the target directory
                                shutil.copy(file_path, abs_target_dir)
                                print('File moved to:', abs_target_dir)
                            else:
                                print('File is already in:', abs_target_dir)

                            img = ctk.CTkImage(Utility.Images.open_as_circle(main_class_object.profile_address), size=img_size)
                            self.profile_pic_btn.configure(image=img)
                else:
                    Utility.Message.display('Please Login', 0)

            def change_mode(self):
                """dark or light mode setting"""
                match self.appearance_mode.get():
                    case 1:
                        ctk.set_appearance_mode('dark')
                        Utility.APPEARANCE_MODE = 1
                    case 0:
                        ctk.set_appearance_mode('light')
                        Utility.APPEARANCE_MODE = 0

            def start_animate(self):
                """Animate the panel forward or backward"""
                if self.in_start_pos:
                    self.animate_forward()
                else:
                    self.animate_backward()

            def animate_forward(self):
                """Forward animation"""
                if self.pos > self.end_pos:  # frame has not reached the destination
                    self.pos -= self.anim_speed
                    self.place(relx=self.pos, rely=0.005, relwidth=self.width, relheight=.985)
                    self.after(10, self.animate_forward)
                else:  # frame has reached the destination
                    self.in_start_pos = False

            def animate_backward(self):
                if self.pos < self.start_pos:  # frame has not reached the destination
                    self.pos += self.anim_speed
                    self.place(relx=self.pos, rely=0.005, relwidth=self.width, relheight=.985)
                    self.after(10, self.animate_backward)
                else:  # frame has reached the destination
                    self.in_start_pos = True

        # settings
        setting_panel = SettingPanel(bg_l1, 1, 0.8, self, bg_l1, app)

        # settings button
        setting_btn = Utility.AnimatedButton(
            master=frame,
            light_path=Utility.ANIM_FOLD_PATH['setting'][0],
            dark_path=Utility.ANIM_FOLD_PATH['setting'][1],
            width=150,
            height=50,
            text='SETTING',
            font=FONT['Button'],
            anchor='center',
            command=setting_panel.start_animate,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover'],
            source=Utility.SETTING_IMAGE_SEQUENCE
        )
        setting_btn.grid(column=0, row=4, padx=25, pady=8, sticky='n')

        # Refresh the window
        app.mainloop()

    @staticmethod
    def validate_input(text):
        """
        Limit the characters to a length specified in the utility
        :param text: the text to limit
        :return: Boolean
        """
        if len(text) <= Utility.U_NAME_CHAR_LEN:
            return True
        else:
            return False

    def login(self, bg_l1, app, join=True, setting_panel=None):
        """
        Performs the login by requesting the server to login, also handles the corresponding UI
        :param bg_l1: BG Image
        :param app: root window
        :param join: if the next task after signing is to join the chat room
        :param setting_panel: the setting panel through which it was called (if any)
        """
        # Removing any other instances of login (making it singleton)
        global login_widget
        if login_widget:
            login_widget.destroy()

        # frame which holds the login ui
        frame = ctk.CTkFrame(
            master=bg_l1,
            width=300,
            height=500,
            fg_color=COLOR['main']['darkest'],
            bg_color=COLOR['main']['darkest']
        )
        frame.place(relx=.5, rely=.5, anchor=ctk.CENTER)
        frame.grid_propagate(False)  # Fix the size

        # assigning the frame as the current instance of login widget
        login_widget = frame

        # logo
        logo_img = Image.open(IMAGES['logo_png'])
        logo_img = ctk.CTkImage(logo_img, size=(216, 216))
        label_logo = ctk.CTkLabel(master=frame, width=100, height=100, text='', image=logo_img, anchor='center')
        label_logo.grid(column=0, row=0, padx=42, pady=(10, 0), sticky='n')

        label = ctk.CTkLabel(
            master=frame,
            width=100,
            height=50,
            text='LOGIN',
            font=FONT['Button'],
            anchor='center',
            text_color=COLOR['font']['2'],
        )
        label.grid(column=0, row=1, sticky='n')

        # display login errors
        login_mes = ctk.CTkLabel(master=frame, width=100, height=50, text='Kindly enter your ID and password', font=FONT['error'], anchor='center')
        login_mes.grid(column=0, row=4, sticky='n')

        # username
        entry = ctk.CTkEntry(
            master=frame,
            width=280,
            height=50,
            placeholder_text='username',
            font=FONT['In_field'],
            validate="key",
            validatecommand=(app.register(self.validate_input), "%P"),
            fg_color=COLOR['main']['inside 1'],
            border_color=COLOR['main']['border']
        )
        entry.grid(column=0, row=2, pady=(0, 5), sticky='n')

        # password
        pass_frame = ctk.CTkFrame(master=frame, fg_color='transparent')
        pass_frame.grid(column=0, row=3, sticky='n')
        entry_pass = ctk.CTkEntry(
            master=pass_frame,
            width=230,
            height=50,
            placeholder_text='password',
            font=FONT['In_field'],
            show='*',
            validate="key",
            validatecommand=(app.register(self.validate_input), "%P"),
            fg_color=COLOR['main']['inside 1'],
            border_color=COLOR['main']['border']
        )
        entry_pass.grid(column=0, row=0, padx=(0, 12), sticky='w')
        pass_show_img = ctk.CTkImage(Image.open(IMAGES['pass show']), size=(25, 25))
        pass_hide_img = ctk.CTkImage(Image.open(IMAGES['pass hide']), size=(25, 25))
        disp_pass = False

        def pass_show():
            """Shows and hides the password"""
            nonlocal disp_pass
            if not disp_pass:  # show password
                entry_pass.configure(show='')
                pass_show_btn.configure(image=pass_hide_img)
                disp_pass = True
            else:  # Hide password
                disp_pass = False
                entry_pass.configure(show='*')
                pass_show_btn.configure(image=pass_show_img)

        # show and hide password button
        pass_show_btn = ctk.CTkButton(
            master=pass_frame,
            width=10,
            height=10,
            text='',
            font=FONT['Button'],
            anchor='center',
            command=pass_show,
            image=pass_show_img,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        pass_show_btn.grid(column=1, row=0, sticky='e')

        def enter():
            """Logs in if given credentials are correct and calls the chat window"""
            if entry.get() != '' and entry_pass.get() != '':  # check if user provided the credentials
                try:  # connect to server and validate credentials
                    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client_socket.connect((HOST, PORT))

                    # send public key to be used only in lobby
                    self.client_socket.send(public_key.save_pkcs1("PEM"))
                    # public key of lobby of server for decryption
                    lobby_public_partner = rsa.PublicKey.load_pkcs1(self.client_socket.recv(1024))
                    # sending type of join to lobby
                    self.client_socket.send(
                        rsa.encrypt(
                            'login'.encode("utf-8"),
                            lobby_public_partner,
                        )
                    )
                    time.sleep(0.05)
                    # sending username
                    self.client_socket.send(
                        rsa.encrypt(
                            entry.get().encode("utf-8"),
                            lobby_public_partner,
                        )
                    )
                    time.sleep(0.05)
                    # sending password
                    self.client_socket.send(
                        rsa.encrypt(
                            entry_pass.get().encode("utf-8"),
                            lobby_public_partner,
                        )
                    )
                    out = eval(rsa.decrypt(self.client_socket.recv(1024), private_key).decode("utf-8"))
                    time.sleep(0.05)
                    # Evaluating the response of server
                    if out[0]:  # Correct credentials
                        self.username = entry.get()
                        self.password = entry_pass.get()
                        print('login done', self.username)
                        if join:  # call the chat window if next task is to join
                            print('hi')
                            # send message to client to start chatroom
                            self.client_socket.send(
                                rsa.encrypt(
                                    'start'.encode("utf-8"),
                                    lobby_public_partner,
                                )
                            )
                            time.sleep(0.05)
                            client = Client.Client()
                            bg_l1.destroy()
                            # call the chat room window
                            client.run(app, self.username, SIZE_X, SIZE_Y, self.client_socket, self.profile_address,
                                       self.conversation, self.history, self.password)

                        else:  # close the settings panel
                            if setting_panel:
                                # send message to client to don't start chatroom
                                self.client_socket.send(
                                    rsa.encrypt(
                                        "don't".encode("utf-8"),
                                        lobby_public_partner,
                                    )
                                )
                                time.sleep(0.05)
                                setting_panel.display_elements_on_cond(self)
                                Utility.Message.display('Logged In Successfully', 0)
                                setting_panel.start_animate()
                                back()
                    else:  # credentials are wrong
                        # refreshing the input UI
                        entry.delete(0, len(entry.get()))
                        entry_pass.delete(0, len(entry_pass.get()))
                        # displaying the message to user
                        Utility.Message.display(out[1], 2)
                except Exception as e:  # displaying the error message to user
                    print(e)
                    Utility.Message.display('Server Error please try again', 2)
            else:  # displaying the message to user to fill in the fields
                Utility.Message.display('Please fill all the fields', 0)

        def sign_up():
            """Calls the sign-up window"""
            self.sign_up(bg_l1, app)

        # login button
        btn_frame = ctk.CTkFrame(master=frame, fg_color='transparent')
        btn_frame.grid(column=0, row=5, pady=(0, 5), sticky='s')
        login_btn = ctk.CTkButton(
            master=btn_frame,
            width=130,
            height=50,
            text='LOGIN',
            font=FONT['Button'],
            anchor='center',
            command=lambda: enter(),
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        login_btn.grid(column=0, row=0, padx=(0, 15), sticky='w')

        # sign-up button
        sign_up_btn = ctk.CTkButton(
            master=btn_frame,
            width=130,
            height=50,
            text='SIGN UP',
            font=FONT['Button'],
            anchor='center',
            command=sign_up,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        sign_up_btn.grid(column=1, row=0, sticky='e')

        def back():
            """Go back to main window"""
            frame.destroy()

        # login back button
        back_btn = ctk.CTkButton(
            master=frame,
            width=10,
            height=10,
            text='back',
            font=FONT['error'],
            anchor='center',
            command=back,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        back_btn.place(relx=0.01, rely=0.01)

        entry.bind('<Return>', lambda event: enter())  # for enter key

    def sign_up(self, bg_l1, app):
        """
        sends request to server to sign up and handles the corresponding UI
        :param bg_l1: BG image
        :param app: root tkinter
        """
        # Frame that holds the sign-up ui
        frame = ctk.CTkFrame(
            master=bg_l1,
            width=300,
            height=500,
            fg_color=COLOR['main']['darkest'],
            bg_color=COLOR['main']['darkest']
        )
        frame.place(relx=.5, rely=.5, anchor=ctk.CENTER)
        frame.grid_propagate(False)  # Fix the size

        # logo
        logo_img = Image.open(IMAGES['logo_png'])
        logo_img = ctk.CTkImage(logo_img, size=(216, 216))
        label_logo = ctk.CTkLabel(master=frame, width=100, height=100, text='', image=logo_img, anchor='center')
        label_logo.grid(column=0, row=0, padx=42, pady=(10, 0), sticky='n')

        label = ctk.CTkLabel(
            master=frame,
            width=100,
            height=50,
            text='CREATE ACCOUNT',
            font=FONT['Button'],
            anchor='center',
            text_color=COLOR['font']['2'],
        )
        label.grid(column=0, row=1, sticky='n', pady=(0, 3))

        # username
        entry = ctk.CTkEntry(
            master=frame,
            width=280,
            height=50,
            placeholder_text='username',
            font=FONT['In_field'],
            validate="key",
            validatecommand=(app.register(self.validate_input), "%P"),
            fg_color=COLOR['main']['inside 1'],
            border_color=COLOR['main']['border']
        )
        entry.grid(column=0, row=2, sticky='n')

        # password
        pass_frame = ctk.CTkFrame(master=frame, fg_color='transparent')
        pass_frame.grid(column=0, row=3, sticky='n', pady=(5, 0))
        entry_pass = ctk.CTkEntry(
            master=pass_frame,
            width=230,
            height=50,
            placeholder_text='password',
            font=FONT['In_field'],
            show='*',
            validate="key",
            validatecommand=(app.register(self.validate_input), "%P"),
            fg_color=COLOR['main']['inside 1'],
            border_color=COLOR['main']['border']
        )
        entry_pass.grid(column=0, row=0, padx=(0, 12), sticky='w')
        pass_show_img = ctk.CTkImage(Image.open(IMAGES['pass show']), size=(25, 25))
        pass_hide_img = ctk.CTkImage(Image.open(IMAGES['pass hide']), size=(25, 25))
        disp_pass = False

        def add_user():
            """Requests the server to add the user to the database"""
            if entry.get() != '' and entry_pass.get() != '' and entry_pass_confirm.get() != '':   # check if fields are filled
                if entry_pass.get() == entry_pass_confirm.get():  # check if the password is confirmed
                    try:  # connect to the server and request it to add the user to the database
                        if self.client_socket:  # close any existing connection
                            self.client_socket.close()
                        # connect to the server
                        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.client_socket.connect((HOST, PORT))

                        # send public key to be used only in lobby
                        self.client_socket.send(public_key.save_pkcs1("PEM"))
                        # public key of lobby of server for decryption
                        lobby_public_partner = rsa.PublicKey.load_pkcs1(self.client_socket.recv(1024))
                        # sending type of join to lobby
                        self.client_socket.send(
                            rsa.encrypt(
                                'sign up'.encode("utf-8"),
                                lobby_public_partner,
                            )
                        )
                        time.sleep(0.05)
                        # sending username
                        self.client_socket.send(
                            rsa.encrypt(
                                entry.get().encode("utf-8"),
                                lobby_public_partner,
                            )
                        )
                        time.sleep(0.05)
                        # sending password
                        self.client_socket.send(
                            rsa.encrypt(
                                entry_pass.get().encode("utf-8"),
                                lobby_public_partner,
                            )
                        )
                        out = eval(rsa.decrypt(self.client_socket.recv(1024), private_key).decode("utf-8"))
                        time.sleep(0.05)
                        print(out)
                        # evaluate the response from server
                        if out[0]:  # user added
                            self.client_socket.close()
                            frame.destroy()
                            Utility.Message.display(out[1], 0)
                        else:  # user not added
                            # refreshing the entry fields
                            entry.delete(0, len(entry.get()))
                            entry_pass.delete(0, len(entry_pass.get()))
                            entry_pass_confirm.delete(0, len(entry_pass_confirm.get()))
                            # displaying the message to the user
                            Utility.Message.display(out[1], 1)
                    except Exception as e:  # displaying the error message to the user
                        print(e)
                        Utility.Message.display("Couldn't connect to server, please try again", 2)
                else:  # Tell user to confirm password
                    Utility.Message.display('Password not matching with confirm password', 1)
            else:  # tell user to fill all the fields
                Utility.Message.display('Please fill all the fields', 0)

        def pass_show():
            """shows or hides password"""
            nonlocal disp_pass
            if not disp_pass:  # shows thw password
                entry_pass.configure(show='')
                pass_show_btn.configure(image=pass_hide_img)
                disp_pass = True
            else:  # Hides the password
                disp_pass = False
                entry_pass.configure(show='*')
                pass_show_btn.configure(image=pass_show_img)

        def back():
            """sign-up back"""
            frame.destroy()

        # password hide show button
        pass_show_btn = ctk.CTkButton(
            master=pass_frame,
            width=10,
            height=10,
            text='',
            font=FONT['Button'],
            anchor='center',
            command=pass_show,
            image=pass_show_img,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        pass_show_btn.grid(column=1, row=0, sticky='e')

        # sign-up back button
        back_btn = ctk.CTkButton(
            master=frame,
            width=10,
            height=10,
            text='back',
            font=FONT['error'],
            anchor='center',
            command=back,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        back_btn.place(relx=0.01, rely=0.01)

        # Confirm Password
        pass_confirm_frame = ctk.CTkFrame(master=frame, fg_color='transparent')
        pass_confirm_frame.grid(column=0, row=4, sticky='n', pady=(5, 0))
        entry_pass_confirm = ctk.CTkEntry(
            master=pass_confirm_frame,
            width=230,
            height=50,
            placeholder_text='confirm password',
            font=FONT['In_field'],
            show='*',
            validate="key",
            validatecommand=(app.register(self.validate_input), "%P"),
            fg_color=COLOR['main']['inside 1'],
            border_color=COLOR['main']['border']
        )
        entry_pass_confirm.grid(column=0, row=0, padx=(0, 12), sticky='w')
        disp_confirm_pass = False

        def pass_confirm_btn():
            """Confirm password hide show"""
            nonlocal disp_confirm_pass
            if not disp_confirm_pass:  # shows the password
                entry_pass_confirm.configure(show='')
                pass_confirm_show_btn.configure(image=pass_hide_img)
                disp_confirm_pass = True
            else:  # hides the password
                disp_confirm_pass = False
                entry_pass_confirm.configure(show='*')
                pass_confirm_show_btn.configure(image=pass_show_img)

        # confirm password hide show button
        pass_confirm_show_btn = ctk.CTkButton(
            master=pass_confirm_frame,
            width=10,
            height=10,
            text='',
            font=FONT['Button'],
            anchor='center',
            command=pass_confirm_btn,
            image=pass_show_img,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        pass_confirm_show_btn.grid(column=1, row=0, sticky='e')

        # Signing up
        sign_up_btn = ctk.CTkButton(
            master=frame,
            width=100,
            height=50,
            text='SIGN UP',
            font=FONT['Button'],
            anchor='center',
            command=add_user,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        sign_up_btn.place(relx=0.5, rely=0.99, anchor='s')
        sign_up_btn.grid(column=0, row=5, sticky='s', pady=5)

    def close_window(self):
        """CLose the main window"""
        # Save the credentials and conversations
        Main.save_login_cred(self.username, self.password, self.profile_address)  # Also Closes The log console, if not closed
        root.destroy()

    @staticmethod
    # Save U-name password and Also Closes The log console, if not closed
    def save_login_cred(username, password, profile_address):
        """
        save the credentials into an encrypted file
        :param username: The username
        :param password: The password
        :param profile_address: The absolute path of the profile address
        """
        # save user details
        # opening the key
        with open(MEMORY['f_key'], 'rb') as file_key:
            key = file_key.read()
        # using the generated key
        fernet = Fernet(key)
        # encrypting the file
        encrypted = fernet.encrypt(f'{username}:{password}:{profile_address}'.encode('utf-8'))
        # opening the file in write mode and writing the encrypted data
        with open(os.path.join(STORE_PATH, MEMORY['u_name']), 'wb') as encrypted_file:
            encrypted_file.write(encrypted)

        Utility.LogCollect.close()  # Closing The log console, if not closed


# main function
if __name__ == '__main__':
    # set appearances
    ctk.set_appearance_mode('dark') if Utility.APPEARANCE_MODE == 1 else ctk.set_appearance_mode('light')
    ctk.set_default_color_theme('dark-blue')

    root = ctk.CTk()  # initiate custom Tkinter
    root.title('Intelli chat')
    # set the icon for the window
    root.iconbitmap(IMAGES['logo_ico'])
    root.wm_iconbitmap(IMAGES['logo_ico'])

    # getting screen width and height of display
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight() - 290
    # setting tkinter window size
    root.geometry("%dx%d+0+0" % (width, height))

    def on_video_end():
        """open the main window after the intro scene"""
        intro.destroy()
        main.run(root)

    # Intro video
    intro = Utility.Video(root, 'Resources/Intro.mp4', on_video_end, scaled=True, keep_aspect=False, consistant_frame_rate=True)
    intro.place(relx=0, rely=0, relwidth=1, relheight=1)
    # set tkinter window minimum size
    root.minsize(1200, 712)  # the values are adjusted (when tkinter converts it becomes [1500, 890])

    main = Main('', [], '')
    root.protocol("WM_DELETE_WINDOW", main.close_window)  # map custom close function to window

    def resizing_mid():
        """resize the window to the middles of the screen on pressing escape button"""
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = int((screen_width/2) - (SIZE_X/2))
        y_coordinate = int((screen_height/2) - (SIZE_Y/2))
        root.geometry(f'{SIZE_X}x{SIZE_Y}+{x_coordinate}+{y_coordinate}')  # Set screen size

    root.bind('<Escape>', lambda event: resizing_mid())

    def get_btn_images():
        """Loading the image sequence for the animated buttons simultaneously"""
        Utility.AI_IMAGE_SEQUENCE = Utility.AnimatedButton.import_folders(Utility.ANIM_FOLD_PATH['AI'][0], Utility.ANIM_FOLD_PATH['AI'][1], (30, 30))
        Utility.FRIEND_IMAGE_SEQUENCE = Utility.AnimatedButton.import_folders(Utility.ANIM_FOLD_PATH['friends'][0], Utility.ANIM_FOLD_PATH['friends'][1], (30, 30))
        Utility.SETTING_IMAGE_SEQUENCE = Utility.AnimatedButton.import_folders(Utility.ANIM_FOLD_PATH['setting'][0], Utility.ANIM_FOLD_PATH['setting'][1], (30, 30))

    threading.Thread(target=get_btn_images).start()
    root.mainloop()
