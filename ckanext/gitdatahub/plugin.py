import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from src.ckan_to_git import CKANGitClient

log = logging.getLogger(__name__)

class GitDataHubException(Exception):
    pass


class PackageGitdatahubPlugin(plugins.SingletonPlugin):
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
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        git_lfs_server_url = toolkit.config.get('ckanext.gitdatahub.git_lfs_server_url')
        try:
            client = CKANGitClient(token, pkg_dict)
            client.create_datapackage()
            client.create_gitattributes()
            client.create_lfsconfig(git_lfs_server_url)
        except Exception as e:
            log.exception('Cannot create {} repository.'.format(pkg_dict['name']))


    def after_update(self, context, pkg_dict):
        # We need to get a complete dict to also update resources data.
        pkg_dict = toolkit.get_action('package_show')(
            {},
            {'id': pkg_dict['id']}
        )
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, pkg_dict)
            client.update_datapackage()
        except Exception as e:
            log.exception('Cannot update {} repository.'.format(pkg_dict['name']))


    def delete(self, entity):
        pkg_dict = toolkit.get_action('package_show')(
            {},
            {'id': entity.id}
        )
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, pkg_dict)
            client.delete_repo()
        except Exception as e:
            log.exception('Cannot delete {} repository.'.format(entity.name))


class ResourceGitdatahubPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IResourceController, inherit=True)

    def after_create(self, context, resource):
        pkg_dict = toolkit.get_action('package_show')(
            {},
            {'id': resource['package_id']}
        )
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, pkg_dict)
            if resource['url_type'] == 'upload':
                client.create_lfspointerfile(resource)

        except Exception as e:
            log.exception('Cannot create {} lfspointerfile.'.format(resource['name']))


    def after_update(self, context, resource):
        pkg_dict = toolkit.get_action('package_show')(
            {},
            {'id': resource['package_id']}
        )
        token = toolkit.config.get('ckanext.gitdatahub.access_token')
        try:
            client = CKANGitClient(token, pkg_dict)
            client.update_lfspointerfile(resource)
        except Exception as e:
            log.exception('Cannot update {} lfspointerfile.'.format(resource['name']))


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
            client = CKANGitClient(token, pkg_dict)
            client.delete_lfspointerfile(resource_dict)
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
                client = CKANGitClient(token, pkg_dict)
                client.check_after_delete(resources)
            except Exception as e:
                log.exception('Cannot perfrom after_delete check')
