# streameasy

- frontend receives a presigned url from the backend to upload a video to a S3 storage service
- the m3u8 playlist contains presigned urls of the chunks stored in S3
- chunking and processing of video, thumbnail extraction were done through workers and a redis queue
- video hosting platform where users can login, view, and manage their videos.