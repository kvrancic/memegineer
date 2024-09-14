import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dotenv import load_dotenv
from PIL import Image, ImageTk, ImageDraw, ImageFont
import base64
import os
import requests
import io
import time
import textwrap

load_dotenv()


class MemeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MemeGineer")

        # Initialize variables
        self.face_img_path = None
        self.template_images = []
        self.selected_template = None

        # Load meme templates
        self.load_templates()

        # Create UI components
        self.create_widgets()

        # API Keys
        self.face_swap_api_key = os.getenv("FACE_SWAP_API_KEY")
        self.imgbb_api_key = os.getenv("IMGBB_API_KEY")

    def load_templates(self):
        # Assuming meme templates are stored in a folder named 'templates'
        template_folder = 'templates'
        self.template_images = []
        for filename in os.listdir(template_folder):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                self.template_images.append(os.path.join(template_folder, filename))

    def create_widgets(self):

        # Face Upload Label
        self.face_upload_label = tk.Label(self.root, text="Upload a picture for face swapping", fg="grey")
        self.face_upload_label.pack()

        # Face Image Upload
        self.face_upload_button = tk.Button(self.root, text="Upload Face Image", command=self.upload_face_image)
        self.face_upload_button.pack(pady=2)

        # Face Image Preview
        self.face_preview_label = tk.Label(self.root)
        self.face_preview_label.pack(pady=2)

        # Meme Template Gallery Label
        self.gallery_label = tk.Label(self.root, text="Template Gallery", fg="grey")
        self.gallery_label.pack()

        # Meme Template Gallery
        self.gallery_frame = tk.Frame(self.root)
        self.gallery_frame.pack(pady=2)

        self.canvas = tk.Canvas(self.gallery_frame, width=500, height=120, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.gallery_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)

        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="bottom", fill="x")

        # Load templates into gallery
        self.load_gallery()

        # Canvas to show selected template and result
        self.image_canvas = tk.Canvas(self.root, bg="gray", highlightthickness=0)
        self.image_canvas.pack(pady=10)

        # Text input fields
        self.top_text_label = tk.Label(self.root, text="Top Text")
        self.top_text_label.pack()
        self.top_text_entry = tk.Entry(self.root, width=60)
        self.top_text_entry.pack()

        self.bottom_text_label = tk.Label(self.root, text="Bottom Text")
        self.bottom_text_label.pack()
        self.bottom_text_entry = tk.Entry(self.root, width=60)
        self.bottom_text_entry.pack()

        # Buttons Frame
        self.buttons_frame = tk.Frame(self.root)
        self.buttons_frame.pack(pady=10)

        # Generate meme button
        self.generate_button = tk.Button(self.buttons_frame, text="Generate Meme", command=self.generate_meme)
        self.generate_button.pack(side=tk.LEFT, padx=5)

        # Save Meme Button
        self.save_button = tk.Button(self.buttons_frame, text="Save Meme", command=self.save_meme, state=tk.DISABLED)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Status Message Label
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=5)

        # Progress Bar (Spinner)
        self.progress = ttk.Progressbar(self.root, orient=tk.HORIZONTAL, mode='indeterminate')

    def load_gallery(self):
        for idx, img_path in enumerate(self.template_images):
            img = Image.open(img_path)
            img.thumbnail((100, 100))
            tk_img = ImageTk.PhotoImage(img)
            label = tk.Label(self.scrollable_frame, image=tk_img, cursor="hand2")
            label.image = tk_img  # Keep a reference
            label.grid(row=0, column=idx, padx=5)
            label.bind("<Button-1>", lambda e, idx=idx: self.select_template(idx))

    def select_template(self, idx):
        self.selected_template = self.template_images[idx]
        self.display_template()

    def display_template(self):
        if self.selected_template:
            self.template_image = Image.open(self.selected_template)
            # Maintain aspect ratio with height locked to 350 pixels
            width, height = self.template_image.size
            new_height = 350
            new_width = int(width * (new_height / height))
            self.template_image = self.template_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            self.tk_template_image = ImageTk.PhotoImage(self.template_image)
            self.image_canvas.config(width=new_width, height=new_height)
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_template_image)

    def upload_face_image(self):
        self.face_img_path = filedialog.askopenfilename()
        if self.face_img_path:
            # Display the face image preview
            face_image = Image.open(self.face_img_path)
            face_image.thumbnail((100, 100))
            self.tk_face_image = ImageTk.PhotoImage(face_image)
            self.face_preview_label.config(image=self.tk_face_image)
            messagebox.showinfo("Face Image Selected", "Face image selected successfully.")

    def generate_meme(self):
        if not self.selected_template:
            messagebox.showwarning("No Template Selected", "Please select a meme template.")
            return

        if not self.face_img_path:
            messagebox.showwarning("No Face Image", "Please upload a face image.")
            return

        # Disable the generate button to prevent multiple clicks
        self.generate_button.config(state=tk.DISABLED)
        self.save_button.config(state=tk.DISABLED)
        self.status_label.config(text="Processing face swap, please wait...")
        self.progress.pack(pady=5)
        self.progress.start()
        self.root.update_idletasks()

        try:
            # Perform face swap
            swapped_image = self.face_swap()

            if swapped_image is None:
                messagebox.showerror("Face Swap Failed", "Face swapping failed.")
                self.generate_button.config(state=tk.NORMAL)
                self.progress.stop()
                self.progress.pack_forget()
                self.status_label.config(text="")
                return

            top_text = self.top_text_entry.get().upper()
            bottom_text = self.bottom_text_entry.get().upper()

            # Prepare the image
            img = swapped_image.copy()
            draw = ImageDraw.Draw(img)

            # Load font
            font = ImageFont.truetype("impact.ttf", 40)

            # Adjust wrap width based on image width
            wrap_width = int(img.width / 15)

            # Wrap and center text
            def wrap_text(text):
                return "\n".join(textwrap.wrap(text, width=wrap_width))

            top_text_wrapped = wrap_text(top_text)
            bottom_text_wrapped = wrap_text(bottom_text)

            # Draw top text
            self.draw_centered_text(draw, img.width, img.height, top_text_wrapped, font, position='top')

            # Draw bottom text
            self.draw_centered_text(draw, img.width, img.height, bottom_text_wrapped, font, position='bottom')

            # Show updated image with text
            self.image_with_text = img
            self.tk_image_with_text = ImageTk.PhotoImage(img)
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image_with_text)

            # Re-enable buttons
            self.generate_button.config(state=tk.NORMAL)
            self.save_button.config(state=tk.NORMAL)
            self.progress.stop()
            self.progress.pack_forget()
            self.status_label.config(text="Meme generated successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.generate_button.config(state=tk.NORMAL)
            self.progress.stop()
            self.progress.pack_forget()
            self.status_label.config(text="")

    def save_meme(self):
        if hasattr(self, 'image_with_text'):
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
            if file_path:
                self.image_with_text.save(file_path)
                messagebox.showinfo("Meme Saved", "Your meme has been saved successfully.")
        else:
            messagebox.showwarning("No Meme", "There is no meme to save.")

    def face_swap(self):
        # Upload images to ImgBB to get URLs
        template_url = self.upload_image_to_imgbb(self.selected_template)
        face_url = self.upload_image_to_imgbb(self.face_img_path)

        if not template_url or not face_url:
            return None

        # Call the face-swapping API
        swap_result_url = self.call_face_swap_api(template_url, face_url)

        if not swap_result_url:
            return None

        # Download the swapped image
        response = requests.get(swap_result_url)
        swapped_image = Image.open(io.BytesIO(response.content))
        # Resize maintaining aspect ratio
        width, height = swapped_image.size
        new_height = 350
        new_width = int(width * (new_height / height))
        swapped_image = swapped_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.image_canvas.config(width=new_width, height=new_height)
        return swapped_image

    def upload_image_to_imgbb(self, image_path):
        url = "https://api.imgbb.com/1/upload"
        with open(image_path, "rb") as file:
            payload = {
                "key": self.imgbb_api_key,
                "image": base64.b64encode(file.read()),
            }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            data = response.json()
            return data["data"]["url"]
        else:
            messagebox.showerror("ImgBB Upload Failed", "Failed to upload image to ImgBB.")
            return None

    def call_face_swap_api(self, target_url, swap_url):
        # Face-swapping API endpoint
        url = "https://api.magicapi.dev/api/v1/capix/faceswap/faceswap/v1/image"

        headers = {
            "accept": "application/json",
            "x-magicapi-key": self.face_swap_api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "target_url": target_url,
            "swap_url": swap_url,
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            result = response.json()
            # Access the nested 'request_id'
            request_id = result.get("image_process_response", {}).get("request_id")
            if request_id:
                # Poll for result
                return self.retrieve_face_swap_result(request_id)
            else:
                messagebox.showerror("Face Swap Error", "No request ID received.")
                return None
        else:
            messagebox.showerror("Face Swap API Error", f"Status Code: {response.status_code}")
            return None

    def retrieve_face_swap_result(self, request_id):
        url = "https://api.magicapi.dev/api/v1/capix/faceswap/result/"

        headers = {
            "accept": "application/json",
            "x-magicapi-key": self.face_swap_api_key,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "request_id": request_id,
        }

        # Polling the API until the result is ready
        for _ in range(10):
            time.sleep(5)
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                result = response.json()
                status = result.get("image_process_response", {}).get("status")
                if status == "OK":
                    result_url = result.get("image_process_response", {}).get("result_url")
                    return result_url
                elif status == "InProgress":
                    self.status_label.config(text="Face swap in progress...")
                    self.root.update_idletasks()
                    time.sleep(5)  # Wait before retrying
                else:
                    messagebox.showerror("Face Swap Failed", f"Status: {status}")
                    return None
            else:
                messagebox.showerror("Result API Error", f"Status Code: {response.status_code}")
                return None
        messagebox.showerror("Timeout", "Face swap result not available in time.")
        return None

    def draw_centered_text(self, draw, img_width, img_height, text, font, position='top'):
        # Calculate line height using textbbox
        bbox = draw.textbbox((0, 0), 'A', font=font)
        line_height = bbox[3] - bbox[1]
        lines = text.split('\n')
        total_text_height = line_height * len(lines)

        if position == 'top':
            y_text = 10
        elif position == 'bottom':
            y_text = img_height - total_text_height - 40
        else:
            y_text = (img_height - total_text_height) / 2

        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x_text = (img_width - text_width) / 2
            draw.text((x_text, y_text), line, font=font, fill="white", stroke_width=2, stroke_fill="black")
            y_text += line_height

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MemeGeneratorApp(root)
    root.mainloop()
