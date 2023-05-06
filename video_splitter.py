from ffmpeg_split import split_by_seconds
import os
import settings


class Video_splitter:
    """Class for video splitting and deletion."""

    def __init__(self):
        self.seconds = settings.SPLIT_SIZE

    def change_seconds(self, new_seconds):
        self.seconds = new_seconds

        
    def split(self, filename, seconds=None):
        if seconds:
            video_files = split_by_seconds(filename, seconds, "h264")
        else:
            video_files = split_by_seconds(filename, self.seconds, "h264")

        return video_files


    def split_by_number(self, filename, video_length, number_of_splits):
        seconds = (video_length * 60) / number_of_splits
        self.split(filename, seconds)

        
    def remove(self, files):
        for file in files:
            os.remove(file)
