==============
Administration
==============

The GraphDb plugin stores a graph model with vertices and edges.
This is ideal for representing an IT network, Power network, Gas network, etc.

Segments
--------

The peek-plugin-graphdb is populated by graph segments.
Segmenting the graph is needed to allow for incremental loads of small parts
of the graphdb (aka segments).

This is for performance reasons, it's not practical to load the entire graph
on every change.

Trace Config
------------

The trace configuration is a list of trace rules that define the behavior of
traces run on the GraphDB.

Storage
-------

This plugin stores three types of data.
#.  An "index" storing the contents of the segments
#.  An "index" that stores which vertices and edges are in which segments
#.  The TraceConfig configuration.
