from .celery import app

import os

from irods.column import Criterion
from irods.exception import CollectionDoesNotExist
from irods.models import DataObject, DataObjectMeta, Collection, CollectionMeta
from irods.session import iRODSSession

delete_this_env = {
	'host': 'fastrm-irods-catalog-provider-1',
	'port': 1247,
	'zone': 'tempZone',
	'user': 'rods',
	'password': 'rods'
}
env_file = os.path.expanduser('~/.irods/irods_environment.json')

@app.task
def list_collection(logical_path, recursive=False):
	"""Return a dict with "data_objects" and "subcollections" in the collection at `logical_path`."""
	with iRODSSession(**delete_this_env) as session:
		try:
			target_collection = session.collections.get(logical_path)
		except CollectionDoesNotExist:
			# Print an error message here because the exception doesn't tell you what doesn't exist.
			print(f"Collection [{logical_path}] does not exist.")
			raise
		data_objects = target_collection.data_objects
		subcollections = target_collection.subcollections
		for subcollection in subcollections:
			list_collection.delay(subcollection.path)
	return {
		"data_objects": [do.path for do in data_objects],
		"subcollections": [sc.path for sc in subcollections]
	}
