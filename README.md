# pyblish-ftrack

[![Code Health](https://landscape.io/github/pyblish/pyblish-ftrack/master/landscape.svg?style=flat)](https://landscape.io/github/pyblish/pyblish-ftrack/master)

Pyblish for FTrack

## Usage

You can choose to use the old api or the new api. There are two different workflows to suit each api.

### New API

In the new api workflow the extension collects the current task and sets up a session. It is expected that you used these to minimize the calls to the server. These can be accessed through the context:

```python
print context.data["ftrackTask"]
print context.data["ftrackSession"]
```

To publish a component you have to add some data to the data member ```ftrackComponentsList``` on an instance, and append the ```ftrack``` family. Each item of ```ftrackComponentsList``` is a dictionary where you specify the parameters of a component. As a minimum you have to specify a ```component_path```:

```python
instance = context.create_instance("A")
instance.data["families"] = ["ftrack"]
instance.data["ftrackComponentsList"] = [{"component_path": "path/to/file"}]
```

To facilitate this simple workflow, there are some assumed data for each component to achieve a successfull publish:


```python
{
  "assettype_data": {
    "short": "upload", # Default asset type is "upload".
  },
  "asset_data": {
    "name": task_name, # This is the name of the current task, collected by the extension.
    "type": assettype_entity, # The AssetType entity derived from the "assettype_data".
    "parent": task_parent, # The parent of the current task.
  },
  "assetversion_data": {
    "version": 0, # This is to ensure a version 1 gets created if non exists.
    "asset": asset_entity, # The Asset entity derived from the "asset_data".
    "task": task, # The current task.
  },
  "component_data": {
    "name": "main", # Default component name is "main".
    "version": assetversion_entity, # The AssetVersion entity derived from "assetversion_data".
  },
  "component_overwrite": False, # Overwriting will deleted existing data, if supported by the location, and component, and then create a new component.
  "component_location": session.pick_location(), # This will pick the highest prioritized location.
}
```

All of this data can be overwritten by providing it in the component data item in ```ftrackComponentsList```, and you can also provide more data. It is also worth noting that you can add any number of components to the ```ftrackComponentsList``` per instance at any point until the integrator executes, which could have completely different data so you can publish any component.
Here is an example of overriding the default, and add another component of a different type:

```python
instance.data["ftrackComponentsList"] = [
  {
    "assettype_data": {
      "short": "scene"
    },
    "assetversion_data": {
      "version": 2
    },
    "component_data": {
      "name": "mayaAscii"
    },
    "component_path": "path/to/file",
    "component_overwrite": True,
  },
  {
    "assettype_data": {
      "short": "mov"
    },
    "assetversion_data": {
      "version": 2
    },
    "component_data": {
      "name": "movie"
    },
    "component_path": "path/to/movie/file",
    "component_overwrite": True
  },
]
```

After a successfull publish of a component, the component will be added to the data:
```python
for data in instance.data["ftrackComponentsList"]:
    print data["component"]
```

### Old API

To succesfully publish an instance to ftrack using this extension you need to append a few data members to the instance you want to publish.

**Required data**

- ftrackComponents (dict) - Dictionary of dictionaries where each key is a component name. There are required and optional keys:
  - **Required keys**
    - *path* (str): Holds the path to the file being published.
  - **Optional keys**
    - *reviewable* (bool): Tells extension whether you want the component to be uploaded to ftrack servers and made available for web-review.
    - *location* (ftrack.Location): If you set this data member on a component, the component will be added to that location when creating the component. By default all components will be added to "ftrack.unmanaged" location.
    - *overwrite* (bool): You can overwrite the data and the component by adding this data member. *NOTE: THIS WILL POTENTIALLY RESULT IN DATA LOSS. USE WITH CAUTION.*

```python
location = ftrack.Location("custom_location")
ftrackComponents = {
    "sequence": {"path": "path/to/file.%04d.exr", "location"=location},
    "movie":    {"path": "path/to/file.mp4", "reviewable"=True},
}

instance.data['ftrackComponents'] = ftrackComponents
```

**Optional data:**

- ftrackAssetName - Name of ftrack asset where you want your AssetVersion to be created. (Context data)
 - If you set this data, extensionwill try to find an existing ftrack asset with given name and attach the version to it. If such asset is not found, a new one will be created.

```python
# Example code to set ftrackAssetName data
context.data["ftrackAssetName"] = "myAsset"
```

- version - Version number of the publish (Context data)
 - ftrack extension needs to know a version number the publish taking place so it can set ftrack version to the same number. If you set version yourself, it will be pick up by plugins and used. If not, extension will try to get the version number from currentFile context.

```python
# Example code to set ftrackAssetName data
context.data["version"] = 2
```

### Ftrack hook

The Ftrack hook allows you to run Pyblish directly from your browser with actions. This allows you to publish any file without opening an application.

**Dependencies**

The hook takes advantage of [pyblish-standalone](https://github.com/pyblish/pyblish-standalone), so the ```pyblish-standalone``` module needs to be available to Python.

**Setup**

In order for ```ftrack-connect``` to find the ```pyblish-ftrack``` hook, you will need to setup your environment.

- Add ```pyblish-ftrack/pyblish_ftrack``` to ```FTRACK_CONNECT_PLUGIN_PATH```

**Usage**

 Currently the Pyblish action is only available for tasks.

 After you have launched the Pyblish action, you will be presented with a file browser where you browse to a specific folder to publish from. The selected folder will be available in Pyblish via the context;
 ```python
 print context.data["currentFile"]
 ```
If you want to specify the folder th browser begins on, you can add the directory in the same way that other Ftrack actions handle this; http://ftrack-connect.rtd.ftrack.com/en/0.1.21/developing/hooks/application_launch.html#ftrack-connect-application-launch

### Debug Messages

By default Ftrack outputs a lot of debug messages. Still can be disabled with:

```python
import logging
logging.getLogger("ftrack_api").setLevel(logging.INFO)
```
