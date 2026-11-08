---
title: Prevention Strategies, Best Practices and Zero Trust
slug: prevention-best-practices-zero-trust
category: Defence
summary: Everyday prevention strategies and best practices, and how Zero Trust Architecture applies "never trust, always verify".
pass_mark: 80
estimated_minutes: 40
---

This module shows how organisations and individuals build cyber security prevention into everyday practice, and introduces Zero Trust Architecture (ZTA). It ties together the threats from Module 2, the defensive domains from Module 3 and the controls from Module 4.

## 5.1 Overview

This module introduces how organisations and individuals build cyber security prevention strategies into everyday practice, and how Zero Trust Architecture (ZTA) is applied. You will learn how organisations reduce their risk, protect critical assets, prevent unauthorised access and strengthen their security posture. It ties together the threats from Module 2, the defensive domains from Module 3 and the controls from Module 4.

### Learning outcomes

By the end of this module, you will be able to:

1. Understand the importance of cyber security prevention strategies.
2. Describe the cyber security best practices used by modern organisations.
3. Understand the importance of access control, multi-factor authentication and the principle of least privilege.
4. Recognise the role of patch management, encryption, network segmentation and data backups in preventing cyber attacks.
5. Define Zero Trust Architecture (ZTA) and explain its core principles.
6. Understand how Zero Trust can be implemented in organisational environments.
7. Apply prevention strategies and Zero Trust principles to real-world scenarios.

## 5.2 Cyber Security Prevention Strategies

Prevention strategies are the policies, technologies and practices organisations use to reduce the likelihood of a cyber attack, by fixing weaknesses before attackers can exploit them. They protect the organisation's systems, networks, applications and data.

<!-- REVIEW: "memorable questions" is listed as an MFA example. Security questions are another
"something you know", the same factor as a password, so they don't make sign-in multi-factor.
Consider replacing with "SMS or app-based code, or a hardware security key". -->

| Strategy | What it does | Example |
|---|---|---|
| **Access control** | Limits access to authorised users based on their roles | Payroll data is accessible only to relevant staff or HR |
| **Multi-factor authentication (MFA)** | Requires more than a password to sign in | App-based code, memorable questions or a security key |
| **Patch management** | Fixes known software vulnerabilities | Promptly applying OS updates |
| **Network segmentation** | Splits the network into segments so attacks cannot spread easily | Staff laptops separated from servers |
| **Endpoint protection** | Detects and blocks malicious activity on devices | Antivirus |
| **Encryption** | Makes data unreadable without the key | Encrypted laptop drives |
| **Security awareness training** | Teaches staff to recognise social engineering | Phishing simulations |
| **Regular backups** | Allows recovery after data loss or a ransomware attack | Offline, tested backups |

## 5.3 Cyber Security Best Practices

Best practices are habits and standards applied consistently to prevent the most common attacks. They need to be repeated continually, because threats and systems keep changing.

Five basic principles:

1. Risk management
2. Network security
3. Access control
4. Monitoring and detection
5. Incident response

Essential cyber security best practices:

- Use strong, unique passwords for different accounts
- Enable multi-factor authentication (MFA)
- Keep software updated and enable automatic updates
- Install antivirus, anti-spyware and anti-malware software on all devices
- Use firewalls
- Secure Wi-Fi networks with WPA3 encryption
- Assess third parties and cloud services before connecting to them
- Back up data regularly
- Beware of phishing attacks
- Educate and train employees

### Try it: good or bad practice?

| Behaviour | Good or bad? |
|---|---|
| Using the same password for work email and a shopping site | ? |
| Phoning a known number to confirm an unexpected payment request | ? |
| Plugging in a USB stick that was found in the park | ? |
| Keeping one backup offline and testing it | ? |

```answer
1. Bad: a breach of the shopping site exposes your work email (credential stuffing).
2. Good: verifying through a separate, known channel defeats impersonation.
3. Bad: this is baiting; the drive may carry malware.
4. Good: an isolated, tested backup survives ransomware.
```

### References

