
namespace :portal_tasks do


    desc "write local buildout file"
    task :localbuildout_config, :roles => [:app] do
        file = File.join(File.dirname(__FILE__), "templates", portal_local_buildout_config_file+".erb")
        template = File.read(file)
        buffer = ERB.new(template).result(binding)
        put buffer, "#{portal_buildout_dir}/#{portal_local_buildout_config_file}", :mode => 0644
	run "echo 'Local buildout configuration has been generated'"
    end


    task :portal_checkout, :roles => [:app] do
	run "mkdir -p #{portal_buildout_dir}"
	run "svn co #{portal_repository} #{portal_buildout_dir} --username=#{scm_username} --password=#{scm_password} --no-auth-cache"
    end 

    desc "bootstrap"
    task :bootstrap_bo, :roles=> :app do
      run  "cd #{portal_buildout_dir} && #{user_python} ../bootstrap.py"
    end


    desc "full buildout"
    task :buildout_full, :roles=> :app do
      run "cd #{portal_buildout_dir} && PYTHON=#{user_python} ./bin/buildout -t 3600"
    end

    desc "full buildout"
    task :buildout_full_local, :roles=> :app do
      run "cd #{portal_buildout_dir} && PYTHON=#{user_python} ./bin/buildout -t 3600 -c #{portal_local_buildout_config_file} -v"
    end

    desc "optimisitic builout"
    task :buildout_opt, :roles=> :app do
      run "cd #{portal_buildout_dir} && PYTHON=#{user_python} ./bin/buildout -N"
    end

    
    desc "optimisitic builout local"
    task :buildout_opt_local, :roles=> :app do
      run "cd #{portal_buildout_dir} && PYTHON=#{user_python} ./bin/buildout -N -c #{portal_local_buildout_config_file} -v"
    end



    desc "update source"
    task :portal_upd, :roles=> :app do
      run "cd #{portal_buildout_dir} && svn up"
      run "cd #{portal_buildout_dir}/src && svn up"
    end

    desc "stop portal"
    task :stop_portal, :roles=> :app do
      run "#{supervisorctl} -c #{buildout_dir}/supervisord.conf stop portal"
    end

    desc "start portal"
    task :start_portal, :roles=> :app do
      run "#{supervisorctl} -c #{buildout_dir}/supervisord.conf start portal"
    end




end
