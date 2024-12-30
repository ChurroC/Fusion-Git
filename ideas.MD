
mayeb isntead of adsk::fusion::ExtrudeFeature we have ExtrudeFeature

as I make every feature modular into each fodle rhave every test have the fusion tester file
later on I can make a custom tester

Maybe use numpy for object: https://forums.autodesk.com/t5/fusion-api-and-scripts/how-to-use-modules-like-numpy-scipy-etc-by-conda-in-fusion-360/td-p/9355499


Visual representation that git doesnt track. Have a folder for each one and have the sketch image there.
Then in the tracked change though the image changes it shouldn't matter because it should be a vsiual represntation.
Since there should be a image of the sketch then red highlight of the change. Then they knoew the diff even
if the image diff don't matter. Then they can check the json diff to see if the sketch is different
then. Take a screenshot of the removals then cv2 to color red. Sketch of the new then color green.
Then sketch eveyrhting else next. THen combine the screenshots. 

Adding onto the idea above I coudl also add stl files since they can be rendered by github

I like the way it currently
data/
├── metadata.json
├── timeline.json           # Main timeline (currently component_timeline.json)
├── components/
    ├── component4.json    # Flattened, no subdirectories
    ├── cube.json
    ├── cylinder.json
└── linked/
    └── component_test_v1.json

But one thing to think about is when I am rebuidlign the timeline how would I recreate the components.
Since if I have to recreate the internal compoentn once then refer back to it. I should do the same when creating these components
by going through each timeline and if it is the first creation I create a new folder for it and such. Like my intial idea. Then refer
to it again and again.
data/
├── metadata.json
├── timeline.json           # Main timeline (currently component_timeline.json)
├── component1/
    ├── timeline.json
    ├── Cube/
        ├── timeline.json
├── Cylinder/
        timeline.json
go back to the og
output_directory/
    Root_Component/
        component.json
        Internal_Child_1/
            component.json
    _linked_components/
        Linked_Component_1/
            component.json
        Linked_Component_2/
            component.json


Maybe have a deteremistic hash for every component referenced. So that when you change one linked component or just a component in general the has changes reflecting the changes everywhere
But also this doesn't reflect how a function works in git cause the function woudl change but the references calling it wouldn't change

have a link for component files to their references in git so like what they have git

data1 - flat config
data2 - folder config
data3 - copies fusion folder path
data4 - uses markdown to show links to the intial reference of a component

Just reallized idot me I just redid yaml
soooo should I change to yaml or just shoudl I keep it.
Since the original json file would have more info so there is no point in having a yaml resprestation if it doesn't have all the data
But if I do give it the data it kinda ruins the super readability portion.

TODO:
Fix up units cause it's a string right now "in" instead of the number
Do Joints
Do Linked Components
Add json hashes - DONEish need to do importing of this
Why have the features be called component_feature_type and not component_type
Stop the annoyting type.type and just turn it into type
Use adsk.core.Camera to take pictures of sketches and cv2 to show the diff by highlgihting in green or red
Do the same for extrudes but instead straight up change the color of the feature then take a picture
Also remember to add stl files at the end
Check out attributes - seems promisisng - https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-BAF017FE-10B8-4612-BDE2-0EF5D4C6F800



RIGHT NOW THE 2 IDEAS TO TRAVERSE:
One is to keep the same idea and just add some code to recursivbely travel through each object and in my custom timline json I can add the path in at the end
Or second idea is take the recursion and screw the rest of the ideas and just recursively go through the entire structure. - I could use component.feature and componen.sketches. 


TIPS:
Import using relative pathing - https://forums.autodesk.com/t5/fusion-api-and-scripts/importing-python-modules-those-i-create-into-scripts/td-p/6061765

See text console do Option + CMD + C on Mac OS or ALT + CTRL + C on Windows OS
