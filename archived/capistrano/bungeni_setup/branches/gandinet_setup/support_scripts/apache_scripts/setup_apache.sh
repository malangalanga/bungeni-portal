cd /home/undesa/disk1/cap_setup/gandinet_setup/
svn up --username=ashok.hariharan
cd support_scripts
cd apache_setup
sudo cp demo-bungeni /etc/apache2/sites-available/
sudo ln -s /etc/apache2/sites-available/demo-bungeni /etc/apache2/sites-enabled/

