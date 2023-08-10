import os
from tkinter import PhotoImage

import pygame
# later: comment document and fix light warnings
# imp: change 'import customtkinter' to 'from customtkinter import *' and other import statements too
###################
import customtkinter as ctk
import CTkListbox
from PIL import Image

###################

pygame.mixer.init()  # initialising pygame

# Sound effects
SOUND_EFFECTS = {
    "join": "Resources/Sound effects/User join.wav",
    "send": "Resources/Sound effects/send_message.wav",
    "receive": "Resources/Sound effects/receive message.wav",
    'error': 'Resources/Sound effects/error.wav',
}
# stored files
MEMORY = {
    'cons': 'Resources/Memory/cons.dat',
    'f_key': 'Resources/Memory/file_key.key',
    'u_name': 'Resources/Memory/u_name.dat'
}
# Images
IMAGES = {'favicon': 'Resources/images/favicon.ico',
          'logo_ico': 'Resources/images/logo.ico',
          'logo_png': 'Resources/images/Logo.png',
          'pass hide': 'Resources/images/pass_hide.png',
          'pass show': 'Resources/images/pass_show.png',
          'pattern': 'Resources/images/pattern_Home.png',
          'bg': 'Resources/images/Bg_image.png',
          'bot': 'Resources/images/bot.png',
          'send': 'Resources/images/send.png',
          'user': 'Resources/images/user.png',
          'attachment': 'Resources/images/attachment.png',
          'close': 'Resources/images/close.png'}
# Fonts
FONT = {
    "Comic": ("Comic Sans MS", 13),
    "t_stamp": ("Comic Sans MS", 8),
    "Oth_uname": ("Comic Sans MS", 16),
    'Button': ('Comic Sans MS', 25),
    'In_field': ('Comic Sans MS', 20),
    'error': ('Comic Sans MS', 15)
}
BG_IMG_SIZE = (1920, 1080)
COLOR = {
    'user': {
        'frame-fg': '#004d4d',
        'frame-border': '#00b3b3',
        't-box-fg': '#006666',
        't-box-scroll': '#00b3b3',
        't-box-scroll-hover':
            '#008080'},
    'other-cl-disp': {
        'frame-fg': '#38761d',
        'frame-border': '#60cd32',
        't-box-fg': '#439023'
    }}


collector = []
console_toggle = False


# To store files in computer where people can't access directly
class DataStorePath:
    @staticmethod
    def get_appdata():
        appdata_path = os.getenv('APPDATA')
        path = os.path.join(appdata_path, 'Intelli Chat')  # Generate corresponding path
        print('File stored in', path)  # displaying it for developer to know where it is stored
        if not os.path.exists(path):  # create intelli chart main folder in appdata
            os.mkdir(path)
        res_path = os.path.join(appdata_path, 'Intelli Chat', 'Resources')  # Generate corresponding path
        if not os.path.exists(res_path):  # create Resource sub folder in intelli chart
            os.mkdir(res_path)
        p_pic_path = os.path.join(appdata_path, 'Intelli Chat', 'Resources', 'profile_pic')  # Generate corresponding path
        if not os.path.exists(p_pic_path):  # create profile pic sub folder in Resource
            os.mkdir(p_pic_path)
        memory_path = os.path.join(appdata_path, 'Intelli Chat', 'Resources', 'Memory')  # Generate corresponding path
        if not os.path.exists(memory_path):  # create Memory sub folder in Resource
            os.mkdir(memory_path)
        images_path = os.path.join(appdata_path, 'Intelli Chat', 'Resources', 'images')  # Generate corresponding path
        if not os.path.exists(images_path):  # create images sub folder in Resource to store user profile pic
            os.mkdir(images_path)
        return path


class SoundManager:
    @staticmethod
    def play(address):
        sound = pygame.mixer.Sound(address)
        sound.play()

    @staticmethod
    def quit():
        pass


class LogCollect:
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')

    log_disp = None
    app = None

    @staticmethod
    def run():
        images = {'logo ICO': 'Resources/images/logo.ico',
                  'logo png': 'Resources/images/logo.png'}
        LogCollect.app = ctk.CTk()
        LogCollect.app.geometry('1000x600')  # Set screen size
        LogCollect.app.title("Intelli chat")  # Set title
        # set the icon for the window
        LogCollect.app.iconbitmap(images['logo ICO'])
        LogCollect.app.wm_iconbitmap(images['logo ICO'])

        frame = ctk.CTkFrame(LogCollect.app)
        # ctk.CTkScrollableFrame(a)
        frame.pack(padx=5, pady=5, fill='both', expand=True)
        LogCollect.log_disp = CTkListbox.CTkListbox(frame, border_color='#201c1c', fg_color='#000000', text_color='white', hover_color='black', select_color='black')
        LogCollect.log_disp.pack(padx=5, pady=5, fill='both', expand=True)
        for i in collector:
            i = map(str, i)
            i = ' '.join(i)
            if i not in LogCollect.log_disp.get(1):
                LogCollect.log_disp.insert(LogCollect.log_disp.size() - 1, i)
                LogCollect.log_disp.update()
        LogCollect.app.mainloop()

    @staticmethod
    def add(data):
        collector.append(data)
        try:
            if LogCollect.log_disp:
                for i in collector:
                    i = map(str, i)
                    i = ' '.join(i)
                    if i not in LogCollect.log_disp.get(1):
                        LogCollect.log_disp.insert(LogCollect.log_disp.size() - 1, i)
                        LogCollect.log_disp.update()
        except Exception as e:
            print(e)

    @staticmethod
    def quit():
        try:
            LogCollect.app.destroy()
        except Exception as e:
            print(e)

    @staticmethod
    def raise_console():
        global console_toggle
        console_toggle = not console_toggle
        """Brings up the Console Window."""
        if console_toggle:
            # Show console
            LogCollect.run()
        else:
            # Hide console
            LogCollect.quit()


class Gif:
    @staticmethod
    def play(path, canvas, root):
        frame_count = Image.open(path).n_frames
        frames = [PhotoImage(file=path, format='gif -index %i' % i) for i in range(frame_count)]

        def update(ind):
            frame = frames[ind]

            ind += 1
            if ind == frame_count:
                ind = 0
            canvas.create_image(0, 0, image=frame, anchor='nw')
            root.after(50, update, ind)

        root.after(0, update, 0)


class Message:
    message_windows = []

    @staticmethod
    def display(message):
        """
        :param message: use it at the last as it leds to a loop which can hinder other statements
        :return: None
        """
        def close_itself():
            Message.message_windows.remove(mes)
            mes.destroy()

        mes = ctk.CTk()
        mes.protocol("WM_DELETE_WINDOW", close_itself)
        Message.message_windows.append(mes)
        mes.title("Messages")   # Set title
        # set the icon for the window
        mes.iconbitmap(IMAGES['logo_ico'])
        mes.wm_iconbitmap(IMAGES['logo_ico'])

        mes_label = ctk.CTkLabel(mes, text=message, font=FONT['error'])
        mes_label.pack(padx=50, pady=50)

        sound = pygame.mixer.Sound(SOUND_EFFECTS['error'])
        sound.play()
        mes.mainloop()

    @staticmethod
    def close():
        for i in Message.message_windows:
            i.destroy()
