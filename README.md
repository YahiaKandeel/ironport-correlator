# IronPort-correlator
Correlate Cisco IronPort ESA messages into one JSON document. A tool that is used as a hub between IronPort and a SIEM solution


![HLD](/images/hld.png "High Level Design")

### Features
* Support Unicode Subject (i.e. Arabic, Turkish, Greek ..etc)
* Expand log message, (one Syslog per recipient)
* Boolean flags for internal engines (Antivirus, DKIM, DMARK, SPF)


### Why This Tool
The motivation behind this tool is to ship IronPort's email Syslog related messages to a SIEM solution in one Syslog message.

IronPort Email Security Appliance works as an MTA server that accepts emails from all other MTAs on the Internet. It is designed to detect and block a wide variety of email-borne threats, such as malware, spam, and phishing attempts. 

When an email reaches IronPort it will be looped through multi-scanning filters/engines. Each engine will report back the status of the scanning result, is there malware in the email? is it from a trusted source? does it have a phishing URL ..etc?


When IronPort is configured to send it's Syslog messages to a centralized log collector; each engine will send a one or more Syslog message per email. In the end, you will end up having many Syslog messages all of the related to one email which make it very hard for the SIEM to do the correlation of different log-sources:
* Dropped|Queued Messages
* Content Filters Logs
* SPF|DKIM|DMARK Logs
* Anti-Spam Logs|Archive
* Anti-Virus Logs|Archive
* SDR Logs
* LDAP Logs
* Reporting Logs
* Scanning Logs
* Safe/Block Lists Logs


#### Example Output:

```
{'Action': 'notify-copy || queued for delivery',
 'Action_Desc': '',
 'Antivirus': 'CLEAN',
 'Attachments': '',
 'CASE': 'spam negative',
 'Content_Filter': 'Blacklisted_Headers',
 'DKIM': 'pass',
 'DKIM_Detail': 'pass signature verified (d=gmail.com s=20161025 i=@gmail.com)',
 'DMARK': 'passed',
 'DMARK_Detail': 'Message from domain gmail.com, DMARC pass (SPF aligned True DKIM aligned False)',
 'DomainAge': '21 years 11 months 7 days for domain: mail-wr1-f50.google.com',
 'From': 'xxxxx@gmail.com',
 'GRAYMAIL': 'negative',
 'ICID': '120873890',
 'IP': 'x.x.x.x',
 'LDAP_Drop': '',
 'MID': '43553478',
 'MessageID': '<xxxxxxxxx@notifications.xxxxx.com>',
 'OutbreakFilters': 'negative',
 'Related_MID': '43553479',
 'SPF': 'Pass',
 'SenderReputation': 'Weak',
 'Subject': 'Your video package was uploaded to YouTube',
 'SuspectedDomains': '',
 'ThreatCategory': 'N/A',
 'To': 'yahia.kandeel@xxxxx.com'}
```

### Application Configuration
Tool configurations are based on Environment Variables, So you need to set them before starting the application.

| Env Variable      | Description             | Default Value |
| ----------------- | ----------------------- | ------------- |
| ENV_SYSLOG_SERVER | SIEM Server IP Address  |               |
| ENV_SYSLOG_PORT   | SIEM Server Port (UDP)  | 5144          |
| ENV_SYSLOG_IDENT  | SysLog Message Prefix   | IronPort      |
| ENV_REDIS_KEY     | Redis Key               | ironport      |
| ENV_REDIS_HOST    | Redis Server            |       |
| ENV_TIMEOUT       | Time to wait to correlate all related events per message(in sec) | 30 |
| ENV_MSG_EXPAND    | If true, foreach sender, one syslog message will be sent| True|


### Dependencies
* Logstash

   - Logstash will listen for any incoming Syslog message from IronPort, parse logs, then send it to the Redis Queue.

* Redis Server

   - Redis contains all parsed IronPort messages as well as the parsed messaged by the Python Application.


### The Correlator
The correlator is a multiprocessing Python3 App, that contains three processes:
1. Correlator
   - correlate all messages and send them
   - send them back to Redis with EPOCH

2. Monitor
   - Looks for the expired Messages
   - Remove them from Redis, and
   - Send them to the Logger Process

3. Logger
   - For each Message it will be dumped as a JSON document, then
   - It will be logged either to a Syslog server or to a local file.
   - This process will duplicate the message based on the recipients :)


### Installation
I'm going to cover the installation by using Dockers and bare-metal installation.
For the bare-metal, I'm going to use CentOS7 as my base OS.

#### Using CentOS7
1. Install JAVA SDK (For Logstash)
```bash
sudo yum -y install http://rpms.remirepo.net/enterprise/remi-release-7.rpm
sudo yum install -y wget vim firewalld net-tools gcc make openssl-devel
```

2. Logstash Installation and Configuration
The existing pipeline will instruct to listen on ports 514/udp/tcp, parse then dump the log messages to redis.
```bash
sudo rpm -ivh https://artifacts.elastic.co/downloads/logstash/logstash-7.1.0.rpm
sudo cp ./logstash.conf /etc/logstash/conf.d/ironport.conf
sudo systemctl enable logstash --now
```

3. Redis Installation and Configuration
```bash
sudo yum install -y redis
# Start the services
sudo systemctl enable redis --now
```

4. Python3 Installation
```bash
sudo yum -y install python36 python36-devel
sudo yum -y install python36-pip
sudo pip3 install ipython redis
```

5. Application Configuration
You need to export your envs before running the application.

``` bash
python3 ./main.py
```

#### The easy way
You do have an install.sh script
```bash
sudo ./install.sh
```

#### Using Vagrant
Make sure you have a pre-configured vagrant environment.

1. Clone the repo
```bash
git clone git@github.com:YahiaKandeel/ironport-correlator.git
```

2.  Edit envs.sh file(as mentioned before), 

3.  edit Vagrantfile to configure the network parameters

4. Bring it up

```bash
vagrant up
```

Take it down
```bash
vagrant destroy -f 
```

#### Using Docker
A Dockerfile is provided if you wish to build a docker image.

```bash
docker build -t yahiakandeel/ironportcorrelator:latest . 
```

A docker-compose file is provided if you wish to use docker-compose.

```bash
docker-compose up -d 
```

Stop the container.

```bash
docker-compose down
```