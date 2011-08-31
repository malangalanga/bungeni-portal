### Defines a sequence of tasks for updating bungeni ###

namespace :portal_update do

    task :quick_update, :roles=> :app do
      run "echo 'Running optimistic update of bungeni'"
    end

    task :quick_update_local, :roles=> :app do
      run "echo 'Running optimistic update of bungeni'"
    end

    after "portal_update:quick_update", 
		"portal_tasks:stop_portal", 
		"portal_tasks:portal_upd", 
		"portal_tasks:buildout_opt", 
		"portal_tasks:start_portal"

    after "portal_update:quick_update_local", 
		"portal_tasks:stop_portal", 
		"portal_tasks:portal_upd", 
		"portal_tasks:buildout_opt_local", 
		"portal_tasks:start_portal"

end
