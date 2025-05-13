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
                {"text": "Price is", "style": "normal"},
                {"text": "what you", "style": "italic"},
                {"text": "pay.", "style": "italic"},
                {"text": "Value is", "style": "normal"},
                {"text": "what you", "style": "italic"},
                {"text": "get.", "style": "italic"}
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {"text": "Patience", "style": "normal"},
                {"text": "creates", "style": "italic"},
                {"text": "wealth.", "style": "italic"}
            ],
            "author": "CHARLIE MUNGER"
        },
        {
            "content": [
                {"text": "Know", "style": "normal"},
                {"text": "what you", "style": "italic"},
                {"text": "own.", "style": "italic"}
            ],
            "author": "PETER LYNCH"
        },
        {
            "content": [
                {"text": "Margin", "style": "normal"},
                {"text": "of safety.", "style": "italic"}
            ],
            "author": "BENJAMIN GRAHAM"
        },
        {
            "content": [
                {"text": "Avoid", "style": "normal"},
                {"text": "popular", "style": "italic"},
                {"text": "assets.", "style": "italic"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "Be fearful", "style": "normal"},
                {"text": "when others", "style": "italic"},
                {"text": "are greedy.", "style": "italic"}
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {"text": "Never", "style": "normal"},
                {"text": "interrupt", "style": "italic"},
                {"text": "compounding.", "style": "italic"}
            ],
            "author": "CHARLIE MUNGER"
        },
        {
            "content": [
                {"text": "Costs", "style": "normal"},
                {"text": "matter.", "style": "italic"}
            ],
            "author": "JOHN BOGLE"
        },
        {
            "content": [
                {"text": "Risk is", "style": "normal"},
                {"text": "not", "style": "italic"},
                {"text": "volatility.", "style": "italic"}
            ],
            "author": "SETH KLARMAN"
        },
        {
            "content": [
                {"text": "Stocks aren't", "style": "normal"},
                {"text": "lottery", "style": "italic"},
                {"text": "tickets.", "style": "italic"}
            ],
            "author": "PETER LYNCH"
        },
        {
            "content": [
                {"text": "Time", "style": "normal"},
                {"text": "is the", "style": "italic"},
                {"text": "friend.", "style": "italic"}
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {"text": "Heads I", "style": "normal"},
                {"text": "win,", "style": "italic"},
                {"text": "tails I", "style": "normal"},
                {"text": "don't lose.", "style": "italic"}
            ],
            "author": "MOHNISH PABRAI"
        },
        {
            "content": [
                {"text": "Price", "style": "normal"},
                {"text": "fluctuations", "style": "italic"},
                {"text": "are your", "style": "italic"},
                {"text": "friend.", "style": "italic"}
            ],
            "author": "BENJAMIN GRAHAM"
        },
        {
            "content": [
                {"text": "Buy good", "style": "normal"},
                {"text": "businesses", "style": "italic"},
                {"text": "cheap.", "style": "italic"}
            ],
            "author": "JOEL GREENBLATT"
        },
        {
            "content": [
                {"text": "Invert,", "style": "normal"},
                {"text": "always", "style": "italic"},
                {"text": "invert.", "style": "italic"}
            ],
            "author": "CHARLIE MUNGER"
        },
        {
            "content": [
                {"text": "You can't", "style": "normal"},
                {"text": "predict.", "style": "italic"},
                {"text": "Prepare.", "style": "italic"}
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {"text": "Growth and", "style": "normal"},
                {"text": "value,", "style": "italic"},
                {"text": "not versus.", "style": "italic"}
            ],
            "author": "ASWATH DAMODARAN"
        },
        {
            "content": [
                {"text": "Scuttlebutt", "style": "normal"},
                {"text": "beats", "style": "italic"},
                {"text": "statistics.", "style": "italic"}
            ],
            "author": "PHILIP FISHER"
        },
        {
            "content": [
                {"text": "Circle", "style": "normal"},
                {"text": "of competence.", "style": "italic"}
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {"text": "Diversify.", "style": "normal"},
                {"text": "Be patient.", "style": "italic"},
                {"text": "Keep costs", "style": "italic"},
                {"text": "low.", "style": "italic"}
            ],
            "author": "WALTER SCHLOSS"
        },
        {
            "content": [
                {"text": "Clone", "style": "normal"},
                {"text": "smart investors", "style": "italic"},
                {"text": "wisely.", "style": "italic"}
            ],
            "author": "GUY SPIER"
        },
        {
            "content": [
                {"text": "Opportunity", "style": "normal"},
                {"text": "lies where", "style": "italic"},
                {"text": "others fear.", "style": "italic"}
            ],
            "author": "SETH KLARMAN"
        },
        {
            "content": [
                {"text": "Buy at", "style": "normal"},
                {"text": "maximum", "style": "italic"},
                {"text": "pessimism.", "style": "italic"}
            ],
            "author": "JOHN TEMPLETON"
        },
        {
            "content": [
                {"text": "Bad news", "style": "normal"},
                {"text": "creates", "style": "italic"},
                {"text": "bargains.", "style": "italic"}
            ],
            "author": "CHRISTOPHER BROWNE"
        },
        {
            "content": [
                {"text": "Few bets,", "style": "normal"},
                {"text": "big bets,", "style": "italic"},
                {"text": "infrequent bets.", "style": "italic"}
            ],
            "author": "MONISH PABRAI"
        },
        {
            "content": [
                {"text": "Value", "style": "normal"},
                {"text": "hides in", "style": "italic"},
                {"text": "plain sight.", "style": "italic"}
            ],
            "author": "BILL MILLER"
        },
        {
            "content": [
                {"text": "Avoid", "style": "normal"},
                {"text": "permanent", "style": "italic"},
                {"text": "capital loss.", "style": "italic"}
            ],
            "author": "JEAN-MARIE EVEILLARD"
        },
        {
            "content": [
                {"text": "Patience", "style": "normal"},
                {"text": "is the", "style": "italic"},
                {"text": "key.", "style": "italic"}
            ],
            "author": "IRVING KAHN"
        },
        {
            "content": [
                {"text": "Know a", "style": "normal"},
                {"text": "few businesses", "style": "italic"},
                {"text": "exceptionally well.", "style": "italic"}
            ],
            "author": "GLENN GREENBERG"
        },
        {
            "content": [
                {"text": "Buy.", "style": "normal"},
                {"text": "Hold.", "style": "italic"},
                {"text": "And buy", "style": "italic"},
                {"text": "more.", "style": "italic"}
            ],
            "author": "SHELBY DAVIS"
        },
        {
            "content": [
                {
                    "text": "Be fearful when",
                    "style": "normal"
                },
                {
                    "text": "others are greedy",
                    "style": "italic"
                },
                {
                    "text": "and greedy when",
                    "style": "normal"
                },
                {
                    "text": "others are fearful",
                    "style": "italic"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "Rule No1: Never",
                    "style": "normal"
                },
                {
                    "text": "lose money",
                    "style": "italic"
                },
                {
                    "text": " Rule No2: Never",
                    "style": "normal"
                },
                {
                    "text": "forget Rule No1",
                    "style": "italic"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "Someone's sitting in",
                    "style": "normal"
                },
                {
                    "text": "the shade today",
                    "style": "italic"
                },
                {
                    "text": "because someone planted",
                    "style": "normal"
                },
                {
                    "text": "a tree a",
                    "style": "italic"
                },
                {
                    "text": "long time ago",
                    "style": "normal"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "Buy wonderful companies",
                    "style": "normal"
                },
                {
                    "text": "at fair prices",
                    "style": "italic"
                },
                {
                    "text": "not fair companies",
                    "style": "normal"
                },
                {
                    "text": "at wonderful prices",
                    "style": "italic"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "If past performance",
                    "style": "normal"
                },
                {
                    "text": "alone made you rich",
                    "style": "italic"
                },
                {
                    "text": "librarians would",
                    "style": "normal"
                },
                {
                    "text": "be the richest",
                    "style": "italic"
                },
                {
                    "text": "people",
                    "style": "normal"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "Diversification is",
                    "style": "normal"
                },
                {
                    "text": "protection against ignorance;",
                    "style": "italic"
                },
                {
                    "text": "it makes little sense",
                    "style": "normal"
                },
                {
                    "text": "if you know",
                    "style": "italic"
                },
                {
                    "text": "what you are doing",
                    "style": "normal"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "Wall Street is the",
                    "style": "normal"
                },
                {
                    "text": "only place where",
                    "style": "italic"
                },
                {
                    "text": "people ride in Rolls-Royces",
                    "style": "normal"
                },
                {
                    "text": "to get advice from",
                    "style": "italic"
                },
                {
                    "text": "those who take subway",
                    "style": "italic"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "When it rains gold,",
                    "style": "normal"
                },
                {
                    "text": "use a bucket,",
                    "style": "italic"
                },
                {
                    "text": "not a thimble",
                    "style": "normal"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "Why jump seven-foot",
                    "style": "normal"
                },
                {
                    "text": "bars when you",
                    "style": "italic"
                },
                {
                    "text": "can step over",
                    "style": "normal"
                },
                {
                    "text": "one-foot bars?",
                    "style": "italic"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "The stock market",
                    "style": "normal"
                },
                {
                    "text": "transfers money from",
                    "style": "italic"
                },
                {
                    "text": "the impatient to",
                    "style": "normal"
                },
                {
                    "text": "the patient",
                    "style": "italic"
                }
            ],
            "author": "WARREN BUFFETT"
        },
        {
            "content": [
                {
                    "text": "Investing without research",
                    "style": "normal"
                },
                {
                    "text": "is like playing",
                    "style": "italic"
                },
                {
                    "text": "poker and never",
                    "style": "normal"
                },
                {
                    "text": "looking at the cards",
                    "style": "italic"
                }
            ],
            "author": "PETER LYNCH"
        },
        {
            "content": [
                {
                    "text": "Even a good",
                    "style": "normal"
                },
                {
                    "text": "investor is right",
                    "style": "italic"
                },
                {
                    "text": "only 6 times",
                    "style": "normal"
                },
                {
                    "text": "out of 10",
                    "style": "italic"
                }
            ],
            "author": "PETER LYNCH"
        },
        {
            "content": [
                {
                    "text": "He who lives",
                    "style": "normal"
                },
                {
                    "text": "by the crystal",
                    "style": "italic"
                },
                {
                    "text": "ball will eat",
                    "style": "normal"
                },
                {
                    "text": "shattered glass",
                    "style": "italic"
                }
            ],
            "author": "RAY DALIO"
        },
        {
            "content": [
                {
                    "text": "If you don\u2019t",
                    "style": "normal"
                },
                {
                    "text": "own gold you",
                    "style": "italic"
                },
                {
                    "text": "know neither history",
                    "style": "normal"
                },
                {
                    "text": "nor economics",
                    "style": "italic"
                }
            ],
            "author": "RAY DALIO"
        },
        {
            "content": [
                {
                    "text": "Pain + Reflection",
                    "style": "normal"
                },
                {
                    "text": "= Progress",
                    "style": "italic"
                }
            ],
            "author": "RAY DALIO"
        },
        {
            "content": [
                {
                    "text": "The big money",
                    "style": "normal"
                },
                {
                    "text": "is not in",
                    "style": "italic"
                },
                {
                    "text": "the buying or",
                    "style": "normal"
                },
                {
                    "text": "selling but in",
                    "style": "italic"
                },
                {
                    "text": "the waiting",
                    "style": "normal"
                }
            ],
            "author": "CHARLIE MUNGER"
        },
        {
            "content": [
                {
                    "text": "Those who keep",
                    "style": "normal"
                },
                {
                    "text": "learning will keep",
                    "style": "italic"
                },
                {
                    "text": "rising in life",
                    "style": "normal"
                }
            ],
            "author": "CHARLIE MUNGER"
        },
        {
            "content": [
                {
                    "text": "Go to bed",
                    "style": "normal"
                },
                {
                    "text": "smarter than when",
                    "style": "italic"
                },
                {
                    "text": "you woke up",
                    "style": "normal"
                }
            ],
            "author": "CHARLIE MUNGER"
        },
        {
            "content": [
                {
                    "text": "Markets can stay",
                    "style": "normal"
                },
                {
                    "text": "irrational longer than",
                    "style": "italic"
                },
                {
                    "text": "you can stay",
                    "style": "normal"
                },
                {
                    "text": "solvent",
                    "style": "italic"
                }
            ],
            "author": "JOHN MAYNARD KEYNES"
        },
        {
            "content": [
                {
                    "text": "The biggest investment",
                    "style": "normal"
                },
                {
                    "text": "mistakes come not",
                    "style": "italic"
                },
                {
                    "text": "from what we",
                    "style": "normal"
                },
                {
                    "text": "know but from",
                    "style": "italic"
                },
                {
                    "text": "how we behave",
                    "style": "normal"
                }
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {
                    "text": "There are old investors",
                    "style": "normal"
                },
                {
                    "text": "and there are",
                    "style": "italic"
                },
                {
                    "text": "bold investors",
                    "style": "normal"
                },
                {
                    "text": "but there are",
                    "style": "italic"
                },
                {
                    "text": "no old bold investors",
                    "style": "normal"
                }
            ],
            "author": "HOWARD MARKS"
        },
        {
            "content": [
                {
                    "text": "Don\u2019t look for",
                    "style": "normal"
                },
                {
                    "text": "the needle in",
                    "style": "italic"
                },
                {
                    "text": "the haystack Just",
                    "style": "normal"
                },
                {
                    "text": "buy the haystack!",
                    "style": "italic"
                }
            ],
            "author": "JOHN BOGLE"
        },
        {
            "content": [
                {
                    "text": "Act like an",
                    "style": "normal"
                },
                {
                    "text": "investor not a",
                    "style": "italic"
                },
                {
                    "text": "speculator",
                    "style": "normal"
                }
            ],
            "author": "BEN GRAHAM"
        },
        {
            "content": [
                {
                    "text": "In investing what",
                    "style": "normal"
                },
                {
                    "text": "is comfortable is",
                    "style": "italic"
                },
                {
                    "text": "rarely profitable",
                    "style": "normal"
                }
            ],
            "author": "ROBERT ARNOTT"
        },
        {
            "content": [
                {
                    "text": "The market is",
                    "style": "normal"
                },
                {
                    "text": "full of people",
                    "style": "italic"
                },
                {
                    "text": "who know the",
                    "style": "normal"
                },
                {
                    "text": "price of everything",
                    "style": "italic"
                },
                {
                    "text": "but value of nothing",
                    "style": "normal"
                }
            ],
            "author": "PHILIP FISHER"
        },
        {
            "content": [
                {
                    "text": "The biggest risk",
                    "style": "normal"
                },
                {
                    "text": "of all is",
                    "style": "italic"
                },
                {
                    "text": "not taking one",
                    "style": "normal"
                }
            ],
            "author": "MELLODY HOBSON"
        },
        {
            "content": [
                {
                    "text": "Time is the",
                    "style": "normal"
                },
                {
                    "text": "friend of the",
                    "style": "italic"
                },
                {
                    "text": "wonderful business the",
                    "style": "normal"
                },
                {
                    "text": "enemy of the",
                    "style": "italic"
                },
                {
                    "text": "mediocre",
                    "style": "normal"
                }
            ],
            "author": "WARREN BUFFETT"
        }
    ]

    font_regular = "fonts/PlayfairDisplay-Regular.ttf"   # Path to your regular TTF font
    font_italic = "fonts/PlayfairDisplay-Italic.ttf"     # Path to your italic TTF font
    audio_path = "audio/rain.mp3"                        # Optional: set to None if no audio

    i = 56
    for quote_data in quotes_data[56:]:
        output_path = f"video_posts/quote_video_{i}.mp4"
        generate_quote_video(quote_data, font_regular, font_italic, audio_path, output_path)
        i += 1
