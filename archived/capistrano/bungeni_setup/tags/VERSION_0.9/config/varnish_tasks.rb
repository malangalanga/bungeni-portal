#### varnish parameters ###


namespace :varnish_tasks do

    desc "write varnish vcl config"
    task :varnish_config, :roles => [:app] do
 	run "cd #{varnish_vcl_config_folder} && [ -f ./#{varnish_vcl_file} ] && echo '#{varnish_vcl_file} exists' || rm -f #{varnish_vcl_file}"
        file = File.join(File.dirname(__FILE__), "templates", varnish_vcl_file+".erb")
        template = File.read(file)
        buffer = ERB.new(template).result(binding)
	put buffer, "#{varnish_vcl_config}", :mode => 0644
	run "echo 'Varnish vcl config created'"
    end


end

