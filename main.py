import MessageManager
import threading
import logging
import can
from can.protocols import j1939
from can.interfaces.interface import Bus as RawCanBus
from can import Message
from can.notifier import Notifier
from can.protocols.j1939.arbitrationid import ArbitrationID
from can.protocols.j1939.pdu import PDU
from can.protocols.j1939.pgn import PGN
from can.bus import BusABC
from can.protocols.j1939 import constants
from can.protocols.j1939.node import Node
from can.protocols.j1939.nodename import NodeName
import os
import time
import NewBus
import DisplayManager
import tkinter

UPDATE_RATE = 4000

from tkinter import *
# import tkinter as tk


class Application(tkinter.Frame):

    def __init__(self, master):
        """ Initialize the Frame"""
        # tkinter.Frame.__init__(self, master)
        # self.grid()
        # self.create_widgets()
        # self.updater()


        # self.frame = Frame(master)
        self.root = root
        self.top = Toplevel(self.root)
       
        # self.frame.pack()
        self.create_widgets()
        self.root.after(30000,self.update)



    def create_widgets(self):

        logger = logging.getLogger(__name__)

        os.system('sudo ip link set can0 up type can bitrate 250000')
        time.sleep(0.1)

        try:
            bus = NewBus.Bus(channel='can0', bustype='socketcan_native')
            bus2 = can.interface.Bus(channel='can0', bustype='socketcan_native')

        except OSError:
            print('Cannot find PiCAN board.')
            exit()

        arbitration_id = ArbitrationID(priority=6, pgn=59904, source_address=1)

        msg2 = PDU(arbitration_id=arbitration_id, data=[229, 254, 000])
        msg3 = PDU(arbitration_id=arbitration_id, data=[233, 254, 000])


        start = time.time()
        runtime = 5  # How long?
        end = start + runtime
        now = time.time()
        

        bus.send(msg2)
        bus.send(msg3)

        while now < end:

            now = time.time()

            message = bus2.recv()

            my_message = MessageManager.MessageTransceiver()

            my_message.listen_data(message)

            my_message.check_message_type()

            if my_message.pgn_number == 0:
                print('Vehicle Odometer Data Found')
                odometer_module = MessageManager.OdometerData(my_message)
                # round_data_1 = int(round(odometer_module.calculate_element()))

            if my_message.pgn_number == 1:
                print('Total Engine Hours Data Found')
                engine_hours_module = MessageManager.EngineHours(my_message)
                # round_data_4 = int(round(engine_hours_module.calculate_element()))

            if my_message.pgn_number == 2:
                print('Total Fuel Used Data Found')
                fuel_used_module = MessageManager.FuelUsed(my_message)
                # round_data_5 = int(round(fuel_used_module.calculate_element()))

            if my_message.pgn_number == 3:
                print('Fuel Economy Data Found')
                fuel_economy_module = MessageManager.FuelEconomyData(my_message)
                # round_data_2 = int(round(fuel_economy_module.calculate_element()))

            if my_message.pgn_number == 4:
                print('Fuel Level 1 Data Found')
                fuel_level_module = MessageManager.FuelLevel1Data(my_message)
                print(fuel_level_module.calculate_element())
                # round_data_3 = round(fuel_level_module.calculate_element(),1)



        round_data_1 = round(odometer_module.calculate_element() , 1)
        round_data_2 = round(fuel_economy_module.calculate_element(), 1)
        # round_data_3 = round(fuel_level_module.calculate_element(), 1)
        round_data_4 = round(engine_hours_module.calculate_element(), 1)
        round_data_5 = round(fuel_used_module.calculate_element(), 1)

        os.system('pkill gpicview')
        plate = DisplayManager.DataPlate('dataplate.txt')



        
        plate.openFile()

        qr = DisplayManager.QRCreator(odometer_module.calculate_element(),fuel_economy_module.calculate_element(),-1, engine_hours_module.calculate_element(),fuel_used_module.calculate_element(), plate)
        #qr = DisplayManager2.QRCreator(round_data_1, round_data_2, -1, round_data_4, round_data_5, plate)
        # qr = DisplayManager2.QRCreator(round_data_1, round_data_2, round_data_3, round_data_4, round_data_5, plate)
        qr.display()
        self.img = PhotoImage(file='image.png')

        Data = [str(plate.serial_number), str(plate.niin),str(plate.tamcn),str(plate.test),"","   Value:", "   " + str(round_data_1), "   " + str(round_data_4), "   " + str(round_data_5), "   " + str(round_data_2), "   " + str(-1)]
        # Data = [str(plate.serial_number), str(plate.niin),str(plate.tamcn),str(plate.test),"","   Value:", "   " + str(odometer_module.calculate_element()), "   " + str(engine_hours_module.calculate_element()), "   " + str(fuel_used_module.calculate_element()), "   " + str(fuel_economy_module.calculate_element()), "   " + str(-1)]
        Labels = ["Serial Number:","NIIN:","TAMCN:","ID Number:","","Parameter:","Vehicle Odometer:","Total Engine Hours:","Total Fuel Used:","Fuel Economy:","Fuel Level 1:"]
        Units = ["","","","","","Units:","Miles","Hours","Gallons","Miles per Gallon","%"]
        height = len(Data)
        width = 3


        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()

        x = (ws/2) 
        y = (hs/2)

        ratio = 1366/18
        size = ws/ratio
        font_size = int(round(size))

        wratio_qr = 1366/700
        width_qr = ws/wratio_qr
        qr_width = int(round(width_qr))

        hratio_qr = 768/700
        height_qr = hs/hratio_qr
        qr_height = int(round(height_qr))

        wratio_dis = 1920/825
        width_dis = ws/wratio_dis
        dis_width = int(round(width_dis))

        hratio_dis = 1080/500
        height_dis = hs/hratio_dis
        dis_height = int(round(height_dis))

        x_dis = x-dis_width
        dis_xpos = x + (x_dis)/2

        y_dis = hs-dis_height
        dis_ypos = (y_dis)/2

        x_qr = x-qr_width
        qr_xpos = (x_qr)/2

        y_qr = hs-qr_height
        qr_ypos = (y_qr)/2
        
        #x_qr = x
        #qr_width = ws/
        

        for i in range(height):
            for j in range(width):
                if j == 1:
                    label = Label(self.root, text = Data[i],font=(None,font_size))
                    label.grid(row=i, column=j, sticky= W)
                elif j == 2:
                    label = Label(self.root, text = Units[i],font=(None,font_size))
                    label.grid(row=i,column =j,sticky = W)
                else:
                    label = Label(self.root, text = Labels[i],font=(None,font_size))
                    label.grid(row=i,column =j,sticky = W)
        # height = 8
        # width = 3



        
        self.root.geometry('%dx%d+%d+%d' % (dis_width,dis_height, dis_xpos,dis_ypos))
        self.top.geometry('%dx%d+%d+%d' % (qr_width,qr_height,qr_xpos,qr_ypos))
        # label = Label(root, text= totalData, width=150, font=(None,15))
        # label.pack()

        self.top.title('QR Code')
        self.root.title('Vehicle Information')
        self.panel = Label(self.top,image=self.img)
        self.panel.pack(side='bottom', fill='both',expand='yes')



        
    def update(self):

        logger = logging.getLogger(__name__)

        os.system('sudo ip link set can0 up type can bitrate 250000')
        time.sleep(0.1)

        try:
            bus = NewBus.Bus(channel='can0', bustype='socketcan_native')
            bus2 = can.interface.Bus(channel='can0', bustype='socketcan_native')

        except OSError:
            print('Cannot find PiCAN board.')
            exit()

        arbitration_id = ArbitrationID(priority=6, pgn=59904, source_address=1)

        msg2 = PDU(arbitration_id=arbitration_id, data=[229, 254, 000])
        msg3 = PDU(arbitration_id=arbitration_id, data=[233, 254, 000])


        start = time.time()
        runtime = 5  # How long?
        end = start + runtime
        now = time.time()
        

        bus.send(msg2)
        bus.send(msg3)

        while now < end:

            now = time.time()

            message = bus2.recv()

            my_message = MessageManager.MessageTransceiver()

            my_message.listen_data(message)

            my_message.check_message_type()

            if my_message.pgn_number == 0:
                print('Vehicle Odometer Data Found')
                odometer_module = MessageManager.OdometerData(my_message)
                # round_data_1 = int(round(odometer_module.calculate_element()))

            if my_message.pgn_number == 1:
                print('Total Engine Hours Data Found')
                engine_hours_module = MessageManager.EngineHours(my_message)
                # round_data_4 = int(round(engine_hours_module.calculate_element()))

            if my_message.pgn_number == 2:
                print('Total Fuel Used Data Found')
                fuel_used_module = MessageManager.FuelUsed(my_message)
                # round_data_5 = int(round(fuel_used_module.calculate_element()))

            if my_message.pgn_number == 3:
                print('Fuel Economy Data Found')
                fuel_economy_module = MessageManager.FuelEconomyData(my_message)
                # round_data_2 = int(round(fuel_economy_module.calculate_element()))

            if my_message.pgn_number == 4:
                print('Fuel Level 1 Data Found')
                fuel_level_module = MessageManager.FuelLevel1Data(my_message)
                print(fuel_level_module.calculate_element())
                # round_data_3 = round(fuel_level_module.calculate_element(),1)


        round_data_1 = round(odometer_module.calculate_element() , 1)
        round_data_2 = round(fuel_economy_module.calculate_element(), 1)
        # round_data_3 = round(fuel_level_module.calculate_element(), 1)
        round_data_4 = round(engine_hours_module.calculate_element(), 1)
        round_data_5 = round(fuel_used_module.calculate_element(), 1)
        
        os.system('pkill gpicview')
        plate = DisplayManager.DataPlate('dataplate.txt')
        plate.openFile()

        qr = DisplayManager.QRCreator(odometer_module.calculate_element(),fuel_economy_module.calculate_element(),-1, engine_hours_module.calculate_element(),fuel_used_module.calculate_element(), plate)

        # qr = DisplayManager2.QRCreator(round_data_1, round_data_2, -1, round_data_4, round_data_5, plate)
        # qr = DisplayManager2.QRCreator(round_data_1, round_data_2, round_data_3, round_data_4, round_data_5, plate)
        qr.display()

        Data = [str(plate.serial_number), str(plate.niin),str(plate.tamcn),str(plate.test),"","   Value:", "   " + str(round_data_1), "   " + str(round_data_4), "   " + str(round_data_5), "   " + str(round_data_2), "   " + str(-1)]
        # Data = [str(plate.serial_number), str(plate.niin),str(plate.tamcn),str(plate.test),"","   Value:", "   " + str(odometer_module.calculate_element()), "   " + str(engine_hours_module.calculate_element()), "   " + str(fuel_used_module.calculate_element()), "   " + str(fuel_economy_module.calculate_element()), "   " + str(-1)]
        Labels = ["Serial Number:","NIIN:","TAMCN:","ID Number:","","Parameter:","Vehicle Odometer:","Total Engine Hours:","Total Fuel Used:","Fuel Economy:","Fuel Level 1:"]
        Units = ["","","","","","Units:","Miles","Hours","Gallons","Miles per Gallon","%"]
        height = len(Data)
        width = 3

        ws = root.winfo_screenwidth()
        hs = root.winfo_screenheight()

        x = (ws/2) 
        y = (hs/2)

        ratio = 1366/18
        size = ws/ratio
        font_size = int(round(size))

        wratio_qr = 1366/700
        width_qr = ws/wratio_qr
        qr_width = int(round(width_qr))

        hratio_qr = 768/700
        height_qr = hs/hratio_qr
        qr_height = int(round(height_qr))

        wratio_dis = 1920/825
        width_dis = ws/wratio_dis
        dis_width = int(round(width_dis))

        hratio_dis = 1080/500
        height_dis = hs/hratio_dis
        dis_height = int(round(height_dis))

        x_dis = x-dis_width
        dis_xpos = x + (x_dis)/2

        y_dis = hs-dis_height
        dis_ypos = (y_dis)/2

        x_qr = x-qr_width
        qr_xpos = (x_qr)/2

        y_qr = hs-qr_height
        qr_ypos = (y_qr)/2
        
        #x_qr = x
        #qr_width = ws/
        

        for i in range(height):
            for j in range(width):
                if j == 1:
                    label = Label(self.root, text = Data[i],font=(None,font_size))
                    label.grid(row=i, column=j, sticky= W)
                elif j == 2:
                    label = Label(self.root, text = Units[i],font=(None,font_size))
                    label.grid(row=i,column =j,sticky = W)
                else:
                    label = Label(self.root, text = Labels[i],font=(None,font_size))
                    label.grid(row=i,column =j,sticky = W)
        # height = 8
        # width = 3



        
        self.root.geometry('%dx%d+%d+%d' % (dis_width,dis_height, dis_xpos,dis_ypos))
        self.top.geometry('%dx%d+%d+%d' % (qr_width,qr_height,qr_xpos,qr_ypos))
        # label = Label(root, text= totalData, width=150, font=(None,15))
        # label.pack()

        print('Updating...........')
        self.img = PhotoImage(file='image.png')
        self.panel.configure(image=self.img)
        self.panel.image = self.img
                
        
        self.root.after(30000,self.update)


        

root = Tk()
a = Application(root)
root.mainloop()

























