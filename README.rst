HitchTest
=========

HitchTest is a part of the hitch testing framework which compiles and runs
YAML (and optionally jinja2) tests like this::

  - engine: engine.DjangoReminderTestExecutionEngine
    description: Sign up, create reminder and wait for email reminder to arrive.
    scenario:
      - Load website
      - Click: Register
      - Fill form:
          Username: django
          Email: django@reinhardt.com
          Password1: jazzguitar
          Password2: jazzguitar
      - Click: Create
      - Create reminder:
          Description: Remind me about upcoming gig.
          Days from now: 30
      - Wait for email:
          Containing: Confirm E-mail Address
      - Confirm emails sent: 1
      - Time travel:
          Days: 30
      - Wait for email:
          Containing: Remind me about upcoming gig.


Why YAML + Jinja2?
==================

To more easily maintain separation of concerns, individual test scripts
should be declarative. This can be enforced by ensuring that they are
written in a purely declarative language - hence YAML.

This also makes reading, writing, adding metadata to and and parsing
test cases much easier.

Combining YAML with jinja2 gives you the power to deduplicate
test case code while still maintaining comprehensibility and simplicity.
