import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip, AudioFileClip
from typing import List, Dict
import tempfile

# Constants
WIDTH, HEIGHT = 1080, 1920
FPS = 30
FONT_SIZE = 70
AUTHOR_FONT_SIZE = 40
LINE_SPACING = 100  # Space between quote lines
BOTTOM_MARGIN = 200  # Space below quote block


def get_centered_position(draw, text, font, y):
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    return ((WIDTH - w) // 2, y)


def split_quote_lines(quote_data: Dict):
    lines = []
    for part in quote_data["content"]:
        text = part["text"]
        style = part["style"]
        lines.append({"text": text, "style": style})
    return lines


def create_typewriter_frames(quote_data: Dict, font_regular: str, font_italic: str, duration: float) -> List[np.ndarray]:
    lines = split_quote_lines(quote_data)
    total_chars = sum(len(line["text"]) for line in lines)
    
    # Calculate frames for typewriter effect and author display
    typewriter_duration = duration  # 7 seconds for typewriter effect
    total_duration = typewriter_duration + 3  # Add 3 extra seconds for author display
    
    typewriter_frames = int(FPS * typewriter_duration)
    total_frames = int(FPS * total_duration)
    
    # Calculate characters per frame to spread across the typewriter duration
    char_per_frame = total_chars / typewriter_frames
    
    regular_font = ImageFont.truetype(font_regular, FONT_SIZE)
    italic_font = ImageFont.truetype(font_italic, FONT_SIZE)
    author_font = ImageFont.truetype(font_regular, AUTHOR_FONT_SIZE)

    frames = []
    current_char_count = 0
    current_visible_chars = 0

    for frame_idx in range(total_frames):
        img = Image.new("RGB", (WIDTH, HEIGHT), color="black")
        draw = ImageDraw.Draw(img)

        y = (HEIGHT - (len(lines) * LINE_SPACING + BOTTOM_MARGIN)) // 2
        char_count_tracker = 0

        # Only update character count if we're still in the typewriter phase
        if frame_idx < typewriter_frames:
            current_char_count += char_per_frame
            current_visible_chars = min(int(current_char_count), total_chars)  # Cap at total chars
        else:
            current_visible_chars = total_chars  # Show all text after typewriter phase

        # Draw the quote text
        for line in lines:
            text = line["text"]
            style = line["style"]
            font = italic_font if style == "italic" else regular_font

            if char_count_tracker + len(text) <= current_visible_chars:
                draw.text(get_centered_position(draw, text, font, y), text, font=font, fill="white")
                char_count_tracker += len(text)
            else:
                visible_chars = max(0, current_visible_chars - char_count_tracker)
                partial_text = text[:visible_chars]
                draw.text(get_centered_position(draw, partial_text, font, y), partial_text, font=font, fill="white")
                char_count_tracker += visible_chars
                break

            y += LINE_SPACING

        # Add divider and author ONLY after typewriter effect is complete
        if frame_idx >= typewriter_frames:
            # Calculate y position after the last line of text
            final_y = (HEIGHT - (len(lines) * LINE_SPACING + BOTTOM_MARGIN)) // 2 + len(lines) * LINE_SPACING
            
            divider_y = final_y + 40
            author_y = divider_y + 30

            divider_width = 100
            draw.line(((WIDTH - divider_width) // 2, divider_y,
                      (WIDTH + divider_width) // 2, divider_y),
                      fill="white", width=2)

            author_text = quote_data.get("author", "").upper()
            bbox = draw.textbbox((0, 0), author_text, font=author_font)
            w_author = bbox[2] - bbox[0]
            draw.text(((WIDTH - w_author) // 2, author_y), author_text, font=author_font, fill="white")

        frame_np = np.array(img)
        frame_cv = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)
        frames.append(frame_cv)

    return frames


def generate_quote_video(quote_data: Dict, font_regular: str, font_italic: str,
                         audio_path: str, output_path: str):
    # Set fixed duration to 7 seconds for the typewriter effect
    duration = 7.0

    frames = create_typewriter_frames(quote_data, font_regular, font_italic, duration)

    with tempfile.TemporaryDirectory() as tmpdir:
        clip = ImageSequenceClip(frames, fps=FPS)
        if audio_path:
            audio = AudioFileClip(audio_path).subclip(0, clip.duration)
            clip = clip.set_audio(audio)
        clip.write_videofile(output_path, codec="libx264", audio_codec="aac")


# Example usage
if __name__ == "__main__":
    quotes_data = [
        {
            "content": [
                {"text": "Successful investing", "style": "normal"},
                {"text": "requires second-level", "style": "italic"},
                {"text": "thinking that is", "style": "normal"},
                {"text": "different and", "style": "italic"},
                {"text": "better than others", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "The biggest", "style": "normal"},
                {"text": "investing errors", "style": "italic"},
                {"text": "come not from", "style": "normal"},
                {"text": "informational factors", "style": "italic"},
                {"text": "but psychological ones", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "Rule number one", "style": "normal"},
                {"text": "is that most", "style": "italic"},
                {"text": "things will", "style": "normal"},
                {"text": "eventually prove", "style": "italic"},
                {"text": "highly cyclical", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "You must buy", "style": "normal"},
                {"text": "when others", "style": "italic"},
                {"text": "are selling and", "style": "normal"},
                {"text": "sell when", "style": "italic"},
                {"text": "others buy", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "An asset bought", "style": "normal"},
                {"text": "at a cheap", "style": "italic"},
                {"text": "price can be", "style": "normal"},
                {"text": "a great", "style": "italic"},
                {"text": "investment", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "Outstanding investors", "style": "normal"},
                {"text": "are distinguished", "style": "italic"},
                {"text": "as much by", "style": "normal"},
                {"text": "their ability to", "style": "italic"},
                {"text": "control risk", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "To achieve", "style": "normal"},
                {"text": "superior results", "style": "italic"},
                {"text": "you must hold", "style": "normal"},
                {"text": "non-consensus views", "style": "italic"},
                {"text": "regarding asset value", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "We cannot", "style": "normal"},
                {"text": "predict the future", "style": "italic"},
                {"text": "of the market", "style": "normal"},
                {"text": "but we can", "style": "italic"},
                {"text": "prepare", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "A large margin", "style": "normal"},
                {"text": "of safety allows", "style": "italic"},
                {"text": "you to withstand", "style": "normal"},
                {"text": "being completely", "style": "italic"},
                {"text": "wrong", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "Great investing", "style": "normal"},
                {"text": "requires both", "style": "italic"},
                {"text": "generating returns and", "style": "normal"},
                {"text": "controlling risk in", "style": "italic"},
                {"text": "equal measure", "style": "normal"}
            ],
            "author": "HOWARD MARKS"
        }
    ]

    font_regular = "fonts/PlayfairDisplay-Regular.ttf"   # Path to your regular TTF font
    font_italic = "fonts/PlayfairDisplay-Italic.ttf"     # Path to your italic TTF font
    audio_path = "audio/rain.mp3"                        # Optional: set to None if no audio

    i = 101 # total 100 already created.. Need to start from 101. 
    # check https://docs.google.com/spreadsheets/d/1PMN3NfaTOj9ezEy7xAJMxnyQFoQZq79erzk-C9OSEOg/edit?gid=0#gid=0
    # books in iteration next 
    # 1. "Security Analysis" by Benjamin Graham and David Dodd
    # 2. "Common Stocks and Uncommon Profits" by Philip Fisher
    # 3. "Margin of Safety" by Seth Klarman
    # 4. "One Up On Wall Street" by Peter Lynch
    # 5. "Poor Charlie’s Almanack" edited by Peter Kaufman
    # 6. "The Dhandho Investor" by Mohnish Pabrai
    for quote_data in quotes_data:
        output_path = f"video_posts/quote_video_{i}.mp4"
        generate_quote_video(quote_data, font_regular, font_italic, audio_path, output_path)
        i += 1