- [SentinelOne: Cyber security best practices](https://www.sentinelone.com/cybersecurity-101/cybersecurity/cyber-security-best-practices/)

## 5.4 Zero Trust Architecture (ZTA)

Zero Trust Architecture is a security framework that authenticates every access request and proactively anticipates attacks. It is built on the idea of **"never trust, always verify"**: no user, device or network is trusted automatically.

The traditional model defended the network edge and trusted everything inside it. That no longer works with cloud, remote and hybrid work, where staff reach organisational resources from many devices and locations.

## 5.5 Core Principles and Components

### Core principles

1. **Verify explicitly:** check every request using identity, device health, location, the resource requested and behaviour.
2. **Use least privilege access:** give only the access needed, for only as long as it is needed.
3. **Assume breach:** design as though an attacker may already be inside, so limit how far they can go and detect them quickly.

### Key components

1. **Identity and access management (IAM):** multi-factor authentication, single sign-on (SSO) and role-based access control help prevent identity-related breaches.
2. **Network segmentation:** the network is divided into small, isolated zones, limiting attackers' lateral movement.
3. **Endpoint security:** protects devices such as laptops, smartphones and tablets so threats like malware can't get into the network.
4. **Data security:** strong access controls, end-to-end encryption and data masking help prevent breaches and unauthorised access to sensitive information.
5. **Security Information and Event Management (SIEM):** provides real-time analysis of security alerts from business applications and network hardware.

### References

- [Microsoft: What is Zero Trust architecture?](https://www.microsoft.com/en-au/security/business/security-101/what-is-zero-trust-architecture)

## 5.6 Traditional Security Model vs ZTA

| | Traditional model | Zero Trust |
|---|---|---|
| **Trust** | Users and devices inside the network are trusted | No implicit, location-based trust |
| **Access decision** | Made once, at the network edge | Made for every request, continuously |
| **Permissions** | Often broad inside the network | Least privilege per resource |
| **Network** | Largely flat once inside | Segmented, down to individual workloads |
| **If an attacker gets in** | Can often move freely | Movement is limited and monitored |

Zero Trust doesn't replace firewalls, VPNs and antivirus. It strengthens them by adding identity checks, access restrictions and continuous monitoring. This is defence in depth.

## 5.7 Implementing Zero Trust

Steps and best practices for adopting Zero Trust:

1. Create strong identity verification
2. Manage access to devices and networks
3. Improve visibility into applications
4. Set data permissions
5. Monitor your infrastructure

Common challenges include legacy systems that lack modern authentication, cost, and user frustration when controls are too disruptive. Starting with the highest-risk assets and the strongest identity controls gives the quickest benefit.

### Try it: allow, challenge or block?

Decide how a Zero Trust policy should respond to each request.

| Scenario | Decision? |
|---|---|
| A staff member opens the roster app from a managed laptop at their usual location | ? |
| A finance officer signs in from a new country and requests a payroll export | ? |
| An unmanaged, out-of-date device requests access to an internal server | ? |

```answer
1. Allow: known user, managed device, usual location, low-risk app.
2. Challenge: unusual location plus a sensitive request; ask for extra verification such as MFA.
3. Block: the device fails the health check, so it gets no access until it is compliant.
```

### References

- [Microsoft: What is Zero Trust architecture?](https://www.microsoft.com/en-au/security/business/security-101/what-is-zero-trust-architecture)

# Knowledge check

### What is the main purpose of prevention strategies?
- [ ] To remove the need for detection and recovery
- [x] To reduce the likelihood of attacks succeeding
- [ ] To give all staff administrator access
- [ ] To replace existing IT systems
Explanation: Prevention fixes weaknesses before attackers exploit them; detection and recovery are still needed.

### What does MFA achieve?
- [ ] It encrypts all stored files
- [ ] It increases network speed
- [x] It makes a stolen password alone insufficient
- [ ] It removes the need for patching
Explanation: With MFA, an attacker also needs the second factor.

### A marketing employee can open payroll records they do not need. Which principle would have prevented this?
- [x] Least privilege
- [ ] Assume breach
- [ ] Segmentation
- [ ] Spoofing
Explanation: Least privilege gives people only the access their role requires.

### Which phrase best summarises Zero Trust?
- [ ] Trust devices inside the network
- [ ] Verify once at the perimeter
- [ ] Block all remote access
- [x] Never trust, always verify
Explanation: Every request is verified; nothing is trusted because of where it comes from.

### What does "assume breach" mean?
- [ ] Treat all staff as attackers
- [ ] Stop using cloud services
- [x] Design controls to limit damage as if an attacker is already inside
- [ ] Skip monitoring when MFA is enabled
Explanation: Assume breach means limiting how far an attacker can go and detecting them quickly.

### A device with an out-of-date operating system requests sensitive data. Under Zero Trust, the best response is to:
- [ ] Allow it because the user is an employee
- [x] Restrict or deny access until the device is compliant
- [ ] Disable MFA
- [ ] Grant temporary administrator rights
Explanation: Device health is part of every access decision.

### Does Zero Trust replace firewalls and other traditional controls?
- [x] No, it works alongside them as part of layered defence
- [ ] Yes, firewalls are obsolete
- [ ] Yes, it replaces encryption
- [ ] No, but it removes the need for access control
Explanation: Zero Trust adds identity checks and monitoring on top of existing controls (defence in depth).
