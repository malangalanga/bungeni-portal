#### CONFIG VARIABLE SETTING ####

set :application, "bungeni"
#set :bungeni_username, "bungeni"
set :repository,  "https://bungeni-portal.googlecode.com/svn/bungeni.buildout/trunk"

## prompt for svn user names & passwords
set :scm, :subversion

set :scm_auth_cache, true
## all prompts here
#prompt_def(:bungeni_username, 'User name to run as:', 'bungeni')
set :scm_username, "bungenibuild" #Proc.new { Capistrano::CLI.ui.ask('SVN Username: ') }
set :scm_password, "CC2Hy6xh5Pz6" #Proc.new { Capistrano::CLI.password_prompt('SVN Password: ') }
#prompt_def(:user_python_home, 'User Python Home Directory', "/home/bungeni/apps/python" )
#prompt_def(:deploy_to_root, 'Deploy within this folder: ', '/home/bungeni/bungeni_deploy')
set :user_python_home, "#{user_python25_runtime}"
set :deploy_to_root, "#{user_install_root}/bungeni_install"


## user python is used to run bungeni in the user context -- this is a pre-requisite
#was "/home/bungeni/apps/python"
set :user_python, "#{user_python_home}/bin/python"

## admin python is used to run supervisord can be same as user python or a different one
set :adm_python_home, "#{user_python_home}"
set :adm_python, "#{adm_python_home}/bin/python"


## generate supervisord config files
## config file for supervisord is generated using a ERB template
## supervisord is installed using ez_setup

set :supervisord, "#{adm_python_home}/bin/supervisord"
set :supervisorctl, "#{adm_python_home}/bin/supervisorctl"

# erb template to supervisord.conf
set :supervisord_config_file, "supervisord.conf.erb"
set :supervisord_config_gandi_file, "supervisord_gandi.conf.erb"

## force prompt if any unknown prompts pop up
default_run_options[:pty] = true

## set :deploy_to_root, Proc.new { Capistrano::CLI.password_prompt('Deploy within this folder: ') }
set :deploy_to, "#{deploy_to_root}/#{application}"
#was set :deploy_to, "/home/bungeni/bungeni_deploy/#{application}"
set :buildout_dir, "#{deploy_to}/current"
set :local_buildout_config_file , "buildout_local.cfg"

#set :user, "#{bungeni_username}"
set :use_sudo, false
set :app_host, "localhost"

#### ROLE SETTING ####
#
# db role is not required for capistrano 
# for webistrano, a db role is mandatory. so we add the following line for webistrano
# which adds the db role but never deploys or releases it
# role :db, "demo.bungeni.org", {:no_release=>true, :primary=>true}
#

role :app, "#{bungeni_username}@#{app_host}"

