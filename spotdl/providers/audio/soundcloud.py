"""
YTMusic module for downloading and searching songs.
"""
from typing import Any, Dict, List, Optional

from soundcloud import SoundCloud as SoundCloudClient
from itertools import islice
from slugify import slugify

import re

from spotdl.utils.providers import match_percentage
from spotdl.providers.audio.base import AudioProvider
from spotdl.types import Song
from spotdl.utils.formatter import (
    create_song_title,
    create_search_query,
)


class SoundCloud(AudioProvider):
    """
    SoundCloud audio provider class
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the SoundCloud API

        ### Arguments
        - args: Arguments passed to the `AudioProvider` class.
        - kwargs: Keyword arguments passed to the `AudioProvider` class.
        """

        super().__init__(*args, **kwargs)
        self.client = SoundCloudClient()

    def search(self, song: Song) -> Optional[str]:
        """
        Search for a song on SoundCloud.

        ### Arguments
        - song: The song to search for.

        ### Returns
        - The url of the best match or None if no match was found.
        """

        if self.search_query:
            search_query = create_search_query(
                song, self.search_query, False, None, True
            )
        else:
            search_query = create_song_title(song.name, song.artists).lower()

        song_results = self.get_results(search_query)

        if not song_results:
            return None

        if self.filter_results:
            # Order results
            songs = self.order_results(song_results, song)
        else:
            songs = {}
            if len(song_results) > 0:
                songs = {song_results[0]["link"]: 100}

        if len(songs) != 0:
            # get the result with highest score
            best_result = max(songs, key=lambda k: songs[k])

            if songs[best_result] >= 80:
                return best_result
        else:
            return None

        results = {**songs}

        result_items = list(results.items())

        # Sort results by highest score
        sorted_results = sorted(result_items, key=lambda x: x[1], reverse=True)

        # Get the result with highest score
        # and return the link
        return sorted_results[0][0]

    def get_results(self, search_term: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Get results from SoundCloud API and simplify them

        ### Arguments
        - search_term: The search term to search for.
        - kwargs: other keyword arguments passed to the `YTMusic.search` method.

        ### Returns
        - A list of simplified results (dicts)
        """

        results = list(islice(self.client.search(search_term), 20))
        regex = r'^(.+?)-|(\(\w+[\s\S]*\))'
        # Because anyone can post on soundcloud, we do another search with an edited search
        # The regex removes anything in brackets and the artist(s)'s name(s) if in the name
        edited_search_term = re.sub(regex, "", search_term)
        results.extend(list(islice(self.client.search(edited_search_term), 20)))

        # Simplify results
        simplified_results = []
        for result in results:
            if result.kind != "track":
                continue

            album = self.client.get_track_albums(result.id)

            try:
                album_name = next(album).title
            except StopIteration:
                album_name = None

            simplified_results.append(
                {
                    "name": result.title,
                    "type": "track",
                    # Should be result.kind, but it will always be track, might change in the future
                    "link": result.permalink_url,
                    "album": album_name,
                    "duration": result.full_duration,
                    "artist": result.user.username,
                    # Soundcloud doesn't give a list of artists, so we have to assume all the
                    # artist names are in the URL, or that if the song only has 1 artist,
                    # we use their username
                    "verified": result.user.verified,
                }
            )

        return simplified_results

    def order_results(
        self, results: List[Dict[str, Any]], song: Song
    ) -> Dict[str, Any]:
        """
        Filter results based on the song's metadata.

        ### Arguments
        - results: The results to filter.
        - song: The song to filter by.

        ### Returns
        - A dict of filtered results.
        """

        # Slugify some variables
        slug_song_name = slugify(song.name)
        slug_album_name = slugify(song.album_name)

        # Assign an overall avg match value to each result
        links_with_match_value = {}
        for result in results:

            # Slugify result title
            slug_result_name = slugify(result["name"])

            # check for common words in result name
            sentence_words = slug_song_name.replace("-", " ").split(" ")
            common_word = any(
                word != "" and word in slug_result_name for word in sentence_words
            )

            # skip results that have no common words in their name
            if not common_word:
                continue

            # Artist divide number
            artist_divide_number = 1

            # Find artist match
            artist_match_number = 0.0
            if result["type"] == "track":
                for artist in song.artists:
                    artist_match = match_percentage(
                        slugify(artist), slugify(result["artist"])
                    )
                    if artist_match == 100:
                        links_with_match_value[result["link"]] = artist_match
                        return links_with_match_value
                    artist_match_number += artist_match

                # If we didn't find any artist match, we fallback to artist name match. Since
                # anyone can post songs on soundcloud, we keep the maximum level to trigger the
                # if block very low
                if artist_match_number <= 30:
                    channel_name_match = match_percentage(
                        slugify(song.artist),
                        slugify(result["name"]),
                    )
                    if channel_name_match > artist_match_number:
                        artist_match_number = channel_name_match
                        artist_divide_number = 1

            # skip results with artist match lower than 70%
            artist_match = artist_match_number / artist_divide_number

            if artist_match < 70:
                continue

            # Find album match
            album_match = 0.0
            album = None

            if result["type"] == "track":
                album = result.get("album")
                if album:
                    album_match = match_percentage(slugify(album), slug_album_name)

            # Calculate time match
            delta = result["duration"] - song.duration
            non_match_value = (delta ** 2) / song.duration * 100

            time_match = 100 - non_match_value

            if result["type"] == "track":
                if album is None:
                    # Don't use album match
                    # If we didn't find album for the result,
                    average_match = (artist_match + time_match) / 2
                elif (
                    match_percentage(album.lower(), result["name"].lower()) > 95
                    and album.lower() != song.album_name.lower()
                ):
                    # If the album name is similar to the result song name,
                    # But the album name is different from the song album name
                    # We don't use album match
                    average_match = (artist_match + time_match) / 2
                else:
                    average_match = (
                                        artist_match + album_match + time_match
                                    ) / 3
            else:
                # Don't use album match for videos
                average_match = (artist_match + time_match) / 2

            # the results along with the avg Match
            links_with_match_value[result["link"]] = average_match

        return links_with_match_value
