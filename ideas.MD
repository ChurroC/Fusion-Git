IDEAS:
Create a Tester?
Add Numpy for speed?

TODO:
Do Joints
Do Planes

Do Linked Components - TBH no clue what to do with them right now

Use adsk.core.Camera to take pictures of sketches and cv2 to show the diff by highlgihting in green or red
Do the same for extrudes but instead straight up change the color of the feature then take a picture

Also remember to add stl files at the end
Threads to fasten the build process

AHHH I ust realized I could use attributes to store info about each timeline

ISSUE:
Need to find a better way to get path to the original component creation rather than just adding it a attribute.

Also do I even need the component_timeline since I could use a component's .features and .sketch instead - but would I have proper indexing? Or I could do all items then order json by that index.


TIPS:
Import using relative pathing - https://forums.autodesk.com/t5/fusion-api-and-scripts/importing-python-modules-those-i-create-into-scripts/td-p/6061765

See text console do Option + CMD + C on Mac OS or ALT + CTRL + C on Windows OS
