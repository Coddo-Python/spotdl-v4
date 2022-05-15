from spotdl.providers.audio import SoundCloud
from spotdl.types.song import Song


def test_find_song():
    provider = SoundCloud()

    song = Song.from_search_term("PS5")

    results = provider.search(song)

    assert results == "https://soundcloud.com/salemilese/ps5-feat-alan-walker"
