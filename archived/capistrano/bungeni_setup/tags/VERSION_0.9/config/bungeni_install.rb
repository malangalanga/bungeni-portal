
### Defines a sequence of tasks for installing bungeni from scratch ###
namespace :bungeni_install do
	
    task :setup, :roles=> [:app] do
	run "echo 'setting up bungeni installation'"
    end

    task :setup_from_cache, :roles=> [:app] do
	run "echo 'setting up bungeni installation (cached) '"
    end

    task :full, :roles=> [:app] do
      run "echo 'bootstraping and running a full buildout'"
    end

    task :full_from_cache, :roles=> [:app] do
      run "echo 'bootstraping and running a full buildout (cached)'"
    end

    task :setup_db, :role=> [:app] do 
      run "echo 'setting up postgres'"
    end


    after "bungeni_install:setup", "deploy:setup", "deploy:update", "bungeni_install:full"

    after "bungeni_install:setup_from_cache", "deploy:setup", "deploy:update", "bungeni_install:full_from_cache"

    after "bungeni_install:full", "bungeni_tasks:python_setup", "bungeni_tasks:bootstrap_bo", "bungeni_tasks:buildout_full", "bungeni_install:setup_db"

    after "bungeni_install:full_from_cache", "bungeni_tasks:python_setup", "bungeni_tasks:bootstrap_bo", "bungeni_tasks:localbuildout_config", "bungeni_tasks:buildout_full_local", "bungeni_install:setup_db"

    after "bungeni_install:setup_db", "bungeni_tasks:setup_db", "bungeni_tasks:install_demo_data", "bungeni_tasks:supervisord_config", "bungeni_tasks:postgres_stop"


end
