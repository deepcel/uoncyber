---
title: Cyber Security Attacks and Threats
slug: cyber-security-attacks-and-threats
category: Threats
summary: Social engineering, network, credential, web and cloud attacks, malware types, the Cyber Kill Chain and their impact on the CIA triad.
pass_mark: 80
estimated_minutes: 50
---

This module introduces common cyber security threats and attack methods that can put people, businesses, networks, applications and cloud environments at risk. It focuses on how attackers exploit weaknesses through social engineering, network-based attacks, credential attacks, application attacks and cloud-based attacks.

## 2.1 Overview

This module introduces common cybersecurity threats and attack methods that can jeopardise people, businesses, networks, apps, and cloud environments. It focuses on how attackers exploit weaknesses through social engineering, network-based attacks, credential attacks, application attacks, and cloud-based attacks.

## 2.2 Learning Outcomes

At the end of this module, you will be able to:

1. Recognise common social engineering techniques and describe how human behaviour is used for attacks.
2. Explain network-based attacks such as DoS/DDoS, man-in-the-middle, spoofing, session hijacking and packet sniffing.
3. Describe the risks of credential attacks such as credential stuffing, brute force and password spraying that can result in account compromise.
4. Identify web and application vulnerabilities such as XSS, command injection, broken access control and vulnerable applications.
5. Understand the different categories of malware, how they spread and their effects.
6. Explain the features of cloud-based attacks and how they differ from traditional attacks.
7. Discuss the Cyber Kill Chain as the process of a cyber attack.
8. Describe the types of attacks on confidentiality, integrity and availability.

## 2.3 Social Engineering

Social engineering is the psychological manipulation of people into performing actions or sharing confidential information that compromises personal or organisational security. It is one of the easiest ways to gain access to a system, because it is easier to persuade someone than to hack a well-defended system.

Common social engineering techniques:

- **Phishing:** an attack used to steal credentials or spread malware via email, impersonating a trusted contact or organisation.
- **Spear phishing:** similar to phishing, but targeting a specific person (often a senior officer) using personal research.
- **Vishing:** phone-based phishing, often impersonating tech support or a bank.
- **Smishing:** phishing via SMS text messages.
- **Pretexting:** gaining trust by inventing a believable scenario to extract information.
- **Baiting:** luring someone with a tempting item, such as an infected USB drive.
- **Tailgating:** following an authorised person through a secure door without having access yourself.

## 2.4 Network-Based Attacks

Network-based attacks target network infrastructure and connected devices, aiming to steal data, disrupt services, intercept traffic or impersonate others.

- **Denial of Service (DoS) and Distributed DoS (DDoS):** denying access to legitimate users by flooding a server, network or website with a massive amount of fake traffic or complex requests to exhaust its resources.
- **Man-in-the-middle (MITM):** an attacker intercepts, listens to, or alters communication between two parties to steal sensitive data such as login credentials or session tokens.
- **Spoofing:** attackers falsify their identity, IP address or DNS data to trick systems into trusting them, or to reroute traffic to malicious sites.
- **Session hijacking:** an active, authenticated session is taken over by an attacker without the user's permission.
- **Packet sniffing:** capturing unencrypted or poorly secured data packets in transit using network monitoring tools.

### Try it: match the scenario to the attack

| Scenario | Attack? |
|---|---|
| A café hotspot silently reads and alters traffic | ? |
| A website is unreachable under traffic from thousands of devices | ? |
| An email shows a sender address that has been forged | ? |
| An attacker reuses a stolen session token to stay logged in as someone else | ? |

```answer
1. Man-in-the-middle
2. DDoS
3. Spoofing
4. Session hijacking
```

## 2.5 Credential and Account Attacks

Credential attacks happen when an attacker steals, guesses or exploits authentication data to bypass security controls and log in as a legitimate user.

- **Credential stuffing:** exploiting password reuse. Automated bots systematically try thousands of leaked username and password pairs against login pages on other platforms.
- **Brute force:** a trial-and-error method where automated software systematically guesses possible combinations until it finds the correct password or encryption key.
- **Stolen credentials:** credentials exposed through phishing, malware, breaches or insecure storage.
- **Password spraying:** trying a few common passwords against hundreds or thousands of different accounts, to avoid triggering lockouts.

