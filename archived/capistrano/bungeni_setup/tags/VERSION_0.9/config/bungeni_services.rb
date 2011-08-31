namespace :bungeni_services do

desc "Start Bungeni"

    task :start_pg, :roles => [:app] do
	run "echo 'Starting postgres'"
    end

    task :stop_pg, :roles => [:app] do
	run "echo 'Stopping postgres'"
    end


    task :start_bungeni, :roles => [:app] do
	run "echo 'Starting Bungeni...'"
    end

    task :stop_bungeni, :roles => [:app] do
	run "echo 'Stopping Bungeni...'"
    end

    task :restart_bungeni, :roles => [:app] do
	run "echo 'Restarting Bungeni...'"
    end

    after "bungeni_services:start_bungeni", "bungeni_tasks:start_supervisor"
    after "bungeni_services:stop_bungeni", "bungeni_tasks:stop_supervisor"
    after "bungeni_services:restart_bungeni", "bungeni_services:stop_bungeni", "bungeni_services:start_bungeni"

    after "bungeni_services:start_pg", "bungeni_tasks:postgres_start"
    after "bungeni_services:stop_pg", "bungeni_tasks:postgres_stop"
    after "bungeni_services:restart_pg", "bungeni_services:stop_pg", "bungeni_services:start_pg"


end

