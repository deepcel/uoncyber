---
title: Security Domains: Network, Cloud and Data Security
slug: security-domains-network-cloud-data
category: Defence
summary: How network, cloud and data security controls work together as layered defence to protect the CIA triad.
pass_mark: 80
estimated_minutes: 45
---

Module 2 looked at how attackers target people, credentials, networks, applications and systems. This module moves from individual attacks to the broader domains organisations use to defend against them: network security, cloud security and data security.

<!-- REVIEW: the original numbering skipped 3.2 (3.1 then 3.3). Sections are renumbered 3.1 to 3.5 here. -->

## 3.1 Introduction to Security Domains

Module 2 examined how attackers target people, credentials, networks, applications and systems through specific attack techniques. This module shifts the focus from individual attacks to the broader domains of practice that organisations use to defend against them. A **security domain** groups together the principles, technologies and practices used to protect a particular part of an organisation's environment.

This module covers three connected domains:

- **Network security** protects the infrastructure that carries data between systems.
- **Cloud security** addresses the shared-responsibility environment of cloud-hosted services.
- **Data security** protects the information itself, wherever it is stored or processed.

Together, these domains provide layered protection consistent with the CIA triad introduced in Module 1.

### Learning outcomes

By the end of this module, you should be able to:

1. Explain the purpose and scope of network, cloud and data security as distinct but related domains.
2. Identify common network security controls and their function.
3. Describe the shared responsibility model and common cloud misconfigurations.
4. Explain core data security practices, including encryption and access control.
5. Recognise how the three domains work together to protect the CIA triad.

## 3.2 Network Security

Network security covers connected systems, devices and traffic. It aims to block unwanted access, identify malicious activity and keep network services available, countering many of the network attacks in Module 2.

### Firewalls

A firewall controls traffic to and from a network according to predefined rules, between trusted internal networks and untrusted external networks such as the internet. Firewalls work at different layers, from simple packet filtering to inspecting the content of application traffic.

### Network segmentation

Segmentation divides an organisation's network into smaller, separate sections to contain the spread of an attack if one part is breached. For instance, staff workstations are separated from servers holding sensitive information, limiting the damage to a single infected machine.

### VPN (Virtual Private Network)

A VPN creates a secure connection over an untrusted network. It encrypts the data passing through it and lets remote users access network resources securely. It directly protects against the man-in-the-middle and packet sniffing attacks from Module 2.

### Intrusion detection and prevention systems (IDS/IPS)

An IDS monitors a network for suspicious activity and alerts staff, while an IPS can also automatically block it. Both use pattern matching for known attacks or unusual behaviour.

### Network access control (NAC)

Network access control decides which devices and users are allowed on a network, usually verifying identity and device security posture before granting access. This reduces the threat from unauthorised or unmanaged devices.

### Try it: what went wrong?

A contractor plugs a personal laptop into the office network. The laptop has malware, which spreads through the network to the server containing payroll information. For three days, no one notices.

1. Which control would have prevented the laptop from connecting?
2. Which control would have helped stop the malware spreading?
3. Which control would have detected the unusual activity earlier?

```answer
1. Network access control (NAC)
2. Network segmentation
3. An intrusion detection/prevention system (IDS/IPS)
```

## 3.3 Cloud Security

Cloud security focuses on securing data, applications and infrastructure hosted in cloud environments. It differs from traditional on-premises security because responsibility is shared, and the danger often comes not from the cloud service itself but from how you configure it.

### The shared responsibility model

Cloud providers are typically responsible for the security **of** the cloud: physical infrastructure, networks and host systems. The customer is responsible for security **in** the cloud: what they configure, who can access it and what they protect. Security gaps often appear when people don't understand this division.

### Misconfiguration

A misconfiguration is when cloud resources are set up to be more open to attack than intended, for example by leaving default settings in place. Cloud services are internet-facing, and misconfiguration is one of the most common causes of cloud security incidents.

### Exposed storage

Cloud storage can be made public, on purpose or by accident. An exposed storage bucket makes its data visible to anyone with the link, or to anyone scanning the internet, without authentication.

### Identity and Access Management (IAM)

IAM controls who can use cloud resources and what they can do with them. Overly broad permissions mean a compromised account can do significant damage, and permissions tend to accumulate over time ("privilege creep"). The **principle of least privilege** counters this by giving each account only the access it needs to do its job.

### Insecure APIs

Cloud services are accessed through application programming interfaces (APIs). An API that is poorly secured, poorly validated or has no rate limiting can let an attacker extract data or perform unauthorised actions directly.

### Try it: spot the misconfiguration

For each scenario, identify the risk and the best fix.

| Scenario | Risk? | Fix? |
|---|---|---|
| A storage bucket is set to public | ? | ? |
| An administrator account has no multi-factor authentication | ? | ? |
| An API accepts requests with no authentication | ? | ? |

```answer
1. Anyone can view or download its contents. Fix: make it private and grant specific access only.
2. A stolen password gives full control. Fix: enforce MFA.
3. Unauthorised data access. Fix: require authentication and add rate limiting.
```

## 3.4 Data Security

Data security protects information in all its forms, from creation to disposal, wherever it is stored, processed or transmitted. Stealing data is usually the real aim of an attack, so these controls still matter even when network or cloud defences fail.

### Encryption

Encryption converts data into an unreadable form that can only be turned back with a key.

- **Encryption in transit** protects data moving across a network, for example from a browser to a server.
- **Encryption at rest** protects stored data on disks, in databases and in backups.

