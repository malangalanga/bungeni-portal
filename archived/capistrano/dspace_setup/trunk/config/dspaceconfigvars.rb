#### CONFIG VARIABLE SETTING ####

set :user, "#{bungeni_username}"
set :use_sudo, false
set :app_host, "localhost"
## force prompt if any unknown prompts pop up


#### ROLE SETTING ####
#
# db role is not required for capistrano 
# for webistrano, a db role is mandatory. so we add the following line for webistrano
# which adds the db role but never deploys or releases it
# role :db, "demo.bungeni.org", {:no_release=>true, :primary=>true}
#

role :app, "#{bungeni_username}@#{app_host}"

