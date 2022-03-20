import pytest
import subprocess

from pathlib import Path

from spotdl.utils.spotify import SpotifyClient

ORIGINAL_INITIALIZE = SpotifyClient.init


class FakeProcess:
    """Instead of running ffmpeg, just fake it"""

    def __init__(self, *args):
        command = list(*args)
        self._input = Path(command[command.index("-i") + 1])
        self._output = Path(command[-1])

    def communicate(self):
        """
        Ensure that the file has been download, and create empty output file,
        to avoid infinite loop.
        """
        assert self._input.is_file()
        self._output.open("w").close()
        return (None, None)

    def wait(self):
        return None

    @property
    def returncode(self):
        return 0


def new_initialize(
    client_id,
    client_secret,
    user_auth=False,
    cache_path=None,
    no_cache=False,
    open_browser=False,
):
    """This function allows calling `initialize()` multiple times"""
    try:
        return SpotifyClient()
    except:
        return ORIGINAL_INITIALIZE(
            client_id=client_id,
            client_secret=client_secret,
            user_auth=user_auth,
            cache_path=cache_path,
            no_cache=no_cache,
            open_browser=open_browser,
        )


def fake_create_subprocess_exec(*args, stdout=None, stderr=None, **kwargs):
    return FakeProcess(args)


@pytest.fixture()
def patch_dependencies(monkeypatch):
    """
    This function is called before each test.
    """

    monkeypatch.setattr(SpotifyClient, "init", new_initialize)
    monkeypatch.setattr(subprocess, "Popen", fake_create_subprocess_exec)
