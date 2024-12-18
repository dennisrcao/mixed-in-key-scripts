import os
from pathlib import Path
from mutagen import File
from mutagen.wave import WAVE
import re

def has_camelot_prefix(filename):
    """Check if filename starts with Camelot key notation (e.g., '1A - ', '12B - ')"""
    pattern = r'^(?:[1-9]|1[0-2])[AB]\s*-\s*'
    return bool(re.match(pattern, filename))

def read_and_rename(file_path):
    """Read metadata and rename files without Camelot prefix"""
    try:
        file_ext = file_path.suffix.lower()
        filename = file_path.name
        artist = "N/A"
        title = "N/A"
        key = "N/A"
        renamed = False
        
        # Check if file needs renaming (no Camelot prefix)
        if not has_camelot_prefix(filename):
            # Create new filename with "All - " prefix
            new_name = f"All - {filename}"
            new_path = file_path.parent / new_name
            
            try:
                # Rename the file
                file_path.rename(new_path)
                file_path = new_path  # Update file_path to new location
                filename = new_name   # Update filename
                renamed = True
                print(f"Renamed to: {new_name}")
            except Exception as e:
                print(f"Error renaming {filename}: {str(e)}")
        
        # Continue with metadata reading
        if file_ext == '.wav':
            try:
                audio = WAVE(str(file_path))
                if hasattr(audio, 'tags'):
                    tags = audio.tags
                    if tags:
                        # Debug: Print all available tags
                        print(f"\nDebug - All tags for {filename}:")
                        for tag_key, tag_value in tags.items():
                            print(f"{tag_key}: {tag_value}")
                        
                        artist = tags.get('artist', ['N/A'])[0]
                        title = tags.get('title', ['N/A'])[0]
                        key = tags.get('key', tags.get('initialkey', 
                              tags.get('TKEY', tags.get('KEY', ['N/A']))))[0]
                
                if hasattr(audio, '_INFO'):
                    print(f"\nDebug - INFO chunks:")
                    print(audio._INFO)
                    
            except Exception as e:
                print(f"Debug - WAV read error: {str(e)}")
                
        else:
            audio = File(str(file_path))
            if audio and hasattr(audio, 'tags'):
                tags = audio.tags
                if tags:
                    artist = tags.get('artist', tags.get('\xa9ART', ['N/A']))[0]
                    title = tags.get('title', tags.get('\xa9nam', ['N/A']))[0]
                    key = tags.get('key', tags.get('initialkey', tags.get('TKEY', ['N/A'])))[0]
        
        return [filename, artist, title, key, renamed]
            
    except Exception as e:
        return [filename, "ERROR", str(e), "N/A", False]

def main():
    root_dir = Path(__file__).parent
    
    audio_extensions = {
        '.wav', '.mp3', '.aiff', '.aif', '.m4a', '.flac',
        '.ogg', '.wma', '.aac', '.alac', '.opus', '.wv',
        '.ape', '.mid', '.midi', '.pcm', '.3gp', '.amr'
    }
    
    # Print header
    print("\n{:<50} | {:<30} | {:<50} | {:<10} | {:<8}".format(
        "Filename", "Artist", "Title", "Key", "Renamed"))
    print("-" * 152)
    
    # Walk through all subdirectories
    for dirpath, dirnames, filenames in os.walk(root_dir):
        current_path = Path(dirpath)
        
        for filename in filenames:
            file_path = current_path / filename
            
            if file_path.suffix.lower() in audio_extensions:
                result = read_and_rename(file_path)
                print("{:<50} | {:<30} | {:<50} | {:<10} | {:<8}".format(
                    result[0][:49],
                    result[1][:29],
                    result[2][:49],
                    result[3][:9],
                    "Yes" if result[4] else "No"
                ))

if __name__ == "__main__":
    main() 