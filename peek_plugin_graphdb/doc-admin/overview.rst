Overview
--------

The following sections describe the parts of the GraphDB plugin.

Importers
`````````

TODO

Client Cache
````````````

TODO

Segment Index
`````````````

The peek`plugin`graphdb is populated by graph segments.
Segmenting the graph is needed to allow for incremental loads of small parts
of the graphdb (aka segments).

This is for performance reasons, it's not practical to load the entire graph
on every change.


Key Index
`````````

TODO

Trace Config
````````````

The trace configuration is a list of trace rules that define the behavior of
traces run on the GraphDB.



