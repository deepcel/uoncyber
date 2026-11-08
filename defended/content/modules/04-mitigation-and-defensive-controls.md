---
title: Mitigation Strategies and Defensive Controls
slug: mitigation-strategies-defensive-controls
category: Defence
summary: Preventive, detective and corrective controls, incident response, resilience, the Essential Eight and matching mitigations to attacks.
pass_mark: 80
estimated_minutes: 40
---

This module shows how organisations stop attacks, limit their impact when they do happen, and recover afterwards. It applies the Protect, Detect, Respond and Recover functions of the NIST CSF from Module 1.

## 4.1 Introduction to Mitigation and Defensive Controls

In Modules 2 and 3 you learnt about attacks and the security domains that protect against them. This module teaches how organisations can stop attacks, limit their impact if they do occur, and get back on their feet afterwards. It applies the **Protect, Detect, Respond and Recover** functions of the NIST CSF from Module 1.

### Learning outcomes

At the end of this module, you should be able to:

- Differentiate between preventive, detective and corrective controls.
- Describe important controls for identity, endpoints and email.
- Describe the steps in incident response.
- Match the attacks from Module 2 with their mitigations.

## 4.2 Types of Security Controls

Controls can be classified by **when they act**:

- **Preventive:** blocks an attack before it succeeds, for example patching, MFA and firewalls.
- **Detective:** detects an attack while it is happening or afterwards, for example monitoring, logging and intrusion detection.
- **Corrective:** limits damage and restores operations, for example backups and incident response.

Controls can also be classified by **what they are**:

- **Administrative controls:** policies, procedures and training.
- **Technical controls:** software and hardware measures, such as encryption and access controls.
- **Physical controls:** measures such as locks, badges and CCTV.

## 4.3 Key Defensive Controls

- **Identity and access:** multi-factor authentication (MFA), account lockout, unique passwords stored in a password manager, and least privilege counter credential attacks.
- **Prompt updates, endpoint protection and application control:** defend against malware and application attacks.
- **Email and people:** email filtering, SPF/DKIM/DMARC, awareness training, and verifying unusual requests through another channel counter social engineering.
- **Monitoring:** logging and a SIEM (which collects and correlates logs and raises alerts) support early detection.
- **Resilience:** tested backups, available offline, that still work after an incident.

## 4.4 Incident Response

Incident response is the process of limiting the damage from a security incident and resolving it as quickly as possible. It relates to the Respond and Recover functions of the NIST CSF (Module 1) and is triggered by the detective controls in section 4.3.

1. **Preparation:** the organisation has a response plan ready before an incident occurs, with defined roles, contact lists, and logging and backup procedures.
2. **Detection and analysis:** an incident is detected through alerts or staff reports, then investigated to determine what happened, which systems were affected and how severe it is.
3. **Containment:** affected devices are isolated and compromised accounts are disabled to stop the incident spreading.
4. **Eradication:** the cause is removed, for example by deleting malware, closing the exploited vulnerability and resetting credentials.
5. **Recovery:** systems are restored from clean, tested backups and closely monitored for repeat activity.
6. **Lessons learned:** the team reviews the incident and how it was handled, then improves controls, training and the response plan.

Time is always critical: early detection and containment can dramatically reduce the impact of an incident.

## 4.5 Resilience and Recovery

Resilience measures make sure an organisation can keep operating, or recover quickly, after an incident.

- **Backups:** several copies, at least one offline or isolated, with restores tested regularly.
- **Business continuity planning:** keeps critical services running when disruption occurs.
- **Disaster recovery planning:** specifies which systems are recovered, and how quickly.

## 4.6 The Essential Eight

The **Essential Eight** is a set of baseline mitigation strategies published by the Australian Cyber Security Centre (ACSC) that make organisations much harder to compromise:

1. Application control
2. Patch applications
3. Configure Microsoft Office macro settings
4. User application hardening
5. Restrict administrative privileges
6. Patch operating systems
7. Multi-factor authentication
8. Regular backups

## 4.7 Matching Mitigations to Attacks

| Attack | Key mitigations |
|---|---|
| Phishing and social engineering | Awareness training, email filtering, verification procedures, MFA |
| Credential attacks | MFA, unique passwords, lockout and throttling, leaked-credential monitoring |
| Man-in-the-middle and packet sniffing | Encryption in transit, VPN, avoiding untrusted networks |
| DoS and DDoS | Traffic filtering, rate limiting, DDoS mitigation services |
| SQL injection and XSS | Input validation, parameterised queries, output encoding, patching |
| Malware and ransomware | Endpoint protection, patching, application control, offline backups |
| Cloud misconfiguration | Configuration reviews, least-privilege IAM, logging and monitoring |

# Knowledge check

### A firewall blocks a malicious connection before it reaches the internal network. Which type of control is this?
- [x] Preventive
- [ ] Detective
- [ ] Corrective
- [ ] Administrative
Explanation: It stops the attack before it succeeds, so it is a preventive control.

### An attacker uses a password stolen in a phishing email but cannot sign in because the account requires a second verification step. Which control stopped the attack?
- [ ] Network segmentation
- [x] Multi-factor authentication
- [ ] Email filtering
- [ ] Data classification
Explanation: MFA makes a stolen password alone insufficient to sign in.

### A security team receives an automated alert after the same account logs in from two countries within minutes. Which tool most likely raised it?
- [x] A SIEM
- [ ] A VPN
- [ ] A password manager
- [ ] An offline backup
Explanation: A SIEM correlates log events and raises alerts on suspicious patterns like "impossible travel".

### During a ransomware incident, staff disconnect the infected servers from the network before any cleanup begins. Which stage of incident response is this?
- [ ] Preparation
- [x] Containment
- [ ] Eradication
- [ ] Recovery
Explanation: Isolating affected systems to stop the spread is containment.

### After restoring systems from backups, a company finds that the attacker returned through the same unpatched server. Which earlier stage was most likely incomplete?
- [ ] Preparation
- [ ] Detection and analysis
- [x] Eradication
- [ ] Lessons learned
Explanation: Eradication should have closed the exploited vulnerability before recovery.

### An organisation holds regular backups, but none have ever been restored as a test. What is the main risk?
- [x] The backups may fail to restore when they are needed
- [ ] The backups will be encrypted twice
- [ ] The backups will slow down the network
- [ ] The backups will no longer count as a corrective control
Explanation: Untested backups may turn out to be incomplete or unusable when you need them.
