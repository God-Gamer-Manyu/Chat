# Importing modules
import concurrent.futures
import datetime
import time
import tkinter

import customtkinter
import openai
from PIL import Image

import Main
import Utility
import os

# later: comment document and fix light warnings
# imp: change 'import customtkinter' to 'from customtkinter import *' and other import statements too
# Global variables
# Fonts
FONT = Utility.FONT
# stored files
IMAGES = Utility.IMAGES
# Sound effects
SOUND_EFFECTS = Utility.SOUND_EFFECTS
# adjustment variables
MESSAGE_LINE_LENGTH = 16  # word limit
PIX_LINE = 15
BORDER_PIX = 44
BG_SIZE = Utility.BG_IMG_SIZE
COLOR = Utility.COLOR


# method which gets the output from open AI
def ask_openai(prompt):
    try:
        # imp: get new upi
        openai.api_key = os.getenv('AI_API_KEY')

        # start_sequence = "\nAI:"
        # restart_sequence = "\nHuman: "

        completion = openai.Completion.create(
            model='text-davinci-003',
            prompt=prompt,
            temperature=0,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=[" Human:", " AI:"]
        )

        return completion.choices[0].text
    except Exception as e:
        raise Exception(str(e))


class AiChat:
    def __init__(self, history):
        if not history:
            self.history = [('Hello, who are you?', "I'm Rohan an AI Assistant. I'm curious to know what your hobbies and interests are, what your goals and aspirations are, and what makes you unique. I'm also interested in learning about your family, your background, and your culture. I'm open to hearing about any experiences you've had that have shaped who you are today.", str(datetime.datetime.now()))]
        else:
            self.history = history

    def chatgpt_clone(self, message):
        s = []  # storing history as one list
        for i in self.history:  # adding the history
            s.append(i[0])
            s.append(i[1])
        print(s)
        s.append('\n'+message)  # for creation of string
        inp = ' '.join(s)  # string to send to open AI
        try:
            output = ask_openai(inp)    # getting the output
        except Exception as e:
            print(e)
            return [('', 'Error while connecting to the internet, please check your internet connection')]
        self.history.append((message, '\n' + output, str(datetime.datetime.now())))   # updating the history
        return self.history  # returning the whole history

    def mainloop(self, app, size_x, size_y, profile_address, username, conversation, password):
        customtkinter.set_appearance_mode('dark')   # set mode
        customtkinter.set_default_color_theme('dark-blue')  # set theme

        app.title("Intelli chat - AI")   # Set title
        # set the icon for the window

        def close_window():
            Main.Main.save_login_cred(username, password, profile_address)
            Utility.SoundManager.quit()
            app.destroy()

        app.protocol("WM_DELETE_WINDOW", close_window)

        # BG
        bg_img = Image.open(IMAGES['bg'])
        bg_img = customtkinter.CTkImage(bg_img, size=BG_SIZE)
        bg_l1 = customtkinter.CTkLabel(master=app, image=bg_img, text='')
        bg_l1.pack(fill='both', expand=True)

        # Main placeholder
        frame = customtkinter.CTkFrame(master=bg_l1, width=size_x - 50, height=size_y - 50, corner_radius=15)
        frame.place(relx=.5, rely=.5, anchor=customtkinter.CENTER)

        intro_label = customtkinter.CTkLabel(master=frame, text='Welcome to Intelli Chat AI!', font=FONT["Oth_uname"])
        intro_label.grid(row=0, column=0, columnspan=2, padx=100, pady=5)

        # back method
        def back():
            bg_l1.destroy()
            main = Main.Main(username, conversation, password, profile_address, self.history)
            main.run(app)

        # back button
        back_btn = customtkinter.CTkButton(master=frame, width=30, height=30, text='Back', font=FONT['Comic'], command=back)
        back_btn.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        # input field
        txt_field = customtkinter.CTkEntry(master=frame, width=size_x - 130, placeholder_text='Type Here', font=FONT['Comic'])
        txt_field.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # message holder
        message_area = customtkinter.CTkScrollableFrame(master=frame, width=size_x - 115, height=size_y - 135)
        message_area.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # User message template
        class User:
            def __init__(self, message):
                self.message = message

            def draw(self, current_time=''):
                Utility.SoundManager.play(SOUND_EFFECTS['send'])

                # message holder
                us_mes = customtkinter.CTkFrame(master=message_area,
                                                border_width=1, fg_color=COLOR['user']['frame-fg'], border_color=COLOR['user']['frame-border'])
                us_mes.pack(anchor='e')
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
                us_txt = customtkinter.CTkLabel(
                    master=us_mes,
                    font=FONT['Comic'],
                    anchor='w',
                    justify='left',
                    text=mes,
                    corner_radius=7,
                    fg_color=COLOR['user']['t-box-fg'])
                us_txt.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

                # display profile pic
                us_img = customtkinter.CTkImage(Image.open(profile_address))
                us_img_l = customtkinter.CTkLabel(master=us_mes, image=us_img, width=30, height=30, text='')
                us_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky='nw')

                # display current_time stamp
                if current_time == '':
                    current_time = datetime.datetime.now()
                us_time = customtkinter.CTkLabel(master=us_mes, text=str(current_time)[:-10], width=30,
                                                 height=10, font=FONT['t_stamp'])
                us_time.grid(row=1, column=1, padx=5, pady=(0, 5), sticky='se')

        # AI message template
        class Ai:
            def draw_from_ques(self, question, history):
                # message placeholder
                client_mes = customtkinter.CTkFrame(master=message_area, border_width=1)
                client_mes.pack(anchor='w')

                # bot logo
                client_img = customtkinter.CTkImage(Image.open(IMAGES['bot']))
                client_img_l = customtkinter.CTkLabel(master=client_mes, image=client_img, width=30, height=30,
                                                      text='')
                client_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky="nw")

                # timestamp
                cur_time = datetime.datetime.now()
                client_time = customtkinter.CTkLabel(master=client_mes, text=str(cur_time)[:-10],
                                                     width=30,
                                                     height=10, font=FONT['t_stamp'])
                client_time.grid(row=1, column=1, padx=5, pady=(0, 5), sticky='ne')
                # bot message
                client_txt = customtkinter.CTkLabel(
                    master=client_mes,
                    font=FONT['Comic'],
                    text='',
                    corner_radius=7,
                    anchor="w",
                    justify='left',
                    fg_color='#424242'
                )
                client_txt.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

                task_finished = False

                def update_text():
                    if not task_finished:
                        # insert the current message and dots
                        dots = ''

                        for ct in range(5):
                            dots += '.'
                            client_txt.configure(text=dots)
                            app.update()
                            time.sleep(.2)

                        # schedule the next update
                        app.after(250, update_text)

                # Create a thread pool executor with one worker thread
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    # Submit the function to the executor and get a Future object
                    aichat = AiChat(history)
                    future = executor.submit(aichat.chatgpt_clone, question)

                    # Do other things while the function is running in another thread
                    update_text()

                    # Get the return value of the function (this blocks until the function completes)
                    response = future.result()[-1][1]  # retrieving bot output
                    task_finished = True
                    Utility.SoundManager.play(SOUND_EFFECTS['receive'])
                    client_txt.configure(state=customtkinter.DISABLED)

                # refining output
                res = ''
                let = False
                for resp in response:
                    if resp in ' ?.,\n' and not let:
                        continue
                    if resp.isalnum():
                        res += resp
                        let = True
                        continue
                    else:
                        res += resp

                client_mes.destroy()
                client_time.destroy()
                client_txt.destroy()

                # message placeholder
                client_mes = customtkinter.CTkFrame(master=message_area, border_width=1)
                client_mes.pack(anchor='w')

                # bot logo
                client_img = customtkinter.CTkImage(Image.open(IMAGES['bot']))
                client_img_l = customtkinter.CTkLabel(master=client_mes, image=client_img, width=30, height=30, text='')
                client_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky="nw")

                # timestamp
                client_time = customtkinter.CTkLabel(master=client_mes, text=str(cur_time)[:-10],
                                                     width=30,
                                                     height=10, font=FONT['t_stamp'])
                client_time.grid(row=1, column=1, padx=5, pady=5, sticky="ne")

                # bot message
                mes = ''
                ct = 0
                for i in res.split():
                    if ct >= MESSAGE_LINE_LENGTH:
                        mes += '\n' + i
                        ct = 0
                    else:
                        mes += ' ' + i
                    ct += 1
                client_txt = customtkinter.CTkLabel(
                    master=client_mes,
                    font=FONT['Comic'],
                    corner_radius=7,
                    text=res,
                    anchor="w",
                    justify='left',
                    fg_color='#424242'
                )
                client_txt.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

            def draw(self, message, current_time):
                Utility.SoundManager.play(SOUND_EFFECTS['receive'])

                # message placeholder
                client_mes = customtkinter.CTkFrame(master=message_area, border_width=1)
                client_mes.pack(anchor='w')

                # bot logo
                client_img = customtkinter.CTkImage(Image.open(IMAGES['bot']))
                client_img_l = customtkinter.CTkLabel(master=client_mes, image=client_img, width=30, height=30, text='')
                client_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky="nw")

                # timestamp
                client_time = customtkinter.CTkLabel(master=client_mes, text=str(current_time)[:-10],
                                                     width=30,
                                                     height=10, font=FONT['t_stamp'])
                client_time.grid(row=1, column=1, padx=5, pady=(0, 5), sticky='ne')

                # bot message
                mes = ''
                ct = 0
                for i in message.split():
                    if ct >= MESSAGE_LINE_LENGTH:
                        mes += '\n' + i
                        ct = 0
                    else:
                        mes += ' ' + i
                    ct += 1
                client_txt = customtkinter.CTkLabel(
                    master=client_mes,
                    font=FONT['Comic'],
                    corner_radius=7,
                    text=mes,
                    anchor="w",
                    justify='left',
                    fg_color='#424242'
                )
                client_txt.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        def enter_btn(event=None):  # functioned called when enter key or send button is pressed
            print(event)
            user_mes = User(txt_field.get())    # invoking user message template
            user_mes.draw()  # displaying user message template

            ai_mes = Ai()   # invoking AI message template
            ai_mes.draw_from_ques(txt_field.get(), self.history)  # displaying AI message template

            txt_field.delete(0, tkinter.END)    # clearing input field

        # sent button
        enter_img = customtkinter.CTkImage(Image.open(IMAGES['send']))
        enter = customtkinter.CTkButton(master=frame, width=30, corner_radius=5, command=enter_btn, text='', image=enter_img)
        enter.grid(row=2, column=1, padx=(0, 5), pady=5, sticky='e')

        app.bind('<Return>', enter_btn)  # Enter button function

        # initial message
        Utility.SoundManager.play(SOUND_EFFECTS["receive"])
        # message placeholder
        i_client_mes = customtkinter.CTkFrame(master=message_area, border_width=1)
        i_client_mes.pack(anchor='w')

        # bot logo
        i_client_img = customtkinter.CTkImage(Image.open(IMAGES['bot']))
        i_client_img_l = customtkinter.CTkLabel(master=i_client_mes, image=i_client_img, width=30, height=30, text='')
        i_client_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky="nw")

        # timestamp
        i_client_time = customtkinter.CTkLabel(master=i_client_mes, text=str(self.history[0][2])[:-10], width=30, height=10, font=FONT['t_stamp'])
        i_client_time.grid(row=1, column=1, padx=5, pady=(0, 5), sticky='ne')
        # bot message
        mes = ''
        ct = 0
        for i in self.history[0][1].strip().split():
            if ct >= 20:
                mes += '\n' + i
                ct = 0
            else:
                mes += ' ' + i
            ct += 1
        i_client_txt = customtkinter.CTkLabel(
            master=i_client_mes,
            font=FONT['Comic'],
            corner_radius=7,
            anchor='w',
            justify='left',
            text=mes,
            fg_color='#424242'
        )
        i_client_txt.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

        ai = Ai()
        for i in self.history[1:]:
            user = User(i[0])
            user.draw(i[2])
            ai.draw(i[1], i[2])
        
        app.mainloop()  # update display per frame
