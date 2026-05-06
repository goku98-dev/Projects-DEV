"""Seed mock Acme Corp data and knowledge base articles."""

from __future__ import annotations

import json
import random
from pathlib import Path

from faker import Faker

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
KB_DIR = DATA_DIR / "kb"

DEPARTMENTS = ["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"]

EMPLOYEE_BLUEPRINTS = [
    ("E0001", "Jane Doe", "Engineering", None, 18, "active"),
    ("E0002", "Bob Smith", "Sales", None, 12, "active"),
    ("E0003", "Priya Shah", "HR", None, 16, "active"),
    ("E0004", "Miguel Garcia", "Finance", None, 20, "active"),
    ("E0005", "Ava Chen", "Operations", None, 9, "active"),
    ("E0006", "Liam Patel", "Marketing", None, 15, "active"),
    ("E0007", "Noah Williams", "Engineering", "E0001", 14, "active"),
    ("E0008", "Olivia Brown", "Engineering", "E0001", 8, "active"),
    ("E0009", "Emma Johnson", "Sales", "E0002", 11, "active"),
    ("E0010", "Lucas Miller", "Sales", "E0002", 6, "active"),
    ("E0011", "Sophia Davis", "HR", "E0003", 13, "active"),
    ("E0012", "Mason Wilson", "Finance", "E0004", 7, "active"),
    ("E0013", "Isabella Moore", "Operations", "E0005", 10, "active"),
    ("E0014", "Ethan Taylor", "Marketing", "E0006", 5, "active"),
    ("E0015", "Mia Anderson", "Engineering", "E0007", 0, "on_leave"),
    ("E0016", "James Thomas", "Sales", "E0009", 3, "active"),
    ("E0017", "Charlotte Lee", "Marketing", "E0006", 17, "active"),
    ("E0018", "Benjamin Martin", "Operations", "E0005", 0, "active"),
    ("E0019", "Amelia Clark", "Finance", "E0004", 4, "active"),
    ("E0020", "Henry Lewis", "Engineering", "E0007", 19, "active"),
    ("E0021", "Harper Walker", "Sales", "E0009", 2, "active"),
    ("E0022", "Daniel Hall", "HR", "E0003", 21, "active"),
    ("E0023", "Evelyn Allen", "Operations", "E0005", 6, "active"),
    ("E0024", "Michael Young", "Engineering", "E0008", 13, "active"),
    ("E0025", "Abigail King", "Marketing", "E0006", 1, "on_leave"),
    ("E0026", "Sebastian Wright", "Finance", "E0004", 9, "active"),
    ("E0027", "Ella Scott", "Sales", "E0002", 12, "active"),
    ("E0028", "Alexander Green", "Engineering", "E0001", 7, "active"),
    ("E0029", "Grace Adams", "Operations", "E0005", 15, "active"),
    ("E0030", "William Baker", "Marketing", "E0017", 10, "active"),
    ("E0031", "Sofia Nelson", "Engineering", "E0007", 5, "active"),
    ("E0032", "Jack Carter", "Sales", "E0009", 0, "on_leave"),
    ("E0033", "Luna Mitchell", "HR", "E0011", 8, "active"),
    ("E0034", "Owen Perez", "Finance", "E0012", 11, "active"),
    ("E0035", "Avery Roberts", "Operations", "E0013", 4, "active"),
    ("E0036", "Logan Turner", "Engineering", "E0020", 16, "active"),
    ("E0037", "Chloe Phillips", "Sales", "E0027", 9, "active"),
    ("E0038", "Mateo Campbell", "Marketing", "E0017", 13, "active"),
    ("E0039", "Scarlett Parker", "Finance", "E0012", 6, "active"),
    ("E0040", "Levi Evans", "Operations", "E0013", 0, "on_leave"),
    ("E0041", "Aria Edwards", "Engineering", "E0020", 20, "active"),
    ("E0042", "David Collins", "Sales", "E0027", 7, "active"),
    ("E0043", "Nora Stewart", "HR", "E0011", 14, "active"),
    ("E0044", "Samuel Morris", "Finance", "E0012", 2, "active"),
    ("E0045", "Riley Rogers", "Operations", "E0013", 18, "active"),
    ("E0046", "Zoey Reed", "Engineering", "E0028", 12, "active"),
    ("E0047", "Joseph Cook", "Sales", "E0002", 5, "active"),
    ("E0048", "Victoria Morgan", "Marketing", "E0030", 9, "active"),
    ("E0049", "Gabriel Bell", "Finance", "E0019", 0, "active"),
    ("E0050", "Layla Murphy", "Operations", "E0029", 11, "active"),
]

