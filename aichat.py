# Importing modules
import openai
import datetime
import customtkinter
import tkinter
from PIL import ImageTk, Image
import concurrent.futures
import time

import Main
import Utility
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
MESSAGE_LINE_LENGTH = 173
PIX_LINE = 15
BORDER_PIX = 44
BG_SIZE = Utility.BG_IMG_SIZE


# method which gets the output from open AI
def ask_openai(prompt):
    try:
        # imp: get new upi and try using env format
        openai.api_key = "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"

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

        app.geometry(f'{size_x}x{size_y}')  # Set screen size
        app.title("Intelli chat - AI")   # Set title
        # set the icon for the window
        app.iconbitmap(IMAGES['logo_ico'])
        app.wm_iconbitmap(IMAGES['logo_ico'])

        def close_window():
            Main.Main.save_login_cred(username, password, profile_address)
            Utility.SoundManager.quit()
            Utility.Message.close()
            app.destroy()

        app.protocol("WM_DELETE_WINDOW", close_window)

        # BG
        bg_img = Image.open(IMAGES['bg'])
        bg_img = customtkinter.CTkImage(bg_img, size=BG_SIZE)
        bg_l1 = customtkinter.CTkLabel(master=app, image=bg_img, text='')
        bg_l1.pack(fill='both', expand=True)

        # todo: Make ui grid and make them scalable
        # Main placeholder
        frame = customtkinter.CTkFrame(master=bg_l1, width=size_x - 50, height=size_y - 50, corner_radius=15)
        frame.place(relx=.5, rely=.5, anchor=tkinter.CENTER)

        # back method
        def back():
            bg_l1.destroy()
            main = Main.Main(username, conversation, password, profile_address, self.history)
            main.run(app)

        # back button
        back_btn = customtkinter.CTkButton(master=bg_l1, width=30, height=30, text='Back', font=FONT['Comic'], command=back)
        back_btn.place(x=45, y=15, anchor=tkinter.CENTER)

        # input field
        txt_field = customtkinter.CTkEntry(master=frame, width=size_x - 130, placeholder_text='Type Here', font=FONT['Comic'])
        txt_field.place(x=25, y=size_y-100)

        # message holder
        message_area = customtkinter.CTkScrollableFrame(master=frame, width=size_x - 115, height=size_y - 135)
        message_area.place(x=25, y=15)

        # User message template
        class User:
            def __init__(self, message):
                self.message = message

            def size_h(self):  # Determines the relative size of message widget
                # Adjustment values
                pix_line = PIX_LINE
                border_pix = BORDER_PIX

                # message
                mes = self.message
                mes = mes.split('\n')

                # finding length
                max_len = max(list(map(len, mes)))
                if max_len >= MESSAGE_LINE_LENGTH:
                    mes_len = 1125
                else:
                    mes_len = max_len % MESSAGE_LINE_LENGTH
                mes_len = (mes_len * 7) + 10

                def clamp(value, min_value, max_value):
                    return max(min(value, max_value), min_value)

                mes_len = clamp(mes_len, 50, 1125)

                # finding the height
                height = len(mes)
                for j in mes:
                    length = len(j)/MESSAGE_LINE_LENGTH
                    if length > 1:
                        height += int(length)
                height *= pix_line
                if height == 15:
                    return 34, mes_len

                return height + border_pix, mes_len

            # urgent: make ui background to blue
            def draw(self, current_time=''):
                Utility.SoundManager.play(SOUND_EFFECTS['send'])
                mes_h, mes_y = self.size_h()   # Getting the desired height

                # message holder
                us_mes = customtkinter.CTkFrame(master=message_area, width=mes_y + 45, height=mes_h + 30,
                                                border_width=1)
                us_mes.pack(anchor='e')
                # display message
                us_txt = customtkinter.CTkTextbox(master=us_mes, width=mes_y, height=mes_h, font=FONT['Comic'],
                                                  corner_radius=7, border_spacing=1)
                us_txt.insert(customtkinter.END, text=self.message)
                us_txt.place(x=5, y=5)
                us_txt.configure(state=customtkinter.DISABLED)

                # display profile pic
                us_img = customtkinter.CTkImage(Image.open(profile_address))
                us_img_l = customtkinter.CTkLabel(master=us_mes, image=us_img, width=30, height=30, text='')
                us_img_l.place(x=mes_y + 5, y=5)

                # display current_time stamp
                if current_time == '':
                    current_time = datetime.datetime.now()
                us_time = customtkinter.CTkLabel(master=us_mes, text=str(current_time)[:-10], width=30,
                                                 height=10, font=FONT['t_stamp'])
                us_time.place(x=mes_y - 30, y=mes_h + 12)

        # AI message template
        class Ai:

            @staticmethod   # Determines the relative size of message widget
            def size_h(message):
                # adjustments
                pix_line = PIX_LINE
                border_pix = BORDER_PIX

                # message
                mes = message
                mes = mes.split('\n')

                # finding relative length
                max_len = max(list(map(len, mes)))
                if max_len >= MESSAGE_LINE_LENGTH:
                    mes_len = 1125
                else:
                    mes_len = max_len % MESSAGE_LINE_LENGTH
                mes_len = (mes_len * 7) + 10

                def clamp(value, min_value, max_value):
                    return max(min(value, max_value), min_value)
                mes_len = clamp(mes_len, 50, 1125)

                # finding relative height
                height = len(mes)
                for j in mes:
                    length = len(j)/MESSAGE_LINE_LENGTH
                    if length > 1:
                        height += int(length)
                height *= pix_line
                if height == 15:
                    return 34, mes_len
                return height + border_pix, mes_len

            def draw_from_ques(self, question, history):
                mes_h, mes_y = self.size_h('.....')
                # message placeholder
                client_mes = customtkinter.CTkFrame(master=message_area, width=mes_y + 45, height=mes_h + 30,
                                                    border_width=1)
                client_mes.pack(anchor='w')

                # bot logo
                client_img = customtkinter.CTkImage(Image.open(IMAGES['bot']))
                client_img_l = customtkinter.CTkLabel(master=client_mes, image=client_img, width=30, height=30,
                                                      text='')
                client_img_l.place(x=5, y=5)

                # timestamp
                cur_time = datetime.datetime.now()
                client_time = customtkinter.CTkLabel(master=client_mes, text=str(cur_time)[:-10],
                                                     width=30,
                                                     height=10, font=FONT['t_stamp'])
                client_time.place(x=mes_y - 30, y=mes_h + 12)
                # bot message
                client_txt = customtkinter.CTkTextbox(master=client_mes, width=mes_y, height=mes_h,
                                                      font=FONT['Comic'],
                                                      corner_radius=7,
                                                      border_spacing=1)
                client_txt.insert(customtkinter.END, text='')
                client_txt.place(x=35, y=5)

                task_finished = False

                def update_text():
                    if not task_finished:
                        # delete all existing text
                        client_txt.delete('1.0', customtkinter.END)
                        # insert the current message and dots
                        dots = ''

                        for ct in range(5):
                            dots += '.'
                            client_txt.delete('1.0', customtkinter.END)
                            client_txt.insert(customtkinter.END, dots)
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

                mes_h, mes_y = self.size_h(res)    # getting relative height
                client_mes.destroy()
                client_time.destroy()
                client_txt.destroy()

                # message placeholder
                client_mes = customtkinter.CTkFrame(master=message_area, width=mes_y + 45, height=mes_h + 30,
                                                    border_width=1)
                client_mes.pack(anchor='w')

                # bot logo
                client_img = customtkinter.CTkImage(Image.open(IMAGES['bot']))
                client_img_l = customtkinter.CTkLabel(master=client_mes, image=client_img, width=30, height=30, text='')
                client_img_l.place(x=5, y=5)

                # timestamp
                client_time = customtkinter.CTkLabel(master=client_mes, text=str(cur_time)[:-10],
                                                     width=30,
                                                     height=10, font=FONT['t_stamp'])
                client_time.place(x=mes_y - 35, y=mes_h + 12)

                # bot message
                client_txt = customtkinter.CTkTextbox(master=client_mes, width=mes_y, height=mes_h, font=FONT['Comic'],
                                                      corner_radius=7,
                                                      border_spacing=1)
                client_txt.insert(customtkinter.END, text=res)
                client_txt.configure(state=customtkinter.DISABLED)
                client_txt.place(x=35, y=5)

            def draw(self, message, current_time):
                Utility.SoundManager.play(SOUND_EFFECTS['receive'])
                mes_h, mes_y = self.size_h(message)    # getting relative height

                # message placeholder
                client_mes = customtkinter.CTkFrame(master=message_area, width=mes_y + 45, height=mes_h + 30,
                                                    border_width=1)
                client_mes.pack(anchor='w')

                # bot logo
                client_img = customtkinter.CTkImage(Image.open(IMAGES['bot']))
                client_img_l = customtkinter.CTkLabel(master=client_mes, image=client_img, width=30, height=30, text='')
                client_img_l.place(x=5, y=5)

                # timestamp
                client_time = customtkinter.CTkLabel(master=client_mes, text=str(current_time)[:-10],
                                                     width=30,
                                                     height=10, font=FONT['t_stamp'])
                client_time.place(x=mes_y - 35, y=mes_h + 12)

                # bot message
                client_txt = customtkinter.CTkTextbox(master=client_mes, width=mes_y, height=mes_h, font=FONT['Comic'],
                                                      corner_radius=7,
                                                      border_spacing=1)
                client_txt.insert(customtkinter.END, text=message)
                client_txt.configure(state=customtkinter.DISABLED)
                client_txt.place(x=35, y=5)

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
        enter.place(x=size_x-100, y=size_y-100)

        app.bind('<Return>', enter_btn)  # Enter button function

        # initial message display
        i_mes_h, i_mes_y = 74, 1125
        # message placeholder
        i_client_mes = customtkinter.CTkFrame(master=message_area, width=i_mes_y + 45, height=i_mes_h + 30, border_width=1)
        i_client_mes.pack(anchor='w')

        # bot logo
        i_client_img = customtkinter.CTkImage(Image.open(IMAGES['bot']))
        i_client_img_l = customtkinter.CTkLabel(master=i_client_mes, image=i_client_img, width=30, height=30, text='')
        i_client_img_l.place(x=5, y=5)

        # timestamp
        i_client_time = customtkinter.CTkLabel(master=i_client_mes, text=str(self.history[0][2])[:-10], width=30, height=10, font=FONT['t_stamp'])
        i_client_time.place(x=i_mes_y - 35, y=i_mes_h + 12)
        # bot message
        i_client_txt = customtkinter.CTkTextbox(master=i_client_mes, width=i_mes_y, height=i_mes_h, font=FONT['Comic'], corner_radius=7, border_spacing=1)
        i_client_txt.insert(customtkinter.END, text=self.history[0][1].strip())
        i_client_txt.configure(state=customtkinter.DISABLED)
        i_client_txt.place(x=35, y=5)

        ai = Ai()
        for i in self.history[1:]:
            user = User(i[0])
            user.draw(i[2])
            ai.draw(i[1], i[2])
        
        app.mainloop()  # update display per frame
