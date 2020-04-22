import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from src.ckan_to_git import CKANGitClient

log = logging.getLogger(__name__)

class GitDataHubException(Exception):
    pass


class GitdatahubPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)

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
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, pkg_dict)

            # Create the datapackage
            client.create_datapackage()

            # Create the gitattributes
            client.create_gitattributes()

            # Create the lfscomfig
            git_lfs_server_url = toolkit.config.get('ckanext.gitdatahub.git_lfs_server_url')
            client.create_lfsconfig(git_lfs_server_url)

        except Exception as e:
            log.exception('Cannot create {} repository.'.format(pkg_dict['name']))

    def after_update(self, context, pkg_dict):
        # Get a complete dict to also save resources data.
        pkg_dict = toolkit.get_action('package_show')(
            {},
            {'id': pkg_dict['id']}
        )
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, pkg_dict)

            # Update the datapackage
            client.update_datapackage()

        except Exception as e:
            log.exception('Cannot update {} repository.'.format(pkg_dict['name']))

        # Create/Update the lfs pointers
        client.create_or_update_lfspointerfile()

    def before_delete(self, context, resource, resources):
        for obj in resources:
            if obj['id'] == resource['id']:
                resource_dict = obj
                break

        pkg_dict = toolkit.get_action('package_show')(
            {},
            {'id': resource_dict['package_id']}
        )
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, dataset_name=pkg_dict['name'])
            client.delete_lfspointerfile(resource_dict['name'])

        except Exception as e:
            log.exception('Cannot delete {} lfspointerfile.'.format(resource_dict['name']))

    def after_delete(self, context, resources):
        if resources:
            pkg_dict = toolkit.get_action('package_show')(
                {},
                {'id': resources[0]['package_id']}
            )
            token = toolkit.config.get('ckanext.gitdatahub.access_token')
            try:
                #Checking whether the resoource is deleted from the database
                #And there is no difference between the lfspointerfiles in repo and resouces in database
                client = CKANGitClient(token, dataset_name=pkg_dict['name'])
                client.check_after_delete(resources)

            except Exception as e:
                log.exception('Cannot perfrom after_delete check .')

    def delete(self, entity):
        return
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, dataset_name=entity.name)
            # Commented because dangerous to use with personal token
            client.delete_repo()

        except Exception as e:
            log.exception('Cannot delete {} repository.'.format(entity.name))

