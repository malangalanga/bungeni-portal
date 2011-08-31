
### Defines a sequence of tasks for installing bungeni from scratch ###
namespace :portal_install do
	
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

	after "portal_install:setup_from_cache", 
		"portal_tasks:portal_checkout"

	after "portal_install:full_from_cache",
		"portal_install:setup_from_cache",
		"portal_tasks:bootstrap_bo",
		"portal_tasks:localbuildout_config",
		"portal_tasks:buildout_full_local"
		

end
