IDEAS:
Create a Tester?
Add Numpy for speed?

For idea 2 check which io function is faster


1: - Just reallized this might be better if I could use threads
This is the way I'm doing it currently
I have one intial iteration over the entire timeline
Then I add attributes to find the source component
Then I recursively read through each occurence
For each once I create a timeline file
2:
This other idea is to hold all the data in one huge object
I have one intial iteration over the entire timeline
Then I add attributes to find the source component
But as I do this for each feature I find I add them directly to the object
Then I iterate through the object to save to file system
3:
This idea still has an error
I start out with recursively reading through each occurence
The problem however is that there is a chance I find the reference or copy
Before I find the intial creation component
Which means I won't be able to have the path to the intial component
I read through the feature and sketch properties of the component
Then just write to file

Still need to get recursively reading diles working for linked components


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
