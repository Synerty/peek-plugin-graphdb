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