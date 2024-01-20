# P2-P3

## Requirements met
Most of P2's criterias were met.

- frontend receives a presigned url from the backend to upload a video to a S3 storage service
- chunks in the m3u8 playlist are replaced with presigned urls of the chunks
- chunking and processing of video, thumbnail extraction were done through workers and a redis queue
- was a working video platform where users could login, view, and manage their videos.
- comments, likes, views features were implemented
- comments, likes, views are all either eventually consistent or updated in real time by utilizing both RESTful apis and websockets
- notifications implemented but doesn't seem to be updating in real time