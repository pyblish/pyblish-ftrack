# pyblish-ftrack
Pyblish for FTrack

###Usage

To succesfully publish an instance to ftrack using this extension you only neew to append a few data members to the instance.

Required data:
* ftrackComponents - a list of dictionaries.
```python
ftrackComponents = [
                    componentName1: {path: 'path/to/file.%04d.exr'}
                    componentName2: {path: 'path/to/file.mp4', reviewable = True}, 
                    ]
```
