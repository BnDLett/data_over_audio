# Data Over Audio
Transfer data (such as text) over audible frequency modulation.

## Readiness of this Library
I wouldn't recommend using this library in an actual production environment. However, if you wish to do so, then all
power to you. Just be sure that your equipment is capable of accurately receiving and transmitting data. Be sure that
you incorporate a standard too. This doesn't (yet) automatically adjust based on the frequencies already in the
environment.

## Equipment
Whenever it comes to equipment, you're going to want something that is frequency accurate and (depending on your
situation) loud. This is quite necessary if you're expecting fault-free communications.

## Data transfer rate
Currently, the lower the rate the better. A rate such as 8-16 bits per second tends to handle decently well. I have had
issues with 32 bits and 64 bits per second transfer rates. Furthermore, the more data you use, the more error-prone the 
result. There currently isn't an implementation to fix this.

## Frequency
The frequency that you use heavily depends on your environment. Just like regular radio, there are frequencies that
experience *a lot* of interference. From my personal experience, higher frequencies (> 500 hz) experienced less
interference.

There are also some frequencies that I consider to be "dead", which are just frequencies that cannot be transmitted or
received by the audio equipment that is currently in use. For example, my equipment can't handle 1500-2500 hz well.
As such, I stick to a 3000 hz base frequency and a 3400 hz max frequency.
