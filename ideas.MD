IDEAS:
Create a Tester?
Add Numpy for speed?

One thing I could do is instead of using a reference file I could use a symlink but it doesn't hold info specific to a compoennt liek if it's activated hidden or something.

Still need to get recursively reading diles working for linked components


In options menu show all the linekd assemblies and choose which data you which to keep and which you want to keep as a export stl file or somthing


Maybe use git attributes to make a custom diff tool
I coudl create a tool to read a step file and turn it into something readable
So It wouldn't be connected to fusion and work on anythign

Also no need to compress json file if I just set it up to not diff in git attribute and just commit


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
