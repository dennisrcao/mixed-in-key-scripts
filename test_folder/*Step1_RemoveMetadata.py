import os
from pathlib import Path
from mutagen import File
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4
from mutagen.wave import WAVE

def prepare_metadata(file_path):
    """Prepare metadata for Mixed In Key processing"""
    try:
        file_ext = file_path.suffix.lower()
        original_name = file_path.stem
        
        # Handle MP3 files
        if file_ext == '.mp3':
            try:
                audio = EasyID3(str(file_path))
                audio.delete()
                audio['title'] = original_name
                audio.save()
            except:
                print(f"Could not set MP3 metadata for: {file_path.name}")
        
        # Handle M4A/MP4/AAC/ALAC files
        elif file_ext in ['.m4a', '.mp4', '.aac', '.alac']:
            audio = MP4(str(file_path))
            audio.delete()
            audio['\xa9nam'] = [original_name]  # title tag
            audio['\xa9ART'] = ['']  # artist tag
            audio.save()
        
        # Handle FLAC files
        elif file_ext == '.flac':
            audio = File(str(file_path))
            if audio:
                audio.delete()
                audio['TITLE'] = original_name
                audio.save()
        
        # Handle OGG/OPUS files
        elif file_ext in ['.ogg', '.opus']:
            audio = File(str(file_path))
            if audio:
                audio.delete()
                audio['TITLE'] = original_name
                audio.save()
        
        # Handle WavPack files
        elif file_ext == '.wv':
            audio = File(str(file_path))
            if audio:
                audio.delete()
                audio['TITLE'] = original_name
                audio.save()
        
        # Handle Monkey's Audio (APE)
        elif file_ext == '.ape':
            audio = File(str(file_path))
            if audio:
                audio.delete()
                audio['TITLE'] = original_name
                audio.save()
        
        # Handle AIFF/AIF files
        elif file_ext in ['.aiff', '.aif']:
            try:
                audio = File(str(file_path))
                if audio:
                    # Clear all existing tags
                    audio.tags.clear()
                    # Add only the title
                    audio.tags['TITLE'] = original_name
                    audio.save()
            except AttributeError:
                # If the above method fails, try alternative approach
                try:
                    audio = File(str(file_path), easy=True)
                    if audio:
                        audio.delete()
                        audio['title'] = original_name
                        audio.save()
                except:
                    print(f"Could not set AIFF metadata for: {file_path.name}")
        
        # Handle WAV files
        elif file_ext == '.wav':
            try:
                audio = WAVE(str(file_path))
                # Clear any existing tags/metadata
                if hasattr(audio, 'tags'):
                    audio.tags.clear()
                if hasattr(audio, 'clear'):
                    audio.clear()
                audio.save()
            except:
                print(f"Could not clear WAV metadata for: {file_path.name}")
        
        # Other formats (WMA, MIDI, PCM, 3GP, AMR) typically don't need metadata
        # modification for Mixed In Key to process them correctly
        
        print(f"Successfully prepared metadata for: {file_path.name}")
        
    except Exception as e:
        print(f"Error processing {file_path.name}: {str(e)}")

def main():
    # Get the root directory (where this script is located)
    root_dir = Path(__file__).parent
    
    # Use the same audio extensions as in extract.py
    audio_extensions = {
        '.wav', '.mp3', '.aiff', '.aif', '.m4a', '.flac',
        '.ogg', '.wma', '.aac', '.alac', '.opus', '.wv',
        '.ape', '.mid', '.midi', '.pcm', '.3gp', '.amr'
    }
    
    # Walk through all subdirectories
    for dirpath, dirnames, filenames in os.walk(root_dir):
        current_path = Path(dirpath)
        
        # Process each file
        for filename in filenames:
            file_path = current_path / filename
            
            # Check if it's an audio file
            if file_path.suffix.lower() in audio_extensions:
                prepare_metadata(file_path)
    
    print("\n" + "="*20)
    print("Finished preparing metadata for all files!")
    print("=" * 20 + "\n")

if __name__ == "__main__":
    main() 