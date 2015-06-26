import pyblish.api

import ftrack


@pyblish.api.log
class ExtractFtrack(pyblish.api.Extractor):
    """ Creating any Asset or AssetVersion in Ftrack.
    """

    label = 'Ftrack'

    def process(self, instance):

        # skipping instance if ftrackData isn't present
        if not instance.context.has_data('ftrackData'):
            self.log.info('No ftrackData present. Skipping this instance')
            return

        # skipping instance if ftrackComponents isn't present
        if not instance.has_data('ftrackComponents'):
            self.log.info('No ftrackComponents found. Skipping this instance')
            return

        ftrack_data = instance.context.data('ftrackData').copy()
        task = ftrack.Task(ftrack_data['Task']['id'])
        parent = task.getParent()

        # creating asset
        if instance.context.data('ftrackAssetCreate'):
            asset = None

            # creating asset from ftrackAssetName
            if instance.context.has_data('ftrackAssetName'):

                asset_name = instance.context.data('ftrackAssetName')
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

            # adding asset to ftrack data
            ftrack_data['Asset'] = {'id': asset.getId(),
                                    'name': asset.getName()}

        # creating version
        version = None
        if instance.context.data('ftrackAssetVersionCreate'):
            asset = ftrack.Asset(ftrack_data['Asset']['id'])
            taskid = ftrack_data['Task']['id']
            version_number = int(instance.context.data('version'))

            version = asset.createVersion(comment='', taskid=taskid)
            version.set('version', value=version_number)
            ftrack_data['AssetVersion'] = {'id': version.getId(),
                                           'number': version_number}
            version.publish()

            self.log.info('Creating new asset version by %s.' % version_number)
        else:
            # using existing version
            version = ftrack.AssetVersion(ftrack_data['AssetVersion']['id'])

        # adding asset to ftrack data
        ftrack_data['AssetVersion'] = {'id': version.getId()}

        # setting ftrackData
        instance.context.set_data('ftrackData', value=ftrack_data)
