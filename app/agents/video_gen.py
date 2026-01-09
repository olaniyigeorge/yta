import time
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Iterable
from concurrent.futures import ThreadPoolExecutor, as_completed

from google import genai

from config import AppConfig
from app.workflows.states import VideoAsset, YouTubeAutomationState

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class VideoGenerationAgent:
    """Agent to generate and download videos using Gemini (genai)."""

    def __init__(
        self,
        state: YouTubeAutomationState,
        api_key: Optional[str] = None,
        client: Optional[genai.Client] = None,
    ):
        # Prefer an injected client (testability); otherwise create one from AppConfig/env.
        self.client = client or genai.Client(
            api_key=api_key or AppConfig.GEMINI_API_KEY
        )
        self.videos: List[VideoAsset] = []

    def _poll_operation(
        self,
        operation: Any,
        timeout_seconds: int = 600,
        initial_sleep: float = 5.0,
        max_sleep: float = 30.0,
    ) -> Any:
        """Poll operation until done or timeout using exponential backoff."""
        start = time.time()
        sleep = initial_sleep
        while True:
            elapsed = time.time() - start
            if elapsed > timeout_seconds:
                logger.error(
                    "Video generation timed out after %s seconds", timeout_seconds
                )
                raise TimeoutError("Video generation timed out")

            try:
                operation = self.client.operations.get(operation)
            except Exception as exc:
                logger.exception("Failed to refresh operation status: %s", exc)
            if getattr(operation, "done", False):
                return operation

            logger.debug("Waiting %s seconds for video generation...", sleep)
            time.sleep(sleep)
            sleep = min(max_sleep, sleep * 1.5)

    def generate_video(
        self,
        frame_prompts: Optional[List[Dict[str, Any]]] = None,
        model: str = "veo-3.1-generate-preview",
        timeout_seconds: int = 600,
    ) -> Any:
        """Start video generation and poll until completion. Returns the completed operation."""
        if frame_prompts is None:
            raise ValueError("frame_prompts must be provided")

        try:
            operation = self.client.models.generate_videos(
                model=model, prompt=frame_prompts
            )
        except Exception as exc:
            logger.exception("Failed to start video generation: %s", exc)
            raise

        return self._poll_operation(operation, timeout_seconds=timeout_seconds)

    def download_video(
        self, operation: Any, out_dir: str = ".", filename: Optional[str] = None
    ) -> Path:
        """Download the first generated video from a completed operation and save it to disk."""
        # Validate operation response
        try:
            generated = getattr(operation, "response", None)
            vids = getattr(generated, "generated_videos", None) or []
            if not vids:
                raise RuntimeError("No generated videos found in operation response")
            generated_video = vids[0]
            file_ref = getattr(generated_video, "video", None)
            if file_ref is None:
                raise RuntimeError("Generated video has no video file reference")
        except Exception as exc:
            logger.exception("Invalid operation/response: %s", exc)
            raise

        out_dir_path = Path(out_dir)
        out_dir_path.mkdir(parents=True, exist_ok=True)
        safe_name = filename or "generated_video.mp4"
        out_path = out_dir_path.joinpath(safe_name)

        try:
            # Use SDK download helper if available; otherwise stream bytes if provided.
            self.client.files.download(file=file_ref)
            # Some SDK objects provide .save() on the file ref
            if hasattr(file_ref, "save"):
                file_ref.save(str(out_path))
            else:
                # Fallback: try to access bytes and write
                content = getattr(file_ref, "content", None)
                if content is None:
                    # Last resort: try SDK to return bytes
                    # (Depending on SDK, .download might have created a local file or returned bytes.)
                    raise RuntimeError(
                        "Unable to obtain binary content for the generated video"
                    )
                with open(out_path, "wb") as f:
                    f.write(content)
        except Exception as exc:
            logger.exception("Failed to download/save generated video: %s", exc)
            raise

        logger.info("Generated video saved to %s", out_path)
        return out_path

    def generate_and_download(
        self,
        frame_prompts: List[Dict[str, Any]],
        out_dir: str = ".",
        filename: Optional[str] = None,
        model: str = "veo-3.1-generate-preview",
        timeout_seconds: int = 600,
    ) -> Path:
        op = self.generate_video(
            frame_prompts=frame_prompts, model=model, timeout_seconds=timeout_seconds
        )
        return self.download_video(op, out_dir=out_dir, filename=filename)

    def generate_batch(
        self,
        list_of_prompts: Iterable[List[Dict[str, Any]]],
        max_workers: int = 4,
        out_dir: str = ".",
    ) -> List[Dict[str, Any]]:
        """Generate multiple videos in parallel. Returns list of result dicts with status and path/exception."""
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as exe:
            futures = {
                exe.submit(
                    self.generate_and_download, prompts, out_dir, f"video_{i}.mp4"
                ): (i, prompts)
                for i, prompts in enumerate(list_of_prompts)
            }
            for fut in as_completed(futures):
                i, prompts = futures[fut]
                try:
                    path = fut.result()
                    results.append({"index": i, "path": path, "success": True})
                except Exception as exc:
                    logger.exception("Batch item %s failed: %s", i, exc)
                    results.append({"index": i, "error": str(exc), "success": False})
        return results
