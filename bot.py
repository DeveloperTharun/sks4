import logging
import os
from telegram import (
    Update,
    error,
    ReplyKeyboardMarkup as RKM,
    ReplyKeyboardRemove as RKR,
    InlineKeyboardButton as IKB,
    InlineKeyboardMarkup as IKM,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from video_splitter import Video_splitter

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

START, VIDEO, SECONDS_OR_PARTS, SPLIT = range(4)


class Katana:
    def __init__(self, update, context, error, ReplyKeyboardMarkup):
        self.context = context
        self.update = update
        self.seconds = 0
        self.parts = 0
        self.rmk_input = None
        self.rmk = ReplyKeyboardMarkup
        self.user = None
        self.video_name
        self.vs = Video_splitter()
        self.error = error

    async def start(self):
        """Start bot"""
        self.user = self.update.message.from_user
        logger.info("%s started the bot", self.user.first_name.title())
        await self.update.message.reply_text(
            "Send a video you'd like to split"
        )

        return VIDEO

    async def collect_video(self):
        try:
            os.mkdir(f"vid/{self.user.id}")
        except FileExistsError:
            logger.info("vid folder already exists.")
        file_id = self.update.message.video.file_id
        new_file = await self.context.bot.get_file(file_id)
        self.video_name = await new_file.download_to_drive(
            f"vid/{self.user.id}/video.mp4"
        )
        logger.info("Saved %s ", self.video_name)

        reply_keyboard = [["Seconds"], ["Parts"]]
        self.update.message.reply_text(
            """Do you want to split the video by seconds or by parts?""",
            reply_markup=self.rmk(
                reply_keyboard,
                one_time_keyboard=True,
            ),
        )

        return SECONDS_OR_PARTS

    async def collect_seconds(self):
        self.rmk_input = self.update.message.text
        logger.info(f"User chose to split video by seconds")
        await self.update.message.reply_text(
            "Enter seconds"
        )

        return SPLIT

    async def collect_parts(self):
        self.rmk_input = self.update.message.text
        logger.info(f"User chose to split video by seconds")
        await self.update.message.reply_text(
            "Enter number of parts"
        )

        return SPLIT

    async def split_video(self):
        user_input = int(self.update.message.text)
        if self.rmk_input == "Parts":
            self.seconds = self.vs.find_split_length(user_input)
            
        # Download file.
        sticker = await self.context.bot.send_sticker(
            chat_id=self.update.effective_chat.id, sticker="loading.tgs"
        )
        sent_videos = []
        try:
            # split
            split_videos = self.vs.split(str(self.video_name), self.seconds)
            for v in split_videos:
                sent_videos.append(v)
                await self.context.bot.send_video(chat_id=self.update.effective_chat.id, video=v)

                # Remove files to reuse folder
            self.vs.remove(split_videos)
            self.vs.remove([str(self.video_name)])
            logger.info("Removed %s and split videos", self.video_name)
            await self.context.bot.delete_message(
                chat_id=self.update.effective_chat.id, message_id=sticker.id
            )

        except self.error.BadRequest:
            video_size = self.update.message.video.file_size
            await self.update.message.reply_text(
                f"""
            Size of video too large to be saved. Please
            try again with a smaller video size.
            Current video size: {int(video_size/1000000)}mb.
            Bot filesize limit: 20mb.
            """,
            )
            logger.info("Video too large; ask your to resend smaller video.")
            await self.context.bot.delete_message(
                chat_id=self.update.effective_chat.id, message_id=sticker.id
            )
        except SystemExit:
            video_duration = self.update.message.video.duration
            message = f"""
            Video duration is too short to be split.
            Current video duration: {video_duration} seconds.
            Current split size: {self.seconds} seconds.
            You can use /split_size {video_duration/2} to split video into 2.
            """
            await self.update.message.reply_text(message)
            self.vs.remove([str(self.video_name)])
            logger.info("Removed %s.", self.video_name)
            logger.info("Ask user to change split size to suit video duration.")
            await self.context.bot.delete_message(
                chat_id=self.update.effective_chat.id, message_id=sticker.id
            )
        except self.error.TimedOut:
            for v in split_videos:
                if v not in sent_videos:
                    sent_videos.append(v)
                    await self.context.bot.send_video(chat_id=self.update.effective_chat.id, video=v)

            # Remove files to reuse folder
            self.vs.remove(split_videos)
            self.vs.remove([str(self.video_name)])
            logger.info("Removed %s and split videos", self.video_name)
            await self.context.bot.delete_message(
                chat_id=self.update.effective_chat.id, message_id=sticker.id
            )
            
        return START
    
    