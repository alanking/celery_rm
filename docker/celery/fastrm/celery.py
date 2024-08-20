from celery import Celery

app = Celery('fastrm')

app.conf.update(
	broker_url=f'redis://redis',
	backend=f'redis://redis',
	task_serializer='json',
	include=['fastrm.tasks']
)

if __name__ == '__main__':
	app.start()
