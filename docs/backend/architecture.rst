.. _backend-architecture:

====================
Backend Architecture
====================

The COPS backend is built using FastAPI which is a web framework built in Python.

The  `FastAPI documentation <https://fastapi.tiangolo.com/>`_ is fantastic
and should be looked over before doing development. It's thorough and provides
lots of good information about the technology used to build the backend.

This architecture documentation will take a more cursory view of the backend and
the patterns that are specific to doing development on the backend. The `FastAPI
tutorial <https://fastapi.tiangolo.com/tutorial/intro/>`_ serves as an excellent
reference for more specifics of the framework.


Data models, Schema models, and the Service layer
=================================================

The backend
