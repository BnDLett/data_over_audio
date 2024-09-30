# Data From Sound
Transfer data (such as text) over sound with Python.

# NOTES
## Readiness
It is planned to prepare this for a more production-like environment; however, until then, understand that this is
purely just a proof of concept. 

## Equipment
Depending on your equipment, you may also have transmission errors. These errors can be
accounted for via adjusting the values in `__init__.py`; however, don't expect it to remove those transmission errors
entirely.

## Data transfer rate
Currently, the lower the rate the better. A rate such as 8-16 bits per second tends to handle decently well. I have had
issues with 32 bits and 64 bits per second transfer rates. Also, the more data you use, the more error-prone the result.
There currently isn't an implementation to fix this.

## Frequency
The frequency that you use heavily depends on your environment. Just like regular radio, there are frequencies that
experience *a lot* of interference. From my personal experience, higher frequencies (> 500 hz) experienced less
interference.

There are also some frequencies that I consider to be "dead", which are just frequencies that cannot be transmitted or
received by the audio equipment that is currently in use. For example, my equipment can't handle 1500-2500 hz well.
As such, I stick to a 3000 hz base frequency and a 3400 hz max frequency.
