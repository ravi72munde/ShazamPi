from dataclasses import dataclass

@dataclass
class SongInfo:
    title: str = "Unknown"
    artist: str = "Unknown"
    album: str = "Unknown"
    album_art: str = ""
    offset: int = 0
    song_duration: int = 0
