#
# This file can be edited manually to set the correct urls - or local paths to installation sources if available #
# Can be set to a http/ftp url or a an absolute path to a file on the computer (/home/undesa/....)
#####################################################################################################

### python_download_url is the url to python 2.5 source ###
set :python_download_url, "/home/undesa/cache/Python-2.5.4.tgz" # http://www.python.org/ftp/python/2.5.4/Python-2.5.4.tgz
set :python_imaging_download_url, "http://effbot.org/media/downloads/Imaging-1.1.7.tar.gz"

### python24_download_url is the url to python 2.4 source ###
set :python24_download_url, "/home/#{bungeni_username}/cache/Python-2.4.6.tgz" # http://www.python.org/ftp/python/2.4.6/Python-2.4.6.tgz
set :python24_imaging_download_url, "http://effbot.org/media/downloads/Imaging-1.1.7.tar.gz"


### varnish source ###
set :varnish_download_url, "/home/undesa/cache/varnish-2.0.6.tar.gz" # "http://downloads.sourceforge.net/project/varnish/varnish/2.0.6/varnish-2.0.6.tar.gz?use_mirror=garr"


