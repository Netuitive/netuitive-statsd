History
-------
Version NEXT
---------------------------
* Support v StatsD tag for tagging app.version on elements

Version 0.3.5 - Apr 25 2018
---------------------------
* Fix poster to add a prefix only when the value is a non-empty string

Version 0.3.4 - Feb 16 2018
---------------------------
* Pull the latest Netuitive python client that contains a bug fix and improvement for handling element metrics lookup during adding a sample

Version 0.3.3 - Jan 17 2018
---------------------------
* Fix forever cached elements in poster

Version 0.3.2 - Sep 06 2017
---------------------------
* Fix the default behavior if given no hostname

Version 0.3.1 - Aug 28 2017
---------------------------
* Fix customizable hostname support constructor bug

Version 0.3.0 - Aug 28 2017
---------------------------
* Add a deploy step to the Travis CI build
* Add customizable hostname support

Version 0.2.3 - Nov 09 2016
---------------------------
* fix "list index out of range" issue

Version 0.2.2 - Sep 30 2016
---------------------------
* update netuitive-python-client

Version 0.2.1 - Jul 26 2016
---------------------------
* fix option to disable internal metrics

Version 0.2.0 - Jul 25 2016
---------------------------
* improve test performance
* add option to disable internal metrics
* update netuitive-python-client

Version 0.1.1 - Jul 07 2016
---------------------------
* fix tag processing bug

Version 0.1.0 - Jun 17 2016
---------------------------
* Change the way SUM is calculated for counter types. SUM will now be calculated as sum the input values instead of the sum of incremental updated counter value for each time period.

Version 0.0.8 - Jun 08 2016
---------------------------
* protect against memory starvation
* improve tests

Version 0.0.7 - Jun 07 2016
---------------------------
* fix samples not being cleared properly

Version 0.0.6 - May 11 2016
---------------------------
* fix element type
* improve logging

Version 0.0.5 - May 10 2016
---------------------------
* fix element type configuration
* add 'ty' reserved tag

Version 0.0.4 - Apr 12 2016
---------------------------
* improve agent string
* improve test coverage

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
