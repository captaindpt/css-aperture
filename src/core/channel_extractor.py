"""YouTube channel indexing functionality."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from urllib.parse import urlparse, urlunparse

from .base import ContentExtractor


@dataclass(frozen=True)
class ChannelVideo:
    video_id: str
    title: str

    @property
    def url(self) -> str:
        return f"https://www.youtube.com/watch?v={self.video_id}"


class YouTubeChannelExtractor(ContentExtractor):
    """Indexes videos from a YouTube channel (Videos tab)."""

    _TAB_NAMES = {"videos", "featured", "streams", "shorts", "playlists", "community", "about"}

    def get_source_type(self) -> str:
        return "youtube_channel"

    def get_content_info(self, source: str) -> Tuple[str, str]:
        return self.get_channel_info(source)

    @staticmethod
    def normalize_channel_videos_url(url: str) -> str:
        """
        Normalize a channel URL to point at the channel's /videos tab.

        Accepts:
          - https://www.youtube.com/@handle
          - https://www.youtube.com/@handle/videos
          - https://www.youtube.com/channel/UCxxxx
          - https://www.youtube.com/channel/UCxxxx/videos
        """
        parsed = urlparse(url)
        path = (parsed.path or "").rstrip("/")
        if not path:
            return url

        last_segment = path.rsplit("/", 1)[-1].lower()
        if last_segment in YouTubeChannelExtractor._TAB_NAMES:
            path = path[: -len(last_segment)].rstrip("/")

        path = f"{path}/videos"

        return urlunparse(parsed._replace(path=path))

    def get_channel_info(self, url: str) -> Tuple[str, str]:
        """
        Get the channel title and channel ID for naming.

        Uses yt-dlp to treat the channel videos page like a playlist.
        """
        url = self.normalize_channel_videos_url(url)

        try:
            cmd = [
                "yt-dlp",
                "--no-update",
                "--flat-playlist",
                "--print", "playlist_title",
                "--print", "playlist_id",
                "--playlist-items", "1",
                url,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split("\n")

            title = lines[0] if lines else "channel"
            channel_id = lines[1] if len(lines) > 1 else "unknown"

            clean_title = re.sub(r"[^\w\s-]", "", title)
            clean_title = re.sub(r"[-\s]+", "_", clean_title).strip("_")

            return clean_title, channel_id

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get channel info: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Channel info retrieval failed: {str(e)}")

    def get_channel_videos(self, url: str, max_videos: Optional[int] = None) -> List[ChannelVideo]:
        """Get list of videos from a channel videos page."""
        url = self.normalize_channel_videos_url(url)

        try:
            cmd = [
                "yt-dlp",
                "--no-update",
                "--flat-playlist",
                "--print", "%(id)s|||%(title)s",
            ]
            if max_videos is not None:
                cmd.extend(["--playlist-end", str(max_videos)])
            cmd.append(url)

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            videos: List[ChannelVideo] = []
            for line in result.stdout.strip().split("\n"):
                if "|||" not in line:
                    continue
                video_id, title = line.split("|||", 1)
                video_id = video_id.strip()
                title = title.strip()
                if video_id:
                    videos.append(ChannelVideo(video_id=video_id, title=title))

            return videos

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to list channel videos: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Channel video listing failed: {str(e)}")

    def extract_content(
        self,
        source: str,
        output_name: Optional[str] = None,
        max_videos: Optional[int] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Index all videos from a YouTube channel.

        Returns:
            Tuple of (channel_info_json_path, channel_videos_md_path)
        """
        source_videos_url = self.normalize_channel_videos_url(source)

        if not output_name:
            clean_title, channel_id = self.get_channel_info(source_videos_url)
            output_name = f"{clean_title}_{channel_id}"
            print(f"📺 Channel: {clean_title.replace('_', ' ')}")
            print(f"📁 Creating folder: {output_name}")

        channel_dir = self._create_output_directory(output_name)

        print("📊 Fetching channel videos...")
        videos = self.get_channel_videos(source_videos_url, max_videos=max_videos)
        print(f"📺 Found {len(videos)} videos\n")

        info = {
            "channel_name": output_name,
            "source_url": source,
            "source_videos_url": source_videos_url,
            "indexed_at": datetime.now(timezone.utc).isoformat(),
            "max_videos": max_videos,
            "total_videos_indexed": len(videos),
            "videos": [
                {
                    "index": idx,
                    "video_id": v.video_id,
                    "title": v.title,
                    "url": v.url,
                }
                for idx, v in enumerate(videos, 1)
            ],
        }

        info_file = channel_dir / "channel_info.json"
        info_file.write_text(json.dumps(info, indent=2, ensure_ascii=False), encoding="utf-8")

        videos_md = channel_dir / "channel_videos.md"
        with open(videos_md, "w", encoding="utf-8") as f:
            f.write(f"# Channel Index: {output_name}\n\n")
            f.write(f"- Source: {source_videos_url}\n")
            f.write(f"- Indexed at: {info['indexed_at']}\n")
            if max_videos is not None:
                f.write(f"- Max videos: {max_videos}\n")
            f.write(f"- Videos indexed: {len(videos)}\n\n")
            f.write("## Videos\n\n")
            for idx, v in enumerate(videos, 1):
                safe_title = v.title.replace("\n", " ").strip()
                f.write(f"{idx}. [{safe_title}]({v.url}) (`{v.video_id}`)\n")

        print(f"✅ Channel index saved:")
        print(f"   JSON: {info_file}")
        print(f"   Markdown: {videos_md}")

        return str(info_file), str(videos_md)

