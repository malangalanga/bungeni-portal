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




namespace :bungeni_presetup do
	
    desc "Installs the OS prequisites for Bungeni"
    task :essentials, :roles=> [:app] do
	required_libs = [
			"wget",
			"zip",
			"unzip",
			"build-essential", # for building from source
			"linux-headers-`uname -r`", # for building from source
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
			"libsqlite3-dev", #for python unit tests
			"uuid-dev", # for ubuntu 9.04 xapian
			"openoffice.org-headless", #for generating pdf reports
			"python-uno", #for generating pdf reports
			"libtidy-dev" #required by tidy
			#"libaprutil1-dev", # for svn
			#"swig", # for svn
			#"xmlto" # for libneon 
			]
	install_cmd = "apt-get install " + required_libs * " " 	+ " -y"
	sudo install_cmd
    end

    desc "Installs the OS prequisites for Bungeni"
    task :essentials_gandi, :roles=> [:app] do
	required_libs = [
			"wget",
			"zip",
			"unzip",
			"build-essential", # for building from source
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
			"libsqlite3-dev", #for python unit tests
			"uuid-dev" # for ubuntu 9.04 xapian
			#"libaprutil1-dev", # for svn
			#"swig", # for svn
			#"xmlto" # for libneon 
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
	"cd #{user_python_build_path}/#{python_src_dir} && CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl ./configure --prefix=#{user_python25_runtime} USE=sqlite",
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






    desc "the build_all task sets up all the prerequisites for a bungeni buildout"
    task :build_all, :roles=> [:app] do
	run "echo 'Installing all bungeni prerequisites'"
    end 
	
    desc "the build task for prerequisites on the gandi platform"
    task :build_all_gandi, :roles=> [:app] do
	run "echo 'Installing gandi pre-requisities'"
    end	

    after "bungeni_presetup:build_all", "bungeni_presetup:essentials", "bungeni_presetup:build_python", "bungeni_presetup:build_imaging"  ###, "varnish_presetup:build_varnish"
    after "bungeni_presetup:build_all_gandi", "bungeni_presetup:essentials_gandi", "bungeni_presetup:build_python", "bungeni_presetup:build_imaging"

end
