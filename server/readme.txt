Setup Server
============
- Launch an EC2 machine
    - note the region!
    - OS: Amazon Linux is RHEL clone; better suited for AWS - recommended
    - kind:
        - t2 micro is too weak
        - t2 medium is great
        - trying t3.small   # PyCharm remote needs at least 4GB - this doesn't have enough - is it important? not sure...
    - security group:
        - open ports 22,80 and maybe 443
    - disk: I took 20GB
    - allocate and associate an elastic IP to have a static IP (free when the machine is running; paying for the IP when the machine is down)
- connect with command like:
    ssh -X -L 8983:localhost:8983 -i "whatever.pem" ec2-user@ec2-54-157-58-145.compute-1.amazonaws.com
    - allows using 'http://localhost:8983/solr/' ; GUI ; connect with .pem key file
- update packages:
     sudo yum -y update
- ssh:
    - add to /etc/ssh/sshd_config  (to allow PyCharm remote connection - very handy)
         AllowTcpForwarding yes
    - restart service:
        $ sudo systemctl restart sshd
- apache:
    - install:
        sudo yum install -y httpd
    - in /etc/httpd/conf/httpd.conf, under <Directory "/var/www/cgi-bin">   (to allow running search.py for AJAX)
        replace
            Options None
        with
            Options +ExecCGI
            AddHandler cgi-script .cgi .pl .py
    - same file, replace    (to disable directories listings)
            Options Indexes FollowSymLinks
        with
            Options FollowSymLinks
    - in the same file, at the end, add:
            # Added by Zvika:
            <VirtualHost *:80>
                    RedirectMatch ^/$ /milon/
            </VirtualHost>
    - start apache now, and forever:
        $ sudo systemctl start httpd
        $ sudo systemctl enable httpd
    - set apache permissions to regulard ec2-user:
        sudo usermod -a -G apache ec2-user
        exit
        # ssh again
        sudo chown -R ec2-user:apache /var/www
        sudo chmod 2775 /var/www
        find /var/www -type d -exec sudo chmod 2775 {} \;
        find /var/www -type f -exec sudo chmod 0664 {} \;
- search.py
    - copy search.py to /var/www/cgi-bin/milon/search.py
    - chmod +x /var/www/cgi-bin/milon/search.py
- install Java 11 (for solr):
    sudo yum install java-11-amazon-corretto
- install solr:
    $ wget https://www.apache.org/dyn/closer.lua/solr/solr/9.1.0/solr-9.1.0.tgz?action=download
    $ mv solr-9.1.0.tgz\?action\=download solr-9.1.0.tgz
    $ tar xzf solr-9.1.0.tgz solr-9.1.0/bin/install_solr_service.sh --strip-components=2
    $ sudo bash ./install_solr_service.sh solr-9.1.0.tgz
    note: this installs to /opt/solr, /var/solr, and creates a 'solr' user
    to check status:
    $ sudo service solr status
    - maybe enable langId module in solr.xml?


milon update
============
- copy local output/www to server /var/www/html/milon/

solr update
===========
- delete and create new 'core':
    sudo su solr
    /opt/solr/bin/solr delete -c milon
    /opt/solr/bin/solr create -c milon
    exit
    - TODO: do it with 'curl' or other API
- update search index with docs_to_index.json
    - currently done with GUI, http://localhost:8983/solr
    - check the following methods:
        $ curl 'http://localhost:8983/solr/milon/update?commit=true' --data-binary docs_to_index.json -H 'Content-type:application/json'  -H 'Content-type:application/json'
        $ /opt/solr/bin/post -c milon docs_to_index.json

