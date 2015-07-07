import pyblish.api
import ftrack


@pyblish.api.log
class ExtractFtrack(pyblish.api.Extractor):

    """ Creating any Asset or AssetVersion in Ftrack.
    """

    label = 'Ftrack'

    def process(self, instance, context):

        # skipping instance if ftrackData isn't present
        if not context.has_data('ftrackData'):
            self.log.info('No ftrackData present. Skipping this instance')
            return

        # skipping instance if ftrackComponents isn't present
        if not instance.has_data('ftrackComponents'):
            self.log.info('No ftrackComponents found. Skipping this instance')
            return

        ftrack_data = context.data('ftrackData').copy()
        task = ftrack.Task(ftrack_data['Task']['id'])
        parent = task.getParent()
        asset_data = None
        create_version = False

        # creating asset
        if instance.data('ftrackAssetCreate'):
            asset = None

            # creating asset from ftrackAssetName
            if instance.has_data('ftrackAssetName'):

                asset_name = instance.data('ftrackAssetName')

                if instance.has_data('ftrackAssetType'):
                    asset_type = instance.data('ftrackAssetType')
                else:
                    asset_type = ftrack_data['Task']['code']

                asset = parent.createAsset(name=asset_name,
                                           assetType=asset_type, task=task)

                msg = "Creating new asset cause ftrackAssetName"
                msg += " (\"%s\") doesn't exist." % asset_name
                self.log.info(msg)
            else:
                # creating a new asset
                asset_name = ftrack_data['Task']['type']
                asset_type = ftrack_data['Task']['code']
                asset = parent.createAsset(name=asset_type,
                                           assetType=asset_type, task=task)

                msg = "Creating asset cause no asset is present."
                self.log.info(msg)

            create_version = True
            # adding asset to ftrack data
            asset_data = {'id': asset.getId(),
                          'name': asset.getName()}

        if not asset_data:
            asset_data = instance.data('ftrackAsset')

        instance.set_data('ftrackAsset', value=asset_data)

        # creating version
        version = None
        if instance.data('ftrackAssetVersionCreate') or create_version:
            asset = ftrack.Asset(asset_data['id'])
            taskid = ftrack_data['Task']['id']
            version_number = int(context.data('version'))

            try:
                version = asset.createVersion(comment='', taskid=taskid)
                version.set('version', value=version_number)
            except:
                version = self.GetVersionByNumber(asset, version_number)

            asset_version = {'id': version.getId(), 'number': version_number}
            instance.set_data('ftrackAssetVersion', value=asset_version)
            version.publish()

            self.log.info('Creating new asset version by %s.' % version_number)
        else:
            # using existing version
            asset_version = instance.data('ftrackAssetVersion')
            version = ftrack.AssetVersion(asset_version['id'])

        # adding asset version to ftrack data
        instance.set_data('ftrackAssetVersion', value=asset_version)

    def GetVersionByNumber(self, asset, number):
        for version in asset.getVersions():
            try:
                if version.getVersion() == int(number):
                    return version
            except:
                return None
