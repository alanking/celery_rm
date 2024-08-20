from .celery import app

import os

from irods.column import Criterion
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
	collection_members = []
	with iRODSSession(**delete_this_env) as session:
		data_object_query = session.query(Collection.name, DataObject.name).filter(
			Criterion('=', Collection.name, logical_path)
		)
		for result in data_object_query:
			collection_members.append('/'.join([result[Collection.name], result[DataObject.name]]))
		collection_query = session.query(Collection.name).filter(
			Criterion('=', Collection.parent_name, logical_path)
		)
		for result in collection_query:
			collection_members.append(result[Collection.name])
	return collection_members