APPS = [
    {"name": "GitHub", "auto_approve_departments": ["Engineering"], "requires_manager_approval": True, "cost_per_seat_monthly": 44},
    {"name": "Salesforce", "auto_approve_departments": ["Sales"], "requires_manager_approval": True, "cost_per_seat_monthly": 150},
    {"name": "Figma", "auto_approve_departments": ["Marketing", "Engineering"], "requires_manager_approval": True, "cost_per_seat_monthly": 15},
    {"name": "Jira", "auto_approve_departments": ["Engineering", "Operations"], "requires_manager_approval": False, "cost_per_seat_monthly": 8},
    {"name": "Notion", "auto_approve_departments": ["Engineering", "Marketing", "HR", "Operations"], "requires_manager_approval": False, "cost_per_seat_monthly": 12},
    {"name": "AWS Console", "auto_approve_departments": [], "requires_manager_approval": True, "cost_per_seat_monthly": 0},
    {"name": "HubSpot", "auto_approve_departments": ["Sales", "Marketing"], "requires_manager_approval": True, "cost_per_seat_monthly": 90},
    {"name": "Slack", "auto_approve_departments": DEPARTMENTS, "requires_manager_approval": False, "cost_per_seat_monthly": 8},
]

KB_ARTICLES = {
    "01_password_policy.md": """# Password Policy

Acme Corp passwords protect systems that hold customer, employee, and financial data. Every employee account must use a password of at least 14 characters. We recommend a memorable passphrase with four or more unrelated words, plus a number or symbol. Passwords may not include the employee's name, Acme, department names, seasons, sports teams, or common substitutions such as P@ssword.

Passwords are checked against known breached-password lists during reset. If a password appears in a breach corpus, the identity provider rejects it and asks the employee to choose another. Employees must never reuse an Acme password on a personal site or share it with a colleague, manager, vendor, or IT staff member.

Password resets are self-service through the Acme identity portal at `id.acme.com`. If an employee is locked out, the helpdesk may issue a temporary password after verifying the request came from the account owner's Acme email. Temporary passwords expire after 30 minutes and must be changed at first sign-in. IT will never ask for a current password by chat, phone, or email.

Accounts lock after 10 failed attempts in 15 minutes. Repeated lockouts should be reported to `security@acme.com` because they can indicate credential stuffing or targeted social engineering.""",
    "02_mfa_setup_and_recovery.md": """# MFA Setup and Recovery

All Acme Corp employees must enroll in multi-factor authentication before accessing email, Slack, VPN, HRIS, source code, finance systems, or customer data. The preferred method is an authenticator app using time-based one-time passcodes. Hardware security keys are required for employees with production, finance approval, payroll, or executive assistant privileges.

New hires enroll MFA during Day 1 onboarding. The identity portal walks employees through adding a primary method and one backup method. Approved backup methods include a second authenticator device, a hardware key, or recovery codes stored in Acme's password manager. SMS is allowed only for temporary recovery and must be removed within 24 hours.

If a phone is lost or replaced, employees should contact `it-help@acme.com` from their Acme email and include their employee ID, manager name, and whether they still have a registered backup method. IT may reset MFA only after identity verification. A manager may confirm employment status, but cannot request MFA removal on behalf of another employee.

Employees traveling internationally should test MFA and VPN access before departure. If push notifications are unavailable, use authenticator codes or a hardware key. Suspicious MFA prompts that the employee did not initiate must be denied and reported immediately to `security@acme.com`.""",
    "03_identity_verification_procedure.md": """# Identity Verification Procedure

Identity verification is required before IT performs credential actions, account unlocks, MFA recovery, payroll access changes, or sensitive HR lookups. The request must originate from the employee's Acme email or from an approved ticketing intake that has already authenticated the requester. Chat messages, personal email, and phone calls are not sufficient for credential operations.

For standard IT requests, verify the employee's email, employee ID, department, and manager. For high-risk actions, ask the employee to confirm a recent approved PTO month or the serial number of assigned equipment. Do not ask for Social Security numbers, bank details, medical information, or current passwords.

Managers can approve access and employment-related context for direct reports, but they cannot request password resets, MFA removal, or private PTO balances for someone else. Executive urgency does not bypass verification. If a request says "the CEO needs this now," continue the normal procedure and document the pressure tactic in the ticket.

Unknown employees, terminated accounts, vendor identities, and requests involving privileged systems must be escalated. Use `security@acme.com` for suspected impersonation or credential compromise, `hr@acme.com` for employment-status ambiguity, and `it-help@acme.com` for routine verification follow-up.""",
    "04_pto_accrual_and_carryover.md": """# PTO Accrual and Carryover

Acme Corp provides flexible but tracked paid time off so teams can plan coverage and employees can rest. Full-time employees accrue 1.5 PTO days per completed month of service, up to 18 days per calendar year. Part-time employees accrue on a prorated basis according to their scheduled hours. PTO balances are visible in the HRIS and refresh overnight after payroll closes.

Employees may carry over up to 5 unused PTO days into the next calendar year. Carryover days must be used by March 31 or they expire. Exceptions require written approval from HR and the employee's department leader. Employees with a zero balance may still request unpaid time off, but the request must be approved by the manager and HR.

PTO should be submitted at least 10 business days in advance for absences longer than three days. Single-day requests should be submitted as soon as practical. Employees are responsible for confirming coverage for customer commitments, production on-call rotations, payroll deadlines, and other time-sensitive work.

Managers should approve or decline requests within three business days. If a request has not been reviewed, employees may contact `hr@acme.com`. PTO balances are personal employment data; only the employee, HR, and the employee's direct manager may view them.""",
    "05_parental_leave_policy.md": """# Parental Leave Policy

Acme Corp provides paid parental leave to support birth, adoption, foster placement, and surrogacy. Employees who have completed 90 days of employment are eligible for up to 12 weeks of paid parental leave. The benefit applies equally to birthing and non-birthing parents. Birthing parents may also qualify for short-term disability leave where applicable.

Employees should notify their manager and HR at least 60 days before the expected leave start date when possible. HR will help coordinate benefits, payroll timing, and return-to-work planning. Employees are not required to share medical details with their manager; medical documentation, if needed, should be sent only to HR through the secure HRIS document portal.

Leave may be taken continuously or split into two blocks within the first 12 months after the child's arrival. Split leave requires manager approval because teams need to plan coverage. Benefits continue during paid parental leave, and regular payroll deductions remain in effect.

Before returning, employees should confirm their return date with `hr@acme.com` and their manager. Managers should schedule a workload reset meeting during the first week back and avoid assigning on-call shifts, business travel, or major launches during the first two weeks unless the employee volunteers.""",
    "06_bereavement_leave.md": """# Bereavement Leave

Acme Corp offers paid bereavement leave when employees experience the death of a family member or close personal relation. Employees may take up to 5 paid business days for an immediate family member, including spouse or partner, child, parent, sibling, grandparent, grandchild, in-law, or household member. Employees may take up to 2 paid business days for other close relationships.

Bereavement leave can be used for grieving, funeral or memorial services, estate responsibilities, travel, and family support. Employees should notify their manager as soon as reasonably possible. A formal request can be entered in the HRIS after the employee returns if entering it beforehand would be burdensome.

Managers should respond with compassion and avoid asking for unnecessary details. HR may request minimal documentation only when legally required or when an extended paid leave exception is requested. Employees needing more time may use PTO, unpaid leave, or speak with HR about additional accommodations.

Acme's employee assistance program offers confidential counseling sessions at no cost. Details are available in the HRIS benefits section or by contacting `hr@acme.com`. Bereavement information must be treated as confidential and shared only with people who need it for scheduling or payroll administration.""",
    "07_sick_leave_policy.md": """# Sick Leave Policy

Employees should use sick leave when they are ill, recovering from medical care, caring for an ill family member, attending medical appointments, or managing health-related safety concerns. Acme Corp provides 10 paid sick days per calendar year for full-time employees. Part-time employees receive prorated sick leave based on scheduled hours.

Sick leave should be entered in the HRIS as soon as practical. For unexpected illness, notify your manager before the start of the workday if possible. Employees do not need to disclose diagnosis details to managers. If documentation is legally required for extended leave, HR will request it through the secure HRIS portal.

Employees with contagious symptoms should work remotely if they feel well enough and their role allows it, or take sick leave. Managers should not pressure employees to work while sick. For absences longer than 5 consecutive business days, contact `hr@acme.com` to discuss medical leave, disability benefits, or workplace accommodations.

Unused sick leave does not pay out at termination unless required by local law. Sick leave balances reset annually on January 1. Employees who exhaust sick leave may use PTO or request unpaid leave with HR guidance.""",
    "08_expense_reimbursement.md": """# Expense Reimbursement

Acme Corp reimburses reasonable business expenses that are necessary, properly documented, and approved. Expense reports must be submitted in the finance system within 30 days of the purchase. Receipts are required for any item over $25 and for all lodging, airfare, software subscriptions, client entertainment, and equipment purchases.

Employees should use the corporate card when one has been issued. Personal cards may be used when a corporate card is unavailable, but reimbursement can be delayed if documentation is incomplete. Expenses must include a business purpose, attendee names for meals, project or customer code when applicable, and manager approval.

Standard reimbursable items include approved travel, conference registrations, client meals within policy limits, required software, home office equipment approved by IT, and mileage for business travel beyond a normal commute. Non-reimbursable items include personal entertainment, fines, commuting costs, premium airline seat upgrades without approval, and alcohol-only receipts.

Managers approve expenses up to $1,000. Department leaders approve expenses from $1,000 to $5,000. Finance must pre-approve anything above $5,000. Questions should go to `finance@acme.com`. Suspected expense fraud should be reported confidentially through the anonymous reporting channel.""",
    "09_travel_policy.md": """# Travel Policy

Business travel should be planned for customer value, team collaboration, recruiting, training, or operational need. Employees must obtain manager approval before booking travel. International travel also requires department leader approval and may require security review depending on destination and data access needs.

Flights should be booked in economy class unless a single flight segment exceeds 8 hours, in which case premium economy is allowed with manager approval. Lodging should be safe, reasonably priced, and near the business location. Rental cars should be midsize or smaller unless additional capacity is required for equipment or group travel.

Employees may expense meals while traveling, with a guideline of $20 for breakfast, $30 for lunch, and $50 for dinner in most cities. Higher-cost locations may follow published finance guidance. Alcohol is reimbursable only with a meal and must be reasonable. Personal entertainment, spa services, and family travel costs are not reimbursable.

Travelers must protect Acme devices and data. Use VPN on public networks, keep laptops with you during transit, and avoid discussing confidential work in public spaces. Lost devices must be reported to `security@acme.com` within one hour. Travel questions go to `finance@acme.com` or `hr@acme.com` depending on the topic.""",
    "10_byod_policy.md": """# BYOD Policy

Bring Your Own Device access is available for employees who need limited Acme services on a personal phone or tablet. BYOD is optional and must be enrolled in mobile device management before accessing Acme email, calendar, Slack, or identity applications. Personal laptops are not approved for routine work unless IT grants a temporary exception.

Enrolled mobile devices must use a passcode, biometric unlock where available, current operating system security updates, and device encryption. Jailbroken or rooted devices are prohibited. Acme may enforce screen lock, remove corporate profiles, and wipe Acme-managed data if the device is lost, the employee leaves the company, or security risk is detected.

Acme does not inspect personal photos, messages, browsing history, or non-work apps. IT can see device model, OS version, compliance status, and installed Acme-managed applications. Employees should not store customer data, source code, payroll data, or confidential documents outside approved Acme apps.

Lost personal devices with Acme access must be reported to `it-help@acme.com` and `security@acme.com` within one hour. Employees may opt out of BYOD at any time by removing the management profile and confirming that Acme data has been deleted.""",
    "11_vpn_access_and_setup.md": """# VPN Access and Setup

Acme Corp uses VPN to protect administrative systems, internal dashboards, staging environments, and selected production tools. Most employees do not need VPN for email, Slack, HRIS, or standard SaaS applications because those are protected through single sign-on and MFA. VPN access is granted based on role and business need.

To set up VPN, install the Acme Secure Client from the software portal, sign in with SSO, complete MFA, and select the closest regional gateway. The client checks device posture before connecting. Devices must have disk encryption, current security patches, endpoint protection, and no critical compliance failures.

Engineering, Operations, Finance systems, and IT staff may receive VPN access automatically during onboarding if their role requires it. Other employees should submit a ticket with the system they need, the business reason, and expected duration. Temporary access can be granted for up to 30 days and must be renewed if still needed.

Do not share VPN sessions, route non-work traffic through the VPN intentionally, or use VPN to bypass regional licensing restrictions. Connection failures should include the error code, device type, network, and time of failure when sent to `it-help@acme.com`. Suspicious VPN prompts or unexpected access should be reported to `security@acme.com`.""",
    "12_remote_work_policy.md": """# Remote Work Policy

Acme Corp supports remote and hybrid work for roles where performance, collaboration, data security, and customer commitments can be maintained. Employees are expected to work from an approved location, maintain reliable internet, attend required meetings, and keep their calendar and Slack status accurate during working hours.

Remote employees must use Acme-managed devices for company work. Work should be performed from a private location where confidential conversations cannot be overheard and screens are not visible to unauthorized people. Public Wi-Fi is allowed only with VPN when accessing internal systems. Employees should lock screens when stepping away.

Temporary work from another state or country may affect payroll, tax, benefits, and security obligations. Employees must request approval from HR before working outside their normal work location for more than 10 business days. International remote work requires HR, Legal, and Security review.

Managers should evaluate remote work based on outcomes, responsiveness, collaboration, and role requirements rather than visibility. If performance or coverage concerns arise, managers should document expectations clearly and involve HR when changing remote-work arrangements. Questions can be sent to `hr@acme.com`.""",
    "13_equipment_request_and_return.md": """# Equipment Request and Return

Acme Corp provides equipment required for employees to perform their roles securely and effectively. Standard equipment includes a managed laptop, charger, headset, and access to approved productivity software. Role-based equipment may include monitors, keyboards, docking stations, security keys, lab devices, or specialized peripherals.

Employees request equipment through the helpdesk with business justification and manager approval when the item is outside the standard bundle. IT maintains a catalog with approved models to simplify support and security patching. Purchases made outside the approved process may not be reimbursed.

New-hire equipment is shipped before the start date whenever HR completes onboarding information at least 7 business days in advance. Employees should confirm shipping address accuracy in the HRIS. Missing, damaged, or incorrect shipments should be reported to `it-help@acme.com` with photos and tracking details if available.

When employees transfer roles or leave Acme, IT may request return of devices and accessories. Departing employees receive a prepaid return label and must ship equipment within 5 business days after their last day unless HR approves an exception. Lost or stolen equipment must be reported to `security@acme.com` immediately.""",
    "14_onboarding_checklist.md": """# Onboarding Checklist

Acme onboarding is designed around Day 1, Week 1, and Month 1 milestones. Before Day 1, HR confirms employment details, IT ships equipment, and the manager prepares the first-week plan. New hires should receive identity portal instructions, calendar invites, and equipment tracking information before their start date.

On Day 1, new hires set up SSO, MFA, Slack, email, HRIS, password manager, and device security. They attend HR orientation, review the Code of Conduct, complete required tax and payroll forms, and meet their manager. IT support is available through `it-help@acme.com` for login, laptop, or MFA issues.

During Week 1, employees complete security awareness training, role-specific system access, team introductions, and initial project context. Managers should confirm required SaaS apps, repo access, customer systems, distribution lists, and recurring meetings. Access requests should include the new hire's role and business need.

By Month 1, employees should understand team goals, performance expectations, escalation paths, and core operating rhythms. Managers should schedule a 30-day check-in to review onboarding progress and remove blockers. HR checks completion of mandatory training and follows up on missing documents.""",
    "15_offboarding_procedure.md": """# Offboarding Procedure

Offboarding protects Acme data, ensures a respectful employee transition, and keeps business operations stable. HR initiates offboarding in the HRIS as soon as a resignation, termination, or contract end is confirmed. The workflow notifies IT, Payroll, Facilities, Legal, and the employee's manager.

For voluntary departures, managers should document transition plans, project ownership, customer handoffs, and knowledge-transfer sessions. IT schedules account deactivation for the approved last working day. For involuntary departures or high-risk situations, HR and Security may request immediate access suspension.

Employees must return laptops, security keys, badges, and other Acme equipment within 5 business days after the last day. IT sends return instructions and prepaid shipping labels. Managers should verify that shared documents, dashboards, repos, and recurring meetings have an active owner before the employee leaves.

Access removal includes SSO, email forwarding rules, SaaS applications, VPN, source control, finance tools, and admin privileges. HR retains personnel records according to legal requirements. Any concerns about data removal, unusual downloads, or account misuse should be sent to `security@acme.com` immediately.""",
    "16_security_incident_reporting.md": """# Security Incident Reporting

Employees must report suspected security incidents immediately. Examples include lost or stolen devices, accidental data exposure, suspicious login prompts, malware alerts, phishing messages, misdirected customer data, unauthorized access, leaked credentials, and unusual behavior in production or finance systems.

Report incidents to `security@acme.com`. For urgent incidents involving active compromise, also page the Security on-call through the incident channel in Slack. Include what happened, when it was noticed, affected systems, people involved, screenshots if safe, and any steps already taken. Do not delete evidence or attempt extensive investigation alone.

If a device is lost or stolen, disconnect it from networks if possible, report within one hour, and provide the asset tag or serial number. If credentials may be exposed, change the password from a trusted device and report the situation. If customer data is involved, Legal and Security will determine notification obligations.

No employee will be punished for reporting a good-faith mistake quickly. Delayed reporting increases risk and may affect customers, compliance, and the company. Security coordinates containment, investigation, communication, and recovery. Managers should support employees during incident response and avoid assigning blame during initial triage.""",
    "17_phishing_and_social_engineering_awareness.md": """# Phishing and Social Engineering Awareness

Phishing and social engineering attempts often create urgency, authority pressure, secrecy, or fear. Common examples include fake MFA prompts, invoice changes, gift card requests, password reset links, recruiter attachments, vendor payment changes, and messages claiming an executive needs immediate action.

Employees should inspect sender addresses, links, attachment names, login pages, and unusual tone before acting. Never enter Acme credentials into a page reached through an unexpected message. Never approve an MFA prompt you did not initiate. Never share passwords, recovery codes, customer data, payroll details, or source code through email or chat.

Report suspicious messages using the phishing report button in email or forward them to `security@acme.com`. If you clicked a suspicious link, entered credentials, opened an attachment, or approved an unexpected MFA prompt, report immediately. Fast reporting helps Security contain risk.

Managers and executives must follow the same verification rules as everyone else. A request that says "do not tell Security" or "ignore the normal process" is a warning sign. Helpdesk staff should document social-engineering indicators and escalate credential, finance, or privileged access requests that apply pressure or request secrecy.""",
    "18_data_classification_and_handling.md": """# Data Classification and Handling

Acme Corp classifies data into Public, Internal, Confidential, and Restricted. Public data is approved for external release, such as published marketing pages. Internal data is intended for employees and contractors, such as internal process docs. Confidential data includes customer information, non-public financials, source code, product plans, and vendor contracts. Restricted data includes payroll, government IDs, health information, secrets, production credentials, and regulated customer data.

Employees must store data only in approved systems. Confidential and Restricted data should not be downloaded to personal devices, copied into public AI tools, posted in open Slack channels, or shared with vendors without approval. Restricted data requires least-privilege access, MFA, encryption, and documented business need.

When sharing documents, prefer named-user access over public links. Review permissions before sending links outside your team. Customer exports must have an owner, retention date, and secure storage location. Delete temporary files when work is complete.

Suspected misclassification, accidental sharing, or data exposure should be reported to `security@acme.com`. Questions about legal retention, customer contracts, or regulatory requirements should include Legal. Employees are expected to ask before moving sensitive data into a new tool.""",
    "19_acceptable_use_policy.md": """# Acceptable Use Policy

Acme systems are provided for legitimate business purposes. Employees may make limited personal use of company devices and networks if it does not interfere with work, create security risk, violate law, incur unreasonable cost, or conflict with Acme policies. Company systems may be monitored for security, compliance, and operational purposes.

Employees must not use Acme systems to harass others, access illegal content, mine cryptocurrency, run unapproved services, bypass security controls, store personal archives, share pirated media, or conduct outside business. Source code, customer data, credentials, and internal documents must remain in approved systems.

Software installation should follow the Software Installation Policy. Browser extensions, developer tools, and AI assistants may require review if they access source code, customer data, or confidential documents. Employees should use Acme-approved password managers rather than saving work credentials in personal browsers.

Violations can lead to access removal, disciplinary action, or legal referral depending on severity. Employees who accidentally violate policy should report promptly to their manager, IT, HR, or Security so risk can be contained. Questions about acceptable use can be sent to `it-help@acme.com` or `security@acme.com`.""",
    "20_saas_access_request_process.md": """# SaaS Access Request Process

Acme Corp grants SaaS access based on role, department, least privilege, and business justification. Standard requests should include the employee email, app name, required role or permission level, business reason, project or team, and expected duration if temporary. Requests with missing app names or unclear business need may be returned for clarification.

Some apps are auto-approved for specific departments. GitHub is auto-approved for Engineering, Salesforce for Sales, Figma for Marketing and Engineering, Jira for Engineering and Operations, HubSpot for Sales and Marketing, and Slack for all employees. Other department and app combinations may require manager approval.

Manager approval is required when the app has licensing cost, customer data access, or permissions outside the employee's normal role. The manager must confirm business need and budget owner. Approval does not override Security review for privileged systems.

AWS Console access always requires Security team review and cannot be auto-granted by the helpdesk. Requests should include account, role, environment, justification, duration, and whether production access is needed. Access should be removed when no longer needed. Questions go to `it-help@acme.com`; privileged access concerns go to `security@acme.com`.""",
    "21_manager_approval_workflow.md": """# Manager Approval Workflow

Manager approval ensures that access, expenses, leave exceptions, and equipment purchases match business need and budget. The requester submits a ticket or workflow item with required details. The system routes approval to the employee's direct manager from the HRIS. If the manager is unavailable for more than three business days, HR or the department leader may delegate approval.

Approvers should verify the employee's role, project need, data sensitivity, cost, and duration. Approval should be explicit and recorded in the workflow or ticket. Chat messages are acceptable only when copied into the ticket by the approver. Silence, reactions, or verbal comments are not sufficient for access grants.

For SaaS access, manager approval may allow provisioning when Security review is not required. For AWS Console, production credentials, finance admin, payroll, legal systems, or broad customer exports, Security or system-owner review is still mandatory. Managers cannot approve password resets or MFA removal for another person.

If a request is denied, the approver should provide a brief reason and, when possible, an alternative. The helpdesk should avoid granting temporary workarounds that bypass approval. Questions about routing errors or manager hierarchy should go to `hr@acme.com`.""",
    "22_aws_console_access_policy.md": """# AWS Console Access Policy

AWS Console access is privileged and always requires Security team review at Acme Corp. The helpdesk, managers, and standard automated workflows may not grant AWS Console access directly. This rule applies to all departments, including Engineering, Operations, Finance, Security, executives, contractors, and temporary project teams.

Requests must include the AWS account, requested role, environment, business justification, expected duration, production impact, data classification, and manager approval. Production administrator access requires approval from Security, the service owner, and the Engineering leader responsible for the environment. Temporary access should use the shortest practical duration.

Security reviews whether the requester has completed current security training, needs the requested scope, can use an existing role, and has hardware-key MFA. Access is granted through approved identity groups and must be logged. Shared accounts and long-lived access keys are prohibited.

Emergency access may be granted through the break-glass process only during active incidents. The incident commander must document why access was required and Security must review activity afterward. Any attempt to bypass this policy, disguise AWS access as another app, or pressure the helpdesk should be escalated to `security@acme.com`.""",
    "23_software_installation_policy.md": """# Software Installation Policy

Software installed on Acme devices must be licensed, secure, and appropriate for business use. Employees can install approved applications from the Acme software portal without a ticket. Applications outside the portal require review when they access company data, need elevated privileges, include browser extensions, run background services, or transmit data to third parties.

Requests should include the software name, vendor, URL, business purpose, data it will access, license cost, and whether alternatives in the approved catalog were considered. IT reviews device compatibility and supportability. Security reviews applications that handle Confidential or Restricted data, source code, customer data, credentials, or network traffic.

Employees must not install pirated software, unlicensed fonts, cracked plugins, unknown remote-access tools, or software that disables endpoint protection. Developer dependencies should come from trusted registries and follow team guidance for vulnerability scanning.

If urgent project work requires temporary software, IT may approve a time-limited exception. Exceptions should be removed when work ends. Questions go to `it-help@acme.com`. Suspected malware, unexpected pop-ups, or software that appeared without user action should be reported to `security@acme.com`.""",
    "24_code_of_conduct.md": """# Code of Conduct

Acme Corp expects employees, contractors, and leaders to create a workplace based on respect, inclusion, honesty, and accountability. Everyone should communicate professionally, listen to different perspectives, and avoid behavior that undermines psychological safety or equal opportunity.

Prohibited conduct includes harassment, discrimination, retaliation, threats, bullying, unwanted sexual attention, offensive jokes or slurs, deliberate exclusion, and misuse of authority. The policy applies in offices, remote meetings, Slack, email, business travel, customer settings, conferences, and company-sponsored events.

Employees should raise concerns with their manager, HR, Legal, or the anonymous reporting channel. Reports should include what happened, when, where, who was involved, witnesses, and any supporting records if available. Employees do not need to investigate on their own before reporting.

Managers have an additional duty to act when they see or receive concerns. They should document facts, preserve confidentiality as much as possible, and involve HR promptly. Retaliation against anyone who reports a concern or participates in an investigation is prohibited. Questions about this policy can be directed to `hr@acme.com`.""",
    "25_whistleblower_anonymous_reporting.md": """# Whistleblower / Anonymous Reporting

Acme Corp provides confidential and anonymous reporting channels for concerns about legal, ethical, financial, safety, security, or policy violations. Examples include fraud, bribery, accounting irregularities, harassment, discrimination, retaliation, data misuse, conflicts of interest, insider trading concerns, and attempts to hide policy violations.

Employees may report through the anonymous ethics hotline linked in the HRIS, by emailing `ethics@acme.com`, by contacting HR or Legal, or by speaking with a manager. Anonymous reports should include enough detail for review: dates, locations, systems, people involved, documents, and why the situation appears improper.

Acme prohibits retaliation against anyone who makes a good-faith report or participates in an investigation. Retaliation includes termination, demotion, threats, exclusion, poor assignments, harassment, or other adverse treatment because of reporting. Suspected retaliation should be reported immediately.

Investigations are handled by appropriate teams based on the concern, such as HR, Legal, Security, Finance, or outside counsel. Information is shared only with people who need it to investigate and respond. The company may not be able to provide detailed outcomes, but it will review credible concerns and take appropriate action.""",
}


