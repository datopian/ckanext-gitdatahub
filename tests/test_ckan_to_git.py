import json
import datetime
from ckanapi.datapackage import dataset_to_datapackage
from src.ckan_to_git import CKANGitClient
import ckan.plugins.toolkit as toolkit

from github import Github


pkg_dict = {'maintainer': '', 'name': 'ckan_to_git_test_repo', 'relationships_as_subject': [], 'author': '',
'author_email': '', 'title': 'testing', 'notes': '', 'owner_org': 'd9e7f375-f540-4699-9054-dc5613dfa4e3',
'private': True, 'maintainer_email': '', 'url': '', 'state': 'draft', 'version': '', 'groups': [],
'relationships_as_object': [], 'license_id': 'cc-by', 'tags': [], 'type': 'dataset',
'id': 'cee102b6-9e67-41b2-9558-46c9fe8fbe34', 'resources': [{'mimetype': 'text/csv', 'description': '',
'format': 'CSV', 'url': 'testing_resource.csv', 'name': 'testing_resource.csv', 'package_id': 'cee102b6-9e67-41b2-9558-46c9fe8fbe34',
'last_modified': datetime.datetime(2020, 4, 19, 12, 15, 48, 33024), 'url_type': 'upload',
'id': 'cc82cc39-3e66-4f77-bb34-fc90566fc612', 'size': 1024, 'sha256': '1234'}], 'extras': []}

token = toolkit.config.get('ckanext.gitdatahub.access_token')
client = CKANGitClient(token, pkg_dict)

class Test:
    def test_create_datapackage(self):
        client.create_datapackage()

        body = dataset_to_datapackage(pkg_dict)
        repo_file_contents = client.repo.get_contents("datapackage.json").decoded_content
        datapackage_body = bytes(json.dumps(body, indent=2), 'UTF-8')

        assert repo_file_contents == datapackage_body

    def test_create_gitattributes(self):
        client.create_gitattributes()

        repo_file_contents = client.repo.get_contents(".gitattributes").decoded_content
        gitattributes_body = bytes('data/* filter=lfs diff=lfs merge=lfs -text\n', 'UTF-8')

        assert repo_file_contents == gitattributes_body

    def test_create_lfsconfig(self):
        git_lfs_server_url = toolkit.config.get('ckanext.gitdatahub.git_lfs_server_url')
        client.create_lfsconfig(git_lfs_server_url)

        repo_file_contents = client.repo.get_contents(".lfsconfig").decoded_content
        lfsconfig_body = bytes('[remote "origin"]\n\tlfsurl = ' +
                            '{}/{}/{}'.format(git_lfs_server_url,client.auth_user.html_url.split('/')[-1],pkg_dict['name']), 'UTF-8')

        assert repo_file_contents == lfsconfig_body

    def test_create_lfspointerfile(self):
        obj = {'mimetype': 'text/csv', 'description': '',
                'format': 'CSV', 'url': 'testing_resource.csv', 'name': 'testing_resource.csv', 'package_id': 'cee102b6-9e67-41b2-9558-46c9fe8fbe34',
                'last_modified': datetime.datetime(2020, 4, 19, 12, 15, 48, 33024), 'url_type': 'upload',
                'id': 'cc82cc39-3e66-4f77-bb34-fc90566fc612', 'size': 1024, 'sha256': '1234'}
        client.create_lfspointerfile(obj)

        lfspointer_name = obj['id']+ '.' + obj['format']
        repo_file_contents = client.repo.get_contents("data/{}".format(lfspointer_name)).decoded_content
        lfs_pointer_body = bytes('version https://git-lfs.github.com/spec/v1\noid sha256:{}\nsize {}\n'.format(obj['sha256'], obj['size']), 'UTF-8')

        assert repo_file_contents == lfs_pointer_body

    def test_update_lfspointerfile(self):
        obj = {'mimetype': 'text/csv', 'description': '',
                'format': 'CSV', 'url': 'testing_resource.csv', 'name': 'testing_resource.csv', 'package_id': 'cee102b6-9e67-41b2-9558-46c9fe8fbe34',
                'last_modified': datetime.datetime(2020, 4, 19, 12, 15, 48, 33024), 'url_type': 'upload',
                'id': 'cc82cc39-3e66-4f77-bb34-fc90566fc612', 'size': 1024, 'sha256': '4321'}
        client.update_lfspointerfile(obj)

        lfspointer_name = obj['id']+ '.' + obj['format']
        repo_file_contents = client.repo.get_contents("data/{}".format(lfspointer_name)).decoded_content
        lfs_pointer_body = bytes('version https://git-lfs.github.com/spec/v1\noid sha256:{}\nsize {}\n'.format(obj['sha256'], obj['size']), 'UTF-8')

        assert repo_file_contents == lfs_pointer_body

    def test_update_datapackage(self):
        client.update_datapackage()

        body = dataset_to_datapackage(pkg_dict)
        repo_file_contents = client.repo.get_contents("datapackage.json").decoded_content
        datapackage_body = bytes(json.dumps(body, indent=2), 'UTF-8')

        assert repo_file_contents == datapackage_body

    def test_check_after_unsuccessful_deletion(self):
        resources = [{'mimetype': 'text/csv', 'description': '',
        'format': 'CSV', 'url': 'testing_resource.csv', 'name': 'testing_resource.csv', 'package_id': 'cee102b6-9e67-41b2-9558-46c9fe8fbe34',
        'last_modified': datetime.datetime(2020, 4, 19, 12, 15, 48, 33024), 'url_type': 'upload',
        'id': 'cc82cc39-3e66-4f77-bb34-fc90566fc612', 'size': 1024, 'sha256': '1234'}]

        assert client.check_after_delete(resources) == False

    def test_delete_lfspointerfile(self):
        obj = {'mimetype': 'text/csv', 'description': '',
                'format': 'CSV', 'url': 'testing_resource.csv', 'name': 'testing_resource.csv', 'package_id': 'cee102b6-9e67-41b2-9558-46c9fe8fbe34',
                'last_modified': datetime.datetime(2020, 4, 19, 12, 15, 48, 33024), 'url_type': 'upload',
                'id': 'cc82cc39-3e66-4f77-bb34-fc90566fc612', 'size': 1024, 'sha256': '1234'}
        lfspointer_name = obj['id']+ '.' + obj['format']

        assert client.delete_lfspointerfile(lfspointer_name) == True

    def test_check_after_successful_deletion(self):
        resources = [{'mimetype': 'text/csv', 'description': '',
        'format': 'CSV', 'url': 'testing_resource.csv', 'name': 'testing_resource.csv', 'package_id': 'cee102b6-9e67-41b2-9558-46c9fe8fbe34',
        'last_modified': datetime.datetime(2020, 4, 19, 12, 15, 48, 33024), 'url_type': 'upload',
        'id': 'cc82cc39-3e66-4f77-bb34-fc90566fc612', 'size': 1024, 'sha256': '1234'}]

        assert client.check_after_delete(resources) == True

    def test_delete_repo(self):
        assert client.delete_repo() == True

