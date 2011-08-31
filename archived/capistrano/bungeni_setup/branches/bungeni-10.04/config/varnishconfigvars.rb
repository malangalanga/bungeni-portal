#### CONFIG VARIABLE SETTING ####

### for building & installing varnish
set :varnish_build_path, "#{user_build_root}/varnish"
set :varnish_runtime, "#{user_install_root}/varnish"
set :varnish_download_url, "/home/undesa/cache/varnish-2.0.6.tar.gz"
set :varnish_download_command, get_download_command(varnish_download_url)
set :varnish_download_file, File.basename(varnish_download_url)
set :varnish_src_dir, File.basename(varnish_download_file, ".tar.gz")

## for configuring varnish
set :varnish_port, "8080"
set :varnish_admin_host, "localhost"
set :varnish_admin_port, "6082"
set :varnish_vcl_file, "bungeni.vcl"
set :varnish_vcl_config_folder, "#{varnish_runtime}/etc/varnish"
set :varnish_vcl_config, "#{varnish_vcl_config_folder}/#{varnish_vcl_file}"
set :varnish_cache_folder, "#{varnish_runtime}/cache"
set :varnish_cache_file, "varnish.cache"
set :varnish_cache, "#{varnish_cache_folder}/#{varnish_cache_file}"
set :varnish_cache_mem, "64M"



