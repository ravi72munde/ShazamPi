import datetime
from service.model.SongInfo import SongInfo

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SongTracker:
    """
    Tracks currently identified song and decides whether re-identification is needed.
    """

    def __init__(self, default_delay: int = 120):
        self.prev_title: str | None = None
        self.next_check_time: datetime.datetime | None = None
        self.default_delay = default_delay

    def should_identify(self) -> bool:
        now = datetime.datetime.now()

        # No previous song → identify
        if self.prev_title is None:
            logger.debug("previous song was None so detecting")
            return True

        if self.next_check_time is None or now >= self.next_check_time:
            logger.debug("Reached the next trigger time".format(self.next_check_time))
            return True

        logger.debug(f"Waiting... will trigger in {(self.next_check_time - now).total_seconds():.2f} seconds")
        return False

    def update(self, song_info: SongInfo):
        now = datetime.datetime.now()

        self.prev_title = song_info.title or "Unknown"
        duration = song_info.song_duration
        offset = song_info.offset

        if duration is None or offset is None:
            self.next_check_time = now + datetime.timedelta(seconds=self.default_delay)
        else:
            self.next_check_time = now + datetime.timedelta(
                seconds=min(self.default_delay, duration - offset - 10)
            )

