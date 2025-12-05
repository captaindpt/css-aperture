"""Whisper-based audio/video transcription extractor."""

import subprocess
from pathlib import Path
from typing import Optional, Tuple
import re
import os

from .base import ContentExtractor


class WhisperExtractor(ContentExtractor):
    """Extract transcriptions from audio/video files using OpenAI Whisper."""

    def __init__(self, output_dir: str = ".", model: str = "base", use_api: bool = False):
        """
        Initialize Whisper extractor.

        Args:
            output_dir: Base output directory
            model: Whisper model size (tiny, base, small, medium, large, turbo) for local
                   or API model (whisper-1, gpt-4o-transcribe) for API mode
            use_api: Use OpenAI API instead of local model (requires OPENAI_API_KEY)
        """
        super().__init__(output_dir)
        self.model = model
        self.use_api = use_api

        if use_api:
            self._check_api_available()
        else:
            self._check_whisper_installed()

    def _check_api_available(self):
        """Check if OpenAI API is configured."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OpenAI API key not found. Set it with:\n"
                "export OPENAI_API_KEY='your-api-key'\n"
                "Or use local model without --api flag"
            )

        try:
            import openai
        except ImportError:
            raise RuntimeError(
                "OpenAI Python library not installed. Install it with:\n"
                "pip install openai"
            )

    def _check_whisper_installed(self):
        """Check if Whisper is installed and install if needed."""
        try:
            subprocess.run(
                ["whisper", "--help"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "OpenAI Whisper is not installed. Install it with:\n"
                "pip install openai-whisper\n"
                "For GPU support, also install: pip install torch torchvision torchaudio"
            )

    def get_source_type(self) -> str:
        """Return the type of content this extractor handles."""
        return "audio/video"

    def get_content_info(self, source: str) -> Tuple[str, str]:
        """
        Get content information for naming.

        Args:
            source: Path to audio/video file

        Returns:
            Tuple of (clean_name, identifier)
        """
        source_path = Path(source)

        if not source_path.exists():
            raise FileNotFoundError(f"File not found: {source}")

        # Use filename (without extension) as base name
        base_name = source_path.stem

        # Clean the name for directory usage
        clean_name = re.sub(r'[^\w\s-]', '', base_name)
        clean_name = re.sub(r'[-\s]+', '_', clean_name)
        clean_name = clean_name.strip('_')

        # Use file extension as identifier
        identifier = source_path.suffix.lstrip('.')

        return clean_name, identifier

    def extract_content(
        self,
        source: str,
        output_name: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Transcribe audio/video file using Whisper.

        Args:
            source: Path to audio/video file
            output_name: Custom output name (optional)
            language: Language code (e.g., 'en', 'es', 'fr') - auto-detected if None
            **kwargs: Additional Whisper parameters

        Returns:
            Tuple of (transcript_file_path, transcript_file_path)
        """
        source_path = Path(source)

        if not source_path.exists():
            raise FileNotFoundError(f"File not found: {source}")

        print(f"\n🎤 Transcribing: {source_path.name}")
        print(f"📊 Mode: {'OpenAI API' if self.use_api else 'Local'}")
        print(f"📊 Model: {self.model}")
        if language:
            print(f"🌐 Language: {language}")

        # Get or create output name
        if not output_name:
            clean_name, identifier = self.get_content_info(source)
            output_name = f"{clean_name}_{identifier}"

        # Create output directory
        output_dir = self._create_output_directory(output_name)

        if self.use_api:
            return self._transcribe_with_api(source_path, output_dir, language)
        else:
            return self._transcribe_locally(source_path, output_dir, language)

    def _transcribe_with_api(
        self,
        source_path: Path,
        output_dir: Path,
        language: Optional[str]
    ) -> Tuple[str, str]:
        """Transcribe using OpenAI API."""
        import openai

        print(f"\n⚙️  Transcribing via OpenAI API...")
        print("   (This may take a moment depending on file size)")

        try:
            with open(source_path, "rb") as audio_file:
                # Use the appropriate model
                model = self.model if self.model in ["whisper-1", "gpt-4o-transcribe"] else "whisper-1"

                params = {
                    "model": model,
                    "file": audio_file,
                }

                if language:
                    params["language"] = language

                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                transcript = client.audio.transcriptions.create(**params)

            # Save transcript
            transcript_file = output_dir / f"{source_path.stem}.txt"
            transcript_file.write_text(transcript.text)

            print(f"\n✅ Transcription complete!")
            print(f"📁 Output: {transcript_file}")

            return str(transcript_file), str(transcript_file)

        except Exception as e:
            raise RuntimeError(f"API transcription failed: {str(e)}")

    def _transcribe_locally(
        self,
        source_path: Path,
        output_dir: Path,
        language: Optional[str]
    ) -> Tuple[str, str]:
        """Transcribe using local Whisper model."""
        # Build Whisper command
        cmd = [
            "whisper",
            str(source_path),
            "--model", self.model,
            "--output_dir", str(output_dir),
            "--output_format", "txt",
            "--verbose", "False"
        ]

        if language:
            cmd.extend(["--language", language])

        # Run Whisper transcription
        print(f"\n⚙️  Running local Whisper transcription...")
        print("   (This may take a few minutes depending on file size and model)")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Whisper creates output file with same name as input
            transcript_file = output_dir / f"{source_path.stem}.txt"

            if not transcript_file.exists():
                raise RuntimeError(
                    f"Transcription failed. Expected output not found: {transcript_file}\n"
                    f"Whisper output: {result.stdout}\n{result.stderr}"
                )

            print(f"\n✅ Transcription complete!")
            print(f"📁 Output: {transcript_file}")

            return str(transcript_file), str(transcript_file)

        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Whisper transcription failed:\n"
                f"stdout: {e.stdout}\n"
                f"stderr: {e.stderr}"
            )


