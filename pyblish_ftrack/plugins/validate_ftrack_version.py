import pyblish.api

import ftrack

@pyblish.api.log
class ValidateFtrackVersion(pyblish.api.Validator):
    """ Validates whether ftrack version with matching version number exists

        Arguments:
            ftrackData (dictionary): Necessary ftrack information gathered by select_ftrack
    """

    families = ['*']
    hosts = ['*']
    version = (0, 1, 0)
    optional = True

    def process_instance(self, instance):

        if instance.context.data('ftrackData')['version']['number']:

            versionNumber = instance.context.data('ftrackData')['version']['number']

            asset = ftrack.Asset(id=instance.context.data('ftrackData')['asset']['id'])

            version = None
            for v in asset.getVersions():
                if int(v.getVersion()) == int(versionNumber):
                    if not v.get('ispublished'):
                        version = v
                        instance.context.set_data('ftrackVersionID', value=version.getId())
                        raise pyblish.api.ValidationError('This version already exists, but is not visible in the UI.')
                    else:
                        version = v
                        instance.context.set_data('ftrackVersionID', value=version.getId())
                        self.log.warning('This version already exists. Will check for existence of  components')

            if not version:
                instance.context.set_data('createFtrackVersion', value=True)
                self.log.info('Setting createFtrackVersion arguments')

        else:
            self.log.warning('Missing version in instance data')