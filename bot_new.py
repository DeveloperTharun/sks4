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
import settings

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

START, VIDEO, SECONDS_OR_PARTS, SPLIT = range(4)


class Katana:
    def __init__(self, update, context, rmk):
        self.context = context
        self.update = update
        self.rmk = rmk
        self.user = None
        self.video_name

    async def start(self):
        """Start bot"""
        self.user = self.update.message.from_user
        logger.info("%s started the bot", self.user.first_name.title())
        await self.update.message.reply_text(
            "I am Katana. Send a video you'd like to split"
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



