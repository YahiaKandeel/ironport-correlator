# ironport-correlator
Correlate Cisco IronPort ESA messages into one JSON document.

## Why This Tool
The motivation behind this tool is to ship IronPort's email syslog related messages to a SIEM solution in one syslog message.

IronPort Email Security Appliance works as MTA server which accepts emails from all other MTAs on the Internet. It is designed to detect and block a wide variety of email-borne threats, such as malware, spam, and phishing attempts.  When an email reaches IronPort it will be looped through multi-scanning filters/engine. Each engine will report back the status of the scanning result, is there malware in the email? is it from a trusted source? does it have a phishing URL ..etc?

When IronPort is configured to send it's Syslog messages to a centralized log collector; each engine will send a one or more Syslog message per email. In the end, you will end up having many syslog messages all of the related to one email which make it very hard for the SIEM to do the correlation of different log-sources:
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
..........

This tool is used a hub between IronPort and a SIEM solution to correlate between the different Engines, Filters per Email.
```json
{'Action': 'notify-copy || queued for delivery',
 'Action_Desc': '',
 'Antivirus': 'CLEAN',
 'Attachments': '',
 'CASE': 'spam negative',
 'Content_Filter': 'Blacklisted_Headers',
 'DKIM': 'pass',
 'DKIM_Detail': 'pass signature verified (d=gmail.com s=20161025 i=@gmail.com)',
 'DMARK': 'passed',
 'DMARK_Detail': 'Message from domain gmail.com, DMARC pass (SPF aligned True, '
                 'DKIM aligned False)',
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

** Note: This application only supported on Python3

## Components
* Logstash
Logstash will listen for any incoming syslog message from IronPort, then send it to the Redis Queue.

* Redis Server
Redis, contains all IronPort messages as well as the parsed messaged by the Python Application

* Python Application (Correlator)
Correlator is a multiprocessing Python3 App, that contains three processes:
1. Parser
   - reads all incoming syslog messages,
   - parse them using the predefind parses
   - send them back to redis with EPOCH

2. Monitor
   - Looks for the expired Messages
   - Remove them from redis, and
   - Send them to the Logger Process

3. Logger
   - For each Message it will be dumped as a JSON document, then
   - It will be logged either to a Syslog server, or to a local file.
   - This process will duplicate the message based on the recipients :)

## Installation
I'm going to cover the installation by using Dockers and bare-metal installation.
For the bare-metal, I'm going to use CentOS7 as my base OS.

### Using CentOS7
* Install JAVA SDK (For Logstash)
You have to have a running version of JAVA SDK before you proceed, you can find it here: https://www.oracle.com/technetwork/java/javase/downloads/,

* Packages Installation
You need to configure logstash repo by executing the below command.

```bash
sudo echo '''[logstash-2.2]
name=logstash repository for 2.2 packages
baseurl=http://packages.elasticsearch.org/logstash/2.2/centos
gpgcheck=1
gpgkey=http://packages.elasticsearch.org/GPG-KEY-elasticsearch
enabled=1''' > /etc/yum.repos.d/logstash.repo
```

Then proceed with the installation 
```bash
# Install required packages
sudo yum install -y epel-release
sudo yum install -y python36-pip redis logstash
sudo pip3.6 install redis
```

* Logstash Configuration
you need to create your pipeline to instruct logstash what to do exactly
logstash will be configured to listen on ports 514/udp/tcp and dump the log messages to redis. This can be done using the below command:
```bash
sudo echo '''
input {
  udp {
    port => 514
    type => syslog
  }
  tcp {
    port => 514
    type => syslog
  }
}
output {
  redis {
    key => "ironport"
    data_type => "list"
  }
}
''' > /etc/logstash/conf.d/ironport.conf
```


* Start the services
Start the logstash & redis services
```bash
sudo systemctl enable redis --now
sudo systemctl enable logstash --now
```

* Running the app
basically what do is to configure which Syslog server you wanna forward your logs to, then you can start your application
``` bash
export SYSLOG=<PlaceWithYourSyslogIP>
python3 ./correlator/main.py
```

* Finally IronPort configuration
Lastly, we need to configure Ironport to send its logs to the newly created machine ;)

### Using Dockers
<Coming Soon>
