---
title: Building Your Environment
category: Setup
---

Currently, Decision Descent doesn't feature an installer,
but everything you'll need to build it was included in
the download.  It's as simple as running a simple batch
file! Naturally, people don't trust suspicious DLLs and
executables included in downloads, so the following
paragraphs are here to walk you through rebuilding what
you downloaded.

Firstly, you need a Python installation.  This project was
built with [Python v3.6.4](https://www.python.org/downloads/release/python-364/).
_Versions older or newer than 3.6.4 may not work._

Secondly, you should ensure your installation includes PIP.
If it doesn't, you should reinstall Python and check the
"Ensure Pip" option.

Next, you'll need to install the project's requirements.
The project's requirements are, funnily enough, listed in
`requirements.txt`.  You can install them individually, or
you can insert the `-r` parameter in the `pip install` command.
*If you don't know how to install Python packages, you can
just run* `python -m pip install -r requirements.txt` *in the
project directory.*