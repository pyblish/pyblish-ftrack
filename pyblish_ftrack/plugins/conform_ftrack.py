import pyblish.api

import ftrack


@pyblish.api.log
class ConformFtrack(pyblish.api.Conformer):
    """ Creating Componenets in Ftrack.
    """

    order = pyblish.api.Conformer.order + 0.11
    label = 'Ftrack'

    def process(self, instance):

        # skipping instance if ftrackData isn't present
        if not instance.context.has_data('ftrackData'):
            self.log.info('No ftrackData present. Skipping this instance')
            return

        # skipping instance if ftrackComponents isn't present
        if not instance.has_data('ftrackComponents'):
            self.log.info('No ftrackComponents present.\
                           Skipping this instance')
            return

        ftrack_data = instance.context.data('ftrackData')

        # creating components
        version = ftrack.AssetVersion(ftrack_data['AssetVersion']['id'])
        components = instance.data('ftrackComponents')
        for component_name in instance.data('ftrackComponents'):

            # creating component
            try:
                path = components[component_name]['path']
            except:
                return

            try:
                version.createComponent(name=component_name, path=path)
                self.log.info('Creating "%s" component.' % component_name)
            except:
                pass

            # make reviewable
            if 'reviewable' in components[component_name]:
                upload = True
                for component in version.getComponents():
                    if component_name in ('ftrackreview-mp4',
                                          'ftrackreview-webm'):
                        upload = False
                        break
                if upload:
                    ftrack.Review.makeReviewable(version, path)
