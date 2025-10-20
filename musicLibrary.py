from typing import Dict, Optional

_music: Dict[str, str] = {
    "stealth": "https://www.youtube.com/watch?v=U47Tr9BB_wE",
    "march": "https://www.youtube.com/watch?v=Xqeq4b5u_Xw",
    "skyfall": "https://www.youtube.com/watch?v=DeumyOzKqgI",
    "wolf": "https://www.youtube.com/watch?v=ThCH0U6aJpU",
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