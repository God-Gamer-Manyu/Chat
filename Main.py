#########################
from __future__ import print_function

import builtins as __builtin__
#######################
import os
import shutil
import socket

import customtkinter
from PIL import ImageTk, Image
from cryptography.fernet import Fernet
from customtkinter import filedialog

import Client
import DatabaseHandler
import Utility
import aichat
from Utility import DataStorePath

# todo: comment document and fix light warnings
# TODO: Remove storage files as it reflects while building exe
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


# Configure data storing paths
STORE_PATH = DataStorePath.get_appdata()


# Set up the server host and port to connect to (note to change the values also in client.py)
HOST = 'localhost'
PORT = 8888
SIZE_X, SIZE_Y = 1280, 720
TITLE = 'Chat'
# fonts
FONT = Utility.FONT
IMAGES_FOLD_PATH = 'Resources/images/'
# Images
IMAGES = Utility.IMAGES
# stored files
MEMORY = Utility.MEMORY


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
        # TODO: while building for production you can uncomment this line
        # u_name = os.path.join(STORE_PATH, MEMORY['u_name'])
        # if os.path.isfile(u_name) and username == '':
        #     file = open(u_name, 'rb')
        #     line = file.read()
        #     line = fernet.decrypt(line).decode()
        #     line = line.split(':')
        #     username = line[0]
        #     password = line[1]
        #     profile_address = line[2] + ':' + line[3]  # because path goes like C:\\

        # load conversation from file
        memory = os.path.join(STORE_PATH, MEMORY['cons'])
        if os.path.isfile(memory) and conversation == []:
            file = open(memory, 'rb')
            lines = file.read()
            lines = fernet.decrypt(lines).decode()
            lines = eval(lines)
            for i in lines:
                conversation.append(i)

        self.username = username
        self.password = password
        self.profile_address = profile_address
        self.conversation = conversation
        self.profile_btn = customtkinter.CTkButton(None)

    def run(self, app):
        app.geometry(f'{SIZE_X}x{SIZE_Y}')  # Set screen size
        app.title("Intelli chat")  # Set title
        # set the icon for the window
        app.iconbitmap(IMAGES['logo_ico'])
        app.wm_iconbitmap(IMAGES['logo_ico'])

        # BG
        bg_img = ImageTk.PhotoImage(Image.open(IMAGES['bg']))
        # noinspection PyTypeChecker
        bg_l1 = customtkinter.CTkLabel(master=app, image=bg_img, text='')
        bg_l1.pack()

        #####################################################################
        '''For Debug purpose'''
        con_ctk_toggle = customtkinter.Variable(value=Utility.console_toggle)
        console_checkbox = customtkinter.CTkCheckBox(bg_l1, 25, 25, text='', bg_color='#000000', command=Utility.LogCollect.raise_console, border_color='#000000', variable=con_ctk_toggle)
        console_checkbox.place(relx=.015, rely=.015, anchor=customtkinter.CENTER)
        #################################################################################

        frame = customtkinter.CTkFrame(master=bg_l1, width=300, height=500, corner_radius=15)
        frame.place(relx=.5, rely=.5, anchor=customtkinter.CENTER)
        frame.grid_propagate(False)  # Fix the size

        # logo
        logo_img = ImageTk.PhotoImage(Image.open(IMAGES['logo_png']).resize((270, 270)))
        label_logo = customtkinter.CTkLabel(master=frame, width=100, height=100, text='', image=logo_img, anchor='center')
        label_logo.grid(column=0, row=0, padx=42, pady=(10, 5), sticky='n')

        def ai():
            aicha = aichat.AiChat(self.history)
            bg_l1.destroy()
            aicha.mainloop(app, SIZE_X, SIZE_Y, self.profile_address, self.username, self.conversation, self.password)

        def friends():
            if self.username == '':
                self.login(bg_l1, app)
            else:
                errors = False
                client = Client.Client()
                # Set up a TCP socket
                try:
                    self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client_socket.connect((HOST, PORT))
                except Exception as e:
                    print(e)
                    errors = True
                if not errors:
                    bg_l1.destroy()
                    client.run(app, self.username, SIZE_X, SIZE_Y, self.client_socket, self.profile_address, self.conversation, self.history, self.password)
                else:
                    error_la = customtkinter.CTkLabel(master=frame, width=100, height=30,
                                                      text='Server Error please try again',
                                                      font=FONT['error'])
                    error_la.place(x=50, y=460)

        label = customtkinter.CTkLabel(master=frame, width=100, height=50, text='CHAT WITH', font=FONT['Button'], anchor='center')
        label.grid(column=0, row=1, padx=25, pady=(5, 15), sticky='n')
        frame.grid_propagate(False)  # Fix the size
        # AI button
        ai_btn = customtkinter.CTkButton(master=frame, width=150, height=50, text='AI', font=FONT['Button'], anchor='center', command=ai)
        ai_btn.grid(column=0, row=2, padx=25, pady=15, sticky='n')

        # Friend button
        friend_btn = customtkinter.CTkButton(master=frame, width=150, height=50, text='FRIENDS', font=FONT['Button'], anchor='center', command=friends)
        friend_btn.grid(column=0, row=3, padx=25, pady=15, sticky='n')

        # Todo: create profile frame with animation, etc, which allows user to change profile pic and username
        print(self.profile_address)
        profile_pic = customtkinter.CTkImage(Image.open(self.profile_address))
        self.profile_btn = customtkinter.CTkButton(master=bg_l1, width=40, height=40, text='', font=FONT['Button'], image=profile_pic, corner_radius=5, anchor='center', command=self.profile_get)
        self.profile_btn.place(relx=0.98, rely=0.05, anchor='e')

        app.mainloop()

    def profile_get(self):
        if self.profile_address == IMAGES['user']:
            # show the file dialog and get the selected file(s)
            file_path = filedialog.askopenfilename()
            if file_path:
                # saving the new pic's address in profile address
                self.profile_address = os.path.join(STORE_PATH, IMAGES_FOLD_PATH) + file_path.split('/')[-1]

                abs_target_dir = STORE_PATH + '\\' + IMAGES_FOLD_PATH.replace('/', '\\')

                # check if the file is already in the target directory
                if os.path.dirname(file_path) != abs_target_dir:
                    # move the file to the target directory
                    shutil.copy(file_path, abs_target_dir)
                    print('File moved to:', abs_target_dir)
                else:
                    print('File is already in:', abs_target_dir)

                profile_pic = customtkinter.CTkImage(Image.open(self.profile_address).resize((40, 40)))
                self.profile_btn.configure(image=profile_pic)

    # limit characters
    @staticmethod
    def validate_input(text):
        if len(text) <= DatabaseHandler.CHAR_LEN:
            return True
        else:
            return False

    def login(self, bg_l1, app):
        frame = customtkinter.CTkFrame(master=bg_l1, width=300, height=500, corner_radius=15)
        frame.place(relx=.5, rely=.5, anchor=customtkinter.CENTER)
        frame.grid_propagate(False)  # Fix the size

        # logo
        logo_img = ImageTk.PhotoImage(Image.open(IMAGES['logo_png']).resize((270, 270)))
        label_logo = customtkinter.CTkLabel(master=frame, width=100, height=100, text='', image=logo_img,
                                            anchor='center')
        label_logo.grid(column=0, row=0, padx=42, pady=(10, 0), sticky='n')

        label = customtkinter.CTkLabel(master=frame, width=100, height=50, text='LOGIN', font=FONT['Button'],
                                       anchor='center')
        label.grid(column=0, row=1, sticky='n')

        # display login errors
        login_error = customtkinter.CTkLabel(master=frame, width=100, height=50, text='Kindly enter your ID and password', font=FONT['error'], anchor='center')
        login_error.grid(column=0, row=4, sticky='n')

        # username
        entry = customtkinter.CTkEntry(master=frame, width=280, height=50, placeholder_text='username', font=FONT['In_field'], validate="key", validatecommand=(root.register(self.validate_input), "%P"))
        entry.grid(column=0, row=2, pady=(0, 5), sticky='n')

        # password
        pass_frame = customtkinter.CTkFrame(master=frame, fg_color='transparent')
        pass_frame.grid(column=0, row=3, sticky='n')
        entry_pass = customtkinter.CTkEntry(master=pass_frame, width=230, height=50, placeholder_text='password', font=FONT['In_field'], show='*', validate="key", validatecommand=(root.register(self.validate_input), "%P"))
        entry_pass.grid(column=0, row=0, padx=(0, 12), sticky='w')
        pass_show_img = customtkinter.CTkImage(Image.open(IMAGES['pass show']), size=(25, 25))
        pass_hide_img = customtkinter.CTkImage(Image.open(IMAGES['pass hide']), size=(25, 25))
        disp_pass = False

        def pass_btn():
            pass_show()

        pass_show_btn = customtkinter.CTkButton(master=pass_frame, width=10, height=10, text='', font=FONT['Button'],
                                                anchor='center', command=pass_btn, image=pass_show_img)
        pass_show_btn.grid(column=1, row=0, sticky='e')

        def pass_show():
            nonlocal disp_pass
            if not disp_pass:
                entry_pass.configure(show='')
                pass_show_btn.configure(image=pass_hide_img)
                disp_pass = True
            else:
                disp_pass = False
                entry_pass.configure(show='*')
                pass_show_btn.configure(image=pass_show_img)

        def enter(event=None):
            print(event)
            if entry.get() != '' and entry_pass.get() != '':
                out = DatabaseHandler.DataBaseHandler.check_user(entry.get(), entry_pass.get())
                if out[0]:
                    self.username = entry.get()
                    self.password = entry_pass.get()
                    print('login done', self.username)
                    errors = False
                    client = Client.Client()
                    # Set up a TCP socket
                    try:
                        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.client_socket.connect((HOST, PORT))
                    except Exception as e:
                        print(e)
                        errors = True
                    if not errors:
                        bg_l1.destroy()
                        client.run(app, self.username, SIZE_X, SIZE_Y, self.client_socket, self.profile_address,
                                   self.conversation, self.history, self.password)
                    else:
                        login_error.configure(text='Server Error please try again')
                else:
                    login_error.configure(text=out[1])
                    entry.delete(0, len(entry.get()))
                    entry_pass.delete(0, len(entry_pass.get()))

        def sign_up():
            self.sign_up(bg_l1)

        btn_frame = customtkinter.CTkFrame(master=frame, fg_color='transparent')
        btn_frame.grid(column=0, row=5, pady=(0, 5), sticky='s')
        login_btn = customtkinter.CTkButton(master=btn_frame, width=130, height=50, text='LOGIN', font=FONT['Button'], anchor='center', command=enter)
        login_btn.grid(column=0, row=0, padx=(0, 15), sticky='w')

        sign_up_btn = customtkinter.CTkButton(master=btn_frame, width=130, height=50, text='SIGN UP', font=FONT['Button'], anchor='center', command=sign_up)
        sign_up_btn.grid(column=1, row=0, sticky='e')

        def back():
            frame.destroy()

        back_btn = customtkinter.CTkButton(master=frame, width=10, height=10, text='back', font=FONT['error'], anchor='center', command=back)
        back_btn.place(relx=0.01, rely=0.01)

        entry.bind('<Return>', enter)  # for enter key

    def sign_up(self, bg_l1):
        frame = customtkinter.CTkFrame(master=bg_l1, width=300, height=500, corner_radius=15)
        frame.place(relx=.5, rely=.5, anchor=customtkinter.CENTER)
        frame.grid_propagate(False)  # Fix the size

        # logo
        logo_img = ImageTk.PhotoImage(Image.open(IMAGES['logo_png']).resize((270, 270)))
        label_logo = customtkinter.CTkLabel(master=frame, width=100, height=100, text='', image=logo_img,
                                            anchor='center')
        label_logo.grid(column=0, row=0, padx=42, pady=(10, 0), sticky='n')

        label = customtkinter.CTkLabel(master=frame, width=100, height=50, text='CREATE ACCOUNT', font=FONT['Button'],
                                       anchor='center')
        label.grid(column=0, row=1, sticky='n', pady=(0, 3))

        # display errors
        error = customtkinter.CTkLabel(master=frame, width=100, height=50, text='Kindly enter your credentials', font=FONT['error'], anchor='center')
        error.grid(column=0, row=4, sticky='n')

        # username
        entry = customtkinter.CTkEntry(master=frame, width=280, height=50, placeholder_text='username',
                                       font=FONT['In_field'], validate="key", validatecommand=(root.register(self.validate_input), "%P"))
        entry.grid(column=0, row=2, sticky='n')

        # password
        pass_frame = customtkinter.CTkFrame(master=frame, fg_color='transparent')
        pass_frame.grid(column=0, row=3, sticky='n', pady=(5, 0))
        entry_pass = customtkinter.CTkEntry(master=pass_frame, width=230, height=50, placeholder_text='password',
                                            font=FONT['In_field'], show='*', validate="key", validatecommand=(root.register(self.validate_input), "%P"))
        entry_pass.grid(column=0, row=0, padx=(0, 12), sticky='w')
        pass_show_img = customtkinter.CTkImage(Image.open(IMAGES['pass show']), size=(25, 25))
        pass_hide_img = customtkinter.CTkImage(Image.open(IMAGES['pass hide']), size=(25, 25))
        disp_pass = False

        def add_user():
            if entry.get() != '' and entry_pass.get() != '':
                out = DatabaseHandler.DataBaseHandler.adduser(entry.get(), entry_pass.get())
                if out[0]:
                    frame.destroy()
                else:
                    error.configure(text=out[1])
                    entry.delete(0, len(entry.get()))
                    entry_pass.delete(0, len(entry_pass.get()))

        def pass_btn():
            pass_show()

        def back():
            frame.destroy()

        pass_show_btn = customtkinter.CTkButton(master=pass_frame, width=10, height=10, text='', font=FONT['Button'],
                                                anchor='center', command=pass_btn, image=pass_show_img)
        pass_show_btn.grid(column=1, row=0, sticky='e')
        back_btn = customtkinter.CTkButton(master=frame, width=10, height=10, text='back', font=FONT['error'], anchor='center', command=back)
        back_btn.place(relx=0.01, rely=0.01)

        def pass_show():
            nonlocal disp_pass
            if not disp_pass:
                entry_pass.configure(show='')
                pass_show_btn.configure(image=pass_hide_img)
                disp_pass = True
            else:
                disp_pass = False
                entry_pass.configure(show='*')
                pass_show_btn.configure(image=pass_show_img)

        sign_up_btn = customtkinter.CTkButton(master=frame, width=100, height=50, text='SIGN UP', font=FONT['Button'],
                                              anchor='center', command=add_user)
        sign_up_btn.place(relx=0.5, rely=0.99, anchor='s')
        sign_up_btn.grid(column=0, row=5, sticky='s', pady=5)

    def close_window(self):
        Main.save_login_cred(self.username, self.password, self.profile_address)  # Also Closes The log console, if not closed
        root.destroy()

    @staticmethod
    # Save U-name password and Also Closes The log console, if not closed
    def save_login_cred(username, password, profile_address):
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

        Utility.LogCollect.quit()  # Closing The log console, if not closed


if __name__ == '__main__':
    customtkinter.set_appearance_mode('dark')
    customtkinter.set_default_color_theme('dark-blue')

    root = customtkinter.CTk()  # initiate custom Tkinter
    main = Main('', [], '')
    root.protocol("WM_DELETE_WINDOW", main.close_window)
    main.run(root)
