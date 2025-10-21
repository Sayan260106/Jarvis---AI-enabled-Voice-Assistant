from typing import Dict, Optional

_music: Dict[str, str] = {
    "arijit singh": "https://youtu.be/kXHiIxx2atA?list=RDkXHiIxx2atA",
    "krishna kumar": "https://youtu.be/r0c1f6XxRQg?list=RDr0c1f6XxRQg",
    "imagine dragons": "https://youtu.be/5JOaTtcg1tE?list=RD5JOaTtcg1tE",
    "skyfall": "https://www.youtube.com/watch?v=DeumyOzKqgI",
}


def get_link(title: str) -> Optional[str]:
    """Return the URL for a given song title (case-insensitive).

    Matches exactly on normalized title; you can extend to fuzzy matching.
    """
    if not title:
        return None
    key = title.strip().lower()
    return _music.get(key)


def list_songs() -> Dict[str, str]:
    """Return a copy of the available songs mapping."""
    return dict(_music)