=begin
Groups various pre-setup and setup recipes to run the installer
=end




namespace :dspace_install do
    desc "Full Install of DSpace  with Postgres"
    task :full, :roles=> [:app] do
	run "echo 'Installing Postgres / DSpace / Tomcat'"
    end 

    after "dspace_install:full", 
	 	"dspace_presetup:essentials", 
		"dspace_presetup:init", 
		"dspace_presetup:jvm",
		"dspace_presetup:tomcat",
		"dspace_presetup:maven",
		"dspace_presetup:ant",
		"dspace_presetup:postgres",
		"dspace_presetup:dspace",
		"dspace_setup:create_db",
		"dspace_setup:setup_dspace_cfg",
		"dspace_setup:setup_dspace_dsrun",
		"dspace_setup:build_dspace",
		"dspace_setup:create_admin",
		"dspace_setup:setup_tomcat_cfg",
		"dspace_services:start_tomcat"

end