Defences include phishing-resistant multi-factor authentication (MFA), unique passwords stored in a password manager, monitoring for leaked credentials, and Zero Trust access controls.

### Try it: identify the attack

An employee reuses a password that was exposed in an unrelated breach, and an attacker logs in to their work account with it. Name the technique and explain why password reuse is risky.

```answer
Credential stuffing. A password leaked from one site is tried automatically on many other sites. If the same password is reused anywhere, a breach of the weakest site gives access to every account that shares it.
```

## 2.6 Web and Application Attacks

These attacks target flaws in software code, server configuration or application logic to steal data, deface sites or disrupt services.

- **Injection attacks:** attackers insert malicious code, such as SQL or command strings, to manipulate database queries through poorly handled input.
- **Cross-site scripting (XSS):** malicious scripts are injected into trusted websites and run in a victim's browser, stealing cookies, session tokens or other sensitive information.
- **Broken access control:** flaws that let unauthorised users view, modify or delete other accounts' data, or reach admin functions.
- **Vulnerable applications:** applications with weaknesses such as outdated components, insecure authentication or inadequate input validation that attackers can exploit to compromise data, accounts or services.
- **Command injection:** an application passes unvalidated user input to the server's operating system, letting an attacker run commands with the application's privileges.

### Try it: true or false?

1. SQL injection can be prevented by using parameterised queries.
2. Output encoding is the main defence against SQL injection.
3. Outdated software components can make an application vulnerable even if its own code is secure.
4. Multi-factor authentication helps reduce the impact of broken authentication.
5. Hiding the login page prevents SQL injection.

```answer
1. True: parameterised queries keep data separate from the SQL command.
2. False: output encoding is the main defence against XSS. Parameterised queries defend against SQL injection.
3. True: vulnerable libraries and frameworks put the whole application at risk.
4. True: a stolen password alone is no longer enough to sign in.
5. False: hiding a page is not a security control; the input is still vulnerable.
```

## 2.7 Malware

Malware is malicious software designed to disrupt, damage or gain unauthorised access to computer systems. Cyber criminals use it to steal information, obtain banking credentials, sell access to computing resources or personal information, or extort payments from victims.

### Types of malware

| Type | Spreads / delivered by | Effect |
|---|---|---|
| **Adware** | Bundled with free software and malicious browser extensions | Displays unwanted ads, tracks browsing and may redirect to malicious sites |
| **Botnets** | Devices infected by other malware, often poorly secured or unpatched | Infected devices are controlled remotely as a group and used for DDoS, spam and other attacks |
| **Cryptojacking** | Compromised websites, malicious downloads and infected cloud systems | Secretly uses the victim's computing power to mine cryptocurrency, slowing systems and raising costs |
| **Exploits and exploit kits** | Code targeting unpatched software flaws; kits are often delivered via compromised or malicious websites | Automatically finds and uses vulnerabilities to install other malware |
| **Fileless malware** | Phishing, malicious scripts and abuse of built-in tools | Runs in memory using legitimate system tools, leaving few files for antivirus to detect |
| **Ransomware** | Phishing, exposed services and other malware | Locks data or systems and demands payment; data may also be stolen |
| **Rootkits** | Installed after initial access, or bundled with other malware | Hides itself and other malware, and keeps privileged long-term access |
| **Spyware** | Bundled with downloads and malicious attachments | Secretly monitors and collects information |
| **Supply chain attacks** | Compromised software updates, libraries or trusted third-party providers | Malicious code reaches many organisations through a trusted source |
| **Trojans** | Disguised as legitimate software | Provides backdoor access and installs further malware |
| **Worms** | Spread between systems, often through existing vulnerabilities | Causes rapid network-wide infection |
| **Viruses** | Attach to files and run when the file is executed or shared | Corrupts files and disrupts operations |

### Try it: name the malware

An employee opens a Word attachment. No new file is saved, but a PowerShell command runs in memory and contacts an unknown server. Antivirus raises no alerts. What type of malware is this?

```answer
Fileless malware: it runs in memory using a legitimate built-in tool (PowerShell), leaving no file for antivirus to scan.
```

### References

