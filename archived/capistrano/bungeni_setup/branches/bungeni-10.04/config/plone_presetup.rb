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


### Defines a sequence of tasks for installing plone from scratch ###

#### download URLs for components #####
### can be set to a http / ftp url or an absolute path to the file on the computer

##### Component Specific Parameters ##### 

#### Python build parameters #####

set :user_python24_build_path, "#{user_build_root}/python24"
set :user_python24_runtime, "#{user_install_root}/python24"
set :python24_download_file, File.basename(python24_download_url)
set :python24_src_dir, File.basename(python24_download_file, ".tgz")
set :python24_download_command, get_download_command(python24_download_url)

#### Python imaging parameters ####

set :python24_imaging_build_path, "#{user_build_root}/imaging24"
set :python24_imaging_download_command, get_download_command(python24_imaging_download_url)
set :python24_imaging_download_file, File.basename(python24_imaging_download_url)
set :python24_imaging_src_dir, File.basename(python24_imaging_download_file, ".tar.gz")



namespace :plone_presetup do
	
    desc "Installs the OS prequisites for Bungeni"
    task :essentials, :roles=> [:app] do
	required_libs = [
			"wget",
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
			"zlib1g-dev"  # for postgresql
			]
	install_cmd = "apt-get install " + required_libs * " " 	+ " -y"
	sudo install_cmd
    end

    task :build_python, :roles=> [:app] do
	[
	"mkdir -p #{user_python24_build_path}",
	"rm -rf #{user_python24_build_path}/*.*",
	"mkdir -p #{user_python24_runtime}",
	"cd #{user_python24_build_path} && #{python24_download_command}",
 	"cd #{user_python24_build_path} && tar xvzf #{python24_download_file}",
	"cd #{user_python24_build_path}/#{python24_src_dir} && CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl ./configure --prefix=#{user_python24_runtime}",
	"cd #{user_python24_build_path}/#{python24_src_dir} && CPPFLAGS=-I/usr/include/openssl LDFLAGS=-L/usr/lib/ssl make",
	"cd #{user_python24_build_path}/#{python24_src_dir} && make install"
	].each {|cmd| run cmd}
    end

    task :build_imaging, :roles=> [:app] do
	[
	"mkdir -p #{python24_imaging_build_path}",
	"cd #{python24_imaging_build_path} && rm -rf #{python24_imaging_download_file}",
	"cd #{python24_imaging_build_path} && wget #{python24_imaging_download_url}",
	"rm -rf #{python24_imaging_build_path}/#{python24_imaging_src_dir}",
 	"cd #{python24_imaging_build_path} && tar xvzf #{python24_imaging_download_file}",
	"cd #{python24_imaging_build_path}/#{python24_imaging_src_dir} && #{user_python24_runtime}/bin/python setup.py build_ext -i",
	"cd #{python24_imaging_build_path}/#{python24_imaging_src_dir} && #{user_python24_runtime}/bin/python setup.py install"
	].each {|cmd| run cmd}
    end

    desc "the build_all task sets up all the prerequisites for a bungeni buildout"
    task :build_all, :roles=> [:app] do
	run "echo 'Installing all bungeni prerequisites'"
    end 
	
	
    after "plone_presetup:build_all",  "plone_presetup:build_python", "plone_presetup:build_imaging"


end
