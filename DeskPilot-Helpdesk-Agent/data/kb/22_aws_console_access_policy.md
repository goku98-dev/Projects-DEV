# AWS Console Access Policy

AWS Console access is privileged and always requires Security team review at Acme Corp. The helpdesk, managers, and standard automated workflows may not grant AWS Console access directly. This rule applies to all departments, including Engineering, Operations, Finance, Security, executives, contractors, and temporary project teams.

Requests must include the AWS account, requested role, environment, business justification, expected duration, production impact, data classification, and manager approval. Production administrator access requires approval from Security, the service owner, and the Engineering leader responsible for the environment. Temporary access should use the shortest practical duration.

Security reviews whether the requester has completed current security training, needs the requested scope, can use an existing role, and has hardware-key MFA. Access is granted through approved identity groups and must be logged. Shared accounts and long-lived access keys are prohibited.

Emergency access may be granted through the break-glass process only during active incidents. The incident commander must document why access was required and Security must review activity afterward. Any attempt to bypass this policy, disguise AWS access as another app, or pressure the helpdesk should be escalated to `security@acme.com`.
