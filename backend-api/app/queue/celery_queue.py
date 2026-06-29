from app.queue.base import QueueService
from app.worker.celery_app import celery_app


class CeleryQueueService(QueueService):
    def enqueue_analysis_job(self, message: dict) -> None:
        celery_app.send_task("app.worker.tasks.process_analysis_job", args=[message], queue="celery")


queue_service = CeleryQueueService()
