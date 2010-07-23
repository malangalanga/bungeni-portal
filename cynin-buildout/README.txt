1. Cyn.in Dependency installation using Package Managers

1.1 Ubuntu 8.0.4 (Hardy)

sudo apt-get build-dep python-ldap python-lxml build-essential gcc g++ libc6-dev libssl-dev zlib1g-dev libjpeg62-dev libreadline5-dev readline-common wv python2.4-dev poppler-utils python-imaging python-libxml2 libxml2-dev libxslt1-dev subversion libdb4.4-dev libldap2-dev libsasl2-dev libssl-dev python-ldap python-setuptools

1.2 Ubuntu 8.1.0 (Intrepid) and Debian 5.0 (Lenny)
sudo apt-get install build-essential gcc g++ libc6-dev libssl-dev zlib1g-dev libjpeg62-dev libreadline5-dev readline-common wv python2.4-dev poppler-utils python-imaging python-libxml2 libxml2-dev libxslt1-dev subversion libsasl2-dev libssl-dev python-ldap libdb-dev libldap2-dev python-setuptools

1.3 Ubuntu 9.04 (Jaunty) - should work for 9.10 (Karmic) as well.
sudo apt-get install build-essential libssl-dev libjpeg62-dev libreadline5-dev wv  libxml2-dev libxslt1-dev libsasl2-dev poppler-utils libdb4.4-dev libldap2-dev python2.4-dev

2. Checkout the cynin-buildout
    svn co https://bungeni-portal.googlecode.com/svn/cynin.buildout/trunk/ cynin

3. Checkout cynin source packages and products into the cynin folder

   svn co http://odn.cynapse.com/svn/cynin/tags/cynin_3_1_3/src/ src
   svn co http://odn.cynapse.com/svn/cynin/tags/cynin_3_1_3/products/

4. Modification to the src/ubify.policy configuration file.
   Open the configure.zcml file in the root of the ubify.policy package.
   Line 55 currently reads as follows:
   
   <i18n:registerTranslations directory="locales" />

   Change it to this:

   <!-- <i18n:registerTranslations directory="locales" /> -->


5. Bootstrap the buildout:

   python2.4 ../bootstrap.py

6. Run the buildout:

   ./bin/buildout -v -c local.cfg

7. Start cynin and browse to it at port 8084
   ./bin/paster serve deploy.ini
   

   
