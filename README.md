# Karrio

- Website: <https://karrio.io>
- Forums: [Github Discussions](https://github.com/orgs/karrioapi/discussions)
- Documentation: [https://docs.karrio.io/](https://docs.karrio.io/)
- Discord: [Karrio Discord server](https://discord.gg/gS88uE7sEx)
- Issues: [Issue Tracker](https://github.com/karrioapi/karrio/issues)
- Blog: [Blog](https://karrio.io/blog)

<img referrerpolicy="no-referrer-when-downgrade" src="https://static.scarf.sh/a.png?x-pxid=e72dd847-dc7f-4f81-bce4-88eeb20d807f" />
<a href="https://karrio.io" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/karrioapi/karrio/main/server/main/karrio/server/static/extra/branding/logo-inverted.svg" height="100px" />
    <img alt="Karrio" src="https://raw.githubusercontent.com/karrioapi/karrio/main/server/main/karrio/server/static/extra/branding/logo.svg" height="100px" />
  </picture>
</a>

[![puprlship-tests](https://github.com/karrioapi/karrio/actions/workflows/tests.yml/badge.svg)](https://github.com/karrioapi/karrio/actions/workflows/tests.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/cc2ac4fcb6004bca84e42a90d8acfe41)](https://www.codacy.com/gh/karrioapi/karrio/dashboard?utm_source=github.com&utm_medium=referral&utm_content=karrioapi/karrio&utm_campaign=Badge_Grade)

Karrio is an open-source shipping infrastructure for platform. With Karrio, you can
build shipping experience into your platform, access a network of shipping carriers
with a single API integration, automate fulfilment and improve logistics operations.

**Get up and running in 1 minute with:**

```sh
git clone --depth 1 https://github.com/karrioapi/karrio
cd karrio/docker
docker compose up
```

- Karrio server accessible at <http://localhost:5002>
- Karrio dashboard accessible at <http://localhost:3000>

Default Login: admin@example.com | demo

## Features

- **Headless Shipping**: Access a network of traditional and modern shipping carriers API-first.
- **Extensible**: Build anything with webhooks, API and metadata.
- **Multi-carrier SDK**: Use the karrio SDK Framework to integrate with custom carrier APIs.
- **Fulfilment**: Connect carrier accounts, get live rates and purchase shipping labels.
- **Tracking**: Create package trackers, get real time tracking status and deliver a great shopping experience.
- **Address Validation**: Validate shipping addresses using integrated 3rd party APIs.
- **Cloud**: Optimized for deployments using Docker.
- **Dashboard**: Use the [karrio dashboard](https://github.com/karrioapi/karrio-dashboard) to orchestrate your logistics operations.

<img alt="Karrio Dashboard" src="screenshots/dashboard.png" />

## Get started

### Quick start demo

[A short video (less than 4 minutes)](https://youtu.be/dFHZosJPaLI) that goes over creating your first label and tracking your first package.

### Open-source hobby deploy

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/karrioapi/karrio/HEAD/bin/deploy-hobby)"
```

### Karrio Cloud

Request access to [Karrio Cloud](https://www.karrio.io/get-started).

### Enterprise self-hosted

See our [enterprise self-hosted docs](https://docs.karrio.io/self-hosting/enterprise) to deploy a scalable, production-ready instance with support from our team.

## The problem: Shipping integration is still painful

- Lack of documentation.
- Multiple and inconsistent APIs.
- Difficult access to account and API credentials for development.
- Poor developer experience.

## Our philosophy

We help you integrate with your shipping carriers and improve your fulfilment processes without loosing control.

We believe that the logistics industry can greatly benefit from a unified, open and standardized shipping API that gives you direct access to a network of carriers, control over customers' personal data and **compliance**.

## What are the benefits?

Karrio is the only **platform-focused** open-source shipping platform with label generation, document generation and package tracking API that **you can host on your own infrastructure**.

We are an open-source alternative to expensive in-house carrier integration and multi-carrier Saas APIs. We're designed to be more **developer-friendly**, with the fullset of shipping functionalities without vendor-lockin.

### Shipping for platforms

With Karrio, you can extend your platform with native shipping capabilities. Improve merchants and customers experience on your Marketplace, eCommerce, ERP, WMS, OMS, 3PL and Logistics platform.

### Shipping for enterprise

Karrio makes modern shipping accessible to brands, retailers as well as enterprises in regulated industries.

## Support

If you have general questions about Karrio, want to say hello or just follow along, we'd like to invite you to join our [Discord Community](https://discord.gg/gS88uE7sEx).

If you run into any problems or issues, please create a Github issue and we'll try our best to help.

We strive to provide good support through our issue trackers on Github. However, if you'd like to receive private & prioritized support with:

- Phone / video calls to discuss your specific use case and get recommendations on best practices
- Guidance around deployment, ops and scaling best practices
- Prioritized feature requests
- Prioritized carriers integrations

We do offer paid support options. Please reach out to us at hello@karrio.io to sign up.

## Developing locally & Contributing

See our Docs for instructions on [developing Karrio locally](https://docs.karrio.io/contributing/development).

We <3 contributions big or small, check out our [guide on how to get started](https://docs.karrio.io/contributing/guidlines).

Not sure where to start? [Send us an email](mailto:dev@karrio.com?subject=Pairing%20session&body=I'd%20like%20to%20do%20a%20pairing%20session!) to chat with a member of our team.

## Open-source vs. paid

This project uses the [Apache v2 license](LICENSE). The core Karrio platform will always remain open and free.

We are developing some commercial enterprise add-ons (contained in the `/ee` directory) only offered on our Cloud and Enterprise editions.

Any other questions, mail us at hello@karrio.io We’d love to meet you!
