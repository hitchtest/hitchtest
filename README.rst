HitchTest
=========

HitchTest is a part of the hitch testing framework which compiles and runs
YAML (and optionally jinja2) tests like this::

    {% extends "base.yml" %}
    {% block test %}
    - engine: engine.py:DjangoReminderTestExecutionEngine
      name: Sign up, create reminder and wait for email reminder to arrive in python {{ python_version }}
      preconditions:
        python_version: "{{ python_version }}"
      scenario:
        - Load website
        - Click: register
        - Fill form:
            id_username: django
            id_email: django@reinhardt.com
            id_password1: jazzguitar
            id_password2: jazzguitar
        - Click submit
        - Click: create
        - Fill form:
            id_description: Remind me about upcoming gig.
            id_when: 30 days
        - Click: create
        - Wait for email:
            Containing: Confirm E-mail Address
        - Confirm emails sent: 1
        - Time travel:
            Days: 30
        - Wait for email:
            Containing: Remind me about upcoming gig.
    {% endblock %}


Features
========

* Integrates with IPython.
* Pretty stacktraces and test results.
* Quiet mode.
* Integrated and easily overriden test settings.


Why YAML + Jinja2?
==================

This is to more easily maintain separation of concerns. Enforcing the use
of YAML keeps the test scripts declarative, and all of the execution
code is kept centralized in the engine.

This also makes reading, writing, adding metadata to and and parsing
test cases much easier.

Combining YAML with jinja2 gives you the power to deduplicate
test case code while still maintaining comprehensibility and simplicity.
