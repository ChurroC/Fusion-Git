Either recreate timeline
- Basically convert timeline into readable text
- Then convert the text back into the extrudes and the proper files

Other idea is for every extrude or feature I find everythign associated kindaaaa

just like how git uses git to add to their repo we could do the same for the fusion files.

Need to type up a dictinary for the output data - in data_types.py.

later seperate everything like profiles in one file or extrudes in another but the annoying thing currently is how do I support global vars over files.
We could move all globals to file like shown here https://stackoverflow.com/questions/13034496/using-global-variables-between-files

mayeb isntead of adsk::fusion::ExtrudeFeature we have ExtrudeFeature

as I make every feature modular into each fodle rhave every test have the fusion tester file
later on I can make a custom tester


Maybe use numpy for object: https://forums.autodesk.com/t5/fusion-api-and-scripts/how-to-use-modules-like-numpy-scipy-etc-by-conda-in-fusion-360/td-p/9355499


In general got to import realtive cause https://forums.autodesk.com/t5/fusion-api-and-scripts/importing-python-modules-those-i-create-into-scripts/td-p/6061765
And due to this I either got to have seperate import files or I'm gonna just symlink it trust - https://stackoverflow.com/questions/5917249/git-symbolic-links-in-windows/59761201#59761201

you can use console - https://forums.autodesk.com/t5/fusion-api-and-scripts/is-it-possible-to-run-and-debug-fusion-360-api-scripts-and-add/td-p/11467726 - Just usual python info - https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-743C88FB-CA3F-44B0-B0B9-FCC378D0D782



Maybe use symlinks to mvoe global files into the same export and improt file.

Visual representation that git doesnt track. Have a folder for each one and have the sketch image there.
Then in the tracked change though the image changes it shouldn't matter because it should be a vsiual represntation.
Since there should be a image of the sketch then red highlight of the change. Then they knoew the diff even
if the image diff don't matter. Then they can check the json diff to see if the sketch is different
then. Take a screenshot of the removals then cv2 to color red. Sketch of the new then color green.
Then sketch eveyrhting else next. THen combine the screenshots. 


Check for first time import and init - https://stackoverflow.com/questions/30483246/how-can-i-check-if-a-module-has-been-imported


also to get to text command do Option + CMD + C on Mac OS or ALT + CTRL + C on Windows OS



        # --check-untyped-defs
        # --ignore-missing-imports
        # --explicit-package-bases












Currenty idea intially was gonna be:
output_directory/
    Test API v17/
        component.json
        Child_Component_1/
            component.json
        Child_Component_2/
            component.json

But linked component are annoying. Since like the nutstrips that Patrick uses.
They are made once as a component that are linked into other componets by linking
Idea currently is:
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
This would help make sure I know which one is the root_component and understand 

Better idea is too have
output_directory/
├── component.json           # Root component features
├── 000_SubComponent1/     # Timeline ordered components
│   └── component.json
├── 001_SubComponent2/
│   └── component.json
├── _linked/               # Linked components
│   ├── LinkedPart1/
│   │   └── component.json
│   └── LinkedPart2/
│       └── component.json

Like so:
// MainAssembly/features.json
{
  "document_name": "MainAssembly",
  "units": 3,
  "features": [
    {
      "name": "Sketch1",
      "type": "adsk::fusion::Sketch",
      "index": 0,
      "details": {
        "curves": [...],
        "plane": {...}
      }
    },
    {
      "name": "SubComponent1",
      "type": "adsk::fusion::Component",
      "index": 1,
      "details": {
        "is_linked": false,
        // Reference to the component's full data in its own directory
        "document_name": "SubComponent1"
      }
    },
    {
      "name": "CircularPattern1",
      "type": "adsk::fusion::CircularPatternFeature",
      "index": 2,
      "details": {...}
    }
  ]
}

// MainAssembly/001_SubComponent1/features.json
{
  "document_name": "SubComponent1",
  "units": 3,
  "features": [
    {
      "name": "BaseSketch",
      "type": "adsk::fusion::Sketch",
      "index": 0,
      "details": {
        "curves": [...],
        "plane": {...}
      }
    },
    {
      "name": "BaseExtrude",
      "type": "adsk::fusion::ExtrudeFeature",
      "index": 1,
      "details": {...}
    }
  ]
}


Can't figure out what type of entitiy a circular pattern of a component is



Also final idea for the strucutre
Basically I go through the timeline but every time I hit a component
I do a recursion basiocally and run the code again but with a different path save
then once the timeline inside the inner component is read it will create a json file
and add it directly to the file system. So the nice part is I don't got to track all the children since they're
just saved to the file system
got to find a way to check for 


At the end try to spawn threads every recursion