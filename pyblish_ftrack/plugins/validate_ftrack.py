import pyblish.api

import ftrack

@pyblish.api.log
class ValidateFtrack(pyblish.api.Validator):
    """ Validate the existence of Asset, AssetVersion and Components.
    """

    optional = True
    label = 'Ftrack'

    def process(self, instance):

        # skipping instance if ftrackData isn't present
        if not instance.context.has_data('ftrackData'):
            self.log.info('No ftrackData present. Skipping this instance')
            return

        # skipping instance if ftrackComponents isn't present
        if not instance.has_data('ftrackComponents'):
            self.log.info('No ftrackComponents present. Skipping this instance')
            return

        ftrack_data = instance.context.data('ftrackData').copy()
        task = ftrack.Task(ftrack_data['Task']['id'])

        # checking asset
        create_asset = True
        asset = None
        asset_type = ftrack_data['Task']['code']
        assets = task.getParent().getAssets(assetTypes=[asset_type])

        if instance.context.has_data('ftrackAssetName'):

            # searching for existing asset
            asset_name = instance.context.data('ftrackAssetName')
            for a in assets:
                if asset_name.lower() == a.getName().lower():
                    asset = a
                    create_asset = False

                    msg = 'Found existing asset from ftrackAssetName'
                    self.log.info(msg)
        else:
            # if only one asset exists, then we'll use that asset
            msg = "Can't compute asset. Multiple assets on shot:"
            for a in assets:
                msg += "\n\n%s" % a
            assert len(assets) == 1, msg

            for a in assets:
                asset = a
                create_asset = False

                self.log.info('Found existing asset by default.')

        # adding asset to ftrack data
        if asset:
            ftrack_data['Asset'] = {'id': asset.getId(),
                                    'name': asset.getName()}

        instance.context.set_data('ftrackAssetCreate', value=create_asset)

        # if we are creating a new asset,
        # then we don't need to validate the rest
        if create_asset:
            instance.context.set_data('ftrackData', value=ftrack_data)
            return

        # checking version
        msg = 'Missing version in context.'
        assert instance.context.has_data('version'), msg

        version_number = int(instance.context.data('version'))
        create_version = True
        version = None

        # search for existing version
        for v in asset.getVersions():
            if int(v.getVersion()) == version_number:

                msg = "AssetVersion exists but is not visible in UI."
                assert v.get('ispublished'), msg

                version = v
                ftrack_data['AssetVersion'] = {'id': v.getId(),
                                               'number': version_number}
                create_version = False

                msg = 'Found existing version number: %s' % version_number
                self.log.info(msg)

        instance.context.set_data('ftrackAssetVersionCreate',
                                  value=create_version)

        # if we are creating a new asset version,
        # then we don't need to validate the rest
        if create_version:
            instance.context.set_data('ftrackData', value=ftrack_data)
            return

        # checking components
        online_components = version.getComponents()
        ftrack_components = instance.data('ftrackComponents').copy()

        for local_c in ftrack_components:
            for online_c in online_components:
                if local_c == online_c.getName():

                    # warning about existing components
                    msg = 'Component "%s" already exists. ' % local_c
                    msg += 'To replace it delete it in the browser first.'
                    self.log.warning(msg)

                    # validating review components
                    if 'reviewable' in ftrack_components[local_c]:
                        msg = 'Reviewable component already exists in the version. To replace it' \
                              ' delete it in the webUI first'
                        assert online_c.getName() not in ('ftrackreview-mp4', 'ftrackreview-webm'), msg

        # setting ftrackData
        instance.context.set_data('ftrackData', value=ftrack_data)
