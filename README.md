# infra-monitoring-stack


![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🚀 Introduction

This project demonstrates my implementation of a **production-grade monitoring and alerting stack** using Prometheus, Grafana, and Alertmanager on Kubernetes — adding full observability to my [CI/CD Deployment Pipeline](https://github.com/Rabaanee/docker-k8s-deployment-pipeline) project.

As part of my DevOps engineering portfolio — building on containerisation, orchestration, and CI/CD from my previous projects — this project completes the DevOps lifecycle by answering the critical question: **"How do you know your application is healthy in production?"**

## 📋 Project Overview

**Objective:** Deploy a complete observability stack that collects application and infrastructure metrics, visualises them in real-time dashboards, and triggers alerts when things go wrong.

**Key Features:**
- ✅ **Application Metrics** – Custom Prometheus metrics exposed from a Python Flask app (`/metrics` endpoint)
- ✅ **Prometheus Monitoring** – Automated service discovery and metric scraping via ServiceMonitor
- ✅ **Grafana Dashboards** – Custom dashboards for application performance and infrastructure health
- ✅ **Alert Rules** – PrometheusRules for error rate, pod restarts, high CPU, and application downtime
- ✅ **Alertmanager Routing** – Alert notification routing with grouping and severity levels
- ✅ **Helm Deployment** – Full stack deployed via kube-prometheus-stack Helm chart
- ✅ **CI/CD Pipeline** – GitHub Actions: lint rules → validate dashboards → Helm lint → deploy

