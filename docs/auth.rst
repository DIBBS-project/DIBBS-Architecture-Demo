===================================
LambdaLink Implementation
===================================

This document describes the reference implementation of the architecture described in [1].

---------------------------
Assumptions
---------------------------

We assume that the services described in [1] are independent, i.e., don’t assume a shared context or a shared deployment platform.

---------------------------
Implementation Overview
---------------------------

LambdaLink is implemented in Python 2.7 and uses the Django 1.8 web framework. It can be deployed as standalone processes or as Docker containers.

Encryption and authentication of the services are provided via HTTPS.


Service Implementation
---------------------------
All services within the LambdaLink Implementation share the following common features.


Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
[How are user accounts created? What type of credentials do we use?]

User accounts are stored within the Central Authentication System (CAS) using the default Django user model. The minimal fields necessary are: a unique user ID, a unique username, and a strongly hashed password field.

[How does user authentication work? What is the workflow?]

To use other DIBBs services in an authenticated manner, the user must first authenticate with the CAS. The user exchanges their credentials (username/password) for a token, which is generated and associated with the user. Whoever possesses the token is assumed to be that user, so it must remain safe, so long as it is valid. All other services expect the token to be passed in an HTTP header. When a service processes a request that contains the HTTP header, it validates the token to authenticate the user.

Interservice requests are authenticated using signed tokens. The requesting service generates a token signifying it is another trusted service, and the user on behalf of whom it is acting.

[Why did you choose to do it this way?]

The pros of this implementation are that most of the communication is authenticated based on temporary user-specific credentials, reducing the impact of a leaked token. Additionally, requiring all requests (from the user and between services) to include authentication removes the need for a pre-authenticated system channel. Furthermore, validating passwords is by-design an expensive operation. The key derivation function used to store passwords is chosen to be costly in order to prevent cracking hashes. Further, the user can interact directly with internal services (as is needed if users want to work with the resource manager). Finally, this also can make it easier to track transactions within the system (although in principle even if they happen via a system channel the transaction itself should simply be tagged with information about the user). The cons are slightly increased network overhead because of authenticating every operation.

Interservice requests do not reuse the token because the token may expire or be revoked after initial processing, and the services should complete processing an initially valid user request to avoid an inconsistent state. The pros of cryptographically signed tokens are that they can be generated on-the-fly and do not need to be stored. Additionally, once the secret is distributed, no network communication is needed to validate the token. Cons are slightly increased processing overhead to generate and sign the token (two SHA256 operations).

Authorization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Resource objects managed by the system have 'owners', and are used to limit who can perform what actions on them. Generally, only the owner and admin can destroy/modify objects. Viewing objects may be expanded to other users where sensible (public operations).


---------------------------
Development priorities
---------------------------


Radical changes?
---------------------------

LambdaLink is currently implemented as several distributed services, each written as a separate Django app. Django doesn't excel with this kind of architecture: rather, it is a web framework designed for monolithic apps. Development may be easier with a framework designed for a distributed architecture.

Development is slowed down due to the lack of tests. While Django offers testing capabilities within each service implementation, the most important testing must be done for interactions between services. We will have to rely on tests based on mocking, which can diverge from reality. It is possible that other frameworks provide better capabilities for testing distributed applications.

Improvements
---------------------------

Admin interface for the resource manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Admin interface allowing to delete allocated OpenStack clusters (stacks)
