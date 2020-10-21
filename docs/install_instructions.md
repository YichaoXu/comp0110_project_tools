## Installation

The terminal version of the tool is in developing, and it can only provide with the complete but untested supports for 
the repository mining. Compared with the terminal tool, to import and
to use the package in a python project are more recommended.

#### 1. Overall 
Currently, the package is based on a third-part python package, the *PyDriller*, and a terminal tool, *GumTree*. 
The following table shows the version and websites for the two tools being used during developing. 

|     Tool     | Version |                         Access                        |
|:------------:|:-------:|:-----------------------------------------------------:|
| PyDriller    | 1.15.2  | https://pydriller.readthedocs.io/en/latest/intro.html |
| GumTree Diff | v2.1.2  | https://github.com/GumTreeDiff/gumtree                | 

Besides, if you want to use the function about evaluating the precision and recall of the strategy, it is also 
essential to install the *matplotlib*, *pandas*, *numpy* and *pdfpages*.

#### 2. Install the PyDriller 

*PyDriller* is a third-party Python package, which requires the python 3.4 or newer and Git,  

A virtual environment is optional but suggested by the developers of PyDriller. 
The following instructions can initialise such an environment. 

```
$ pip install virtualenv
$ cd my_project_dir
$ virtualenv venv
$ source venv/bin/activate
``` 

The package can be installed by using the following statement. 

```
$ pip install pydriller 
```

Or you can use the requirement.txt file in the directory. 

```
$ pip install -r requirement.txt
```

The more specific instructions for installing can be found in the 
[official website of the PyDriller](https://pydriller.readthedocs.io/en/latest/intro.html).

#### 3. Install the GumTree Diff 

*GumTree* is a tool based on Java 11, so that at least this version or newer version of Java is essential.

The released version of the tool can be found in [their website](https://github.com/GumTreeDiff/gumtree/releases/).
After extract the *.zip* file, please add the executable in your environment variable $PATH. 

```
$ export PATH=path_to_gumtree_executable:$PATH
``` 

In Windows, the instruction will be: 
```
$ set PATH=path_to_gumtree_executable:$PATH
```

#### 4. (Optional) Install other python packages for the evaluation functions

In the case to use the evaluation functions, it is essential to also install other python package. 
To use the requirement file is recommended. The instruction will be like: 
 ```
$ pip install -r requirement.txt
```
