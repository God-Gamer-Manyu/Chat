#########################
# testing purposes don't put in documentation
from __future__ import print_function
import builtins as __builtin__
#######################
# Importing modules
import os
import threading
from typing import Callable
from playsound import playsound
import customtkinter as ctk
from tkinter import messagebox
import CTkListbox
from dotenv import load_dotenv
import numpy as np
from PIL import Image, ImageDraw
from tkVideoPlayer import TkinterVideo
import pyaudio


def is_sound_device_present():
    try:
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        return device_count > 0
    except Exception:
        return False


# Network connection
HOST = "localhost"
PORT = 8888

# Sound effects
SOUND_EFFECTS = {
    "join": "Resources/Sound effects/User join.wav",
    "send": "Resources/Sound effects/send_message.wav",
    "receive": "Resources/Sound effects/receive message.wav",
    'error': 'Resources/Sound effects/error.wav',
    'disconnect': 'Resources/Sound effects/disconnect.wav'
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
          'bg': ('Resources/images/light bg.jpg', 'Resources/images/bg_dark.png'),
          'bot': 'Resources/images/bot.png',
          'send': 'Resources/images/send.png',
          'user': 'Resources/images/user.png',
          'attachment': 'Resources/images/attachment.png',
          'close': 'Resources/images/close.png',
          'def_profile': 'Resources/images/default profile picture.jpg',
          'right_arrow': ('Resources/images/right_arrow_white.png', 'Resources/images/right_arrow_white.png'),
          }
