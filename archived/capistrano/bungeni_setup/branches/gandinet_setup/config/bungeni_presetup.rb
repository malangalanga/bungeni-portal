################################################################
#### Namespace to setup the runtime environment for bungeni ####
####  - Does an apt-get to install all the OS libraries
####  - Downloads and installs a user python 
####  - Installs all the required python libraries 
####  	- Python Imaging
####	- Python ssl
#### 	- Python svn bindings
#####	Tested on Ubuntu 8.04 
#####   To setup all the pre-requisites simply run :
#####   cap bungeni_presetup:build_all
##################################################################


### Defines a sequence of tasks for installing bungeni from scratch ###

#### General Build Parameter #####

### only the following 2 parameters need to be set by the user to customize
### this installation script for different computersi
#set :use_sudo, false
#set :system_build_root, "/home/undesa/disk1/bungeni"
set :user_build_root, "#{system_build_root}/cap_builds"
set :user_install_root, "#{system_build_root}/cap_installs"

#### download URLs for components #####
### can be set to a http / ftp url or an absolute path to the file on the computer
set :python_download_url, "http://www.python.org/ftp/python/2.5.4/Python-2.5.4.tgz"
set :python_imaging_download_url, "http://effbot.org/media/downloads/Imaging-1.1.7.tar.gz"
set :svn_download_url,  "http://subversion.tigris.org/downloads/subversion-1.5.4.tar.gz"
set :varnish_download_url, "http://sourceforge.net/projects/varnish/files/varnish/2.0.6/varnish-2.0.6.tar.gz/download"

##### Component Specific Parameters ##### 

#### Python build parameters #####

set :user_python_build_path, "#{user_build_root}/python"
set :user_python25_runtime, "#{user_install_root}/python25"
set :python_download_file, File.basename(python_download_url)
set :python_src_dir, File.basename(python_download_file, ".tgz")
set :python_download_command, get_download_command(python_download_url)

#### Python imaging parameters ####

set :python_imaging_build_path, "#{user_build_root}/imaging"
set :python_imaging_download_command, get_download_command(python_imaging_download_url)
set :python_imaging_download_file, File.basename(python_imaging_download_url)
set :python_imaging_src_dir, File.basename(python_imaging_download_file, ".tar.gz")


#### libneon parameters ####
set :neon_build_path, "#{user_build_root}/neon"
set :neon_src_dir, "#{neon_build_path}/src"
set :neon_runtime, "#{user_install_root}/neon"
set :neon_svn_source, "http://svn.webdav.org/repos/projects/neon/tags/0.28.3"

#### svn build parameters ####
set :svn_build_path, "#{user_build_root}/svn"
set :svn_runtime, "#{user_install_root}/svn"
set :svn_download_command, get_download_command(svn_download_url)
set :svn_download_file, File.basename(svn_download_url)
set :svn_src_dir, File.basename(svn_download_file, ".tar.gz")
set :svn_neon_config, "#{neon_runtime}/bin/neon-config"




namespace :bungeni_presetup do
	
    desc "Installs the OS prequisites for Bungeni"
    task :essentials, :roles=> [:app] do
	required_libs = [
			"wget",
			"build-essential", # for building from source
			#"linux-headers-generic", # for building from source
			"libjpeg62-dev", # for python
			"libfreetype6-dev", # for python
			"libbz2-dev", # for python bz2 processing
			"libxslt1-dev", # for python lxml
			"libxml2-dev", # for python lxml
			"libpng12-dev", # for python
			"openssl", # for python
			"libssl-dev", # for python
			"bison",  # for postgresql
			"flex" , # for postgresql
			"libreadline5-dev" , # for postgresql
			"zlib1g-dev" , # for postgresql
			"libtool" , # for svn
			"automake" ,  # for svn
			"autoconf" , # for svn
			"libaprutil1-dev", # for svn
			"swig", # for svn
			"xmlto" # for libneon 
			]
	install_cmd = "apt-get install " + required_libs * " " 	+ " -y"
	sudo install_cmd
    end

    task :build_python, :roles=> [:app] do
	[
	"mkdir -p #{user_python_build_path}",
	"rm -rf #{user_python_build_path}/*.*",
	"mkdir -p #{user_python25_runtime}",
	"cd #{user_python_build_path} && #{python_download_command}",
 	"cd #{user_python_build_path} && tar xvzf #{python_download_file}",
	"cd #{user_python_build_path}/#{python_src_dir} && CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl ./configure --prefix=#{user_python25_runtime}",
	"cd #{user_python_build_path}/#{python_src_dir} && CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl make",
	"cd #{user_python_build_path}/#{python_src_dir} && make install"
	].each {|cmd| run cmd}
    end

    task :build_imaging, :roles=> [:app] do
	[
	"mkdir -p #{python_imaging_build_path}",
	"cd #{python_imaging_build_path} && rm -rf #{python_imaging_download_file}",
	"cd #{python_imaging_build_path} && wget #{python_imaging_download_url}",
	"rm -rf #{python_imaging_build_path}/#{python_imaging_src_dir}",
 	"cd #{python_imaging_build_path} && tar xvzf #{python_imaging_download_file}",
	"cd #{python_imaging_build_path}/#{python_imaging_src_dir} && #{user_python25_runtime}/bin/python setup.py build_ext -i",
	"cd #{python_imaging_build_path}/#{python_imaging_src_dir} && #{user_python25_runtime}/bin/python setup.py install"
	].each {|cmd| run cmd}
    end

    task :build_libneon, :roles=> [:app] do 
	[
	"mkdir -p #{neon_build_path}",
	"mkdir -p #{neon_src_dir}",
	"mkdir -p #{neon_runtime}",
	"svn export #{neon_svn_source} #{neon_src_dir} --force",
	"cd #{neon_src_dir} && ./autogen.sh",
	"cd #{neon_src_dir} && ./configure --prefix=#{neon_runtime} --with-ssl=openssl", 
	"cd #{neon_src_dir} && make ",
	### the output exit 0 in the below line is required to prevent a 
	### man installation error in neon which causes the capistrano task 
	### to wrongly fail
	"cd #{neon_src_dir} && make install ; exit 0"
	].each {|cmd| run cmd}
    end

    task :build_svn, :roles=> [:app] do 
	[
	"mkdir -p #{svn_build_path}",
	"rm -rf #{svn_build_path}/*.*",
	"mkdir -p #{svn_runtime}",
	"cd #{svn_build_path} && #{svn_download_command}",
 	"cd #{svn_build_path} && tar xvzf #{svn_download_file}",
	"cd #{svn_build_path}/#{svn_src_dir} && neon_config=#{svn_neon_config} ./configure --prefix=#{svn_runtime} PYTHON=#{user_python25_runtime}/bin/python",
	"cd #{svn_build_path}/#{svn_src_dir} && make && make install",
	"cd #{svn_build_path}/#{svn_src_dir} && make swig-py && make check-swig-py && make install-swig-py",
	"echo #{svn_runtime}/lib/svn-python > #{user_python25_runtime}/lib/python2.5/site-packages/subversion.pth"
	].each {|cmd| run cmd}
    end





    desc "the build_all task sets up all the prerequisites for a bungeni buildout"
    task :build_all, :roles=> [:app] do
	run "echo 'Installing all bungeni prerequisites'"
    end 
	
	
    after "bungeni_presetup:build_all", "bungeni_presetup:essentials", "bungeni_presetup:build_python", "bungeni_presetup:build_imaging", "bungeni_presetup:build_libneon", "bungeni_presetup:build_svn" ###, "varnish_presetup:build_varnish"


end
