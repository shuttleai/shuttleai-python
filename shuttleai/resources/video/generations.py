from functools import cached_property
from typing import Generic, Optional, Type, TypeVar, cast

from shuttleai.client.base import ClientBase
from shuttleai.resources.common import AsyncResource, SyncResource, T
from shuttleai.schemas.video.generations import VideoGenerationResponse, VideoJobResponse


class AsyncGenerations(AsyncResource):
    async def generate(
        self,
        prompt: str,
        model: str = "sora",
        width: int = 480,
        height: int = 480,
        n_seconds: int = 5,
        # n_variants: Optional[int] = 1,
    ) -> VideoGenerationResponse:
        """Create a video generation job.

        Args:
            prompt: The prompt to generate the video from
            model: The model to use for video generation (default: "sora")
            width: The width of the video in pixels (default: 480)
            height: The height of the video in pixels (default: 480)
            n_seconds: The duration of the video in seconds (default: 5)
            # n_variants: The number of video variants to generate (default: 1) (unused for now)

        Returns:
            VideoGenerationResponse: The job creation response
        """
        request = self._client._make_video_request(
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            n_seconds=n_seconds,
            # n_variants=n_variants,
        )

        response = await self.handle_request(
            method="post",
            endpoint="/video/generations/jobs",
            request_data=request,
            response_cls=VideoGenerationResponse,
        )
        return cast(VideoGenerationResponse, response)

    async def get_job_status(self, job_id: str) -> VideoJobResponse:
        """Get the status of a video generation job.

        Args:
            job_id: The ID of the video generation job

        Returns:
            VideoJobResponse: The job status response
        """
        response = await self.handle_request(
            method="get",
            endpoint=f"/video/generations/jobs/{job_id}",
            response_cls=VideoJobResponse,
        )
        return cast(VideoJobResponse, response)

    async def get_video_content(self, generation_id: str) -> bytes:
        """Get the video content as bytes.

        Args:
            generation_id: The ID of the generated video

        Returns:
            bytes: The video content as bytes
        """
        response = await self._client._raw_request(
            method="get",
            json=None,
            path=f"/video/generations/{generation_id}/content/video",
            accept_header="application/octet-stream",
        )

        return await response.read()


class SyncGenerations(SyncResource):
    def generate(
        self,
        prompt: str,
        model: str = "sora",
        width: int = 480,
        height: int = 480,
        n_seconds: int = 5,
        # n_variants: Optional[int] = 1,
    ) -> VideoGenerationResponse:
        """Create a video generation job.

        Args:
            prompt: The prompt to generate the video from
            model: The model to use for video generation (default: "sora")
            width: The width of the video in pixels (default: 480)
            height: The height of the video in pixels (default: 480)
            n_seconds: The duration of the video in seconds (default: 5)
            # n_variants: The number of video variants to generate (default: 1)

        Returns:
            VideoGenerationResponse: The job creation response
        """
        request = self._client._make_video_request(
            prompt=prompt,
            model=model,
            width=width,
            height=height,
            n_seconds=n_seconds,
            # n_variants=n_variants,
        )
        response = self.handle_request(
            method="post",
            endpoint="/video/generations/jobs",
            request_data=request,
            response_cls=VideoGenerationResponse,
        )
        return cast(VideoGenerationResponse, response)

    def get_job_status(self, job_id: str) -> VideoJobResponse:
        """Get the status of a video generation job.

        Args:
            job_id: The ID of the video generation job

        Returns:
            VideoJobResponse: The job status response
        """
        response = self.handle_request(
            method="get",
            request_data=None,
            endpoint=f"/video/generations/jobs/{job_id}",
            response_cls=VideoJobResponse,
        )
        return cast(VideoJobResponse, response)

    def get_video_content(self, generation_id: str) -> bytes:
        """Get the video content as bytes.

        Args:
            generation_id: The ID of the generated video

        Returns:
            bytes: The video content as bytes
        """
        response = self._client._raw_request(
            method="get",
            json=None,
            path=f"/video/generations/{generation_id}/content/video",
            accept_header="application/octet-stream",
        )
        return response.read()


GenerationsType = TypeVar("GenerationsType", SyncGenerations, AsyncGenerations)


class BaseVideo(Generic[T, GenerationsType]):
    _client: T
    _generations_class: Type[GenerationsType]
    _generations: Optional[GenerationsType]

    def __init__(self, client: T, generations_class: Type[GenerationsType]) -> None:
        self._client = client
        self._generations_class = generations_class
        self._generations = None

    @cached_property
    def generations(self) -> GenerationsType:
        if self._generations is None:
            self._generations = self._generations_class(self._client)
        return self._generations


class Video(BaseVideo[ClientBase, SyncGenerations]):
    def __init__(self, client: ClientBase) -> None:
        super().__init__(client, SyncGenerations)


class AsyncVideo(BaseVideo[ClientBase, AsyncGenerations]):
    def __init__(self, client: ClientBase) -> None:
        super().__init__(client, AsyncGenerations)
