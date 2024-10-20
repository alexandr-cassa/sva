import cv2
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.uix.label import Label


class CameraApp(App):
    def build(self):

        layout = BoxLayout(orientation='vertical')

        # Create the main layout
        up_layout = BoxLayout(orientation='horizontal')

        save_photos_layout_right = BoxLayout(orientation='horizontal')
        save_photos_layout_left = BoxLayout(orientation='horizontal')

        #Original screen
        self.original_saved = Image()
        save_photos_layout_right.add_widget(self.original_saved)

        #Red screen
        self.red_saved = Image()
        save_photos_layout_right.add_widget(self.red_saved)

        #Green screen
        self.green_saved = Image()
        save_photos_layout_left.add_widget(self.green_saved)

        #Blue screen
        self.blue_saved = Image()
        save_photos_layout_left.add_widget(self.blue_saved)

        save_photos_layout = BoxLayout(orientation='vertical')
        save_photos_layout.add_widget(save_photos_layout_right)
        save_photos_layout.add_widget(save_photos_layout_left)

        # Left side: Camera stream
        down_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))

        # Add an Image widget to display the camera feed
        self.img = Image()
        up_layout.add_widget(self.img)

        start_button = Button(text="Start Camera")
        start_button.bind(on_press=self.start_camera)
        down_layout.add_widget(start_button)

        stop_button = Button(text="Stop Camera")
        stop_button.bind(on_press=self.stop_camera)
        down_layout.add_widget(stop_button)

        save_button = Button(text="Save Frame")
        save_button.bind(on_press=self.save_frame)
        down_layout.add_widget(save_button)

        # Add an Image widget to display the saved frame
        up_layout.add_widget(save_photos_layout)


        # Add both the left and right layouts to the main layout
        layout.add_widget(up_layout)
        layout.add_widget(down_layout)

        # Initialize camera capture object
        self.capture = None
        self.streaming = False

        return layout

    def start_camera(self, *args):
        if self.capture is None:
            self.capture = cv2.VideoCapture(0)  # Open the default camera
        if not self.streaming:
            self.streaming = True
            Clock.schedule_interval(self.update_frame, 1.0/30.0)  # Update at 30 FPS

    def stop_camera(self, *args):
        if self.streaming:
            self.streaming = False
            Clock.unschedule(self.update_frame)

    def update_frame(self, dt):
        ret, frame = self.capture.read()
        if ret:
            # Convert the frame to a Kivy-compatible texture
            buffer = cv2.flip(frame, 0).tobytes()
            texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
            texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')

            # Update the Image widget with the new texture
            self.img.texture = texture

    def create_texture(self, frame):
        buffer = cv2.flip(frame, 0).tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')

        return texture



    def save_frame(self, *args):
        if self.capture:
            ret, frame = self.capture.read()
            if ret:
                # Save the frame as an image file
                filename = "saved_frame.jpg"
                cv2.imwrite(filename, frame)
                print("Frame saved as 'saved_frame.jpg'")

                # Update the saved image widget with the new texture
                my_frame = frame.copy()
                for i in range(0, 3):
                    my_frame[:,:, i] = 255 - my_frame[:,:, i]

                self.original_saved.texture = self.create_texture(my_frame)

                h, w, chn = frame.shape

                red_list = [0]*256
                green_list = [0]*256
                blue_list = [0]*256

                for y in range(h):
                    for x in range(w):
                        pixel = frame[y, x]

                        red_list[pixel[2]] += 1
                        green_list[pixel[1]] += 1
                        blue_list[pixel[0]] += 1

                print("R " + str(max(red_list)) + " -> " + str(red_list.index(max(red_list))))
                print("G " + str(max(green_list)) + " -> " + str(green_list.index(max(green_list))))
                print("B " + str(max(blue_list)) + " -> " + str(blue_list.index(max(blue_list))))

                red_frame = frame.copy()
                red_frame[:,:, 0] = 0
                red_frame[:,:, 1] = 0
                self.red_saved.texture = self.create_texture(red_frame)

                green_frame = frame.copy()
                green_frame[:,:, 0] = 0
                green_frame[:,:, 2] = 0
                self.green_saved.texture = self.create_texture(green_frame)

                blue_frame = frame.copy()
                blue_frame[:,:, 1] = 0
                blue_frame[:,:, 2] = 0
                self.blue_saved.texture = self.create_texture(blue_frame)

    def on_stop(self):
        # Release the camera when the app is closed
        if self.capture:
            self.capture.release()

def calculate_histo(frame):
    rmax = 0
    gmax = 0
    bmax = 0


    print(frame)

    return rmax, gmax, bmax

# Run the app
if __name__ == '__main__':
    CameraApp().run()

