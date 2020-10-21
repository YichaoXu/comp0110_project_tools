## Architecture and Design 

There are three separate classes providing different APIs in the package, namely the **commits2sql**, **sql2link** and 
**evaluator4link**. 

The first one is used to mine the git repository, which can extract the changes from the github repository and then 
store the results into a sqlite file. The second one implement the CoEv strategy with different optimisations, which can
use the sqlite file to construct the traceability links. The final one can evaluate the precision and recall of 
different strategies for different projects.  