- [Microsoft: What is malware?](https://www.microsoft.com/en-au/security/business/security-101/what-is-malware)

## 2.8 Cloud-Based Attacks

Cloud security attacks are activities initiated by attackers against cloud computing architecture to gain access to sensitive information and resources, or to manipulate data on cloud platforms without authorisation. They are usually intentional and take advantage of common vulnerabilities or misconfigurations in cloud infrastructure.

Cloud attacks differ from traditional threats because cloud environments have unique characteristics:

1. **Multi-tenancy risks:** the cloud isolates different tenants (organisations) from each other, but during an attack that isolation can be breached.
2. **Scalability of threats:** the cloud uses a distributed architecture, so an attack can spread across resources, or even affect multiple customers of the same provider.
3. **Data mobility challenges:** data constantly moves between cloud services and on-premises systems, and can be attacked in transit if it isn't encrypted.
4. **API-centric threats:** many cloud attacks exploit vulnerabilities in the APIs used to integrate cloud services.

### References

- [SentinelOne: Cloud security attacks](https://www.sentinelone.com/cybersecurity-101/cloud-security/cloud-security-attacks/)

## 2.9 Stages of a Cyber Attack

A cyber attack follows the seven stages of the **Cyber Kill Chain**:

1. **Reconnaissance:** harvesting email addresses, conference information and other details about the target.
2. **Weaponisation:** coupling an exploit with a backdoor into a deliverable payload.
3. **Delivery:** delivering the weaponised bundle to the victim via email, web, USB and so on.
4. **Exploitation:** exploiting a vulnerability to run code on the victim's system.
5. **Installation:** installing malware on the asset.
6. **Command and control (C2):** opening a command channel to control the victim's system remotely.
7. **Actions on objectives:** with "hands on keyboard" access, the intruder achieves their original goals.

Stopping an attack at any stage limits its damage. This is why layered defences matter (Module 3).

### References

- [Lockheed Martin: The Cyber Kill Chain](https://www.lockheedmartin.com/en-us/capabilities/cyber/cyber-kill-chain.html)

## 2.10 Impact on the CIA Triad

Revisit section 1.3 of Module 1 for the CIA triad.

<!-- REVIEW: Phishing and SQL injection have no Availability entry in the original. SQL injection can
also delete data (affecting availability), and phishing often delivers ransomware. Consider filling these in. -->

| Attack | Confidentiality | Integrity | Availability |
|---|---|---|---|
| Phishing | Exposed data | Records altered under the stolen accounts | |
| SQL injection | Data read | Data modified | |
| DDoS | | | Services become unavailable |
| Ransomware | Data may be stolen | | Systems locked |
| Spyware | Information secretly collected | | |
| Botnet | | | Services unavailable when used for DDoS |
| Cryptojacking | | | Systems lag or are disrupted |
| Rootkit | Hidden access to data | Logs and system files altered to hide activity | |
| Supply chain attack | Exposed data | Trusted software is tampered with | Services disrupted if the payload is destructive |

## 2.11 Case Studies

Review these real incidents and map each one to the malware, attack types and Kill Chain stages above:

- [Queensland Government: Cyber security case studies](https://www.qld.gov.au/community/your-home-community/cyber-security/cyber-security-for-queenslanders/case-studies)

# Knowledge check

### Which malware spreads between systems using existing vulnerabilities?
- [ ] Trojan
- [ ] Spyware
- [x] Worm
- [ ] Ransomware
Explanation: Worms self-propagate across systems by exploiting existing vulnerabilities.

### Which attack mainly affects availability?
- [ ] Spyware
- [x] DDoS
- [ ] Credential stuffing
- [ ] Phishing
Explanation: A DDoS floods a service so legitimate users cannot reach it.

### Which malware hides its own presence and other malware while keeping privileged access?
- [ ] Adware
- [x] Rootkit
- [ ] Worm
- [ ] Ransomware
Explanation: Rootkits conceal themselves and other malware and maintain privileged long-term access.

### After installing free software, a user's browser shows constant pop-up ads and redirects to unfamiliar sites. This is most likely:
- [ ] A worm
- [ ] Spyware
- [ ] A Trojan
- [x] Adware
Explanation: Adware is bundled with free software and shows unwanted ads and redirects.
