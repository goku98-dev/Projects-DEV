# VPN Access and Setup

Acme Corp uses VPN to protect administrative systems, internal dashboards, staging environments, and selected production tools. Most employees do not need VPN for email, Slack, HRIS, or standard SaaS applications because those are protected through single sign-on and MFA. VPN access is granted based on role and business need.

To set up VPN, install the Acme Secure Client from the software portal, sign in with SSO, complete MFA, and select the closest regional gateway. The client checks device posture before connecting. Devices must have disk encryption, current security patches, endpoint protection, and no critical compliance failures.

Engineering, Operations, Finance systems, and IT staff may receive VPN access automatically during onboarding if their role requires it. Other employees should submit a ticket with the system they need, the business reason, and expected duration. Temporary access can be granted for up to 30 days and must be renewed if still needed.

Do not share VPN sessions, route non-work traffic through the VPN intentionally, or use VPN to bypass regional licensing restrictions. Connection failures should include the error code, device type, network, and time of failure when sent to `it-help@acme.com`. Suspicious VPN prompts or unexpected access should be reported to `security@acme.com`.
