# Password Policy

Acme Corp passwords protect systems that hold customer, employee, and financial data. Every employee account must use a password of at least 14 characters. We recommend a memorable passphrase with four or more unrelated words, plus a number or symbol. Passwords may not include the employee's name, Acme, department names, seasons, sports teams, or common substitutions such as P@ssword.

Passwords are checked against known breached-password lists during reset. If a password appears in a breach corpus, the identity provider rejects it and asks the employee to choose another. Employees must never reuse an Acme password on a personal site or share it with a colleague, manager, vendor, or IT staff member.

Password resets are self-service through the Acme identity portal at `id.acme.com`. If an employee is locked out, the helpdesk may issue a temporary password after verifying the request came from the account owner's Acme email. Temporary passwords expire after 30 minutes and must be changed at first sign-in. IT will never ask for a current password by chat, phone, or email.

Accounts lock after 10 failed attempts in 15 minutes. Repeated lockouts should be reported to `security@acme.com` because they can indicate credential stuffing or targeted social engineering.
