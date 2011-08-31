
### Defines a sequence of tasks for installing bungeni from scratch ###
namespace :plone_install do
	
    task :setup, :roles=> [:app] do
	run "echo 'setting up plone installation'"
    end

    task :setup_from_cache, :roles=> [:app] do
	run "echo 'setting up plone installation (cached) '"
    end

    task :full, :roles=> [:app] do
      run "echo 'bootstraping and running a full buildout'"
    end

    task :full_from_cache, :roles=> [:app] do
      run "echo 'bootstraping and running a full buildout (cached)'"
    end


#### After Hooks ####

	after "plone_install:setup_from_cache", 
		"plone_tasks:plone_checkout"

	after "plone_install:setup",
		"plone_tasks:plone_checkout"

	after "plone_install:full_from_cache",
		"plone_install:setup_from_cache",
		"plone_tasks:bootstrap_bo",
		"plone_tasks:localbuildout_config",
		"plone_tasks:buildout_full_local",
		"plone_tasks:create_fs_folder",
	        "plone_tasks:update_zopeconf",
		"plone_tasks:add_admin_user"
		

			
	after "plone_install:full",
		"plone_install:setup",
		"plone_tasks:bootstrap_bo",
		"plone_tasks:buildout_full",
		"plone_tasks:create_fs_folder",
	        "plone_tasks:update_zopeconf",
		"plone_tasks:add_admin_user"

end
