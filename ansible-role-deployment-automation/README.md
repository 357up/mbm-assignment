Zabbix Deployment Automation Role
=================================

Overview
--------

This role builds a local proof-of-concept environment that demonstrates a
containerized Zabbix stack fronted by MetalLB and backed by synthetic SNMPv3
endpoints. It stands up two kind clusters (``mgmt`` for Zabbix, ``infra`` for
the simulated devices), deploys supporting Helm charts, configures a reverse
proxy for the web UI, and registers a proxy plus SNMP hosts through the Zabbix
API.

What ships today
----------------

- Bootstraps kind-based ``infra`` and ``mgmt`` clusters with MetalLB configured.
- Builds a demo ``snmpd`` image locally and loads it into the infra cluster.
- Deploys Zabbix server, web, and proxy charts with optional embedded Postgres.
- Brings up a Podman-hosted NGINX reverse proxy bound to ``127.0.0.1``.
- Manages Zabbix API credentials, proxy registration, and SNMP host discovery.

Known gaps and production notes
-------------------------------

- Environment lifecycle is crammed into a single role. In production the
  responsibilities must be split at least into three dedicated roles (cluster
  bootstrap, Zabbix deployment, synthetic workload). That separation isolates
  permissions per team, keeps lifecycles and upgrade cadences independent,
  allows cluster provisioning to remain reusable Terraform/Ansible plumbing,
  and limits blast-radius when only the monitoring payload needs redeploying.
- The SNMP simulator currently runs as a Kubernetes StatefulSet. In a real
  estate it would more likely live alongside the workload it shadows (VM,
  bare-metal device, or a sidecar) so it can probe real interfaces and respect
  existing network ACLs.
- Only happy-path tear-down is implemented. Persistent volumes, external DNS,
  or managed database instances are out of scope for this PoC.
- Credentials and secrets are stored in variables. Production rollouts need a
  secret manager (Vault, SOPS, SealedSecrets) plus policy-bound rotations.

Prerequisites
-------------

- Ansible 2.16+ with ``community.zabbix``, ``kubernetes.core``, and ``containers.podman`` collections.
- Local tooling: ``kind``, ``kubectl``, ``podman``, ``helm`` (Docker might work with extra tweaks but is untested).
- Python 3.9+ and the ability to run Podman containers on the host.
- At least 8 vCPU, 8 GiB RAM, and outbound internet access for Helm charts.

Usage
-----

1. Install Ansible collections.
`ansible-galaxy collection install -r ansible-role-deployment-automation/meta/requirements.yml`
2. Provide any overrides in ``ansible-role-deployment-automation/tests/inventory``
   or pass them on the command line.
3. Run the playbook locally:
`ansible-playbook -i ansible-role-deployment-automation/tests/inventory ansible-role-deployment-automation/tests/test.yml`
4. Browse the UI via the reverse proxy (default ``http://127.0.0.1:8123``).
5. Tear down the environment with ``-e state=absent`` when finished.

Key variables
-------------

| Variable | Default | Notes |
| --- | --- | --- |
| ``state`` | ``present`` | Switch to ``absent`` to delete kind clusters and containers. |
| ``infra_cluster_name`` | ``infra-cluster`` | Name for the synthetic workload kind cluster. |
| ``mgmt_cluster_name`` | ``mgmt-cluster`` | Name for the management kind cluster hosting Zabbix. |
| ``helm_binary_path`` | ``undefined`` | Point to ``files/helm-wrapper.py`` if you run Helm 4. |
| ``mgmt_cluster_zabbix_namespace`` | ``zabbix`` | Namespace for the Zabbix release. |
| ``mgmt_cluster_zabbix_admin_password`` | ``zabbix`` | Initial Admin password; override in secrets storage. |
| ``infra_cluster_zabbix_proxy_hostname`` | ``zabbix-proxy`` | Proxy identity shown in Zabbix. |
| ``snmpd_user`` | ``snmpv3user`` | SNMPv3 security name used by simulated devices. |
| ``snmpd_auth_pass`` / ``snmpd_priv_pass`` | ``ChangeMe...`` | Must be rotated before sharing the demo. |
| ``zabbix_web_reverse_proxy_host_port`` | ``8123`` | Host port exposing the Zabbix web UI. |

See ``defaults/main.yml`` for the full catalog of tunables including MetalLB,
PostgreSQL, and SNMP host registration details.

Testing
-------
- CI-style verification (lint, molecule) is not wired; add them before shipping
  this to a shared repository.

Demo
-----
[![Demo Video](https://img.youtube.com/vi/AOSk8T9o7tk/0.jpg)](https://youtu.be/AOSk8T9o7tk)