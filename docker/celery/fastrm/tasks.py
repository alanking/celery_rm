from .celery import app

import os

from irods.column import Criterion
from irods.exception import CollectionDoesNotExist, DataObjectDoesNotExist
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

@app.task
def remove_collection(logical_path):
	"""Remove all data objects in a collection and its subcollections."""
	with iRODSSession(**delete_this_env) as session:
		try:
			target_collection = session.collections.get(logical_path)
		except CollectionDoesNotExist:
			# Print an error message here because the exception doesn't tell you what doesn't exist.
			print(f"Collection [{logical_path}] does not exist.")
			raise
		data_objects_to_remove = []
		chunk_size = 50
		for data_object in target_collection.data_objects:
			data_objects_to_remove.append(data_object.path)
			if len(data_objects_to_remove) >= chunk_size - 1:
				remove_data_objects.delay(data_objects_to_remove)
				data_objects_to_remove = []
		if len(data_objects_to_remove) > 0:
			remove_data_objects.delay(data_objects_to_remove)
			data_objects_to_remove = []
		for subcollection in target_collection.subcollections:
			remove_collection.delay(subcollection.path)

		#remove_empty_collection.delay(logical_path)

@app.task
def remove_data_objects(logical_paths, no_trash=False):
	"""Remove a data object, optionally omitting rename to trash collection."""
	with iRODSSession(**delete_this_env) as session:
		for logical_path in logical_paths:
			try:
				session.data_objects.unlink(logical_path, force=not no_trash)
			except DataObjectDoesNotExist:
				print(f"Data object [{logical_path}] does not exist.")
				# raise
				continue

@app.task
def remove_empty_collection(logical_path, no_trash=False):
	with iRODSSession(**delete_this_env) as session:
		try:
			session.collections.remove(logical_path, recurse=False, force=not no_trash)
		except CollectionDoesNotExist:
			# Print an error message here because the exception doesn't tell you what doesn't exist.
			print(f"Collection [{logical_path}] does not exist.")
			raise
