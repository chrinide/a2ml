**************
Philosophy
**************

A2ML is an source project to Automate Automated Machine Learning.  It was started
by the team of Auger.AI.  But it is not an attempt to make Auger.AI's own API a standard.
In general we have erred towards using the option names from other AutoML providers. 
In particular we found Microsoft Azure AutoML's vocabulary to be reasonable and descriptive.
So we adopted much of their vocabulary in A2ML. 

Why Are We Doing This
=====================
The team behind Auger.AI has a history of building free useful services and figuring 
out how to monetize them later. We felt that the AutoML industry desperately needed 
a common API.  The dominant players in AutoML have particularly poor performance in 
finding optimal algorithms and hyperparameters, due to their unsophisticated grid search 
approach.  AutoML needs innovation and disruption.  An open, common API makes this much
easier to happen.

We are also offering a paid hosted service that manages the connections to AutoML services
from various vendors.   Just like you pay for hosted instances of other technologies 
(Spark from DataBricks, Docker, Redis) we offer a hosted A2ML service that manages
your connections and instances of AutoML providers from various vendors.  

Review and Monitoring
---------------------
A2ML also introduces the concept of a Review phase to help users monitor that their models
remain accurate.   Auger.AI includes charts and diagnostics of a model's ongoing 
accuracy.  While the Auger Review service is paid, the base code for aggregating 
accuracy (comparing predictions and actual results and several measures of ongoing
data values) is in fact free as part of A2ML.  This should allow accuracy to be provided
for AutoML services which don't provide this capability (today that is most other
other AutoML providers).   We believe this will result in more accurate AutoML models in 
general over the lifetime of their usage. 