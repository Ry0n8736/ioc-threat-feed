# IOC Threat Feed Pipeline

## Overview

This project is a custom IOC (Indicator of Compromise) ingestion and telemetry pipeline built in Python.

The pipeline ingests threat intelligence feeds, normalizes and validates indicators, enriches metadata, applies suppression logic, and exports structured JSON telemetry for operational visibility.

The long-term goal of the project is to complement enterprise SIEM and threat intelligence platforms by adding:

* environment-specific filtering
* custom suppression logic
* operational telemetry
* IOC lifecycle management
* intelligence engineering experimentation

This project is intentionally focused on learning and engineering progression rather than large-scale production deployment.

---

# Current Features

## IOC Ingestion

* Multi-feed IOC ingestion
* Support for external threat intelligence feeds
* Feed isolation to prevent single-feed failures from crashing the pipeline

---

## IOC Normalization

* Lowercase normalization
* Whitespace cleanup
* Tab-separated IOC parsing
* Structured IOC extraction

---

## IOC Validation

### IP Validation

* Private IP suppression
* Loopback suppression
* Multicast suppression
* Reserved IP suppression

### Domain Validation

* Invalid character filtering
* URL rejection
* Comment filtering
* Malformed IOC rejection

---

# IOC Metadata

Each IOC currently supports:

* IOC value
* IOC type
* Source attribution
* Source label
* Source URL
* Confidence score
* First seen timestamp
* Last seen timestamp
* Expiration state

---

# Suppression Architecture

The pipeline supports policy-based IOC suppression using:

```text
feeds/suppressions.txt
```

Suppressed IOCs are exported into telemetry output for observability and auditing.

---

# Reliability Engineering Features

The pipeline includes:

* Structured logging
* Timeout handling
* HTTP response validation
* Feed-level exception handling
* Network exception classification
* Runtime telemetry
* Automatic directory creation
* Feed health tracking

---

# Operational Telemetry

The pipeline exports operational telemetry including:

## Feed Health

```text
output/feed_health.json
```

Tracks:

* feed status
* IOC contribution counts
* feed failures
* error messages

## Suppressed IOC Telemetry

```text
output/suppressed_iocs.json
```

Tracks:

* suppressed IOCs
* suppression reason metadata

## IOC Metadata Output

```text
output/combined_iocs.json
```

Structured IOC records with enrichment metadata.

---

# Runtime Metrics

The pipeline displays:

* execution time
* feed processing count
* failed feed count
* suppressed IOC count
* IOC totals

---

# Project Structure

```text
ioc-threat-feed/
│
├── feeds/
│   ├── urls.txt
│   └── suppressions.txt
│
├── logs/
│
├── output/
│
├── scripts/
│   └── fetch_feeds.py
│
├── utils/
│   └── logger.py
│
├── README.md
└── requirements.txt
```

---

# Current Threat Feeds

Current feeds include sources such as:

* Abuse.ch
* URLHaus
* Feodo Tracker
* Emerging Threats
* Blocklist.de
* Stamparm Ipsum

---

# Future Development Goals

Planned future improvements include:

* Persistent IOC state storage
* True IOC aging and expiration
* ASN enrichment
* GeoIP enrichment
* CDN and cloud provider suppression
* Elastic ECS alignment
* Elasticsearch ingestion
* Kibana dashboards
* IOC enrichment scoring
* Detection engineering integrations
* Scheduled automation
* SOAR-style workflows

---

# Installation

## Clone Repository

```bash
git clone <repo-url>
cd ioc-threat-feed
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Running the Pipeline

```bash
python -m scripts.fetch_feeds
```

---

# Notes

This project is intended for:

* learning
* SOC engineering development
* threat intelligence engineering experimentation
* operational pipeline design practice

This project is not intended to replace commercial threat intelligence platforms.

Instead, it is designed to explore how custom intelligence engineering can complement enterprise SIEM workflows.
