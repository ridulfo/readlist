# ReadList
A minimal self-hosted reading list. 

*I got tired of unpredictable synchronization of safari's reading-lists, so I made my own.*

**Problems tried to be solved:**
- owning my data
- predictable synchronization

My browser of choice has been safari. Mostly due to [its performance](https://miro.medium.com/v2/resize:fit:1400/format:webp/1*Wypare7p0SZ19mMutFaB_A.png) on Apple devices. Consequently, I've always used Safari's builtin reading list. However, when jumping between Apple devices I've noticed that some links that I have saved from one device aren't there on another and some old links that I've removed are still there.

## How I run it
I'm running this service on my Nixos homelab server on my local network. The service is declared in my Nixos configuration and the service management is handled by systemd. To access this service from outside of my home network, I use my gateway's builtin VPN-server.

To allow me to easily add a link to the reading list I have created a Apple Shortcut that I've added as a sharing option. So if I long-press a link or press the share button in safari I get the option to "Save URL". This simply sends a request to the "/add-link" endpoint with the link as a payload.


<img src="/assets/save-url-shortcut.jpg" width="500" alt="Apple Shortcut">
