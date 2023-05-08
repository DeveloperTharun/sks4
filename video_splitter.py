from ffmpeg_split import split_by_seconds, get_video_length
import os
import settings


class Video_splitter:
    """Class for video splitting and deletion."""

    def __init__(self):
        self.seconds = settings.SPLIT_SIZE
        self.split_by_number = False 
        self.split_number = None

    def change_seconds(self, new_seconds):
        self.seconds = new_seconds
        
    
    def find_split_length(filename, split_number):
        video_length = get_video_length(filename)
        return video_length / split_number
        

        
    def split(self, filename, seconds=None):
        if seconds:
            video_files = split_by_seconds(filename, seconds, "h264")
        elif self.split_by_number:
            video_files = split_by_seconds(filename, self.split_number, "h264")
        else:
            video_files = split_by_seconds(filename, self.seconds, "h264")

        return video_files


        
    def remove(self, files):
        for file in files:
            os.remove(file)
