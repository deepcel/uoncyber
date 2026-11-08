---
title: Introduction to Cyber Security
slug: introduction-to-cyber-security
category: Fundamentals
summary: Core cyber security concepts, the CIA triad, threats and risk, governance frameworks and the shared responsibility model.
pass_mark: 80
estimated_minutes: 40
---

This module introduces cyber security and the security fundamentals. You will gain strong foundational knowledge of cyber security concepts, terminology, challenges, governance and principles in the digital environment. It prepares you for the modules that follow.

## 1.1 Overview

This module will introduce cyber security and the security fundamentals. You will gain strong foundational knowledge of cyber security concepts, terminologies, challenges, governance and principles in the digital environment. This module will prepare you for the upcoming modules.

### Learning outcomes

By the end of this module, you will be able to:

1. Define cyber security
2. Understand the difference between threat, vulnerability and risk
3. Gain understanding of the CIA triad
4. Understand security governance and compliance
5. Know the shared responsibility model
6. Recognise the use of cyber security in modern organisations

## 1.2 What Is Cyber Security

The practice of providing protection to the systems, networks, applications and data from digital attacks is known as **cyber security**.

Importance of cyber security:

- Rising dependency on the digital environment
- Increase of cyber crime
- The need to protect organisational trust and reputation

### References