If an attacker obtains encrypted data, it stays unreadable without the key, so keys must be protected and rotated.

### Access control

Access control determines who can see, modify or delete data. **Role-Based Access Control (RBAC)** grants access based on role, and the **principle of least privilege** limits access to what each person needs. Multi-factor authentication and audit logs add protection and make misuse easier to detect.

### Data classification

Data classification labels information by how sensitive or critical it is, from public to internal, confidential and restricted. It lets organisations apply protection in proportion, because not all data needs the same level of protection.

### Data loss prevention (DLP)

DLP is a set of tools and practices that detect and stop sensitive information leaving the organisation, for example blocking a sensitive file from being emailed out or copied to a USB drive.

### Secure disposal and privacy

Deleting a file does not always remove it, and retired devices should be securely erased or destroyed. In Australia, the **Privacy Act 1988** governs how organisations handle personal information and is enforced by the OAIC. Under the **Notifiable Data Breaches scheme**, covered organisations must notify affected individuals and the OAIC when a breach is likely to cause serious harm.

### Backup and recovery

Regularly tested backups protect data integrity and availability against ransomware, hardware failure or data loss. Keeping a copy offline, or disconnected from the main network, makes it much less likely that the same attack destroys the backup too.

### Try it: one-word answers

1. The practice of converting data into ciphertext so it is unreadable without the corresponding key is known as ________.
2. The security principle that restricts users and systems to the minimum permissions needed for their function is known as ________.
3. The process of categorising information by sensitivity, so that protective controls can be applied proportionately, is known as ________.

```answer
1. Encryption
2. Least privilege
3. Data classification
```

## 3.5 How the Domains Work Together

Network controls decide who can reach a resource. Once in the cloud, what they can do is governed by cloud identity and configuration controls. If both fail, data controls, especially encryption, still protect the information itself.

Network, cloud and data security are not separate silos. Each manages a different layer of the same environment, and each is meant to compensate when another fails:

- **Network security** controls access to resources. Firewalls, segmentation and access control reduce exposure and contain attackers who get in.
- **Cloud security** controls what an authenticated party can do once connected: IAM, secure configuration and monitoring of cloud resources.
- **Data security** protects the data itself. Encryption, access control and classification keep data hard to read or misuse even if the network and cloud layers are bypassed.

This is **defence in depth**. Because the controls are independent, an attacker has to defeat several in turn, not just one. For example, a misconfigured storage bucket is far less harmful if access is restricted to certain users and its contents are encrypted.

The three domains also map back to the CIA triad from Module 1:

- Network controls keep the network available and keep data confidential as it moves.
- Cloud controls reduce the chance of unauthorised access and misconfiguration across hosted services.
- Data controls keep data confidential and intact, and backups keep it available after an incident.

Coordination is the key to effective security, not any single control. A compromise in one domain can affect the others, and strength across all three greatly reduces both the likelihood and the impact of a successful attack.

# Knowledge check

### A stolen mobile phone contains customer data, but the drive was fully encrypted. Which CIA principle was primarily protected?
- [ ] Availability
- [ ] Integrity
- [x] Confidentiality
- [ ] Accountability
Explanation: Encryption keeps the data unreadable to the thief, protecting confidentiality.

### Why do organisations classify data by sensitivity?
- [ ] To ensure all data receives identical protection
- [x] To apply controls proportionate to the risk each type of data presents
- [ ] To reduce the amount of data stored
- [ ] To remove the need for access control
Explanation: Classification lets protection match the sensitivity of each type of data.

### Under Australia's Notifiable Data Breaches scheme, when must a covered organisation notify affected individuals and the OAIC?
- [ ] After any data loss, regardless of impact
- [x] When an eligible data breach is likely to cause serious harm
- [ ] Only when a ransom is demanded
- [ ] Only when the breach involves a cloud provider
Explanation: Notification is required for eligible breaches likely to result in serious harm.

### Remote employees regularly connect from public Wi-Fi. Which control best protects their traffic from interception?
- [ ] An intrusion detection system
- [x] A virtual private network (VPN)
- [ ] Network access control
- [ ] Data loss prevention
Explanation: A VPN encrypts traffic over untrusted networks, preventing interception.

### Customer records were exposed from a cloud storage bucket that a developer left publicly accessible. Under the shared responsibility model, who is primarily accountable?
- [ ] The cloud provider, for hosting the bucket
- [x] The customer, for configuring access
- [ ] The internet service provider
- [ ] No party, as the exposure was accidental
Explanation: Configuring access to resources is the customer's responsibility in the cloud.

### Which practice best protects backups from ransomware?
- [ ] Storing them on the same network share as the originals
- [x] Keeping an offline or isolated copy and testing restores regularly
- [ ] Encrypting only the original data
- [ ] Backing up only once a year
Explanation: An isolated copy can't be reached by the same attack, and testing proves it can be restored.

### An unmanaged personal laptop is plugged into a meeting room port and gains access to the corporate network. Which control would most directly have prevented this?
- [ ] Data classification
- [x] Network access control
- [ ] Encryption at rest
- [ ] A longer password policy
Explanation: NAC checks devices before letting them onto the network.

### Customer data is transmitted between a web browser and a server over an unencrypted connection and intercepted on a public network. Which control would have protected this data?
- [x] Encryption in transit
- [ ] Data classification
- [ ] Offline backups
- [ ] Secure disposal
Explanation: Encryption in transit (such as HTTPS/TLS) protects data as it travels across the network.
