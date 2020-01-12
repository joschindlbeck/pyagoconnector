from tkinter import *
from pyagoconnector import connector
import time

# Global variables
ago_connector: connector.AgoUdpServer = None

def start_monitor():
    window = Tk()
    window.title("AGOpen UDP Monitor")
    window.geometry("800x600")

    while True:

        # clear window
        children = window.winfo_children()
        for c in children:
            c.grid_forget()
            c.destroy()

        # generate labels for parameters
        i = 0
        for pgn in ago_connector.pgndata.values():  # loop pgns
            frame = create_frame(pgn, window)
            frame.grid(column=0, row=i)
            i += 1

        window.update()

        time.sleep(0.2)

    #window.mainloop()


def create_frame(pgn: connector.AgoPgn, window):

    # generate frame
    frame_title = "PGN " + str(pgn.pgn_number) + ": " \
                    + pgn.descr
    frame = LabelFrame(window, text=frame_title, padx=5, pady=5)
    # frame.grid(column=0, row=0)

    # add one label per data element
    i = 0
    for cur_par_id in pgn.data:  # loop parameters
        lbl_key = Label(frame, text=cur_par_id)
        lbl_key.grid(column=0, row=i)
        lbl_value = Label(frame, text=pgn.data[cur_par_id])
        lbl_value.grid(column=1, row=i)
        i += 1

    return frame

if __name__ == "__main__":
    # Create Server
    ago_connector = connector.AgoUdpServer.start_server_thread()
    time.sleep(1)
    # Start Monitor
    start_monitor()


