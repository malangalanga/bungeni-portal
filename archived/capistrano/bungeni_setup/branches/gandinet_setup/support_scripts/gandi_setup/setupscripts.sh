echo 'updating ownership'

cd disk1
sudo chown -R undesa:undesa .

echo 'updating ubuntu'
sudo apt-get update
sudo apt-get upgrade

echo 'build environment'
sudo apt-get install ruby-full build-essential rubygems ssh subversion -y

echo 'updating ruby gems'
sudo apt-get autoremove rubygems -y
wget http://rubyforge.org/frs/download.php/60718/rubygems-1.3.5.tgz
tar xzvf rubygems-1.3.5.tgz
cd rubygems-1.3.5
## running without sudo will install the ruby gems within the user's
## home folder e.g. /home/user/.gem/ruby/1.x/bin
sudo ruby setup.rb && sudo ln -s /usr/bin/gem1.8 /usr/bin/gem && sudo gem update --system

echo 'installing rake & capistrano '
sudo gem install rake -y 
sudo gem install capistrano -y
cd ..

echo 'getting cap-scripts'
mkdir cap_setup
cd cap_setup
svn co https://bungeni-portal.googlecode.com/svn/capistrano/bungeni_setup/branches/gandinet_setup --username=ashok.hariharan --password=y8n5h7d9

echo 'updating manual configs for cap scripts'

cd /home/undesa/disk1/cap_setup/gandinet_setup/config
wget -O manual_configs.rb http://sites.google.com/site/ashokhariharan/Home/manual_configs.rb?attredirects=0&d=1

cd ..

cap bungeni_presetup:build_all






