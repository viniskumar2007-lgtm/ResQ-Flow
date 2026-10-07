# 🚨 ResQ-Flow

## Offline-First AI Disaster Response System

ResQ-Flow is an offline-first emergency response system designed to help victims send emergency reports even when normal internet connectivity is unavailable.

The system uses **AI-based emergency analysis** to classify disaster type, determine severity, calculate priority, and route emergency information through a **mesh network** until it reaches a rescue device.

---

## 🎯 Problem

During disasters such as floods, earthquakes, fires, cyclones, landslides, and building collapses:

- Internet connectivity may be unavailable.
- Mobile towers may be damaged or overloaded.
- Victims may not know how to properly describe their emergency.
- Rescue teams may receive incomplete or unprioritized information.
- Direct communication between victims and rescue teams may not be possible.

ResQ-Flow addresses these problems using:

> **AI + Offline Processing + Mesh Networking + Rescue Prioritization**

---

## 💡 Solution

A victim submits an emergency message through the ResQ-Flow application.

The message passes through the following pipeline:

```text
Victim
   ↓
Emergency Message
   ↓
AI Message Analysis
   ↓
Disaster Classification
   ↓
Severity Classification
   ↓
Priority Calculation
   ↓
Emergency Packet
   ↓
Mesh Network
   ↓
Relay Device(s)
   ↓
Rescue Device
   ↓
Rescue Team