class WhisperYouTubeExtractor(ContentExtractor):
    """Download YouTube video and transcribe using Whisper."""

    def __init__(self, output_dir: str = ".", model: str = "base", use_api: bool = False):
        """
        Initialize YouTube+Whisper extractor.

        Args:
            output_dir: Base output directory
            model: Whisper model size
            use_api: Use OpenAI API instead of local model
        """
        super().__init__(output_dir)
        self.model = model
        self.use_api = use_api
        self._check_dependencies()

        if use_api:
            self._check_api_available()

    def _check_api_available(self):
        """Check if OpenAI API is configured."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OpenAI API key not found. Set it with:\n"
                "export OPENAI_API_KEY='your-api-key'\n"
                "Or use local model without --api flag"
            )

        try:
            import openai
        except ImportError:
            raise RuntimeError(
                "OpenAI Python library not installed. Install it with:\n"
                "pip install openai"
            )

    def _check_dependencies(self):
        """Check if required tools are installed."""
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("yt-dlp is not installed. Install it with: pip install yt-dlp")

        try:
            subprocess.run(["whisper", "--help"], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("OpenAI Whisper is not installed. Install it with: pip install openai-whisper")

    def get_source_type(self) -> str:
        """Return the type of content this extractor handles."""
        return "youtube_whisper"

    def get_content_info(self, source: str) -> Tuple[str, str]:
        """
        Get YouTube video information.

        Args:
            source: YouTube URL

        Returns:
            Tuple of (clean_title, video_id)
        """
        # Extract video ID
        video_id_match = re.search(r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})', source)
        if not video_id_match:
            raise ValueError(f"Invalid YouTube URL: {source}")
        video_id = video_id_match.group(1)

        # Get video title
        try:
            result = subprocess.run(
                ["yt-dlp", "--get-title", source],
                capture_output=True,
                text=True,
                check=True,
                timeout=30
            )
            title = result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            title = "YouTube_Video"

        # Clean title for directory name
        clean_title = re.sub(r'[^\w\s-]', '', title)
        clean_title = re.sub(r'[-\s]+', '_', clean_title)
        clean_title = clean_title.strip('_')[:100]  # Limit length

        return clean_title, video_id

    def extract_content(
        self,
        source: str,
        output_name: Optional[str] = None,
        language: Optional[str] = None,
        **kwargs
    ) -> Tuple[str, str]:
        """
        Download YouTube video and transcribe using Whisper.

        Args:
            source: YouTube URL
            output_name: Custom output name (optional)
            language: Language code for transcription
            **kwargs: Additional parameters

        Returns:
            Tuple of (transcript_file_path, transcript_file_path)
        """
        print(f"\n📺 Downloading YouTube video: {source}")

        # Get or create output name
        if not output_name:
            clean_title, video_id = self.get_content_info(source)
            output_name = f"{clean_title}_{video_id}"

        # Create output directory
        output_dir = self._create_output_directory(output_name)

        # Download audio only
        audio_file = output_dir / "audio.m4a"
        print(f"⬇️  Downloading audio...")

        try:
            subprocess.run(
                [
                    "yt-dlp",
                    "-f", "bestaudio[ext=m4a]",
                    "-o", str(audio_file),
                    source
                ],
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to download video: {e.stderr}")

        if not audio_file.exists():
            raise RuntimeError(f"Audio download failed. File not found: {audio_file}")

        print(f"✅ Audio downloaded: {audio_file}")

        # Transcribe with Whisper
        print(f"\n🎤 Transcribing with Whisper...")
        print(f"📊 Mode: {'OpenAI API' if self.use_api else 'Local'}")
        print(f"📊 Model: {self.model}")
        if language:
            print(f"🌐 Language: {language}")

        if self.use_api:
            final_transcript = self._transcribe_with_api(audio_file, output_dir, output_name, language)
        else:
            final_transcript = self._transcribe_locally(audio_file, output_dir, output_name, language)

        # Optional: clean up audio file to save space
        # audio_file.unlink()

        return str(final_transcript), str(final_transcript)

    def _transcribe_with_api(
        self,
        audio_file: Path,
        output_dir: Path,
        output_name: str,
        language: Optional[str]
    ) -> Path:
        """Transcribe using OpenAI API."""
        import openai

        print(f"\n⚙️  Transcribing via OpenAI API...")

        try:
            with open(audio_file, "rb") as f:
                model = self.model if self.model in ["whisper-1", "gpt-4o-transcribe"] else "whisper-1"

                params = {
                    "model": model,
                    "file": f,
                }

                if language:
                    params["language"] = language

                client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                transcript = client.audio.transcriptions.create(**params)

            # Save transcript
            final_transcript = output_dir / f"{output_name}.txt"
            final_transcript.write_text(transcript.text)

            print(f"\n✅ Transcription complete!")
            print(f"📁 Transcript: {final_transcript}")

            return final_transcript

        except Exception as e:
            raise RuntimeError(f"API transcription failed: {str(e)}")

    def _transcribe_locally(
        self,
        audio_file: Path,
        output_dir: Path,
        output_name: str,
        language: Optional[str]
    ) -> Path:
        """Transcribe using local Whisper model."""
        cmd = [
            "whisper",
            str(audio_file),
            "--model", self.model,
            "--output_dir", str(output_dir),
            "--output_format", "txt",
            "--verbose", "False"
        ]

        if language:
            cmd.extend(["--language", language])

        print(f"\n⚙️  Running local Whisper transcription...")

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)

            transcript_file = output_dir / "audio.txt"

            if not transcript_file.exists():
                raise RuntimeError(f"Transcription failed. Expected output not found: {transcript_file}")

            # Rename transcript to match output name
            final_transcript = output_dir / f"{output_name}.txt"
            transcript_file.rename(final_transcript)

            print(f"\n✅ Transcription complete!")
            print(f"📁 Transcript: {final_transcript}")

            return final_transcript

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Whisper transcription failed: {e.stderr}")
