from PIL import Image, ImageDraw, ImageFont
import json
import os

def create_quote_image(quote_data, width=1080, height=1350, output_filename='quote_image.png'):
    """
    Creates an image with a black background and centered text based on input JSON,
    making better use of vertical space.
    
    Args:
        quote_data (dict): Dictionary containing quote content and author
        width (int): The width of the image in pixels
        height (int): The height of the image in pixels
        output_filename (str): The name of the output file
    
    Returns:
        None: The image is saved to disk
    """
    # Create a new black image with the specified dimensions
    img = Image.new('RGB', (width, height), color='black')
    draw = ImageDraw.Draw(img)
    
    # Load fonts - replace these paths with your actual font file paths
    try:
        # Try to load custom fonts if they exist
        regular_font_path = "fonts/PlayfairDisplay-Regular.ttf"
        italic_font_path = "fonts/PlayfairDisplay-Italic.ttf"
        author_font_path = "fonts/PlayfairDisplay-Regular.ttf"
        
        # Check if font files exist, otherwise use default
        if not os.path.exists(regular_font_path):
            print(f"Warning: Font file {regular_font_path} not found. Using default.")
            regular_font_path = None
        if not os.path.exists(italic_font_path):
            print(f"Warning: Font file {italic_font_path} not found. Using default.")
            italic_font_path = None
        if not os.path.exists(author_font_path):
            print(f"Warning: Font file {author_font_path} not found. Using default.")
            author_font_path = None
            
    except Exception as e:
        print(f"Error loading fonts: {e}")
        regular_font_path = None
        italic_font_path = None
        author_font_path = None
    
    # Set up font sizes
    main_text_size = 70  # Increased font size
    author_text_size = 26
    
    # Create font objects
    regular_font = ImageFont.truetype(regular_font_path, main_text_size) if regular_font_path else ImageFont.load_default()
    italic_font = ImageFont.truetype(italic_font_path, main_text_size) if italic_font_path else ImageFont.load_default()
    author_font = ImageFont.truetype(author_font_path, author_text_size) if author_font_path else ImageFont.load_default()
    
    content = quote_data.get('content', [])
    
    # ----------------
    # IMPROVED SPACING CALCULATIONS
    # ----------------
    
    # Calculate total available vertical space and distribute it better
    usable_height = height * 0.8  # Use 80% of image height for better spacing
    
    # Define spacing ratios for better distribution
    top_margin_ratio = 0.2    # Space at the top (20% of usable height)
    quote_section_ratio = 0.5  # Quote takes 50% of usable height
    bottom_section_ratio = 0.3 # Bottom section (line + author) takes 30% of usable height
    
    # Calculate actual spaces based on ratios
    top_margin = usable_height * top_margin_ratio
    quote_section_height = usable_height * quote_section_ratio
    bottom_section_height = usable_height * bottom_section_ratio
    
    # Line heights and inter-line spacing
    line_heights = []
    line_spacing = main_text_size * 0.7  # Increased spacing between lines
    
    # Calculate height of all text elements
    quote_text_height = 0
    for item in content:
        font = italic_font if item['style'] == 'italic' else regular_font
        text = item['text']
        bbox = draw.textbbox((0, 0), text, font=font)
        line_height = bbox[3] - bbox[1]
        line_heights.append(line_height)
        quote_text_height += line_height
    
    # Add spacing between lines
    total_quote_height = quote_text_height + (len(content) - 1) * line_spacing
    
    # Horizontal line and author settings
    horizontal_line_thickness = 3  # Slightly thicker line
    line_length = 120  # Length of the horizontal line
    
    # Get author text height
    author_text = quote_data.get('author', '')
    author_bbox = draw.textbbox((0, 0), author_text.upper(), font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    
    # Calculate starting position
    start_y = top_margin
    
    # Calculate even distribution within quote section
    if len(content) > 1:
        # Distribute lines evenly in the quote section
        quote_start_y = start_y + (quote_section_height - total_quote_height) / 2
    else:
        quote_start_y = start_y
    
    current_y = quote_start_y
    
    # Draw each line of the quote
    for i, item in enumerate(content):
        text = item['text']
        font = italic_font if item['style'] == 'italic' else regular_font
        text_width = draw.textlength(text, font=font)
        text_x = (width - text_width) // 2  # Center text horizontally
        
        # Draw the text
        draw.text((text_x, current_y), text, fill='white', font=font)
        
        # Move to next line position
        current_y += line_heights[i] + line_spacing
    
    # Position the horizontal line and author in the bottom section
    bottom_section_start = start_y + quote_section_height
    line_to_author_spacing = 40  # Space between line and author
    
    # Calculate positions for line and author
    line_y = bottom_section_start + (bottom_section_height - line_to_author_spacing - author_height) / 2
    line_start_x = (width - line_length) // 2
    line_end_x = line_start_x + line_length
    
    # Draw horizontal line
    draw.line([(line_start_x, line_y), (line_end_x, line_y)], fill='white', width=horizontal_line_thickness)
    
    # Draw author name in uppercase below the line
    author_text = quote_data.get('author', '').upper()
    author_width = draw.textlength(author_text, font=author_font)
    author_x = (width - author_width) // 2
    author_y = line_y + line_to_author_spacing
    
    draw.text((author_x, author_y), author_text, fill='white', font=author_font)
    
    # Save the image
    img.save(output_filename)
    print(f"Created quote image with better spacing as '{output_filename}'")
    return img


# Example usage
if __name__ == "__main__":
    # Sample input data
    quotes_data = [
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

    # Create the image
    i = 30
    for quote_data in quotes_data:
        file_name = f'posts/quote_image_{i}.png'
        create_quote_image(quote_data, output_filename=file_name)
        i += 1