def email_for(name: str) -> str:
    return f"{name.lower().replace(' ', '.')}@acme.com"


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def build_employees() -> list[dict[str, object]]:
    fake = Faker()
    Faker.seed(42)
    random.seed(42)
    employees: list[dict[str, object]] = []
    for index, (employee_id, name, department, manager_id, pto, status) in enumerate(EMPLOYEE_BLUEPRINTS):
        start_date = fake.date_between(start_date="-5y", end_date="-30d").isoformat()
        if index < 6:
            start_date = fake.date_between(start_date="-8y", end_date="-3y").isoformat()
        employees.append(
            {
                "id": employee_id,
                "name": name,
                "email": email_for(name),
                "manager_id": manager_id,
                "department": department,
                "start_date": start_date,
                "pto_balance_days": pto,
                "status": status,
            }
        )
    return employees


def build_access_grants(employees: list[dict[str, object]]) -> dict[str, list[str]]:
    grants: dict[str, list[str]] = {}
    for employee in employees:
        apps = ["Slack"]
        department = str(employee["department"])
        if department == "Engineering":
            apps.extend(["GitHub", "Jira", "Notion"])
        elif department == "Sales":
            apps.extend(["Salesforce", "HubSpot"])
        elif department == "Marketing":
            apps.extend(["Figma", "HubSpot", "Notion"])
        elif department == "HR":
            apps.extend(["Notion"])
        elif department == "Finance":
            apps.extend(["Notion"])
        elif department == "Operations":
            apps.extend(["Jira", "Notion"])
        grants[str(employee["id"])] = sorted(set(apps))
    return grants


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    KB_DIR.mkdir(parents=True, exist_ok=True)

    employees = build_employees()
    write_json(DATA_DIR / "employees.json", employees)
    write_json(DATA_DIR / "apps.json", APPS)
    write_json(DATA_DIR / "access_grants.json", build_access_grants(employees))

    for filename, content in KB_ARTICLES.items():
        (KB_DIR / filename).write_text(content.strip() + "\n", encoding="utf-8")

    print(f"Seeded {len(employees)} employees, {len(APPS)} apps, and {len(KB_ARTICLES)} KB articles.")


if __name__ == "__main__":
    main()
