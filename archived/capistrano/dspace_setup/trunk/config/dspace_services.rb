
namespace :dspace_services do

    desc "Start Dspace " 
    task :start_tomcat, :roles=> [:app] do
	[
	"echo 'Starting tomcat'",
	"cd #{tomcat_home}/bin && JAVA_HOME=#{java6_home} ./startup.sh"
#	"cd #{dspace_maven_target_dir} && JAVA_HOME=#{java6_home} #{ant_home}/bin/ant fresh_install"
#	"JAVA_HOME=#{java6_home} && cd #{dspace_maven_root} && #{ant_home}/bin/ant",
#	"JAVA_HOME=#{java6_home} && cd #{dspace_maven_root} && #{ant_home}/bin/ant fresh_install"
	].each {|cmd| run cmd}	
    end

    task :stop_tomcat, :roles=> [:app] do
	[
	"echo 'Stopping tomcat'",
	"cd #{tomcat_home}/bin && JAVA_HOME=#{java6_home} ./shutdown.sh"
#	"cd #{dspace_maven_target_dir} && JAVA_HOME=#{java6_home} #{ant_home}/bin/ant fresh_install"
#	"JAVA_HOME=#{java6_home} && cd #{dspace_maven_root} && #{ant_home}/bin/ant",
#	"JAVA_HOME=#{java6_home} && cd #{dspace_maven_root} && #{ant_home}/bin/ant fresh_install"
	].each {|cmd| run cmd}	
    end

    task :restart_tomcat, :roles=> [:app] do
	[
	"echo 'Restarting Tomcat'"
	].each {|cmd| run cmd}
    end

    after "dspace_services:restart_tomcat", "dspace_services:stop_tomcat", "dspace_services:start_tomcat"


    task :pg_start, :roles=>[:app] do 
	[
	"echo 'Starting Postgres'",
	"cd #{pg_home}/bin && ./pg_ctl -D #{pg_data} start "
	].each { |cmd| run cmd}
     end

    task :pg_stop, :roles=>[:app] do 
	[
	"echo 'Stopping Postgres'",
	"cd #{pg_home}/bin && ./pg_ctl -D #{pg_data} stop "
	].each { |cmd| run cmd}
     end


end
