Netuitive StatsD Server 
=======================

[![Build Status](https://travis-ci.org/Netuitive/netuitive-statsd.svg?branch=master)](https://travis-ci.org/Netuitive/netuitive-statsd) [![Coverage Status](https://coveralls.io/repos/github/Netuitive/netuitive-statsd/badge.svg?branch=master)](https://coveralls.io/github/Netuitive/netuitive-statsd?branch=master)

>**Note:** This is already installed as part of the [Netuitive Linux Agent](https://help.netuitive.com/Content/Misc/Datasources/Netuitive/new_netuitive_datasource.htm) package and does not need to be installed separately.

The Netuitive StatsD Server interprets, aggregates, and forwards custom metrics generated from your application. Using the values instrumented from your application's key actions and data (method calls, database queries, etc.), Netuitive aggregates the values, associates them with corresponding metrics, and analyzes them in our analytics cycles.

For more information on the Netuitive StatsD Server, see our [help docs](https://help.netuitive.com/Content/Misc/Datasources/Netuitive/new_netuitive_datasource.htm#kanchor275), or contact Netuitive support at [support@netuitive.com](mailto:support@netuitive.com).


Features
--------

* Interprets, aggregates, and forwards the follow formats to [Netuitive](http://www.netuitive.com/)
    * StatsD
    * DogStatsD Metrics
    * DogStatsD Events
    * DogStatsD Service Checks


Usage
-----
See [usage doc](USAGE.md)


Requirements
------------

- Python >= 2.7 or >= 3.3
- See [requirements.txt](requirements.txt) for Python modules
- Working Netuitive Custom Datasource


History
-------


Version 0.0.3 - Mar 12 2016
---------------------------
* improve hostname detection

Version 0.0.2 - Mar 11 2016
---------------------------

* Fix memory usage in error condition

Version 0.0.1 - Feb 29 2016
---------------------------

* First release


Copyright and License
---------------------

Copyright 2016 Netuitive, Inc. under [the Apache 2.0 license](LICENSE).
