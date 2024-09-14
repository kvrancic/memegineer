import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import requests
import io
import time
import textwrap




class MemeGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MemeMorph: Meme Generator")

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
        # Face Image Upload
        self.face_upload_button = tk.Button(self.root, text="Upload Face Image", command=self.upload_face_image)
        self.face_upload_button.pack(pady=5)

        # Meme Template Gallery
        self.gallery_frame = tk.Frame(self.root)
        self.gallery_frame.pack(pady=5)

        self.canvas = tk.Canvas(self.gallery_frame, width=500, height=120)
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
        self.image_canvas = tk.Canvas(self.root, width=500, height=500, bg="gray")
        self.image_canvas.pack()

        # Text input fields
        self.top_text_label = tk.Label(self.root, text="Top Text")
        self.top_text_label.pack()
        self.top_text_entry = tk.Entry(self.root, width=60)
        self.top_text_entry.pack()

        self.bottom_text_label = tk.Label(self.root, text="Bottom Text")
        self.bottom_text_label.pack()
        self.bottom_text_entry = tk.Entry(self.root, width=60)
        self.bottom_text_entry.pack()

        # Generate meme button
        self.generate_button = tk.Button(self.root, text="Generate Meme", command=self.generate_meme)
        self.generate_button.pack(pady=10)

    def load_gallery(self):
        for idx, img_path in enumerate(self.template_images):
            img = Image.open(img_path)
            img.thumbnail((100, 100))
            tk_img = ImageTk.PhotoImage(img)
            label = tk.Label(self.scrollable_frame, image=tk_img)
            label.image = tk_img  # Keep a reference
            label.grid(row=0, column=idx, padx=5)
            label.bind("<Button-1>", lambda e, idx=idx: self.select_template(idx))

    def select_template(self, idx):
        self.selected_template = self.template_images[idx]
        self.display_template()

    def display_template(self):
        if self.selected_template:
            self.template_image = Image.open(self.selected_template)
            self.template_image = self.template_image.resize((500, 500), Image.Resampling.LANCZOS)
            self.tk_template_image = ImageTk.PhotoImage(self.template_image)
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_template_image)

    def upload_face_image(self):
        self.face_img_path = filedialog.askopenfilename()
        if self.face_img_path:
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
        self.root.update_idletasks()

        try:
            # Perform face swap
            swapped_image = self.face_swap()

            if swapped_image is None:
                messagebox.showerror("Face Swap Failed", "Face swapping failed.")
                self.generate_button.config(state=tk.NORMAL)
                return

            top_text = self.top_text_entry.get().upper()
            bottom_text = self.bottom_text_entry.get().upper()

            # Prepare the image
            img = swapped_image.copy()
            draw = ImageDraw.Draw(img)

            # Load font
            font = ImageFont.truetype("impact.ttf", 40)

            # Wrap and center text
            def wrap_text(text, width):
                return "\n".join(textwrap.wrap(text, width=20))

            top_text_wrapped = wrap_text(top_text, 20)
            bottom_text_wrapped = wrap_text(bottom_text, 20)

            # Draw top text
            self.draw_centered_text(draw, img.width, img.height, top_text_wrapped, font, position='top')

            # Draw bottom text
            self.draw_centered_text(draw, img.width, img.height, bottom_text_wrapped, font, position='bottom')

            # Show updated image with text
            self.image_with_text = img
            self.tk_image_with_text = ImageTk.PhotoImage(img)
            self.image_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image_with_text)

            # Re-enable the generate button
            self.generate_button.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.generate_button.config(state=tk.NORMAL)

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
        swapped_image = swapped_image.resize((500, 500), Image.Resampling.LANCZOS)
        return swapped_image

    def upload_image_to_imgbb(self, image_path):
        url = "https://api.imgbb.com/1/upload"
        with open(image_path, "rb") as file:
            payload = {
                "key": self.imgbb_api_key,
                "image": file.read(),
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
            request_id = result.get("request_id")
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
            response = requests.post(url, headers=headers, data=data)
            if response.status_code == 200:
                result = response.json()
                status = result.get("status")
                if status == "succeeded":
                    result_url = result.get("result_url")
                    return result_url
                elif status == "pending":
                    time.sleep(2)  # Wait before retrying
                else:
                    messagebox.showerror("Face Swap Failed", f"Status: {status}")
                    return None
            else:
                messagebox.showerror("Result API Error", f"Status Code: {response.status_code}")
                return None
        messagebox.showerror("Timeout", "Face swap result not available in time.")
        return None

    def draw_centered_text(self, draw, img_width, img_height, text, font, position='top'):
        # Calculate text size
        lines = text.split('\n')
        line_height = font.getsize('A')[1]
        total_text_height = line_height * len(lines)

        if position == 'top':
            y_text = 10
        elif position == 'bottom':
            y_text = img_height - total_text_height - 10
        else:
            y_text = (img_height - total_text_height) / 2

        for line in lines:
            text_width, _ = draw.textsize(line, font=font)
            x_text = (img_width - text_width) / 2
            draw.text((x_text, y_text), line, font=font, fill="white", stroke_width=2, stroke_fill="black")
            y_text += line_height

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = MemeGeneratorApp(root)
    root.mainloop()
