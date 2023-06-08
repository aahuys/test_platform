## Test platform
### How to run it
Create a new app on [Heroku](https://dashboard.heroku.com/)

In terminal:

```console
$ heroku login
```

```console
$ cd test_platform/
$ git init
$ heroku git:remote -a appname
```
```console
$ git add .
$ git commit -am "make it better"
$ git push heroku master
```

You can also run it locally by running the app.py file in your compiler.

### Contents
This repository contains all the files concerning the online evaluation platform.

app.py contains the main code of the platform

DecisionTrees.py contains the code surrounding the decision tree class. All tree manipulation functions are in this class

Covers.py contains a function to extract the cover of a certain movie by using the title.

InitData.py contains the functions to load in the datafiles.

templates contains all the html templates used.

dataset25M contains the MovieLens25M dataset, more precise the links and movies datafiles.

binary_tree.pkl is a file with the pickled tree that will be used in the active learning.

emails.csv contains all the emails and ratings of the users that perform the online evaluation on the platform. 

requirements.txt contains all the pyton libraries needed and their versions.

runtime.txt contains the python version

procfile is a basic procfile for heroku
