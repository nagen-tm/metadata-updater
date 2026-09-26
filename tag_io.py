# core/tag_io.py  (minimal start)
from __future__ import annotations
from pathlib import Path
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TPE2, TRCK, TPE3, TYER,
TCON
from .models import TrackMeta

def read_tags(path: Path) -> TrackMeta:
    tags = ID3(str(path))
    return TrackMeta(
        title     = str(tags.get("TIT2", "Unknown")),
        artist    = str(tags.get("TPE1", "Unknown")),
        album     = str(tags.get("TALB", "")),
        album_artist = str(tags.get("TPE2", "")),
        track_no  = int(tags.get("TRCK", "0").split("/")[0]) or None,
        year      = str(tags.get("TYER", "")),
        genre     = str(tags.get("TCON", "")),
    )

def write_tags(path: Path, meta: TrackMeta) -> None:
    tags = ID3(str(path))
    if meta.title:         tags["TIT2"] = TIT2(encoding=3,
text=meta.title)
    if meta.artist:        tags["TPE1"] = TPE1(encoding=3,
text=meta.artist)
    if meta.album:         tags["TALB"] = TALB(encoding=3,
text=meta.album)
    if meta.album_artist:  tags["TPE2"] = TPE2(encoding=3,
text=meta.album_artist)
    if meta.track_no:      tags["TRCK"] = TRCK(encoding=3,
text=str(meta.track_no))
    if meta.year:          tags["TYER"] = TYER(encoding=3, text=meta.year)
    if meta.genre:         tags["TCON"] = TCON(encoding=3,
text=meta.genre)
    tags.save()