# celery_rm

This project is an experimental Celery application. It is meant for educating myself about Celery and to eventually demonstrate a fully parallel, recursive removal tool for iRODS collections and data objects. It is like the reverse of the iRODS Automated Ingest Capability: https://github.com/irods/irods_capability_automated_ingest

## Run with Docker Compose

Run the Docker Compose project like this:
```bash
docker compose --project-directory docker up --build
```

## Celery project

Currently, the Celery project is structed like this:
```
docker/celery/fastrm/
├── celery.py
├── __init__.py
└── tasks.py
```

`celery.py` contains the Celery instance (and its attendant configuration).

`tasks.py` contains the Celery tasks which can be invoked from a client application. Currently, a hard-coded iRODS client environment sits in this module and is the means by which the application authenticates with iRODS.

## Usage

### `list_collection`

`list_collection` lists the contents in the collection specified by `logical_path`:
```python
>>> from .fastrm.tasks import list_collection
>>> list_collection('/tempZone/home/')
['/tempZone/home/public', '/tempZone/home/rods']
>>> result = list_collection.delay('/tempZone/home/')
>>> result.get() # this requires that a Celery backend has been configured
['/tempZone/home/public', '/tempZone/home/rods']
```
