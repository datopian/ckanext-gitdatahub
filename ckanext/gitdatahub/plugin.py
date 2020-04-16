import json
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanapi.datapackage import dataset_to_datapackage
from github import Github, GithubException
import hashlib

log = logging.getLogger(__name__)

class GitDataHubException(Exception):
    pass


class GitdatahubPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer
    def configure(self, config):
        # TODO: This doesn't work
        if not config['ckanext.gitdatahub.access_token']:
            msg = 'ckanext.gitdatahub.access_token is missing from config file'
            raise GitDataHubException(msg)

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'gitdatahub')

    def after_create(self, context, pkg_dict):
        log.info('################### After Create! ###################')
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            g = Github(token)
            auth_user = g.get_user()
            repo = auth_user.create_repo(pkg_dict['name'], pkg_dict['notes'])
            body = dataset_to_datapackage(pkg_dict)
            repo.create_file(
                'datapackage.json',
                'Create datapackage.json',
                json.dumps(body, indent=2)
                )
            repo.create_file(
                '.gitattributes',
                'Create .gitattributes',
                ''
                )
            git_lfs_server_url = toolkit.config.get('ckanext.gitdatahub.git_lfs_server_url')
            repoUrl = '{}/{}/{}'.format(git_lfs_server_url,auth_user.html_url.split('/')[-1],pkg_dict['name'])
            repo.create_file(
                '.lfsconfig',
                'Create .lfsconfig',
                '[remote "origin"]\n\tlfsurl = ' + repoUrl
                )            
        except Exception as e:
            log.exception('Cannot create {} repository.'.format(pkg_dict['name']))

    def after_update(self, context, pkg_dict):
        #TODO: What happens if user changes the package name? Should we create a new repo?
        # Get a complete dict to also save resources data.
        log.info('################### After Update! ###################')
        pkg_dict = toolkit.get_action('package_show')(
            {},
            {'id': pkg_dict['id']}
        )
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            g = Github(token)
            auth_user = g.get_user()
            repo = auth_user.get_repo(pkg_dict['name'])
            contents = repo.get_contents("datapackage.json")
            body = dataset_to_datapackage(pkg_dict)
            repo.update_file(
                contents.path,
                "Update datapackage.json",
                json.dumps(body, indent=2),
                contents.sha
                )
            try:
                lfs_pointers = [obj.name for obj in repo.get_contents("data")]
            except GithubException as e:
                lfs_pointers = list()

            gitattributes_body = ''
            for index, obj in enumerate(body['resources']):
                gitattributes_body += "data/{} filter=lfs diff=lfs merge=lfs -text\n".format(obj['title'])
                if obj['title'] not in lfs_pointers:
                    sha256 = pkg_dict['resources'][index]['id']
                    size = pkg_dict['resources'][index]['size']
                    lfs_pointer_body ='version https://git-lfs.github.com/spec/v1\noid sha256:{}\nsize {}\n'.format(sha256, size)
                    repo.create_file(
                        "data/{}".format(obj['title']),
                        "Create LfsPointerFile",
                        lfs_pointer_body,
                        )   

            contents = repo.get_contents(".gitattributes")
            repo.update_file(
                contents.path,
                "Update .gitattributes",
                gitattributes_body,
                contents.sha,
                )

        except Exception as e:
            log.exception('Cannot update {} repository.'.format(pkg_dict['name']))

    def delete(self, entity):
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            g = Github(token)
            auth_user = g.get_user()
            repo = auth_user.get_repo(entity.name)
            # Commented because dangerous to use with personal token
            repo.delete()
            log.info("{} repository deleted.".format(entity.name))
        except Exception as e:
            log.exception('Cannot delete {} repository.'.format(entity.name))
