
namespace :plone_tasks do

    ## setup easy_install for the python and then install supervisord
    task :python_setup, :roles => [:app] do
      run "cd #{user24_python_home} && [ -f ./ez_setup.py ] && echo 'ez_setup.py exists' || wget http://peak.telecommunity.com/dist/ez_setup.py"
      run "cd #{user24_python_home} && #{user24_python} ./ez_setup.py"
      run "#{user24_python_home}/bin/easy_install supervisor"
    end

    desc "write local buildout file"
    task :localbuildout_config, :roles => [:app] do
        file = File.join(File.dirname(__FILE__), "templates", plone_local_buildout_config_file+".erb")
        template = File.read(file)
        buffer = ERB.new(template).result(binding)
        put buffer, "#{plone_buildout_dir}/#{plone_local_buildout_config_file}", :mode => 0644
	run "echo 'Local buildout configuration has been generated'"
    end


    task :plone_checkout, :roles => [:app] do
	run "mkdir -p #{plone_buildout_dir}"
	run "svn co #{plone_respository} #{plone_buildout_dir} --username=#{scm_username} --password=#{scm_password} "
    end 


    desc "bootstrap"
    task :bootstrap_bo, :roles=> :app do
      run  "cd #{plone_buildout_dir} && #{user24_python} ../bootstrap.py"
    end


    desc "full buildout"
    task :buildout_full, :roles=> :app do
      run "cd #{plone_buildout_dir} && PATH=#{buildout_dir}/parts/postgresql/bin:$PATH PYTHON=#{user24_python} ./bin/buildout -t 3600"
    end

    desc "full buildout"
    task :buildout_full_local, :roles=> :app do
      run "cd #{plone_buildout_dir} &&  PATH=#{buildout_dir}/parts/postgresql/bin:$PATH PYTHON=#{user24_python} ./bin/buildout -t 3600 -c #{plone_local_buildout_config_file} -v"
    end

    desc "optimisitic builout"
    task :buildout_opt, :roles=> :app do
      run "cd #{plone_buildout_dir} && PATH=#{buildout_dir}/parts/postgresql/bin:$PATH PYTHON=#{user24_python} ./bin/buildout -N"
    end

    
    desc "optimisitic builout local"
    task :buildout_opt_local, :roles=> :app do
      run "cd #{plone_buildout_dir} && PATH=#{buildout_dir}/parts/postgresql/bin:$PATH PYTHON=#{user24_python} ./bin/buildout -N -c #{plone_local_buildout_config_file} -v"
    end

    desc "add plone 0 user"
    task :add_admin_user, :roles=> :app do
      run "cd #{plone_buildout_dir} && ./bin/addzope2user admin #{plone_admin_password}"
    end
	

    desc "update source"
    task :plone_upd, :roles=> :app do
      run "cd #{plone_buildout_dir} && svn up"
      run "cd #{plone_buildout_dir}/src && svn up"
    end

    desc "update zope conf" 
    task :update_zopeconf, :roles=> :app do
      run "cd #{plone_buildout_dir} && sed -i 's|INSTANCE \.|INSTANCE #{plone_buildout_dir}|g' ./etc/zope.conf"
    end

    desc "create filestorage folder" 
    task :create_fs_folder, :roles=> :app do
      run "cd #{plone_buildout_dir} && mkdir -p ./var/filestorage"
    end
    
    desc "import demo data "
    task :import_demo_data, :roles=> :app do
      run "cd #{plone_buildout_dir} && mkdir -p ./import"
      run "cd #{plone_buildout_dir}/import && rm -rf *.*"
      run "cd #{plone_buildout_dir}/import && wget #{plone_demo_data}"
    end



    desc "stop plone"
    task :stop_plone, :roles=> :app do
      run "#{supervisorctl} -c #{buildout_dir}/supervisord.conf stop plone"
    end

    desc "start plone"
    task :start_plone, :roles=> :app do
      run "#{supervisorctl} -c #{buildout_dir}/supervisord.conf start plone"
    end



end
