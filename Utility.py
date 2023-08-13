import os

import pygame
# later: comment document and fix light warnings
###################
import customtkinter as ctk
from tkinter import messagebox
import CTkListbox
from dotenv import load_dotenv
import numpy as np
from PIL import Image, ImageDraw

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
          'close': 'Resources/images/close.png',
          'def_profile': 'Resources/images/default profile picture.jpg',
          'right_arrow': ('Resources/images/right_arrow_white.png', 'Resources/images/right_arrow_white.png'),
          }
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
color_palate_light_1 = [
    '#ECECF4',
    "#685D82",
    '#A8A4BB',
    '#847C9C',
    '#8C84A0',
    '#C7C5D7',
    '#948CA4',
    '#BCBCCC',
    '#8C8CA4',
    '#FCFCFC']
color_palate_light_2 = [
    '#2e8cf3',
    '#ffffff',
    '#f2f5fa',
    '#f8fcff',
    '#f4f8fb'
]
color_palate_dark_1 = [
    '#242131',
    '#2567F6',
    '#BFBEC3',
    '#0C0C11',
    '#585E7A',
    '#77A2F8',
    '#695952',
    '#44455A',
    '#323244',
    '#51545C'
]
color_palate_dark_2 = [
    '#252331',
    '#211f2c',
    '#343145',
    '#252331',
    '#2e79fd'
]
COLOR = {
    'user': {
        'frame-fg': ('#00b3b3', '#1c497d'),
        'frame-border': ('#009999', '#2e7ad1'),
        't-box-fg': ('#00e6e6', '#205592'),
    },
    'other-cl-disp': {
        'frame-fg': ('#60cd32', '#38761d'),
        'frame-border': ('#4da428', '#60cd32'),
        't-box-fg': ('#80d75b', '#439023')
    },
    'other cl': {
        'frame-fg': ("#8C84A0", '#211f2c'),
        'frame-border': ('#685D82', '#4f4a68'),
        't-box-fg': ('#ECECF4', '#343145'),
    },
    'chat': {
        'darkest': ('#847C9C', '#211f2c'),
        'inside 1': ('#BCBCCC', '#252331'),
        'inside 2': ('#C7C5D7', '#343145'),
        'scroll': ('#847C9C', '#343145'),
        'scroll hover': ('#ECECF4', '#4f4a68'),
    },
    'main': {
        'darkest': ('#847C9C', '#211f2c'),
        'inside 1': ('#BCBCCC', '#252331'),
        'border': ('#847C9C', '#343145')
    },
    'font': {
        '1': ('#BCBCCC', '#BCBCCC'),
        '2': ('#343145', '#BCBCCC')
    },
    'button': {
        'normal': ('#4f4a68', '#343145'),
        'hover': ('#343145', '#4f4a68')
    },
    'switch': {
        'progress': ('#847C9C', '#685D82'),
        'fg': ('#BCBCCC', '#252331'),
        'btn normal': ('#4f4a68', '#343145'),
        'btn hover': ('#343145', '#4f4a68')
    }
}


collector = []
console_toggle = False
load_dotenv()


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
        rec_images_path = os.path.join(appdata_path, 'Intelli Chat', 'Resources', 'rec_images')  # Generate corresponding path
        if not os.path.exists(rec_images_path):  # create rec_images sub folder in Resource to store incoming images
            os.mkdir(rec_images_path)
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


class Message:
    @staticmethod
    def display(message, message_type: int):
        """
        :param message_type: 0- informative message,1- warning, 2- error
        :param message: use it at the last as it leds to a loop which can hinder other statements
        :return: None
        """
        match message_type:
            case 0:
                messagebox.showinfo('Intelli Chat', message)
            case 1:
                messagebox.showwarning('Intelli Chat', message)
            case _:  # refers to any case which is not covered
                messagebox.showerror('Intelli Chat', message)


class Images:
    @staticmethod
    def open_as_circle(filename):
        img = Image.open(filename)
        img = img.convert('RGB')
        h, w = img.size

        # creating luminous image
        lum_img = Image.new('L', [h, w], 0)
        draw = ImageDraw.Draw(lum_img)
        draw.pieslice([(0, 0), (h, w)], 0, 360, fill=255)
        img_arr = np.array(img)
        lum_img_arr = np.array(lum_img)

        final_img_arr = np.dstack((img_arr, lum_img_arr))
        return Image.fromarray(final_img_arr)

