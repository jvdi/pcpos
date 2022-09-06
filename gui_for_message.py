from pathlib import Path
from tkinter import Tk, Canvas, Button, PhotoImage, scrolledtext


# asset directory
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


class tk_gui:
    def __init__(self):
        self.window = Tk()
        self.window.title('PCPos Ver:2.1.1')
        self.window.iconbitmap('assets/pos.ico')
        self.window.eval('tk::PlaceWindow . center')
        self.window.geometry("300x150")
        self.window.configure(bg="#FFFFFF")
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)

    def canvas(self):
        self.canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=150,
            width=300,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )

    def dialog(self, option_1, func_1, flag, option_2, func_2, log):
        self.canvas()
        # btn 1 - OK
        self.canvas.place(x=0, y=0)
        button_image_1 = PhotoImage(
            file=relative_to_assets(option_1))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: [self.window.destroy(), func_1()],
            relief="flat"
        )
        button_1.place(
            x=7.0,
            y=89.0,
            width=90.0,
            height=46.0
        )
        if flag:
            pass
        else:
            # btn 2 - Cancell
            button_image_2 = PhotoImage(
                file=relative_to_assets(option_2))
            button_2 = Button(
                image=button_image_2,
                borderwidth=0,
                highlightthickness=0,
                command=lambda: [self.window.destroy(), func_2()],
                relief="flat"
            )
            button_2.place(
                x=203.0,
                y=89.0,
                width=90.0,
                height=46.0
            )
        # TextAria
        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = self.canvas.create_image(
            150.0,
            37.5,
            image=entry_image_1
        )
        entry_1 = scrolledtext.ScrolledText(
            bd=0,
            bg="#C4C4C4",
            highlightthickness=0,
            font=("Aria", 15),
            wrap='word'
        )
        entry_1.place(
            x=0.0,
            y=0.0,
            width=300.0,
            height=73.0
        )
        # Show log
        entry_1.insert("end", log)
        entry_1.configure(state='disabled')
        self.window.mainloop()

    def show_message(self, send_prc, abort_pay, json, pay_name):
        # Do TransAction again btn or Cancell TransAction btn
        self.dialog(
            'button_1.png',
            send_prc,
            False,
            'button_2.png',
            abort_pay,
            json['PcPosStatus']+'\n'+json['ResponseCodeMessage']+'\n'+pay_name
        )
