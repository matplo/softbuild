# softbuild

## general approach

- provide <package>/build_version.sh which use some environment variables
- provide a <package>/config_version.cfg which overwrites some of those env variables and defines other flags etc
-- you can also provide dependencies there (to be defined how and how these the build.sh should take into account)
- the python script will parse config and setup a build.sh and execute it - at that point the software should be intalled
- you can publish the recipes to the web

## main questions

- how to make it robust
- how to make it super easy to use
- upload recipies to a common github

## what does it look like

- well it looks like just another building from recipes system

