# Quandelabra

<img src="quandelabra.svg" width="130" height="140" align="left" />

A tiny tool for quickly downloading large (and free) datasets from Quandl.

Since Quandl limits the ability to download an entire dataset at once to premium offerings, this tool was made to instead download the entire thing in multiple pieces at the same time.  
"*But wait!*" you say, "*Doesn't the Quandl Python API allow you to do that already?*".  
Well, yes, it does.  
However, it is painfully slow while doing it and it is not multithreaded by default. Adding threading or even multiprocessing afterwads is tedious and still suffers from the massive overhead the Quandl Python package has with every request.

Quandelabra solves this problem by <strike>not giving a shit about official packages</strike> requesting data directly via the REST API, circumventing the CPU-monster that is the Quandl-provided API wrapper. Additionally, it makes use of `asyncio` and `aiohttp` to deliver buzzword-worthy, *blazing-fast* speeds due to being able to issue dozens of requests simultaneously. And this without eating any of your RAM or CPU for breakfast! Everything stays nice, cool and under control, as long as your network can sustain the load, that is.

## Disclaimer
As with most everything that I put out, these are personal projects and there's no guarantee that they will either:

* Always work
* Be maintained forever
* Do what you want

If this works for you, great!  
If you got improvements, even better, send me a pull request!  
If it doesn't work, let me know and I'l try my best to ignore it. *Just kidding, I gotta keep my GitHub cred high.*

## Installation
Quandelabra is a simple Python script, so the installation procedure is a very complex and error-prone process which works as follows:

1. Download `git clone git@github.com:timwedde/quandelabra.git`
2. Execute `cd quandelabra/ && python3 quandelabra.py`
3. ??? `python3 quandelabra.py -h`
4. Profit!

## Usage
```
usage: quandelabra.py [-h] -d quandl_code -a key -o dir [-t N]

A tiny tool for quickly downloading large (and free) datasets from Quandl.

optional arguments:
  -h, --help            show this help message and exit
  -d quandl_code, --dataset quandl_code
                        (required) The Quandl Code for the dataset to download
  -a key, --api_key key
                        (required) Your Quandl API key
  -o dir, --output dir  (required) The directory to output data to
  -t N, --tasks N       The amount of tasks to spawn (default: 75)
```

## Credits
* Quandl, for providing amazing datasets for free and even more amazing datasets for little money.
* <div>Candalebra icon made by <a href="https://www.freepik.com/" title="Freepik">Freepik</a> and procured from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a>, licensed under <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>
