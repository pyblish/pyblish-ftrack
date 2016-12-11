import pyblish.api


class PyblishFtrackIntegrateFtrackApi(pyblish.api.InstancePlugin):
    """ Commit components to server. """

    order = pyblish.api.IntegratorOrder
    label = "Ftrack"
    families = ["ftrack"]

    def query(self, entitytype, data):
        """ Generate a query expression from data supplied.

        If a value is not a string, we'll add the id of the entity to the
        query.

        Args:
            entitytype (str): The type of entity to query.
            data (dict): The data to identify the entity.
            exclusions (list): All keys to exclude from the query.

        Returns:
            str: String query to use with "session.query"
        """
        queries = []
        for key, value in data.iteritems():
            if not isinstance(value, (basestring, int)):
                if "id" in value.keys():
                    queries.append(
                        "{0}.id is \"{1}\"".format(key, value["id"])
                    )
            else:
                queries.append("{0} is \"{1}\"".format(key, value))

        query = (
            "select id from " + entitytype + " where " + " and ".join(queries)
        )
        self.log.debug(query)
        return query

    def process(self, instance):

        session = instance.context.data["ftrackSession"]
        task = instance.context.data["ftrackTask"]

        # Iterate over components and publish
        for data in instance.data["ftrackComponentsList"]:

            # AssetType
            # Get existing entity.
            assettype_data = {"short": "upload"}
            assettype_data.update(data.get("assettype_data", {}))

            assettype_entity = session.query(
                self.query("AssetType", assettype_data)
            ).first()

            # Create a new entity if none exits.
            if not assettype_entity:
                assettype_entity = session.create("AssetType", assettype_data)
                self.log.info(
                    "Created new AssetType with data: ".format(assettype_data)
                )

            # Asset
            # Get existing entity.
            asset_data = {
                "name": task["name"],
                "type": assettype_entity,
                "parent": task["parent"],
            }
            asset_data.update(data.get("asset_data", {}))

            asset_entity = session.query(
                self.query("Asset", asset_data)
            ).first()

            # Create a new entity if none exits.
            if not asset_entity:
                asset_entity = session.create("Asset", asset_data)
                self.log.info(
                    "Created new Asset with data: {0}".format(asset_data)
                )

            # AssetVersion
            # Get existing entity.
            assetversion_data = {
                "version": 0,
                "asset": asset_entity,
                "task": task
            }
            assetversion_data.update(data.get("assetversion_data", {}))

            assetversion_entity = session.query(
                self.query("AssetVersion", assetversion_data)
            ).first()

            # Create a new entity if none exits.
            if not assetversion_entity:
                assetversion_entity = session.create(
                    "AssetVersion", assetversion_data
                )
                self.log.info(
                    "Created new AssetVersion with data: {0}".format(
                        assetversion_data
                    )
                )

            # Have to commit the version and asset, because location can't
            # determine the final location without.
            session.commit()

            # Component
            # Get existing entity.
            component_data = {
                "name": "main",
                "version": assetversion_entity
            }
            component_data.update(data.get("component_data", {}))

            component_entity = session.query(
                self.query("Component", component_data)
            ).first()

            component_overwrite = data.get("component_overwrite", False)
            location = data.get("component_location", session.pick_location())

            # Delete existing component if requested.
            if component_entity and component_overwrite:
                location.remove_component(component_entity)
                session.delete(component_entity)
                self.log.info("Deleted existing component.")
                component_entity = None

            # Create new component if none exists.
            if not component_entity:
                assetversion_entity.create_component(
                    data["component_path"],
                    data=component_data,
                    location=location
                )
                msg = "Created new Component with path: {0}, data: {1}, "
                msg += "location: {2}"
                self.log.info(
                    msg.format(
                        data["component_path"],
                        component_data,
                        location
                    )
                )

            # Inform user about no changes to the database.
            if component_entity and not component_overwrite:
                self.log.info(
                    "Found existing component, and no request to overwrite. "
                    "Nothing has been changed."
                )
            else:
                # Commit changes.
                session.commit()
