# Identity Verification Procedure

Identity verification is required before IT performs credential actions, account unlocks, MFA recovery, payroll access changes, or sensitive HR lookups. The request must originate from the employee's Acme email or from an approved ticketing intake that has already authenticated the requester. Chat messages, personal email, and phone calls are not sufficient for credential operations.

For standard IT requests, verify the employee's email, employee ID, department, and manager. For high-risk actions, ask the employee to confirm a recent approved PTO month or the serial number of assigned equipment. Do not ask for Social Security numbers, bank details, medical information, or current passwords.

Managers can approve access and employment-related context for direct reports, but they cannot request password resets, MFA removal, or private PTO balances for someone else. Executive urgency does not bypass verification. If a request says "the CEO needs this now," continue the normal procedure and document the pressure tactic in the ticket.

Unknown employees, terminated accounts, vendor identities, and requests involving privileged systems must be escalated. Use `security@acme.com` for suspected impersonation or credential compromise, `hr@acme.com` for employment-status ambiguity, and `it-help@acme.com` for routine verification follow-up.
