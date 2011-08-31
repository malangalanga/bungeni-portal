#### varnish parameters ###


namespace :varnish_presetup do

    task :build_varnish, :roles=> [:app] do 
	[
	"mkdir -p #{varnish_build_path}",
	"rm -rf #{varnish_build_path}/*.*",
	"mkdir -p #{varnish_runtime}",
	"cd #{varnish_build_path} && #{varnish_download_command}",
 	"cd #{varnish_build_path} && tar xvzf #{varnish_download_file}",
	"cd #{varnish_build_path}/#{varnish_src_dir} && ./configure --prefix=#{varnish_runtime}",
	"cd #{varnish_build_path}/#{varnish_src_dir} && make && make install"
	].each {|cmd| run cmd}
    end

end

