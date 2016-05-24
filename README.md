## GashoTorrent
BitTorrent client project for the Python 2016 course at FMI.

GashoTorrent is a simple BitTorrent client application, which can be used
for simultaneous downloading and seeding of multiple torrent files. The application
will be providing information about every torrent file - average download/upload speed, 
downloaded bytes, uploaded bytes, etc. GashoTorrent will provide a simple preferences
window where the user can modify different settings, affecting the behaviour of the 
application
<br />
<br />
  
  - For the GUI will be used PyQt5 (5.6)
  - For the torrent handling will be used [libtorrent-rasterbar](http://libtorrent.org/)
<br />
<br />

Some features, which i will try to implement:
<br />
  - Drag and drop .torrent files
  - Minimization to tray (with information about currently running torrents on hover)
