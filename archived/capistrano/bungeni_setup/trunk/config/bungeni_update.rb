### Defines a sequence of tasks for updating bungeni ###

namespace :bungeni_update do

    task :quick_update, :roles=> :app do
      run "echo 'Running optimistic update of bungeni'"
    end

    task :quick_update_with_db, :roles=> :app do
      run "echo 'Runnning quick update with db update'"
    end

    task :quick_update_local, :roles=> :app do
      run "echo 'Running optimistic update of bungeni'"
    end

    task :stop_all_services, :roles=> :app do
      run "echo 'Stopping all services'"
    end


    task :quick_update_with_db_local, :roles=> :app do
      run "echo 'Runnning quick update with db update'"
    end

    
    after "bungeni_update:stop_all_services", 
		"bungeni_tasks:stop_bungeni", 
		"plone_tasks:stop_plone",
		"portal_tasks:stop_portal"


    after "bungeni_update:quick_update", 
		"bungeni_tasks:stop_bungeni", 
		"bungeni_tasks:bungeni_upd", 
		"bungeni_tasks:buildout_opt", 
		"bungeni_tasks:start_bungeni"

    after "bungeni_update:quick_update_local", 
		"bungeni_tasks:stop_bungeni", 
		"bungeni_tasks:bungeni_upd", 
		"bungeni_tasks:buildout_opt_local", 
		"bungeni_tasks:start_bungeni"


    after "bungeni_update:quick_update_with_db",  
		"bungeni_tasks:stop_bungeni", 
		"bungeni_tasks:bungeni_upd", 
		"bungeni_tasks:buildout_opt", 
		"bungeni_tasks:reset_db", 
		"bungeni_tasks:install_demo_data", 
		"bungeni_tasks:start_bungeni"

    after "bungeni_update:quick_update_with_db_local",  
		"bungeni_update:stop_all_services", 
		"bungeni_tasks:bungeni_upd", 
		"bungeni_tasks:buildout_opt_local", 
		"bungeni_tasks:reset_db", 
		"bungeni_tasks:install_demo_data", 
		"bungeni_tasks:start_bungeni"

end
