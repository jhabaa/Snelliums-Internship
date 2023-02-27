import json
import time
import tkinter
import cv2 as cv2
import customtkinter
import requests
import numpy as np
import threading
from PIL import Image, ImageTk

"""
+++++++++++++++++++++++++++++++++++
Parameters:
"""
server_address = "http://90.90.0.176:8080/cameras"
#camera_id = 'virtual-3'

"""
+++++++++++++++++++++++++++++++++++
Interface creation
==================
"""
#customtkinter.set_appearance_mode("dark")
#customtkinter.set_default_color_theme("green")

#app = customtkinter.CTk()
#app.geometry("1000x1000")


i = 0


#Class for asynchronous image acquisition
class AsyncImageAcquisition(threading.Thread):
    def __init__(self, camera_id, parent):
        threading.Thread.__init__(self) # make super ?
        print("Creating thread for camera: " + str(camera_id))
        self.parent = parent
        self.camera_id = camera_id
        #self.trigger_source = "TRIGGER_SOURCE_SOFTWARE"
        self.infos = requests.get(server_address + f"/{self.camera_id}/info").json()
        
        print(self.infos)
        #self.canvas_dict = canvas_dict
        self.running = True
        #Add canvas to the frame in app
       # self.canvas = tkinter.Canvas(app, width=300, height=300)
        #self.canvas.pack()
        #self.thread = threading.Thread(target=self.run, args=())


    def run(self):
        print("Starting thread for camera: " + str(self.camera_id))
        params = json.dumps({"perform-auto-adjustment": False})
        response = requests.post(server_address + f"/{self.camera_id}" + f"/start-continuous-image-acquisition", headers={"Content-Type": "application/json"}, data=params, stream=True)
        #self.running = True if response.status_code == 200 else False
        
        while self.running:
            responseImage = requests.get(server_address + f"/{self.camera_id}" + f"/last-image")
            if cv2.waitKey(1) & 0xFF == ord('p'):
                    print("Taking picture")
                    self.takePicture()
            #Quit if q is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                response.close()    
                self.stop()

                break
            #print("OK")
            img1 = np.frombuffer(bytearray(responseImage.content), dtype="uint8")
            self.img = cv2.imdecode(img1, cv2.COLOR_GRAY2BGR)
            self.img = cv2.resize(self.img, (300, 300))
            #print id camera in the image
            cv2.putText(self.img, self.camera_id, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            self.lastImage = Image.fromarray(self.img)
            self.lastImage = ImageTk.PhotoImage(self.lastImage)
            self.canvas = tkinter.Canvas(self.parent, width=300, height=300)
            self.canvas.pack()

                

    def stop(self):
        self.running = False
        self.stop()
        #self.thread.join()
        print("Stopping thread for camera: " + str(self.camera_id))
    
    def takePicture(self):
        #Save image in the pictures folder
        cv2.imwrite("pictures/" + self.camera_id + ".jpg", self.img)



#class Applicattion
class Application(customtkinter.CTkFrame):
    def __init__(self,cameras, master):
        super().__init__(master)
        self.cameras = cameras
        self.camera_threads = []
        self.create_widgets()
        


    def create_widgets(self):
        #create frame 1
        self.frame1 = customtkinter.CTkFrame(self.master)
        self.frame1.pack(side=tkinter.LEFT, padx=10, pady=10)
        #create frame 2
        self.frame2 = customtkinter.CTkFrame(self.master)
        self.frame2.pack(side=tkinter.RIGHT, padx=10, pady=10)

        #Set cameras in frames
        for i, camera in enumerate(self.cameras):
            if i%2 == 0:
                parent = self.frame1
            else:
                parent = self.frame2
            #Create canvas for each camera
            label = customtkinter.CTkLabel(parent, text=camera["device-id"])
            label.pack()

            camera_thread = AsyncImageAcquisition(camera["device-id"], parent)
            self.camera_threads.append(camera_thread)

        #button to start camera
        start_button = customtkinter.CTkButton(self.master, text="Start", command=self.start_threads)
        start_button.pack()

        #button to stop camera
        stop_button = customtkinter.CTkButton(self.master, text="Stop", command=self.stop_threads)
        stop_button.pack(padx=10, pady=10)

        #button to toggle trigger source
        toggle_button = customtkinter.CTkButton(self.master, text = "Software" if self.camera_threads[0].infos["parameters"]["trigger-source"]["value"] == "software" else "Hardware", command=self.toggle_trigger_source)
        toggle_button.pack(padx=10, pady=10)



    def start_threads(self):
        for thread in self.camera_threads:
            thread.start()
    
    def stop_threads(self):
        for thread in self.camera_threads:
            thread.running = False
            thread.stop()
           
    
    def toggle_trigger_source(self):
        print(self.camera_threads[0].infos["parameters"]["trigger-source"]["value"] + " trigger source")
        #self.camera_threads[0].infos["parameters"]["trigger-source"]["value"] = "hardware"
        data = {
            'parameters': {
                #'trigger-mode-enabled':False
                #'frame-rate': 5.0
                'trigger-source': "hardware"
            }

        }

        for thread in self.camera_threads:
            #thread.infos["parameters"]["trigger-source"]["value"] = "software" if thread.infos["parameters"]["trigger-source"]["value"] == "hardware" else "hardware"
            receive = requests.post(server_address + f"/{thread.camera_id}" + f"/update-parameters", headers={"Content-Type": "application/json"}, data=json.dumps(data))
            print("Trigger source changed to " + str(thread.infos["parameters"]["trigger-source"]["value"] + " for camera ") + str(thread.camera_id) if receive.status_code == 200 else "Error changing trigger source for camera " + str(thread.camera_id))
            #print server response
            print(receive.text)

#Create a thread for each camera
"""
for camera in cameras:
    thread = AsyncImageAcquisition(camera["device-id"], canvas_dict)
    thread.start()
"""

def main():
    app = customtkinter.CTk()
    app.geometry("1000x1000")
    app.title("Camera")
    #Get camera list
    camera_list = requests.get(server_address+"-list")
    cameras = json.loads(camera_list.text)
    print(cameras)
    root = Application(master=app, cameras=cameras)
    root.mainloop()

if __name__ == "__main__":
    main()



