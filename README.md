# MemeGineer: Meme Generator with Deepfake Face Swapping

![Basic use case](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExczR3b3Y3ZHdjbTVyb2lsYXkxaHV6d2UxMmlsam1wd3c0Y3hiN2F2ZSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/JC5Ug9Zl02Kj6xunis/giphy.gif)

## Overview

MemeGineer is a meme generator that integrates deepfake face-swapping. Built during the **LauzHack Deepfake Sprint Hackathon** in **less than 7 hours**, this project allows users to select meme templates, upload face images, and generate custom memes with swapped faces. You are completely free to use it for fun and entertainment purposes.

## Features

- **Meme Template Selection**: Scrollable gallery of popular meme templates.
- **Face Upload**: Upload an image of a face to be swapped into the meme.
- **Customizable Text**: Add top and bottom text with automatic wrapping.
- **Deepfake Face Swapping**: Face swapping powered by external APIs.
- **Meme Saving**: Save the generated meme locally.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-repository-url/memegineer.git
    cd memegineer
    ```

2. Install the required libraries:

    ```bash
    pip install -r requirements.txt
    ```

3. Set up the `.env` file with your API keys:

    ```
    FACE_SWAP_API_KEY=your_face_swap_api_key
    IMGBB_API_KEY=your_imgbb_api_key
    ```

4. Run the app:

    ```bash
    python memegineer.py
    ```

## Usage

1. **Select a template** from the gallery.
2. **Upload a face image**.
3. **Add top and bottom text**.
4. **Click "Generate Meme"** to swap the face and generate the meme.
5. **Save the meme** if desired.

### Team members:
- **Karlo Vrancic** (kvrancic11@gmail.com)
- **Mathieu Pardoux** (mathieu.pardoux@epfl.ch)
- **Dylan Callahan** (dylan.callahan@epfl.ch)

## Commit History

See the full commit history [here](https://github.com/kvrancic/memegineer/commits/main/).

## Contact

For inquiries or further development, contact **Karlo Vrancic** at kvrancic11@gmail.com.
