import subprocess

import pytest

from src.core.channel_extractor import YouTubeChannelExtractor
from src.core.extractor_factory import ExtractorFactory


def test_normalize_channel_videos_url_adds_videos_tab():
    url = "https://www.youtube.com/@plus1software"
    normalized = YouTubeChannelExtractor.normalize_channel_videos_url(url)
    assert normalized.endswith("/@plus1software/videos")


def test_normalize_channel_videos_url_replaces_other_tab():
    url = "https://www.youtube.com/@plus1software/shorts"
    normalized = YouTubeChannelExtractor.normalize_channel_videos_url(url)
    assert normalized.endswith("/@plus1software/videos")


def test_is_youtube_channel_url_detection():
    assert ExtractorFactory.is_youtube_channel_url("https://www.youtube.com/@plus1software/videos")
    assert ExtractorFactory.is_youtube_channel_url("https://www.youtube.com/channel/UCfWhnGPpZTfUzlhfwTh7sqg")
    assert not ExtractorFactory.is_youtube_channel_url("https://www.youtube.com/watch?v=2GPNKKeXSyQ")
    assert not ExtractorFactory.is_youtube_channel_url("https://www.youtube.com/playlist?list=PLxxxx")


def test_get_channel_info_parses_yt_dlp_output(monkeypatch, tmp_path):
    extractor = YouTubeChannelExtractor(str(tmp_path))

    def fake_run(cmd, capture_output, text, check):
        assert cmd[:3] == ["yt-dlp", "--no-update", "--flat-playlist"]
        return subprocess.CompletedProcess(cmd, 0, stdout="PLUS+1 Software - Videos\nUC123\n", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    title, channel_id = extractor.get_channel_info("https://www.youtube.com/@plus1software/videos")
    assert title.startswith("PLUS1_Software")
    assert channel_id == "UC123"


def test_get_channel_videos_parses_entries_and_respects_limit(monkeypatch, tmp_path):
    extractor = YouTubeChannelExtractor(str(tmp_path))

    def fake_run(cmd, capture_output, text, check):
        assert "--playlist-end" in cmd
        assert cmd[cmd.index("--playlist-end") + 1] == "2"
        stdout = "aaaaaaaaaaa|||First video\nbbbbbbbbbbb|||Second video\n"
        return subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    videos = extractor.get_channel_videos("https://www.youtube.com/@plus1software/videos", max_videos=2)
    assert [v.video_id for v in videos] == ["aaaaaaaaaaa", "bbbbbbbbbbb"]
    assert videos[0].url.endswith("watch?v=aaaaaaaaaaa")

