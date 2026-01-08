"""YouTube playlist extraction functionality."""

import json
import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any

from .base import ContentExtractor
from .extractor import YouTubeExtractor


class YouTubePlaylistExtractor(ContentExtractor):
    """Extracts subtitles from all videos in a YouTube playlist."""

    def __init__(self, output_dir: str = ".", use_whisper: bool = False,
                 whisper_model: str = "base", use_api: bool = False):
        super().__init__(output_dir)
        self.use_whisper = use_whisper
        self.whisper_model = whisper_model
        self.use_api = use_api

    def get_source_type(self) -> str:
        """Return the type of content this extractor handles."""
        return "youtube_playlist"

    def get_content_info(self, source: str) -> Tuple[str, str]:
        """
        Get YouTube playlist information for naming.

        Args:
            source: YouTube playlist URL

        Returns:
            Tuple of (clean_title, playlist_id)
        """
        return self.get_playlist_info(source)

    def get_playlist_info(self, url: str) -> Tuple[str, str]:
        """
        Get the title and ID of a YouTube playlist.

        Args:
            url: YouTube playlist URL

        Returns:
            Tuple of (clean_title, playlist_id)

        Raises:
            RuntimeError: If info retrieval fails
        """
        try:
            cmd = [
                "yt-dlp",
                "--no-update",
                "--flat-playlist",
                "--print", "playlist_title",
                "--print", "playlist_id",
                "--playlist-items", "1",
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split('\n')

            title = lines[0] if lines else "playlist"
            playlist_id = lines[1] if len(lines) > 1 else "unknown"

            # Clean title for filename
            clean_title = re.sub(r'[^\w\s-]', '', title)
            clean_title = re.sub(r'[-\s]+', '_', clean_title)

            return clean_title, playlist_id

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get playlist info: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Playlist info retrieval failed: {str(e)}")

    def get_playlist_videos(self, url: str) -> List[Dict[str, str]]:
        """
        Get list of videos in the playlist.

        Args:
            url: YouTube playlist URL

        Returns:
            List of dicts with video_id and title
        """
        try:
            cmd = [
                "yt-dlp",
                "--no-update",
                "--flat-playlist",
                "--print", "%(id)s|||%(title)s",
                url
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            videos = []
            for line in result.stdout.strip().split('\n'):
                if '|||' in line:
                    video_id, title = line.split('|||', 1)
                    videos.append({
                        'video_id': video_id.strip(),
                        'title': title.strip()
                    })

            return videos

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to get playlist videos: {e.stderr}")
        except Exception as e:
            raise RuntimeError(f"Playlist video listing failed: {str(e)}")

    def extract_content(
        self,
        source: str,
        output_name: Optional[str] = None,
        language: str = "en",
        **kwargs
    ) -> Tuple[str, str]:
        """
        Extract subtitles from all videos in a YouTube playlist.

        Args:
            source: YouTube playlist URL
            output_name: Custom output folder name
            language: Subtitle language code (default: "en")
            **kwargs: Additional parameters

        Returns:
            Tuple of (playlist_info_path, combined_text_path)
        """
        # Get playlist info
        if not output_name:
            clean_title, playlist_id = self.get_playlist_info(source)
            output_name = f"{clean_title}_{playlist_id}"
            print(f"📋 Playlist: {clean_title.replace('_', ' ')}")
            print(f"📁 Creating folder: {output_name}")

        # Create playlist directory
        playlist_dir = self._create_output_directory(output_name)

        # Get video list
        print("📊 Fetching playlist contents...")
        videos = self.get_playlist_videos(source)
        total_videos = len(videos)
        print(f"📺 Found {total_videos} videos in playlist\n")

        # Track results
        extracted_videos = []
        failed_videos = []

        # Create video extractor - use playlist_dir directly as extractions_dir
        # to avoid nested 'extractions' folders
        if self.use_whisper:
            from .whisper_extractor import WhisperYouTubeExtractor
            video_extractor = WhisperYouTubeExtractor(
                str(playlist_dir.parent),
                model=self.whisper_model,
                use_api=self.use_api
            )
            # Override extractions_dir to be the playlist folder directly
            video_extractor.extractions_dir = playlist_dir
        else:
            video_extractor = YouTubeExtractor(str(playlist_dir.parent))
            # Override extractions_dir to be the playlist folder directly
            video_extractor.extractions_dir = playlist_dir

        # Extract each video
        for idx, video in enumerate(videos, 1):
            video_id = video['video_id']
            video_title = video['title']
            video_url = f"https://www.youtube.com/watch?v={video_id}"

            print(f"[{idx}/{total_videos}] Extracting: {video_title[:50]}...")

            try:
                _, text_file = video_extractor.extract_content(
                    video_url,
                    output_name=None,  # Auto-generate name
                    language=language
                )
                extracted_videos.append({
                    'video_id': video_id,
                    'title': video_title,
                    'text_file': text_file
                })
                print(f"    ✅ Done\n")
            except Exception as e:
                print(f"    ❌ Failed: {str(e)[:50]}\n")
                failed_videos.append({
                    'video_id': video_id,
                    'title': video_title,
                    'error': str(e)
                })

        # Save playlist info
        playlist_info = {
            'playlist_name': output_name,
            'source_url': source,
            'total_videos': total_videos,
            'extracted': len(extracted_videos),
            'failed': len(failed_videos),
            'videos': extracted_videos,
            'failed_videos': failed_videos
        }

        info_file = playlist_dir / "playlist_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(playlist_info, f, indent=2, ensure_ascii=False)

        # Create combined transcript
        combined_file = playlist_dir / f"{output_name}_combined.txt"
        self._create_combined_transcript(extracted_videos, combined_file)

        # Print summary
        print(f"\n{'='*60}")
        print(f"📋 Playlist extraction complete!")
        print(f"   ✅ Extracted: {len(extracted_videos)}/{total_videos} videos")
        if failed_videos:
            print(f"   ❌ Failed: {len(failed_videos)} videos")
        print(f"   📁 Output folder: {playlist_dir}")
        print(f"   📄 Combined transcript: {combined_file}")
        print(f"{'='*60}")

        return str(info_file), str(combined_file)

    def _create_combined_transcript(
        self,
        videos: List[Dict[str, Any]],
        output_file: Path
    ) -> None:
        """Create a single combined transcript from all videos."""
        with open(output_file, 'w', encoding='utf-8') as out_f:
            out_f.write("# Combined Playlist Transcript\n\n")
            out_f.write(f"Total videos: {len(videos)}\n\n")
            out_f.write("=" * 60 + "\n\n")

            for video in videos:
                video_title = video['title']
                text_file = video['text_file']

                out_f.write(f"## {video_title}\n\n")

                try:
                    with open(text_file, 'r', encoding='utf-8') as in_f:
                        content = in_f.read()
                        # Skip the header if present
                        if content.startswith("**Transcript"):
                            content = '\n'.join(content.split('\n')[2:])
                        out_f.write(content.strip())
                except Exception as e:
                    out_f.write(f"[Error reading transcript: {e}]")

                out_f.write("\n\n" + "-" * 40 + "\n\n")
