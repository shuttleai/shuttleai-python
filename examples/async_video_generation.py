#!/usr/bin/env python

import asyncio

from shuttleai import AsyncShuttleAI


async def main() -> None:
    # Initialize the async ShuttleAI client
    client = AsyncShuttleAI()

    # Create a video generation job
    prompt = "A serene sunset over a calm ocean with gentle waves"
    video_response = await client.video.generations.generate(
        prompt=prompt,
        model="sora",
        width=480,
        height=480,
        n_seconds=5
    )
    print(f"Video generation job created with ID: {video_response.id}")
    print(f"Initial status: {video_response.status}")

    # Poll for job status until completion or failure
    job_id = video_response.id
    while True:
        status_response = await client.video.generations.get_job_status(job_id)
        print(f"Job status: {status_response.status}")

        if status_response.is_completed:
            if status_response.first_video and status_response.first_video.video_url:
                print(f"Video generated successfully! URL: {status_response.first_video.video_url}")
                # Save the video to a file
                status_response.first_video.to_file("output_video.mp4")
                print("Video saved to output_video.mp4")
            else:
                print("No video URL available.")
            break
        elif status_response.has_failed:
            print("Video generation job failed.")
            break
        else:
            print("Job still processing, waiting...")
            await asyncio.sleep(5)  # Wait before polling again

if __name__ == "__main__":
    asyncio.run(main())
