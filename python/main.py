import datetime
from dataclasses import asdict

import requests
import threading

from service.helper.SongTracker import SongTracker
from service.audio_service import AudioService
from service.music_detector import MusicDetector
from service.shazam_service import ShazamService

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

WEBHOOK_URL = "http://homeassistant.local:8123/api/webhook/-shazampi-trigger"

def notify_webhook(data):
    try:
        payload = {"data": asdict(data) if hasattr(data, "__dataclass_fields__") else data}
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to notify webhook: {e}")

def music_detection_loop():
    recording_duration = 10
    seconds_delay_to_mark_no_song = 30
    last_music_detected_time = datetime.datetime.now() - datetime.timedelta(seconds=seconds_delay_to_mark_no_song)
    while True:
        raw_audio = audio_service.record_raw_audio(recording_duration)

        if music_detector.is_audio_music(raw_audio):
            logging.debug("Music Detected")
            last_music_detected_time = datetime.datetime.now()
            if tracker.should_identify():
                logging.debug("Identifying song")
                waveform = audio_service.convert_audio_to_wav_format(raw_audio)
                song_info = shazam_service.identify_song(waveform)
                if song_info:
                    logging.debug("Song Identified")
                    notify_webhook(song_info)
                    logging.debug(f"Now playing: {asdict(song_info)}")
                    tracker.update(song_info)
        else:
            tracker.prev_title = None  # reset if no music
            # only send no music notification if no music detected for more than 30 sec
            if( datetime.datetime.now()-last_music_detected_time).total_seconds() > seconds_delay_to_mark_no_song:
                notify_webhook(None)
            logging.debug("No music.")

if __name__ == "__main__":
    audio_service = AudioService()
    music_detector = MusicDetector(recording_duration=10)
    shazam_service = ShazamService()
    tracker = SongTracker(default_delay=120)

    threading.Thread(
        target=music_detection_loop,
        daemon=True
    ).start()

    logger.info("Running music detection with webhook notifications...")
    threading.Event().wait()  # blocks forever without CPU waste
