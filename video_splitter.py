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

    
    def change_split_number(self, new_number):
        if new_number > 0:
            self.split_by_number = True
            self.split_number = new_number
        else:
            self.split_by_number = False
            self.split_number = 0
        
    
    def find_split_length(self, filename, split_number):
        video_length = get_video_length(filename)
        print(video_length)
        return video_length / split_number
        

        
    def split(self, filename, seconds=None):
        if self.split_by_number:
            seconds = self.find_split_length(filename, self.split_number)
            video_files = split_by_seconds(filename, seconds, "h264")
        elif seconds:
            video_files = split_by_seconds(filename, seconds, "h264")
        else:
            video_files = split_by_seconds(filename, self.seconds, "h264")

        return video_files


        
    def remove(self, files):
        for file in files:
            os.remove(file)
