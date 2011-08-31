### Defines a sequence of tasks for updating bungeni ###

namespace :plone_update do

    task :quick_update, :roles=> :app do
      run "echo 'Running optimistic update of bungeni'"
    end

    task :quick_update_local, :roles=> :app do
      run "echo 'Running optimistic update of bungeni'"
    end

    after "plone_update:quick_update", 
		"plone_tasks:stop_plone", 
		"plone_tasks:plone_upd", 
		"plone_tasks:buildout_opt", 
		"plone_tasks:start_plone"

    after "plone_update:quick_update_local", 
		"plone_tasks:stop_plone", 
		"plone_tasks:plone_upd", 
		"plone_tasks:buildout_opt_local", 
		"plone_tasks:start_plone"

end
