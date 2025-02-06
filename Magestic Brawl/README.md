# MagesticBrawl

# Main Pygame Project
My main pygame project that I am working on is Magestic Brawl. It is a knockoff version of Streetfighter. 

# Install Requirements and Instructions

Before installing pygame, you must check that Python is installed
on your machine. To find out, open a command prompt (if you have
Windows) or a terminal (if you have MacOS or Linux) and type this:
::

   python --version


If a message such as "Python 3.8.10" appears, it means that Python
is correctly installed. If an error message appears, it means that
it is not installed yet. You must then go to the `official website
<https://www.python.org/downloads/>`_ to download it.

Once Python is installed, you have to perform a final check: you have
to see if pip is installed. Generally, pip is pre-installed with
Python but we are never sure. Same as for Python, type the following
command:
::

   pip --version


If a message such as "pip 20.0.2 from /usr/lib/python3/dist-packages/pip
(python 3.8)" appears, you are ready to install pygame! To install
it, enter this command:
::

   pip install pygame

Once pygame is installed, quickly test your library by entering the following
command, which opens one of the many example games that comes pre-installed: 
::

	python3 -m pygame.examples.aliens


If this doesn’t work, the `Getting Started 
<https://www.pygame.org/wiki/GettingStarted/>`_ section of the official 
website has more information for platform specific issues, such as adding
python to your machine’s PATH settings
