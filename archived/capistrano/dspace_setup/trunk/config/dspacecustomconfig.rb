### General Parameters ###
set :application, "bungeni-dspace"
set :bungeni_username, "undesa"
set :user_root, "/home/undesa/bungeni_dspace"
set :dl_cache_folder, "/home/undesa/cache"

### Download URLs ###
set :java6_download_url, "#{dl_cache_folder}/jdk-6u14-ea-bin-b06-linux-i586-06_may_2009.bin" # "http://www.java.net/download/jdk6/6u14/promoted/b06/binaries/jdk-6u14-ea-bin-b06-linux-i586-06_may_2009.bin"
set :tomcat_download_url, "#{dl_cache_folder}/apache-tomcat-5.5.27.tar.gz" #"http://mirror.cinquix.com/pub/apache/tomcat/tomcat-5/v5.5.27/bin/apache-tomcat-5.5.27.tar.gz"
set :maven_download_url, "#{dl_cache_folder}/apache-maven-2.1.0-bin.tar.gz" #"http://www.apache.org/dist/maven/binaries/apache-maven-2.1.0-bin.tar.gz"
set :ant_download_url, "#{dl_cache_folder}/apache-ant-1.7.1-bin.tar.gz" #"http://archive.apache.org/dist/ant/binaries/apache-ant-1.7.1-bin.tar.gz"
set :pg_download_url, "#{dl_cache_folder}/postgresql-8.3.7.tar.gz" #"http://wwwmaster.postgresql.org/download/mirrors-ftp/source/v8.3.7/postgresql-8.3.7.tar.gz"
set :dspace_download_url, "#{dl_cache_folder}/dspace-1.5.2-release.tar.gz"


### Tomcat Params ###
set :tomcat_host, "localhost"
set :tomcat_port, "20000" ## do not use 9000
set :tomcat_admin_user, "admin"
set :tomcat_admin_password, "admin"


### DSpace Admin user ###
set :dspace_admin_email, "ashok@parliaments.info"
set :dspace_admin_fname, "ashok"
set :dspace_admin_lname, "hariharan"
set :dspace_admin_password, "password"


