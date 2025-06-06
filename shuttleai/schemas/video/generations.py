from datetime import datetime
from typing import List, Literal, Optional, Union

from pydantic import BaseModel


class VideoGeneration(BaseModel):
    id: str
    """The unique identifier for the generated video."""

    output: dict
    """The output containing the video_url."""

    @property
    def video_url(self) -> Optional[str]:
        """Get the video URL from the output."""
        return self.output.get("video_url")

    def to_file(self, path: str) -> None:
        """Save the video to a file.

        Args:
            path (str): The path to save the video to.
        """
        if not self.video_url:
            raise ValueError("No video URL available")

        import httpx  # TODO: fix to make it async compatible

        response = httpx.get(self.video_url)
        response.raise_for_status()
        with open(path, "wb") as file:
            file.write(response.content)

    def to_bytes(self) -> bytes:
        """Get the video as bytes.

        Returns:
            bytes: The video as bytes.
        """
        if not self.video_url:
            raise ValueError("No video URL available")

        import httpx

        response = httpx.get(self.video_url)
        response.raise_for_status()
        return response.content

    def __str__(self) -> str:
        return self.video_url or "No video URL available"


class VideoGenerationResponse(BaseModel):
    id: str
    """The unique identifier for the video generation job."""

    status: Literal["queued", "preprocessing", "processing", "running", "completed", "failed"]
    """The current status of the video generation job."""

    created_at: Union[datetime, str]
    """The timestamp when the job was created."""


class VideoJobResponse(BaseModel):
    id: str
    """The unique identifier for the video generation job."""

    status: Literal["queued", "preprocessing", "processing", "running", "succeeded", "failed", "unknown"]
    """The current status of the video generation job."""

    generations: Optional[List[VideoGeneration]] = None
    """The list of generated videos (only present when status is 'succeeded')."""

    @property
    def first_video(self) -> Optional[VideoGeneration]:
        """Get the first generated video."""
        if self.generations and len(self.generations) > 0:
            return self.generations[0]
        return None

    @property
    def is_completed(self) -> bool:
        """Check if the job is completed successfully."""
        return self.status == "succeeded"

    @property
    def has_failed(self) -> bool:
        """Check if the job has failed."""
        return self.status == "failed"
