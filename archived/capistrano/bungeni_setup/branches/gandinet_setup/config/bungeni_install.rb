
### Defines a sequence of tasks for installing bungeni from scratch ###
namespace :bungeni_install do
   
    task :cleanup_folders , :roles=> [:app] do
	sudo "rm -rf /tmp/* /tmp/.*?? /tmp/*.log 2> /dev/null"
	sudo %#["$(ls -A /var/cache/apt/archives/*.deb 2> /dev/null)%"] && rm /var/cache/apt/archives/*.deb || echo 'No deb files to delete'#
    end
	
    task :setup, :roles=> [:app] do
	run "echo 'setting up bungeni installation'"
    end

    task :setup_gandi, :roles=> [:app] do
	run "echo 'setting up bungeni installation (gandi) '"
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

    task :full_gandi, :roles=> [:app] do
      run "echo 'bootstraping and running a full buildout (gandi)'"
    end

    task :setup_db, :role=> [:app] do 
      run "echo 'setting up postgres'"
    end
	
    task :svn_perm, :role=> [:app] do
      run "echo 't' > #{system_build_root}/svn_ans_t.txt"
      run "svn info #{repository} --username=#{scm_username} --password=#{scm_password} <#{system_build_root}/svn_ans_t.txt"
    end

    after "bungeni_install:setup","bungeni_install:cleanup_folders", "bungeni_install:svn_perm", "deploy:setup", "deploy:update", "bungeni_install:full"

    after "bungeni_install:setup_from_cache","bungeni_install:cleanup_folders", "bungeni_install:svn_perm",  "deploy:setup", "deploy:update", "bungeni_install:full_from_cache"

    after "bungeni_install:setup_gandi","bungeni_install:cleanup_folders", "bungeni_install:svn_perm", "deploy:setup", "deploy:update", "bungeni_install:full_gandi"

    after "bungeni_install:full", "bungeni_tasks:python_setup", "bungeni_tasks:bootstrap_bo", "bungeni_tasks:buildout_full", "bungeni_install:setup_db"

    after "bungeni_install:full_gandi", "bungeni_tasks:python_setup", "bungeni_tasks:bootstrap_bo", "bungeni_tasks:buildout_full_gandi","bungeni_tasks:supervisord_config_gandi"

    after "bungeni_install:full_from_cache", "bungeni_tasks:python_setup", "bungeni_tasks:bootstrap_bo", "bungeni_tasks:localbuildout_config", "bungeni_tasks:buildout_full_local", "bungeni_install:setup_db"

    after "bungeni_install:setup_db", "bungeni_tasks:setup_db", "bungeni_tasks:install_demo_data", "bungeni_tasks:supervisord_config", "bungeni_tasks:postgres_stop"


end
