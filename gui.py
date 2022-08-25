from pathlib import Path
from tkinter import Tk, Canvas, Text, Button, PhotoImage


# asset directory
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)


class tk_gui:
    def __init__(self):
        self.window = Tk()
        self.window.title('PCPos')
        self.window.iconbitmap('assets/pos.ico')
        self.window.eval('tk::PlaceWindow . center')
        self.window.geometry("300x150")
        self.window.configure(bg="#FFFFFF")
        self.window.resizable(False, False)
        self.window.attributes('-topmost', True)
    
    def show_message(self, send_prc, abort_pay, json, pay_name):
        self.canvas = Canvas(
            self.window,
            bg="#FFFFFF",
            height=150,
            width=300,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        # run
        self.canvas.place(x=0, y=0)
        button_image_1 = PhotoImage(
            file=relative_to_assets("button_1.png"))
        button_1 = Button(
            image=button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: [self.window.destroy(), send_prc()],
            relief="flat"
        )
        button_1.place(
            x=7.0,
            y=89.0,
            width=90.0,
            height=46.0
        )
        # cancell
        button_image_2 = PhotoImage(
            file=relative_to_assets("button_2.png"))
        button_2 = Button(
            image=button_image_2,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: [self.window.destroy(), abort_pay()],
            relief="flat"
        )
        button_2.place(
            x=203.0,
            y=89.0,
            width=90.0,
            height=46.0
        )

        entry_image_1 = PhotoImage(
            file=relative_to_assets("entry_1.png"))
        entry_bg_1 = self.canvas.create_image(
            150.0,
            37.5,
            image=entry_image_1
        )
        entry_1 = Text(
            bd=0,
            bg="#C4C4C4",
            highlightthickness=0,
            font=("Aria", 15),
            wrap='word',


        )
        entry_1.place(
            x=0.0,
            y=0.0,
            width=300.0,
            height=73.0
        )
        # Print error for user
        entry_1.insert("end", json['PcPosStatus'] +
                       '\n'+json['ResponseCodeMessage']+
                       '\n'+pay_name)
        self.window.mainloop()
