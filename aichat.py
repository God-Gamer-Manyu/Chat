# Importing modules
import concurrent.futures
import datetime
import time
import tkinter

import customtkinter as ctk
import openai
from PIL import Image

import Main
import Utility
import os

# later: comment, document, fix light warnings, optimise code and use tkinter class wherever possible to organise code
# later: For approach to optimise tkinter ui - https://www.youtube.com/watch?v=0y1kYxOp8hE&list=PLpMixYKO4EXflJFPhTvZOVAbs7lBdEBSa&index=11
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
        # imp: uncomment when building exe for actual board practicals
        # openai.api_key = os.getenv('AI_API_KEY')
        openai.api_key = 'disabled for testing'

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
            if 'Incorrect API key' in str(e):
                return [('', 'disabled Temporarily, will be enabled during actual practicals')]
            return [('', 'Error while connecting to the internet, please check your internet connection')]
        self.history.append((message, '\n' + output, str(datetime.datetime.now())))   # updating the history
        return self.history  # returning the whole history

    def mainloop(self, app, size_x, size_y, profile_address, username, conversation, password):
        app.title(f"Intelli chat - {Utility.AI_CHAT_NAME}")   # Set title

        def close_window():
            Main.Main.save_login_cred(username, password, profile_address)
            Utility.SoundManager.quit()
            app.destroy()

        app.protocol("WM_DELETE_WINDOW", close_window)

        # BG
        bg_img = ctk.CTkImage(*map(Image.open, IMAGES['bg']), size=BG_SIZE)
        bg_l1 = ctk.CTkLabel(master=app, image=bg_img, text='')
        bg_l1.pack(fill='both', expand=True)

        # Main placeholder
        frame = ctk.CTkFrame(
            master=bg_l1,
            width=size_x - 50,
            height=size_y - 50,
            fg_color=COLOR['chat']['darkest'],
            bg_color=COLOR['chat']['darkest']
        )
        frame.place(relx=.5, rely=.5, anchor=ctk.CENTER)

        intro_label = ctk.CTkLabel(
            master=frame,
            text='Welcome to Intelli Chat AI!',
            font=FONT["Oth_uname"],
            text_color=COLOR['font']['2'],
        )
        intro_label.grid(row=0, column=0, columnspan=2, padx=100, pady=5)

        # back method
        def back():
            bg_l1.destroy()
            main = Main.Main(username, conversation, password, profile_address, self.history)
            main.run(app)

        # back button
        back_btn = ctk.CTkButton(
            master=frame,
            width=30,
            height=30,
            text='Back',
            font=FONT['Comic'],
            command=back,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        back_btn.grid(row=0, column=0, sticky='w', padx=5, pady=5)

        # input field
        txt_field = ctk.CTkEntry(
            master=frame,
            width=size_x - 130,
            placeholder_text='Type Here',
            font=FONT['Comic'],
            fg_color=COLOR['chat']['inside 1'],
            border_color=COLOR['chat']['scroll']
        )
        txt_field.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky='w')

        # message holder
        message_area = ctk.CTkScrollableFrame(
            master=frame,
            width=size_x - 115,
            height=size_y - 135,
            fg_color=COLOR['chat']['inside 1'],
            scrollbar_button_color=COLOR['chat']['scroll'],
            scrollbar_button_hover_color=COLOR['chat']['scroll hover']
        )
        message_area.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # User message template
        class User(ctk.CTkFrame):
            def __init__(self, message):
                super().__init__(
                    message_area,
                    border_width=1,
                    fg_color=COLOR['user']['frame-fg'],
                    border_color=COLOR['user']['frame-border']
                )
                self.pack(anchor='e')
                self.message = message

            def draw(self, current_time=''):
                Utility.SoundManager.play(SOUND_EFFECTS['send'])
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
                    font=FONT['Comic'],
                    anchor='w',
                    justify='left',
                    text=mes,
                    corner_radius=7,
                    fg_color=COLOR['user']['t-box-fg'])
                us_txt.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

                # display profile pic
                if profile_address == IMAGES['user']:
                    us_img = ctk.CTkImage(Image.open(profile_address))
                else:
                    us_img = ctk.CTkImage(Utility.Images.open_as_circle(profile_address))
                us_img_l = ctk.CTkLabel(master=self, image=us_img, width=30, height=30, text='')
                us_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky='nw')

                # display current_time stamp
                if current_time == '':
                    current_time = datetime.datetime.now()
                us_time = ctk.CTkLabel(master=self, text=str(current_time)[:-10], width=30,
                                                 height=10, font=FONT['t_stamp'])
                us_time.grid(row=1, column=1, padx=5, pady=(0, 5), sticky='se')

        # AI message template
        class Ai(ctk.CTkFrame):
            def __init__(self):
                super().__init__(
                    message_area,
                    border_width=1,
                    fg_color=COLOR['other cl']['frame-fg'],
                    border_color=COLOR['other cl']['frame-border']
                )
                self.pack(anchor='w')

            def draw_from_ques(self, question, history):
                # bot logo
                client_img = ctk.CTkImage(Image.open(IMAGES['bot']))
                client_img_l = ctk.CTkLabel(master=self, image=client_img, width=30, height=30,
                                                      text='')
                client_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky="nw")

                # timestamp
                cur_time = datetime.datetime.now()
                client_time = ctk.CTkLabel(master=self, text=str(cur_time)[:-10],
                                                     width=30,
                                                     height=10, font=FONT['t_stamp'])
                client_time.grid(row=1, column=1, padx=5, pady=(0, 5), sticky='ne')
                # bot message
                client_txt = ctk.CTkLabel(
                    master=self,
                    font=FONT['Comic'],
                    text='',
                    corner_radius=7,
                    anchor="w",
                    justify='left',
                    fg_color=COLOR['other cl']['t-box-fg'],
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
                    client_txt.configure(state=ctk.DISABLED)

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

                client_time.destroy()
                client_txt.destroy()

                # bot logo
                client_img = ctk.CTkImage(Image.open(IMAGES['bot']))
                client_img_l = ctk.CTkLabel(master=self, image=client_img, width=30, height=30, text='')
                client_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky="nw")

                # timestamp
                client_time = ctk.CTkLabel(master=self, text=str(cur_time)[:-10],
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

                client_txt = ctk.CTkLabel(
                    master=self,
                    font=FONT['Comic'],
                    corner_radius=7,
                    text=mes,
                    anchor="w",
                    justify='left',
                    fg_color=COLOR['other cl']['t-box-fg'],
                )
                client_txt.grid(row=0, column=1, padx=5, pady=5, sticky='nsew')

            def draw(self, message, current_time):
                Utility.SoundManager.play(SOUND_EFFECTS['receive'])

                # bot logo
                client_img = ctk.CTkImage(Image.open(IMAGES['bot']))
                client_img_l = ctk.CTkLabel(master=self, image=client_img, width=30, height=30, text='')
                client_img_l.grid(row=0, column=0, padx=(5, 0), pady=7, sticky="nw")

                # timestamp
                client_time = ctk.CTkLabel(master=self, text=str(current_time)[:-10],
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
                client_txt = ctk.CTkLabel(
                    master=self,
                    font=FONT['Comic'],
                    corner_radius=7,
                    text=mes,
                    anchor="w",
                    justify='left',
                    fg_color=COLOR['other cl']['t-box-fg'],
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
        enter_img = ctk.CTkImage(Image.open(IMAGES['send']))
        enter = ctk.CTkButton(
            master=frame,
            width=30,
            corner_radius=5,
            command=enter_btn,
            text='',
            image=enter_img,
            text_color=COLOR['font']['1'],
            fg_color=COLOR['button']['normal'],
            hover_color=COLOR['button']['hover']
        )
        enter.grid(row=2, column=1, padx=(0, 5), pady=5, sticky='e')

        app.bind('<Return>', enter_btn)  # Enter button function

        # initial message
        initial_ai = Ai()
        initial_ai.draw(self.history[0][1], str(self.history[0][2]))

        for i in self.history[1:]:
            user = User(i[0])
            user.draw(i[2])
            ai = Ai()
            ai.draw(i[1], i[2])
        
        app.mainloop()  # update display per frame
