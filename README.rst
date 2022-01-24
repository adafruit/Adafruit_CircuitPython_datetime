Introduction
============

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-datetime/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/datetime/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_datetime/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_datetime/actions
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

Basic date and time types. Implements a subset of the `CPython datetime module <https://docs.python.org/3/library/datetime.html>`_.

NOTE: This library has a large memory footprint and is intended for hardware such as the SAMD51, ESP32-S2, and nRF52.

Dependencies
=============
This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://circuitpython.org/libraries>`_.

Installing from PyPI
=====================
On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-datetime/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-datetime

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-datetime

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .env
    source .env/bin/activate
    pip3 install adafruit-circuitpython-datetime

Usage Example
=============

.. code-block:: python

    # Example of working with a `datetime` object
    # from https://docs.python.org/3/library/datetime.html#examples-of-usage-datetime
    from adafruit_datetime import datetime, date, time

    # Using datetime.combine()
    d = date(2005, 7, 14)
    print(d)
    t = time(12, 30)
    print(datetime.combine(d, t))

    # Using datetime.now()
    print("Current time (GMT +1):", datetime.now())

    # Using datetime.timetuple() to get tuple of all attributes
    dt = datetime(2006, 11, 21, 16, 30)
    tt = dt.timetuple()
    for it in tt:
        print(it)

    print("Today is: ", dt.ctime())

    iso_date_string = "2020-04-05T05:04:45.752301"
    print("Creating new datetime from ISO Date:", iso_date_string)
    isodate = datetime.fromisoformat(iso_date_string)
    print("Formatted back out as ISO Date: ", isodate.isoformat())


Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/datetime/en/latest/>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_datetime/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Documentation
=============

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

License
=======
See LICENSE/ for details.

Copyright (c) 2001-2021 Python Software Foundation. All rights reserved.

Copyright (c) 2000 BeOpen.com. All rights reserved.

Copyright (c) 1995-2001 Corporation for National Research Initiatives. All rights reserved.

Copyright (c) 1991-1995 Stichting Mathematisch Centrum. All rights reserved.