- [Cisco: What is cybersecurity?](https://www.cisco.com/site/us/en/learn/topics/security/what-is-cybersecurity.html)

## 1.3 CIA Triad

CIA stands for **Confidentiality, Integrity and Availability**. The CIA triad is a model that forms the base for developing security for the systems in an organisation.

**Confidentiality:** the efforts an organisation takes to make sure that information is only accessible by authorised personnel.

> For example, employees who work in the finance department of an organisation should be able to access all the information related to transactions, spreadsheets, bank accounts and other flows of money. However, the same information should not be accessible by other employees, and even some executives should not be granted access to it.

**Integrity:** making sure that data and information are authentic, accurate and protected from tampering and alteration.

> For example, if a university's database contains all students' grades, they should be the true grades. If a student hacks into the database and modifies it, integrity has been lost.

**Availability:** ensuring that the information kept confidential and intact is available to the organisation's employees and customers when needed.

> For example, if an organisation has no disaster recovery system and a power outage occurs, regaining access to critical systems might not be possible. This means availability is compromised.

### Try it: match the scenario to the CIA principle

| Scenario | CIA principle? |
|---|---|
| A hospital admin accidentally uploads a list of patients' personal information, including their Medicare numbers, to publicly accessible cloud storage indexed by a search engine. | ? |
| During a system update, an attacker exploits a vulnerability in the organisation's network and modifies the prices of items. Customers are now overpaying, even though the system is still online and no data was deleted. | ? |
| A flood stops employees from travelling to their workplace, so they cannot access their workstations and other devices. | ? |

```answer
1. Confidentiality: private patient data was exposed to the public.
2. Integrity: the prices were altered without authorisation.
3. Availability: staff could not reach the systems they need.
```

### References

- [Fortinet: CIA triad](https://www.fortinet.com/resources/cyberglossary/cia-triad)

## 1.4 Threat vs Vulnerability vs Risk and Assets

**Asset:** anything of value in an organisation or business that requires protection.
For example: customer information and databases, cloud storage, networks, applications, and physical devices such as laptops and phones.

**Vulnerability:** a weakness in the organisation's infrastructure that could lead to exploitation.
For example: unpatched software, weak passwords.

**Threat:** a malicious event or actor that exploits a vulnerability and causes harm to an asset.
For example: insider threats (people), malware, natural disasters, attackers or cyber criminals.

**Risk:** the potential loss or damage to assets when a threat successfully exploits a vulnerability.

<!-- REVIEW: "Risk = Threat x Vulnerability" is a simplification. Risk is more commonly taught as
Likelihood x Impact (or Threat x Vulnerability x Asset value). Consider rewording before publishing. -->
Risk is often expressed as:

**Risk = Threat × Vulnerability**

### Real-world example

In an organisation, the customer database is an **asset**. Cyber criminals are a **threat** to the database. Unpatched software on the database server is a **vulnerability**. If the attacker exploits the vulnerability, customer data is compromised. The **risks** include financial losses, legal consequences and operational disruption.

### References

- [Splunk: Vulnerability vs threat vs risk](https://www.splunk.com/en_us/blog/learn/vulnerability-vs-threat-vs-risk.html)

## 1.5 Security Governance and Compliance

Cyber security governance is the framework of policies, compliance requirements, processes and controls. It ensures that the security and resilience of an organisation's information systems meet the standards of broader IT governance.

Governance makes sure that an organisation's cyber security is proactively planned, measured and continuously improved.

Common cyber security frameworks:

### ISO/IEC 27001: Information Security Management System (ISMS)

ISO/IEC 27001 is an information security management standard that helps organisations build a structured framework to safeguard their information assets. It also covers risk management and risk assessment, and supports continuous assessment and improvement.

### NIST Cybersecurity Framework (NIST CSF)

NIST CSF is a widely used framework that helps organisations manage their cyber security risks. Its six core functions are:

| Function | What it covers |
|---|---|
| **Govern** | The organisation's cyber security risk management strategy, expectations and policy are established, communicated and monitored. |
| **Identify** | The organisation's current cyber security risks are understood, including assets, suppliers and business context. |
| **Protect** | Safeguards are used to manage cyber security risks, such as access control, training and encryption. |
| **Detect** | Possible cyber security attacks and compromises are found and analysed. |
| **Respond** | Action is taken on a detected cyber security incident. |
| **Recover** | Assets and operations affected by an incident are restored. |

Govern sits at the centre and informs the other five functions.

### References

- [DataGuard: Cyber security governance](https://www.dataguard.com/cyber-security/governance/)
- [ISMS.online: ISO 27001](https://www.isms.online/iso-27001/)
- [NIST CSF 2.0 (NIST CSWP 29)](https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.29.pdf)

## 1.6 Shared Responsibility Models (On-Premises vs Cloud)

A shared responsibility model defines who is responsible for cyber security: the cloud service provider or the customer.

**On-premises responsibility model:** the traditional model in which the organisation is responsible for everything, including storage, networks, physical servers, applications, monitoring and software updates.

**Cloud responsibility model:** responsibility is shared between the cloud service provider and the customer.

- The **cloud service provider** is responsible for networking, physical data centres, hardware and similar infrastructure.
- The **customer** is responsible for data protection, encryption, logging and monitoring, and identity and access management (IAM).

Understanding these responsibilities is crucial: many cloud breaches happen because of customer misconfiguration, not a fault of the provider. Common misconfigurations include open security groups and exposed APIs.

### References

- [Microsoft: Shared responsibility in the cloud](https://learn.microsoft.com/en-us/azure/security/fundamentals/shared-responsibility)
- [Zscaler: What is the shared responsibility model?](https://www.zscaler.com/resources/security-terms-glossary/what-is-shared-responsibility-model)

## 1.7 Cyber Security in Modern Organisations

Modern organisations have a hybrid work environment: a mix of office and remote work, on-premises and cloud systems, SaaS applications and hybrid networks. This increases both the risks and the complexity of keeping the organisation secure.

Modern approaches are needed to prevent cyber attacks, such as:

- Zero Trust Architecture (ZTA)
- Automation and monitoring
- Security awareness and training
- Identity-centric security

## 1.8 Case Studies

The links below describe major cyber security incidents:

- [Queensland Government: Cyber security case studies](https://www.qld.gov.au/community/your-home-community/cyber-security/cyber-security-for-queenslanders/case-studies)
- [EIMT: Best-known cybersecurity case studies](https://www.eimt.edu.eu/top-best-known-cybersecurity-case-studies)

# Knowledge check

### What is the primary purpose of cyber security in an organisation?
- [ ] To increase the number of digital systems used
- [x] To protect systems, networks, applications, and data from digital attacks
- [ ] To allow employees unrestricted access to all organisational information
- [ ] To replace physical security controls
Explanation: Cyber security is the practice of protecting systems, networks, applications and data from digital attacks.

### Which of the following best describes a vulnerability?
- [ ] A malicious actor attempting to exploit a system
- [x] A weakness in a system that can be exploited
- [ ] The financial impact of a cyber attack
- [ ] Any valuable organisational asset
Explanation: A vulnerability is a weakness. The actor is the threat, the impact is the risk, and the valuable item is the asset.

### Which CIA principle is compromised when authorised users cannot access critical systems due to a power outage?
- [ ] Confidentiality
- [ ] Integrity
- [x] Availability
- [ ] Authenticity
Explanation: Availability means information and systems are accessible to authorised users when needed.

### Which NIST CSF function focuses on restoring systems and operations after a cybersecurity incident?
- [ ] Protect
- [ ] Detect
- [ ] Respond
- [x] Recover
Explanation: Recover restores the assets and operations affected by an incident.

### In the shared responsibility model, which of the following is the customer responsible for in cloud environments?
- [ ] Physical data centre security
- [ ] Hypervisor protection
- [x] Identity and Access Management (IAM)
- [ ] Hardware maintenance
Explanation: The provider secures the physical infrastructure; the customer manages identities and access.

### Which statement best describes cyber security in modern organisations?
- [ ] Organisations only use on-premises systems, reducing complexity
- [x] Hybrid environments increase complexity and require modern approaches like Zero Trust
- [ ] Remote work eliminates the need for cyber security controls
- [ ] Cloud systems remove all security responsibilities from the customer
Explanation: Hybrid work, cloud and SaaS increase complexity, so approaches such as Zero Trust are needed.

### ISO 27001 primarily helps organisations with:
- [ ] Building mobile applications
- [ ] Managing physical security guards
- [x] Establishing an Information Security Management System (ISMS)
- [ ] Creating marketing strategies
Explanation: ISO/IEC 27001 is the standard for an Information Security Management System.
