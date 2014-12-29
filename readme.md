
# "betabrite" - displays Twitter feed and other info on an LED sign.

Way back in 1999 or so, I bought a *Beta-Brite* LED from Sam's Club.
One of the selling points, for me at least, was the serial port.
I thought it would be cool to send messages to it from my computer.
After I got home and opened the box, I realized that the company,
Adaptive Micro Systems, had built it with a proprietary and
undocumented serial port and protocol.  Foo on them!  So the LED
sign sat unused for 15 years.

Then, through the wonder of the Internet, I discovered that the pinouts
and protocol for these signs was documented (I am not sure if AMS opened
their documentation, or if it was just reverse-engineered).

So I spent a weekend hacking together a Python script that would grab
my Twitter feed and send it to the sign.  Over time, I added a few other
small messages:

* the status of my [garage door](https://github.com/sudoer/doorman/)
* the status of my [backups](https://github.com/sudoer/flashback/)

I have also added external cron scripts that turn the display off at
11pm and on again at 6am.

It's pretty cool to have the sign always scrolling some current bits
of Internet info.

Things I would like to improve:

* Currently, the sign shows each Twitter message for a specific
(configurable) amount of time.  Short tweets will scroll across
twice, longer ones might not completely scroll across once.  I
someone who knew more about the Beta-Brite protocol could queue
up the messages in the various buffers so they would scroll
across seamlessly.

Alan Porter
(alan@alanporter.com)

