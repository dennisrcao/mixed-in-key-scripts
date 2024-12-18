import os
import shutil
from pathlib import Path
import wave
import contextlib
from pydub import AudioSegment
import math

def is_oneshot(audio_file_path):
    """Determine if an audio file is a oneshot based on its length"""
    try:
        # Get file extension
        file_ext = Path(audio_file_path).suffix.lower()
        
        # Format mapping for pydub
        format_map = {
            '.m4a': 'mp4',
            '.aif': 'aiff',
            '.aiff': 'aiff'
        }
        format_name = format_map.get(file_ext, file_ext[1:])
        
        # Convert path to string and escape special characters
        file_path_str = str(audio_file_path)
        
        # Load audio file using pydub
        try:
            audio = AudioSegment.from_file(file_path_str, format=format_name)
            
            # Get duration in seconds
            duration = len(audio) / 1000.0
            
            # Print debug info
            print(f"\nChecking file: {Path(audio_file_path).name}")
            print(f"Duration: {duration:.2f} seconds")
            print(f"Is oneshot: {duration < 2.0}\n")
            
            # Consider files under 2 seconds as oneshots
            return duration < 2.0
            
        except Exception as e:
            print(f"Error loading audio file {Path(audio_file_path).name}: {str(e)}")
            return False
            
    except Exception as e:
        print(f"Error processing {Path(audio_file_path).name}: {str(e)}")
        return False

def split_long_audio(file_path, parts_dir):
    """Split audio files longer than 10 minutes into parts"""
    # Determine file type and load accordingly
    file_ext = file_path.suffix.lower()
    try:
        # Special handling for different formats
        format_map = {
            '.m4a': 'mp4',
            '.aif': 'aiff',
            '.aiff': 'aiff'
        }
        format_name = format_map.get(file_ext, file_ext[1:])
        
        audio = AudioSegment.from_file(str(file_path), format=format_name)
        
        # Get duration in milliseconds and convert to minutes
        duration_mins = len(audio) / (1000 * 60)
        
        # If file is shorter than 10 minutes, return
        if duration_mins <= 10:
            return False
            
        # Calculate number of parts needed
        part_length_ms = 10 * 60 * 1000  # 10 minutes in milliseconds
        num_parts = math.ceil(len(audio) / part_length_ms)
        
        # Create parts directory if it doesn't exist
        parts_dir.mkdir(exist_ok=True)
        
        # Split and export parts
        for i in range(num_parts):
            start_ms = i * part_length_ms
            end_ms = min((i + 1) * part_length_ms, len(audio))
            
            segment = audio[start_ms:end_ms]
            
            # Create output filename
            output_name = f"{file_path.stem}_part{i+1}{file_path.suffix}"
            output_path = parts_dir / output_name
            
            # Export the segment, using mp4 format for m4a files
            segment.export(str(output_path), format=format_name)
            print(f"Created part {i+1} of {num_parts}: {output_name}")
        
        # Delete original file
        os.remove(file_path)
        print(f"Deleted original file: {file_path.name}")
        return True
        
    except Exception as e:
        print(f"Error processing {file_path.name}: {str(e)}")
        return False

def has_camelot_prefix(filename):
    """Check if filename starts with a valid Camelot wheel key (1A-12B) or 'All'"""
    # Split the filename into parts based on common separators
    parts = filename.split(' - ')[0].split('_')[0].strip()
    
    # Check for "All" prefix first
    if parts.startswith('All'):
        return False  # Treat "All" prefix as no valid Camelot key
    
    # Valid Camelot wheel numbers and keys
    numbers = list(range(1, 13))  # 1-12
    keys = ['A', 'B']
    
    # Check if any part starts with a valid Camelot combination
    for num in numbers:
        for key in keys:
            prefix = f"{num}{key}"
            if parts.startswith(prefix):
                return True
    return False

def main():
    # Get the root directory (where this script is located)
    root_dir = Path(__file__).parent
    
    # Create directories if they don't exist
    oneshots_dir = root_dir / "11. OneShots"
    parts_dir = root_dir / "12. Parts"
    unlabeled_dir = root_dir / "13. Unlabeled"
    oneshots_dir.mkdir(exist_ok=True)
    parts_dir.mkdir(exist_ok=True)
    unlabeled_dir.mkdir(exist_ok=True)
    
    # Audio file extensions to look for
    audio_extensions = {
        '.wav',    # Waveform Audio File
        '.mp3',    # MPEG Layer-3
        '.aiff',   # Audio Interchange File Format
        '.aif',    # Short for AIFF
        '.m4a',    # MPEG-4 Audio
        '.flac',   # Free Lossless Audio Codec
        '.ogg',    # Ogg Vorbis
        '.wma',    # Windows Media Audio
        '.aac',    # Advanced Audio Coding
        '.alac',   # Apple Lossless Audio Codec
        '.opus',   # Opus Audio Format
        '.wv',     # WavPack
        '.ape',    # Monkey's Audio
        '.mid',    # MIDI files
        '.midi',   # MIDI files
        '.pcm',    # Raw PCM audio
        '.3gp',    # 3GPP audio container
        '.amr'     # Adaptive Multi-Rate audio
    }
    
    # Walk through all subdirectories
    for dirpath, dirnames, filenames in os.walk(root_dir):
        current_path = Path(dirpath)
        
        # Skip the oneshots, parts, and unlabeled directories
        if any(x in str(current_path) for x in ["11. OneShots", "12. Parts", "13. Unlabeled"]):
            continue
            
        # Process each file
        for filename in filenames:
            file_path = current_path / filename
            
            # Check if it's an audio file
            if file_path.suffix.lower() in audio_extensions:
                # First check if it needs to be split
                if split_long_audio(file_path, parts_dir):
                    continue
                
                # If file doesn't have Camelot prefix, move to unlabeled
                if not has_camelot_prefix(filename):
                    # Create destination path
                    dest_path = unlabeled_dir / filename
                    
                    # Handle duplicate filenames
                    counter = 1
                    while dest_path.exists():
                        name = file_path.stem + f"_{counter}" + file_path.suffix
                        dest_path = unlabeled_dir / name
                        counter += 1
                    
                    # Move the file
                    shutil.move(file_path, dest_path)
                    print(f"Moved unlabeled file: {filename}")
                    continue
                
                # Process oneshots for remaining files
                if is_oneshot(str(file_path)):
                    # Create destination path preserving original filename
                    dest_path = oneshots_dir / filename
                    
                    # Handle duplicate filenames
                    counter = 1
                    while dest_path.exists():
                        name = file_path.stem + f"_{counter}" + file_path.suffix
                        dest_path = oneshots_dir / name
                        counter += 1
                    
                    # Move the file instead of copying
                    shutil.move(file_path, dest_path)
                    print(f"Moved oneshot: {filename}")
    
    # After processing all files, print a separator
    print("\n" + "="*20)  # 80 equal signs
    print("Finished processing all files!")
    print("=" * 20 + "\n")

if __name__ == "__main__":
    main() 