ANIM_FOLD_PATH = {
    'AI': ('Resources/images/bot dark', 'Resources/images/bot dark'),  # (<light>, <dark>)
    'friends': ('Resources/images/friends dark', 'Resources/images/friends dark'),  # (<light>, <dark>)
    'setting': ('Resources/images/settings dark', 'Resources/images/settings dark'),
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
BG_VID_PATH = ('Resources/light bg.mp4', 'Resources/dark bg.mp4')  # taking too long to load so not in use
BG_IMG_SIZE = (1920, 1080)  # size of the background
APPEARANCE_MODE = 1  # 0- light, 1- dark
AI_CHAT_NAME = 'Ask me'  # Name for Ai chatting
FRIEND_CHAT_NAME = 'Friend Zone'  # Name for chatting with friends

# Colors used in UI elements
COLOR = {
    'user': {
        'frame-fg': ('#B5D7F3', '#1c497d'),
        'frame-border': ('#009999', '#2e7ad1'),
        't-box-fg': ('#BEE2FF', '#205592'),
    },
    'other-cl-disp': {
        'frame-fg': ('#B1CD9E', '#38761d'),
        'frame-border': ('#4da428', '#60cd32'),
        't-box-fg': ('#DCFFC4', '#439023')
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

AI_IMAGE_SEQUENCE = None  # image sequence
FRIEND_IMAGE_SEQUENCE = None  # image sequence
SETTING_IMAGE_SEQUENCE = None  # image sequence

U_NAME_CHAR_LEN = 50
MESSAGE_LINE_LENGTH_CHAT = 16  # word limit
MESSAGE_LINE_LENGTH_AI = 16  # word limit


load_dotenv()  # loading AI API Key


##################################
# testing purposes don't put in documentation
collector = []
console_toggle = False


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
    LogCollect.add((' '.join(values), str(**kwargs)))
    return __builtin__.print(*args, **kwargs)
#######################


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
    def play(address: str):
        """
        Play a sound
        :param address: Relative path to the sound
        """
        def play_sound(sound_path):
            try:
                playsound(sound_path)
            except Exception:
                return
        if is_sound_device_present():  # play sound
            threading.Thread(target=play_sound, args=(address,), daemon=True).start()

    @staticmethod
    def quit():
        pass


##################################################
# For Debugging Purpose don't put in documentation
class LogCollect(ctk.CTkCheckBox):
    def __init__(self, master, width, height, color, text='', **kwargs):
        super().__init__(
            master=master,
            width=width,
            height=height,
            text=text,
            command=lambda: LogCollect.raise_console(),
            bg_color=color,
            border_color=color,
            **kwargs
        )
        self.set_var()

    def set_var(self):
        LogCollect.show = ctk.BooleanVar(value=console_toggle)
        self.configure(variable=LogCollect.show)

    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')

    log_disp = None
    app = None
    show: ctk.BooleanVar = None

    @staticmethod
    def run():
        images = {'logo ICO': 'Resources/images/logo.ico',
                  'logo png': 'Resources/images/logo.png'}
        LogCollect.app = ctk.CTk()
        LogCollect.app.geometry('1000x600')  # Set screen size
        LogCollect.app.title("Intelli chat")  # Set title
        LogCollect.app.protocol('WM_DELETE_WINDOW', LogCollect.raise_console)
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
            if LogCollect.app:
                for i in collector:
                    i = map(str, i)
                    i = ' '.join(i)
                    if i not in LogCollect.log_disp.get(1):
                        LogCollect.log_disp.insert(LogCollect.log_disp.size() - 1, i)
                        LogCollect.log_disp.update()
        except Exception as e:
            print(e)

    @staticmethod
    def close():
        try:
            if LogCollect.app:
                LogCollect.app.destroy()
                LogCollect.app = None
        except Exception as e:
            print(e)

    @staticmethod
    def raise_console():
        global console_toggle
        console_toggle = not console_toggle
        """Brings up the Console Window."""
        if console_toggle:
            # Show console
            if LogCollect.show:
                LogCollect.show.set(True)
            LogCollect.run()
        else:
            # Hide console
            if LogCollect.show:
                LogCollect.show.set(False)
            LogCollect.close()
############################################################################


class Message:
    @staticmethod
    def display(message: str, message_type: int):
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
    def open_as_circle(filename: str):
        """
        Open Image in circular format
        :param filename: relative path to the image
        :return: an Image
        """
        img = Image.open(filename)
        img = img.convert('RGB')  # remove alpha
        h, w = img.size

        # creating luminous image
        lum_img = Image.new('L', [h, w], 0)
        draw = ImageDraw.Draw(lum_img)
        draw.pieslice([(0, 0), (h, w)], 0, 360, fill=255)
        lum_img_arr = np.array(lum_img)

        # converting it to a numpy array
        img_arr = np.array(img)
        img.close()

        # Merging image to the mask already created
        final_img_arr = np.dstack((img_arr, lum_img_arr))
        return Image.fromarray(final_img_arr)


class AnimatedButton(ctk.CTkButton):
    def __init__(
            self,
            master: ctk.CTkFrame,
            light_path: str,
            dark_path: str,
            pic_size=(30, 30),
            anim_speed=20,
            source=None,
            **kwargs
    ):
        # animation setup
        if not source:
            self.frames = AnimatedButton.import_folders(light_path, dark_path, pic_size)
        else:
            self.frames = source
        self.frame_index = 0
        self.animation_length = len(self.frames) - 1
        self.animation_status = 'start'

        super().__init__(
            master,
            image=self.frames[self.frame_index],
            **kwargs
        )
        self.animate(anim_speed)

    @staticmethod
    def import_folders(light: str, dark: str, size: tuple):
        """
        Import light and dark image sequences
        :param light: relative path to light folder
        :param dark: relative path to dark folder
        :param size: size of the images
        :return: array of tuple of light and dark ctk images
        """
        image_paths = []
        for path in (light, dark):
            ''' 
            walk() gives [<folder>,[<sub folder>],[<list of files>]
            so '_' ignores the <folder> and '__' ignores the <sub folder>
            '''
            for _, __, img_data in os.walk(path):
                sorted_data = sorted(
                    img_data,
                    key=lambda x: int(x.split('.')[0][-4:])  # key performs any function on the data before applying sort
                )
                # performs the before operation first and then add it to the list
                full_path_data = [path + '/' + item for item in sorted_data]
                image_paths.append(full_path_data)
        # '*' unpacks the image paths
        # zip merges 1st element of 1st list with 1st element of 2nd list as one tuple for the whole list
        # and creates an iterable of those tuples
        image_paths = list(zip(*image_paths))

        ctk_images = []
        for image_path in image_paths:
            ctk_image = ctk.CTkImage(
                light_image=Image.open(image_path[0]),
                dark_image=Image.open(image_path[1]),
                size=size
            )
            ctk_images.append(ctk_image)

        return ctk_images

    def animate(self, anim_speed: int):
        """
        animates the button
        :param anim_speed: speed of animation
        """
        if self.animation_status == 'start':  # start the animation
            self.frame_index += 1
            self.configure(image=self.frames[self.frame_index])

            if self.frame_index < self.animation_length:  # if animation has ended
                self.after(anim_speed, lambda: self.animate(anim_speed))
            else:
                self.animation_status = 'end'
        if self.animation_status == 'end':  # play the animation ijn reverse
            self.frame_index -= 1
            self.configure(image=self.frames[self.frame_index])

            if self.frame_index > 0:  # if animation has ended
                self.after(anim_speed, lambda: self.animate(anim_speed))
            else:
                self.animation_status = 'start'
                self.after(anim_speed, lambda: self.animate(anim_speed))


class Video(TkinterVideo):
    def __init__(self, master: ctk.CTk, video_file_path: str, audio_path='', end_function: Callable[[], None] = None, **kwargs):
        super().__init__(master=master, **kwargs)
        # attributes
        self.ended = False
        self.end_function = end_function
        self.set_resampling_method(1)
        self.bind("<<Ended>>", lambda event: self.video_ended())
        self.video_file_path = video_file_path
        self.audio_path = audio_path
        try:
            self.load(video_file_path)
        except Exception as e:
            print("Unable to load the file", e)
        self.bg_play()

    def video_ended(self):
        """performs something on video being ended"""
        self.ended = True
        if self.end_function is not None:
            self.end_function()
        else:
            self.play()

    def has_video_end(self):
        """
        returns The status of the video
        :return: Boolean, True if ended
        """
        return self.ended

    def bg_play(self):
        """Play the video"""
        self.ended = False
        self.play()
        if self.audio_path:  # Play audio if externally provided
            threading.Thread(target=SoundManager.play, args=(self.audio_path,), daemon=True).start()

    def play_pause(self):
        """Pause and resume the video"""
        if self.is_paused():
            self.play()
        else:
            self.pause()
