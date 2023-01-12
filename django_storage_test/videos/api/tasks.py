import requestsfrom celery import shared_task@shared_taskdef upload_video(url, file):    with open(file, "rb") as f:        requests.put(url, data=f)
